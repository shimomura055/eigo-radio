# ============================================================
# er011_open107_audio_stage_03_cost_compute.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03
# ============================================================
# 既存の共有pricingヘルパー(er011_specfix_cost_compute_01.summarize()等)
# を無変更で再利用し、今回session内で新規に生成した全raw_usage_logを
# 集計するだけの薄いwrapper(新しいpricingロジックは追加しない)。

from __future__ import annotations

import json
import os

import er011_specfix_cost_compute_01 as base

OUT_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2"
EVIDENCE_DIR = "er011_output/open107_production_wiring_runtime_evidence_03"

LOGS = [
    f"{OUT_DIR}/raw_usage_log_open107_b1_text_patch_requa.jsonl",
    f"{OUT_DIR}/raw_usage_log_open107_support.jsonl",
    f"{OUT_DIR}/raw_usage_log_open107_audio.jsonl",
    f"{OUT_DIR}/raw_usage_log_open107_b1_failed_retry.jsonl",
    f"{EVIDENCE_DIR}/raw_usage_log.jsonl",
]

if __name__ == "__main__":
    summaries = {}
    grand_total_jpy = 0.0
    grand_total_calls = 0
    for path in LOGS:
        if not os.path.exists(path):
            continue
        s = base.summarize(path)
        summaries[path] = s
        grand_total_jpy += s["total_jpy"]
        grand_total_calls += s["total_calls"]
    result = {"per_log": summaries, "grand_total_jpy": round(grand_total_jpy, 1), "grand_total_calls": grand_total_calls}
    with open(f"{OUT_DIR}/cost_summary_open107_audio_stage_03.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"grand_total_jpy={result['grand_total_jpy']} grand_total_calls={grand_total_calls}")
    for path, s in summaries.items():
        print(f"  {path}: {s['total_jpy']}円 ({s['total_calls']}件) {s['by_stage_category_jpy']}")
