# -*- coding: utf-8 -*-
# ============================================================
# er012_open138_household_fact0304_consistency_fix_03.py
# ============================================================
# HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03(OPEN-138継続)。
# Household Verified Fact Ledger v5(FACT-03修正: バナナ・トマトを低湿度
# ドロワー適合例から除外)とFACT-04(バナナ・トマトは冷蔵不要・常温推奨)
# の間の内部矛盾が解消されたことを、既存Research正式経路のFact Checker
# 関数(er002_ja_web_research_r3.py、web_searchツール付き、Production同一
# 関数)をそのまま1回呼び出して確認する薄いスクリプト。記事の再生成・
# Ledger以外の変更は一切行わない。検証対象はFACT-03(v5)・FACT-04の2
# claimのみ(記事全体ではない)。
from __future__ import annotations

import json
import time

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

OUT_DIR = "er012_output/open138_household_fact0304_consistency_fix_03/run2_literal_ledger_wording"

TOPIC = (
    "Household refrigerator crisper drawer storage: whether ethylene-heavy "
    "produce should be kept in the low-humidity crisper drawer, and whether "
    "this is consistent with separate guidance that tomatoes and bananas "
    "should not be refrigerated at all and are better kept at room "
    "temperature (e.g. on a counter)."
)

# Household Verified Fact Ledger v5のFACT-03(usable部分、ANCHOR)とFACT-04
# を、それぞれの主張のまま2文にまとめた抜粋(新しい事実主張を加えず、
# Ledger本文の言い換えのみ)。
ARTICLE_EXCERPT = """Foods that release a lot of ethylene, such as apples and pears, are well suited to the refrigerator's low-humidity crisper drawer.

Tomatoes and bananas are not well suited to refrigerated storage. Room-temperature storage, such as on a counter, is recommended instead."""


def main():
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")  # 冒頭で必ず有効化(実測usageログ)

    fc_prompt = r3.build_fact_check_prompt(TOPIC, ARTICLE_EXCERPT, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    with cl.logging_context("household_fact0304_consistency_fix_03", "fact_checker"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)

    verdict = fc_result.get("verdict") if fc_result else None
    print(f"fact_check status={fc_status} verdict={verdict}")
    if fc_result:
        print("contradictions:", json.dumps(fc_result.get("contradictions"), ensure_ascii=False, indent=2))
        print("unsupported_specific_claims:",
              json.dumps(fc_result.get("unsupported_specific_claims"), ensure_ascii=False, indent=2))
        print("notes:", fc_result.get("notes"))

    fact_qa_record = {
        "management_id": "HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03(OPEN-138継続)",
        "target": "er003_output/n3_01/household/research/verified_fact_ledger.txt "
                  "FACT-03(v5)とFACT-04の内部整合確認(2 claimのみ、記事全体ではない)",
        "topic": TOPIC,
        "article_excerpt": ARTICLE_EXCERPT,
        "final_status": fc_status,
        "model": fc_model,
        "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": fc_attempts,
        "result": fc_result,
    }
    with open(f"{OUT_DIR}/fact_check_result.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2, default=str)
    print(f"[OK] saved -> {OUT_DIR}/fact_check_result.json")


if __name__ == "__main__":
    main()
