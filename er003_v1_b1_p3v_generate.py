# ============================================================
# er003_v1_b1_p3v_generate.py
# ER-003-B1-P3V: 明示Break／Timestampによる英語差し込み再検証
# ============================================================
# Phase 1(API機能確認)を実行し、ネイティブBreak/SSML break/
# Mark・Timepoint/TTS由来Timestampのいずれかが使える場合のみ
# Phase 2A(Break方式)またはPhase 2B(Mark/Timestamp方式)へ進む。
# いずれも使えない場合は、句読点・ASR・最長無音方式へ戻らず、
# ここで停止して報告する(指示section 6/16の明記通り)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3v_generate.py

from __future__ import annotations

import json
import os

import er003_b1_p3t_audio as p3t
import er003_b1_p3v_capability as cap

OUT_DIR = "er003_output/b1_p3v/A01"

SOURCE_INTEGRATED_SENTENCE = p3t.SOURCE_INTEGRATED_SENTENCE
SOURCE_JAPANESE_FULL_SENTENCE = p3t.SOURCE_JAPANESE_FULL_SENTENCE
SOURCE_ENGLISH_KEYWORD = p3t.SOURCE_ENGLISH_KEYWORD
EXPLICIT_BOUNDARY = "枠内シュート｜を記録できないまま"


def _build_capability_report_markdown(result: dict) -> str:
    lines = [
        "# ER-003-B1-P3V Phase 1: TTS API機能確認レポート",
        "",
        "推測ではなく、実装コード(`er002_gemini_client.py`)とインストール済み",
        "`google-genai` SDKの型定義(実際のフィールド一覧)を直接調べた結果。",
        "",
        "## 対象",
        "",
        f"- TTS model: `{result['tts_model']}`",
        f"- SDK: `{result['sdk_name']} {result['sdk_version']}`",
        f"- request形式: `{result['request_form']}`",
        f"- response形式: `{result['response_form']}`",
        "",
        "## 判定結果",
        "",
        "| 優先順位 | 機能 | 対応 | 根拠 |",
        "|---|---|---|---|",
        f"| 1 | ネイティブBreak | {'対応' if result['native_break_supported'] else '非対応'} "
        f"| `SpeechConfig`のフィールドは `{result['speech_config_fields']}` のみで、"
        f"break/pause/silence/mark系の専用フィールドは存在しない |",
        f"| 2 | SSML `<break>` | {'対応' if result['ssml_break_supported'] else '非対応'} "
        f"| {result['ssml_break_note']} |",
        f"| 3 | Mark / Bookmark / Timepoint | {'対応' if result['mark_timepoint_supported'] else '非対応'} "
        f"| `SpeechConfig`にmark/bookmark/timepoint系フィールドが存在しない |",
        f"| 4 | TTS由来Timestamp / SDK offset metadata | {'対応' if result['tts_timestamp_supported'] else '非対応'} "
        f"| `Part`のフィールドは `{result['part_fields']}` で、timestamp/offset系フィールドが存在しない。"
        f"{result['part_metadata_note']} |",
        "",
        f"## 採用方式と根拠",
        "",
    ]
    if result["any_capability_available"]:
        lines.append("いずれかの機能が利用可能と判定されたため、Phase 2へ進む(本レポート作成時点では未実施)。")
    else:
        lines.extend([
            "上記4項目のいずれも利用できないと判定した。この環境のGemini TTS"
            "(`gemini-2.5-pro-preview-tts`、`google-genai`経由の`generate_content`"
            "呼び出し)は、plain textのpromptを渡して生PCMバイト列のみを受け取る"
            "インターフェースであり、SSML等のマークアップ解釈、Mark/Bookmark/"
            "Timepointの指定、生成結果に対する文字・単語レベルのタイムスタンプや"
            "audio offsetメタデータの返却、のいずれにも対応していない。",
            "",
            "指示section 6の分岐(「いずれも使えない：停止して報告」)に従い、"
            "Phase 2A/Phase 2Bへは進まず、ここで停止する。句読点・ASR・最長無音"
            "方式へは戻らない(指示section 6・16の明記通り)。",
        ])
    return "\n".join(lines) + "\n"


def run() -> dict:
    for sub in ("capability", "source"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    with open(f"{OUT_DIR}/source/integrated_source.txt", "w", encoding="utf-8") as f:
        f.write(SOURCE_INTEGRATED_SENTENCE)
    with open(f"{OUT_DIR}/source/japanese_source.txt", "w", encoding="utf-8") as f:
        f.write(SOURCE_JAPANESE_FULL_SENTENCE)
    with open(f"{OUT_DIR}/source/english_keyword.txt", "w", encoding="utf-8") as f:
        f.write(SOURCE_ENGLISH_KEYWORD)

    capability_result = cap.check_tts_capability()
    with open(f"{OUT_DIR}/capability/tts_capability_result.json", "w", encoding="utf-8") as f:
        json.dump(capability_result, f, ensure_ascii=False, indent=2)

    report_md = _build_capability_report_markdown(capability_result)
    with open(f"{OUT_DIR}/capability/tts_capability_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    if not capability_result["any_capability_available"]:
        status = {
            "management_id": "ER-003-B1-P3V",
            "article_id": "A01",
            "record_status": "PROTOTYPE",
            "approval_status": "NOT_APPROVED",
            "status": "STOPPED",
            "stop_phase": "Phase 1",
            "stop_reason": (
                "ネイティブBreak/SSML break/Mark・Bookmark・Timepoint/"
                "TTS由来Timestamp・SDK offset metadataのいずれも、現在使用中の"
                "Gemini TTS(gemini-2.5-pro-preview-tts、google-genai SDK)では"
                "利用できないと確認したため(指示section 6・16の明記通りの"
                "停止条件)。"
            ),
            "fallback_to_previous_methods": False,
            "explicit_boundary_target": EXPLICIT_BOUNDARY,
            "source_integrated_sentence": SOURCE_INTEGRATED_SENTENCE,
            "source_japanese_full_sentence": SOURCE_JAPANESE_FULL_SENTENCE,
            "source_english_keyword": SOURCE_ENGLISH_KEYWORD,
            "capability_result": capability_result,
            "phase2_reached": False,
            "tts_calls_made": 0,
            "japanese_raw_audio_generated": False,
            "final_audio_generated": False,
            "pattern_a_full_generated": False,
            "b1_body_generated": False,
        }
        with open(f"{OUT_DIR}/generation_stopped_status.json", "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        return {"status": "STOPPED", "reason": status["stop_reason"], "capability_result": capability_result}

    # Phase 1で機能が利用可能と判定された場合のみここに到達する。
    # 本ステージの実行時点(このリポジトリのTTS実装)では到達しない分岐であり、
    # Phase 2A/2Bの実装はここでは行わない(未到達コードとして残さない)。
    return {"status": "PHASE2_REQUIRED", "capability_result": capability_result}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] == "STOPPED":
        print(result["reason"])
    cr = result["capability_result"]
    print(f"native_break_supported={cr['native_break_supported']}")
    print(f"ssml_break_supported={cr['ssml_break_supported']}")
    print(f"mark_timepoint_supported={cr['mark_timepoint_supported']}")
    print(f"tts_timestamp_supported={cr['tts_timestamp_supported']}")
