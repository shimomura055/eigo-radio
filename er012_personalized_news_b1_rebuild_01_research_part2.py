# ============================================================
# er012_personalized_news_b1_rebuild_01_research_part2.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01
# ============================================================
# Part 2: Voice 1(パーソナライズの便利さ・関連性)側の事実・パーソナライズ
# 機構の説明・規制動向(EU DSA等)を、現在時点で再確認する追加Research。
# Part 1(政治的態度変化の研究動向)とは別クエリで実行し、結果は同じ
# research/配下へ別ファイルとして保存、後でLedger統合時にfact_idの重複を
# 避けるためprefix "P2-" を付与する。
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl

BASE_DIR = "er012_output/personalized_news_b1_rebuild_01"
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log_research_part2.jsonl"
THEME_ID = "personalized_news_b1_rebuild_01_part2"

TOPIC_EN_PART2 = (
    "Current topic (research as of 2026-09-17): re-verify, from current sources, the following claims "
    "about personalized/algorithmic news feeds that were used in an earlier article: (1) how Google News "
    "personalizes its 'For You'/'Following' sections based on followed topics/sources and past Google/"
    "YouTube activity, and what controls users have to adjust this (follow/unfollow, show more/less, hide "
    "source) -- confirm this is still accurate as currently documented by Google; (2) how Meta describes "
    "its Facebook News Feed ranking (signals used, approximate scale of candidate posts considered per "
    "person) -- confirm current official description; (3) Reuters Institute survey findings on how people "
    "feel about algorithmic/automated news selection versus editor-selected news, including comfort levels, "
    "efficiency perceptions, and stated worries about missing important stories or missing other viewpoints "
    "-- find the most recent available Reuters Institute Digital News Report or related survey data (2024, "
    "2025, or 2026 if available), not just older survey waves; (4) the current legal status and content of "
    "EU Digital Services Act (Regulation (EU) 2022/2065) Articles 27 and 38 on recommender system "
    "transparency and non-profiling alternatives -- confirm these articles are still in force as described "
    "and note any amendments; (5) how the US Congressional Research Service or similar official body "
    "currently describes social media companies' ability to tune ranking algorithms toward engagement or "
    "ad revenue goals. For each claim, report the exact current wording/finding, source, publication date, "
    "and population/scope. Do not invent details; use only what is confirmed by web search."
)


def run_researcher_for_topic(client, topic: str) -> dict:
    prompt = vfl01.build_researcher_prompt(topic=topic)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
            "response_id": response.id, "search_usage": search_usage, "sources": sources}


def run_verification_for_topic(client, topic: str, ledger_parsed: dict) -> dict:
    prompt = vfl01.build_verification_prompt(topic, ledger_parsed)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
            "response_id": response.id, "search_usage": search_usage, "sources": sources}


def main():
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    structured_path = f"{RESEARCH_DIR}/verified_fact_ledger_flat_part2.json"
    if os.path.exists(structured_path):
        print("[part2] 既存成果物を再利用します。")
        return
    client = vfl01.get_client()
    with cl.logging_context(THEME_ID, "researcher"):
        research_result = run_researcher_for_topic(client, TOPIC_EN_PART2)
    with open(f"{RESEARCH_DIR}/fact_ledger_draft_part2.json", "w", encoding="utf-8") as f:
        json.dump(research_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[part2] Researcher完了: {len(research_result['parsed']['facts'])}件")

    with cl.logging_context(THEME_ID, "verification"):
        verification_result = run_verification_for_topic(client, TOPIC_EN_PART2, research_result["parsed"])
    with open(f"{RESEARCH_DIR}/fact_ledger_verification_part2.json", "w", encoding="utf-8") as f:
        json.dump(verification_result, f, ensure_ascii=False, indent=2, default=str)

    ledger_parsed = research_result["parsed"]
    verdict_map = {v["fact_id"]: v for v in verification_result["parsed"]["verifications"]}
    all_facts = []
    counts = {"VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0}
    for fact in ledger_parsed["facts"]:
        v = verdict_map.get(fact["fact_id"])
        verdict = v["verdict"] if v else "AMBIGUOUS"
        counts[verdict] = counts.get(verdict, 0) + 1
        all_facts.append({**fact, "verification_verdict": verdict,
                           "verification_notes": v["verification_notes"] if v else "(no record)"})
    structured = {"topic": TOPIC_EN_PART2, "all_facts_with_verdict": all_facts, "counts": counts}
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    print(f"[part2] 完了。counts={counts}")


if __name__ == "__main__":
    main()
