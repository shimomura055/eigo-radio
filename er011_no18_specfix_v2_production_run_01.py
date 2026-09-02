# ============================================================
# er011_no18_specfix_v2_production_run_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01
# ============================================================
# No.18の記事・SupportをNo.18で発見された問題(Key Phraseの文脈依存人称
# 表現・意味重複、Point Twoの留保のみ構成)を修正した、変更後の汎用
# Production仕様(Point Role Planning + Point Value QA、Key Phrase人称
# 一般化 + Set Redundancy QA)で再生成する。Research/Verified Fact Ledger
# 自体は変更していない(既存No.18のresearch出力をそのまま再利用、
# er011_no18_discovery_why_full_production_run_01.pyと同一のTOPIC_JA/
# TITLE_EN/JAPANESE_TITLE_JAをそのまま使用、記事固有の書き換えは一切
# 行わない)。No.18の旧article/Support(pool_n18_notifications)は変更・
# 上書きしない(比較のため保持する)。出力先はpool_n18_notifications_
# specfix_v2。TTS/Assemblyはユーザーが再生成された文章を確認するまで
# 実行しない(このscriptにはaudioステージを含めない)。

from __future__ import annotations

import json
import time

import er005_cost_logger as cl
import er011_no18_discovery_why_full_production_run_01 as no18_orig

THEME_ID = "pool_n18_notifications_specfix_v2"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
TITLE_EN = no18_orig.TITLE_EN
TOPIC_JA = no18_orig.TOPIC_JA
JAPANESE_TITLE_JA = no18_orig.JAPANESE_TITLE_JA


def run_writer_stage_baseline() -> dict:
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"

    t0 = time.time()
    with cl.logging_context(THEME_ID, "writer"):
        result = writer_mod.run_writer_for_theme(
            client, master_full_text, THEME_ID, TOPIC_JA, ledger_path, OUT_DIR, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Writer完了(blueprint=None)。elapsed={elapsed}s")
    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return result


def run_support_stage_baseline() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_support as support_mod

    client = vfl01.get_client()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    t0 = time.time()
    with cl.logging_context(THEME_ID, "support"):
        result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Support完了(blueprint=None, comment anchor不使用)。elapsed={elapsed}s")
    return result


if __name__ == "__main__":
    import sys
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "writer":
        run_writer_stage_baseline()
    elif stage == "support":
        run_support_stage_baseline()
    else:
        print("usage: er011_no18_specfix_v2_production_run_01.py [writer|support]")
