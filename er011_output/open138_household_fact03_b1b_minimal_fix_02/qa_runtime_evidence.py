# ============================================================
# qa_runtime_evidence.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(OPEN-138)
# ============================================================
# textfix.pyで置換したfact03_fix_02/b1b/article.md(修正後の記事全文)に、
# 既存Production経路のFact Checker(er002_ja_web_research_r3.py、
# web_search tool付き)とLedger Deviation Checker(er003_v1_en_direct_
# vfl_01_generate.py::run_deviation_check、hook_aware=True)をそのまま
# 適用する。呼び出し方法・model・topic・Ledger textは、
# er003_v1_n3_01_articles_generate.py本体がB1B生成時に実際に使っている
# ものと同一(THEMES[household].topic、routing.require_model経由の
# gpt-5.6-luna、verified_fact_ledger.txt v4[FACT-03修正済み])。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_output/open138_household_fact03_b1b_minimal_fix_02/qa_runtime_evidence.py
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
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

# er003_v1_n3_01_articles_generate.py THEMES[household]["topic"]と一字一句
# 同一(Production側は変更していない)。
TOPIC = (
    "冷蔵庫のクリスパードロワー(野菜室)には低湿度・高湿度の2種類があり、正しく"
    "使い分けると食品が長持ちする。高湿度は葉物野菜がしおれるのを防ぎ、低湿度は"
    "果物が放出するエチレンガスを逃がして周囲の食品が早く傷むのを防ぐ。"
    "(Iowa State University Extension and Outreach等の情報に基づく)"
)


def main():
    cl.install(COST_LOG_PATH)

    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    with open(LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    # --- Fact Checker(Production同一関数、web_search tool付き) ---
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])
    fc_model_id = routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt, model=fc_model_id)

    with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02", "fact_checker"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)

    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[fact_checker] status={fc_status} verdict={verdict}")

    fact_qa_record = {
        "label": "B1B", "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
        "source_note": "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02: "
                        "point_one_body差し替え後の記事全体に対し、Production Fact Checker "
                        "(er002_ja_web_research_r3.py)を再実行した結果。",
    }
    with open("er003_output/n3_01/household/fact03_fix_02/b1b/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # --- Ledger Deviation Checker(Production同一関数、hook_aware=True) ---
    client = vfl01.get_client()
    ledger_model_id = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02", "ledger_deviation"):
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model_id, hook_aware=True)

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
    print(f"[ledger_deviation] overall_status={deviation_result['parsed']['overall_status']} "
          f"MAJOR={len(major_items)}件 total_deviations={len(deviation_result['parsed']['deviations'])}")

    with open("er003_output/n3_01/household/fact03_fix_02/b1b/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "fact_checker": {
            "final_status": fc_status, "verdict": verdict,
            "contradictions": fc_result.get("contradictions") if fc_result else None,
            "unsupported_specific_claims": fc_result.get("unsupported_specific_claims") if fc_result else None,
        },
        "ledger_deviation": {
            "overall_status": deviation_result["parsed"]["overall_status"],
            "major_count": len(major_items),
            "major_items": major_items,
            "total_deviations": len(deviation_result["parsed"]["deviations"]),
        },
    }
    with open(f"{OUT_DIR}/qa_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str))
    print(f"\n[qa_runtime_evidence] summary -> {OUT_DIR}/qa_summary.json")


if __name__ == "__main__":
    main()
