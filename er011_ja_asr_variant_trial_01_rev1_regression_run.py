# ============================================================
# er011_ja_asr_variant_trial_01_rev1_regression_run.py
# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01 修正1回目
# 既存回帰(er007/er011 wiring08)の再確認。
# ============================================================
# 既存test fixtureファイル(er007_ja_asr_validator_01_test.py /
# er011_no18_connected_speech_reading_resolver_wiring_08_test.py)を
# importし、そのfixtureデータをそのまま再利用する(fixtureを作り直さない)。
# classify関数だけをCandidate B+C(追加方式)へ差し替えて同じ期待値を
# 確認する。実際のLLM呼び出しが必須な項目(er007の
# READING_RESOLVER_CORRECTLY_RESOLVES_FIXTURES、er011 wiring08の項目9)は
# 本Trialの禁止事項(API支出禁止)のためskipし、件数のみ計上する
# (初回Trialと同じ扱い)。
from __future__ import annotations

import json

import er007_ja_asr_validator_01_test as er007_test
import er011_ja_asr_variant_trial_01_rev1 as candidate_bc


def classify(canonical, asr):
    result, calls, tag = candidate_bc.classify_with_candidate_additive_bc(canonical, asr)
    return result


def run_er007_regression():
    groups = {}
    all_ok = True

    def check_group(name, fixtures, check_fn):
        nonlocal all_ok
        items = []
        for fx in fixtures:
            r = classify(fx["canonical"], fx["asr"])
            ok = check_fn(r)
            items.append({"name": fx["name"], "classification": r.classification,
                          "should_pass": r.should_pass, "ok": ok})
            if not ok:
                all_ok = False
        groups[name] = items

    check_group("POSITIVE", er007_test.POSITIVE_FIXTURES,
                lambda r: r.should_pass is True)
    check_group("NEGATIVE", er007_test.NEGATIVE_FIXTURES,
                lambda r: r.should_pass is False)
    check_group("ENTITY_LIKE", er007_test.ENTITY_LIKE_FIXTURES,
                lambda r: r.should_pass is False)
    check_group("PHONETIC_UNCERTAIN", er007_test.PHONETIC_UNCERTAIN_FIXTURES,
                lambda r: r.classification != "TRUE_CONTENT_MISMATCH")
    check_group("WHOLE_TEXT_SCRIPT_MISMATCH", er007_test.WHOLE_TEXT_SCRIPT_MISMATCH_FIXTURES,
                lambda r: r.classification != "TRUE_CONTENT_MISMATCH")
    check_group("WHOLE_TEXT_SCRIPT_MISMATCH_NEGATIVE", er007_test.WHOLE_TEXT_SCRIPT_MISMATCH_NEGATIVE_FIXTURES,
                lambda r: r.classification == "TRUE_CONTENT_MISMATCH" and r.should_pass is False)
    check_group("KNOWN_TRADEOFF", er007_test.KNOWN_TRADEOFF_FIXTURES,
                lambda r: r.should_pass is False)
    check_group("NOT_PHONETIC_UNCERTAIN", er007_test.NOT_PHONETIC_UNCERTAIN_FIXTURES,
                lambda r: r.classification == "TRUE_CONTENT_MISMATCH")

    skipped = [
        "READING_RESOLVER_CORRECTLY_RESOLVES_FIXTURES (月/つき、実際のLLM呼び出しが"
        "必須なためAPI支出禁止の本Trialでは未実行、件数のみ計上=1件)",
    ]

    return {"groups": groups, "all_ok": all_ok, "skipped": skipped}


def run_er011_wiring08_relevant_regression():
    # er011_no18_..._wiring08_test.pyのA2(日本語)関連項目のうち、実際の
    # LLM呼び出しが必須な項目9を除く、10・14をCandidate B+Cで再確認する
    # (1-8はB1英語Validatorのみでer007/er011 A2パイプラインと無関係、
    # 11-13はresolve_reading_diff内部のmock検証でclassify関数を経由しない
    # ため対象外、15はimportチェックでコード変更なし=対象外、いずれも
    # Candidate B+Cの影響を受けない箇所であるため、実質的にA2の分類結果へ
    # 影響し得る9・10・14のみを対象とする)。
    results = []
    all_ok = True

    r10 = classify("今日は天気がいいですね。", "今日は天気がいいですね。")
    ok10 = (r10.classification == "EXACT_MATCH")
    results.append({"name": "10. 完全一致segment -> EXACT_MATCH", "classification": r10.classification,
                     "should_pass": r10.should_pass, "ok": ok10})
    all_ok = all_ok and ok10

    r14 = classify("今日は増加傾向にあります。", "今日は減少傾向にあります。")
    ok14 = (r14.classification == "TRUE_CONTENT_MISMATCH" and r14.should_pass is False)
    results.append({"name": "14. 読み問題でない真の内容誤り(増加/減少) -> TRUE_CONTENT_MISMATCH",
                     "classification": r14.classification, "should_pass": r14.should_pass, "ok": ok14})
    all_ok = all_ok and ok14

    skipped = [
        "9. 後->あと (実際のLLM Resolver呼び出しが必須、API支出禁止の本Trialでは未実行)",
        "1-8 (B1英語Validator、A2 JAパイプラインと無関係、Candidate B/Cの対象外)",
        "11-13 (resolve_reading_diff内部のmock検証、classify_ja_asr_matchを経由しないためCandidate B/Cの対象外)",
        "15 (importチェック、コード変更なし対象外)",
    ]

    return {"results": results, "all_ok": all_ok, "skipped": skipped}


def main():
    er007_result = run_er007_regression()
    er011_result = run_er011_wiring08_relevant_regression()

    print("=== er007 regression (Candidate B+C) ===")
    for group, items in er007_result["groups"].items():
        n_ok = sum(1 for i in items if i["ok"])
        print(f"  {group}: {n_ok}/{len(items)} OK")
        for i in items:
            if not i["ok"]:
                print(f"    FAIL: {i}")
    print(f"  skipped: {er007_result['skipped']}")
    print(f"  all_ok: {er007_result['all_ok']}")

    print("\n=== er011 wiring08 A2-relevant regression (Candidate B+C) ===")
    for i in er011_result["results"]:
        print(f"  [{'OK' if i['ok'] else 'FAIL'}] {i['name']}: {i['classification']}")
    print(f"  skipped: {er011_result['skipped']}")
    print(f"  all_ok: {er011_result['all_ok']}")

    out = {"er007": er007_result, "er011_wiring08_a2_relevant": er011_result}
    with open("er011_output/ja_asr_variant_trial_01/rev1_regression_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nsaved: er011_output/ja_asr_variant_trial_01/rev1_regression_result.json")


if __name__ == "__main__":
    main()
