# ============================================================
# er003_v1_repro02_preview_audio_generate.py
# ER-003-REPRO-02-PREVIEW: ADD03 Preview音声生成(初回1回のみ)
# ============================================================
# A01最終Preview(preview_japanese_only_short.wav)/A02 Previewと完全に
# 同一の生成経路(er003_b1_p9a_audio.generate_narration_snippet、単一
# TTS call、ASR検証付きretryは使わない)を、承認済みADD03台本へそのまま
# 適用する。新しいinstruction/style/後処理は一切追加しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_repro02_preview_audio_generate.py

from __future__ import annotations

import json
import os

import er002_common as common
import er003_b1_p9a_audio as p9a

MANAGEMENT_ID = "ER-003-REPRO-02-PREVIEW"
ARTICLE_ID = "ADD03"
OUT_DIR = f"er003_output/b1_p9a/{ARTICLE_ID}"

APPROVED_SCRIPT_PATH = f"{OUT_DIR}/source/japanese_only_preview_script_draft.txt"


def load_approved_script() -> str:
    with open(APPROVED_SCRIPT_PATH, encoding="utf-8") as f:
        return f.read().strip()


def run() -> dict:
    os.makedirs(f"{OUT_DIR}/narration", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/asr", exist_ok=True)

    text = load_approved_script()
    out_path = f"{OUT_DIR}/narration/preview_japanese_only.wav"

    # 初回生成は1回のみ。generate_narration_snippet自体が持つ技術的
    # retry(API失敗等、common._call_tts_with_retry)以外の自動再生成は
    # 一切行わない(ASR検証付きgenerate_narration_snippet_verifiedは
    # 使わない、A02と同一条件)。
    result = p9a.generate_narration_snippet(text, "ja", out_path)

    if result.get("status") != "OK":
        with open(f"{OUT_DIR}/audit/preview_audio_generation_result.json", "w", encoding="utf-8") as f:
            json.dump({"management_id": MANAGEMENT_ID, "status": result.get("status"),
                       "reason": result.get("reason")}, f, ensure_ascii=False, indent=2)
        return result

    # ASR(診断のみ、内容起因の自動再生成トリガーにはしない)
    import er003_b1_p4_audio as p4
    asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="ja-JP", timeout_seconds=60.0)

    data, sr, channels, _ = common.read_wav_float(out_path)
    metrics = common.measure_metrics(data if data.ndim == 1 else data[:, 0], sr)

    with open(f"{OUT_DIR}/asr/preview_audio_asr.txt", "w", encoding="utf-8") as f:
        f.write(asr_text or "")

    generation_record = {
        "management_id": MANAGEMENT_ID,
        "article_id": ARTICLE_ID,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "approved_script_path": APPROVED_SCRIPT_PATH,
        "approved_script_text": text,
        "approved_script_char_count": len(text),
        "model": result["model"],
        "voice": result["voice"],
        "language": "ja",
        "single_speaker": True,
        "chunking": "none (single TTS call for the entire script)",
        "tts_call_count": result["call_count"],
        "technical_retry_count": result["retry_count"],
        "content_based_auto_regeneration_count": 0,
        "dynamics3_applied": False,
        "dynamics3_note": ("A01/A02のPreview生成関数(generate_narration_snippet)自体が"
                           "Dynamics3を呼び出していないことをコード確認済み。同一関数をそのまま"
                           "使用したため、ADD03でもDynamics3は適用していない。"),
        "path": out_path,
        "sha256": result["sha256"],
        "duration_seconds": result["duration_seconds"],
        "sample_rate": sr,
        "channels": 1,
        "clipping_detected": metrics["clipping_detected"],
        "peak": round(float(max(abs(data.min()), abs(data.max()))), 5),
        "trim_info": result["trim_info"],
        "asr_text": asr_text,
        "asr_error": asr_err,
    }
    with open(f"{OUT_DIR}/audit/preview_audio_generation_result.json", "w", encoding="utf-8") as f:
        json.dump(generation_record, f, ensure_ascii=False, indent=2)

    return generation_record


if __name__ == "__main__":
    result = run()
    print("status:", result.get("status", "OK"))
    if "path" in result:
        print("path:", result["path"])
        print("duration_seconds:", result["duration_seconds"])
        print("tts_call_count:", result["tts_call_count"])
        print("technical_retry_count:", result["technical_retry_count"])
        print("asr_text:", result["asr_text"])
