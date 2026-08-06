# ============================================================
# er003_v1_b1_p7a_generate.py
# ER-003-B1-P7A: Geminiモデル監査・3.1単一call限定検証
# ============================================================
# P4Dで生成した「英語5件を目印へ置換した直後」の漢字かな交じり原稿
# (er003_output/b1_p4d/A01/source/pattern_a_with_markers.txt)を変更せず
# 使用し、gemini-3.1-flash-tts-preview・voice Aoede・単一TTS call・
# chunk分割なし・技術retryなしで生成する。分割方式やmarker処理の再調整
# は行わない。MFA・英語Component置換・Dynamics3・B1本文・pushは対象外。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p7a_generate.py

from __future__ import annotations

import json
import os

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p7a_audio as p7a

OUT_DIR = "er003_output/b1_p7a/A01"
INPUT_PATH = "er003_output/b1_p4d/A01/source/pattern_a_with_markers.txt"


def _mkdirs() -> None:
    for sub in ("source", "raw", "asr", "audit"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def step1_model_audit() -> dict:
    client = None
    baseline_available = p7a.model_is_available(p7a.BASELINE_MODEL_NAME)
    candidate_available = p7a.model_is_available(p7a.CANDIDATE_MODEL_NAME)
    audit = {
        "baseline_model_name": p7a.BASELINE_MODEL_NAME,
        "baseline_model_evidence": "er002_common.py:53 MODEL_NAME (frozen spec, used unconditionally by "
                                    "er002_gemini_client.make_tts_call_fn -> generate_content(model=...))",
        "baseline_model_confirmed_accessible_via_api_list": baseline_available,
        "candidate_model_name": p7a.CANDIDATE_MODEL_NAME,
        "candidate_model_confirmed_accessible_via_api_list": candidate_available,
        "api": "Gemini Developer API (google-genai SDK, genai.Client(api_key=...), not Vertex AI)",
        "sdk": "google-genai",
        "voice_name": p7a.VOICE_NAME,
        "branch_decision": "3.1未満のため検証実施" if p7a.BASELINE_MODEL_NAME != p7a.CANDIDATE_MODEL_NAME else "既に3.1のため新規生成なし",
    }
    with open(f"{OUT_DIR}/audit/model_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    return audit


def step2_prepare_input() -> dict:
    with open(INPUT_PATH, encoding="utf-8") as f:
        input_text = f.read()
    input_sha256 = p7a.sha256_text(input_text)
    with open(f"{OUT_DIR}/source/input_text.txt", "w", encoding="utf-8") as f:
        f.write(input_text)
    marker_count = input_text.count(p7a.MARKER_TOKEN)
    info = {
        "input_path": INPUT_PATH,
        "input_sha256": input_sha256,
        "char_count": len(input_text),
        "marker_count": marker_count,
        "marker_count_matches_expected": marker_count == p7a.EXPECTED_MARKER_COUNT,
    }
    with open(f"{OUT_DIR}/source/input_hashes.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    return {**info, "input_text": input_text}


def step3_generate_tts(input_text: str, tts_call_fn=None, sleep_function=None) -> dict:
    call_fn = tts_call_fn or p7a.make_tts_call_fn_for_model(p7a.CANDIDATE_MODEL_NAME, p7a.VOICE_NAME)
    prompt = p7a.build_tts_prompt(input_text, p7a.JAPANESE_STYLE_PREFIX)

    with open(f"{OUT_DIR}/source/instruction.txt", "w", encoding="utf-8") as f:
        f.write(p7a.JAPANESE_STYLE_PREFIX)
    with open(f"{OUT_DIR}/source/full_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p7a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "phase": "tts_generation", "reason": f"3.1単一callが失敗: {err}"}

    wav_path = f"{OUT_DIR}/raw/A01_p7a_gemini31_single_call.wav"
    with open(wav_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    return {
        "status": "OK",
        "wav_path": wav_path,
        "call_count": 1 + retries,
        "retry_count": retries,
        "sha256": p7a.sha256_file(wav_path),
        "duration_seconds": metrics["duration_seconds"],
        "clipping_detected": metrics["clipping_detected"],
        "model_used": p7a.CANDIDATE_MODEL_NAME,
        "voice_used": p7a.VOICE_NAME,
    }


def step4_asr_and_diff(wav_path: str, input_text: str) -> dict:
    recognized, err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    if recognized is None:
        return {"status": "ERROR", "reason": err}

    with open(f"{OUT_DIR}/asr/asr_transcript.txt", "w", encoding="utf-8") as f:
        f.write(recognized)

    key_expr = p7a.check_key_expressions(recognized)
    diff = p7a.diff_input_vs_asr(input_text, recognized)

    with open(f"{OUT_DIR}/asr/key_expression_check.json", "w", encoding="utf-8") as f:
        json.dump(key_expr, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/asr/diff_report.json", "w", encoding="utf-8") as f:
        json.dump(diff, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "recognized_text": recognized, "key_expr": key_expr, "diff": diff}


def run(tts_call_fn=None, sleep_function=None) -> dict:
    _mkdirs()
    audit = step1_model_audit()

    if audit["baseline_model_name"] == audit["candidate_model_name"]:
        return {"status": "STOPPED", "phase": "branch_decision",
                "reason": "現行モデルが既に3.1のため新規生成を行わない", "audit": audit}

    prep = step2_prepare_input()
    gen = step3_generate_tts(prep["input_text"], tts_call_fn=tts_call_fn, sleep_function=sleep_function)
    if gen["status"] != "OK":
        return {**gen, "audit": audit, "prep": prep}

    asr = step4_asr_and_diff(gen["wav_path"], prep["input_text"])

    return {"status": "OK", "audit": audit, "prep": prep, "gen": gen, "asr": asr}


if __name__ == "__main__":
    result = run()
    print("status:", result["status"])
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        print("wav_path:", result["gen"]["wav_path"])
        print("duration_seconds:", result["gen"]["duration_seconds"])
        print("clipping_detected:", result["gen"]["clipping_detected"])
        print("key_expr_all_present:", result["asr"]["key_expr"]["all_key_expressions_present"])
        print("marker_count:", result["asr"]["key_expr"]["marker_count"])
        print("similarity_ratio:", result["asr"]["diff"]["similarity_ratio"])
