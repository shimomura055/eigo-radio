# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_03 作業2-2(¥0、API呼び出しなし): Tier 0 因果floor(語彙は言語学的目録から構築・
# 流出16行を見ずに確定し、git commit 3808f61fで評価前に固定)の評価。can/would=A(ヘッジに含める)/B(含めない)の2版。
# 母集団は replay_guards_03_gl.py と同一(rca_major_rows_01.json、Checker MAJOR 1143件、降格534・流出16・正当降格518・NORMAL群110)。
# 採用条件(Fable事前設定): 正当降格の誤停止<=2% かつ 流出閉鎖>=15/16(「and」版を除き15/15)。
import collections
import json
import os
import sys

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner

OUT = "er052_output/open233_kpi_recovery_02_offline_01"
rows = json.load(open(f"{OUT}/rca_major_rows_01.json", encoding="utf-8"))
NORMAL = runner.NORMAL_GROUP_INSTANCE_IDS
NEG5 = "neg5_hormuz_div_a2"

down = [r for r in rows if r["materiality"] != "BLOCKING"]
leaks_old = [r for r in down if r["sub_id"]]
neg5_same = [r for r in down if r["instance_id"] == NEG5 and runner.normalized_same_as_labeled(r["claim"], "bgroup_B3")]
leaks_new = leaks_old + neg5_same
leak_ids = {id(r) for r in leaks_new}
legit = [r for r in down if id(r) not in leak_ids]
legit_normal = [r for r in legit if r["instance_id"] in NORMAL and r["instance_id"] != NEG5]


def is_and_version(r):
    t = (r["claim"] or "").casefold()
    return "and the flashy 20% plan" in t and "so the flashy 20% plan" not in t


and_rows = [r for r in leaks_new if is_and_version(r)]
leaks_ex_and = [r for r in leaks_new if not is_and_version(r)]


def dev_of(r):
    d = {k: True for k in r["flags"]}
    d["issue"] = r["issue"] or ""
    return d


def run(name, fn):
    cl = [r for r in leaks_new if fn(r)]
    bl = [r for r in legit if fn(r)]
    bn = [r for r in legit_normal if fn(r)]
    res = {
        "leaks_closed_new16": f"{len(cl)}/{len(leaks_new)}",
        "leaks_closed_old10": f"{sum(1 for r in leaks_old if fn(r))}/{len(leaks_old)}",
        "leaks_closed_excl_and": f"{sum(1 for r in leaks_ex_and if fn(r))}/{len(leaks_ex_and)}",
        "and_version_closed": f"{sum(1 for r in and_rows if fn(r))}/{len(and_rows)}",
        "leaks_open": [(r["dir"][-8:], r["instance_id"], r["sub_id"], r["cycle"], (r["claim"] or "")[:90]) for r in leaks_new if not fn(r)],
        "legit_blocked": len(bl), "legit_blocked_rate": round(len(bl) / max(1, len(legit)), 4),
        "QUALITY": sum(1 for r in bl if r["materiality"] == "QUALITY"),
        "ACCEPTABLE": sum(1 for r in bl if r["materiality"] == "ACCEPTABLE"),
        "NORMAL_blocked": len(bn), "NORMAL_rate": round(len(bn) / max(1, len(legit_normal)), 4),
        "unique_claims": len({(r["instance_id"], (r["claim"] or "")[:100]) for r in bl}),
    }
    ok_fp = res["legit_blocked_rate"] <= 0.02
    ok_cl = len([r for r in leaks_ex_and if fn(r)]) == len(leaks_ex_and) and len(cl) >= 15
    res["meets_fp<=2%"] = ok_fp
    res["meets_closure(>=15/16, and-excluded all)"] = ok_cl
    res["meets_adoption_condition"] = ok_fp and ok_cl
    return res


def causal(can_would):
    return lambda r: runner.causal_floor_guard(dev_of(r), r["claim"] or "", can_would)[0]


def g_h(r):
    return runner.g_h_guard(dev_of(r), r["claim"] or "")[0]


result = {"n_rows": len(rows), "n_downgrades": len(down), "n_leaks_old": len(leaks_old), "n_leaks_new": len(leaks_new),
          "n_and_version": len(and_rows), "n_legit": len(legit), "n_legit_normal_excl_neg5": len(legit_normal), "versions": {}}
def ia(r):
    return runner.issue_actor_guard(dev_of(r), r["claim"] or "")[0]


fns = {"A(can/would=hedge)": causal(True), "B(can/would!=hedge)": causal(False), "G_H既知6語(参考)": g_h,
       "Tier0全体A(因果floor_A∨issue_actor、参考)": lambda r: causal(True)(r) or ia(r),
       "Tier0全体G_H6語(G_H∨issue_actor、参考=委任_02補助ベルト)": lambda r: g_h(r) or ia(r)}
for name, fn in fns.items():
    result["versions"][name] = run(name, fn)

# 既知G_H 6語との差分(拡張で新たに閉じた・止めた件)
for ver, cw in (("A(can/would=hedge)", True), ("B(can/would!=hedge)", False)):
    f = causal(cw)
    new_closed = [r for r in leaks_new if f(r) and not g_h(r)]
    lost_closed = [r for r in leaks_new if g_h(r) and not f(r)]
    new_stop = [r for r in legit if f(r) and not g_h(r)]
    lost_stop = [r for r in legit if g_h(r) and not f(r)]
    result["versions"][ver]["vs_G_H"] = {
        "newly_closed_leaks": len(new_closed), "lost_closed_leaks": len(lost_closed),
        "newly_stopped_legit": len(new_stop), "no_longer_stopped_legit": len(lost_stop),
        "newly_stopped_legit_examples": [(r["instance_id"], (r["claim"] or "")[:100]) for r in new_stop[:8]]}
# 採用版の選択(Fable事前規則: 条件を満たす方。両方なら閉鎖が多い方、同じなら誤停止が少ない方)
# 参考(判定には使わない): 拡張で新たに誤停止した正当降格の一致語内訳
_new = [r for r in legit if causal(True)(r) and not g_h(r)]
result["newly_stopped_legit_matched_connectives"] = collections.Counter(
    c for r in _new for c in runner.causal_vocab_hits(r["claim"] or "", True)["connectives"]).most_common()
result["newly_stopped_legit_detail"] = [(r["instance_id"], r["materiality"], runner.causal_vocab_hits(r["claim"] or "", True)["connectives"],
                                         (r["claim"] or "")[:120]) for r in _new]
cands = [(v, result["versions"][v]) for v in ("A(can/would=hedge)", "B(can/would!=hedge)")
         if result["versions"][v]["meets_adoption_condition"]]
if not cands:
    result["decision"] = "どちらも採用条件を満たさない(語彙は削らず事実を記録、Fableへ報告。Step 5へ進まない)"
    result["adopted"] = None
else:
    cands.sort(key=lambda x: (-int(x[1]["leaks_closed_new16"].split("/")[0]), x[1]["legit_blocked"]))
    result["adopted"] = cands[0][0]
    result["decision"] = f"採用: {cands[0][0]}"
json.dump(result, open(f"{OUT}/replay_guards_04_causal_floor.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in result.items() if k != "versions"}, ensure_ascii=False))
hdr = "%-22s %-8s %-8s %-9s %-8s | %-26s | %-16s"
print(hdr % ("version", "閉鎖16", "閉鎖旧10", "閉鎖(and除)", "and版", "正当降格誤停止(件/率)", "NORMAL群(件/率)"))
for name, g in result["versions"].items():
    print("%-22s %-8s %-8s %-9s %-8s | %4d / %5.2f%% (Q%3d A%3d) | %3d / %5.1f%%   fp<=2%%:%s closure:%s" % (
        name, g["leaks_closed_new16"], g["leaks_closed_old10"], g["leaks_closed_excl_and"], g["and_version_closed"],
        g["legit_blocked"], 100 * g["legit_blocked_rate"], g["QUALITY"], g["ACCEPTABLE"],
        g["NORMAL_blocked"], 100 * g["NORMAL_rate"], g["meets_fp<=2%"], g["meets_closure(>=15/16, and-excluded all)"]))
print("拡張で新たに誤停止した正当降格の一致語:", result["newly_stopped_legit_matched_connectives"])
for d in result["newly_stopped_legit_detail"]:
    print("  ", d)
for name, g in result["versions"].items():
    print(name, "open leaks:", g["leaks_open"])
    if "vs_G_H" in g:
        print(name, "vs_G_H:", json.dumps(g["vs_G_H"], ensure_ascii=False))
