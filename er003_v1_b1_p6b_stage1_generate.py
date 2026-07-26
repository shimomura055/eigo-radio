# ============================================================
# er003_v1_b1_p6b_stage1_generate.py
# ER-003-B1-P6B Stage1: 2-Macrochunk日本語raw接続の生成・評価
# ============================================================
# 承認済みPattern Aを2-Macrochunk(文1+文2 / 文3+文4)へ分割し、各1回
# ずつTTS生成する(合計2回)。英語Componentへの置換は行わない
# (Stage2はStage1がユーザー試聴で合格した場合のみ実施)。Dynamics3も
# 適用しない(指示section5: 日本語接続の一次評価時には適用しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p6b_stage1_generate.py

from __future__ import annotations

import difflib
import hashlib
import json
import os
import time

import numpy as np

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p4_audio as p4
import er003_b1_p6a_audio as p6a
import er003_b1_p6b_audio as p6b

OUT_DIR = "er003_output/b1_p6b/A01"
MANAGEMENT_ID = "ER-003-B1-P6B"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mkdirs() -> None:
    for sub in ("source", "stage1/macrochunks", "stage1/connected", "instruction"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def _float_to_pcm_bytes(samples: "np.ndarray") -> bytes:
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767.0).astype(np.int16).tobytes()


def check_chunk_content(recognized_text: str, chunk: dict) -> dict:
    """P6Aのcheck_chunk_content相当(1chunkに複数markerを許容)を、
    ここでも同じ設計で使う(P6Aの関数はgenerate script内定義のため
    直接importできず、同じロジックをここに複製している。P6A自体の
    公開APIではないため、モジュール化はしない)。"""
    stripped = p4._strip_punctuation(recognized_text)
    ja_char_count = sum(
        1 for ch in recognized_text
        if ("぀" <= ch <= "ゟ") or ("゠" <= ch <= "ヿ") or ("一" <= ch <= "鿿")
    )
    ja_char_ratio = ja_char_count / len(recognized_text) if recognized_text else 0.0
    is_japanese = ja_char_ratio >= 0.5
    ascii_letter_count = len(p6a._ASCII_LETTER_PATTERN.findall(recognized_text))
    marker_count_in_recognized = stripped.count(p6b.MARKER_TOKEN)
    expected_marker_count = len(chunk["used_forms"])
    marker_ok = marker_count_in_recognized == expected_marker_count
    ref_stripped = p4._strip_punctuation(chunk["tts_text"])
    similarity_ratio = difflib.SequenceMatcher(None, ref_stripped, stripped).ratio()
    similarity_ok = similarity_ratio >= 0.5
    passed = is_japanese and ascii_letter_count == 0 and marker_ok and similarity_ok
    return {
        "recognized_text_ja_JP": recognized_text, "ja_char_ratio": round(ja_char_ratio, 4),
        "is_japanese": is_japanese, "ascii_letter_count": ascii_letter_count,
        "marker_count_in_recognized": marker_count_in_recognized, "expected_marker_count": expected_marker_count,
        "marker_ok": marker_ok, "content_similarity_ratio": round(similarity_ratio, 4),
        "similarity_ok": similarity_ok, "passed": passed,
    }


def _step_build_and_verify_plan() -> dict:
    pattern_a_text = p4.load_pattern_a_text()
    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    used_forms = next(p for p in raw["patterns"] if p["pattern_id"] == "A")["used_forms"]

    chunk_plan = p6b.build_macrochunk_plan(pattern_a_text, used_forms)
    static_check = p6b.verify_macrochunk_plan_static(chunk_plan, pattern_a_text)

    with open(f"{OUT_DIR}/source/pattern_a_approved.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/macrochunk_plan.json", "w", encoding="utf-8") as f:
        json.dump(chunk_plan, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/source/static_check.json", "w", encoding="utf-8") as f:
        json.dump(static_check, f, ensure_ascii=False, indent=2)

    return {"pattern_a_text": pattern_a_text, "used_forms": used_forms, "chunk_plan": chunk_plan, "static_check": static_check}


def _step_generate_macrochunks(chunk_plan: list, tts_call_fn, sleep_function) -> dict:
    results = {}
    for chunk in chunk_plan:
        prompt = p6b.build_tts_prompt(chunk["tts_text"], p6b.JAPANESE_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            tts_call_fn, prompt, max_retry=p6b.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        if not ok:
            return {"status": "STOPPED", "phase": "macrochunk_generation", "chunk_id": chunk["chunk_id"], "reason": f"TTSが失敗: {err}", "results": results}

        wav_path = f"{OUT_DIR}/stage1/macrochunks/macrochunk{chunk['chunk_id']}_ja.wav"
        with open(wav_path, "wb") as f:
            f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
        samples, sr, ch, _ = common.read_wav_float(wav_path)
        metrics = common.measure_metrics(samples, sr)

        recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
        content_check = check_chunk_content(recognized, chunk) if recognized is not None else {"status": "ERROR", "reason": stt_err}

        results[chunk["chunk_id"]] = {
            "status": "OK", "wav_path": wav_path, "call_count": 1 + retries, "retry_count": retries,
            "sha256": _sha256_file(wav_path), "duration_seconds": metrics["duration_seconds"],
            "clipping_detected": metrics["clipping_detected"], "samples": samples, "sample_rate": sr,
            "content_check": content_check,
        }
    return {"status": "OK", "results": results}


def _step_build_connected_variants(chunk_plan: list, gen_results: dict, sr: int) -> dict:
    """新規TTS callなしで、同一raw音声からMacrochunk間無音の異なる
    接続版を作る(0.8秒は必須、他は比較用で最大2件まで、指示section6)。"""
    pcm_chunks = [_float_to_pcm_bytes(gen_results[c["chunk_id"]]["samples"]) for c in chunk_plan]

    variants = {}
    all_pause_values = [p6b.MACROCHUNK_JOIN_PAUSE_SECONDS] + list(p6b.MACROCHUNK_JOIN_PAUSE_COMPARISON_CANDIDATES)
    for pause_seconds in all_pause_values:
        combined_pcm, pause_positions = common.assemble_audio(pcm_chunks, sample_rate=sr, pause_seconds=pause_seconds)
        combined_samples = common.pcm_bytes_to_float_mono(combined_pcm)
        label = f"{pause_seconds:.1f}s".replace(".", "p")
        path = f"{OUT_DIR}/stage1/connected/A01_stage1_connected_pause_{label}.wav"
        common.write_wav_float(path, combined_samples, sr, 1)
        metrics = common.measure_metrics(combined_samples, sr)
        variants[label] = {
            "pause_seconds": pause_seconds, "path": path, "sha256": _sha256_file(path),
            "duration_seconds": metrics["duration_seconds"], "clipping_detected": metrics["clipping_detected"],
            "is_honpen_standard": pause_seconds == p6b.MACROCHUNK_JOIN_PAUSE_SECONDS,
        }
    return {"status": "OK", "variants": variants}


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()
    call_fn = tts_call_fn or gclient.make_tts_call_fn(p6b.VOICE_NAME)

    plan_step = _step_build_and_verify_plan()
    if not plan_step["static_check"]["all_passed"]:
        return {"status": "STOPPED", "phase": "static_check", "reason": "Macrochunk計画の静的検証に不合格のため、TTSを呼び出さず停止", "plan_step": plan_step}

    chunk_plan = plan_step["chunk_plan"]

    gen = _step_generate_macrochunks(chunk_plan, call_fn, sleep_function)
    if gen["status"] != "OK":
        return {**gen, "plan_step": plan_step}

    sr = common.SAMPLE_RATE
    connected = _step_build_connected_variants(chunk_plan, gen["results"], sr)

    return {"status": "OK", "plan_step": plan_step, "gen": gen, "connected": connected}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        for cid, r in result["gen"]["results"].items():
            print(cid, "call_count:", r["call_count"], "content_check_passed:", r["content_check"].get("passed"))
        for label, v in result["connected"]["variants"].items():
            print("connected", label, v["path"], v["duration_seconds"])
