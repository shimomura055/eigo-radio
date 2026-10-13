# Round1 Stage3の組合せ選択(事前登録規則 plan_r1.md を機械適用。¥0)
import json, os, sys
sys.path.insert(0, os.getcwd())
OUT = "er064_output/kp_integrated_opt_01/round1"
A = json.load(open(f"{OUT}/analysis_r1.json", encoding="utf-8"))
combos = sorted({e["combo"] for e in A.values() if e["article"] == "coffee"})
def lv(c, l): return A[f"coffee_{l}_{c}"]
base = "M0P0"
bs = [lv(base, l) for l in ("std", "adv")]
base_pass = sum(e["sel_pass"] for e in bs) / sum(e["n"] for e in bs)
base_low = sum(e["low_slots_per_run"] for e in bs) / 2
base_cre = sum(e["creative_important_per_run"] for e in bs) / 2
rows = []
for c in combos:
    es = [lv(c, l) for l in ("std", "adv")]
    pr = sum(e["sel_pass"] for e in es) / sum(e["n"] for e in es)
    low = sum(e["low_slots_per_run"] for e in es) / 2
    cre = sum(e["creative_important_per_run"] for e in es) / 2
    score = sum(e["score_mean"] for e in es)
    jac = sum(e["jaccard_mean"] or 0 for e in es) / 2
    cost = sum(e["cost_mean"] for e in es) / 2
    excl = []
    if pr < base_pass - 0.10: excl.append(f"(a) selection PASS率 {pr:.2f} < 基準{base_pass:.2f}-0.10")
    if cre > base_cre: excl.append("(b) 創作比喩Imp混入が基準より多い")
    if low > base_low + 1e-9: excl.append(f"(c) 低優先枠 {low:.2f} > 基準{base_low:.2f}")
    rows.append({"combo": c, "score_sum_std_adv": round(score, 2), "sel_pass_rate": round(pr, 3), "low_slots_mean": round(low, 3), "creative_imp_mean": round(cre, 3), "jaccard_mean": round(jac, 3), "cost_mean": round(cost, 3), "excluded": excl})
ok = [r for r in rows if not r["excluded"] and r["combo"] != base]
ok.sort(key=lambda r: (-r["score_sum_std_adv"], r["low_slots_mean"], -r["jaccard_mean"], r["cost_mean"]))
pick = [r["combo"] for r in ok[:2]]
plan = {"rule": "plan_r1.md 事前登録規則", "baseline": base, "baseline_stats": {"sel_pass_rate": base_pass, "low_slots_mean": base_low, "creative_imp_mean": base_cre},
        "table": rows, "combos": pick, "articles": ["meta", "hormuz"], "n": 2}
json.dump(plan, open(f"{OUT}/stage3_plan_r1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in sorted(rows, key=lambda r: -r["score_sum_std_adv"]): print(r)
print("PICK", pick)
