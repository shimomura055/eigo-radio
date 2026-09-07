# ============================================================
# gate3_a2_flagship_runtime_evidence.py
# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01
# Gate 3 runtime evidence (1): A2英語本文 "showed strong" 保全音声を
# 実際にProduction Cascade経路(修正後、evaluate_attempt_with_cascade_
# detail、enable_connected_speech_equivalence_layer=True)へ投入する。
#
# 新規TTS生成は行わない(既存の保全音声・既知のPrimary ASR結果を再利用)。
# Secondary ASR(Azure)+local faster-whisperの実呼び出しのみ発生する
# (Standard同期、小額)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import er005_cost_logger as cl
import er006_secondary_asr_01 as secondary_asr

WAV_PATH = ("er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2/narration/"
            "attempts/point_two_attempt1_custom35d6860b.wav")
DIAG_RAW_PATH = "er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/point_two_showed_show_diag/diag_raw_evidence.json"
OUT_DIR = "er011_output/open122_connected_speech_equivalence_layer_production_wiring_01"

raw = json.load(open(DIAG_RAW_PATH, encoding="utf-8"))
canonical_text = raw["canonical_text"]
primary_attempt1_text = next(r["asr_text"] for r in raw["production_asr_full_noprompt"] if r["label"] == "attempt1")

print("canonical_text(先頭160字):", canonical_text[:160])
print("primary_attempt1_text(既知、実データ、先頭160字):", primary_attempt1_text[:160])

cl.install(f"{OUT_DIR}/gate3_a2_flagship_raw_usage_log.jsonl")

detail_out = {}
verified, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
    canonical_text, primary_attempt1_text, [], WAV_PATH, language="en-US",
    ledger_phrases=None, cascade_enabled=True,
    enable_connected_speech_equivalence_layer=True, detail_out=detail_out)

print("\n=== 結果 ===")
print("verified:", verified)
print("stop_retrying:", stop_retrying)
print("classification:", cls.classification)
print("should_pass:", cls.should_pass)
print("connected_speech_equivalence_layer_invoked:", detail_out.get("connected_speech_equivalence_layer_invoked"))
print("cascade_invoked:", detail_out.get("cascade_invoked"))
for s in detail_out.get("steps", []):
    print(" step:", {k: v for k, v in s.items() if k != "text"} | {"text_preview": (s.get("text") or "")[:120]})

result_record = {
    "wav_path": WAV_PATH,
    "canonical_text": canonical_text,
    "primary_attempt1_text": primary_attempt1_text,
    "verified": verified,
    "stop_retrying": stop_retrying,
    "classification": cls.classification,
    "should_pass": cls.should_pass,
    "reason": cls.reason,
    "connected_speech_info": cls.connected_speech_info,
    "detail": {k: v for k, v in detail_out.items() if k != "classification"},
}
with open(f"{OUT_DIR}/gate3_a2_flagship_result.json", "w", encoding="utf-8") as f:
    json.dump(result_record, f, ensure_ascii=False, indent=2, default=str)
print(f"\n結果保存: {OUT_DIR}/gate3_a2_flagship_result.json")
