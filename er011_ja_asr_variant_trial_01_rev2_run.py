# ============================================================
# er011_ja_asr_variant_trial_01_rev2_run.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 修正2回目 実行
# ============================================================
# 修正1回目と同じ3つのアーティファクト(自作82件 test_dataset.json、
# 過去MISMATCH7件+過去PASS72件 historical_results.json)をそのまま再利用し
# (データを作り直さない)、Candidate B+C+D
# (er011_ja_asr_variant_trial_01_rev2.classify_with_candidate_additive_bcd)
# で再評価する。API支出は一切発生しない(Reading Resolverはdry-run stub)。
from __future__ import annotations

import json
import sys

import er011_ja_asr_variant_trial_01 as candidate_b
import er011_ja_asr_variant_trial_01_rev2 as candidate_bcd

OUT_DIR = "er011_output/ja_asr_variant_trial_01"


def classify_baseline(canonical, asr):
    return candidate_b.classify_with_baseline(canonical, asr)


def classify_bcd(canonical, asr):
    result, calls, tag = candidate_bcd.classify_with_candidate_additive_bcd(canonical, asr)
    return result, calls, tag


def run_synthetic():
    with open(f"{OUT_DIR}/test_dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    results = []
    for item in dataset:
        expected_pass = (item["expected"] == "PASS")
        baseline_result, baseline_calls = classify_baseline(item["canonical"], item["asr"])
        bcd_result, bcd_calls, bcd_tag = classify_bcd(item["canonical"], item["asr"])

        baseline_pass = baseline_result.should_pass
        bcd_pass = bcd_result.should_pass

        results.append({
            **item,
            "baseline_classification": baseline_result.classification,
            "baseline_should_pass": baseline_pass,
            "baseline_resolver_dry_run_calls": baseline_calls,
            "bcd_classification": bcd_result.classification,
            "bcd_should_pass": bcd_pass,
            "bcd_rescue_tag": bcd_tag,
            "bcd_resolver_dry_run_calls": bcd_calls,
            "correct": bcd_pass == expected_pass,
            "false_pass": (expected_pass is False) and (bcd_pass is True),
            "broke_a_baseline_correct": (baseline_pass == expected_pass) and (bcd_pass != expected_pass),
            "fixed_vs_baseline": (baseline_pass != expected_pass) and (bcd_pass == expected_pass),
        })

    summary = {
        "n": len(results),
        "correct": sum(1 for r in results if r["correct"]),
        "false_pass": sum(1 for r in results if r["false_pass"]),
        "broke_a_baseline_correct": sum(1 for r in results if r["broke_a_baseline_correct"]),
        "fixed_vs_baseline": sum(1 for r in results if r["fixed_vs_baseline"]),
        "resolver_dry_run_calls_total": sum(r["bcd_resolver_dry_run_calls"] for r in results),
    }

    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], {"n": 0, "correct": 0})
        by_category[r["category"]]["n"] += 1
        by_category[r["category"]]["correct"] += 1 if r["correct"] else 0

    return {"summary": summary, "by_category": by_category, "results": results}


def run_historical():
    with open(f"{OUT_DIR}/historical_results.json", encoding="utf-8") as f:
        hist = json.load(f)

    mismatch_results = []
    for case in hist["past_mismatch_cases"]:
        bcd_result, bcd_calls, bcd_tag = classify_bcd(case["canonical"], case["asr"])
        mismatch_results.append({
            **case,
            "bcd_classification": bcd_result.classification,
            "bcd_should_pass": bcd_result.should_pass,
            "bcd_rescue_tag": bcd_tag,
        })

    pass_results = []
    broke = []
    for case in hist["past_pass_cases"]:
        # rev1と同じ理由(REPORTの「修正1回目」節「methodology上の発見」参照)で、
        # historical_results.json内の古いフィールドは信用せず、baseline/
        # 追加方式を両方その場で再計算し、fresh な値同士で比較する。
        fresh_baseline_result, _ = classify_baseline(case["canonical"], case["asr"])
        bcd_result, bcd_calls, bcd_tag = classify_bcd(case["canonical"], case["asr"])
        entry = {
            **case,
            "fresh_baseline_classification": fresh_baseline_result.classification,
            "fresh_baseline_should_pass": fresh_baseline_result.should_pass,
            "bcd_classification": bcd_result.classification,
            "bcd_should_pass": bcd_result.should_pass,
            "bcd_rescue_tag": bcd_tag,
        }
        pass_results.append(entry)
        if entry["fresh_baseline_should_pass"] is True and entry["bcd_should_pass"] is False:
            broke.append(entry)

    summary = {
        "past_mismatch_total": len(mismatch_results),
        "past_mismatch_bcd_resolved_to_pass": sum(1 for r in mismatch_results if r["bcd_should_pass"]),
        "past_mismatch_bcd_still_mismatch": sum(1 for r in mismatch_results if not r["bcd_should_pass"]),
        "past_pass_total": len(pass_results),
        "past_pass_fresh_baseline_pass": sum(1 for r in pass_results if r["fresh_baseline_should_pass"]),
        "past_pass_bcd_still_pass": sum(1 for r in pass_results if r["bcd_should_pass"]),
        "past_pass_bcd_broke_true_regression": len(broke),
    }

    return {"summary": summary, "mismatch_results": mismatch_results,
            "pass_results": pass_results, "broke": broke}


def main():
    synthetic = run_synthetic()
    historical = run_historical()

    print("=== synthetic (82件) ===")
    print(json.dumps(synthetic["summary"], ensure_ascii=False, indent=2))
    for cat, s in synthetic["by_category"].items():
        print(f"  {cat}: {s}")

    print("\n=== historical (7 mismatch + 72 pass) ===")
    print(json.dumps(historical["summary"], ensure_ascii=False, indent=2))

    print("\n=== incorrect synthetic items (should be empty) ===")
    for r in synthetic["results"]:
        if not r["correct"]:
            print(f"  [{r['category']}] {r['note']}: bcd_classification={r['bcd_classification']} "
                  f"bcd_should_pass={r['bcd_should_pass']} expected={r['expected']}")

    print("\n=== still-mismatch historical items ===")
    for r in historical["mismatch_results"]:
        if not r["bcd_should_pass"]:
            print(f"  {r['canonical'][:40]!r} / {r['asr'][:40]!r}: {r['bcd_classification']}")

    if historical["broke"]:
        print("\n!!! REGRESSION: 過去PASSが壊れた実データ !!!")
        for r in historical["broke"]:
            print(f"  {json.dumps(r, ensure_ascii=False)}")

    with open(f"{OUT_DIR}/rev2_synthetic_results.json", "w", encoding="utf-8") as f:
        json.dump(synthetic, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/rev2_historical_results.json", "w", encoding="utf-8") as f:
        json.dump(historical, f, ensure_ascii=False, indent=2)

    print(f"\nsaved: {OUT_DIR}/rev2_synthetic_results.json, {OUT_DIR}/rev2_historical_results.json")


if __name__ == "__main__":
    main()
