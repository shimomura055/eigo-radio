#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01: Gate 3 runtime evidence

Production正式初回path(`er006_pool_pilot_01_writer.py::run_writer_for_theme()`、
mode指定なし[editorial_mode=None]、既存承認済みHanshin Ledger)を実際に1回
呼び出し、Diagnostic Full Retry(Point Overlap NG時の記事全体再生成)が発火
した場合に、診断prompt(`build_diagnostic_retry_prompt()`が構成する実際の
prompt文字列)へ前回Point One/Two本文の実テキストが含まれる(旧プレース
ホルダー文字列が含まれない)ことを確認する。

**instrumentation方針**: `er003_v1_n3_01_articles_generate.py::
build_diagnostic_retry_prompt()`はProduction関数を一切変更せず、この
評価スクリプト内でのみ薄いwrapper(元の関数をそのまま呼び出し、戻り値を
そのままreturnしつつ、evidence保存のため一時変数へ記録するだけ)へ差し
替える。retry判定・prompt内容・戻り値はいずれも無変更(元の関数呼び出しを
1回そのまま経由するだけ)。

費用上限¥60。`cl.install()`をスクリプト冒頭で必ず呼ぶ。
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er006_pool_pilot_01_writer as writer_mod
import er009_n1_routing_governance_10_actual_model_cost as cost_calc

OUT_DIR = "er011_output/open112_diagnostic_retry_point_body_regression_fix_01_runtime_evidence_01"
COST_LOG_PATH = f"{OUT_DIR}/cost_log.jsonl"
COST_CAP_JPY = 60.0

os.makedirs(OUT_DIR, exist_ok=True)
cl.install(COST_LOG_PATH)

client = OpenAI()

HANSHIN_LEDGER_PATH = "er003_output/n3_01/hanshin/research/verified_fact_ledger.txt"
HANSHIN_TOPIC_JA = (
    "2026年6月某日、阪神対広島戦(甲子園)で、阪神が守備の乱れから広島に先制点を許す"
    "も、直後の攻撃でモンテロの適時打などで逆転し、最終的に接戦を制した一戦。ホーム"
    "ランではなく、堅実な攻守の積み重ねと1点を争う緊迫した展開が特徴の試合。"
)

OLD_PLACEHOLDER_P1 = "(Point One body from previous attempt)"
OLD_PLACEHOLDER_P2 = "(Point Two body from previous attempt)"

captured_diagnostic_prompts = []
_original_build_diagnostic_retry_prompt = gen.build_diagnostic_retry_prompt


def _instrumented_build_diagnostic_retry_prompt(original_prompt, previous_article_text, point_overlap):
    """元のProduction関数をそのまま1回呼び出し、戻り値も無変更でそのまま
    returnする。evidence保存のためcaptured_diagnostic_prompts へ記録するのみ。"""
    result = _original_build_diagnostic_retry_prompt(original_prompt, previous_article_text, point_overlap)
    captured_diagnostic_prompts.append({
        "original_prompt_length": len(original_prompt),
        "previous_article_text": previous_article_text,
        "diagnostic_prompt": result,
    })
    return result


def current_cost_jpy() -> float:
    summary = cost_calc.summarize_cost_log(COST_LOG_PATH)
    return summary["total_cost_jpy"]


def run_once(attempt_idx: int) -> dict:
    theme_id = f"open112_g1_evidence_attempt{attempt_idx}"
    out_dir = f"{OUT_DIR}/attempt{attempt_idx}"
    os.makedirs(out_dir, exist_ok=True)
    master_full_text = ab01.load_master_full_text()

    gen.build_diagnostic_retry_prompt = _instrumented_build_diagnostic_retry_prompt
    try:
        writer_output = writer_mod.run_writer_for_theme(
            client, master_full_text, theme_id, HANSHIN_TOPIC_JA,
            HANSHIN_LEDGER_PATH, out_dir,
        )
    finally:
        gen.build_diagnostic_retry_prompt = _original_build_diagnostic_retry_prompt

    # run_writer_for_theme()は{"results": {...}, "timing": {...}, "run_metadata": {...}}
    # を返す(er006_pool_pilot_01_writer.py 111行)。per-level結果は["results"]配下。
    results = writer_output["results"]

    fired = {}
    for label, result in results.items():
        retry_attempts = result.get("point_overlap_article_retry_attempts") or 0
        fired[label] = retry_attempts > 0

    return {"theme_id": theme_id, "out_dir": out_dir, "results_status": {
        k: v.get("status") for k, v in results.items()}, "diagnostic_fired": fired}


def main():
    print("[OPEN-112-G1-EVIDENCE] === Gate 3 runtime evidence: Production正式初回path ===", flush=True)
    attempts_summary = []
    any_fired = False

    for attempt_idx in range(1, 4):  # 初回 + 最大2回まで再実行(合計最大3回)
        cost_before = current_cost_jpy()
        if cost_before >= COST_CAP_JPY:
            print(f"[OPEN-112-G1-EVIDENCE] cost cap reached (¥{cost_before:.2f}), stopping before attempt {attempt_idx}", flush=True)
            break

        print(f"[OPEN-112-G1-EVIDENCE] --- attempt {attempt_idx} (cost so far ¥{cost_before:.2f}) ---", flush=True)
        run_result = run_once(attempt_idx)
        attempts_summary.append(run_result)
        print(f"[OPEN-112-G1-EVIDENCE] attempt {attempt_idx}: status={run_result['results_status']} "
              f"diagnostic_fired={run_result['diagnostic_fired']}", flush=True)

        # 途中終了(taskkill等)でも証跡が残るよう、attemptごとに中間保存する
        with open(f"{OUT_DIR}/evidence_summary_partial.json", "w", encoding="utf-8") as f:
            json.dump({"attempts": attempts_summary, "captured_count": len(captured_diagnostic_prompts)},
                       f, ensure_ascii=False, indent=2, default=str)
        for i, cap in enumerate(captured_diagnostic_prompts):
            with open(f"{OUT_DIR}/captured_diagnostic_prompt_{i}.txt", "w", encoding="utf-8") as f:
                f.write(cap["diagnostic_prompt"])

        if any(run_result["diagnostic_fired"].values()):
            any_fired = True
            break

        cost_after = current_cost_jpy()
        if cost_after >= COST_CAP_JPY:
            print(f"[OPEN-112-G1-EVIDENCE] cost cap reached (¥{cost_after:.2f}) after attempt {attempt_idx}, stopping", flush=True)
            break

    total_cost = current_cost_jpy()
    print(f"[OPEN-112-G1-EVIDENCE] Total cost: ¥{total_cost:.4f}", flush=True)
    print(f"[OPEN-112-G1-EVIDENCE] Diagnostic Full Retry fired at least once: {any_fired}", flush=True)

    verification = None
    if captured_diagnostic_prompts:
        # 最初に発火したcaptureを検証対象とする
        cap = captured_diagnostic_prompts[0]
        prompt_text = cap["diagnostic_prompt"]
        contains_old_placeholder = (OLD_PLACEHOLDER_P1 in prompt_text) or (OLD_PLACEHOLDER_P2 in prompt_text)
        # previous_article_textから前回Point本文を抽出し、実際にprompt内に含まれるか確認
        sections = gen.split_common_sections_for_point_qa(cap["previous_article_text"])
        contains_real_point_one = sections is not None and sections["point_one_body"] != "" and \
            sections["point_one_body"] in prompt_text
        contains_real_point_two = sections is not None and sections["point_two_body"] != "" and \
            sections["point_two_body"] in prompt_text
        verification = {
            "contains_old_placeholder_strings": contains_old_placeholder,
            "contains_real_point_one_body": contains_real_point_one,
            "contains_real_point_two_body": contains_real_point_two,
            "sections_extracted": sections is not None,
        }
        with open(f"{OUT_DIR}/captured_diagnostic_prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt_text)
        print(f"[OPEN-112-G1-EVIDENCE] verification: {verification}", flush=True)
    else:
        print("[OPEN-112-G1-EVIDENCE] Diagnostic Full Retry did NOT fire in any attempt "
              "(within cost cap / attempt budget). No diagnostic prompt captured.")

    summary = {
        "attempts": attempts_summary,
        "any_fired": any_fired,
        "total_cost_jpy": total_cost,
        "verification": verification,
    }
    with open(f"{OUT_DIR}/evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print("[OPEN-112-G1-EVIDENCE] === Complete ===", flush=True)


if __name__ == "__main__":
    main()
