# ============================================================
# er011_no18_open108_b1_ledger_refined_regenerate_01.py
# ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02 / Track A
# ============================================================
# OPEN-108: pool_n18_notifications_specfix_v2のB1BがFact Checker verdict=FAIL
# (2回連続、Pew統計の丸め・"hard-to-resist habit"の非サポート・Skowronek研究への
# 予期的解釈の混入)となっていたため、まずVerified Fact Ledger
# (er006_output/.../research/verified_fact_ledger.txt)自体をsource-groundedに
# 精密化した(F-009分割・F-011削除・F-002/F-003/F-005/F-006/F-007へのwriter_guidance
# 追加。詳細はLedgerファイル冒頭の注記3を参照)。
#
# 本scriptは、精密化後のLedgerを使い、既存Production正式Writer path
# (gen.run_one_pattern、Fact Checker含め一切コード変更なし)からB1Bを1回だけ
# 再生成する。Fact Checker verdict=FAILに対する自動Writer再生成retryは現行仕様に
# 存在しない(er002_ja_web_research_r3.run_fact_checker_with_gatesのretryは技術的
# failure専用で、MAX_FACT_CHECK_ATTEMPTS=2は「初回+web検索未使用/JSON不正のときの
# 技術再試行1回」のみを意味し、verdict=FAILは即blocking)。したがって本scriptの
# 1回の実行こそが、Ledger精密化後の正式なB1B生成であり、これがFAILした場合は
# 仕様上さらなる自動retryを行わず、そのままUSER_DECISION_REQUIREDとして報告する
# (retry上限を勝手に増やさない)。

from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er011_no18_specfix_v2_production_run_01 as driver

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR

cl.install(f"{OUT_DIR}/raw_usage_log_open108.jsonl")

client = vfl01.get_client()
master_full_text = __import__("er003_v1_en_direct_ab_01_generate").load_master_full_text()
ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
verified_ledger_text = open(ledger_path, encoding="utf-8").read()

common_block = gen.build_common_block(master_full_text, driver.TOPIC_JA, verified_ledger_text)
prompt = gen.build_prompt(common_block, gen.B1_B_DIRECT_INSTRUCTION)

with cl.logging_context(THEME_ID, "writer_b1_open108_ledger_refined"):
    result = gen.run_one_pattern(client, THEME_ID, "B1B", prompt, verified_ledger_text,
                                  driver.TOPIC_JA, f"{OUT_DIR}/b1b")

print(f"[{THEME_ID}] OPEN-108 Ledger精密化後B1B再生成完了。status={result.get('status')} "
      f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')}")
