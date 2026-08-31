#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11

Formatting禁止仕様(emoji・unnecessary bold削除)をProduction正式pathへ反映後、
No.9 A2/B1を新仕様で再生成する。

実行:
  .venv/Scripts/python.exe er010_no9_formatting_production_and_fact_review_11.py
"""

import json
import er005_cost_logger as cl
import er009_n1_production_integration_01 as n9

OUT_DIR = "er010_output/no9_formatting_production_and_fact_review_11"


def run():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{n9.OUT_DIR}/research/verified_fact_ledger.txt"

    print("="*70)
    print("ER-010-NO9-FORMAT-PRODUCTION-AND-FACT-REVIEW-11")
    print("Formatting Production: No.9 A2/B1再生成(emoji・bold禁止仕様適用)")
    print("="*70)

    result = writer_mod.run_writer_for_theme(
        client, master_full_text, n9.THEME_ID, n9.TOPIC_JA, ledger_path, OUT_DIR, blueprint=None)

    with open(f"{OUT_DIR}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in result["results"].items()},
                   f, ensure_ascii=False, indent=2, default=str)

    print("\n" + "="*70)
    for label, r in result["results"].items():
        print(f"{label}:")
        print(f"  status={r.get('status')} fact_verdict={r.get('fact_verdict')}")
        print(f"  ledger_status={r.get('ledger_status')} deviations={r.get('ledger_deviation_count')}")
        print(f"  local_rewrite_items={len(r.get('local_rewrite_results') or [])}")

    print("="*70)
    print("Complete.")
    return result


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run()
