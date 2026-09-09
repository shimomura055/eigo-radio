# ============================================================
# revision3_qa.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続、Fable修正指示1回目)
# ============================================================
# revision2("...others in the low-humidity one.")はTTSが2回目の"humidity"
# を3回連続で省略しASR照合がTRUE_CONTENT_MISMATCHとなりHuman Review Lock
# が発動した。Ledger v4の範囲内で同じ事実内容のまま、"low-humidity one"の
# 省略されやすい反復パターンを避けたrevision3を2案作成し、Fact Checker/
# Ledger Deviationを通す。新しい具体的事実は追加しない。
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

ARTICLE_PATH = "er003_output/n3_01/household/fact03_fix_02/b1b/article.md"
LEDGER_PATH = "er003_output/n3_01/household/research/verified_fact_ledger.txt"
OUT_DIR = "er011_output/open138_household_fact03_b1b_minimal_fix_02"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log_revision3.jsonl"

TOPIC = (
    "冷蔵庫のクリスパードロワー(野菜室)には低湿度・高湿度の2種類があり、正しく"
    "使い分けると食品が長持ちする。高湿度は葉物野菜がしおれるのを防ぎ、低湿度は"
    "果物が放出するエチレンガスを逃がして周囲の食品が早く傷むのを防ぐ。"
    "(Iowa State University Extension and Outreach等の情報に基づく)"
)

REVISION2_BODY = (
    "The common shortcut—fruit in low humidity and vegetables in high humidity"
    "—has important exceptions. Strawberries are one case: some refrigerator "
    "makers place them in the high-humidity drawer, others in the low-humidity one. "
    "The food’s behavior matters more than its category."
)

CANDIDATES = {
    "revision3a": (
        "The common shortcut—fruit in low humidity and vegetables in high humidity"
        "—has important exceptions. Strawberries are one case: some refrigerator "
        "makers put them in the high-humidity drawer, while others put them in the "
        "low-humidity drawer instead. The food’s behavior matters more than its "
        "category."
    ),
    "revision3b": (
        "The common shortcut—fruit in low humidity and vegetables in high humidity"
        "—has important exceptions. Strawberries are one case: some refrigerator "
        "makers keep them in the high-humidity drawer, but other brands choose the "
        "low-humidity setting instead. The food’s behavior matters more than its "
        "category."
    ),
}


def build_full_article(body_text: str, base_article_text: str) -> str:
    assert base_article_text.count(REVISION2_BODY) == 1, (
        "base article.mdにrevision2本文がちょうど1箇所存在しません。"
    )
    return base_article_text.replace(REVISION2_BODY, body_text)


def run_qa_for(name: str, article_text: str, verified_ledger_text: str) -> dict:
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])
    fc_model_id = routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt, model=fc_model_id)

    with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02-REVISION3", f"fact_checker_{name}"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)

    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[{name}][fact_checker] status={fc_status} verdict={verdict}")

    client = vfl01.get_client()
    ledger_model_id = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02-REVISION3", f"ledger_deviation_{name}"):
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model_id, hook_aware=True)

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
    print(f"[{name}][ledger_deviation] overall_status={deviation_result['parsed']['overall_status']} "
          f"MAJOR={len(major_items)}件")

    return {
        "fact_checker": {
            "final_status": fc_status, "verdict": verdict,
            "contradictions": fc_result.get("contradictions") if fc_result else None,
            "unsupported_specific_claims": fc_result.get("unsupported_specific_claims") if fc_result else None,
            "attempts": len(fc_attempts),
        },
        "ledger_deviation": {
            "overall_status": deviation_result["parsed"]["overall_status"],
            "major_count": len(major_items),
            "major_items": major_items,
            "total_deviations": len(deviation_result["parsed"]["deviations"]),
        },
        "full_fact_checker_result": fc_result,
        "full_deviation_parsed": deviation_result["parsed"],
    }


def main():
    cl.install(COST_LOG_PATH)

    with open(ARTICLE_PATH, encoding="utf-8") as f:
        base_article_text = f.read()
    with open(LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    results = {}
    for name, body in CANDIDATES.items():
        article_text = build_full_article(body, base_article_text)
        results[name] = run_qa_for(name, article_text, verified_ledger_text)
        results[name]["body_text"] = body

    with open(f"{OUT_DIR}/revision3_qa_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print("\n=== SUMMARY ===")
    for name, r in results.items():
        print(f"{name}: fact_checker={r['fact_checker']['final_status']} "
              f"ledger={r['ledger_deviation']['overall_status']} "
              f"MAJOR={r['ledger_deviation']['major_count']}")
    print(f"\n[revision3_qa] -> {OUT_DIR}/revision3_qa_results.json")


if __name__ == "__main__":
    main()
