# ============================================================
# er003_v1_b1_p5a_generate.py
# ER-003-B1-P5A: 日本語TTS原稿忠実性スクリーニング
# ============================================================
# P4Dで実際に使用したのと完全に同一の全文ひらがな入力を、複数の日本語
# TTSエンジンで1回ずつ生成し、原稿忠実性(省略・追加がないか)を比較
# する。Google Cloud TTS/Amazon Pollyは、本実行環境ではパッケージ・
# 認証情報のいずれも未整備のため実行できない(明示的に報告し、勝手な
# 代替エンジンへは差し替えない)。Azure Speechのみ実行する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p5a_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p4d_audio as p4d
import er003_b1_p5a_audio as p5a

OUT_DIR = "er003_output/b1_p5a/A01"
MANAGEMENT_ID = "ER-003-B1-P5A"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _mkdirs() -> None:
    for sub in ("source", "azure_ja-JP-NanamiNeural/raw", "azure_ja-JP-NanamiNeural/asr",
                "google_cloud_tts", "amazon_polly", "instruction"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def _step_load_input_and_check_availability() -> dict:
    p4d_input = p5a.load_p4d_input()
    marked_text = p5a.load_p4d_marked_text()
    availability = p5a.check_engine_availability()

    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump({
            "p4d_hiragana_script_path": p5a.P4D_HIRAGANA_SCRIPT_PATH,
            "p4d_hiragana_script_sha256": p4d_input["sha256"],
            "p4d_marked_text_path": p5a.P4D_MARKED_TEXT_PATH,
        }, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/source/availability.json", "w", encoding="utf-8") as f:
        json.dump(availability, f, ensure_ascii=False, indent=2)

    return {"p4d_input": p4d_input, "marked_text": marked_text, "availability": availability}


def _run_azure(p4d_text: str, marked_text: str, tts_call_fn, sleep_function) -> dict:
    prompt = p4d_text  # 指示section4: 変更せずそのまま送信(スタイル指定・prefixなし)
    pcm, retries, ok, err = common._call_tts_with_retry(
        tts_call_fn, prompt, max_retry=p5a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "reason": f"Azure Speech合成が失敗: {err}", "call_count": 1 + retries}

    call_metadata = dict(tts_call_fn.last_result_metadata) if tts_call_fn.last_result_metadata else None

    wav_path = f"{OUT_DIR}/azure_ja-JP-NanamiNeural/raw/A01_p5a_azure_ja-JP-NanamiNeural.wav"
    with open(wav_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    asr_result = None
    if recognized is not None:
        with open(f"{OUT_DIR}/azure_ja-JP-NanamiNeural/asr/asr_transcript.txt", "w", encoding="utf-8") as f:
            f.write(recognized)

        content_check = p4d.check_full_text_content(recognized, marked_text)

        normalized = p5a.asr_reading_normalize(recognized, work_dir=f"{OUT_DIR}/azure_ja-JP-NanamiNeural/_sudachi_work")
        with open(f"{OUT_DIR}/azure_ja-JP-NanamiNeural/asr/asr_reading_normalized.txt", "w", encoding="utf-8") as f:
            f.write(normalized)

        target_phrase_results = p5a.check_target_phrases(normalized)

        asr_result = {
            "status": "OK", "recognized_text_ja_JP": recognized, "content_check": content_check,
            "asr_reading_normalized": normalized, "target_phrase_results": target_phrase_results,
        }
    else:
        asr_result = {"status": "ERROR", "reason": stt_err}

    return {
        "status": "OK", "voice_name": p5a.AZURE_VOICE_NAME, "region": os.getenv("SPEECH_REGION"),
        "sent_text": prompt, "sent_text_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "call_count": 1 + retries, "retry_count": retries, "call_metadata": call_metadata,
        "wav_path": wav_path, "wav_sha256": _sha256_file(wav_path),
        "duration_seconds": metrics["duration_seconds"], "clipping_detected": metrics["clipping_detected"],
        "asr": asr_result,
    }


def run() -> dict:
    _mkdirs()
    load_step = _step_load_input_and_check_availability()

    results = {"azure_speech": None, "google_cloud_tts": None, "amazon_polly": None}

    if load_step["availability"]["azure_speech"]["available"]:
        tts_call_fn = p5a.make_azure_tts_call_fn()
        results["azure_speech"] = _run_azure(load_step["p4d_input"]["text"], load_step["marked_text"], tts_call_fn, sleep_fn)
    else:
        results["azure_speech"] = {"status": "NOT_EXECUTED", "reason": load_step["availability"]["azure_speech"]["reason"]}

    for engine_key in ("google_cloud_tts", "amazon_polly"):
        if not load_step["availability"][engine_key]["available"]:
            results[engine_key] = {"status": "NOT_EXECUTED", "reason": load_step["availability"][engine_key]["reason"]}

    return {"status": "OK", "load_step": load_step, "results": results}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    for engine, r in result["results"].items():
        print(engine, "->", r["status"] if r else None)
    if result["results"]["azure_speech"] and result["results"]["azure_speech"]["status"] == "OK":
        azure = result["results"]["azure_speech"]
        print("azure duration:", azure["duration_seconds"])
        if azure["asr"]["status"] == "OK":
            print("target_phrase_results:", azure["asr"]["target_phrase_results"])
