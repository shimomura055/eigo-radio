# ============================================================
# er011_no18_open110_comment2_ending_clarity_retry_04.py
# ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04
# ============================================================
# comment_2("The studies suggest..."->ASR"The study suggests...")は
# OPEN-107 Ending-Clarity fallbackの対象("studies"の複数マーカー/z/脱落)
# であるのに、Comment segmentがNews本文loopと別経路(voice01.
# generate_charon_english直接呼び出し)だったため、これまでfallbackへ
# 到達できていなかった(配線漏れ、er011_ending_clarity_fallback_01.pyの
# generate_charon_english_with_ending_clarity_fallback()で解消済み)。
#
# 本scriptは、comment_2 1segmentのみをこの新しいProduction正式経路で
# 再生成し、Ending-Clarity fallbackが実Production呼び出しで実発火する
# runtime evidenceを採取する。comment_3は対象外(survey->surveysは
# "追加"であり"脱落"ではないため、そもそもtriggerしない設計、別途診断)。
# 他の既にRESOLVED済みsegmentには一切触れない。

from __future__ import annotations

import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er011_ending_clarity_fallback_01 as ending_clarity
import er011_human_review_lock_01 as review_lock
import er011_no18_specfix_v2_production_run_01 as driver

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
LEVEL_OUT_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{LEVEL_OUT_DIR}/narration"

TARGET = "comment_2"


def main():
    cl.install(f"{OUT_DIR}/raw_usage_log_open110_comment2_ending_clarity_retry.jsonl")

    support = tts_gen.load_json(f"{LEVEL_OUT_DIR}/b1_support_texts.json")
    results_path = f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json"
    summary_path = f"{LEVEL_OUT_DIR}/run_summary_tts.json"
    all_results = tts_gen.load_json(results_path)
    all_summary = tts_gen.load_json(summary_path)

    text = support[TARGET]
    out_path = f"{NARRATION_DIR}/{TARGET}.wav"
    safe_text = tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text))
    review_lock.approve_regenerate(out_path, safe_text, approved_by="claude_code_operator_open109_110_04")
    print(f"[{THEME_ID}] b1b {TARGET}: REGENERATE_APPROVED付与、Ending-Clarity fallback配線済み経路で再生成開始...")

    with cl.logging_context(THEME_ID, "tts_comment2_ending_clarity_retry_open110_04"), \
         cl.segment_context(TARGET):
        r = ending_clarity.generate_charon_english_with_ending_clarity_fallback(
            safe_text, out_path, style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM,
            disfluency_qa=True)
    r["canonical_text"] = text
    print(f"[{THEME_ID}] b1b {TARGET}: 結果 status={r.get('status')} "
          f"ending_clarity_fallback_used={r.get('ending_clarity_fallback_used')} "
          f"asr_text={r.get('asr_text')!r}")

    all_results["segments"][TARGET] = r
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    all_status = {k: v.get("status") for k, v in all_results["segments"].items()}
    all_summary["segment_status"] = all_status
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)

    with open(f"{LEVEL_OUT_DIR}/audit/open110_comment2_ending_clarity_runtime_evidence_04.json",
              "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2, default=str)

    print(f"[{THEME_ID}] b1b comment_2 Ending-Clarity retry完了。status={all_status[TARGET]}")


if __name__ == "__main__":
    main()
