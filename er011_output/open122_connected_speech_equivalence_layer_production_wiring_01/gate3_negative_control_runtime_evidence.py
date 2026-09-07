# ============================================================
# gate3_negative_control_runtime_evidence.py
# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01
# Gate 3 runtime evidence (3): true content mismatch非acceptの証拠
#
# Trial-01 N1(claimed canonical "showed"、実発話"show"、flagshipと同一
# 音韻環境の最も厳しい敵対的陰性対照)とTrial-02 T2N4(claimed canonical
# "turned"、実発話"turn"、SecondaryがcanonicalをMIXEDに誤支持する陰性
# 対照)を、修正後のProduction Cascade経路(evaluate_attempt_with_cascade、
# enable_connected_speech_equivalence_layer=True)へ実際に投入し、
# ACCEPTしない(=既存TRUE_CONTENT_MISMATCHのまま)ことを確認する。
# 実音声(Trial-01/02の保全音声)を再利用し、Secondary Azure/local
# faster-whisperは実際に呼び出す(小額課金)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import er005_cost_logger as cl
import er006_secondary_asr_01 as secondary_asr

OUT_DIR = "er011_output/open122_connected_speech_equivalence_layer_production_wiring_01"
cl.install(f"{OUT_DIR}/gate3_negative_control_raw_usage_log.jsonl")

CASES = [
    {
        "id": "N1_show_not_showed",
        "canonical": "Young travelers still showed strong interest in the results.",
        "primary_asr_text": "Young travelers still show strong interest in the results.",
        "wav_path": "er011_output/connected_speech_equivalence_layer_trial_01/audio/N1_show_not_showed.wav",
        "expect_not_accept_reason": "flagshipと同一環境の敵対的陰性対照(実際にshowと発話、showedではない)",
    },
    {
        "id": "T2N4_turn_not_turned",
        "canonical": "The cars turned back before reaching the bridge.",
        "primary_asr_text": "The cars turn back before reaching the bridge.",
        "wav_path": "er011_output/connected_speech_equivalence_layer_trial_02/audio/T2N4_turn_not_turned.wav",
        "expect_not_accept_reason": "Secondaryが誤ってcanonicalを支持するがlocalが正しく実発話を支持するMIXED_EVIDENCE",
    },
]

results = []
for case in CASES:
    print(f"\n=== {case['id']} ===")
    detail_out = {}
    verified, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
        case["canonical"], case["primary_asr_text"], [], case["wav_path"], language="en-US",
        ledger_phrases=None, cascade_enabled=True,
        enable_connected_speech_equivalence_layer=True, detail_out=detail_out)
    print("canonical:", case["canonical"])
    print("primary_asr_text:", case["primary_asr_text"])
    print("verified:", verified, "classification:", cls.classification, "should_pass:", cls.should_pass)
    for s in detail_out.get("steps", []):
        print(" step:", {k: v for k, v in s.items() if k != "text"} | {"text_preview": (s.get("text") or "")[:120]})
    ok = (not verified) and (not cls.should_pass) and cls.classification == "TRUE_CONTENT_MISMATCH"
    print("false_accept_check(0件が必須):", "OK(acceptされなかった)" if ok else "FAIL(誤ってacceptされた)")
    results.append({
        "id": case["id"], "canonical": case["canonical"], "primary_asr_text": case["primary_asr_text"],
        "verified": verified, "classification": cls.classification, "should_pass": cls.should_pass,
        "reason": cls.reason, "connected_speech_info": cls.connected_speech_info,
        "false_accept_check_passed": ok,
        "detail": {k: v for k, v in detail_out.items() if k != "classification"},
    })

with open(f"{OUT_DIR}/gate3_negative_control_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

all_ok = all(r["false_accept_check_passed"] for r in results)
print(f"\n=== 集計: false_accept=0件必須、全件PASS={all_ok} ===")
print(f"結果保存: {OUT_DIR}/gate3_negative_control_result.json")
