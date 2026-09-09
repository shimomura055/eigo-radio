# -*- coding: utf-8 -*-
# ============================================================
# er012_open138_household_fact03_reverify_01.py
# ============================================================
# HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01(OPEN-138、ユーザーD2-UDR-2
# 承認、2026-09-09)。Household Verified Fact Ledger FACT-03(柑橘類の
# 高湿度保存に関する記述)を、Discovery Trial-07で独立Fact Checkerが
# 別情報源と矛盾すると判定(12本中2本FAIL)したことを受け、既存Research
# 正式経路のFact Checker関数(er002_ja_web_research_r3.py、web_search
# ツール付き)をそのままProduction関数として1回呼び出し、再検証する
# 薄いスクリプト。記事全体の再生成・Ledger以外の変更は一切行わない。
#
# 検証対象は、Householdの完成B1記事(2026-08-17承認、
# er003_output/n3_01/household/b1b/article.md)に実際に使われている
# FACT-03由来の段落そのもの(公開済み文言、改変なし)。
from __future__ import annotations

import json
import time

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

OUT_DIR = "er012_output/open138_household_fact03_reverify_01"

TOPIC = (
    "Household refrigerator crisper drawer humidity settings: which foods "
    "(especially strawberries and citrus fruits such as oranges) belong in "
    "the high-humidity drawer vs. the low-humidity drawer, and whether "
    "manufacturer/home-storage guidance matches postharvest-research optimal "
    "relative humidity figures."
)

# 公開済みHousehold B1記事(er003_output/n3_01/household/b1b/article.md)の
# 該当段落そのもの(一字一句改変なし)。FACT-03の「イチゴ・柑橘類は高湿度
# を好む(UC Davis 90-95%)」という記述を含む。
ARTICLE_EXCERPT = """Many crisper drawers offer low-humidity and high-humidity settings. Some refrigerators have two separate drawers. Others let users change the setting with a slider.

Low-humidity drawers allow more air to move through. This matters because fruits release ethylene as they ripen. If nearby produce stays exposed to the gas, it may ripen too quickly and spoil.

Foods that release a lot of ethylene, such as apples and pears, are better suited to the low-humidity drawer. The open vent helps the gas escape.

High-humidity drawers do the opposite. They stay more closed, so moisture remains inside.

That helps foods that lose water easily. Leafy greens such as kale can become soft and wilted when they dry out. Broccoli also benefits from high humidity for the same reason.

The common shortcut - fruit in low humidity and vegetables in high humidity - has important exceptions. Strawberries and citrus fruits, including oranges, prefer high humidity. UC Davis lists an ideal humidity of 90 to 95 percent for both. The food's behavior matters more than its category.

A humidity setting cannot fix the wrong storage location. Iowa State says tomatoes and bananas are better kept at room temperature, such as on a counter. Potatoes, sweet potatoes, onions, and garlic do not need refrigeration. They prefer a cool, dry place instead."""


def main():
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")  # 冒頭で必ず有効化(実測usageログ)

    fc_prompt = r3.build_fact_check_prompt(TOPIC, ARTICLE_EXCERPT, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    with cl.logging_context("household_fact03_reverify", "fact_checker"):
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
        "management_id": "HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01(OPEN-138)",
        "target": "er003_output/n3_01/household/research/verified_fact_ledger.txt FACT-03"
                  "(published paragraph: er003_output/n3_01/household/b1b/article.md)",
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
