import sys, json, os
sys.path.insert(0, os.getcwd())
import er019_family_x_entertainment_production_runner_01 as r
base = "er052_output/factlock_astra_e2e_trial_01/stage_r"
out = {}
for slug in sys.argv[1:]:
    p = f"{base}/{slug}/raw_usage_log.jsonl"
    if not os.path.exists(p):
        continue
    b = r.compute_stage_cost_breakdown(p)
    rows = []
    for l in open(p, encoding="utf-8"):
        d = json.loads(l)
        rows.append({"stage": d.get("stage"), "model": d.get("model_id") or d.get("model"),
                     "in": d.get("input_tokens"), "out": d.get("output_tokens"),
                     "ws": d.get("web_search_call_count")})
    out[slug] = {"cost": b, "calls": rows}
print(json.dumps(out, ensure_ascii=False, indent=1))
