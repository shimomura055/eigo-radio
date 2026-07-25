# ============================================================
# er003_v1_b1_p3w_generate.py
# ER-003-B1-P3W: MFAマーカー置換・短尺検証・生成
# ============================================================
# Step 1: MFA隔離環境の確認(構築自体はer003_b1_p3w_audio.pyのMFA_*定数
#         が指す環境として、本スクリプト実行前にmicromamba経由で完了済み)
# Step 2: 既存のMFAスモークテスト結果(mfa_tool/smoke_test_output/)を
#         再検証(語順一致確認)。新しいalignmentは不要ならば再実行しない。
# Step 3: マーカー入り日本語一時原稿を1回だけTTS生成
# Step 4: MFAでマーカー区間をalignment
# Step 5: 既存のtrim済み英語音声でマーカー区間を置換
# Step 6: Dynamics3を1回だけ適用
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3w_generate.py

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3w_audio as p3w

OUT_DIR = "er003_output/b1_p3w/A01"
SMOKE_TEST_TEXTGRID_SRC = "mfa_tool/smoke_test_output/ja_full_sentence.TextGrid"
_EXPECTED_SMOKE_TEST_WORD_ORDER = [
    "前半", "は", "激しい", "接触", "と", "緊張", "が", "続き",
    "両", "チーム", "とも", "枠内", "シュート", "を", "記録",
    "できない", "まま", "静か", "な", "均衡", "が", "保たれます",
]


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _save_wav(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def check_environment_and_smoke_test() -> dict:
    """Step 1(MFA隔離環境の存在確認)とStep 2(既存スモークテスト結果の
    再検証)。新しいalignment実行はしない(既に本セッション内でmfa align
    により生成済みのTextGridを再パースして語順一致を確認するのみ)。"""
    env_available = p3w.mfa_environment_available()
    if not env_available:
        return {
            "status": "STOPPED",
            "phase": "Step1",
            "reason": "MFA隔離環境(mfa_tool/)が見つかりません",
        }

    if not os.path.exists(SMOKE_TEST_TEXTGRID_SRC):
        return {
            "status": "STOPPED",
            "phase": "Step2",
            "reason": f"スモークテストのTextGridが見つかりません: {SMOKE_TEST_TEXTGRID_SRC}",
        }

    words = p3w.parse_textgrid_words_tier(SMOKE_TEST_TEXTGRID_SRC)
    non_empty_texts = [w["text"] for w in words if w["text"] != ""]
    order_matches = non_empty_texts == _EXPECTED_SMOKE_TEST_WORD_ORDER

    if not order_matches:
        return {
            "status": "STOPPED",
            "phase": "Step2",
            "reason": "スモークテストの語順が原稿順と一致しません",
            "actual_order": non_empty_texts,
        }

    return {
        "status": "OK",
        "mfa_micromamba_exe": p3w.MFA_MICROMAMBA_EXE,
        "mfa_env_prefix": p3w.MFA_ENV_PREFIX,
        "mfa_root_dir": p3w.MFA_ROOT_DIR,
        "mfa_acoustic_model": p3w.MFA_ACOUSTIC_MODEL_NAME,
        "mfa_dictionary": p3w.MFA_DICTIONARY_NAME,
        "smoke_test_wav_path": p3w.SMOKE_TEST_WAV_PATH,
        "smoke_test_wav_sha256": _sha256_file(p3w.SMOKE_TEST_WAV_PATH),
        "smoke_test_textgrid_path": SMOKE_TEST_TEXTGRID_SRC,
        "smoke_test_word_order_matches_source": order_matches,
        "smoke_test_word_count": len(non_empty_texts),
    }


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    for sub in ("environment", "source", "raw", "alignment", "components", "final"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    # --- Step 1 + Step 2 ---
    env_check = check_environment_and_smoke_test()
    if env_check["status"] != "OK":
        return env_check
    shutil.copyfile(SMOKE_TEST_TEXTGRID_SRC, f"{OUT_DIR}/environment/smoke_test_ja_full_sentence.TextGrid")

    with open(f"{OUT_DIR}/source/integrated_source.txt", "w", encoding="utf-8") as f:
        f.write(p3w.SOURCE_INTEGRATED_SENTENCE)
    with open(f"{OUT_DIR}/source/japanese_source.txt", "w", encoding="utf-8") as f:
        f.write(p3w.SOURCE_JAPANESE_FULL_SENTENCE)
    with open(f"{OUT_DIR}/source/english_keyword.txt", "w", encoding="utf-8") as f:
        f.write(p3w.SOURCE_ENGLISH_KEYWORD)

    marker_script = p3w.build_tts_marker_script()
    with open(f"{OUT_DIR}/source/tts_marker_script.txt", "w", encoding="utf-8") as f:
        f.write(marker_script)

    # --- 既存のtrim済み英語音声の再利用確認(新規TTS生成しない) ---
    if not os.path.exists(p3w.EXISTING_EN_TRIMMED_PATH):
        return {
            "status": "STOPPED", "phase": "Step5-pre",
            "reason": f"既存の英語音声が見つかりません: {p3w.EXISTING_EN_TRIMMED_PATH}",
            "env_check": env_check,
        }
    en_trimmed_sha256 = _sha256_file(p3w.EXISTING_EN_TRIMMED_PATH)
    en_samples, en_sr, en_ch, _ = common.read_wav_float(p3w.EXISTING_EN_TRIMMED_PATH)
    shutil.copyfile(p3w.EXISTING_EN_TRIMMED_PATH, f"{OUT_DIR}/components/en_shot_on_target_trimmed.wav")

    # --- Step 3: マーカー入り日本語一時原稿を1回だけTTS生成 ---
    # 本ステージ中の以前の実行(Step4のalignment失敗前)で既にTTS生成済み
    # の場合は、それを再利用し新規TTS呼び出しを行わない(1回だけ生成する
    # という指示section 5の方針を、スクリプトを再実行しても壊さないため)。
    ja_wav_path = f"{OUT_DIR}/raw/ja_with_spoken_marker.wav"
    ja_retries = 0
    ja_call_count = 0
    if os.path.exists(ja_wav_path):
        ja_call_count = 0  # このスクリプト実行内では新規呼び出しなし(既存ファイルを再利用)
    else:
        style_prefix = p3w.build_style_prefix()
        if tts_call_fn is None:
            tts_call_fn = gclient.make_tts_call_fn(p3w.VOICE_NAME)

        ja_prompt = p3w.build_tts_prompt(marker_script, style_prefix)
        ja_pcm, ja_retries, ja_ok, ja_err = common._call_tts_with_retry(
            tts_call_fn, ja_prompt, max_retry=p3w.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        if not ja_ok:
            return {
                "status": "STOPPED", "phase": "Step3",
                "reason": f"マーカー入り日本語音声のTTSが失敗: {ja_err}",
                "env_check": env_check,
            }
        _save_wav(ja_wav_path, ja_pcm)
        ja_call_count = 1 + ja_retries

    ja_sha256 = _sha256_file(ja_wav_path)
    ja_samples, ja_sr, ja_ch, _ = common.read_wav_float(ja_wav_path)
    ja_metrics = common.measure_metrics(ja_samples, ja_sr)

    marker_count_in_script = marker_script.count(p3w.MARKER_TOKEN)

    # --- Step 4: MFAでマーカー区間をalignment ---
    align_corpus_dir = f"{OUT_DIR}/_mfa_corpus"
    align_output_dir = f"{OUT_DIR}/alignment/_mfa_raw_output"
    os.makedirs(align_corpus_dir, exist_ok=True)
    shutil.copyfile(ja_wav_path, f"{align_corpus_dir}/ja_with_spoken_marker.wav")
    with open(f"{align_corpus_dir}/ja_with_spoken_marker.lab", "w", encoding="utf-8") as f:
        f.write(marker_script)

    align_result = p3w.run_mfa_align(align_corpus_dir, align_output_dir)
    if not align_result["success"]:
        return {
            "status": "STOPPED", "phase": "Step4",
            "reason": "MFA alignmentが失敗しました",
            "align_result": align_result,
            "env_check": env_check,
            "ja_call_count": ja_call_count, "ja_retry_count": ja_retries,
        }

    textgrid_path = f"{align_output_dir}/ja_with_spoken_marker.TextGrid"
    if not os.path.exists(textgrid_path):
        return {
            "status": "STOPPED", "phase": "Step4",
            "reason": f"TextGridが生成されませんでした: {textgrid_path}",
            "align_result": align_result,
            "env_check": env_check,
        }
    shutil.copyfile(textgrid_path, f"{OUT_DIR}/alignment/ja_with_spoken_marker.TextGrid")
    shutil.rmtree(align_output_dir, ignore_errors=True)

    words = p3w.parse_textgrid_words_tier(f"{OUT_DIR}/alignment/ja_with_spoken_marker.TextGrid")
    marker_span, marker_error = p3w.find_marker_span(words)
    if marker_span is None:
        return {
            "status": "STOPPED", "phase": "Step4",
            "reason": f"マーカー区間を特定できませんでした: {marker_error}",
            "textgrid_path": f"{OUT_DIR}/alignment/ja_with_spoken_marker.TextGrid",
            "words": words,
            "env_check": env_check,
        }

    # --- Step 5: マーカー区間を英語へ置換 ---
    ja_before, ja_after = p3w.remove_marker_span(
        ja_samples, ja_sr, marker_span["marker_start_seconds"], marker_span["marker_end_seconds"])
    if len(ja_before) == 0 or len(ja_after) == 0:
        return {
            "status": "STOPPED", "phase": "Step5",
            "reason": "マーカー区間の位置が音声の端に近すぎ、安全に分割できません",
            "marker_span": marker_span, "env_check": env_check,
        }

    common.write_wav_float(f"{OUT_DIR}/components/ja_before_marker.wav", ja_before, ja_sr, 1)
    common.write_wav_float(f"{OUT_DIR}/components/ja_after_marker.wav", ja_after, ja_sr, 1)

    joined = p3w.p3u.join_with_boundary_pauses(
        ja_before, en_samples, ja_after, ja_sr, boundary_pause_seconds=p3w.BOUNDARY_PAUSE_SECONDS)
    raw_path = f"{OUT_DIR}/final/A01_b1_mfa_marker_replacement_raw.wav"
    common.write_wav_float(raw_path, joined, ja_sr, 1)

    # --- Step 6: Dynamics3を1回だけ適用 ---
    dynamics_result = common.apply_dynamics3_once(joined, ja_sr)
    final_path = f"{OUT_DIR}/final/A01_b1_mfa_marker_replacement_dynamics3.wav"
    common.write_wav_float(final_path, dynamics_result.c1_samples, ja_sr, 1)

    metrics_ja_before = common.measure_metrics(ja_before, ja_sr)
    metrics_en_trimmed = common.measure_metrics(en_samples, en_sr)
    metrics_ja_after = common.measure_metrics(ja_after, ja_sr)
    metrics_raw = common.measure_metrics(joined, ja_sr)
    metrics_final = dynamics_result.metrics_c1

    shutil.rmtree(align_corpus_dir, ignore_errors=True)

    metadata = {
        "management_id": "ER-003-B1-P3W",
        "article_id": "A01",
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "env_check": env_check,
        "source_integrated_sentence": p3w.SOURCE_INTEGRATED_SENTENCE,
        "source_japanese_full_sentence": p3w.SOURCE_JAPANESE_FULL_SENTENCE,
        "source_english_keyword": p3w.SOURCE_ENGLISH_KEYWORD,
        "tts_marker_script": marker_script,
        "marker_token": p3w.MARKER_TOKEN,
        "marker_token_count_in_script": marker_count_in_script,
        "tts_model": common.MODEL_NAME,
        "voice": p3w.VOICE_NAME,
        "ja_call_count": ja_call_count,
        "ja_retry_count": ja_retries,
        "max_technical_retry": p3w.MAX_TTS_TECHNICAL_RETRY,
        "ja_tts_note": (
            "本ステージ中、Step4(alignment)の失敗を調査・修正する過程で、"
            "既存のraw/ja_with_spoken_marker.wavを再利用せずスクリプトを"
            "再実行してしまい、意図せず2回目の実TTS呼び出しが発生した"
            "(合計2回)。最終的にadoptしたのはこの2回目の生成結果であり、"
            "以降このファイルが存在する限り新規TTS呼び出しは行わない"
            "(このrun内でのja_call_countは0=既存ファイル再利用)。"
        ),
        "ja_with_spoken_marker_path": ja_wav_path,
        "ja_with_spoken_marker_sha256": ja_sha256,
        "ja_with_spoken_marker_duration_seconds": ja_metrics["duration_seconds"],
        "ja_with_spoken_marker_clipping_detected": ja_metrics["clipping_detected"],
        "textgrid_path": f"{OUT_DIR}/alignment/ja_with_spoken_marker.TextGrid",
        "mfa_align_result": {k: v for k, v in align_result.items() if k != "command"},
        "marker_span": marker_span,
        "existing_english_audio_path": p3w.EXISTING_EN_TRIMMED_PATH,
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
        "boundary_pause_seconds": p3w.BOUNDARY_PAUSE_SECONDS,
        "boundary_pause_count": 2,
        "dynamics3_applied": dynamics_result.applied_once,
        "dynamics3_params": dynamics_result.dynamics_params,
        "loudness_matching": dynamics_result.loudness_matching,
        "raw_path": raw_path,
        "final_path": final_path,
        "final_path_format_note": (
            "MP3エンコーダ(ffmpeg/pydub)がこの環境に存在しないため、WAVのまま"
            "保存した(ER-003-B1-P3R/P3S/P3T/P3Uと同一の判断)。"
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
