#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13

Diagnostic Full Retry を正式Production本体へ統合し、
er003_v1_n3_01_articles_generate.py の実装を検証する。

No.9 A2 (Digital tipping screens) を正式Production経路で実行。
実装：Build Diagnostic section（診断情報なし）→
      Point overlap check → flagged なら Diagnostic Retry
      → Ledger Deviation + Fact Check
"""

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as n3_01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

OUT_DIR = "er009_output/diagnostic_full_retry_production_wiring_13"
COST_LOG_PATH = f"{OUT_DIR}/cost_log.jsonl"
RESULTS_PATH = f"{OUT_DIR}/results.json"

os.makedirs(OUT_DIR, exist_ok=True)
cl.install(COST_LOG_PATH)

client = OpenAI()

# No.9 A2 topic (Digital tipping screens)
TOPIC_JA = ("デジタルtippingスクリーン（支払い時に顧客に提示されるチップ金額の"
            "提案画面）が、消費者の行動に影響を与えているという研究。"
            "ニューヨーク市タクシーの2014年研究では、提案額が高いほど"
            "チップ額も増えるが、同時に「チップをゼロにする」選択を"
            "する乗客も増える二重効果があったという結果と、"
            "2026年Popmenu調査での米国消費者78%がtipping practicesを"
            "ridiculous（不当・馬鹿げている）と回答した事例。")

TOPIC_EN = "Digital Tipping Screens"

# Verified Fact Ledger (使用する記事のLedger)
# er009_n1_full_writer_ledger_integration_08 のものと同一
VERIFIED_LEDGER_TEXT = """
【研究1】Haggag & Paci (2014) "Default Tips"
- ニューヨーク市タクシー: 13百万件以上のクレジットカード利用記録を分析
- 決済端末の提示額が $15 未満では $2-4、$15 以上では 20-30% へ変更
- 高いデフォルト提案により平均チップ額は増加
- 同時に「チップゼロ」を選ぶ乗客の割合も増加
- American Economic Journal: Applied Economics

【研究2】Alexander, Boone, Lynn
- ランドリーサービスのフィールド実験
- tip推奨が顧客チップ額・再来店頻度に与える影響を検証

【Rutgers (2022) "Guilt Tipping and the Inflated Default Tip"】
- デジタル画面で従業員の前で tip割合を選ぶ社会的圧力を分析
- 高いデフォルト提案が平均チップを増やす効果を論文で整理
- tip額がある閾値を超えると「意図的にゼロを選ぶ」傾向

【Popmenu 2026年消費者調査】
- 2026年3月15-16日実施、米国成人1000人対象
- 78% が tipping practices を「ridiculous」と評価
- 44% が前年度より tip を減らしたと回答
- 各業界（レストラン、デリバリー、ホテル、タクシー、ライドシェア等）での傾向調査
- これは消費者の自己申告: デジタル画面が原因と証明するものではない
""".strip()


def run_production_validation() -> dict:
    """正式Production経路で A2 記事を生成し、Diagnostic Full Retry の
    完全な動作を検証する。
    """
    print("[WIRING-13] === ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13 ===")

    # Build prompt using n3_01 infrastructure
    master_full_text = ab01.load_master_full_text()
    common_block = n3_01.build_common_block(master_full_text, TOPIC_JA, VERIFIED_LEDGER_TEXT,
                                             shared_point_blueprint_block="")
    prompt = n3_01.build_prompt(common_block, n3_01.A2_KAI1_INSTRUCTION)

    theme_id = "n9_tipping_screens"
    label = "A2"
    out_dir = f"{OUT_DIR}/production_runtime"

    # Run production pattern via n3_01.run_one_pattern
    print(f"[WIRING-13] {label}: Starting production-wired generation...")
    start_time = time.time()
    result = n3_01.run_one_pattern(
        client, theme_id, label, prompt, VERIFIED_LEDGER_TEXT, TOPIC_EN, out_dir,
        apply_evidence_compression=True, apply_directional_fact_precheck=False)
    elapsed = time.time() - start_time

    # Extract results
    return {
        "theme_id": theme_id,
        "label": label,
        "status": result.get("status"),
        "elapsed_seconds": elapsed,
        "article_text": result.get("article_text"),
        "metrics": result.get("metrics"),
        "section_word_counts": result.get("section_word_counts"),
        "point_overlap_qa_applied": result.get("point_overlap_qa_applied"),
        "fact_status": result.get("fact_status"),
        "fact_verdict": result.get("fact_verdict"),
        "ledger_status": result.get("ledger_status"),
        "ledger_deviation_count": result.get("ledger_deviation_count"),
        "evidence_compression_applied": result.get("evidence_compression_applied"),
    }


def main():
    print("[WIRING-13] Writer Model: gpt-5.6-luna (via routing SSOT)")

    # Production validation
    result = run_production_validation()

    # Load retry log for diagnostic info
    retry_log_path = f"{OUT_DIR}/production_runtime/point_overlap_article_retry_log.json"
    retry_log = []
    if os.path.exists(retry_log_path):
        with open(retry_log_path, encoding="utf-8") as f:
            retry_log = json.load(f)

    # Save comprehensive results
    safe_result = {
        "status": result.get("status"),
        "writer_model": routing.require_model("A2_WRITER", routing.WRITER_MODEL),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "article_text": result.get("article_text"),
        "metrics": result.get("metrics"),
        "section_word_counts": result.get("section_word_counts"),
        "point_overlap_retry_log": retry_log,
        "point_overlap_qa_applied": result.get("point_overlap_qa_applied"),
        "fact_status": result.get("fact_status"),
        "fact_verdict": result.get("fact_verdict"),
        "ledger_status": result.get("ledger_status"),
        "ledger_deviation_count": result.get("ledger_deviation_count"),
        "evidence_compression_applied": result.get("evidence_compression_applied"),
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(safe_result, f, ensure_ascii=False, indent=2, default=str)

    # Cost summary
    cost_summary = __import__("er009_n1_routing_governance_10_actual_model_cost",
                              fromlist=["summarize_cost_log"]).summarize_cost_log(COST_LOG_PATH)
    print(f"[WIRING-13] Total Cost: ¥{cost_summary['total_cost_jpy']:.4f} ({cost_summary['total_calls']} calls)")

    # Report
    print(f"[WIRING-13] Status: {result['status']}")
    if retry_log:
        print(f"[WIRING-13] Point Overlap Retry Attempts: {len(retry_log) - 1}")
        for log_entry in retry_log:
            flagged = log_entry.get("flagged")
            if log_entry["report"]:
                p1_score = log_entry["report"].get("point_one", {}).get("before_overlap", {}).get("overlap_ratio")
                p2_score = log_entry["report"].get("point_two", {}).get("before_overlap", {}).get("overlap_ratio")
                print(f"  Attempt {log_entry['attempt']}: P1={p1_score:.3f}, P2={p2_score:.3f}, flagged={flagged}")
    print(f"[WIRING-13] Ledger Status: {result['ledger_status']}")
    print(f"[WIRING-13] Fact Verdict: {result['fact_verdict']}")
    print("[WIRING-13] === Complete ===")


if __name__ == "__main__":
    main()
