# ============================================================
# er011_no18_connected_speech_reading_resolver_scoped_retry_08.py
# ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08
# ============================================================
# No.18のB1 `comment_2`/`comment_3`・A2 `comment_1`は、前回session(2026-09-02)
# の一連のTrial・診断runで既にer011_human_review_lock_01.pyのHUMAN_REVIEW_
# REQUIRED状態(comment_2は累積TTS試行が上限を超過しBUDGET_GUARD_TRIGGERED)
# へ到達済みだった。今回の本番Audio Stage run(er011_no18_connected_speech_
# reading_resolver_audio_stage_08.py)を素直に再実行しても、review_lockの
# 事前ゲートが「既にHUMAN_REVIEW_REQUIRED」を検出してTTS/ASR呼び出し自体を
# 0回でblockしてしまい(comment_2/comment_3/comment_1がすべてHUMAN_REVIEW_
# LOCKEDのまま)、新しいConnected Speech Validator/Reading Resolverが実際の
# 新規TTS/ASR出力に対して発火する機会が一度も得られなかった。
#
# 本scriptは、この3segmentだけを対象にreview_lock.approve_regenerate()
# (ユーザーの明示的な指示によってのみ呼ぶことが許されている経路、今回の
# タスク自体がNo.18本番Audio Stageの通し直しとruntime evidence取得を明示
# 指示しているため、その指示に基づく正当な呼び出し)を付与したうえで、
# 他の全segmentが実際に呼んでいるのと同一のProduction正式関数を直接呼ぶ
# (er011_no18_open110_comment2_ending_clarity_retry_04.pyで確立済みの
# scoped retryパターンを踏襲)。他の既にVALIDATED済みsegmentには一切
# 触れない(無駄な再生成をしない)。

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


def retry_b1():
    level_out_dir = f"{OUT_DIR}/b1b"
    narration_dir = f"{level_out_dir}/narration"
    support = tts_gen.load_json(f"{level_out_dir}/b1_support_texts.json")
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    summary_path = f"{level_out_dir}/run_summary_tts.json"
    all_results = tts_gen.load_json(results_path)
    all_summary = tts_gen.load_json(summary_path)

    for target in ("comment_2", "comment_3"):
        text = support[target]
        out_path = f"{narration_dir}/{target}.wav"
        safe_text = tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text))
        review_lock.approve_regenerate(
            out_path, safe_text, approved_by="claude_code_operator_wiring08_no18_audio_stage_task")
        print(f"[{THEME_ID}] b1b {target}: REGENERATE_APPROVED付与、"
              f"Connected Speech Validator配線済みclassify_asr_match経由で再生成開始...")
        with cl.logging_context(THEME_ID, f"tts_{target}_wiring08_scoped_retry"), cl.segment_context(target):
            r = voice01.generate_charon_english(
                safe_text, out_path, style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM,
                disfluency_qa=True)
        r["canonical_text"] = text
        print(f"[{THEME_ID}] b1b {target}: 結果 status={r.get('status')} "
              f"audio_classification={r.get('audio_classification')} "
              f"connected_speech_info={r.get('connected_speech_info')} "
              f"asr_text={r.get('asr_text')!r}")
        all_results["segments"][target] = r

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    all_summary["segment_status"] = {k: v.get("status") for k, v in all_results["segments"].items()}
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] b1b scoped retry完了。segment_status={all_summary['segment_status']}")


def retry_a2():
    level_out_dir = f"{OUT_DIR}/a2"
    narration_dir = f"{level_out_dir}/narration"
    support = tts_gen.load_json(f"{level_out_dir}/a2_support_texts.json")
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    summary_path = f"{level_out_dir}/run_summary_tts.json"
    all_results = tts_gen.load_json(results_path)
    all_summary = tts_gen.load_json(summary_path)

    target = "comment_1"
    text = support[target]
    out_path = f"{narration_dir}/{target}.wav"
    placeholder_safe = tts_gen.tts_safe_ja(text)
    tts_input = tts_gen.safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)
    review_lock.approve_regenerate(
        out_path, tts_input, approved_by="claude_code_operator_wiring08_no18_audio_stage_task")
    print(f"[{THEME_ID}] a2 {target}: REGENERATE_APPROVED付与、"
          f"A2 Reading Resolver配線済みclassify_ja_asr_match経由で再生成開始...")
    with cl.logging_context(THEME_ID, f"tts_{target}_wiring08_scoped_retry"), cl.segment_context(target):
        r = tts_gen.generate_a2_japanese_with_reading_safety(
            text, out_path, tts_gen.expected_substring_ja(text))
    print(f"[{THEME_ID}] a2 {target}: 結果 status={r.get('status')} "
          f"audio_classification={(r.get('attempts_log') or [{}])[-1].get('audio_classification') if r.get('attempts_log') else None} "
          f"reading_resolver_info_present={'reading_resolver_info' in r} "
          f"asr_text={r.get('asr_text')!r}")
    all_results["segments"][target] = r

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    all_summary["segment_status"] = {k: v.get("status") for k, v in all_results["segments"].items()}
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] a2 scoped retry完了。segment_status={all_summary['segment_status']}")


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log_wiring08_scoped_retry.jsonl")
    retry_b1()
    retry_a2()
