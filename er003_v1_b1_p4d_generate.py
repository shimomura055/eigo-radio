# ============================================================
# er003_v1_b1_p4d_generate.py
# ER-003-B1-P4D: 全文ひらがな読み正規化・日本語Preview検証
# ============================================================
# 承認済みPattern Aを5 used form→「目印」置換→SudachiPy全文ひらがな
# 読み正規化→1回のTTS callで音声化する。MFA・英語Component置換・
# Dynamics3・B1本文・通し音声には進まない(このステージは日本語raw
# 音声の検証で停止する研究ステージ)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p4d_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p4_audio as p4
import er003_b1_p4d_audio as p4d

OUT_DIR = "er003_output/b1_p4d/A01"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mkdirs() -> None:
    for sub in ("source", "preview/raw", "asr"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def _load_pattern_a_and_used_forms() -> tuple[str, list[dict]]:
    pattern_a_text = p4.load_pattern_a_text()
    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        pattern_a_raw_json_text = f.read()
    pattern_a_used_forms = json.loads(pattern_a_raw_json_text)
    used_forms = next(p for p in pattern_a_used_forms["patterns"] if p["pattern_id"] == "A")["used_forms"]
    return pattern_a_text, used_forms


# ============================================================
# Step 1: source保存 + marker置換 + 全文ひらがな読み正規化 + 静的検証
# ============================================================
def _step_build_and_verify_reading() -> dict:
    pattern_a_text, used_forms = _load_pattern_a_and_used_forms()

    marked = p4d.build_marker_replaced_source(pattern_a_text, used_forms)
    if not (marked["used_form_residue_all_zero"] and marked["marker_count_is_five"]):
        return {"status": "STOPPED", "phase": "marker_replacement", "reason": "marker置換の検証に失敗", "marked": marked}

    morphemes = p4d.sudachi_tokenize(marked["marked_text"], work_dir=f"{OUT_DIR}/_sudachi_work")
    reading_map = p4d.build_reading_map(morphemes)
    hiragana_script = p4d.build_full_hiragana_script(reading_map)
    verification = p4d.verify_reading_conversion(marked["marked_text"], reading_map, hiragana_script)
    key_expr_pre_tts = p4d.check_key_expressions(hiragana_script)

    with open(f"{OUT_DIR}/source/pattern_a_approved.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/pattern_a_with_markers.txt", "w", encoding="utf-8") as f:
        f.write(marked["marked_text"])
    with open(f"{OUT_DIR}/source/pattern_a_full_hiragana.txt", "w", encoding="utf-8") as f:
        f.write(hiragana_script)
    with open(f"{OUT_DIR}/source/reading_map.json", "w", encoding="utf-8") as f:
        json.dump(reading_map, f, ensure_ascii=False, indent=2)

    source_hashes = {
        "pattern_a_source_path": p4.PATTERN_A_SOURCE_PATH,
        "pattern_a_source_sha256": _sha256_file(p4.PATTERN_A_SOURCE_PATH),
        "pattern_a_text_sha256": _sha256_text(pattern_a_text),
        "pattern_a_char_count": len(pattern_a_text),
        "pattern_a_with_markers_sha256": _sha256_text(marked["marked_text"]),
        "pattern_a_full_hiragana_sha256": _sha256_text(hiragana_script),
    }
    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump(source_hashes, f, ensure_ascii=False, indent=2)

    _write_reading_audit_md(pattern_a_text, marked, verification, key_expr_pre_tts, source_hashes)

    return {
        "status": "OK" if verification["all_passed"] else "STOPPED",
        "phase": None if verification["all_passed"] else "reading_verification",
        "reason": None if verification["all_passed"] else "全文ひらがな読み正規化の静的検証に不合格のため、TTSを呼び出さず停止",
        "pattern_a_text": pattern_a_text, "used_forms": used_forms, "marked": marked,
        "reading_map": reading_map, "hiragana_script": hiragana_script,
        "verification": verification, "key_expr_pre_tts": key_expr_pre_tts,
        "source_hashes": source_hashes,
    }


def _write_reading_audit_md(pattern_a_text, marked, verification, key_expr, source_hashes) -> None:
    lines = [
        "# ER-003-B1-P4D 読み正規化監査\n",
        f"- Pattern A文字数: {len(pattern_a_text)}\n",
        f"- marker(目印)置換件数: {marked['marker_count']}(5であるべき)\n",
        f"- used form残存: {marked['used_form_residue']}\n",
        "\n## 静的検証結果\n",
        f"- reconstruction_matches: {verification['reconstruction_matches']}\n",
        f"- unconvertible_token_count: {len(verification['unconvertible_tokens'])}\n",
        f"- ascii_letter_count: {verification['ascii_letter_count']}\n",
        f"- arabic_numeral_count: {verification['arabic_numeral_count']}\n",
        f"- kanji_count: {verification['kanji_count']}\n",
        f"- katakana_letter_count: {verification['katakana_letter_count']}\n",
        f"- marker_hiragana_count: {verification['marker_hiragana_count']}(5であるべき)\n",
        f"- sentence_count_matches: {verification['sentence_count_matches']}"
        f"(source={verification['source_sentence_count']}, script={verification['script_sentence_count']})\n",
        f"- punctuation_sequence_matches: {verification['punctuation_sequence_matches']}\n",
        f"- **all_passed: {verification['all_passed']}**\n",
        "\n## 重点表現(TTS前、期待変換結果)\n",
        f"- 最後の数分 → {key_expr['last_few_minutes']['expected']}: present={key_expr['last_few_minutes']['present']}\n",
        f"- 守備を固め → {key_expr['defend']['expected']}: present={key_expr['defend']['present']}, "
        f"forbidden(しゅびをかためる)present={key_expr['defend']['forbidden_form_present']}\n",
        f"- わずかなリード → {key_expr['narrow_lead']['expected']}: present={key_expr['narrow_lead']['present']}\n",
        "\n## source hashes\n",
        f"```json\n{json.dumps(source_hashes, ensure_ascii=False, indent=2)}\n```\n",
    ]
    with open(f"{OUT_DIR}/source/reading_audit.md", "w", encoding="utf-8") as f:
        f.writelines(lines)


# ============================================================
# Step 2: 全文ひらがなscriptを1回のTTS callで生成
# ============================================================
def _step_generate_tts(hiragana_script: str, tts_call_fn, sleep_function) -> dict:
    prompt = p4d.build_tts_prompt(hiragana_script, p4d.JAPANESE_STYLE_PREFIX)
    pcm, retries, ok, err = common._call_tts_with_retry(
        tts_call_fn, prompt, max_retry=p4d.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "phase": "tts_generation", "reason": f"全文ひらがなTTSが失敗: {err}"}

    wav_path = f"{OUT_DIR}/preview/raw/A01_preview_full_hiragana_with_markers.wav"
    with open(wav_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    return {
        "status": "OK", "wav_path": wav_path, "call_count": 1 + retries, "retry_count": retries,
        "sha256": _sha256_file(wav_path), "duration_seconds": metrics["duration_seconds"],
        "clipping_detected": metrics["clipping_detected"],
    }


# ============================================================
# Step 3: ASR診断 + 同一読み正規化処理での比較
# ============================================================
def _step_asr_and_reading_comparison(wav_path: str, marked_text: str) -> dict:
    recognized, err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    if recognized is None:
        return {"status": "ERROR", "reason": err}

    with open(f"{OUT_DIR}/asr/asr_transcript.txt", "w", encoding="utf-8") as f:
        f.write(recognized)

    content_check = p4d.check_full_text_content(recognized, marked_text)

    asr_morphemes = p4d.sudachi_tokenize(recognized, work_dir=f"{OUT_DIR}/_sudachi_work_asr")
    asr_reading_map = p4d.build_reading_map(asr_morphemes)
    asr_reading_normalized = p4d.build_full_hiragana_script(asr_reading_map)
    with open(f"{OUT_DIR}/asr/asr_reading_normalized.txt", "w", encoding="utf-8") as f:
        f.write(asr_reading_normalized)

    key_expr_asr = p4d.check_key_expressions(asr_reading_normalized)

    return {
        "status": "OK", "recognized_text_ja_JP": recognized, "content_check": content_check,
        "asr_reading_normalized": asr_reading_normalized, "key_expr_asr": key_expr_asr,
    }


# ============================================================
# 実行本体
# ============================================================
def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()
    call_fn = tts_call_fn or gclient.make_tts_call_fn(p4d.VOICE_NAME)

    reading_step = _step_build_and_verify_reading()
    if reading_step["status"] != "OK":
        return reading_step

    gen = _step_generate_tts(reading_step["hiragana_script"], call_fn, sleep_function)
    if gen["status"] != "OK":
        return {**gen, "reading_step": reading_step}

    asr = _step_asr_and_reading_comparison(gen["wav_path"], reading_step["marked"]["marked_text"])

    return {
        "status": "OK", "reading_step": reading_step, "gen": gen, "asr": asr,
    }


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        print("raw_wav_path:", result["gen"]["wav_path"])
        print("duration_seconds:", result["gen"]["duration_seconds"])
        print("verification_all_passed:", result["reading_step"]["verification"]["all_passed"])
        if result["asr"]["status"] == "OK":
            print("asr_key_expr:", result["asr"]["key_expr_asr"])
