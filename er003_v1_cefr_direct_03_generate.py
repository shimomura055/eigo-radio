# ============================================================
# er003_v1_cefr_direct_03_generate.py
# ER-003-CEFR-DIRECT-03: A01/ADD03 CEFR Direct Cross-Genre Validation
# ============================================================
# ER-003-CEFR-DIRECT-02でA02について検証したVariation 2(Listening/
# Cognitive Load)完全記事構成のDifficulty Controlを、別ジャンル2記事
# (A01: スポーツ、ADD03: 経済・地政学)へ横展開する。
#
# 各記事につき B2 V2 / B1 V2 / A2 V2 改1(Cognitive Load Reduction)の
# 3版を、日本語阪神master + 既存Verified Fact Ledger(ER-003-EN-DIRECT-
# VFL-02の最終rerun版、新規researchなし)からDirect Generation方式で
# 生成する。Original(VFL-02最終版)はwriter入力に使わず、比較基準
# としてのみ使用する。
#
# Production(CURRENT_SPEC.md、R4 Production prompt、VFL/spoken_first/
# cefr_direct_01/02関連スクリプト)は一切変更せず、この独立スクリプト
# から関数を読み取り専用でimportするのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_cefr_direct_03_generate.py

from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er003_v1_cefr_direct_02_generate as cd2

load_dotenv()

OUT_DIR = "er003_output/cefr_direct_03"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

POINT_TARGET_LOWER = cd2.POINT_TARGET_LOWER
POINT_TARGET_UPPER = cd2.POINT_TARGET_UPPER
POINT_TOLERANCE_LOWER = cd2.POINT_TOLERANCE_LOWER
POINT_TOLERANCE_UPPER = cd2.POINT_TOLERANCE_UPPER
TOTAL_SOFT_LOWER = cd2.TOTAL_SOFT_LOWER
TOTAL_SOFT_UPPER = cd2.TOTAL_SOFT_UPPER

ARTICLES = {
    "A01": {
        "topic": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
        "ledger_path": "er003_output/en_direct_vfl_02/A01/verified_fact_ledger.txt",
        "original_path": "er003_output/en_direct_vfl_02/A01/article.md",
    },
    "ADD03": {
        "topic": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
        "ledger_path": "er003_output/en_direct_vfl_02/ADD03/verified_fact_ledger.txt",
        "original_path": "er003_output/en_direct_vfl_02/ADD03/article.md",
    },
}

# ER-003-CEFR-DIRECT-02の共通prompt枠組み・難易度指示文(B2/B1/A2改1)を
# そのまま再利用する。COMMON_BLOCK_TEMPLATEはA02固有の内容を含まない
# 汎用テンプレートであることを確認済み。
COMMON_BLOCK_TEMPLATE = cd2.COMMON_BLOCK_TEMPLATE
B2_V2_INSTRUCTION = cd2.B2_V2_INSTRUCTION
B1_V2_INSTRUCTION = cd2.B1_V2_INSTRUCTION
A2_KAI1_INSTRUCTION = cd2.A2_KAI1_INSTRUCTION

PATTERNS = [("B2_v2", B2_V2_INSTRUCTION), ("B1_v2", B1_V2_INSTRUCTION), ("A2_kai1", A2_KAI1_INSTRUCTION)]


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_common_block(master_full_text: str, topic: str, verified_ledger_text: str) -> str:
    return COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
    )


def build_prompt(common_block: str, instruction: str) -> str:
    return common_block + "\n【難易度指示】\n" + instruction


# ============================================================
# Metrics(参考値のみ。ER-003-CEFR-DIRECT-02と同一ロジック)
# ============================================================
compute_metrics = cd2.compute_metrics


# ============================================================
# 1版のFull pipeline(writer -> fact check -> ledger deviation)
# ============================================================
def run_one_pattern(client, article_id: str, topic: str, label: str, prompt: str,
                     verified_ledger_text: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    tag = f"{article_id}:{label}"
    print(f"[CEFR-DIRECT-03] {tag}: writer呼び出し開始...")
    writer_result = vfl01.run_writer_with_technical_retry(client, prompt)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[CEFR-DIRECT-03] {tag}: writer失敗 status={writer_result['status']}")
        return {"label": label, "status": writer_result["status"], "article_text": None}

    article_text = writer_result["raw_text"].strip()
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    metrics = compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": POINT_TARGET_LOWER <= section_wc["point_one"] <= POINT_TARGET_UPPER,
        "point_one_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= POINT_TOLERANCE_UPPER,
        "point_two_within_target": POINT_TARGET_LOWER <= section_wc["point_two"] <= POINT_TARGET_UPPER,
        "point_two_within_tolerance": POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= POINT_TOLERANCE_UPPER,
        "total_within_soft_range": TOTAL_SOFT_LOWER <= metrics["word_count"] <= TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[CEFR-DIRECT-03] {tag}: metrics={metrics} sections={section_wc}")

    print(f"[CEFR-DIRECT-03] {tag}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[CEFR-DIRECT-03] {tag}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    print(f"[CEFR-DIRECT-03] {tag}: ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text)
    print(f"[CEFR-DIRECT-03] {tag}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "writer_technical_attempts": len(writer_result["attempts"]),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()
    master_ja_full_text = vfl01.load_master_full_text()

    summary = {}
    for article_id, cfg in ARTICLES.items():
        summary[article_id] = {}
        verified_ledger_text = load_text(cfg["ledger_path"])
        common_block = build_common_block(master_ja_full_text, cfg["topic"], verified_ledger_text)
        for label, instruction in PATTERNS:
            prompt = build_prompt(common_block, instruction)
            out_dir = f"{OUT_DIR}/{article_id}/{label}"
            result = run_one_pattern(client, article_id, cfg["topic"], label, prompt, verified_ledger_text, out_dir)
            summary[article_id][label] = {k: v for k, v in result.items() if k != "article_text"}

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[CEFR-DIRECT-03] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
