# ============================================================
# er006_pool_benches_luna_cost_compare.py
# ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Sol版(pool_benches) vs
# Luna版(pool_benches_luna)のCost/Waste比較
# ============================================================
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

USD_JPY = 160.0
LUNA_IN, LUNA_CACHED, LUNA_OUT = 0.20, 0.02, 1.20
SOL_IN, SOL_CACHED, SOL_OUT = 5.00, 0.50, 30.00
GEMINI_IN, GEMINI_OUT = 1.00, 20.00
AZURE_HOUR = 1.00
SEARCH_PER_1K = 10.00

with open("er006_output/pool_pilot_01/raw_usage_log.jsonl", encoding="utf-8") as f:
    RECORDS = [json.loads(l) for l in f]


def cost_jpy(r):
    if not r.get("success"):
        return 0.0
    provider, model_id = r["provider"], r.get("model_id") or ""
    if provider == "openai":
        it, ct, ot = r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        if "sol" in model_id:
            cost = (billable_in / 1e6) * SOL_IN + (ct / 1e6) * SOL_CACHED + (ot / 1e6) * SOL_OUT
        else:
            cost = (billable_in / 1e6) * LUNA_IN + (ct / 1e6) * LUNA_CACHED + (ot / 1e6) * LUNA_OUT
        cost += ((r.get("web_search_call_count") or 0) / 1000) * SEARCH_PER_1K
        return cost * USD_JPY
    if provider == "gemini":
        return ((r.get("input_tokens") or 0) / 1e6 * GEMINI_IN + (r.get("output_tokens") or 0) / 1e6 * GEMINI_OUT) * USD_JPY
    if provider == "azure":
        return ((r.get("audio_duration_submitted_seconds") or 0) / 3600) * AZURE_HOUR * USD_JPY
    return 0.0


def stage_category(stage):
    if stage.startswith("writer_"):
        return "writer"
    if stage.startswith("support_"):
        return "support"
    if stage.startswith("research_"):
        return "research"
    if stage == "tts_b1" or stage == "tts_a2":
        return "audio"
    return "other"


def level_of(stage):
    if stage.endswith("_b1"):
        return "b1"
    if stage.endswith("_a2"):
        return "a2"
    return "shared"


def summarize(theme_id):
    recs = [r for r in RECORDS if r["theme"] == theme_id]
    by_stage_provider = defaultdict(lambda: {"cost_jpy": 0.0, "n_calls": 0})
    for r in recs:
        c = cost_jpy(r)
        key = (r["stage"], r["provider"])
        by_stage_provider[key]["cost_jpy"] += c
        by_stage_provider[key]["n_calls"] += 1

    totals = defaultdict(lambda: defaultdict(float))
    for (stage, provider), v in by_stage_provider.items():
        level = level_of(stage)
        cat = stage_category(stage)
        if cat == "audio":
            sub = "tts" if provider == "gemini" else "asr" if provider == "azure" else "other"
            totals[level][f"audio_{sub}_jpy"] += v["cost_jpy"]
        else:
            totals[level][f"{cat}_jpy"] += v["cost_jpy"]

    n_calls_total = sum(v["n_calls"] for v in by_stage_provider.values())
    actual_total = sum(sum(d.values()) for d in totals.values())

    # STOPPED segment count (from run_summary_tts.json if present)
    n_stopped = {}
    for level_key, level_dir in [("b1", "b1b"), ("a2", "a2")]:
        try:
            summary = json.load(open(f"er006_output/pool_pilot_01/{theme_id}/{level_dir}/run_summary_tts.json", encoding="utf-8"))
            stopped_main = [k for k, v in summary["segment_status"].items() if v == "STOPPED"]
            stopped_kp = [f"kp{k}_{kk}" for k, v in summary["key_phrase_status"].items() for kk, vv in v.items() if vv == "STOPPED"]
            uncertain_main = [k for k, v in summary["segment_status"].items() if v == "ASR_VALIDATION_UNCERTAIN"]
            uncertain_kp = [f"kp{k}_{kk}" for k, v in summary["key_phrase_status"].items() for kk, vv in v.items() if vv == "ASR_VALIDATION_UNCERTAIN"]
            n_stopped[level_key] = {"stopped": stopped_main + stopped_kp, "uncertain": uncertain_main + uncertain_kp}
        except FileNotFoundError:
            n_stopped[level_key] = None

    return {
        "theme_id": theme_id, "n_calls_total": n_calls_total, "actual_total_jpy": round(actual_total, 1),
        "by_level": {k: {kk: round(vv, 1) for kk, vv in v.items()} for k, v in totals.items()},
        "stopped_and_uncertain": n_stopped,
    }


if __name__ == "__main__":
    sol = summarize("pool_benches")
    luna = summarize("pool_benches_luna")
    print("=== SOL (pool_benches) ===")
    print(json.dumps(sol, ensure_ascii=False, indent=2))
    print("=== LUNA (pool_benches_luna) ===")
    print(json.dumps(luna, ensure_ascii=False, indent=2))

    json.dump({"sol": sol, "luna": luna},
              open("er006_output/pool_pilot_01/pool_benches_sol_vs_luna_cost.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
