# ============================================================
# gate3_b1_runtime_evidence.py
# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01
# Gate 3 runtime evidence (2): B1英語本文
#
# Part A: B1の実本文segment1件を実生成(Standard、既存承認済みhanshin
# テーマのpoint_two_body、小額課金)。修正後のProduction経路
# (news_tail_fix.generate_news_narration_wide_margin、
# enable_connected_speech_equivalence_layer=True)を通し、通常は
# EXACT/NORMALIZED_MATCHでLayerが不介入のまま合格することを確認する
# (出力はevidence専用ディレクトリのみ、既存Production narration
# ファイルは一切上書きしない)。
#
# Part B: Trial-01の"showed strong"型と同環境(カテゴリA/B/C、語末
# alveolar stop+次語頭alveolar stop)の合成fallthroughを、Trial-01の
# 実音声(P6_dont_you.wav、"want"の実発話を含む)を再利用して構成する。
# canonical="Don't you want to come with us?"(実音声どおり)に対し、
# Primary ASR側だけを"wan"(wantの語末/t/脱落)へ意図的に差し替えた
# 合成mismatchを与え、Secondary Azure/local faster-whisperは実音声へ
# 実際にASRを実行する(fabricatedなのはPrimary ASR文字列のみ、
# Secondary/localは本物のASR実行結果)。ACCEPTに到達することを確認する。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import er005_cost_logger as cl
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er006_secondary_asr_01 as secondary_asr

OUT_DIR = "er011_output/open122_connected_speech_equivalence_layer_production_wiring_01"

cl.install(f"{OUT_DIR}/gate3_b1_raw_usage_log.jsonl")

# ------------------------------------------------------------
# Part A: 実生成(hanshinテーマ point_two_body、既存承認済み本文の再利用。
# 新規記事コンテンツは作らない)
# ------------------------------------------------------------
parts = json.load(open("er003_output/n3_01/hanshin/b1b/parts.json", encoding="utf-8"))
body_text = parts["point_two_body"]
print("=== Part A: B1実本文segment、実生成(Standard) ===")
print("text:", body_text)

out_path = f"{OUT_DIR}/gate3_b1_real_generation_point_two_body.wav"
result_a = news_tail_fix.generate_news_narration_wide_margin(
    body_text, out_path, enable_connected_speech_equivalence_layer=True)
print("status:", result_a.get("status"))
print("audio_classification:", result_a.get("audio_classification"))
print("asr_text:", result_a.get("asr_text"))
print("connected_speech_info:", result_a.get("connected_speech_info"))

with open(f"{OUT_DIR}/gate3_b1_part_a_real_generation_result.json", "w", encoding="utf-8") as f:
    json.dump(result_a, f, ensure_ascii=False, indent=2, default=str)

# ------------------------------------------------------------
# Part B: 合成fallthrough(Trial-01の実音声P6_dont_you.wav再利用、
# Primary ASR文字列のみ"want"->"wan"へ意図的に差し替え)
# ------------------------------------------------------------
print("\n=== Part B: 合成fallthrough(Trial-01実音声P6再利用、カテゴリA/B/C環境) ===")
canonical_b = "Don't you want to come with us?"
fabricated_primary_asr_text = "Don't you wan to come with us?"
wav_path_b = "er011_output/connected_speech_equivalence_layer_trial_01/audio/P6_dont_you.wav"

detail_out_b = {}
verified_b, stop_retrying_b, cls_b = secondary_asr.evaluate_attempt_with_cascade(
    canonical_b, fabricated_primary_asr_text, [], wav_path_b, language="en-US",
    ledger_phrases=None, cascade_enabled=True,
    enable_connected_speech_equivalence_layer=True, detail_out=detail_out_b)

print("canonical:", canonical_b)
print("fabricated_primary_asr_text:", fabricated_primary_asr_text)
print("verified:", verified_b)
print("classification:", cls_b.classification)
print("should_pass:", cls_b.should_pass)
for s in detail_out_b.get("steps", []):
    print(" step:", {k: v for k, v in s.items() if k != "text"} | {"text_preview": (s.get("text") or "")[:120]})

result_b = {
    "wav_path": wav_path_b, "canonical_text": canonical_b,
    "fabricated_primary_asr_text": fabricated_primary_asr_text,
    "note": "Primary ASR文字列のみ意図的に改変した合成fallthrough。Secondary/localは"
            "実音声(Trial-01 P6_dont_you.wav)への実際のASR実行結果。",
    "verified": verified_b, "stop_retrying": stop_retrying_b,
    "classification": cls_b.classification, "should_pass": cls_b.should_pass,
    "reason": cls_b.reason, "connected_speech_info": cls_b.connected_speech_info,
    "detail": {k: v for k, v in detail_out_b.items() if k != "classification"},
}
with open(f"{OUT_DIR}/gate3_b1_part_b_synthetic_fallthrough_result.json", "w", encoding="utf-8") as f:
    json.dump(result_b, f, ensure_ascii=False, indent=2, default=str)
print(f"\n結果保存: {OUT_DIR}/gate3_b1_part_a_real_generation_result.json, "
      f"{OUT_DIR}/gate3_b1_part_b_synthetic_fallthrough_result.json")
