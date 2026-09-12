# ============================================================
# er011_ja_asr_variant_trial_01_rev1_run.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 修正1回目 実行
# ============================================================
# 初回Trialの3つのアーティファクト
#   - er011_output/ja_asr_variant_trial_01/test_dataset.json (自作82件)
#   - historical_extraction_dedup.json / historical_results.json
#     (past_mismatch 7件、past_pass 72件)
# をそのまま再利用し(データを作り直さない、初回と同じ161件で評価する)、
# Candidate B+C(er011_ja_asr_variant_trial_01_rev1.
# classify_with_candidate_additive_bc)で再評価する。
#
# API支出はここでも一切発生しない(Reading Resolverはdry-run stubのまま、
# 実際のLLM呼び出しは行わない、禁止事項の遵守)。
from __future__ import annotations

import json
import sys

import er011_ja_asr_variant_trial_01 as candidate_b
import er011_ja_asr_variant_trial_01_rev1 as candidate_bc

OUT_DIR = "er011_output/ja_asr_variant_trial_01"


def classify_baseline(canonical, asr):
    result, calls = candidate_b.classify_with_baseline(canonical, asr)
    return result, calls


def classify_bc(canonical, asr):
    result, calls, tag = candidate_bc.classify_with_candidate_additive_bc(canonical, asr)
    return result, calls, tag


# ------------------------------------------------------------
# 1. 自作82件データセット(test_dataset.json、初回と同一データを再利用)
# ------------------------------------------------------------
def run_synthetic():
    with open(f"{OUT_DIR}/test_dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    results = []
    for item in dataset:
        expected_pass = (item["expected"] == "PASS")
        baseline_result, baseline_calls = classify_baseline(item["canonical"], item["asr"])
        bc_result, bc_calls, bc_tag = classify_bc(item["canonical"], item["asr"])

        baseline_pass = baseline_result.should_pass
        bc_pass = bc_result.should_pass

        results.append({
            **item,
            "baseline_classification": baseline_result.classification,
            "baseline_should_pass": baseline_pass,
            "baseline_resolver_dry_run_calls": baseline_calls,
            "bc_classification": bc_result.classification,
            "bc_should_pass": bc_pass,
            "bc_rescue_tag": bc_tag,
            "bc_resolver_dry_run_calls": bc_calls,
            "correct": bc_pass == expected_pass,
            "false_pass": (expected_pass is False) and (bc_pass is True),
            "broke_a_baseline_correct": (baseline_pass == expected_pass) and (bc_pass != expected_pass),
            "fixed_vs_baseline": (baseline_pass != expected_pass) and (bc_pass == expected_pass),
        })

    summary = {
        "n": len(results),
        "correct": sum(1 for r in results if r["correct"]),
        "false_pass": sum(1 for r in results if r["false_pass"]),
        "broke_a_baseline_correct": sum(1 for r in results if r["broke_a_baseline_correct"]),
        "fixed_vs_baseline": sum(1 for r in results if r["fixed_vs_baseline"]),
        "resolver_dry_run_calls_total": sum(r["bc_resolver_dry_run_calls"] for r in results),
    }

    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], {"n": 0, "correct": 0})
        by_category[r["category"]]["n"] += 1
        by_category[r["category"]]["correct"] += 1 if r["correct"] else 0

    return {"summary": summary, "by_category": by_category, "results": results}


# ------------------------------------------------------------
# 2. 実データ抽出(historical_results.json の past_mismatch/past_pass、
#    初回と同一データを再利用)
# ------------------------------------------------------------
def run_historical():
    with open(f"{OUT_DIR}/historical_results.json", encoding="utf-8") as f:
        hist = json.load(f)

    mismatch_results = []
    for case in hist["past_mismatch_cases"]:
        bc_result, bc_calls, bc_tag = classify_bc(case["canonical"], case["asr"])
        mismatch_results.append({
            **case,
            "bc_classification": bc_result.classification,
            "bc_should_pass": bc_result.should_pass,
            "bc_rescue_tag": bc_tag,
        })

    pass_results = []
    broke = []
    for case in hist["past_pass_cases"]:
        # 重要: historical_results.json内の既存フィールド
        # "baseline_should_pass"/"candidate_should_pass" は、確認の結果
        # "candidate_*" が実は「置換方式」(classify_with_candidate_morph)
        # で計算されていたことが判明した(本ファイルの「修正1回目」節に
        # 詳細記録)。「追加方式」(本命)の regression 判定を正しく行うため、
        # ここでは古いフィールドを信用せず、baseline/追加方式を両方その場で
        # 再計算し、fresh な値同士で比較する。
        fresh_baseline_result, _ = classify_baseline(case["canonical"], case["asr"])
        bc_result, bc_calls, bc_tag = classify_bc(case["canonical"], case["asr"])
        entry = {
            **case,
            "fresh_baseline_classification": fresh_baseline_result.classification,
            "fresh_baseline_should_pass": fresh_baseline_result.should_pass,
            "bc_classification": bc_result.classification,
            "bc_should_pass": bc_result.should_pass,
            "bc_rescue_tag": bc_tag,
        }
        pass_results.append(entry)
        # 正しい regression 定義: 「(fresh)baselineではshould_pass=Trueだったが
        # Candidate B+C適用後はshould_pass=Falseになった」場合のみ regression
        # として記録する(dry-run方式の制約上、実運用でReading Resolver[LLM]
        # が実際には解決していたはずのケースが baseline 自体で既にFalseに
        # なるのは、Candidate B/C導入前から存在する dry-run 評価方法自体の
        # 制約であり、Candidate B/C起因のregressionではないため区別する)。
        if entry["fresh_baseline_should_pass"] is True and entry["bc_should_pass"] is False:
            broke.append(entry)

    summary = {
        "past_mismatch_total": len(mismatch_results),
        "past_mismatch_bc_resolved_to_pass": sum(1 for r in mismatch_results if r["bc_should_pass"]),
        "past_mismatch_bc_still_mismatch": sum(1 for r in mismatch_results if not r["bc_should_pass"]),
        "past_pass_total": len(pass_results),
        "past_pass_fresh_baseline_pass": sum(1 for r in pass_results if r["fresh_baseline_should_pass"]),
        "past_pass_bc_still_pass": sum(1 for r in pass_results if r["bc_should_pass"]),
        # 正しい定義(fresh_baseline True -> bc False の遷移のみ)。
        "past_pass_bc_broke_true_regression": len(broke),
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

    print("\n=== incorrect synthetic items (should be small residual list) ===")
    for r in synthetic["results"]:
        if not r["correct"]:
            print(f"  [{r['category']}] {r['note']}: bc_classification={r['bc_classification']} "
                  f"bc_should_pass={r['bc_should_pass']} expected={r['expected']}")

    print("\n=== still-mismatch historical items ===")
    for r in historical["mismatch_results"]:
        if not r["bc_should_pass"]:
            print(f"  {r['canonical'][:40]!r} / {r['asr'][:40]!r}: {r['bc_classification']}")

    if historical["broke"]:
        print("\n!!! REGRESSION: 過去PASSが壊れた実データ !!!")
        for r in historical["broke"]:
            print(f"  {json.dumps(r, ensure_ascii=False)}")

    with open(f"{OUT_DIR}/rev1_synthetic_results.json", "w", encoding="utf-8") as f:
        json.dump(synthetic, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/rev1_historical_results.json", "w", encoding="utf-8") as f:
        json.dump(historical, f, ensure_ascii=False, indent=2)

    print(f"\nsaved: {OUT_DIR}/rev1_synthetic_results.json, {OUT_DIR}/rev1_historical_results.json")


if __name__ == "__main__":
    main()
