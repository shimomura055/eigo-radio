# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 作業4(¥0、実装しない): 後段Safety設計案の決定論部分のreplay。
# 入力: rca_major_rows_01.json(rca_scan_01.pyの出力。既存instance JSON全体のChecker MAJOR 1143件、Stage 2通過後)。
# 評価する決定論Guard(Checkerの構造化出力[flag]・claim文・Ledger fact本文だけを使う。追加LLM callなし):
#   G_A : changed_causality=true かつ claim文に因果接続語(so/because/therefore/as a result/led to 等)
#   G_B : changed_causality=true(接続語を問わない)
#   G_C : changed_causality ∨ unsupported_new_claim ∨ changed_certainty (Safety-critical流出10件が持つflagの和集合)
#   G_D : G_C かつ claimがLedgerと矛盾する具体値でなく...は決定論では判定不能のため対象外(記録のみ)
# 指標:
#   - 流出閉鎖: Safety-critical最終非BLOCKING 10行のうち、Guardで「AI解除不可(BLOCKING固定)」になる行数
#   - 解除不可になる正当降格: 最終非BLOCKING(降格)534件のうち、Guardで解除不可になる件数(QUALITY/ACCEPTABLE別、
#     NORMAL群[正解ラベル=全claim問題なし]内の件数=不要Rewrite確定の代理指標、rep24の件数、cycle別)
#   - S1(2回確認)を「Guard該当のllm_direct降格」だけに限定した場合のcall数(batch=instance×cycle×route単位)
import json, os, re, sys, collections
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
rows = json.load(open(f"{OUT}/rca_major_rows_01.json", encoding="utf-8"))
NORMAL = runner.NORMAL_GROUP_INSTANCE_IDS
CONN_CORE = re.compile(r"\b(so|because|therefore|as a result|led to|leading to)\b", re.I)
CONN_WIDE = re.compile(r"\b(so|because|because of|therefore|thus|hence|consequently|as a result|led to|leading to|lead to|"
                       r"caused|causing|cause of|due to|thanks to|owing to|which is why|that is why|that's why|resulting in|"
                       r"result of|driven by|reason (?:for|why))\b", re.I)
# 日本語claim(旧Checker言語)向けの因果語
CONN_JA = re.compile(r"ため|ので|から、|により|によって|せいで|おかげ|原因|理由|結果として|したがって|そのため")

cache = {}


def grp(f):
    if f not in cache:
        d = json.load(open(f, encoding="utf-8"))
        cache[f] = d.get("group")
    return cache[f]


def feats(r):
    c = r["claim"] or ""
    fl = set(r["flags"])
    return {
        "causality": "changed_causality" in fl,
        "unsupported": "unsupported_new_claim" in fl,
        "certainty": "changed_certainty" in fl,
        "conn_core": bool(CONN_CORE.search(c)) or bool(CONN_JA.search(c)),
        "conn_wide": bool(CONN_WIDE.search(c)) or bool(CONN_JA.search(c)),
        "hedge": bool(HEDGE.search(c)),
        "fact_cause": fact_has_cause_marker(r),
    }


HEDGE = re.compile(r"\b(could|may|might|can|would|possibly|perhaps|probably|likely|seems?|appears?)\b", re.I)
CAUSE_JA = re.compile(r"基づく|ため|ので|により|によって|理由|原因|結果|から、")
_fx = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}


def fact_has_cause_marker(r):
    led = _fx.get(r["instance_id"]) or ""
    m = re.search(r"(?ms)^\[VERIFIED\] %s:.*?(?=^\[VERIFIED\]|\Z)" % re.escape(r["fid"] or "@@"), led)
    return bool(m and CAUSE_JA.search(m.group(0)))


GUARDS = {
    "G_A(causality∧接続語core)": lambda f: f["causality"] and f["conn_core"],
    "G_A'(causality∧接続語wide)": lambda f: f["causality"] and f["conn_wide"],
    "G_H(G_A∧ヘッジ語なし)": lambda f: f["causality"] and f["conn_core"] and not f["hedge"],
    "G_I(G_H∧関連factがLedger上で原因/理由を明示[日本語因果語])": lambda f: f["causality"] and f["conn_core"] and not f["hedge"] and f["fact_cause"],
    "G_B(causality flagのみ)": lambda f: f["causality"],
    "G_C(causality∨unsupported∨certainty)": lambda f: f["causality"] or f["unsupported"] or f["certainty"],
    "G_E(causality∨certainty、unsupportedを除く)": lambda f: f["causality"] or f["certainty"],
}
down = [r for r in rows if r["materiality"] != "BLOCKING"]
leaks = [r for r in rows if r["sub_id"] and r["materiality"] != "BLOCKING"]
llm_direct = [r for r in down if r["llm_materiality"] != "BLOCKING" and not r["two_of_two"]]
rep24 = [r for r in llm_direct if r["dir"].endswith("rep24")]
res = {"n_rows": len(rows), "n_downgrades": len(down), "n_llm_direct": len(llm_direct), "n_rep24_llm_direct": len(rep24),
       "n_leaks": len(leaks), "guards": {}}
out_lines = []
for name, g in GUARDS.items():
    L = [(r, feats(r)) for r in leaks]
    closed = [r for r, f in L if g(f)]
    blocked = [(r, feats(r)) for r in down if g(feats(r)) and r not in leaks]
    bl_q = sum(1 for r, f in blocked if r["materiality"] == "QUALITY")
    bl_a = sum(1 for r, f in blocked if r["materiality"] == "ACCEPTABLE")
    bl_norm = sum(1 for r, f in blocked if r["instance_id"] in NORMAL and r["instance_id"] != "neg5_hormuz_div_a2")
    bl_uniq = len({(r["instance_id"], (r["claim"] or "")[:120]) for r, f in blocked})
    bl_uniq_norm = len({(r["instance_id"], (r["claim"] or "")[:120]) for r, f in blocked if r["instance_id"] in NORMAL and r["instance_id"] != "neg5_hormuz_div_a2"})
    bl_grp = collections.Counter(grp(r["file"]) for r, f in blocked)
    bl_sc = sum(1 for r, f in blocked if r["sub_id"])
    bl_rep24 = [r for r, f in blocked if r in rep24]
    bl_ld = [r for r, f in blocked if r in llm_direct]
    batches = {(r["dir"], r["instance_id"], r["cycle"], r["route"]) for r in bl_ld}
    by_inst = collections.Counter(r["instance_id"] for r, f in blocked)
    res["guards"][name] = {
        "leaks_closed": f"{len(closed)}/{len(leaks)}", "leaks_open": [(r["dir"][-8:], r["instance_id"], r["cycle"]) for r in leaks if r not in closed],
        "legit_downgrades_blocked": len(blocked), "of_which_QUALITY": bl_q, "of_which_ACCEPTABLE": bl_a,
        "of_which_in_NORMAL_group_excl_neg5(不要Rewrite確定の代理)": bl_norm, "unique_claims_blocked": bl_uniq,
        "unique_claims_in_NORMAL_excl_neg5": bl_uniq_norm, "by_instance_group": dict(bl_grp), "rep24_blocked": len(bl_rep24), "llm_direct_blocked": len(bl_ld),
        "S1_batches_if_limited": len(batches), "top_instances": by_inst.most_common(6),
        "blocked_rate_of_all_534": round(len(blocked) / max(1, len(down) - len(leaks)), 3),
    }
    out_lines.append((name, res["guards"][name]))
# rep24基準: 38 instance-runの1記事あたりの追加call・追加Rewriteの粗い試算
rep24_runs = len({r["file"] for r in rep24}) or 1
res["rep24_instance_runs_with_downgrade"] = rep24_runs
# 全MAJOR(1143)のうち、Guard該当でStage 2がBLOCKING判定済みの件数(影響なし)
res["guard_hits_among_all_major"] = {name: sum(1 for r in rows if g(feats(r))) for name, g in GUARDS.items()}
res["guard_hits_among_downgrades"] = {name: sum(1 for r in down if g(feats(r))) for name, g in GUARDS.items()}
# 内訳: 解除不可になる正当降格の仮ラベル用(NORMAL群の件数と、非NORMALのうちSafety群/B群等のinstance別)
json.dump(res, open(f"{OUT}/replay_guards_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for name, v in out_lines:
    print(name)
    for k, x in v.items():
        print("   ", k, x)
print("guard hits among all MAJOR:", res["guard_hits_among_all_major"])
print("guard hits among downgrades:", res["guard_hits_among_downgrades"])
print("n:", {k: res[k] for k in ("n_rows", "n_downgrades", "n_llm_direct", "n_rep24_llm_direct", "n_leaks")})
