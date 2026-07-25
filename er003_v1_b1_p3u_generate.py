# ============================================================
# er003_v1_b1_p3u_generate.py
# ER-003-B1-P3U: 正確な語句境界への英語Key Phrase差し込み再検証・生成
# ============================================================
# 新しいTTS呼び出しは一切行わない。既存のER-003-B1-P3T音声
# (ja_full_sentence.wav / en_shot_on_target.wav)を再利用する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3u_generate.py

from __future__ import annotations

import hashlib
import json
import os

import er002_common as common
import er003_b1_p3u_audio as p3u

OUT_DIR = "er003_output/b1_p3u/A01"

_PREVIOUS_WRONG_CUT_SECONDS = 3.16  # ER-003-B1-P3Tで採用された誤った挿入位置


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run() -> dict:
    for sub in ("source", "alignment", "components", "final"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    # --- Step 0: 既存音声の再利用確認(新規TTS生成は行わない) ---
    if not os.path.exists(p3u.EXISTING_JA_PATH):
        return {"status": "STOPPED", "reason": f"既存の日本語音声が見つかりません: {p3u.EXISTING_JA_PATH}"}
    if not os.path.exists(p3u.EXISTING_EN_PATH):
        return {"status": "STOPPED", "reason": f"既存の英語音声が見つかりません: {p3u.EXISTING_EN_PATH}"}

    ja_sha256 = _sha256_file(p3u.EXISTING_JA_PATH)
    en_sha256 = _sha256_file(p3u.EXISTING_EN_PATH)

    ja_samples, ja_sr, ja_ch, _ = common.read_wav_float(p3u.EXISTING_JA_PATH)
    en_samples, en_sr, en_ch, _ = common.read_wav_float(p3u.EXISTING_EN_PATH)
    if ja_sr != en_sr:
        return {"status": "STOPPED", "reason": f"サンプルレート不一致(ja={ja_sr}, en={en_sr})"}
    sample_rate = ja_sr

    with open(f"{OUT_DIR}/source/japanese_full_sentence.txt", "w", encoding="utf-8") as f:
        f.write(p3u.SOURCE_JAPANESE_FULL_SENTENCE)
    with open(f"{OUT_DIR}/source/english_keyword.txt", "w", encoding="utf-8") as f:
        f.write(p3u.SOURCE_ENGLISH_KEYWORD)

    # --- Step 1: Azure STTによるalignment(既存音声の解析のみ) ---
    words, stt_error = p3u.get_word_timestamps_via_azure_stt(p3u.EXISTING_JA_PATH)
    if words is None:
        return {"status": "STOPPED", "reason": f"Azure STTでの解析に失敗しました: {stt_error}"}

    with open(f"{OUT_DIR}/alignment/azure_stt_words.json", "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    boundary, boundary_error = p3u.find_keyword_boundary(words)
    if boundary is None:
        return {"status": "STOPPED", "reason": f"境界特定に失敗しました: {boundary_error}", "words": words}

    boundary["previous_wrong_cut_seconds"] = _PREVIOUS_WRONG_CUT_SECONDS
    boundary["difference_from_previous_wrong_cut_seconds"] = round(
        boundary["boundary_seconds"] - _PREVIOUS_WRONG_CUT_SECONDS, 4)
    with open(f"{OUT_DIR}/alignment/boundary_result.json", "w", encoding="utf-8") as f:
        json.dump(boundary, f, ensure_ascii=False, indent=2)

    # --- Step 2: 英語Key Phraseの前後無音トリム ---
    en_trimmed, trim_info = p3u.trim_english_keyword_silence(en_samples, sample_rate)
    if en_trimmed is None:
        return {"status": "STOPPED", "reason": "英語Key Phrase音声内に発話区間を検出できませんでした"}

    # --- Step 3: 日本語音声を境界時刻で分割 ---
    ja_before, ja_after = p3u.split_japanese_at_boundary(ja_samples, sample_rate, boundary["boundary_seconds"])
    if len(ja_before) == 0 or len(ja_after) == 0:
        return {"status": "STOPPED", "reason": "境界時刻が音声の範囲外か端に近すぎ、安全に分割できません"}

    common.write_wav_float(f"{OUT_DIR}/components/ja_before_keyword.wav", ja_before, sample_rate, 1)
    common.write_wav_float(f"{OUT_DIR}/components/en_shot_on_target_trimmed.wav", en_trimmed, sample_rate, 1)
    common.write_wav_float(f"{OUT_DIR}/components/ja_after_keyword.wav", ja_after, sample_rate, 1)

    # --- Step 4: 0.12秒固定ポーズで結合 ---
    joined = p3u.join_with_boundary_pauses(ja_before, en_trimmed, ja_after, sample_rate,
                                            boundary_pause_seconds=p3u.BOUNDARY_PAUSE_SECONDS)
    raw_path = f"{OUT_DIR}/final/A01_b1_exact_boundary_insert_raw.wav"
    common.write_wav_float(raw_path, joined, sample_rate, 1)

    # --- Step 5: Dynamics3を一度だけ適用 ---
    dynamics_result = common.apply_dynamics3_once(joined, sample_rate)
    final_path = f"{OUT_DIR}/final/A01_b1_exact_boundary_insert_dynamics3.wav"
    common.write_wav_float(final_path, dynamics_result.c1_samples, sample_rate, 1)

    metrics_ja_before = common.measure_metrics(ja_before, sample_rate)
    metrics_en_trimmed = common.measure_metrics(en_trimmed, sample_rate)
    metrics_ja_after = common.measure_metrics(ja_after, sample_rate)
    metrics_raw = common.measure_metrics(joined, sample_rate)
    metrics_final = dynamics_result.metrics_c1

    metadata = {
        "management_id": "ER-003-B1-P3U",
        "article_id": p3u.ARTICLE_ID,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "reused_existing_audio": {
            "ja_full_sentence_path": p3u.EXISTING_JA_PATH,
            "ja_full_sentence_sha256": ja_sha256,
            "en_shot_on_target_path": p3u.EXISTING_EN_PATH,
            "en_shot_on_target_sha256": en_sha256,
            "new_tts_calls_made": 0,
        },
        "alignment_method": "Azure Cognitive Services Speech SDK (Speech-to-Text, ja-JP, Detailed output, word-level timestamps)",
        "alignment_result": boundary,
        "en_trim": trim_info,
        "en_trim_safety_margin_seconds": p3u.EN_TRIM_SAFETY_MARGIN_SECONDS,
        "boundary_pause_seconds": p3u.BOUNDARY_PAUSE_SECONDS,
        "boundary_pause_count": 2,
        "join_order": ["ja_before_keyword", "en_shot_on_target_trimmed", "ja_after_keyword"],
        "components": {
            "ja_before_keyword_path": f"{OUT_DIR}/components/ja_before_keyword.wav",
            "ja_before_keyword_duration_seconds": metrics_ja_before["duration_seconds"],
            "en_shot_on_target_trimmed_path": f"{OUT_DIR}/components/en_shot_on_target_trimmed.wav",
            "en_shot_on_target_trimmed_duration_seconds": metrics_en_trimmed["duration_seconds"],
            "ja_after_keyword_path": f"{OUT_DIR}/components/ja_after_keyword.wav",
            "ja_after_keyword_duration_seconds": metrics_ja_after["duration_seconds"],
        },
        "dynamics3_applied": dynamics_result.applied_once,
        "dynamics3_params": dynamics_result.dynamics_params,
        "loudness_matching": dynamics_result.loudness_matching,
        "raw_path": raw_path,
        "final_path": final_path,
        "final_path_format_note": (
            "MP3エンコーダ(ffmpeg/pydub)がこの環境に存在しないため、WAVのまま"
            "保存した(ER-003-B1-P3R/P3S/P3Tと同一の判断)。"
        ),
        "sample_rate": sample_rate,
        "channels": 1,
        "metrics_raw": metrics_raw,
        "metrics_final": metrics_final,
        "final_duration_seconds": metrics_final["duration_seconds"],
        "final_sha256": _sha256_file(final_path),
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
        md = result["metadata"]
        print(f"boundary_seconds={md['alignment_result']['boundary_seconds']}")
        print(f"difference_from_previous_wrong_cut={md['alignment_result']['difference_from_previous_wrong_cut_seconds']}")
        print(f"final_duration_seconds={md['final_duration_seconds']}")
