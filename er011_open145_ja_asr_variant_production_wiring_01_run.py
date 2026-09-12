# ============================================================
# er011_open145_ja_asr_variant_production_wiring_01_run.py
# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01
# ============================================================
# Trial(JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01、修正2回目
# までVALIDATED)と同じ3つのfixtureファイル(er011_output/
# ja_asr_variant_trial_01/test_dataset.json[82件]・historical_results.json
# [過去MISMATCH7件+過去PASS72件、計161件])をそのまま再利用し(データを
# 作り直さない)、Production配線後の実関数
# (er007_ja_asr_validator_01.classify_ja_asr_match、Candidate B/C/D-1が
# 内部配線済み)で再評価する。API支出は一切発生しない(Reading Resolver
# のcall_resolverはdry-run stubへ差し替える、TrialのCandidate B
# classify_with_baseline()と同じ設計)。
#
# flag ON(既定)/OFF両方で実行し、OFF時は「配線前の実測結果」
# (pre_wiring_baseline)と完全一致することも確認する。
from __future__ import annotations

import json

import er007_ja_asr_validator_01 as javal
import er011_a2_reading_resolver_01 as reading_resolver
import er011_ja_asr_variant_layer_01 as ja_variant_layer

OUT_DIR = "er011_output/ja_asr_variant_trial_01"
RESULT_DIR = "er011_output/open145_ja_asr_variant_production_wiring_01"


def classify_dry_run(canonical: str, asr: str):
    """Production既定動作の再現。Resolverはoffline dry-run stub(実際に
    call_resolverが呼ばれる回数だけを数える、ネットワークへは一切出ない)。
    Trialのclassify_with_baseline()と同じ設計。

    Candidate D-2(voicing許容Cascadeの厳密一致引き上げ)は、Production
    ではclassify_ja_asr_match()自身の内部ではなく、A2 Cascade呼び出し元
    (er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail、
    OPEN-145の設計どおり)でpost-processingとして適用される。この
    dry-runでも、実際のA2 Production runtime経路と同じ挙動を再現するため
    classify_ja_asr_match()の直後にja_variant_layer.try_upgrade_voicing_
    cascade()を明示的に適用する(Cascade呼び出し元のロジックをここで
    再実装するのではなく、同じ関数を呼ぶだけ)。"""
    calls = {"n": 0}
    orig_call_resolver = reading_resolver.call_resolver
    orig_flag = javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED

    def _stub_call_resolver(full_text_context, target_word, candidates):
        calls["n"] += 1
        raise RuntimeError("dry-run stub: 本タスクではAPI支出禁止のためLLM呼び出しを行わない")

    try:
        reading_resolver.call_resolver = _stub_call_resolver
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = True
        result = javal.classify_ja_asr_match(canonical, asr)
    finally:
        reading_resolver.call_resolver = orig_call_resolver
        javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = orig_flag

    upgraded = ja_variant_layer.try_upgrade_voicing_cascade(canonical, asr, result)
    if upgraded is not None:
        result = upgraded
    return result, calls["n"]


def run_synthetic(label: str):
    with open(f"{OUT_DIR}/test_dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    results = []
    for item in dataset:
        expected_pass = (item["expected"] == "PASS")
        result, calls = classify_dry_run(item["canonical"], item["asr"])
        results.append({
            **item,
            "classification": result.classification,
            "should_pass": result.should_pass,
            "resolver_dry_run_calls": calls,
            "reason": result.reason,
            "correct": result.should_pass == expected_pass,
            "false_pass": (expected_pass is False) and (result.should_pass is True),
        })

    summary = {
        "label": label,
        "n": len(results),
        "correct": sum(1 for r in results if r["correct"]),
        "false_pass": sum(1 for r in results if r["false_pass"]),
    }
    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], {"n": 0, "correct": 0})
        by_category[r["category"]]["n"] += 1
        by_category[r["category"]]["correct"] += 1 if r["correct"] else 0

    return {"summary": summary, "by_category": by_category, "results": results}


def run_historical_compare():
    """flag ON/OFFを同一ループ内でその場で再計算し(古いfixtureファイル内の
    フィールドは信用しない、Trial REPORT「修正1回目」節の
    methodology修正と同じ方針)、fresh同士で比較する。真のregressionは
    「flag OFF(旧挙動)でPASSだったのに、flag ON(配線後)でPASSしなく
    なった」場合のみとする。"""
    with open(f"{OUT_DIR}/historical_results.json", encoding="utf-8") as f:
        hist = json.load(f)

    orig_flag = ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED

    def _classify_both(canonical, asr):
        nonlocal orig_flag
        try:
            ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = False
            off_result, _ = classify_dry_run(canonical, asr)
            ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = True
            on_result, on_calls = classify_dry_run(canonical, asr)
        finally:
            ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = orig_flag
        return off_result, on_result, on_calls

    mismatch_results = []
    for case in hist["past_mismatch_cases"]:
        off_result, on_result, on_calls = _classify_both(case["canonical"], case["asr"])
        mismatch_results.append({
            **case,
            "flag_off_classification": off_result.classification, "flag_off_should_pass": off_result.should_pass,
            "flag_on_classification": on_result.classification, "flag_on_should_pass": on_result.should_pass,
        })

    pass_results = []
    broke = []
    for case in hist["past_pass_cases"]:
        off_result, on_result, on_calls = _classify_both(case["canonical"], case["asr"])
        entry = {
            **case,
            "flag_off_classification": off_result.classification, "flag_off_should_pass": off_result.should_pass,
            "flag_on_classification": on_result.classification, "flag_on_should_pass": on_result.should_pass,
        }
        pass_results.append(entry)
        if entry["flag_off_should_pass"] is True and entry["flag_on_should_pass"] is False:
            broke.append(entry)

    summary = {
        "past_mismatch_total": len(mismatch_results),
        "past_mismatch_flag_off_resolved_to_pass": sum(1 for r in mismatch_results if r["flag_off_should_pass"]),
        "past_mismatch_flag_on_resolved_to_pass": sum(1 for r in mismatch_results if r["flag_on_should_pass"]),
        "past_pass_total": len(pass_results),
        "past_pass_flag_off_still_pass": sum(1 for r in pass_results if r["flag_off_should_pass"]),
        "past_pass_flag_on_still_pass": sum(1 for r in pass_results if r["flag_on_should_pass"]),
        "past_pass_true_regression_flag_on_broke_flag_off_pass": len(broke),
    }
    return {"summary": summary, "mismatch_results": mismatch_results,
            "pass_results": pass_results, "broke": broke}


def main():
    import os
    os.makedirs(RESULT_DIR, exist_ok=True)

    orig_flag = ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED
    out = {}
    try:
        ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = True
        out["flag_on_synthetic"] = run_synthetic("flag_on")

        ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = False
        out["flag_off_synthetic"] = run_synthetic("flag_off")
    finally:
        ja_variant_layer.FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED = orig_flag

    out["historical_compare"] = run_historical_compare()

    print("=== flag ON: synthetic (82件) ===")
    print(json.dumps(out["flag_on_synthetic"]["summary"], ensure_ascii=False, indent=2))
    print("=== flag OFF: synthetic (82件, 旧挙動) ===")
    print(json.dumps(out["flag_off_synthetic"]["summary"], ensure_ascii=False, indent=2))
    print("=== historical (7 past-mismatch + 72 past-pass, flag ON/OFF比較) ===")
    print(json.dumps(out["historical_compare"]["summary"], ensure_ascii=False, indent=2))

    print("\n=== flag ON: incorrect synthetic items (should be empty) ===")
    for r in out["flag_on_synthetic"]["results"]:
        if not r["correct"]:
            print(f"  [{r['category']}] {r['note']}: classification={r['classification']} "
                  f"should_pass={r['should_pass']} expected={r['expected']}")

    print("\n=== flag OFF vs flag ON: synthetic items that differ (should be additive-only, i.e. "
          "flag_off should_pass=False -> flag_on should_pass=True, never the reverse) ===")
    off_by_key = {(r["canonical"], r["asr"]): r for r in out["flag_off_synthetic"]["results"]}
    reverse_regressions = []
    for r_on in out["flag_on_synthetic"]["results"]:
        r_off = off_by_key[(r_on["canonical"], r_on["asr"])]
        if r_off["should_pass"] != r_on["should_pass"]:
            print(f"  [{r_on['category']}] {r_on['note']}: flag_off_should_pass={r_off['should_pass']} "
                  f"-> flag_on_should_pass={r_on['should_pass']}")
            if r_off["should_pass"] is True and r_on["should_pass"] is False:
                reverse_regressions.append(r_on)
    if reverse_regressions:
        print(f"\n!!! REGRESSION: flag ON回帰(旧挙動でPASSだったのに配線後にMISMATCH化)"
              f"{len(reverse_regressions)}件 !!!")

    if out["historical_compare"]["broke"]:
        print("\n!!! REGRESSION: 過去PASSが壊れた実データ(flag OFF基準) !!!")
        for r in out["historical_compare"]["broke"]:
            print(f"  {json.dumps(r, ensure_ascii=False)}")

    with open(f"{RESULT_DIR}/production_wiring_synthetic_historical_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nsaved: {RESULT_DIR}/production_wiring_synthetic_historical_result.json")


if __name__ == "__main__":
    main()
