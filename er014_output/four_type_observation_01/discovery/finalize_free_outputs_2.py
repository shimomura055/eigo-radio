# ============================================================
# er014_output/four_type_observation_01/discovery/finalize_free_outputs_2.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE(継続、CONT1)
#
# 目的: run_discovery_complete_2.pyがBudgetStopで途中終了したため、
# A2最終QA再実行以降の工程(jargon最終確認・Cross-Level Consistency)へ
# 到達できなかった。この2つは決定的ローカル処理(API呼び出しなし)なので、
# 追加コスト¥0のまま完成させる。あわせてproduction_set_cost.jsonの
# 古い(2026-09-14 17:12時点、Key Phrase B1B retry2成功より前に書かれた)
# 'key_phrase_b1b_status'記述を、実際のパイプライン最終状態(selector
# PASS→canonicalization REVIEW_REQUIRED→redundancy NG)へ訂正する
# (新規API呼び出しなし、既存ディスク上JSONの読み取りのみ)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import run_discovery_complete as base

BASE_DIR = base.BASE_DIR

with open(f"{BASE_DIR}/a2/article.md", encoding="utf-8") as f:
    a2_text = f.read()
with open(f"{BASE_DIR}/b1b/article.md", encoding="utf-8") as f:
    b1b_text = f.read()

jargon_final = {"a2": base.prev_driver.jargon_scan(a2_text), "b1b": base.prev_driver.jargon_scan(b1b_text)}
with open(f"{BASE_DIR}/run_result_complete_2.json", encoding="utf-8") as f:
    prior_result = json.load(f)

with open(f"{BASE_DIR}/jargon_scan_final.json", "w", encoding="utf-8") as f:
    json.dump({
        "before_this_task": {"a2": {"hit_count": 0}, "b1b": {"hit_count": 0}},
        "after_f002_and_qa_fix": prior_result.get("jargon_after_fix"),
        "final_local_recheck_zero_cost": {"a2": jargon_final["a2"]["hit_count"],
                                           "b1b": jargon_final["b1b"]["hit_count"]},
        "note": ("run_discovery_complete_2.py hit BudgetStop before a2_final_qa_recheck; this final "
                 "jargon recheck was computed afterward with zero additional API cost (jargon_scan is "
                 "a local deterministic regex check, no LLM call) using the same final a2/article.md "
                 "and b1b/article.md text that a2_final_qa_recheck would have used."),
    }, f, ensure_ascii=False, indent=2)
print(f"jargon_final(zero-cost recheck): a2={jargon_final['a2']['hit_count']} b1b={jargon_final['b1b']['hit_count']}")

cross_md, cross_consistent = base.build_cross_level_consistency_md(a2_text, b1b_text)
with open(f"{BASE_DIR}/cross_level_consistency.md", "w", encoding="utf-8") as f:
    f.write(cross_md)
print(f"cross_level_consistent={cross_consistent}")

# production_set_cost.json: key_phrase_b1b_status訂正(新規APIなし、既存
# key_phrases/b1b/配下JSONの読み取りのみ)
kp_dir_b1b = f"{BASE_DIR}/key_phrases/b1b"
with open(f"{kp_dir_b1b}/keywords_runtime_metadata.json", encoding="utf-8") as f:
    kp_selector = json.load(f)
with open(f"{kp_dir_b1b}/canonicalization_runtime_metadata.json", encoding="utf-8") as f:
    kp_canon = json.load(f)
with open(f"{kp_dir_b1b}/keyphrase_redundancy_qa.json", encoding="utf-8") as f:
    kp_redundancy = json.load(f)

kp_dir_a2 = f"{BASE_DIR}/key_phrases/a2"
with open(f"{kp_dir_a2}/keywords_runtime_metadata.json", encoding="utf-8") as f:
    kp_a2_selector = json.load(f)
with open(f"{kp_dir_a2}/canonicalization_runtime_metadata.json", encoding="utf-8") as f:
    kp_a2_canon = json.load(f)
with open(f"{kp_dir_a2}/keyphrase_redundancy_qa.json", encoding="utf-8") as f:
    kp_a2_redundancy = json.load(f)

prod_cost_path = f"{BASE_DIR}/production_set_cost.json"
with open(prod_cost_path, encoding="utf-8") as f:
    prod_cost = json.load(f)
prod_cost["key_phrase_a2_status_corrected"] = {
    "selector_final_status": kp_a2_selector.get("final_status"),
    "canonicalization_final_status": kp_a2_canon.get("final_status"),
    "redundancy_qa_status": kp_a2_redundancy.get("status"),
    "overall": "PASS" if (kp_a2_canon.get("final_status") == "CANONICALIZATION_PASS" and
                           kp_a2_redundancy.get("status") == "REDUNDANCY_PASS") else "NOT_FULLY_PASS",
}
prod_cost["key_phrase_b1b_status_corrected"] = {
    "attempt1_selector_status": "KEY_WORDS_STRUCTURE_INVALID (run_discovery_complete.py, original call)",
    "attempt2_selector_status": kp_selector.get("final_status") + " (retry_key_phrase_b1b.py, retry2)",
    "attempt2_canonicalization_status": kp_canon.get("final_status"),
    "attempt2_redundancy_qa_status": kp_redundancy.get("status"),
    "attempt2_redundancy_issue": (kp_redundancy.get("duplicate_pairs") or [{}])[0].get("reasoning")
        if kp_redundancy.get("duplicate_pairs") else None,
    "overall": "NOT_FULLY_PASS (selector PASS but canonicalization REVIEW_REQUIRED and redundancy NG; "
               "2 of max-3 allowed run_key_phrases() calls used; superseded the stale "
               "'key_phrase_b1b_status' note written before this task, which said '2回とも失敗' -- "
               "that was based on incomplete reading; corrected here from actual on-disk artifacts, "
               "zero new API cost)",
    "calls_used_of_max_3": 2,
}
with open(prod_cost_path, "w", encoding="utf-8") as f:
    json.dump(prod_cost, f, ensure_ascii=False, indent=2, default=str)
print("production_set_cost.json key_phrase status corrected (zero new API cost).")
