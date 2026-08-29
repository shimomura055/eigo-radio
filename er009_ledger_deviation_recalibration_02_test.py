# -*- coding: utf-8 -*-
# ============================================================
# er009_ledger_deviation_recalibration_02_test.py
# ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02 / 6. False negative検証
# ============================================================
# 新しいLedger Deviation Checker候補(er009_ledger_deviation_
# recalibration_02.py)が、過剰検知を減らした副作用として本当に危険な
# Fact deviationまで見逃す(false negative)ようになっていないかを、
# 意図的に不正な記述へ書き換えたfixtureで検証する。
#
# 各fixtureは、No.9で実際に確認されたVerified Fact Ledgerを基準に、
# 1箇所だけ意図的にFactを壊した短い記事断片。新Checkerがそれぞれを
# 正しくMAJOR(かつ対応するchanged_*フラグ=true)と判定することを確認する。
from __future__ import annotations

import json

import er009_ledger_deviation_recalibration_02 as v2

OUT_DIR = "er006_output/pool_pilot_01/pool_n9_tip_screens"
LEDGER_TEXT = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

# Ledgerの実際の記述(F-002等)を基準に、1箇所だけ壊した意図的に危険なfixture。
FIXTURES = {
    "changed_number": (
        "Researchers studied more than 30 million credit card payments in New York City taxis, "
        "and found that higher suggested tip rates led passengers to leave more money."
    ),
    "changed_actor": (
        "A team at Harvard Business School studied more than 13 million credit card payments in "
        "New York City taxis, and found that higher suggested tip rates led passengers to leave more money."
    ),
    "changed_scope": (
        "The taxi study's results have now been directly confirmed in restaurants nationwide: "
        "higher suggested tip rates on restaurant screens cause customers to leave more money, "
        "just as they did in the New York City taxi data."
    ),
    "changed_causality": (
        "The rise in US restaurant tipping from about 10-15 percent in the early 1970s to about "
        "20 percent by the late 1990s was directly caused by the introduction of digital tip screens."
    ),
    "changed_certainty": (
        "It is now proven beyond doubt that suggested tip screens cause guilt tipping in every "
        "customer who sees one."
    ),
    "changed_negation": (
        "The taxi study found that passengers who saw higher suggested tip rates did NOT leave "
        "more money; the suggested rate had no effect on the final tip."
    ),
    "changed_comparison": (
        "Passengers who saw LOWER suggested tip rates left more money than those who saw higher "
        "suggested rates, according to the New York City taxi study."
    ),
    "changed_time": (
        "In 2019, researchers published a study in the American Economic Journal: Applied "
        "Economics showing that higher suggested tip rates led New York City taxi passengers "
        "to leave more money."
    ),
    "unsupported_new_claim": (
        "The same New York City taxi researchers also found that male passengers tipped twice "
        "as much as female passengers when shown a higher suggested rate."
    ),
}


def run_all() -> dict:
    client = v2.vfl01.get_client()
    results = {}
    for name, article_text in FIXTURES.items():
        print(f"[fixture:{name}] チェック実行開始...")
        result = v2.run_deviation_check_v2(client, LEDGER_TEXT, article_text)
        parsed = result["parsed"]
        major_devs = [d for d in parsed["deviations"] if d["severity"] == "MAJOR"]
        caught = len(major_devs) > 0
        expected_flag_true = any(d.get(name) for d in major_devs) if caught else False
        results[name] = {
            "caught_as_major": caught,
            "expected_flag_true": expected_flag_true,
            "overall_status": parsed["overall_status"],
            "deviations": parsed["deviations"],
        }
        print(f"[fixture:{name}] caught_as_major={caught} expected_flag_true={expected_flag_true}")
    return results


if __name__ == "__main__":
    out = run_all()
    with open(f"{OUT_DIR}/false_negative_fixture_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    n_pass = sum(1 for v in out.values() if v["caught_as_major"])
    print(f"\n合計: {n_pass}/{len(out)} fixtureがMAJORとして検知された")
    for name, v in out.items():
        status = "PASS" if v["caught_as_major"] else "FAIL(見逃し)"
        print(f"  {name}: {status}")
