"""委任_01B: Phase 2 費用見積(API呼出なし)。ABC実績(cost_01.json)のjob単価から段階化案を算出。"""
import json, collections
OUT = "er064_output/kp_extraction_selection_opt_01/phase1_b"
abc = json.load(open("er064_output/kp_idiom_priority_abc_01/cost_01.json", encoding="utf-8"))
per_tag = collections.defaultdict(float)
for c in abc["calls"]:
    per_tag[c["tag"]] += c["cost_jpy"]
lv = {"std": [], "adv": []}
for t, v in per_tag.items():
    lv[t.split("_")[0]].append(v)
unit = {k: round(sum(v) / len(v), 4) for k, v in lv.items()}
overall = round(sum(per_tag.values()) / len(per_tag), 4)
# After prompt は入力 +約280token(+約10%)。出力が費用の大半のため +3% を保守的に上乗せ
AFTER_UPLIFT = 1.03
RESERVE = 0.0
n = 3
BUDGET = 50.0


def jobs(articles, conds):
    return {(a, l, c): n for a in articles for l in ("std", "adv") for c in conds}


def cost_of(plan):
    tot = 0.0
    for (a, l, c), k in plan.items():
        u = unit[l] * (AFTER_UPLIFT if c in ("C2", "C3") else 1.0)
        tot += u * k
    return round(tot, 2)


stages = {
    "stage1_coffee_full": jobs(["coffee"], ["C0", "C1", "C2"]),
    "stage2_meta_C0_vs_C2": jobs(["meta"], ["C0", "C2"]),
    "stage3_hormuz_C0_vs_C2": jobs(["hormuz"], ["C0", "C2"]),
}
optional = {
    "opt_coffee_C3_newprompt_oldshortlist": jobs(["coffee"], ["C3"]),
    "opt_meta_hormuz_C1": jobs(["meta", "hormuz"], ["C1"]),
    "full_3articles_x_3conds": jobs(["coffee", "meta", "hormuz"], ["C0", "C1", "C2"]),
}
res = {"status": "ESTIMATE_ONLY_NOT_EXECUTED", "budget_jpy": BUDGET, "n_per_cell": n,
       "unit_cost_jpy_per_job_from_ABC": unit, "overall_unit": overall, "after_prompt_uplift": AFTER_UPLIFT,
       "basis": "ABC cost_01.json 18 jobs total 19.1078 (select+canonicalization+Redundancy QA, retryなし)", "stages": {}, "optional": {}}
cum = 0.0
for k, p in stages.items():
    c = cost_of(p)
    cum = round(cum + c, 2)
    res["stages"][k] = {"jobs": sum(p.values()), "cost_jpy": c, "cumulative_jpy": cum}
for k, p in optional.items():
    res["optional"][k] = {"jobs": sum(p.values()), "cost_jpy": cost_of(p), "fits_in_50_with_stages_1_to_3": round(cum + cost_of(p), 2) <= BUDGET}
res["recommended_total_jpy"] = cum
res["reserve_jpy"] = round(BUDGET - cum, 2)
res["stop_rule"] = "累計 JPY48 到達で新規job停止し報告(retry自動実行なし=ABCと同じく初回gate結果を記録)"
res["conditions"] = {"C0": "現行Prompt+現行shortlist(Production現行)", "C1": "現行Prompt+改善shortlist(Phase 1-A出力)",
                     "C2": "改善Prompt(prompt_after_01)+改善shortlist", "C3(任意)": "改善Prompt+現行shortlist(Prompt効果の単独分離)"}
json.dump(res, open(f"{OUT}/phase2_cost_estimate_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
