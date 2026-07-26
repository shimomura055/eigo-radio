# ============================================================
# er003_v1_b1_p5c_generate.py
# ER-003-B1-P5C: GCP漢字かな交じり入力検証
# ============================================================
# P5B-GCPと完全に同一の実装・voice・生成条件(Google Cloud TTS、
# ja-JP-Neural2-B、LINEAR16、SSML/話速/pitch指定なし)のまま、入力表記
# だけを「全文ひらがな」から「英語used form5件を目印へ置換した直後の
# 漢字かな交じり原稿」へ変更し、1回だけ生成する。新しいTTSエンジンは
# 追加しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p5c_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p5b_audio as p5b
import er003_b1_p5c_audio as p5c

OUT_DIR = "er003_output/b1_p5c/A01"
MANAGEMENT_ID = "ER-003-B1-P5C"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mkdirs() -> None:
    for sub in ("source", "raw", "asr", "instruction"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def _step_precheck() -> dict:
    availability = p5b.check_google_cloud_tts_availability()
    with open(f"{OUT_DIR}/source/availability.json", "w", encoding="utf-8") as f:
        json.dump(availability, f, ensure_ascii=False, indent=2)
    return availability


def _step_load_and_verify_input() -> dict:
    marked = p5c.load_marked_text_input()  # sha256不一致なら例外(改変検知)
    pattern_a_text = p4.load_pattern_a_text()
    used_forms = p5c.load_used_forms()
    verification = p5c.verify_marker_replacement(marked["text"], pattern_a_text, used_forms)

    with open(f"{OUT_DIR}/source/pattern_a_approved.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump({
            "p4d_marked_text_path": p5c.P4D_MARKED_TEXT_PATH,
            "p4d_marked_text_sha256_full": marked["sha256"],
            "matches_p4d_recorded_value": marked["sha256"] == p5c.P4D_MARKED_TEXT_EXPECTED_SHA256,
        }, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/source/marker_replacement_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification, f, ensure_ascii=False, indent=2)

    return {"marked": marked, "pattern_a_text": pattern_a_text, "used_forms": used_forms, "verification": verification}


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()

    availability = _step_precheck()
    if not availability["available"] or not availability["voice_available"]:
        return {"status": "STOPPED", "phase": "precheck", "reason": "Google Cloud TTSまたは指定voiceが利用できません", "availability": availability}

    input_step = _step_load_and_verify_input()
    if not input_step["verification"]["all_passed"]:
        return {"status": "STOPPED", "phase": "input_verification", "reason": "入力の静的QAに不合格のため、TTSを呼び出さず停止", "input_step": input_step}

    call_fn = tts_call_fn or p5b.make_google_tts_call_fn()
    prompt = input_step["marked"]["text"]
    sent_text_sha256 = _sha256_text(prompt)

    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p5c.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "phase": "tts_generation", "reason": f"Google Cloud TTS合成が失敗: {err}", "call_count": 1 + retries}

    call_metadata = dict(call_fn.last_response_metadata) if getattr(call_fn, "last_response_metadata", None) else None

    wav_path = f"{OUT_DIR}/raw/A01_p5c_google_kanji_kana_ja-JP-Neural2-B.wav"
    with open(wav_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    asr_result = {"status": "ERROR", "reason": stt_err}
    if recognized is not None:
        with open(f"{OUT_DIR}/asr/asr_transcript.txt", "w", encoding="utf-8") as f:
            f.write(recognized)
        kanji_target_phrase_results = p5c.check_kanji_target_phrases(recognized)
        asr_result = {"status": "OK", "recognized_text_ja_JP": recognized, "kanji_target_phrase_results": kanji_target_phrase_results}

    return {
        "status": "OK", "availability": availability, "input_step": input_step,
        "voice_name": p5c.GOOGLE_VOICE_NAME, "language_code": p5c.GOOGLE_LANGUAGE_CODE,
        "sent_text_sha256": sent_text_sha256,
        "sent_text_matches_input": sent_text_sha256 == input_step["marked"]["sha256"],
        "call_count": 1 + retries, "retry_count": retries, "call_metadata": call_metadata,
        "wav_path": wav_path, "wav_sha256": _sha256_file(wav_path),
        "duration_seconds": metrics["duration_seconds"], "clipping_detected": metrics["clipping_detected"],
        "sample_rate": sr, "channels": ch,
        "asr": asr_result,
    }


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        print("wav_path:", result["wav_path"])
        print("duration:", result["duration_seconds"])
        print("call_count:", result["call_count"])
        if result["asr"]["status"] == "OK":
            print("kanji_target_phrase_results:", result["asr"]["kanji_target_phrase_results"])
