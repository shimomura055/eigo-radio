"""委任_02: Phase 2改訂計画の費用見積と、期待ラベルの測定可能性(各shortlist構成に存在するか)の算出。API呼出なし。"""
import collections, json

OUT = "er064_output/kp_extraction_selection_opt_01/phase1_fix"
abc = json.load(open("er064_output/kp_idiom_priority_abc_01/cost_01.json", encoding="utf-8"))
per_tag = collections.defaultdict(float)
for c in abc["calls"]:
    per_tag[c["tag"]] += c["cost_jpy"]
lv = {"std": [], "adv": []}
for t, v in per_tag.items():
    lv[t.split("_")[0]].append(v)
unit = {k: round(sum(v) / len(v), 4) for k, v in lv.items()}
UPLIFT = 1.03  # C0以外は改善shortlist(+約51token)等を見込み保守的に+3%(C2 Promptは現行より短縮されたため過大見積)
BUDGET, STOP = 50.0, 48.0
n = 3
# (id, article, level, condition, label)
plan = []
for a in ("coffee", "meta", "hormuz"):
    for l in ("std", "adv"):
        for c in ("C0", "C2"):
            plan.append((a, l, c))
plan += [("coffee", "adv", "C1"), ("coffee", "adv", "C2prime")]
rows = []
for a, l, c in plan:
    u = unit[l] * (1.0 if c == "C0" else UPLIFT)
    rows.append({"article": a, "level": l, "condition": c, "n": n, "unit_jpy": round(u, 4), "cost_jpy": round(u * n, 3)})
stages = [("Stage 1: Coffee C0/C2 両Level + C1 Adv + C2' Adv", lambda r: r["article"] == "coffee"),
          ("Stage 2: meta C0/C2 両Level", lambda r: r["article"] == "meta"),
          ("Stage 3: hormuz C0/C2 両Level", lambda r: r["article"] == "hormuz")]
res = {"status": "ESTIMATE_ONLY_NOT_EXECUTED", "unit_cost_jpy_per_job_from_ABC": unit, "uplift_non_C0": UPLIFT, "n_per_cell": n, "budget_jpy": BUDGET, "stop_rule_jpy": STOP,
       "stages": [], "rows": rows}
cum = 0.0
for name, f in stages:
    rr = [r for r in rows if f(r)]
    c = round(sum(r["cost_jpy"] for r in rr), 2)
    cum = round(cum + c, 2)
    res["stages"].append({"name": name, "jobs": sum(r["n"] for r in rr), "cost_jpy": c, "cumulative_jpy": cum})
res["total_jobs"] = sum(r["n"] for r in rows)
res["total_jpy"] = round(sum(r["cost_jpy"] for r in rows), 2)
res["margin_to_stop_rule"] = round(STOP - res["total_jpy"], 2)
res["margin_to_budget"] = round(BUDGET - res["total_jpy"], 2)
res["note_C0prime"] = "C0'(方式2のV2 shortlist+現行Prompt)はABC-A既存18 jobの結果を再利用(新規費用0)"
res["note_without_uplift"] = round(sum(unit[r["level"]] * r["n"] for r in rows), 2)
json.dump(res, open(f"{OUT}/phase2_cost_estimate_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, ensure_ascii=False, indent=1))

# ---- 期待ラベルの測定可能性 ----
fx = json.load(open(f"{OUT}/shortlists_fixed_02.json", encoding="utf-8"))["articles"]
LABELS = {
    "coffee": {"good": ["time lag", "push prices up", "be behind price increases", "show up", "come down", "raw bean", "price tag", "lag"],
               "article_specific_creative(受入2の分母)": ["two numbers in the ring", "in the ring", "its own hidden clock", "hidden clock"],
               "keep_check_only": ["pump one's fist"],
               "low_priority_relative": ["take time", "right away", "on a regular basis", "price measure", "retail prices", "usual cup"],
               "never_fragment": ["be behind", "been behind price increases"]},
    "meta": {"good": ["behind the scenes", "contract workers", "concierge", "bargain", "by mistake"], "avoid": ["of a", "calls to", "call it", "calls it", "end of", "needed to"]},
    "hormuz": {"good": ["give back gains", "sea blockade", "brent crude futures", "take a sharp turn", "center stage"], "avoid": ["settle at", "take for", "gave back"]},
}
cov = {}
for art, groups in LABELS.items():
    for lvl in ("std", "adv"):
        e = fx[f"{art}_{lvl}"]
        cur = {c["canonical_form"].lower() for c in e["current"]["candidates"]}
        grd = {c["canonical_form"].lower() for c in e["alt_precision_guarded"]["candidates"]}
        for g, items in groups.items():
            for it in items:
                k = it.lower()
                in_c, in_g = k in cur, k in grd
                cov.setdefault(f"{art}_{lvl}", {}).setdefault(g, {})[it] = {"in_current": in_c, "in_guarded": in_g,
                                                                          "comparable_C0_vs_C2": in_c and in_g,
                                                                          "measurable_by_method1": "both" if (in_c and in_g) else ("guarded_only" if in_g else ("current_only" if in_c else "absent_in_both"))}
absent_both = sorted({(a, it) for a, v in cov.items() for g, items in v.items() for it, d in items.items() if d["measurable_by_method1"] == "absent_in_both"})
json.dump({"note": "期待ラベル候補が各shortlist構成(current/alt_precision_guarded)に存在するか。比較(C0 vs C2)は『両方に存在する候補』に限る。guarded_only/current_onlyは条件間の候補差(U3等)で比較から除外。absent_in_bothは方式1では測定不能。",
           "coverage": cov, "absent_in_both": [list(x) for x in absent_both]}, open(f"{OUT}/phase2_label_coverage_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("absent_in_both:", absent_both)
for a, v in cov.items():
    for g, items in v.items():
        print(a, g, {it: d["measurable_by_method1"] for it, d in items.items() if d["measurable_by_method1"] != "absent_in_both"})
