# ============================================================
# er033_output/phase2_ja_evidence_01/run_ja_flashlite_evidence_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 2
# ============================================================
# Meta A2 japanese_title 1segmentのspeech_metadata_flash_lite backend
# 実測(JA speech_metadataの初実測)。既存Production関数
# n3_tts.generate_a2_japanese_with_reading_safety()をそのまま
# tts_backend="speech_metadata_flash_lite"で呼ぶ(委任文3節)。
#
# 既存Production artifact(Meta A2 japanese_title.wav、
# er019_output/family_x_audio_production_wiring_01/
# family_x_b3_production_wiring_01__run_01/a2/narration/japanese_title.wav)
# は一切上書きしない(別途新規out_pathへ書く)。
#
# 実行方法(Production .venv、TTS_EXECUTION_MODE=STANDARD必須):
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er033_output/phase2_ja_evidence_01/run_ja_flashlite_evidence_01.py
from __future__ import annotations

import json
import os

import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl

OUT_DIR = "er033_output/phase2_ja_evidence_01"
OUT_WAV = f"{OUT_DIR}/japanese_title_flashlite.wav"
RAW_USAGE_LOG = f"{OUT_DIR}/raw_usage_log.jsonl"

# Meta A2 japanese_title canonical text(既存entry_point.json由来、
# er019_output/family_x_audio_production_wiring_01/
# family_x_b3_production_wiring_01__run_01/entry_point.json)。
JAPANESE_TITLE = "AIからの電話だと思ったら…中に“人”がいた？　MetaのMuseで起きたまさかの展開"


def main() -> None:
    assert os.environ.get("TTS_EXECUTION_MODE") == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を設定してから実行してください"
        "(委任文: 全TTSでSTANDARD、逐語記録)。")
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(RAW_USAGE_LOG)
    with cl.logging_context("phase2_ja_evidence_meta_japanese_title", "tts"):
        with cl.segment_context("japanese_title"):
            result = n3_tts.generate_a2_japanese_with_reading_safety(
                JAPANESE_TITLE, OUT_WAV,
                n3_tts.expected_substring_ja(JAPANESE_TITLE),
                max_extra_chars=30,
                tts_backend="speech_metadata_flash_lite")
    result["canonical_text"] = JAPANESE_TITLE
    with open(f"{OUT_DIR}/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[PHASE2-JA-EVIDENCE] status={result.get('status')} "
          f"model={result.get('model')} out={OUT_WAV}")


if __name__ == "__main__":
    main()
