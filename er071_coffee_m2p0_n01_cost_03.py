# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03: Coffee runのstage別費用集計(runnerのcompute_cost_jpy_so_farを再利用、API呼出なし)。"""
import collections, json, os, sys, tempfile
sys.path.insert(0, os.getcwd())
import er019_family_x_audio_production_runner_01 as R
D = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01"
rows = [json.loads(l) for l in open(f"{D}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
groups = collections.defaultdict(list)
for r in rows:
    seg = r.get("segment") or ""
    th = r.get("theme") or ""
    lv = "b1b" if ("b1b" in th or "b1b" in seg) else ("a2" if ("a2" in th or "a2" in seg) else "?")
    key = (r.get("stage"), r.get("provider"), lv)
    groups[key].append(r)
out = []
for key, rs in sorted(groups.items(), key=lambda kv: str(kv[0])):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        for r in rs:
            f.write(json.dumps(r) + "\n")
    jpy, _ = R.compute_cost_jpy_so_far(f.name)
    os.unlink(f.name)
    out.append({"stage": key[0], "provider": key[1], "level_hint": key[2], "n_calls": len(rs), "jpy": round(jpy, 3),
                "segments_sample": sorted({(r.get("segment") or "") for r in rs})[:6]})
tot, byp = R.compute_cost_jpy_so_far(f"{D}/raw_usage_log.jsonl")
kp_calls = [r for r in rows if r.get("stage") == "scaffold"]
res = {"total_jpy": round(tot, 2), "by_provider": byp, "budget_guardrail_jpy_this_delegation": 30, "run_dir_baseline_before_d03_jpy": 25.70, "groups": out, "n_records": len(rows),
       "opus9_kp_llm_in_raw_usage_log": {"scaffold_records": len(kp_calls), "models": sorted({r.get("model_id") for r in kp_calls}), "segments": sorted({r.get("segment") for r in kp_calls})}}
json.dump(res, open("er071_output/m2p0_n01_production_wiring_01/cost_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:3500])
