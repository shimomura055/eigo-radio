# ============================================================
# er011_no18_specfix_v2_b1_retry_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01
# ============================================================
# pool_n18_notifications_specfix_v2のB1B初回候補がFact Checker verdict=
# FAIL(Pewの「4割」精度・Skowronek研究の実施環境の記述、いずれも既存
# Fact Checkerが正しく検出した、今回の仕様変更とは無関係な問題)となり
# blockingでNG_REVIEW_REQUIREDになったため、既存Production経路
# (gen.run_one_pattern、Fact Checkerは無変更)をそのまま使い、B1Bだけを
# 再実行する(A2は既にPASS済みのため再実行しない、無駄なコストを避ける)。
# 記事固有のハードコード修正ではなく、通常のWriter再試行。

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

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

client = vfl01.get_client()
master_full_text = __import__("er003_v1_en_direct_ab_01_generate").load_master_full_text()
ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
verified_ledger_text = open(ledger_path, encoding="utf-8").read()

common_block = gen.build_common_block(master_full_text, driver.TOPIC_JA, verified_ledger_text)
prompt = gen.build_prompt(common_block, gen.B1_B_DIRECT_INSTRUCTION)

with cl.logging_context(THEME_ID, "writer_b1_retry"):
    result = gen.run_one_pattern(client, THEME_ID, "B1B", prompt, verified_ledger_text,
                                  driver.TOPIC_JA, f"{OUT_DIR}/b1b")

print(f"[{THEME_ID}] B1B retry完了。status={result.get('status')} "
      f"fact_verdict={result.get('fact_verdict')}")
