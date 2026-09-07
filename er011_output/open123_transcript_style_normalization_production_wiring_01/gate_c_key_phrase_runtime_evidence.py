# ============================================================
# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01
# Runtime evidence (c): 英語Key Phrase経路(generate_key_phrase_component_
# verified -> generate_narration_snippet_verified_strict -> Cascade -> ...
# -> evaluate_attempt_with_cascade_detail(enable_non_latin_cascade=True))
# へ、Transcript Style Normalization配線後の分類が想定通りであることを
# 実経路で確認する。
#
# Part 1(既存PASS維持の確認、実データ): er003_output/b1_p9a/A02/audit/
# key_phrase_components_result.json の実preserved KP音声5件(いずれも
# contraction無し)を、実wav_path+実canonical/asr textでCascade実関数
# (evaluate_attempt_with_cascade_detail、enable_non_latin_cascade=True、
# Key Phrase呼び出しと同じkwarg)へ投入し、既存classification(全て
# NORMALIZED_MATCH/EXACT_MATCH相当)が変化しないことを確認する。
#
# Part 2(合成、明記): 実データにcontractionを含むKey Phraseが無いため、
# canonical_text/asr_textのみ合成(fabricated)し、audio_pathは実物の
# preserved wav(kp_1_opt_out.wav、内容はcontractionと無関係、classify_
# asr_match自体はテキストのみで判定するため実行結果に影響しない)を
# そのまま流用する。1件は救済されるべきケース(標準contraction、否定
# 保持のみ)、1件は救済されてはいけないケース(can/can't、否定反転)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import er006_secondary_asr_01 as secondary_asr

KP_RESULT_PATH = "er003_output/b1_p9a/A02/audit/key_phrase_components_result.json"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate_c_key_phrase_result.json")


def run_kp_call(canonical_text, asr_text, wav_path, note):
    """実際のKey Phrase呼び出しと同じkwarg(enable_non_latin_cascade=True、
    他opt-inフラグは一切渡さない)でCascade実関数を呼ぶ。"""
    detail = secondary_asr.evaluate_attempt_with_cascade_detail(
        canonical_text, asr_text, prior_results=[], wav_path=wav_path, language="en-US",
        enable_non_latin_cascade=True)
    return {
        "note": note, "canonical_text": canonical_text, "asr_text": asr_text, "wav_path": wav_path,
        "verified": detail["verified"], "final_status": detail["final_status"],
        "human_review_required": detail["human_review_required"],
        "cascade_invoked": detail["cascade_invoked"],
        "non_latin_cascade_invoked": detail["non_latin_cascade_invoked"],
    }


def main():
    kp_data = json.load(open(KP_RESULT_PATH, encoding="utf-8"))
    part1 = []
    for k, v in kp_data.items():
        canonical = v["text"]
        asr_text = v.get("asr_text")
        wav_path = v["path"]
        if asr_text is None or not os.path.exists(wav_path):
            continue
        r = run_kp_call(canonical, asr_text, wav_path,
                         note=f"実データ(kp_{k})、契約形/短縮形なし、既存PASSが維持されることの確認")
        r["existing_asr_verified_before_this_task"] = v.get("asr_verified")
        part1.append(r)
        print(f"[Part1 kp_{k}] canonical={canonical!r} asr={asr_text!r} -> "
              f"verified={r['verified']} final_status={r['final_status']} "
              f"(existing asr_verified={v.get('asr_verified')})")

    part1_ok = all(r["verified"] == r["existing_asr_verified_before_this_task"] for r in part1)

    synthetic_wav = kp_data["1"]["path"]  # 実物のpreserved wav(内容はcontractionと無関係、流用のみ)
    part2 = []
    r_rescue = run_kp_call(
        "The manager does not check the schedule every day.",
        "The manager doesn't check the schedule every day.",
        synthetic_wav,
        note="合成(fabricated text pair、audio_pathは実物wavを流用、内容はcontractionと無関係だが"
             "classify_asr_matchはtextのみで判定するため実行結果に影響しない)。標準contraction"
             "(否定保持)のみの差 -> 救済されるべきケース。")
    part2.append(r_rescue)
    print(f"[Part2 rescue] -> verified={r_rescue['verified']} final_status={r_rescue['final_status']}")

    r_negative = run_kp_call(
        "You can access the shared folder from any device.",
        "You can't access the shared folder from any device.",
        synthetic_wav,
        note="合成(fabricated text pair、audio_pathは実物wavを流用)。can/can't(否定反転) "
             "-> 絶対に救済されてはいけないNegative control。")
    part2.append(r_negative)
    print(f"[Part2 negative] -> verified={r_negative['verified']} final_status={r_negative['final_status']}")

    part2_ok = (r_rescue["verified"] is True and r_rescue["final_status"] == "TRANSCRIPT_STYLE_NORMALIZED_MATCH"
                and r_negative["verified"] is False and r_negative["final_status"] == "TRUE_CONTENT_MISMATCH")

    summary = {
        "part1_existing_kp_pass_unchanged": part1,
        "part1_ok": part1_ok,
        "part2_synthetic_contraction_checks": part2,
        "part2_ok": part2_ok,
        "overall_ok": part1_ok and part2_ok,
    }
    json.dump(summary, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\npart1_ok={part1_ok} part2_ok={part2_ok} overall_ok={summary['overall_ok']}")
    print(f"saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
