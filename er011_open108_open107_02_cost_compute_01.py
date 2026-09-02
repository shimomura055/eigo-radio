# ============================================================
# er011_open108_open107_02_cost_compute_01.py
# ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02
# ============================================================
# 今回作業(Track A: OPEN-108 B1 Ledger精密化+再生成、Track B: OPEN-107
# Ending-Clarity fallback Trial)のcostを、既存er011_specfix_cost_compute_01.py
# のprice_tiered/categorize/summarize実装をそのまま再利用して分離集計する
# (新しい単価ロジックは書かない)。

from __future__ import annotations

import json

import er011_specfix_cost_compute_01 as base

THEME_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2"

track_a_logs = [
    f"{THEME_DIR}/raw_usage_log_open108.jsonl",
    f"{THEME_DIR}/raw_usage_log_open108_support.jsonl",
]
track_b_log = "er011_output/open107_ending_clarity_fallback_trial_02/raw_usage_log.jsonl"


def summarize_multi(paths):
    combined = {"by_stage_category_jpy": {}, "call_counts": {}, "total_usd": 0.0, "total_jpy": 0.0, "total_calls": 0}
    for p in paths:
        s = base.summarize(p)
        for k, v in s["by_stage_category_jpy"].items():
            combined["by_stage_category_jpy"][k] = round(combined["by_stage_category_jpy"].get(k, 0) + v, 2)
        for k, v in s["call_counts"].items():
            combined["call_counts"][k] = combined["call_counts"].get(k, 0) + v
        combined["total_usd"] += s["total_usd"]
        combined["total_jpy"] += s["total_jpy"]
        combined["total_calls"] += s["total_calls"]
    combined["total_usd"] = round(combined["total_usd"], 4)
    combined["total_jpy"] = round(combined["total_jpy"], 1)
    combined["source_logs"] = paths
    return combined


if __name__ == "__main__":
    print("=== Track A: OPEN-108 Ledger精密化後 B1 Writer+Support再生成 ===")
    track_a = summarize_multi(track_a_logs)
    print(json.dumps(track_a, ensure_ascii=False, indent=2))

    print("\n=== Track B: OPEN-107 Ending-Clarity Fallback Trial ===")
    track_b = base.summarize(track_b_log)
    print(json.dumps(track_b, ensure_ascii=False, indent=2))

    with open(f"{THEME_DIR}/cost_summary_open108.json", "w", encoding="utf-8") as f:
        json.dump(track_a, f, ensure_ascii=False, indent=2)
    with open("er011_output/open107_ending_clarity_fallback_trial_02/cost_summary_trial.json",
              "w", encoding="utf-8") as f:
        json.dump(track_b, f, ensure_ascii=False, indent=2)

    print(f"\nGRAND TOTAL (Track A + Track B、分離): "
          f"TrackA=Y{track_a['total_jpy']} TrackB=Y{track_b['total_jpy']}")
