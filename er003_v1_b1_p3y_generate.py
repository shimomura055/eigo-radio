# ============================================================
# er003_v1_b1_p3y_generate.py
# ER-003-B1-P3Y: 日本語用instruction＋カタカナマーカー置換検証・生成
# ============================================================
# Step 2: 日本語TTS一時原稿を1回だけ生成(技術的失敗時のみ1回まで再試行)
# Step 3: MFA・切り出しへ進む前に、raw音声が日本語であることを診断用
#         ASR(Azure STT)で確認する。英語または原稿と不一致の場合は、
#         ここで停止し、MFAへは進まない・置換しない・再生成しない。
# Step 4: MFA(P3Wの隔離環境をそのまま再利用)でカタカナマーカー区間を
#         alignment。
# Step 5: 既存のtrim済み英語音声(P3U成果物)でマーカー区間を置換。
# Step 6: Dynamics3を1回適用。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3y_generate.py

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w
import er003_b1_p3y_audio as p3y

OUT_DIR = "er003_output/b1_p3y/A01"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _save_wav(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def check_ja_content(wav_path: str, expected_script: str, marker: str) -> dict:
    """Step 3: raw音声が日本語であることを診断用ASR(Azure STT、境界決定
    には使わない)で確認する。原文一致は求めず、日本語として認識される
    こと・カタカナマーカーに対応する音がある程度含まれることを目安に
    判定する(ASRの完全一致は前提にできないため、言語判定を主目的とする)。"""
    words, err = p3u.get_word_timestamps_via_azure_stt(wav_path, language="ja-JP")
    if words is None:
        return {"status": "ERROR", "reason": err}

    recognized_ja = "".join(w["word"] for w in words)

    words_en, err_en = p3u.get_word_timestamps_via_azure_stt(wav_path, language="en-US")
    recognized_en = None
    if words_en is not None:
        recognized_en = " ".join(w["word"] for w in words_en)

    # 簡易な日本語判定: ja-JP認識結果に日本語文字(ひらがな/カタカナ/漢字)が
    # 一定割合以上含まれているか。英語化していた場合(P3X)は、ja-JP指定でも
    # ローマ字が連結された文字列になり、日本語文字はほぼ0になることを
    # P3Xで確認済み。
    ja_char_count = sum(
        1 for ch in recognized_ja
        if ("぀" <= ch <= "ゟ") or ("゠" <= ch <= "ヿ") or ("一" <= ch <= "鿿")
    )
    ja_char_ratio = ja_char_count / len(recognized_ja) if recognized_ja else 0.0
    is_japanese = ja_char_ratio >= 0.5

    return {
        "status": "OK",
        "recognized_text_ja_JP": recognized_ja,
        "recognized_text_en_US": recognized_en,
        "ja_char_count": ja_char_count,
        "ja_char_ratio": round(ja_char_ratio, 4),
        "is_japanese": is_japanese,
        "expected_script": expected_script,
        "marker": marker,
    }


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    for sub in ("source", "raw", "alignment", "components", "final"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    # --- Step 1: instruction差分の記録 ---
    diff = p3y.build_instruction_diff()
    with open(f"{OUT_DIR}/source/instruction_before.txt", "w", encoding="utf-8") as f:
        f.write(diff["before"])
    with open(f"{OUT_DIR}/source/instruction_after.txt", "w", encoding="utf-8") as f:
        f.write(diff["after"])
    with open(f"{OUT_DIR}/source/instruction_diff.txt", "w", encoding="utf-8") as f:
        for d in diff["changed_lines"]:
            f.write(f"line {d['line_index']}:\n- {d['before']}\n+ {d['after']}\n")
    if not diff["only_one_line_changed"]:
        return {
            "status": "STOPPED", "phase": "Step1",
            "reason": "instructionの差分が1行だけではありません",
            "diff": diff,
        }

    with open(f"{OUT_DIR}/source/approved_integrated_source.txt", "w", encoding="utf-8") as f:
        f.write(p3y.SOURCE_INTEGRATED_SENTENCE)
    marker_script = p3y.build_tts_katakana_marker_script()
    with open(f"{OUT_DIR}/source/tts_japanese_marker_script.txt", "w", encoding="utf-8") as f:
        f.write(marker_script)

    # --- 既存のtrim済み英語音声の再利用確認(新規TTS生成しない) ---
    if not os.path.exists(p3y.EXISTING_EN_TRIMMED_PATH):
        return {
            "status": "STOPPED", "phase": "Step5-pre",
            "reason": f"既存の英語音声が見つかりません: {p3y.EXISTING_EN_TRIMMED_PATH}",
        }
    en_trimmed_sha256 = _sha256_file(p3y.EXISTING_EN_TRIMMED_PATH)
    en_samples, en_sr, en_ch, _ = common.read_wav_float(p3y.EXISTING_EN_TRIMMED_PATH)
    shutil.copyfile(p3y.EXISTING_EN_TRIMMED_PATH, f"{OUT_DIR}/components/en_shot_on_target_trimmed.wav")

    # --- Step 2: 日本語TTS一時原稿を1回だけ生成 ---
    ja_wav_path = f"{OUT_DIR}/raw/ja_with_katakana_marker.wav"
    style_prefix = p3y.build_japanese_style_prefix()
    if tts_call_fn is None:
        tts_call_fn = gclient.make_tts_call_fn(p3y.VOICE_NAME)

    ja_prompt = p3y.build_tts_prompt(marker_script, style_prefix)
    ja_pcm, ja_retries, ja_ok, ja_err = common._call_tts_with_retry(
        tts_call_fn, ja_prompt, max_retry=p3y.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ja_ok:
        return {
            "status": "STOPPED", "phase": "Step2",
            "reason": f"日本語TTSが失敗: {ja_err}",
            "ja_call_count": 1 + ja_retries, "ja_retry_count": ja_retries,
        }
    _save_wav(ja_wav_path, ja_pcm)
    ja_call_count = 1 + ja_retries
    ja_sha256 = _sha256_file(ja_wav_path)
    ja_samples, ja_sr, ja_ch, _ = common.read_wav_float(ja_wav_path)
    ja_metrics = common.measure_metrics(ja_samples, ja_sr)

    # --- Step 3: 生成直後の言語確認(MFAへ進む前のゲート) ---
    content_check = check_ja_content(ja_wav_path, marker_script, p3y.KATAKANA_MARKER)
    with open(f"{OUT_DIR}/raw/content_check.json", "w", encoding="utf-8") as f:
        json.dump(content_check, f, ensure_ascii=False, indent=2)

    if content_check["status"] != "OK" or not content_check["is_japanese"]:
        return {
            "status": "STOPPED", "phase": "Step3",
            "reason": "raw音声が日本語であることを確認できませんでした(英語化、または診断失敗)",
            "content_check": content_check,
            "ja_call_count": ja_call_count, "ja_retry_count": ja_retries,
            "ja_with_katakana_marker_path": ja_wav_path,
            "ja_with_katakana_marker_sha256": ja_sha256,
        }

    # --- Step 4: MFA alignment(P3Wの隔離環境を再利用) ---
    align_corpus_dir = f"{OUT_DIR}/_mfa_corpus"
    align_output_dir = f"{OUT_DIR}/alignment/_mfa_raw_output"
    os.makedirs(align_corpus_dir, exist_ok=True)
    shutil.copyfile(ja_wav_path, f"{align_corpus_dir}/ja_with_katakana_marker.wav")
    with open(f"{align_corpus_dir}/ja_with_katakana_marker.lab", "w", encoding="utf-8") as f:
        f.write(marker_script)

    align_result = p3w.run_mfa_align(align_corpus_dir, align_output_dir)
    if not align_result["success"]:
        return {
            "status": "STOPPED", "phase": "Step4",
            "reason": "MFA alignmentが失敗しました",
            "align_result": align_result,
            "content_check": content_check,
            "ja_call_count": ja_call_count, "ja_retry_count": ja_retries,
        }

    textgrid_path = f"{align_output_dir}/ja_with_katakana_marker.TextGrid"
    if not os.path.exists(textgrid_path):
        return {
            "status": "STOPPED", "phase": "Step4",
            "reason": f"TextGridが生成されませんでした: {textgrid_path}",
            "align_result": align_result,
        }
    shutil.copyfile(textgrid_path, f"{OUT_DIR}/alignment/ja_with_katakana_marker.TextGrid")
    shutil.rmtree(align_output_dir, ignore_errors=True)

    words = p3w.parse_textgrid_words_tier(f"{OUT_DIR}/alignment/ja_with_katakana_marker.TextGrid")
    marker_span, marker_error = p3w.find_marker_span(words, marker_tokens=p3y.MARKER_TOKEN_SEQUENCE)
    if marker_span is None:
        return {
            "status": "STOPPED", "phase": "Step4",
            "reason": f"マーカー区間を特定できませんでした: {marker_error}",
            "textgrid_path": f"{OUT_DIR}/alignment/ja_with_katakana_marker.TextGrid",
            "words": words,
        }

    with open(f"{OUT_DIR}/alignment/marker_alignment_report.md", "w", encoding="utf-8") as f:
        f.write("# ER-003-B1-P3Y marker alignment\n\n")
        f.write(f"- marker_tokens: {marker_span['marker_tokens']}\n")
        f.write(f"- marker_start_seconds: {marker_span['marker_start_seconds']}\n")
        f.write(f"- marker_end_seconds: {marker_span['marker_end_seconds']}\n")
        f.write(f"- preceding_token: {marker_span['preceding_token']}\n")
        f.write(f"- following_token: {marker_span['following_token']}\n")

    # --- Step 5: マーカー区間を英語へ置換 ---
    ja_before, ja_after = p3w.remove_marker_span(
        ja_samples, ja_sr, marker_span["marker_start_seconds"], marker_span["marker_end_seconds"])
    if len(ja_before) == 0 or len(ja_after) == 0:
        return {
            "status": "STOPPED", "phase": "Step5",
            "reason": "マーカー区間の位置が音声の端に近すぎ、安全に分割できません",
            "marker_span": marker_span,
        }

    common.write_wav_float(f"{OUT_DIR}/components/ja_before_marker.wav", ja_before, ja_sr, 1)
    common.write_wav_float(f"{OUT_DIR}/components/ja_after_marker.wav", ja_after, ja_sr, 1)

    joined = p3u.join_with_boundary_pauses(
        ja_before, en_samples, ja_after, ja_sr, boundary_pause_seconds=p3y.BOUNDARY_PAUSE_SECONDS)
    raw_path = f"{OUT_DIR}/final/A01_b1_katakana_marker_replacement_raw.wav"
    common.write_wav_float(raw_path, joined, ja_sr, 1)

    # --- Step 6: Dynamics3を1回だけ適用 ---
    dynamics_result = common.apply_dynamics3_once(joined, ja_sr)
    final_path = f"{OUT_DIR}/final/A01_b1_katakana_marker_replacement_dynamics3.wav"
    common.write_wav_float(final_path, dynamics_result.c1_samples, ja_sr, 1)

    metrics_ja_before = common.measure_metrics(ja_before, ja_sr)
    metrics_en_trimmed = common.measure_metrics(en_samples, en_sr)
    metrics_ja_after = common.measure_metrics(ja_after, ja_sr)
    metrics_raw = common.measure_metrics(joined, ja_sr)
    metrics_final = dynamics_result.metrics_c1

    shutil.rmtree(align_corpus_dir, ignore_errors=True)

    metadata = {
        "management_id": "ER-003-B1-P3Y",
        "article_id": "A01",
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "instruction_diff": diff,
        "source_integrated_sentence": p3y.SOURCE_INTEGRATED_SENTENCE,
        "source_japanese_full_sentence": p3y.SOURCE_JAPANESE_FULL_SENTENCE,
        "source_english_keyword": p3y.SOURCE_ENGLISH_KEYWORD,
        "tts_japanese_marker_script": marker_script,
        "katakana_marker": p3y.KATAKANA_MARKER,
        "tts_model": common.MODEL_NAME,
        "voice": p3y.VOICE_NAME,
        "ja_call_count": ja_call_count,
        "ja_retry_count": ja_retries,
        "max_technical_retry": p3y.MAX_TTS_TECHNICAL_RETRY,
        "ja_with_katakana_marker_path": ja_wav_path,
        "ja_with_katakana_marker_sha256": ja_sha256,
        "ja_with_katakana_marker_duration_seconds": ja_metrics["duration_seconds"],
        "ja_with_katakana_marker_clipping_detected": ja_metrics["clipping_detected"],
        "content_check": content_check,
        "textgrid_path": f"{OUT_DIR}/alignment/ja_with_katakana_marker.TextGrid",
        "mfa_align_result": {k: v for k, v in align_result.items() if k != "command"},
        "marker_span": marker_span,
        "existing_english_audio_path": p3y.EXISTING_EN_TRIMMED_PATH,
        "existing_english_audio_sha256": en_trimmed_sha256,
        "existing_english_audio_duration_seconds": metrics_en_trimmed["duration_seconds"],
        "components": {
            "ja_before_marker_path": f"{OUT_DIR}/components/ja_before_marker.wav",
            "ja_before_marker_duration_seconds": metrics_ja_before["duration_seconds"],
            "en_shot_on_target_trimmed_path": f"{OUT_DIR}/components/en_shot_on_target_trimmed.wav",
            "en_shot_on_target_trimmed_duration_seconds": metrics_en_trimmed["duration_seconds"],
            "ja_after_marker_path": f"{OUT_DIR}/components/ja_after_marker.wav",
            "ja_after_marker_duration_seconds": metrics_ja_after["duration_seconds"],
        },
        "join_order": ["ja_before_marker", "en_shot_on_target_trimmed", "ja_after_marker"],
        "boundary_pause_seconds": p3y.BOUNDARY_PAUSE_SECONDS,
        "boundary_pause_count": 2,
        "dynamics3_applied": dynamics_result.applied_once,
        "dynamics3_params": dynamics_result.dynamics_params,
        "loudness_matching": dynamics_result.loudness_matching,
        "raw_path": raw_path,
        "final_path": final_path,
        "final_path_format_note": (
            "MP3エンコーダ(ffmpeg/pydub)がこの環境に存在しないため、WAVのまま"
            "保存した(ER-003-B1-P3R/P3S/P3T/P3U/P3Wと同一の判断)。"
        ),
        "sample_rate": ja_sr,
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
        print(result.get("phase"), result.get("reason"))
    else:
        md = result["metadata"]
        print(f"marker_start={md['marker_span']['marker_start_seconds']}")
        print(f"marker_end={md['marker_span']['marker_end_seconds']}")
        print(f"final_duration_seconds={md['final_duration_seconds']}")
