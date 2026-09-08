# ============================================================
# er011_output/open127_em_dash_wiring_01/run_runtime_evidence.py
# OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01: Runtime evidence
# ============================================================
# Production module(er011_open121_repetition_qa_production_01.py、em dash
# 修正適用後)を、Production entry(evaluate_repetition_qa()、
# apply_repetition_qa_gate()が実際に呼ぶのと同一関数)経由で、既存wavへ
# 直接実行する。新規ASR呼び出しはローカルfaster-whisperのみ(追加API
# 課金ゼロ)。
#
# 対象:
#  - negative controls(4件、Voice B意図的並行構文、flagged=False必須):
#    phase1_02 point_two attempt1-3 + trial_08 point_two
#  - positive controls(10件、既知真の重複、flagged=True維持必須):
#    method_d_flag23_review_01 index0-7(真の重複8件)+ known_case 2件
#    (point_two_BUGGY_UNFIXED_backup / in_one_line_BEFORE_FIX_buggy_backup)
#
# 実行方法: .venv/Scripts/python.exe er011_output/open127_em_dash_wiring_01/
#   run_runtime_evidence.py
from __future__ import annotations

import json
import os
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

import er011_open121_repetition_qa_production_01 as repetition_qa  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def main():
    review = load("er011_output/method_d_flag23_review_01/classification_table.json")
    sweep_classified = load("er011_output/open121_existing_audio_dprime_sweep_01/results/classified_table.json")
    canonical_by_segment = {
        "point_two": next(x["canonical_text"] for x in review if x["segment_id"] == "point_two"),
        "in_one_line": next(x["canonical_text"] for x in review if x["segment_id"] == "in_one_line"),
    }
    known_case_path = {
        "known_case::point_two_BUGGY_UNFIXED_backup":
            "er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/"
            "duplication_diagnosis_review_fix_02/2_a2_point_two_narration_BUGGY_UNFIXED_pending_human_review.wav",
        "known_case::in_one_line_BEFORE_FIX_buggy_backup":
            "er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/"
            "duplication_diagnosis_review_fix_02/3_a2_in_one_line_narration_BEFORE_FIX_buggy.wav",
    }

    positive_items = []
    for it in review[:8]:
        positive_items.append({
            "item_id": it["item_id"], "path": it["path"], "canonical_text": it["canonical_text"],
        })
    for it in sweep_classified:
        if it["item_id"] in known_case_path:
            seg_key = "point_two" if "point_two" in it["item_id"] else "in_one_line"
            positive_items.append({
                "item_id": it["item_id"], "path": known_case_path[it["item_id"]],
                "canonical_text": canonical_by_segment[seg_key],
            })
    assert len(positive_items) == 10, f"positive件数が想定外: {len(positive_items)}"

    negative_items = []
    parts = load("er012_output/editorial_b_family_production_phase1_02/b1b/parts.json")
    canonical_phase1_02 = parts["point_two_body"]
    attempts_dir = os.path.join(REPO_ROOT, "er012_output", "editorial_b_family_production_phase1_02",
                                 "b1b", "narration", "attempts")
    for fn in sorted(os.listdir(attempts_dir)):
        if fn.startswith("point_two_attempt") and fn.endswith("englishstyleprefixwidemargin.wav"):
            negative_items.append({
                "item_id": f"phase1_02::{fn[:-4]}",
                "path": f"er012_output/editorial_b_family_production_phase1_02/b1b/narration/attempts/{fn}",
                "canonical_text": canonical_phase1_02,
            })
    tts_gen = load("er012_output/editorial_b_voices_trial_08_audio/p1/b1b/audit/tts_generation_results.json")
    negative_items.append({
        "item_id": "er012_laneb_trial08::er012_output/editorial_b_voices_trial_08_audio/p1::b1b::point_two",
        "path": "er012_output/editorial_b_voices_trial_08_audio/p1/b1b/narration/point_two.wav",
        "canonical_text": tts_gen["segments"]["point_two"]["text"],
    })
    assert len(negative_items) == 4, f"negative件数が想定外: {len(negative_items)}"

    results = {"positive_controls": [], "negative_controls": []}
    t0 = time.time()

    for it in positive_items:
        path = os.path.join(REPO_ROOT, it["path"])
        r = repetition_qa.evaluate_repetition_qa(path, it["canonical_text"], language="en")
        results["positive_controls"].append({
            "item_id": it["item_id"], "path": it["path"],
            "flagged": r["flagged"],
            "method_a_ngram_flagged": r["method_a_ngram"]["flagged"],
            "method_d_flagged": r["method_d_spectral_long_lag"]["flagged"],
            "method_d_prime_flagged": r["method_d_prime_spectral_short_lag"]["flagged"],
        })
        print(f"[positive] {it['item_id'][:70]:70s} flagged={r['flagged']}")

    for it in negative_items:
        path = os.path.join(REPO_ROOT, it["path"])
        r = repetition_qa.evaluate_repetition_qa(path, it["canonical_text"], language="en")
        results["negative_controls"].append({
            "item_id": it["item_id"], "path": it["path"],
            "flagged": r["flagged"],
            "method_a_ngram_flagged": r["method_a_ngram"]["flagged"],
            "method_d_flagged": r["method_d_spectral_long_lag"]["flagged"],
            "method_d_prime_flagged": r["method_d_prime_spectral_short_lag"]["flagged"],
        })
        print(f"[negative] {it['item_id'][:70]:70s} flagged={r['flagged']}")

    elapsed = round(time.time() - t0, 1)
    tp_ok = sum(1 for r in results["positive_controls"] if r["flagged"])
    fp_ok = sum(1 for r in results["negative_controls"] if not r["flagged"])
    summary = {
        "management_id": "OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01",
        "entry_point": "er011_open121_repetition_qa_production_01.evaluate_repetition_qa() "
                        "(apply_repetition_qa_gate()が実際に呼ぶ関数と同一、Production entry経由)",
        "positive_controls_flagged_true_count": f"{tp_ok}/10",
        "negative_controls_flagged_false_count": f"{fp_ok}/4",
        "all_expected_pass": (tp_ok == 10 and fp_ok == 4),
        "elapsed_seconds": elapsed,
        "cost_jpy": 0,
        "note": "faster-whisperローカルCPU実行のみ、追加API課金ゼロ。em dash修正後の"
                "_normalize_tokens()を経由(re.sub em-dash-only)。",
    }
    results["summary"] = summary
    with open(os.path.join(OUT_DIR, "runtime_evidence.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
