# ============================================================
# er010_no9_storytelling_nojargon_wiring_06.py
# ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06
# ============================================================
# Storytelling First / No Jargonを正式Production Writer初回経路
# (er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE)へ実装した
# うえで、既存のNo.9 Verified Fact Ledger(research段階は再実行しない)を
# 使い、正式Production経路(er006_pool_pilot_01_writer.run_writer_for_theme
# → er003_v1_n3_01_articles_generate.run_one_pattern、Point Overlap QA/
# Diagnostic Full Retry/Ledger Deviation Checker v2/Fact Checker/
# Directional Fact Precheckを全て含む)からNo.9 A2/B1を再生成する。
#
# Git保全済みの2026-08-29版(er006_output/pool_pilot_01/pool_n9_tip_screens/
# {a2,b1b}/article.md)は一切上書きしない。出力は新規ディレクトリへ書く。

from __future__ import annotations

import json

import er005_cost_logger as cl
import er009_n1_production_integration_01 as n9

OUT_DIR = "er010_output/no9_storytelling_nojargon_wiring_06"


def run():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{n9.OUT_DIR}/research/verified_fact_ledger.txt"

    result = writer_mod.run_writer_for_theme(
        client, master_full_text, n9.THEME_ID, n9.TOPIC_JA, ledger_path, OUT_DIR, blueprint=None)

    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return result


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run()
