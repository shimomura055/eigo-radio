# ============================================================
# er003_v1_sing01_factqa_generate.py
# ER-003-B1-NOVEL-AUDIO-01: SING01 Fact Safety QA
# ============================================================
# 新規記事(Singularity)のB2本文に対し、既存のFact Checker(独立Web検証、
# er002_ja_web_research_r3)とLedger Deviation Check
# (er003_v1_en_direct_vfl_01_generate)を適用する。新しいQAロジックは
# 作らず、既存モジュールをそのまま再利用する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_factqa_generate.py

from __future__ import annotations

import json
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT_DIR = "er003_output/novel_audio_01/SING01"
ARTICLE_PATH = f"{OUT_DIR}/article/B2_article.md"
LEDGER_PATH = f"{OUT_DIR}/research/verified_fact_ledger.txt"

TOPIC = "AI / Technological Singularity — 2026年時点でのSingularity論争(著名なAI企業リーダーの発言 vs 研究者調査データ)"

WRITER_SOURCES = [
    {"title": "If The AI Singularity Is Here, Where Is The Evidence?", "url": "https://www.forbes.com/sites/ronschmelzer/2026/07/28/ai-singularity-evidence/"},
    {"title": "2026 Singularity? Muskian Comment Is Backed By Real Stuff", "url": "https://www.forbes.com/sites/johnwerner/2026/01/05/2026-singularity-muskian-comment-is-backed-by-real-stuff/"},
    {"title": "The 2026 AI Index Report", "url": "https://hai.stanford.edu/ai-index/2026-ai-index-report"},
    {"title": "AGI/Singularity: 10,000 Predictions Analyzed", "url": "https://aimultiple.com/artificial-general-intelligence-singularity-timing"},
    {"title": "Stanford HAI 2026 AI Index: AI posts gains in science and medicine while often struggling to read a clock", "url": "https://www.rdworldonline.com/stanford-hai-2026-ai-index-ai-posts-gains-in-science-and-medicine-while-often-struggling-to-read-a-clock/"},
]


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    article_text = load_text(ARTICLE_PATH)
    ledger_text = load_text(LEDGER_PATH)

    print("[SING01-FACTQA] Fact Checker(独立Web検証)開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, WRITER_SOURCES)

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[SING01-FACTQA] fact_check status={fc_status} verdict={verdict}")

    with open(f"{OUT_DIR}/research/fact_check_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status": fc_status, "result": fc_result, "model": fc_model,
            "response_id": fc_response_id, "search_usage": fc_search_usage, "sources": fc_sources,
        }, f, ensure_ascii=False, indent=2, default=str)

    print("[SING01-FACTQA] Ledger Deviation Check開始...")
    client = vfl01.get_client()
    deviation_result = vfl01.run_deviation_check(client, ledger_text, article_text)
    print(f"[SING01-FACTQA] deviation={deviation_result['parsed']['overall_status']} "
          f"count={len(deviation_result['parsed']['deviations'])}")

    with open(f"{OUT_DIR}/research/ledger_deviation_result.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "fact_check_status": fc_status, "fact_check_verdict": verdict,
        "ledger_deviation_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
    }
    print("[SING01-FACTQA] 完了。summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
