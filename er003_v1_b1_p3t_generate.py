# ============================================================
# er003_v1_b1_p3t_generate.py
# ER-003-B1-P3T: 日本語通し音声への英語Key Phrase差し込み生成
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3t_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import numpy as np

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3r_audio as p3r
import er003_b1_p3s_audio as p3s
import er003_b1_p3t_audio as p3t

OUT_DIR = "er003_output/b1_p3t/A01"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _save_wav(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def check_p3s_span_03_raw() -> dict:
    """Step 1: 前回(ER-003-B1-P3S)raw音声の確認。機械的に判定できる
    範囲(decode可能性・duration・clipping等)のみ確認し、発音の自然さ
    そのものはINCONCLUSIVEとして記録する(指示section 5の明記通り)。"""
    path = "er003_output/b1_p3s/A01/raw/span_03_ja_after.wav"
    if not os.path.exists(path):
        return {"path": path, "exists": False, "note": "前回rawファイルが見つかりません"}
    samples, sr, ch, nframes = common.read_wav_float(path)
    metrics = common.measure_metrics(samples, sr)
    return {
        "path": path,
        "exists": True,
        "decodable": True,
        "sample_rate": sr,
        "channels": ch,
        "duration_seconds": metrics["duration_seconds"],
        "clipping_detected": metrics["clipping_detected"],
        "note": (
            "このraw音声は、ER-003-B1-P3Sの結合処理(assemble_audio)で内容を"
            "一切変更・トリムされずにそのまま結合サンプルへ使われた"
            "(P3Sのassemble_audioはチャンク間に無音を挿入するだけで、"
            "チャンク自体の内容は変更しない)。したがって、結合後に聞こえた"
            "「を」の不自然さは、この生成段階(助詞始まりの断片としての"
            "単独生成)に起因する可能性が高いと機械的に推定できる。"
            "ただし、実際に「を」がどう聞こえるか(発音の自然さそのもの)"
            "は、機械的な判定手段を持たないためINCONCLUSIVEとする。"
        ),
        "pronunciation_assessment": "INCONCLUSIVE",
    }


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    for sub in ("source", "raw", "final"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    step1_result = check_p3s_span_03_raw()

    pattern_a_sha256_before = p3t.sha256_text(p3t.SOURCE_JAPANESE_FULL_SENTENCE)
    tts_script = p3t.build_tts_japanese_script()

    with open(f"{OUT_DIR}/source/source_integrated_sentence.txt", "w", encoding="utf-8") as f:
        f.write(p3t.SOURCE_INTEGRATED_SENTENCE)
    with open(f"{OUT_DIR}/source/source_japanese_full_sentence.txt", "w", encoding="utf-8") as f:
        f.write(p3t.SOURCE_JAPANESE_FULL_SENTENCE)
    with open(f"{OUT_DIR}/source/source_english_keyword.txt", "w", encoding="utf-8") as f:
        f.write(p3t.SOURCE_ENGLISH_KEYWORD)
    with open(f"{OUT_DIR}/source/tts_japanese_script.txt", "w", encoding="utf-8") as f:
        f.write(tts_script)

    style_prefix = p3t.build_style_prefix()
    if tts_call_fn is None:
        tts_call_fn = gclient.make_tts_call_fn(p3t.VOICE_NAME)

    # --- Step 2: 日本語通し音声(1回のTTS call) ---
    ja_prompt = p3t.build_tts_prompt(tts_script, style_prefix)
    ja_pcm, ja_retries, ja_ok, ja_err = common._call_tts_with_retry(
        tts_call_fn, ja_prompt, max_retry=p3t.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ja_ok:
        return {"status": "STOPPED", "reason": f"日本語通し音声のTTSが失敗: {ja_err}", "step1": step1_result}
    _save_wav(f"{OUT_DIR}/raw/ja_full_sentence.wav", ja_pcm)

    # --- Step 3: 英語Key Phrase(別のTTS call) ---
    en_prompt = p3t.build_tts_prompt(p3t.SOURCE_ENGLISH_KEYWORD, style_prefix)
    en_pcm, en_retries, en_ok, en_err = common._call_tts_with_retry(
        tts_call_fn, en_prompt, max_retry=p3t.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not en_ok:
        return {
            "status": "STOPPED", "reason": f"英語Key PhraseのTTSが失敗: {en_err}",
            "step1": step1_result, "ja_call_count": 1 + ja_retries, "ja_retry_count": ja_retries,
        }
    _save_wav(f"{OUT_DIR}/raw/en_shot_on_target.wav", en_pcm)

    # --- Step 4: 差し込み位置の検出 ---
    ja_mono = common.pcm_bytes_to_float_mono(ja_pcm)
    en_mono = common.pcm_bytes_to_float_mono(en_pcm)

    pause_window = p3t.find_pause_window(ja_mono, common.SAMPLE_RATE)
    if pause_window is None:
        return {
            "status": "STOPPED",
            "reason": "日本語通し音声内に安全な差し込み位置(無音区間)を検出できませんでした",
            "step1": step1_result,
            "ja_call_count": 1 + ja_retries, "en_call_count": 1 + en_retries,
        }

    # --- Step 5: 結合 ---
    spliced = p3t.splice_english_into_japanese(
        ja_mono, en_mono, pause_window, common.SAMPLE_RATE, boundary_pause_seconds=p3t.JOIN_PAUSE_SECONDS)

    raw_join_path = f"{OUT_DIR}/final/A01_b1_ja_full_with_en_insert_raw.wav"
    common.write_wav_float(raw_join_path, spliced, common.SAMPLE_RATE, 1)

    # --- Step 6: Dynamics3を一度だけ適用 ---
    dynamics_result = common.apply_dynamics3_once(spliced, common.SAMPLE_RATE)
    final_path = f"{OUT_DIR}/final/A01_b1_ja_full_with_en_insert_dynamics3.wav"
    common.write_wav_float(final_path, dynamics_result.c1_samples, common.SAMPLE_RATE, 1)

    pattern_a_sha256_after = p3t.sha256_text(p3t.SOURCE_JAPANESE_FULL_SENTENCE)

    metrics_ja = common.measure_metrics(ja_mono, common.SAMPLE_RATE)
    metrics_raw_join = common.measure_metrics(spliced, common.SAMPLE_RATE)
    metrics_final = dynamics_result.metrics_c1

    wo_present = "を記録できないまま" in tts_script

    metadata = {
        "management_id": "ER-003-B1-P3T",
        "article_id": p3t.ARTICLE_ID,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "step1_previous_raw_check": step1_result,
        "source_integrated_sentence": p3t.SOURCE_INTEGRATED_SENTENCE,
        "source_japanese_full_sentence": p3t.SOURCE_JAPANESE_FULL_SENTENCE,
        "source_english_keyword": p3t.SOURCE_ENGLISH_KEYWORD,
        "tts_japanese_script": tts_script,
        "source_sha256_before": pattern_a_sha256_before,
        "source_sha256_after": pattern_a_sha256_after,
        "source_unchanged": pattern_a_sha256_before == pattern_a_sha256_after,
        "wo_present_in_tts_script": wo_present,
        "tts_model": common.MODEL_NAME,
        "voice": p3t.VOICE_NAME,
        "tts_instruction_used": style_prefix,
        "ja_call_count": 1 + ja_retries,
        "ja_retry_count": ja_retries,
        "en_call_count": 1 + en_retries,
        "en_retry_count": en_retries,
        "max_technical_retry": p3t.MAX_TTS_TECHNICAL_RETRY,
        "ja_full_sentence_path": f"{OUT_DIR}/raw/ja_full_sentence.wav",
        "ja_full_sentence_duration_seconds": metrics_ja["duration_seconds"],
        "en_keyword_path": f"{OUT_DIR}/raw/en_shot_on_target.wav",
        "en_keyword_duration_seconds": round(len(en_mono) / common.SAMPLE_RATE, 3),
        "pause_window_detection": pause_window,
        "insertion_method": (
            "日本語通し音声内の最長無音区間をRMSベースで検出し、その中心点で"
            "音声を2分割して英語Key Phraseを境界無音付きで挿入した"
            "(枠内シュートの途中や「を」の直前音を削らないよう、区間の端では"
            "なく中心を分割点に採用)。"
        ),
        "join_order": ["ja_before", "en_keyword", "ja_after"],
        "boundary_pause_seconds": p3t.JOIN_PAUSE_SECONDS,
        "boundary_pause_count": 2,
        "dynamics3_applied": dynamics_result.applied_once,
        "dynamics3_params": dynamics_result.dynamics_params,
        "loudness_matching": dynamics_result.loudness_matching,
        "raw_join_path": raw_join_path,
        "final_path": final_path,
        "final_path_format_note": (
            "MP3エンコーダ(ffmpeg/pydub)がこの環境に存在しないため、WAVのまま"
            "保存した(ER-003-B1-P3R/P3Sと同一の判断)。"
        ),
        "sample_rate": common.SAMPLE_RATE,
        "channels": 1,
        "metrics_ja_full_sentence": metrics_ja,
        "metrics_raw_join": metrics_raw_join,
        "metrics_final": metrics_final,
        "final_duration_seconds": metrics_final["duration_seconds"],
        "final_sha256": hashlib.sha256(open(final_path, "rb").read()).hexdigest(),
        "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    with open(f"{OUT_DIR}/audio_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "metadata": metadata}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("reason"))
    else:
        print(f"final_duration_seconds={result['metadata']['final_duration_seconds']}")
        print(f"source_unchanged={result['metadata']['source_unchanged']}")
        print(f"wo_present_in_tts_script={result['metadata']['wo_present_in_tts_script']}")
