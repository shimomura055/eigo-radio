# ============================================================
# er010_no9_production_integration_final_09.py
# ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09
# ============================================================
# ユーザーが正式採用したLocal Rewrite / Hook-aware Deviation Checker /
# Evidence-bounded Interpretationを本体へ配線した後、正式Production初回
# 経路(er006_pool_pilot_01_writer.run_writer_for_theme →
# er003_v1_n3_01_articles_generate.run_one_pattern、Point Overlap QA/
# Diagnostic Full Retry/Fact Checker/Ledger Deviation Checker(Hook-aware)/
# Local Rewrite/Directional Fact Precheckを全て含む)からNo.9 A2/B1を
# 実生成し、runtime evidenceを取得する。
#
# 既存のNo.9 Verified Fact Ledger(research段階は再実行しない、ER-010-06
# と同一のledger)を使う。Git保全済みの過去出力(er006_output/pool_pilot_01/
# pool_n9_tip_screens/、er010_output/no9_storytelling_nojargon_wiring_06/)
# は一切上書きしない。DEV/Trigger runner用runnerを模擬せず、正式Production
# 初回経路(gen.run_one_pattern)をそのまま使う。

from __future__ import annotations

import json

import er005_cost_logger as cl
import er009_n1_production_integration_01 as n9

OUT_DIR = "er010_output/no9_production_integration_final_09"


def run():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{n9.OUT_DIR}/research/verified_fact_ledger.txt"

    result = writer_mod.run_writer_for_theme(
        client, master_full_text, n9.THEME_ID, n9.TOPIC_JA, ledger_path, OUT_DIR, blueprint=None)

    with open(f"{OUT_DIR}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in result["results"].items()},
                   f, ensure_ascii=False, indent=2, default=str)

    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')} ledger_deviation_count={r.get('ledger_deviation_count')} "
              f"local_rewrite_items={len(r.get('local_rewrite_results') or [])}")
    return result


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run()
