# ============================================================
# er012_open131_attribution_block_multiline_fix_02_evidence_01.py
# OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02
# ============================================================
# 目的: `build_voice_attribution_block()`の多行evidence欠落バグを修正した
# 後、実際のProduction関数(er012_b_family_production_runner_01.
# run_fact_check_b1/run_fact_check_a2 -> b1prod/a2prod.run_fact_checker ->
# er002_ja_web_research_r3.build_fact_check_prompt/run_fact_checker_
# with_gates、いずれも既存Production primitive、無変更)を通じてruntime
# evidenceを再取得する。
#
# 追加でfalse accept検証(TRIAL-02の事実誤り混入control、N=2)を、修正後の
# (中身が大幅に増えた)blockに対しても実施し、5/5相当の検知が維持される
# ことを確認する。
#
# 費用: 実際の有料LLM呼び出し4回(B1清書1回、A2清書1回、B1 control改変2回)。
# いずれもweb_search tool使用(本番Fact Checkerと同一設定)。上限¥60。
# 費用ロガーは冒頭で必ず有効化する(本タスク専用ログパス、Production側の
# 既存ログファイルとは別ファイルへ書き込み、Production側ログを汚さない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er012_open131_attribution_block_multiline_fix_02_evidence_01.py
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er005_cost_logger as cl  # noqa: E402
import er012_b_family_editorial_type_registry_01 as registry  # noqa: E402  Production、無変更
import er012_b_family_production_runner_01 as runner  # noqa: E402  Production、無変更

OUT_DIR = f"{REPO_ROOT}/er012_output/open131_attribution_block_multiline_fix_02"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"

# 費用ロガーは冒頭で必ず有効化する(このスクリプト専用ログ、Production側の
# 既存ログ[er012_output/editorial_b_family_production_phase1_02/audit/
# raw_usage_log.jsonl 等]とは別ファイル)。
os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
cl.install(COST_LOG_PATH)
print(f"[evidence-02] cost logger installed: {COST_LOG_PATH}")

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

A2_ARTICLE_PATH = "er012_output/editorial_b_family_voices_a2_production_wiring_01/a2/article.md"
A2_LEDGER_PATH = B1_LEDGER_PATH  # 同一テーマ・同一Ledger(既存evidence_01と同じ前提)

PREVIOUS_EVIDENCE_DIR = "er012_output/open131_fact_attribution_production_wiring_evidence_01"


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


# ============================================================
# false accept control(TRIAL-02の数値改変/主体捏造/実在人物誇張と同種)
# 本物のB1記事(One Voice section)へ、Ledgerのどのevidenceにも対応しない
# 捏造・誇張claimを挿入した2バリアントを作る(N=2)。
# ============================================================
CONTROL_1_FABRICATED_STAT_INSERT = (
    "\n\nA private 2026 workplace survey by a firm called Meridian Analytics "
    "found that 97% of employees who kept the same assigned desk reported "
    "feeling proud of their office, a number no earlier study has come close "
    "to matching.\n"
)

CONTROL_2_NAMED_INDIVIDUAL_EXAGGERATION_INSERT = (
    "\n\nAs workplace psychologist Nigel Oseland has stated in a recent "
    "interview, 95% of all office workers worldwide now consider a personally "
    "assigned desk to be a basic legal right that employers must guarantee.\n"
)


def build_control_article(base_article_text: str, insert_text: str) -> str:
    # One Voice sectionの末尾(Another Voiceの見出し直前)へ挿入する。
    marker = "### Another Voice"
    idx = base_article_text.index(marker)
    return base_article_text[:idx] + insert_text + "\n" + base_article_text[idx:]


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    et = registry.EDITORIAL_TYPES["b_family_voices"]
    original_mode = et["fact_attribution_mode"]

    ledger_text = load_text(B1_LEDGER_PATH)
    b1_article_text = load_text(B1_ARTICLE_PATH)
    a2_article_text = load_text(A2_ARTICLE_PATH)

    print(f"[evidence-02] fact_attribution_mode default = {original_mode} (must be False)")
    assert original_mode is False, "既定はFalseである必要がある(opt-in、既定OFF)"

    off_block = runner.build_fact_attribution_block_if_enabled(ledger_text)
    assert off_block == ""

    try:
        et["fact_attribution_mode"] = True
        on_block_after_fix = runner.build_fact_attribution_block_if_enabled(ledger_text)
        print(f"[evidence-02] ON block length AFTER FIX: {len(on_block_after_fix)} chars, "
              f"{on_block_after_fix.count(chr(10)) + 1} lines")
        with open(f"{OUT_DIR}/on_block_after_fix.txt", "w", encoding="utf-8") as f:
            f.write(on_block_after_fix)

        print("[evidence-02] B1 Fact Checker実行(opt-in ON、修正後block、実LLM呼び出し、web_search使用)...")
        on_b1_after_fix = runner.run_fact_check_b1(b1_article_text, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/b1_on_after_fix_result.json", on_b1_after_fix)

        print("[evidence-02] A2 Fact Checker実行(opt-in ON、修正後block、実LLM呼び出し、web_search使用)...")
        on_a2_after_fix = runner.run_fact_check_a2(a2_article_text, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/a2_on_after_fix_result.json", on_a2_after_fix)

        print("[evidence-02] false accept control 1(fabricated stat, B1, opt-in ON、実LLM呼び出し)...")
        control_1_article = build_control_article(b1_article_text, CONTROL_1_FABRICATED_STAT_INSERT)
        control_1_result = runner.run_fact_check_b1(control_1_article, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/control_1_fabricated_stat_result.json", control_1_result)

        print("[evidence-02] false accept control 2(named individual exaggeration, B1, opt-in ON、実LLM呼び出し)...")
        control_2_article = build_control_article(b1_article_text, CONTROL_2_NAMED_INDIVIDUAL_EXAGGERATION_INSERT)
        control_2_result = runner.run_fact_check_b1(control_2_article, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/control_2_named_individual_result.json", control_2_result)
    finally:
        et["fact_attribution_mode"] = original_mode
        print(f"[evidence-02] fact_attribution_mode restored to {et['fact_attribution_mode']}")

    # 修正前(既存記録、追加課金なしで読み取りのみ)との比較
    prev_comparison = load_json(f"{PREVIOUS_EVIDENCE_DIR}/on_off_comparison.json")

    comparison = {
        "b1": {
            "off_pre_existing_baseline": prev_comparison["b1"]["off"],
            "on_before_fix_truncated_block": prev_comparison["b1"]["on"],
            "on_after_fix_full_block": summarize(on_b1_after_fix, "b1_on_after_fix"),
        },
        "a2": {
            "off_pre_existing_baseline": prev_comparison["a2"]["off"],
            "on_before_fix_truncated_block": prev_comparison["a2"]["on"],
            "on_after_fix_full_block": summarize(on_a2_after_fix, "a2_on_after_fix"),
        },
        "false_accept_control": {
            "control_1_fabricated_stat": summarize(control_1_result, "control_1_fabricated_stat"),
            "control_2_named_individual_exaggeration": summarize(control_2_result, "control_2_named_individual"),
        },
        "block_size": {
            "before_fix_evidence_only_chars": 741,
            "before_fix_evidence_only_lines": 13,
            "after_fix_evidence_only_chars": len(on_block_after_fix.split(
                "【Voice別 Verified Fact Ledger evidence(抜粋)】\n", 1)[1].rstrip("\n"))
            if "【Voice別 Verified Fact Ledger evidence(抜粋)】\n" in on_block_after_fix else None,
        },
    }
    save_json(f"{OUT_DIR}/on_off_comparison_after_fix.json", comparison)
    print(json.dumps(comparison, ensure_ascii=False, indent=2))

    jpy, by_provider = runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    print(f"[evidence-02][cost] total so far = {jpy:.2f} JPY by_provider={by_provider}")
    save_json(f"{OUT_DIR}/cost_report_after_fix.json", {"total_jpy_at_160": jpy, "by_provider_jpy": by_provider})


if __name__ == "__main__":
    main()
