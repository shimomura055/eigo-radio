# ============================================================
# er011_open109_110_cost_compute_04.py
# ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04
# ============================================================
# 既存の共有pricingヘルパー(er011_specfix_cost_compute_01.summarize()等)を
# 無変更で再利用し、本session内で新規に生成した全raw_usage_logを、
# A2/B1・Production/Trialを分離して集計するだけの薄いwrapper
# (新しいpricingロジックは追加しない、前回session[er011_open107_audio_
# stage_03_cost_compute.py]と同じ方針)。

from __future__ import annotations

import json
import os

import er011_specfix_cost_compute_01 as base

OUT_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2"

LOGS = {
    "a2_writer_open109": f"{OUT_DIR}/raw_usage_log_open109_a2_writer.jsonl",
    "a2_support_kp_open109": f"{OUT_DIR}/raw_usage_log_open109_a2_support.jsonl",
    "a2_audio_open109": f"{OUT_DIR}/raw_usage_log_open109_a2_audio.jsonl",
    "b1_comment2_ending_clarity_retry_open110": f"{OUT_DIR}/raw_usage_log_open110_comment2_ending_clarity_retry.jsonl",
    "survey_diagnostic_trial_open110": "er011_output/open110_survey_diagnostic_04/raw_usage_log.jsonl",
}

if __name__ == "__main__":
    summaries = {}
    grand_total_jpy = 0.0
    grand_total_calls = 0
    for label, path in LOGS.items():
        if not os.path.exists(path):
            continue
        s = base.summarize(path)
        summaries[label] = s
        grand_total_jpy += s["total_jpy"]
        grand_total_calls += s["total_calls"]

    a2_production_jpy = sum(summaries[k]["total_jpy"] for k in
                             ("a2_writer_open109", "a2_support_kp_open109", "a2_audio_open109") if k in summaries)
    b1_production_jpy = summaries.get("b1_comment2_ending_clarity_retry_open110", {}).get("total_jpy", 0.0)
    trial_jpy = summaries.get("survey_diagnostic_trial_open110", {}).get("total_jpy", 0.0)

    result = {
        "per_log": summaries,
        "grand_total_jpy": round(grand_total_jpy, 1),
        "grand_total_calls": grand_total_calls,
        "a2_production_jpy": round(a2_production_jpy, 1),
        "b1_production_jpy": round(b1_production_jpy, 1),
        "trial_jpy": round(trial_jpy, 1),
    }
    with open(f"{OUT_DIR}/cost_summary_open109_110_04.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"grand_total_jpy={result['grand_total_jpy']} grand_total_calls={grand_total_calls} "
          f"a2_production={result['a2_production_jpy']} b1_production={result['b1_production_jpy']} "
          f"trial={result['trial_jpy']}")
    for label, s in summaries.items():
        print(f"  {label}: {s['total_jpy']}円 ({s['total_calls']}件) {s['by_stage_category_jpy']}")
