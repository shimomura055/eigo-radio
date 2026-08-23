# -*- coding: utf-8 -*-
# ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01 Part A:
# 較正後プロンプトでのNo.1-6再backtest。No.1-3は本セッションで初めて
# backtest対象にする(expected指定なし、実際の判定結果をそのまま報告する)。
import sys, time, json
sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/coverage_gate_01/gate_usage_log_calibrated.jsonl")

import er006_research_coverage_gate_01 as gate

CASES = [
    ("pool_n1_benches_backtest", "Why Are More Cities Rethinking Public Benches?",
     "er006_output/pool_pilot_01/pool_benches/research/verified_fact_ledger.txt", None),
    ("pool_n2_subscriptions_backtest", "Why Do Companies Make Subscriptions So Easy to Start—and Hard to Stop?",
     "er006_output/pool_pilot_01/pool_subscriptions/research/verified_fact_ledger.txt", None),
    ("pool_n3_startups_backtest", "Why Do Some Startups Chase Growth Before Profit?",
     "er006_output/pool_pilot_01/pool_startups/research/verified_fact_ledger.txt", None),
    ("pool_n4_supermarket_round1_backtest", "The Supermarket Shuffle: Why Shelves Keep Moving",
     "er006_output/pool_pilot_01/coverage_gate_01/n4_round1_reconstruction/verified_fact_ledger_round1.txt",
     "MORE_RESEARCH_REQUIRED"),
    ("pool_n5_cafes_backtest", "Cafes Are Rethinking the All-Day Customer",
     "er006_output/pool_pilot_01/pool_n5_cafes/research/verified_fact_ledger.txt",
     "COVERAGE_PASS"),
    ("pool_n6_delivery_backtest", "The Strange Pull of Delivery Tracking",
     "er006_output/pool_pilot_01/pool_n6_delivery/research/verified_fact_ledger.txt",
     "COVERAGE_PASS"),
]

results = {}
for theme_id, title, ledger_path, expected in CASES:
    ledger_text = open(ledger_path, encoding="utf-8").read()
    t0 = time.time()
    with cl.logging_context(theme_id, "research_coverage_gate_calibrated"):
        r = gate.run_coverage_gate(title, ledger_text)
    elapsed = round(time.time() - t0, 2)
    verdict = r["parsed"]["verdict"]
    if expected is None:
        match = "N/A(No.1-3はexpected指定なし)"
    else:
        match = "MATCH" if verdict == expected else "MISMATCH"
    print(f"[{theme_id}] verdict={verdict} expected={expected} [{match}] elapsed={elapsed}s "
          f"in_tok={r['input_tokens']} out_tok={r['output_tokens']}")
    results[theme_id] = {**r, "elapsed_seconds": elapsed, "expected": expected, "match": match}
    with open(f"er006_output/pool_pilot_01/coverage_gate_01/{theme_id}_calibrated_result.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in results[theme_id].items()}, f, ensure_ascii=False, indent=2, default=str)

print("\nBACKTEST_DONE")
