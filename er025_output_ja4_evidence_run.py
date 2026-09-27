# ============================================================
# er025_output_ja4_evidence_run.py
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正1回目)
# JA-4 runtime evidence: Family Z Melos名(Dionysius/Melos/Selinuntius)を
# source_context="family_z_melos"でseed済みの状態で、共有JA TTS入口
# (generate_a2_japanese_with_reading_safety、Production関数)を実際に
# 直接呼び、TTS/ASR PASS + web lookup 0回(cache hit)を確認する。
#
# 実データ注記: er026_output/family_z_production_e2e_01/melos/run_01/の
# 既存preview.txt/comment_1.jsonは、LLM writerが既にカタカナ表記
# (「ディオニュシオス」「ディオニュシウス」等、記事間で不統一)で直接
# 出力しており、Latin表記の"Dionysius"トークン自体が本文中に残らない
# (Foreign Token Gateの検出対象外=resolverが発火する機会が無い)。
# そのため、本resolver(BLOCKER-2)の実際の動作を示すには、Phase 2の
# JA-2(Figma)と同じ方式で、Latin表記を含む代表的なfixture文を用いる
# (作品本文を書き換えるものではない、TTS入口の直接呼び出しのみ)。
# ============================================================
from __future__ import annotations

import json
import os

os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er025_entity_pronunciation_resolver_core_01 as pron_resolver_core
import er003_v1_n3_01_tts_generate as tts_gen

OUT_DIR = "er025_output/pronunciation_resolution_phase2_evidence_01/ja4_melos_evidence_01"
OUT_WAV = f"{OUT_DIR}/melos_evidence.wav"

FIXTURE_TEXT = "小さな王国の支配者Dionysiusは、羊飼いのMelosを捕らえ、友人Selinuntiusを人質にしました。"


def main():
    result = tts_gen.generate_a2_japanese_with_reading_safety(
        FIXTURE_TEXT, OUT_WAV, tts_gen.expected_substring_ja(FIXTURE_TEXT),
        source_context="family_z_melos")

    resolver_info = result.get("ja_pronunciation_resolver_info", {})
    summary = {
        "fixture_text": FIXTURE_TEXT,
        "source_context": "family_z_melos",
        "status": result.get("status"),
        "asr_verified": result.get("asr_verified"),
        "asr_text": result.get("asr_text"),
        "tts_input_text_after_reading_safety": result.get("tts_input_text_after_reading_safety"),
        "web_lookup_called": resolver_info.get("web_lookup_called"),
        "resolved": resolver_info.get("resolved"),
        "unresolved_human_review": resolver_info.get("unresolved_human_review"),
        "reading_dictionary": resolver_info.get("reading_dictionary"),
        "fallback_used": result.get("fallback_used"),
        "reason": result.get("reason"),
    }
    with open(f"{OUT_DIR}/ja4_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/ja4_evidence_full_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
