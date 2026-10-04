# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_02 作業3(¥0、API呼び出しなし): Tier 0 G_L(Ledger構造化欄×Checker flag)の判別力評価。
# 入力: rca_major_rows_01.json(既存instance JSON全体のChecker MAJOR 1143件、Stage 2通過後)+runnerのfixture(Ledger)。
# 評価対象(いずれも決定論、runnerの`stage2_release_guard`と同じ定数・関数を使う):
#   G_L          : runner.g_l_guard(Ledger関連factの`causal_strength`/`notes_for_writer`の禁止文 × Checkerのchanged_* flag)
#   G_H          : runner.g_h_guard(補助ベルト、委任_01の定義のまま)
#   issue_actor  : runner.issue_actor_guard(補助ベルト、委任_01の定義のまま)
#   組合せ       : G_L∨G_H∨issue_actor(=Tier 0全体)ほか
# 指標: 流出閉鎖(Safety-critical流出10行+neg5のB3同一文6行=16行のうちBLOCKING固定になる行数)、
#       正当降格のBLOCKING化(降格534件から流出16行を除いた件のうちBLOCKING固定になる件数・率、QUALITY/ACCEPTABLE別、NORMAL群別)。
# 判定基準(Fable事前設定): 正当降格BLOCKING化>5%かつ流出閉鎖の上積みなし → G_L不採用(補助ベルトのみ)。
import collections
import json
import os
import sys

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner

OUT = "er052_output/open233_kpi_recovery_02_offline_01"
rows = json.load(open(f"{OUT}/rca_major_rows_01.json", encoding="utf-8"))
fx = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
NORMAL = runner.NORMAL_GROUP_INSTANCE_IDS
NEG5 = "neg5_hormuz_div_a2"

down = [r for r in rows if r["materiality"] != "BLOCKING"]
leaks_old = [r for r in down if r["sub_id"]]
# neg5のB3同一文(正規化同一文)=自動導出の同一文判定と同じ関数で判定する
neg5_same = [r for r in down if r["instance_id"] == NEG5 and runner.normalized_same_as_labeled(r["claim"], "bgroup_B3")]
leaks_new = leaks_old + neg5_same
leak_ids = {id(r) for r in leaks_new}
legit = [r for r in down if id(r) not in leak_ids]
legit_normal = [r for r in legit if r["instance_id"] in NORMAL and r["instance_id"] != NEG5]
llm_direct = [r for r in legit if r["llm_materiality"] != "BLOCKING" and not r["two_of_two"]]


def dev_of(r):
    d = {k: True for k in r["flags"]}
    d["issue"] = r["issue"] or ""
    d["related_fact_id"] = r["fid"]
    return d


def guard_eval(r):
    """行 -> {guard名: (blocked, reason)}"""
    dev = dev_of(r)
    claim = r["claim"] or ""
    block = runner.floor_verify_fact_block(fx.get(r["instance_id"], ""), r["fid"])
    gl, gl_reason = runner.g_l_guard(dev, block)
    gh, gh_reason = runner.g_h_guard(dev, claim)
    ia, ia_reason = runner.issue_actor_guard(dev, claim)
    out = {"G_L": (gl, gl_reason), "G_H": (gh, gh_reason), "issue_actor": (ia, ia_reason)}
    for name, part in (("G_L_causal_strength_only", "gl_causal_strength"), ("G_L_notes_only", "gl_notes")):
        out[name] = (gl and gl_reason.startswith(part), gl_reason)
    out["aux(G_H∨issue_actor)"] = (gh or ia, gh_reason or ia_reason)
    out["G_B(参考: causality flagのみ=G_Lが『G_B並みに広い』かの比較基準)"] = (bool(dev.get("changed_causality")), "")
    out["Tier0全体(G_L∨aux)"] = (gl or gh or ia, gl_reason or gh_reason or ia_reason)
    return out


ev = {id(r): guard_eval(r) for r in rows}
names = list(next(iter(ev.values())).keys())
result = {"n_rows": len(rows), "n_downgrades": len(down), "n_leaks_old": len(leaks_old), "n_neg5_same_sentence": len(neg5_same),
          "n_leaks_new": len(leaks_new), "n_legit": len(legit), "n_legit_normal_excl_neg5": len(legit_normal), "guards": {}}
for name in names:
    closed_old = [r for r in leaks_old if ev[id(r)][name][0]]
    closed_new = [r for r in leaks_new if ev[id(r)][name][0]]
    bl = [r for r in legit if ev[id(r)][name][0]]
    bl_norm = [r for r in legit_normal if ev[id(r)][name][0]]
    bl_ld = [r for r in llm_direct if ev[id(r)][name][0]]
    reasons = collections.Counter(ev[id(r)][name][1] for r in bl)
    result["guards"][name] = {
        "leaks_closed_old10": f"{len(closed_old)}/{len(leaks_old)}", "leaks_closed_new16": f"{len(closed_new)}/{len(leaks_new)}",
        "leaks_open_new": [(r["dir"][-8:], r["instance_id"], r["sub_id"], r["cycle"]) for r in leaks_new if r not in closed_new],
        "legit_blocked": len(bl), "legit_blocked_rate": round(len(bl) / max(1, len(legit)), 4),
        "QUALITY": sum(1 for r in bl if r["materiality"] == "QUALITY"), "ACCEPTABLE": sum(1 for r in bl if r["materiality"] == "ACCEPTABLE"),
        "in_NORMAL_excl_neg5": len(bl_norm), "NORMAL_rate": round(len(bl_norm) / max(1, len(legit_normal)), 4),
        "llm_direct_blocked": len(bl_ld), "unique_claims": len({(r["instance_id"], (r["claim"] or "")[:100]) for r in bl}),
        "reasons": dict(reasons.most_common(8)),
    }
# G_Lが補助ベルトに対して上積みする流出閉鎖(新16行)
aux_closed = {id(r) for r in leaks_new if ev[id(r)]["aux(G_H∨issue_actor)"][0]}
gl_closed = {id(r) for r in leaks_new if ev[id(r)]["G_L"][0]}
result["G_L_added_closure_over_aux"] = len(gl_closed - aux_closed)
result["aux_added_closure_over_G_L"] = len(aux_closed - gl_closed)
gl_bl = result["guards"]["G_L"]
result["G_L_decision"] = (
    "不採用(補助ベルトのみ)" if (gl_bl["legit_blocked_rate"] > 0.05 and result["G_L_added_closure_over_aux"] == 0)
    else "採用(主Guard候補)")
# 最終判断(Claude/Sonnet、Fable評価4「G_B並みに広ければ不採用」と確認役replay採否基準(ii)[NORMAL群BLOCKING化率<=10%、Tier 0該当分を含む]との整合):
# 事前基準の文面どおりでは「採用」(上積み1行があるため)だが、G_L単独でNORMAL群のBLOCKING化が10%を超え(確認役の前に基準(ii)を満たせない)、
# 上積みはrep24 cycle 2の1行だけ(確認役が閉じる見込み)なので、Tier 0の既定は補助ベルトのみ(runner TIER0_G_L_ENABLED=False)とする。
# G_L有効時の反実仮想は確認役replay(replay_verify_01.py)で併記する。事前基準の文面と最終判断の差はFableへ報告する。
result["G_L_final_decision"] = ("Tier 0既定は補助ベルトのみ(G_L既定OFF)" if gl_bl["NORMAL_rate"] > 0.10
                                else "G_Lを主Guardとして採用")
result["G_L_final_decision_basis"] = {"G_L_NORMAL_rate": gl_bl["NORMAL_rate"], "criterion_ii_limit": 0.10,
                                      "G_L_legit_blocked_rate": gl_bl["legit_blocked_rate"],
                                      "G_B_reference_legit_blocked_rate": result["guards"]["G_B(参考: causality flagのみ=G_Lが『G_B並みに広い』かの比較基準)"]["legit_blocked_rate"]}
json.dump(result, open(f"{OUT}/replay_guards_03_gl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in result.items() if k != "guards"}, ensure_ascii=False))
print("%-28s %-9s %-9s | %-26s | %-14s %-8s" % ("guard", "閉鎖(旧10)", "閉鎖(新16)", "正当降格BLOCKING化(件/率)", "NORMAL群(件/率)", "unique"))
for name in names:
    g = result["guards"][name]
    print("%-28s %-9s %-9s | %4d / %5.1f%% (Q%3d A%3d) | %3d / %5.1f%%    %4d" % (
        name, g["leaks_closed_old10"], g["leaks_closed_new16"], g["legit_blocked"], 100 * g["legit_blocked_rate"],
        g["QUALITY"], g["ACCEPTABLE"], g["in_NORMAL_excl_neg5"], 100 * g["NORMAL_rate"], g["unique_claims"]))
only_gl = [r for r in leaks_new if id(r) in (gl_closed - aux_closed)]
print("G_Lだけが閉じる流出行:", [(r["dir"][-8:], r["instance_id"], r["cycle"], (r["claim"] or "")[:80]) for r in only_gl])
print("G_L reasons:", result["guards"]["G_L"]["reasons"])
print("G_L open leaks:", result["guards"]["G_L"]["leaks_open_new"])
print("Tier0全体 open leaks:", result["guards"]["Tier0全体(G_L∨aux)"]["leaks_open_new"])
print("G_L added closure over aux:", result["G_L_added_closure_over_aux"], "| aux added over G_L:", result["aux_added_closure_over_G_L"])
print("G_L decision(事前基準の文面):", result["G_L_decision"])
print("G_L final decision:", result["G_L_final_decision"], result["G_L_final_decision_basis"])
