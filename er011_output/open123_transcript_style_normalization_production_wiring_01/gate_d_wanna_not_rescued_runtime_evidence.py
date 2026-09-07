# ============================================================
# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01
# Runtime evidence (d): wanna系(方式iv、口語的縮約)はユーザー決定
# (2026-09-07)により不採用のため、本層(標準contraction展開のみ)では
# 非救済のまま維持されることを、OPEN-122 Trial-01の実測音声(P6_dont_you、
# "Don't you want to come with us?"の実発話、Primary ASRが実際に
# "wanna"と誤書き起こしした実データ)を再利用して確認する。
# OPEN-122 Equivalence Layer(A2/B1本文限定、opt-inフラグ)で救済される
# かどうかは別層の話であり、本Gateでは意図的にそのフラグを渡さない
# (=Transcript Style Normalization単体の挙動を見る)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr

MANIFEST_PATH = "er011_output/connected_speech_equivalence_layer_trial_01/results/manifest.json"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate_d_wanna_result.json")


def main():
    m = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    by_id = {r["id"]: r for r in m.get("positive_results", [])}
    r = by_id["P6_dont_you"]
    canonical = r["claimed_canonical"]
    primary = r["primary_asr_text"]
    wav_path = r["audio_path"]

    cls = val.classify_asr_match(canonical, primary)
    detail = secondary_asr.evaluate_attempt_with_cascade_detail(
        canonical, primary, prior_results=[], wav_path=wav_path, language="en-US")
    # enable_connected_speech_equivalence_layerもenable_non_latin_cascadeも
    # 渡さない(=本文/Key Phrase双方の既定呼び出しと同じ、Transcript Style
    # Normalization[本Gate対象]単体の挙動のみを見る)。

    result = {
        "id": "P6_dont_you", "canonical_text": canonical, "primary_asr_text": primary,
        "wav_path": wav_path,
        "classify_asr_match_direct": {
            "classification": cls.classification, "should_pass": cls.should_pass,
            "should_retry": cls.should_retry, "reason": cls.reason,
        },
        "evaluate_attempt_with_cascade_detail_no_optin_flags": {
            "verified": detail["verified"], "final_status": detail["final_status"],
            "human_review_required": detail["human_review_required"],
        },
        "not_rescued_as_expected": (not cls.should_pass) and cls.classification == "TRUE_CONTENT_MISMATCH",
    }
    json.dump(result, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"classify_asr_match: classification={cls.classification} should_pass={cls.should_pass}")
    print(f"cascade(no opt-in flags): verified={detail['verified']} final_status={detail['final_status']}")
    print(f"not_rescued_as_expected={result['not_rescued_as_expected']}")
    print(f"saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
