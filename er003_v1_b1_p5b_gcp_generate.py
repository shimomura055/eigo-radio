# ============================================================
# er003_v1_b1_p5b_gcp_generate.py
# ER-003-B1-P5B-GCP: Google Cloud TTS単独検証
# ============================================================
# P4D/P5Aと完全に同一の全文ひらがな入力を、Google Cloud TTS
# (ja-JP-Neural2-B、ADC認証)で1回生成し、原稿忠実性と自然さ検証の
# 基礎データを作る。Amazon Pollyの認証・実装・生成は行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p5b_gcp_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p4d_audio as p4d
import er003_b1_p5a_audio as p5a
import er003_b1_p5b_audio as p5b

OUT_DIR = "er003_output/b1_p5b_gcp/A01"
MANAGEMENT_ID = "ER-003-B1-P5B-GCP"


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
    """指示section4の事前確認: ADC取得・API疎通・voice存在・課金なしの
    list_voices呼び出しのみで行う。"""
    availability = p5b.check_google_cloud_tts_availability()
    with open(f"{OUT_DIR}/source/availability.json", "w", encoding="utf-8") as f:
        json.dump(availability, f, ensure_ascii=False, indent=2)
    return availability


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()

    availability = _step_precheck()
    if not availability["available"]:
        return {"status": "STOPPED", "phase": "precheck", "reason": "Google Cloud TTSが利用できません", "availability": availability}
    if not availability["voice_available"]:
        return {
            "status": "STOPPED", "phase": "precheck",
            "reason": f"指定voice({p5b.GOOGLE_VOICE_NAME})が利用可能voice一覧に存在しません。代替voiceへは変更せず停止します。",
            "availability": availability,
        }

    p4d_input = p5a.load_p4d_input()  # sha256不一致なら例外(改変検知)
    marked_text = p5a.load_p4d_marked_text()
    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump({
            "p4d_hiragana_script_path": p5a.P4D_HIRAGANA_SCRIPT_PATH,
            "p4d_hiragana_script_sha256_full": p4d_input["sha256"],
            "matches_p5a_expected": p4d_input["sha256"] == p5a.P4D_EXPECTED_HIRAGANA_SHA256,
        }, f, ensure_ascii=False, indent=2)

    call_fn = tts_call_fn or p5b.make_google_tts_call_fn()
    prompt = p4d_input["text"]  # 変更せずそのまま送信
    sent_text_sha256 = _sha256_text(prompt)

    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p5a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "phase": "tts_generation", "reason": f"Google Cloud TTS合成が失敗: {err}", "call_count": 1 + retries}

    call_metadata = dict(call_fn.last_response_metadata) if getattr(call_fn, "last_response_metadata", None) else None

    wav_path = f"{OUT_DIR}/raw/A01_p5b_google_ja-JP-Neural2-B.wav"
    with open(wav_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    asr_result = {"status": "ERROR", "reason": stt_err}
    if recognized is not None:
        with open(f"{OUT_DIR}/asr/asr_transcript.txt", "w", encoding="utf-8") as f:
            f.write(recognized)

        content_check = p4d.check_full_text_content(recognized, marked_text)

        normalized = p5a.asr_reading_normalize(recognized, work_dir=f"{OUT_DIR}/_sudachi_work")
        with open(f"{OUT_DIR}/asr/asr_reading_normalized.txt", "w", encoding="utf-8") as f:
            f.write(normalized)

        target_phrase_results = p5b.check_target_phrases(normalized)
        nani_ga_okiru = p5b.check_nani_ga_okiru(normalized)

        asr_result = {
            "status": "OK", "recognized_text_ja_JP": recognized, "content_check": content_check,
            "asr_reading_normalized": normalized, "target_phrase_results": target_phrase_results,
            "nani_ga_okiru": nani_ga_okiru,
        }

    return {
        "status": "OK", "availability": availability, "p4d_input": p4d_input,
        "voice_name": p5b.GOOGLE_VOICE_NAME, "language_code": p5b.GOOGLE_LANGUAGE_CODE,
        "sent_text_sha256": sent_text_sha256, "sent_text_matches_input": sent_text_sha256 == p4d_input["sha256"],
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
            print("target_phrase_results:", result["asr"]["target_phrase_results"])
            print("nani_ga_okiru:", result["asr"]["nani_ga_okiru"])
