# ============================================================
# er003_v1_b1_p4a_generate.py
# ER-003-B1-P4A: Preview TTS入力監査と5マーカー再生成
# ============================================================
# Phase 1: P4で実際に使ったTTS入力の静的監査(新規TTS呼び出しなし)
# Phase 2: 修正後marker map・TTS scriptの構築 + API call前の確定チェック
# Phase 3: チェック通過後のみ、日本語Preview rawを1回だけ再生成・確認
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p4a_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p4_audio as p4
import er003_b1_p4a_audio as p4a

OUT_DIR = "er003_output/b1_p4a/A01"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _save_wav_pcm(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def _mkdirs() -> None:
    for sub in ("audit", "source", "raw"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def _load_pattern_a_and_used_forms():
    pattern_a_text = p4.load_pattern_a_text()
    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    used_forms = next(p for p in raw["patterns"] if p["pattern_id"] == "A")["used_forms"]
    return pattern_a_text, used_forms


def run_phase1_audit() -> dict:
    _mkdirs()
    pattern_a_text, used_forms = _load_pattern_a_and_used_forms()
    original_marker_map = p4.build_marker_map(pattern_a_text, used_forms)

    if not os.path.exists(p4a.P4_TTS_INPUT_PATH):
        return {"status": "STOPPED", "phase": "Phase1", "reason": f"P4のTTS入力ファイルが見つかりません: {p4a.P4_TTS_INPUT_PATH}"}

    with open(p4a.P4_TTS_INPUT_PATH, encoding="utf-8") as f:
        p4_actual_input = f.read()

    audit = p4a.audit_tts_input(p4_actual_input, p4a._USED_FORMS, original_marker_map)
    audit_full = {
        "p4_tts_input_path": p4a.P4_TTS_INPUT_PATH,
        "p4_tts_input_sha256": _sha256_file(p4a.P4_TTS_INPUT_PATH),
        "p4_tts_input_text": p4_actual_input,
        "original_marker_map": original_marker_map,
        **audit,
    }

    with open(f"{OUT_DIR}/audit/tts_input_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_full, f, ensure_ascii=False, indent=2)

    audit_md = _build_audit_markdown(audit_full)
    with open(f"{OUT_DIR}/audit/tts_input_audit.md", "w", encoding="utf-8") as f:
        f.write(audit_md)

    if audit["case"] not in ("A", "B"):
        return {
            "status": "STOPPED", "phase": "Phase1",
            "reason": f"静的監査で原因をA/Bに分類できませんでした(case={audit['case']})",
            "audit": audit_full,
        }

    return {"status": "OK", "audit": audit_full, "pattern_a_text": pattern_a_text, "used_forms": used_forms}


def _build_audit_markdown(audit: dict) -> str:
    lines = [
        "# ER-003-B1-P4A Phase 1: TTS入力静的監査レポート",
        "",
        f"- 対象ファイル: `{audit['p4_tts_input_path']}`",
        f"- sha256: `{audit['p4_tts_input_sha256']}`",
        "",
        "## used form残存数(5件)",
        "",
        "| used form | 残存数 |",
        "|---|---|",
    ]
    for uf, count in audit["used_form_counts"].items():
        lines.append(f"| {uf} | {count} |")
    lines += ["", "## マーカー出現数(5件)", "", "| マーカー | 出現数 |", "|---|---|"]
    for marker, count in audit["marker_counts"].items():
        lines.append(f"| {marker} | {count} |")
    lines += [
        "",
        f"- ASCII英字残存数: {audit['ascii_letter_count']}",
        f"- マーカー総数: {audit['marker_total']}",
        "",
        f"## 判定: Case {audit['case']}",
        "",
        audit["case_reason"],
    ]
    return "\n".join(lines) + "\n"


def run_phase2_build_fixed(pattern_a_text: str, used_forms: list) -> dict:
    fixed_marker_map = p4a.build_marker_map_fixed(pattern_a_text, used_forms)
    fixed_script = p4a.build_tts_script_with_markers_fixed(pattern_a_text, fixed_marker_map)

    with open(f"{OUT_DIR}/source/pattern_a_tts_with_5_markers_fixed.txt", "w", encoding="utf-8") as f:
        f.write(fixed_script)
    with open(f"{OUT_DIR}/source/marker_map_fixed.json", "w", encoding="utf-8") as f:
        json.dump(fixed_marker_map, f, ensure_ascii=False, indent=2)

    checks = p4a.verify_pre_call_checks(fixed_script, fixed_marker_map, pattern_a_text)
    if not checks["all_passed"]:
        return {
            "status": "STOPPED", "phase": "Phase2",
            "reason": "API call前の確定チェックに1つ以上失敗したため、TTSを呼ばず停止します",
            "checks": checks, "fixed_marker_map": fixed_marker_map, "fixed_script": fixed_script,
        }

    return {
        "status": "OK", "fixed_marker_map": fixed_marker_map, "fixed_script": fixed_script,
        "fixed_script_path": f"{OUT_DIR}/source/pattern_a_tts_with_5_markers_fixed.txt",
        "checks": checks,
    }


def run_phase3_generate(fixed_script: str, fixed_marker_map: list, tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    prompt = p4a.build_tts_prompt(fixed_script, p4a.JAPANESE_STYLE_PREFIX)
    if tts_call_fn is None:
        tts_call_fn = gclient.make_tts_call_fn(p4a.VOICE_NAME)

    pcm, retries, ok, err = common._call_tts_with_retry(
        tts_call_fn, prompt, max_retry=p4a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "phase": "Phase3", "reason": f"日本語Preview TTSが失敗: {err}"}

    wav_path = f"{OUT_DIR}/raw/preview_ja_with_5_markers_fixed.wav"
    _save_wav_pcm(wav_path, pcm)
    call_count = 1 + retries
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    content_check = None
    if recognized is not None:
        content_check = p4.check_ja_content(recognized, fixed_marker_map)
        content_check["recognized_text_ja_JP"] = recognized
        content_check["status"] = "OK"
    else:
        content_check = {"status": "ERROR", "reason": stt_err}

    return {
        "status": "OK",
        "wav_path": wav_path, "sha256": _sha256_file(wav_path),
        "duration_seconds": metrics["duration_seconds"], "clipping_detected": metrics["clipping_detected"],
        "call_count": call_count, "retry_count": retries,
        "content_check": content_check,
    }


def run() -> dict:
    p1 = run_phase1_audit()
    if p1["status"] != "OK":
        return p1

    p2 = run_phase2_build_fixed(p1["pattern_a_text"], p1["used_forms"])
    if p2["status"] != "OK":
        return {**p2, "phase1_audit": p1["audit"]}

    p3 = run_phase3_generate(p2["fixed_script"], p2["fixed_marker_map"])
    if p3["status"] != "OK":
        return {**p3, "phase1_audit": p1["audit"], "phase2_checks": p2["checks"]}

    metadata = {
        "management_id": "ER-003-B1-P4A",
        "article_id": "A01",
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "phase1_audit": p1["audit"],
        "phase2_fixed_marker_map": p2["fixed_marker_map"],
        "phase2_fixed_script_path": p2["fixed_script_path"],
        "phase2_fixed_script_sha256": _sha256_text(p2["fixed_script"]),
        "phase2_pre_call_checks": p2["checks"],
        "phase3_preview_ja_tts": {
            "path": p3["wav_path"], "sha256": p3["sha256"],
            "duration_seconds": p3["duration_seconds"], "clipping_detected": p3["clipping_detected"],
            "call_count": p3["call_count"], "retry_count": p3["retry_count"],
        },
        "phase3_content_check": p3["content_check"],
        "mfa_executed": False,
        "english_tts_calls_made": 0,
        "b1_body_generated": False,
        "combined_audio_generated": False,
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
        print("case:", md["phase1_audit"]["case"])
        print("preview duration:", md["phase3_preview_ja_tts"]["duration_seconds"])
        print("is_japanese:", md["phase3_content_check"].get("is_japanese"))
        print("all_markers_present_once:", md["phase3_content_check"].get("all_markers_present_once"))
