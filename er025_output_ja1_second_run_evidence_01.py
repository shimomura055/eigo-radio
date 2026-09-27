# ============================================================
# er025_output_ja1_second_run_evidence_01.py
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正2回目=closeout)
#
# JA-1(Meta記事`family_x_b3_production_wiring_01__run_01`のa2/japanese_title)
# の2回目実行(cache hit・追加web lookup 0回)evidence。
#
# 手順: runner(er019_family_x_audio_production_runner_01.py)にはsegment単位
# の限定実行オプションが無いため、runnerが実際に呼んでいるのと同一の
# Production関数(er003_v1_n3_01_tts_generate.generate_a2_japanese_with_
# reading_safety、runner側呼び出しコード上記547行付近と同じ引数
# max_extra_chars=30・source_context省略=既定""・max_attempts省略=既定6)を
# 同一canonical_text(1回目実行時の実際のaudit記録
# `er019_output/family_x_audio_production_wiring_01/family_x_b3_production_
# wiring_01__run_01/a2/audit/tts_generation_results.json`の
# segments.japanese_title.canonical_textから取得、記事本文を書き換えるもの
# ではない)で再現する。出力は別の評価用out_dirへ保存し、本番runner側
# artifact(narration/japanese_title.wav等)・Master Audio Storeは一切
# 変更しない。
# ============================================================
from __future__ import annotations

import json
import os

# 前回JA-1(1回目)でBatch modeのまま実行してしまった手順ミスの再発防止。
# 必ずSTANDARD modeを明示してから実行する。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

OUT_DIR = "er025_output/pronunciation_resolution_phase2_evidence_01/ja1_second_run_evidence_01"
OUT_WAV = f"{OUT_DIR}/japanese_title_second_run.wav"

# 1回目実行時の実際のaudit記録(tts_generation_results.json)から取得した
# canonical_text(記事本文そのもの、書き換えなし)。
CANONICAL_TEXT = (
    "AIからの電話だと思ったら…中に“人”がいた？　MetaのMuseで起きたまさかの展開"
)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    result = tts_gen.generate_a2_japanese_with_reading_safety(
        CANONICAL_TEXT, OUT_WAV, tts_gen.expected_substring_ja(CANONICAL_TEXT),
        max_extra_chars=30)

    resolver_info = result.get("ja_pronunciation_resolver_info", {})
    summary = {
        "canonical_text": CANONICAL_TEXT,
        "source_context": "",
        "tts_execution_mode_env": os.environ.get("TTS_EXECUTION_MODE"),
        "status": result.get("status"),
        "asr_verified": result.get("asr_verified"),
        "asr_text": result.get("asr_text"),
        "audio_classification": result.get("audio_classification"),
        "tts_input_text_after_reading_safety": result.get("tts_input_text_after_reading_safety"),
        "foreign_token_findings": result.get("foreign_token_findings"),
        "web_lookup_called": resolver_info.get("web_lookup_called"),
        "resolved": resolver_info.get("resolved"),
        "unresolved_human_review": resolver_info.get("unresolved_human_review"),
        "reading_dictionary": resolver_info.get("reading_dictionary"),
        "fallback_used": result.get("fallback_used"),
        "reason": result.get("reason"),
    }
    with open(f"{OUT_DIR}/ja1_second_run_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/ja1_second_run_evidence_full_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
