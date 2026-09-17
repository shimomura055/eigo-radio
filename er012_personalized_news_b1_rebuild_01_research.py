# ============================================================
# er012_personalized_news_b1_rebuild_01_research.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01
# ============================================================
# 目的: Personalized News B1(Advanced)の再構築のための再Research(Phase 1:
# Researcher+Verification、標準vfl01経路・web_search)。旧Ledger
# (er014_output/four_type_observation_01/voices/research/verified_fact_ledger.txt)
# を信用せず、現在時点(2026-09-17)の一次情報・高品質ソースを再確認する。
# 旧Ledgerで問題となった「短期テストでは政治的態度の測定可能な変化は
# 確認されていない」という一般化が、他の研究(Xのアルゴリズムfeedに関する
# Nature論文、4,965人・約7週間)と矛盾しうる点を明示的に再検証させる。
#
# 出力先: er012_output/personalized_news_b1_rebuild_01/research/
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl

THEME_ID = "personalized_news_b1_rebuild_01"
BASE_DIR = "er012_output/personalized_news_b1_rebuild_01"
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log_research.jsonl"

TOPIC_ID = "is_personalized_news_good_for_us_rebuild_2026_09"

TOPIC_EN = (
    "Current topic (research as of 2026-09-17, this is a REBUILD of an earlier article -- do not "
    "assume the earlier conclusions still hold, re-verify from scratch): is personalized news good "
    "for us? Many news apps, social platforms, and search engines use algorithms to personalize the "
    "news people see, based on past clicks, interests, and behavior. Aim: cover this topic so both "
    "sides are strongly true at once, not a simple good-vs-bad framing. Side 1 (convenience/relevance): "
    "personalization saves time, surfaces stories that match real interests, cuts through information "
    "overload. Side 2 (filter bubble / worldview narrowing / editorial control): personalization can "
    "narrow the range of perspectives and topics people see over time, and shifts editorial control "
    "from human editors to opaque, commercially-incentivized ranking algorithms. "
    "CRITICAL: specifically re-investigate the current state of research on whether algorithmic/"
    "personalized feeds measurably change people's political attitudes or polarization in the "
    "short term versus longer term. Prior research included: (a) a 2023 Nature study of 23,377 US "
    "Facebook users finding no measurable short-term change in political attitude indices when "
    "cross-cutting exposure was reduced (with an explicit caveat that the 3-month design could not "
    "capture cumulative long-term effects), and (b) a separate Nature study of 4,965 active US X "
    "(Twitter) users over an average of about 7 weeks finding that switching from chronological to "
    "algorithmic feed did shift attitudes toward policy/current-events news in a more conservative "
    "direction (about 0.12 SD) with no significant change in affective polarization or self-reported "
    "partisanship. Find and report the CURRENT, up-to-date status of this research area: are there "
    "newer studies (including anything published in 2025 or 2026) that confirm, contradict, or refine "
    "either of these findings? Do not assume either finding generalizes beyond its own platform, "
    "population, and time period. Clearly distinguish observational/correlational findings from "
    "causal/experimental findings, and note the population, region, platform, and time period for "
    "every claim. Flag anything contested or where researchers disagree. Do not invent facts; use "
    "only what is confirmed by web search."
)

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


PRICING = _load_pricing()


def _price(provider, model, meter, tier="Standard"):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier", "Standard") == tier)


def _call_cost_usd(rec: dict) -> float:
    provider, model = rec.get("provider"), rec.get("model_id")
    if provider != "openai":
        return 0.0
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    in_price = _price("openai", model, "input_tokens")
    cached_price = _price("openai", model, "cached_input_tokens")
    out_price = _price("openai", model, "output_tokens")
    cost = (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price
    web_search_calls = rec.get("web_search_call_count") or 0
    web_search_price = _price("openai", "N/A (tool, all models)", "web_search_call")
    cost += (web_search_calls / 1000) * web_search_price
    return cost


def cost_so_far_jpy() -> float:
    if not os.path.exists(LOG_PATH):
        return 0.0
    total_usd = 0.0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("success") is False:
                continue
            total_usd += _call_cost_usd(rec)
    return total_usd * USD_JPY


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


def phase1_research():
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    cl.install(LOG_PATH)

    structured_path = f"{RESEARCH_DIR}/verified_fact_ledger_flat.json"
    if os.path.exists(structured_path):
        with open(structured_path, encoding="utf-8") as f:
            structured = json.load(f)
        print(f"[{THEME_ID}] Resume: 既存のresearch/成果物を再利用します(API call再実行なし)。"
              f"counts={structured['counts']}")
        return structured

    client = vfl01.get_client()
    with cl.logging_context(THEME_ID, "researcher"):
        research_result = run_researcher_for_topic(client, TOPIC_EN)
    with open(f"{RESEARCH_DIR}/fact_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(research_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] Researcher完了: {len(research_result['parsed']['facts'])}件のFact下書き、"
          f"web_search={research_result['search_usage']}")

    with cl.logging_context(THEME_ID, "verification"):
        verification_result = run_verification_for_topic(client, TOPIC_EN, research_result["parsed"])
    with open(f"{RESEARCH_DIR}/fact_ledger_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_result, f, ensure_ascii=False, indent=2, default=str)

    ledger_parsed = research_result["parsed"]
    verdict_map = {v["fact_id"]: v for v in verification_result["parsed"]["verifications"]}
    kept_facts = []
    all_facts_with_verdict = []
    counts = {"VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0}
    for fact in ledger_parsed["facts"]:
        v = verdict_map.get(fact["fact_id"])
        verdict = v["verdict"] if v else "AMBIGUOUS"
        counts[verdict] = counts.get(verdict, 0) + 1
        entry = {**fact, "verification_verdict": verdict,
                 "verification_notes": v["verification_notes"] if v else "(no verification record found)"}
        all_facts_with_verdict.append(entry)
        if verdict != "VERIFIED":
            continue
        kept_facts.append(entry)

    structured = {"topic": TOPIC_EN, "topic_id": TOPIC_ID, "kept_facts": kept_facts,
                  "all_facts_with_verdict": all_facts_with_verdict, "counts": counts,
                  "note": "CONFIRMED(VERIFIED)のみ採用。AMBIGUOUS/REJECTEDはfact_ledger_verification.json"
                          "に記録済みだが本Ledgerからは除外した。"}
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)

    cost = cost_so_far_jpy()
    print(f"[{THEME_ID}] Phase 1(Research+Verification)完了。CONFIRMED(VERIFIED)="
          f"{counts.get('VERIFIED', 0)}件、AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件、"
          f"REJECTED={counts.get('REJECTED', 0)}件。費用実測(累計): ¥{cost:.2f}")
    for f_ in kept_facts:
        print(f"  - {f_['fact_id']}: {f_['claim'][:160]}")
    return structured


if __name__ == "__main__":
    phase1_research()
