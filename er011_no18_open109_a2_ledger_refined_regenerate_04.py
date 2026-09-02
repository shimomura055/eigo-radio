# ============================================================
# er011_no18_open109_a2_ledger_refined_regenerate_04.py
# ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04
# ============================================================
# OPEN-109: pool_n18_notifications_specfix_v2のA2記事は、OPEN-108(前session)
# でVerified Fact Ledger(er006_output/.../research/verified_fact_ledger.txt、
# A2/B1共有の単一ファイル)がsource-groundedに精密化された後も、一度も
# 再生成されておらず、旧Ledger由来の不正確な記述("hard-to-resist habit"
# =削除済みF-011、Pew"約4割"丸め=旧F-009)をそのまま残していた。
#
# 本scriptは、er011_no18_open108_b1_ledger_refined_regenerate_01.pyがB1Bに
# 対して行ったのと全く同じ手法(既存Production正式Writer path=
# gen.run_one_pattern、Fact Checker含め一切コード変更なし)で、A2を同じ
# 精密化済みLedgerから1回だけ再生成する。LedgerファイルはA2/B1共有であり、
# 今回新たな編集は行わない(前回既に精密化済み)。

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

cl.install(f"{OUT_DIR}/raw_usage_log_open109_a2_writer.jsonl")

client = vfl01.get_client()
master_full_text = __import__("er003_v1_en_direct_ab_01_generate").load_master_full_text()
ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
verified_ledger_text = open(ledger_path, encoding="utf-8").read()

common_block = gen.build_common_block(master_full_text, driver.TOPIC_JA, verified_ledger_text)
prompt = gen.build_prompt(common_block, gen.A2_KAI1_INSTRUCTION)

with cl.logging_context(THEME_ID, "writer_a2_open109_ledger_refined"):
    result = gen.run_one_pattern(client, THEME_ID, "A2", prompt, verified_ledger_text,
                                  driver.TOPIC_JA, f"{OUT_DIR}/a2")

print(f"[{THEME_ID}] OPEN-109 Ledger精密化後A2再生成完了。status={result.get('status')} "
      f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')}")
