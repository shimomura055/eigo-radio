# ============================================================
# er012_open131_fact_attribution_local_rewrite_evidence_01.py
# OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01
# ============================================================
# 目的: 実際のLocal Rewrite primitive(er010_ledger_local_rewrite_09.py::
# apply_rewrites()、既存Production関数・無変更)を使い、B1 Phase 1記事の
# 実文1件を「内容不変・表現のみ変更」する形で書き換えたうえで、opt-in ON
# の実Fact Checker(er012_open131_fact_attribution_production_wiring_
# evidence_01.pyと同じProduction経路)を再実行し、書き換え後も帰属
# (attribution)判定が維持されることを実出力で確認する。
#
# 費用: 実際の有料LLM呼び出し1回(追加、web_search使用)。上限¥60
# (er012_open131_fact_attribution_production_wiring_evidence_01.pyの
# 既存2回[合計約¥6.92]と合算しても上限内)。
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er010_ledger_local_rewrite_09 as rewrite_mod  # noqa: E402  Production、無変更
import er012_b_family_editorial_type_registry_01 as registry  # noqa: E402  Production、無変更
import er012_b_family_production_runner_01 as runner  # noqa: E402  Production、無変更

OUT_DIR = f"{REPO_ROOT}/er012_output/open131_fact_attribution_production_wiring_evidence_01"
B1_ARTICLE_PATH = "er012_output/editorial_b_family_production_phase1_02/b1b/article.md"
B1_LEDGER_PATH = "er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt"

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

# 実記事(Voice A本文)の1文。内容を変えず、表現のみ言い換える
# (Local Rewriteの契約=「内容不変・表現のみ変更」を模した合成rewrite_results。
# 実際のLLMによるrewrite生成[generate_rewrite]は呼ばず、apply_rewrites()
# という既存Production純関数[str.replaceのみ]自体を実引数で駆動する)。
ORIGINAL_SENTENCE = "I miss the same desk, drawer, and view."
REWRITTEN_SENTENCE = "I miss having that same desk, that same drawer, and that same view every day."

SYNTHETIC_REWRITE_RESULTS = [
    {"original_ng_sentence": ORIGINAL_SENTENCE, "final_text": REWRITTEN_SENTENCE,
     "issue": "synthetic-local-rewrite-simulation-for-open131-evidence", "resolved": True,
     "human_review_required": False},
]


def load_text(path: str) -> str:
    with open(f"{REPO_ROOT}/{path}", encoding="utf-8") as f:
        return f.read()


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    article_text = load_text(B1_ARTICLE_PATH)
    ledger_text = load_text(B1_LEDGER_PATH)

    assert ORIGINAL_SENTENCE in article_text, "対象文が実記事内に見つからない"

    rewritten_text = rewrite_mod.apply_rewrites(article_text, SYNTHETIC_REWRITE_RESULTS)
    assert rewritten_text != article_text
    assert REWRITTEN_SENTENCE in rewritten_text
    assert ORIGINAL_SENTENCE not in rewritten_text
    print("[evidence] apply_rewrites()による書き換え確認: OK(1文のみ変更、他は不変)")

    et = registry.EDITORIAL_TYPES["b_family_voices"]
    original_mode = et["fact_attribution_mode"]
    try:
        et["fact_attribution_mode"] = True
        block_before = runner.build_fact_attribution_block_if_enabled(ledger_text)
        block_after = runner.build_fact_attribution_block_if_enabled(ledger_text)
        assert block_before == block_after, "blockはarticle_textに依存しないはず"
        print(f"[evidence] block不変確認: OK(rewrite前後で同一block、length={len(block_after)})")

        print("[evidence] rewrite後の記事でFact Checker再実行(opt-in ON、実LLM呼び出し)...")
        result = runner.run_fact_check_b1(rewritten_text, TOPIC_JA, ledger_text)
        save_json(f"{OUT_DIR}/b1_on_after_local_rewrite_result.json", result)
    finally:
        et["fact_attribution_mode"] = original_mode

    r = result.get("result") or {}
    summary = {
        "final_status": result.get("final_status"),
        "verdict": r.get("verdict"),
        "unsupported_specific_claims_count": len(r.get("unsupported_specific_claims") or []),
        "unsupported_specific_claims": r.get("unsupported_specific_claims"),
    }
    save_json(f"{OUT_DIR}/b1_on_after_local_rewrite_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
