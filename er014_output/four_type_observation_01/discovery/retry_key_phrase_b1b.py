# ============================================================
# er014_output/four_type_observation_01/discovery/retry_key_phrase_b1b.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE(追加操作)
#
# 目的: run_discovery_complete.py 1回目実行でB1B Key Phrase選定が
# KEY_WORDS_STRUCTURE_INVALID(1件: "have agency"が有限動詞を含むとして
# 既存Validatorに不合格)となったため、既存run_key_phrases()(無変更)を
# もう一度呼び出す(単純な運用上の再試行。新Validator/QA変更ではない、
# production側のmax_attempts=1という既存の1回制限に対する手動再実行)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import run_discovery_fix_b1b_kp as prev_driver

BASE_DIR = prev_driver.BASE_DIR
LOG_PATH = prev_driver.LOG_PATH
THEME_ID = prev_driver.THEME_ID


def main():
    prev_driver.cl.install(LOG_PATH)
    with open(LOG_PATH, encoding="utf-8") as f:
        baseline_lines = f.readlines()
    baseline_line_count = len(baseline_lines)

    with open(f"{BASE_DIR}/b1b/article.md", encoding="utf-8") as f:
        b1b_text = f.read()

    kp_dir_b1b = f"{BASE_DIR}/key_phrases/b1b"
    kp_b1b = prev_driver.scaffold_gen.run_key_phrases(
        b1b_text, kp_dir_b1b, f"{THEME_ID}_b1b_complete_retry2", "B1-B(N3-01, fact-fix complete, retry2)",
        process="B1_SUPPORT")
    kp_b1b_status = (kp_b1b["canonicalization"] or {}).get("status") if kp_b1b["canonicalization"] else kp_b1b["selection"]["status"]
    print(f"[{THEME_ID}][COMPLETE][KP_B1B_RETRY2] status={kp_b1b_status}")

    with open(LOG_PATH, encoding="utf-8") as f:
        all_lines = f.readlines()
    new_lines = all_lines[baseline_line_count:]
    this_retry_cost_jpy = round(prev_driver._lines_cost_jpy(new_lines), 2)
    print(f"[{THEME_ID}][COMPLETE][KP_B1B_RETRY2] cost_jpy={this_retry_cost_jpy} calls={len(new_lines)}")

    with open(f"{BASE_DIR}/key_phrase_b1b_retry2_result.json", "w", encoding="utf-8") as f:
        json.dump({"status": kp_b1b_status, "cost_jpy": this_retry_cost_jpy, "calls": len(new_lines),
                    "redundancy_qa": kp_b1b.get("redundancy_qa")}, f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
    sys.exit(0)
