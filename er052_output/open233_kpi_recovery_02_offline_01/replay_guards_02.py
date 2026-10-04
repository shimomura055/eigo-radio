# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 作業4(¥0、実装しない): 推奨案D*の決定論Guard(G_H+issue_actor)と
# 補助案(issue_cause・recurrence)のreplay。入力は rca_major_rows_01.json(rca_scan_01.py出力)。
#   G_H          : Checkerのchanged_causality=true ∧ claimに因果接続語(英語: so/because/therefore/as a result/led to/leading to) ∧ ヘッジ語なし
#   issue_actor  : Checker issue文が「支払者・責任主体・負担者」等の主体付与を名指し(語彙一致)
#   D*_guard     : G_H ∨ issue_actor(=AI単独の解除を禁止する決定論クラス。英語claimのみ。日本語claim[旧paired JA]は対象外)
#   issue_cause  : issue文に因果語(参考。広すぎる)
#   recurrence   : 同instance・同fact_idで前cycleがBLOCKING→後cycleで非BLOCKING(参考)
# 評価母集団: (a)最終非BLOCKING(降格)の全行 (b)llm_direct降格(Stage 2単独の降格) (c)rep24のllm_direct降格68件
import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
rows = json.load(open(f"{OUT}/rca_major_rows_01.json", encoding="utf-8"))
BS = chr(92)
CONN = re.compile(BS + "b(so|because|therefore|as a result|led to|leading to)" + BS + "b", re.I)
HEDGE = re.compile(BS + "b(could|may|might|can|would|possibly|perhaps|probably|likely|seems?|appears?)" + BS + "b", re.I)
CAUSE_ISSUE = re.compile(r"caus|because|attribut|due to|led to|result of|reason for|因果|原因|理由|せい", re.I)
ACTOR_ISSUE = re.compile(
    r"payer|liable|who would (?:pay|be)|who pays|responsib|"
    r"identif(?:y|ies|ied) " + "[^.]{0,40}" + r" as (?:the )?(?:payer|responsible|party|actor)|支払|負担者|主体|担当者", re.I)
JA = re.compile(r"[぀-ヿ一-鿿]")

down = [r for r in rows if r["materiality"] != "BLOCKING"]
leaks = [r for r in rows if r["sub_id"] and r["materiality"] != "BLOCKING"]
llm_direct = [r for r in down if r["llm_materiality"] != "BLOCKING" and not r["two_of_two"]]
rep24 = [r for r in llm_direct if r["dir"].endswith("rep24")]
idset = lambda xs: {id(x) for x in xs}


def is_en(r):
    return not JA.search(r["claim"] or "")


def g_h(r):
    c = r["claim"] or ""
    return is_en(r) and "changed_causality" in r["flags"] and bool(CONN.search(c)) and not HEDGE.search(c)


def issue_actor(r):
    return is_en(r) and bool(ACTOR_ISSUE.search(r["issue"] or ""))


def dstar(r):
    return g_h(r) or issue_actor(r)


by = collections.defaultdict(list)
for r in rows:
    by[(r["file"], r["fid"])].append(r)
rec_ids = set()
for k, rs in by.items():
    rs.sort(key=lambda x: x["cycle"])
    for i, r in enumerate(rs):
        if r["materiality"] != "BLOCKING" and any(p["materiality"] == "BLOCKING" and p["cycle"] < r["cycle"] for p in rs[:i]):
            rec_ids.add(id(r))
GUARDS = {
    "G_H": g_h,
    "issue_actor": issue_actor,
    "D*_guard(G_H∨issue_actor)": dstar,
    "issue_cause(参考)": lambda r: is_en(r) and bool(CAUSE_ISSUE.search(r["issue"] or "")),
    "recurrence(参考)": lambda r: id(r) in rec_ids,
}
NEG = lambda r: r["instance_id"].startswith("neg") and r["instance_id"] != "neg5_hormuz_div_a2"
result = {}
for name, g in GUARDS.items():
    closed = [r for r in leaks if g(r)]
    res = {"leaks_closed": f"{len(closed)}/{len(leaks)}"}
    for label, pop in (("all_downgrades", down), ("llm_direct", llm_direct), ("rep24_llm_direct", rep24)):
        bl = [r for r in pop if g(r) and r not in leaks]
        res[label] = {
            "population": len(pop), "blocked": len(bl),
            "QUALITY": sum(1 for r in bl if r["materiality"] == "QUALITY"),
            "ACCEPTABLE": sum(1 for r in bl if r["materiality"] == "ACCEPTABLE"),
            "unique_claims": len({(r["instance_id"], (r["claim"] or "")[:100]) for r in bl}),
            "in_negative_group_excl_neg5(不要Rewrite確定の代理)": sum(1 for r in bl if NEG(r)),
            "neg5(=B3同一文、プロジェクトのv2訂正で正BLOCKING扱い)": sum(1 for r in bl if r["instance_id"] == "neg5_hormuz_div_a2"),
            "cycle1": sum(1 for r in bl if r["cycle"] == 1), "cycle2plus": sum(1 for r in bl if r["cycle"] >= 2),
            "batches(instance×cycle×route)": len({(r["dir"], r["instance_id"], r["cycle"], r["route"]) for r in bl}),
        }
    result[name] = res
# 参考: llm_direct降格(Stage 2単独で解除)の中でD*に非該当の件数=S1(2回確認)の対象。rep24でのbatch数
rest = [r for r in llm_direct if not dstar(r)]
rest24 = [r for r in rep24 if not dstar(r)]
result["S1_target_after_D*"] = {
    "llm_direct_not_gated": len(rest), "rep24_not_gated": len(rest24),
    "rep24_batches": len({(r["dir"], r["instance_id"], r["cycle"], r["route"]) for r in rest24}),
    "rep24_instance_runs": len({r["file"] for r in rep24}),
}
json.dump(result, open(f"{OUT}/replay_guards_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(result, ensure_ascii=False, indent=1))
print("---- D*_guardでブロックされる非流出行(一覧)")
for r in down:
    if dstar(r) and r not in leaks:
        print(r["dir"][-8:], r["instance_id"], "c%d" % r["cycle"], r["materiality"], r["basis"], "|", (r["claim"] or "")[:110].replace("\n", " "), "| issue:", (r["issue"] or "")[:110].replace("\n", " "))
