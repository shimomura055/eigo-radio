"""rep30 38 run call_log.usage を gpt-6-luna / gpt-5.6-luna 単価で再計算 (¥0、offline)。
為替は rep30 記録と同一 (stage2_production_01.USD_JPY=156.88)。S1(¥3.0909, 25 batch)はusage未保存のため別掲。"""
import glob, json, statistics, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
B = os.path.join(ROOT, "er052_output", "open233_self_recovery_flow_runner_01_rep30")
USD_JPY = 156.88
PRICES = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-5.6-luna": (0.20, 0.02, 1.20)}
S1_COST_LUNA = 3.0909
def cost(u, p):
    it, ct, ot = u.get("input_tokens") or 0, u.get("cached_input_tokens") or 0, u.get("output_tokens") or 0
    return (max(it - ct, 0) / 1e6 * p[0] + ct / 1e6 * p[1] + ot / 1e6 * p[2]) * USD_JPY
fs = sorted(glob.glob(B + "/instances_s1/*.json") + glob.glob(B + "/instances_s2/*.json"))
res = {"n_runs": len(fs), "usd_jpy": USD_JPY, "models": {}}
for m, p in PRICES.items():
    per = {}
    for f in fs:
        x = json.load(open(f, encoding="utf8"))
        per[x["instance_id"] + "@" + os.path.basename(os.path.dirname(f))] = sum(cost(c["usage"], p) for c in x["call_log"])
    v = list(per.values())
    res["models"][m] = {"total": round(sum(v), 4), "mean_per_run": round(sum(v) / len(v), 4),
                        "median": round(statistics.median(v), 4), "worst": round(max(v), 4),
                        "worst_run": max(per, key=per.get)}
a, b = res["models"]["gpt-6-luna"], res["models"]["gpt-5.6-luna"]
res["ratio_5_6_over_6"] = round(b["total"] / a["total"], 3)
res["s1_note"] = {"s1_cost_luna_jpy": S1_COST_LUNA, "per_run_share_luna": round(S1_COST_LUNA / len(fs), 4),
                  "per_run_share_5_6_luna_est(x ratio)": round(S1_COST_LUNA / len(fs) * res["ratio_5_6_over_6"], 4),
                  "note": "S1 usage未保存。5.6-lunaは本体比率での推定"}
json.dump(res, open(os.path.join(os.path.dirname(__file__), "agg_cost_recalc_models_01.json"), "w", encoding="utf8"), ensure_ascii=False, indent=2)
md = ["# rep30 費用再計算(両単価、為替%.2f固定)" % USD_JPY, "", "| model | 合計 | 平均/run | 中央値 | worst |", "|---|---|---|---|---|"]
for m, r in res["models"].items():
    md.append("| %s | %.4f | %.4f | %.4f | %.4f (%s) |" % (m, r["total"], r["mean_per_run"], r["median"], r["worst"], r["worst_run"]))
md += ["", "S1(Stage1 union screen)は別掲: luna ¥%.4f/38run" % S1_COST_LUNA]
open(os.path.join(os.path.dirname(__file__), "agg_cost_recalc_models_01.md"), "w", encoding="utf8").write("\n".join(md))
print(json.dumps(res, ensure_ascii=False, indent=1))
