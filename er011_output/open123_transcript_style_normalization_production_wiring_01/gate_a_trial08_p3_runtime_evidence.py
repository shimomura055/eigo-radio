# ============================================================
# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01
# Runtime evidence (a): Trial-08 P3 point_two(3回STOPPED、do not/don't)を
# 保全音声+実Primary ASR結果で、修正後の実Production関数
# (er006_preprod_hardening_01_validation.classify_asr_match、
# er006_secondary_asr_01.evaluate_attempt_with_cascade_detail)へ実際に
# 投入し、救済されることを確認する。追加のTTS/ASR呼び出しは行わない
# (保全済みのcanonical_text/asr_textをそのままclassify_asr_matchへ渡す。
# evaluate_attempt_with_cascade_detailはwav_pathを受け取るが、Primary#1の
# 時点でTRANSCRIPT_STYLE_NORMALIZED_MATCHでverified=Trueとなるため、
# Cascade内の追加ASR呼び出し[Primary#2/Secondary等]は一切発生しない)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr

EVIDENCE_PATH = ("er012_output/editorial_b_voices_trial_08_audio/p3/b1b/"
                  "audit/stopped_audio_evidence/point_two_result.json")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate_a_trial08_p3_result.json")


def main():
    data = json.load(open(EVIDENCE_PATH, encoding="utf-8"))
    canonical = data["canonical_text"]
    results = []
    for att in data["attempts_log"]:
        asr_text = att["asr_text"]
        wav_path = att["attempt_audio_path"]
        # (1) classify_asr_match単体(直接呼び出し、Production公開関数=新規wrapper)
        cls = val.classify_asr_match(canonical, asr_text)
        # (2) 実際のCascadeエントリポイント(evaluate_attempt_with_cascade_detail)
        # へ実wav_pathで投入し、verified/human_review_required/追加ASR呼び出しの
        # 有無まで確認する(既存3引数のみ、opt-inフラグは一切渡さない=通常の
        # 本文経路と同じ呼び出し方)。
        detail = secondary_asr.evaluate_attempt_with_cascade_detail(
            canonical, asr_text, prior_results=[], wav_path=wav_path, language="en-US")
        entry = {
            "attempt": att["attempt"],
            "asr_text": asr_text,
            "audio_path": wav_path,
            "original_audio_classification_before_fix": att["audio_classification"],
            "classify_asr_match_direct": {
                "classification": cls.classification,
                "should_pass": cls.should_pass,
                "should_retry": cls.should_retry,
                "reason": cls.reason,
            },
            "evaluate_attempt_with_cascade_detail": {
                "verified": detail["verified"],
                "stop_retrying": detail["stop_retrying"],
                "final_status": detail["final_status"],
                "human_review_required": detail["human_review_required"],
                "cascade_invoked": detail["cascade_invoked"],
                "steps": [{"step": s["step"], "classification": s.get("classification")} for s in detail["steps"]],
            },
        }
        results.append(entry)
        print(f"attempt {att['attempt']}: before_fix={att['audio_classification']} "
              f"-> classify_asr_match={cls.classification} (should_pass={cls.should_pass}) "
              f"-> cascade verified={detail['verified']} final_status={detail['final_status']} "
              f"cascade_invoked={detail['cascade_invoked']}")

    all_rescued = all(r["classify_asr_match_direct"]["should_pass"]
                       and r["classify_asr_match_direct"]["classification"] == "TRANSCRIPT_STYLE_NORMALIZED_MATCH"
                       and r["evaluate_attempt_with_cascade_detail"]["verified"]
                       and not r["evaluate_attempt_with_cascade_detail"]["cascade_invoked"]
                       for r in results)
    summary = {"canonical_text": canonical, "attempts": results, "all_3_rescued_with_zero_extra_asr_calls": all_rescued}
    json.dump(summary, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nall_3_rescued_with_zero_extra_asr_calls: {all_rescued}")
    print(f"saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
