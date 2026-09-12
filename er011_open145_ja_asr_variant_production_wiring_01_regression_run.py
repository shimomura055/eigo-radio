# ============================================================
# er011_open145_ja_asr_variant_production_wiring_01_regression_run.py
# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01
# ============================================================
# 既存回帰(er007_ja_asr_validator_01_test.py / er011_no18_connected_
# speech_reading_resolver_wiring_08_test.py)のfixtureをそのまま再利用し
# (作り直さない)、配線後のProduction関数(javal.classify_ja_asr_match、
# Candidate B/C/D-1が内部配線済み)で再確認する。両ファイルとも
# `run_project_regression.py`のglobパターン(er0*_test_*.py)に一致しない
# ため(ファイル名が「_test.py」で終わり「_test_X.py」ではない、OPEN-27
# で既知)、独立に実行する必要がある。
#
# READING_RESOLVER_CORRECTLY_RESOLVES_FIXTURES(月/つき)と、er011
# wiring08の#9(後/あと)は実際のLLM呼び出しが必須なため、本タスクの
# API支出禁止(¥0)方針によりskipする(件数のみ計上、Trial時と同じ扱い)。
# call_resolverはこのテスト全体を通じて一切呼び出されない(呼ばれたら
# 即座にRuntimeErrorになるスタブへ差し替える、意図しないAPI支出の
# 混入を検知できるようにするため)。
from __future__ import annotations

import json
import os

import er007_ja_asr_validator_01_test as er007_test
import er007_ja_asr_validator_01 as javal
import er011_a2_reading_resolver_01 as reading_resolver

RESULT_DIR = "er011_output/open145_ja_asr_variant_production_wiring_01"


def _block_call_resolver(full_text_context, target_word, candidates):
    raise RuntimeError("call_resolver呼び出しを検知(本回帰テストではAPI支出禁止のためブロックする)")


def classify(canonical, asr):
    return javal.classify_ja_asr_match(canonical, asr)


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
        "必須なためAPI支出禁止の本タスクでは未実行、件数のみ計上=1件。Trial時と同じ扱い)",
    ]

    return {"groups": groups, "all_ok": all_ok, "skipped": skipped}


def run_er011_wiring08_relevant_regression():
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

    with open("er006_preprod_hardening_01_validation.py", encoding="utf-8") as f:
        en_validator_src = f.read()
    ok15 = "er011_a2_reading_resolver_01" not in en_validator_src
    results.append({"name": "15. B1(英語Validator)にはReading Resolverが一切importされない",
                     "classification": None, "should_pass": None, "ok": ok15})
    all_ok = all_ok and ok15
    ok15b = "er011_ja_asr_variant_layer_01" not in en_validator_src
    results.append({"name": "15b(追加). B1(英語Validator)にはJA ASR Variant Layerも一切importされない",
                     "classification": None, "should_pass": None, "ok": ok15b})
    all_ok = all_ok and ok15b

    skipped = [
        "9. 後->あと (実際のLLM Resolver呼び出しが必須、API支出禁止の本タスクでは未実行)",
        "1-8 (B1英語Validator、A2 JAパイプラインと無関係、Candidate B/C/D-1/D-2の対象外)",
        "11-13 (resolve_reading_diff内部のmock検証、classify_ja_asr_matchを経由しないため対象外)",
    ]

    return {"results": results, "all_ok": all_ok, "skipped": skipped}


def main():
    os.makedirs(RESULT_DIR, exist_ok=True)
    orig_call_resolver = reading_resolver.call_resolver
    reading_resolver.call_resolver = _block_call_resolver
    try:
        er007_result = run_er007_regression()
        er011_result = run_er011_wiring08_relevant_regression()
    finally:
        reading_resolver.call_resolver = orig_call_resolver

    print("=== er007 regression (Production配線後、Candidate B+C+D-1) ===")
    for group, items in er007_result["groups"].items():
        n_ok = sum(1 for i in items if i["ok"])
        print(f"  {group}: {n_ok}/{len(items)} OK")
        for i in items:
            print(f"    [{'OK' if i['ok'] else 'FAIL'}] {i['name'][:60]}: {i['classification']}")
    print(f"  skipped: {er007_result['skipped']}")
    print(f"  all_ok: {er007_result['all_ok']}")

    print("\n=== er011 wiring08 A2-relevant regression (Production配線後) ===")
    for i in er011_result["results"]:
        print(f"  [{'OK' if i['ok'] else 'FAIL'}] {i['name']}: {i['classification']}")
    print(f"  skipped: {er011_result['skipped']}")
    print(f"  all_ok: {er011_result['all_ok']}")

    out = {"er007": er007_result, "er011_wiring08_a2_relevant": er011_result}
    with open(f"{RESULT_DIR}/existing_er007_er011_offline_regression_after_wiring.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nsaved: {RESULT_DIR}/existing_er007_er011_offline_regression_after_wiring.json")

    if not (er007_result["all_ok"] and er011_result["all_ok"]):
        raise AssertionError("offline regressionにFAILが含まれる")


if __name__ == "__main__":
    main()
