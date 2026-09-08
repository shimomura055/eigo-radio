# ============================================================
# er012_open131_fact_attribution_production_wiring_evidence_01.py
# OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01
# ============================================================
# 目的: 本タスクで実際に配線したFact Checker候補A'(opt-in、既定OFF)を、
# 実際のProduction関数(er012_b_family_production_runner_01.run_fact_
# check_b1/run_fact_check_a2 -> b1prod/a2prod.run_fact_checker ->
# er002_ja_web_research_r3.build_fact_check_prompt/make_fact_checker_fn/
# run_fact_checker_with_gates、いずれも既存Production primitive)を通じて、
# B-Family B1(Phase 1記事)・A2(production_wiring_01記事)の実記事に対し
# opt-in ONで実行し、OFF時(既存記録)と比較する。
#
# 費用: 実際の有料LLM呼び出し2回(B1・A2それぞれ1回、opt-in ON時のみ。
# OFF側は既存記録[fact_qa.json/fact_check.json]を再利用し追加課金なし)。
# web_search tool使用(本番Fact Checkerと同一設定)。上限¥60。
#
# 実行方法:
#   .venv/Scripts/python.exe er012_open131_fact_attribution_production_wiring_evidence_01.py
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er012_b_family_editorial_type_registry_01 as registry  # noqa: E402  Production、無変更
import er012_b_family_production_runner_01 as runner  # noqa: E402  Production、無変更

OUT_DIR = f"{REPO_ROOT}/er012_output/open131_fact_attribution_production_wiring_evidence_01"

# 実際のTrial-07 TOPIC_JA定数の全文コピー(Production runner自体は
# Trialスクリプトを一切importしないという既存設計方針を、本evidence
# script自体にも適用するため、importではなく文字列として転記した。
# 内容はEDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01/02
# および過去のB-Family全runで使われてきたものと同一)。
TOPIC_JA = (
    "2026年9月時点、オフィスの座席運用が変わりつつある。パンデミック下で広がった"
    "フリーアドレス制(ホットデスキング、社員が毎日座席を選ぶ方式)をやめ、社員一人"
    "ひとりに専用の「固定席」を再び割り当てる動きが一部の企業で見られる一方、"
    "デスク共有(ホットデスキング)を維持・拡大する企業も依然として多い。この記事の"
    "中心テーマは、『固定席派 vs フリーアドレス派』のどちらが正しいかを決めることでは"
    "なく、同じオフィスで働く社員という同じ立場の中にも、固定席を好む人と自由席"
    "(フリーアドレス)を好む人がいて、それぞれになぜそう思うのか、何を大切にし、"
    "何を不便・不安・価値と感じ、どんな経験や条件からその考えに至っているのかを、"
    "実在する発言・調査・事例に基づいて具体的に描き、そのうえで、なぜ同じ状況が"
    "人によって違って見えるのかを理解することである。"
)

B1_ARTICLE_PATH = "er012_output/editorial_b_family_production_phase1_02/b1b/article.md"
B1_LEDGER_PATH = "er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt"
B1_OFF_BASELINE_PATH = "er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/fact_qa.json"

A2_ARTICLE_PATH = "er012_output/editorial_b_family_voices_a2_production_wiring_01/a2/article.md"
A2_LEDGER_PATH = B1_LEDGER_PATH  # 同一テーマ・同一Ledger(A2は同一article.mdをsha256照合済みで再利用)
A2_OFF_BASELINE_PATH = "er012_output/editorial_b_voices_a2_free_address_04/a2/audit/fact_check.json"


def load_text(path: str) -> str:
    with open(f"{REPO_ROOT}/{path}", encoding="utf-8") as f:
        return f.read()


def load_json(path: str) -> dict:
    with open(f"{REPO_ROOT}/{path}", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def summarize(result_dict: dict, label: str) -> dict:
    r = result_dict.get("result") or {}
    return {
        "label": label,
        "final_status": result_dict.get("final_status"),
        "verdict": r.get("verdict"),
        "unsupported_specific_claims_count": len(r.get("unsupported_specific_claims") or []),
        "contradictions_count": len(r.get("contradictions") or []),
        "unsupported_specific_claims": r.get("unsupported_specific_claims"),
    }


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    et = registry.EDITORIAL_TYPES["b_family_voices"]
    original_mode = et["fact_attribution_mode"]

    ledger_text = load_text(B1_LEDGER_PATH)
    b1_article_text = load_text(B1_ARTICLE_PATH)
    a2_article_text = load_text(A2_ARTICLE_PATH)

    off_b1 = load_json(B1_OFF_BASELINE_PATH)
    off_a2 = load_json(A2_OFF_BASELINE_PATH)

    print(f"[evidence] fact_attribution_mode default = {original_mode} (must be False)")
    assert original_mode is False, "既定はFalseである必要がある(opt-in、既定OFF)"

    # 既定OFFで呼んだ場合、blockは空文字列であることを確認(実際にはLLM
    # 呼び出し前のprompt構築段階の検証のみ、追加課金なし)。
    off_block = runner.build_fact_attribution_block_if_enabled(ledger_text)
    print(f"[evidence] OFF block empty: {off_block == ''}")
    assert off_block == ""

    try:
        et["fact_attribution_mode"] = True
        on_block = runner.build_fact_attribution_block_if_enabled(ledger_text)
        print(f"[evidence] ON block length: {len(on_block)}")
        assert on_block != ""

        print("[evidence] B1 Fact Checker実行(opt-in ON、実LLM呼び出し、web_search使用)...")
        on_b1 = runner.run_fact_check_b1(b1_article_text, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/b1_on_result.json", on_b1)

        print("[evidence] A2 Fact Checker実行(opt-in ON、実LLM呼び出し、web_search使用)...")
        on_a2 = runner.run_fact_check_a2(a2_article_text, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/a2_on_result.json", on_a2)
    finally:
        et["fact_attribution_mode"] = original_mode
        print(f"[evidence] fact_attribution_mode restored to {et['fact_attribution_mode']}")

    comparison = {
        "b1": {"off": summarize(off_b1, "b1_off_existing_record"), "on": summarize(on_b1, "b1_on_new_run")},
        "a2": {"off": summarize(off_a2, "a2_off_existing_record"), "on": summarize(on_a2, "a2_on_new_run")},
    }
    save_json(f"{OUT_DIR}/on_off_comparison.json", comparison)
    print(json.dumps(comparison, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
