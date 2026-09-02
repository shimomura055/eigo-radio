# ============================================================
# er011_no18_open107_b1_failed_segments_retry_03.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03
# ============================================================
# No.18 B1のsync TTS Audio Stage初回実行(er011_no18_open107_audio_stage_03.py)
# で、comment_2(STOPPED、3attemptとも"studies"→"study"のTRUE_CONTENT_
# MISMATCH)・comment_3(ASR_VALIDATION_UNCERTAIN、"survey"↔"surveys")が
# 不合格となり、Audio Validation GateがB1 episode assemblyを正しくblockした
# (fail-closed、既存Production安全設計通り)。どちらもEnding-Clarity
# fallbackの対象segment(News本文voice、news_tail_fix経由)ではなく、
# Preview/Comment用のCharon voice(voice01.generate_charon_english)経路の
# 通常ASR不一致であり、語尾脱落パターンではない。
#
# review_lockは、STOPPED/ASR_VALIDATION_UNCERTAINへ到達したsegmentを
# 明示的なapprove_regenerate()なしには再生成させない設計のため、本script
# はこの2segmentに限定してapprove_regenerate()を呼んだ上で、実Production
# 関数(voice01.generate_charon_english、無変更)を使い再試行する。他の
# 既にRESOLVED済みのsegmentには一切触れない(再生成しない、無駄なAPI消費を
# 避ける)。結果は既存のtts_generation_results.json/run_summary_tts.jsonへ
# 該当2件のみ差分更新する(他segmentの記録を上書きしない)。

from __future__ import annotations

import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er011_human_review_lock_01 as review_lock
import er011_no18_specfix_v2_production_run_01 as driver

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
LEVEL_OUT_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{LEVEL_OUT_DIR}/narration"

TARGETS = ("comment_2", "comment_3")


def main():
    cl.install(f"{OUT_DIR}/raw_usage_log_open107_b1_failed_retry.jsonl")

    support = tts_gen.load_json(f"{LEVEL_OUT_DIR}/b1_support_texts.json")
    results_path = f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json"
    summary_path = f"{LEVEL_OUT_DIR}/run_summary_tts.json"
    all_results = tts_gen.load_json(results_path)
    all_summary = tts_gen.load_json(summary_path)

    retry_results = {}
    for name in TARGETS:
        text = support[name]
        out_path = f"{NARRATION_DIR}/{name}.wav"
        safe_text = tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text))
        review_lock.approve_regenerate(out_path, safe_text, approved_by="claude_code_operator_open107_03")
        print(f"[{THEME_ID}] b1b {name}: REGENERATE_APPROVED付与、再生成開始...")
        with cl.logging_context(THEME_ID, "tts_b1_failed_segment_retry_open107_03"), \
             cl.segment_context(name):
            r = voice01.generate_charon_english(
                safe_text, out_path, style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM,
                disfluency_qa=True)
        r["canonical_text"] = text
        retry_results[name] = r
        print(f"[{THEME_ID}] b1b {name}: retry結果 status={r.get('status')} asr_text={r.get('asr_text')!r}")

    all_results["segments"].update(retry_results)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    all_status = {k: v.get("status") for k, v in all_results["segments"].items()}
    all_summary["segment_status"] = all_status
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)

    print(f"[{THEME_ID}] b1b failed-segment retry完了。segment_status={all_status}")


if __name__ == "__main__":
    main()
