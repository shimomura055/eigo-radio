# ============================================================
# er005_avr02_instruction_separation.py
# ER-005-AUDIO-VALIDATION-ROBUSTNESS-02: Structured Separation A/B test
# ============================================================
# Current(既存の style_prefix + text という単純連結)と、Structured
# Separation(style instructionとspoken textを明示的なdelimiterで区切る、
# ただし両者の中身は一切変更しない)を、同一のvoice/model/textで比較する。
#
# system_instruction(GenerateContentConfigの正式フィールド)は、Gemini
# 公式ドキュメント(ai.google.dev/gemini-api/docs/speech-generation)に
# TTSでのサポート記載がなく、実際に試したところ2回とも500 INTERNAL
# エラーになることを確認したため、本命候補から除外した
# (README/報告書に記録)。

from __future__ import annotations

import json
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
from google.genai import types

OUT_DIR = "er005_output/audio_validation_robustness_02"


def build_current_prompt(text: str, style_prefix: str) -> str:
    return style_prefix + text


def build_structured_prompt(text: str, style_prefix: str) -> str:
    """style_prefix・textの中身は一切変更せず、明示的なdelimiterで
    「話し方の指示(読み上げ対象外)」と「読み上げ対象の本文」を分離する。"""
    return (
        "The message below has two clearly separated sections.\n\n"
        "=== STYLE INSTRUCTIONS (meta-guidance only — do not speak this section aloud, "
        "it only describes how to perform the reading in the next section) ===\n"
        f"{style_prefix.strip()}\n"
        "=== END STYLE INSTRUCTIONS ===\n\n"
        "=== TEXT TO SPEAK (speak this section aloud exactly as written, and nothing else — "
        "do not speak anything from the STYLE INSTRUCTIONS section above) ===\n"
        f"{text}\n"
        "=== END TEXT TO SPEAK ==="
    )


def run_single_trial(call_fn, prompt: str, canonical_text: str, language: str,
                      out_path: str) -> dict:
    """1回のTTS呼び出し(technical retryなし、生の1呼び出し)を行い、
    生成直後の異常長検知・ASR検証まで通した結果を返す。"""
    t0 = time.time()
    try:
        pcm = call_fn(prompt)
    except Exception as e:
        return {"status": "TTS_ERROR", "error": str(e), "elapsed_seconds": round(time.time() - t0, 2)}
    samples_raw = common.pcm_bytes_to_float_mono(common.normalize_pcm(pcm))
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"status": "NO_SPEECH_DETECTED", "elapsed_seconds": round(time.time() - t0, 2)}
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], canonical_text, language)
    result = {
        "status": "OK", "trim_info": trim_info, "duration_anomaly": anomaly,
        "elapsed_seconds": round(time.time() - t0, 2),
    }
    if anomaly["is_anomaly"]:
        result["status"] = "DURATION_ANOMALY"
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        result["path"] = out_path
        return result
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    result["path"] = out_path
    asr_lang = "ja-JP" if language == "ja" else "en-US"
    asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language=asr_lang)
    result["asr_text"] = asr_text
    result["asr_error"] = asr_err
    match = safety.validate_asr_match(canonical_text, asr_text, n=min(6, max(1, len(canonical_text.split()))),
                                       asr_error=asr_err)
    result["asr_verdict"] = match["verdict"]
    result["asr_passed"] = match["passed"]
    return result


def classify_trial(r: dict) -> str:
    """報告用の要約カテゴリ。"""
    status = r.get("status")
    if status == "TTS_ERROR":
        if "INVALID_ARGUMENT" in str(r.get("error", "")):
            return "INVALID_ARGUMENT"
        if "timed out" in str(r.get("error", "")).lower():
            return "TIMEOUT"
        if "500 INTERNAL" in str(r.get("error", "")):
            return "500_INTERNAL"
        return "OTHER_TTS_ERROR"
    if status == "NO_SPEECH_DETECTED":
        return "NO_SPEECH_DETECTED"
    if status == "DURATION_ANOMALY":
        return "HALLUCINATION_DURATION_ANOMALY"
    if status == "OK":
        return "NORMAL_ASR_PASS" if r.get("asr_passed") else "NORMAL_ASR_MISMATCH"
    return "UNKNOWN"


def run_segment_trials(segment_name: str, text: str, style_prefix: str, voice: str,
                        language: str, n_trials: int) -> dict:
    call_fn = gclient.make_tts_call_fn(voice)
    out = {"segment": segment_name, "language": language, "voice": voice, "n_trials": n_trials,
           "current": [], "structured": []}
    for method, builder, key in [("current", build_current_prompt, "current"),
                                  ("structured", build_structured_prompt, "structured")]:
        for i in range(1, n_trials + 1):
            prompt = builder(text, style_prefix)
            out_path = f"{OUT_DIR}/trials/{segment_name}_{method}_{i}.wav"
            print(f"[{segment_name}] {method} trial {i}/{n_trials}...")
            r = run_single_trial(call_fn, prompt, text, language, out_path)
            r["category"] = classify_trial(r)
            print(f"  -> {r['category']}")
            out[key].append(r)
    return out


if __name__ == "__main__":
    import sys
    print("This module is imported by er005_avr02_run.py; not run directly.")
