# ============================================================
# er014_output/four_type_observation_01/voices/run_voices_2v_b1.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-
# WIRING-01(OPEN-151)
# ============================================================
# 目的: 「Production Writerを2/3 Voices可変へ一般化する」(2026-09-14
# ユーザー正式決定、APPROVED_FOR_PRODUCTION)の2V runtime evidence取得。
# topic「Is personalized news good for us?」(personalizationの便利さ・
# relevance vs filter bubble/worldview narrowing/editorial controlの
# 双方が強く成立する記事を狙う、ユーザー指示原文)。
#
# 構造(先例: er014_output/four_type_observation_01/news/run_news_a2.py
# のResearch→Verification→Ledger構造、vfl01.build_researcher_prompt/
# build_verification_prompt + client.responses.create、web_search tool
# をそのまま再現。topicのみ本タスクのTopicへ差し替え):
#   research/ (fact_ledger_draft.json, fact_ledger_verification.json,
#              verified_fact_ledger_flat.json[VERIFIED факт一覧])
#   research/verified_fact_ledger.txt (VOICE_1_EVIDENCE/VOICE_2_EVIDENCE
#              タグ付きLedger本体、`voices_theme_personalized_news_01.py`
#              が読み込む正本)
#
# 2段階実行(先例: ai_screening_ledger_trial_01の多段Perplexity構成とは
# 異なり、本タスクは標準Research→Verificationを1回だけ行うが、B-Family
# Voicesが要求するVOICE_n_EVIDENCEタグ付与は、実際にVERIFIEDされた
# factの内容を人間/Fableが読んでから対応表(FACT_VOICE_ASSIGNMENT)を
# 書く必要があるため、以下の2段階で実行する):
#   Phase 1: `python run_voices_2v_b1.py research` — Researcher+
#            Verificationのみ実行し、research/配下へ保存してSTOPする
#            (Writerは呼ばない)。
#   Phase 2: `python run_voices_2v_b1.py write` — Phase 1の成果物と
#            `voices_theme_personalized_news_01.py`のFACT_VOICE_
#            ASSIGNMENT(Phase 1結果を見て人手/Fableが追記した対応表)を
#            読み、VOICE_n_EVIDENCEタグ付きLedgerを組み立てたうえで、
#            2V正式Production Writer入口
#            (er012_b_family_voices_writer_generic_01.run_writer_stage_
#            generic()、voice_cards=2)を呼ぶ。TTSは一切呼ばない。
#
# 費用上限: BUDGET_JPY(既定150円)。Phase 1完了時点で既にBUDGET_JPYの
# 大半を消費している場合、Phase 2実行前にコンソールへ警告を出す
# (Writer実行自体は分割不可のため、事前警告のみ)。
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er012_b_family_voices_writer_generic_01 as writer_generic

THEME_ID = "voices_2v_personalized_news_open151"
BASE_DIR = "er014_output/four_type_observation_01/voices"
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"
OUT_DIR_BASE = f"{BASE_DIR}/b1_2v_new_theme"

TOPIC_ID = "is_personalized_news_good_for_us"
BUDGET_JPY = 150.0

# ユーザー指示原文のTopic+狙いを、そのままResearcher/Writer両方へ渡す
# topic文として使う(Sonnet自身の知識で事実を補わない。Ledgerの事実は
# web_search由来のVERIFIED[CONFIRMED]のみ)。
TOPIC_EN = (
    "Current topic: is personalized news good for us? Many news apps, social "
    "platforms, and search engines now use algorithms to personalize the news "
    "people see, based on their past clicks, interests, and behavior. Aim: cover "
    "this topic in a way that makes both sides strongly true at once, not a "
    "simple good-vs-bad framing. On one side, personalization makes news "
    "consumption more convenient and relevant: it saves people time, surfaces "
    "stories that match their actual interests, and helps people cut through "
    "information overload. On the other side, personalization raises real "
    "concerns: filter bubbles (seeing mostly information that confirms existing "
    "views), worldview narrowing (a shrinking, self-reinforcing range of "
    "perspectives and topics over time), and editorial control shifting from "
    "human editors to opaque ranking algorithms with commercial incentives. "
    "Use only facts confirmed by web search (no invented details, no facts "
    "supplied from the assistant's own prior knowledge)."
)

TOPIC_JA = (
    "2026年9月時点、多くのニュースアプリ・SNS・検索エンジンが、利用者の"
    "過去のクリック・興味・行動履歴に基づいてニュースをパーソナライズする"
    "アルゴリズムを使っている。この記事の中心テーマは、パーソナライズされた"
    "ニュースが良いか悪いかを単純などちらか一方に決めることではなく、"
    "両方の側面が同時に強く成立することを描くことである。一方で、"
    "パーソナライズは情報取得を便利・関連性の高いものにする(時間の節約、"
    "自分の興味に合った記事の表示、情報過多からの解放)。他方で、"
    "パーソナライズはfilter bubble(既存の考えを裏付ける情報ばかりを"
    "見ること)、worldview narrowing(視野・話題の範囲が時間とともに"
    "自己強化的に狭まっていくこと)、editorial control(人間の編集者から"
    "商業的インセンティブを持つ不透明なランキングアルゴリズムへ編集権限が"
    "移ること)という現実の懸念も引き起こす。"
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


# ============================================================
# Research / Verification(先例: run_news_a2.py::run_researcher_for_topic/
# run_verification_for_topicと同一のclient呼び出し構造。topicのみ差し替え)。
# ============================================================
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
    counts = {"VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0}
    for fact in ledger_parsed["facts"]:
        v = verdict_map.get(fact["fact_id"])
        verdict = v["verdict"] if v else "AMBIGUOUS"
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict != "VERIFIED":
            continue
        kept_facts.append({**fact, "verification_verdict": verdict, "verification_notes": v["verification_notes"]})

    structured = {"topic": TOPIC_EN, "topic_id": TOPIC_ID, "kept_facts": kept_facts, "counts": counts,
                  "note": "CONFIRMED(VERIFIED)のみ採用。AMBIGUOUS/REJECTEDはfact_ledger_verification.json"
                          "に記録済みだが本Ledgerからは除外した。"}
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)

    cost = cost_so_far_jpy()
    print(f"[{THEME_ID}] Phase 1(Research+Verification)完了。CONFIRMED(VERIFIED)="
          f"{counts.get('VERIFIED', 0)}件、AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件、"
          f"REJECTED={counts.get('REJECTED', 0)}件。費用実測(累計): ¥{cost:.2f}")
    for f_ in kept_facts:
        print(f"  - {f_['fact_id']}: {f_['claim'][:140]}")
    return structured


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "research"
    if mode == "research":
        phase1_research()
    elif mode == "write":
        import voices_theme_personalized_news_01 as theme_mod  # Phase 2でのみ必要(Phase 1後に作成)
        started_at = datetime.now(timezone.utc).isoformat()
        cl.install(LOG_PATH)
        cost_before_writer = cost_so_far_jpy()
        if cost_before_writer >= BUDGET_JPY:
            print(f"[{THEME_ID}] STOP_BUDGET_EXCEEDED: Phase 1完了時点で費用実測(累計)¥{cost_before_writer:.2f}"
                  f"がBUDGET_JPY=¥{BUDGET_JPY:.2f}に到達/超過したため、Writerを実行せずSTOPします。")
            sys.exit(1)
        print(f"[{THEME_ID}] Phase 2(Writer)開始。Phase 1完了時点の費用実測(累計)=¥{cost_before_writer:.2f}、"
              f"残り予算=¥{BUDGET_JPY - cost_before_writer:.2f}")
        result = writer_generic.run_writer_stage_generic(theme_mod.THEME_CONFIG, OUT_DIR_BASE, label="B1B")
        cost_after_writer = cost_so_far_jpy()
        summary = {
            "status": result.get("status"), "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "cost_jpy_after_research": cost_before_writer, "cost_jpy_final": cost_after_writer,
            "budget_jpy": BUDGET_JPY, "budget_exceeded": cost_after_writer > BUDGET_JPY,
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] Phase 2完了。status={result.get('status')} 費用実測(最終)=¥{cost_after_writer:.2f}")
    else:
        raise SystemExit(f"unknown mode: {mode} (research|write)")
