# ============================================================
# er018_fiction_external_story_seed_trial_01.py
# 管理ID: FICTION-EXTERNAL-STORY-SEED-TRIAL-01
# ============================================================
# 目的: 完全創作方式(Story DNA / Coverage Run / Core Provocation、
# er018_fiction_story_dna_e_axis_redesign_01.py等)とは別に、実在する
# Public Domain / CC0 / 翻案可能ライセンスが確認できる外部ソース
# (実話・人生談/実話・歴史的逸話/日本文学(青空文庫)/世界文学
# (Gutenberg等))を出発点として、Seed化(抽象化・再構成)した英語学習用
# 短編を試作するTrial。
#
# Status: Trial専用、未承認draft実装(APPROVED_FOR_PRODUCTIONではない)。
# 到達上限: VALIDATED。Production Fiction仕様への反映は本タスクの対象外。
#
# 権利方針(委任文どおり、厳守):
# 「Web公開=自由利用」とは扱わない。PD/CC0/翻案可能な明確なライセンスを、
# ソース側の明記(Gutenberg/Standard Ebooks/Wikisource/青空文庫の著作権
# 表示、LOC "American Life Histories"のrights statement等)で確認し、
# URL・確認文言・確認日付を記録する。確認できない候補は採用しない。
# SNS/掲示板/Redditはアイデア発見用途までで投稿文を翻案素材にしない。
#
# 4系統: 01_life_history(LOC American Life Histories等) /
#        02_historical(実話・歴史的逸話、PD史料) /
#        03_japanese_lit(青空文庫、著作権なし) /
#        04_world_lit(Gutenberg/Standard Ebooks/Wikisource)
#
# 実行方法(root直下):
#   .venv/Scripts/python.exe er018_fiction_external_story_seed_trial_01.py \
#       --out-dir er018_output/fiction_external_story_seed_trial_01 \
#       --step search --budget-jpy 30
#   (Sonnetがcandidates.mdを読み、代表1件を選定 -> selection.jsonを手動作成)
#   ...--step verify   (requestsで実URL fetch。API課金なし)
#   (Sonnetがfetch結果を読み、rights_status確認文言をselection.jsonへ反映)
#   ...--step seed --budget-jpy 30     (系統ごと1 call、計4 call)
#   ...--step story --budget-jpy 30    (系統ごと1 call、計4 call)
#   ...--step assemble
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3  # extract_web_search_usage/extract_sources(read-only再利用)
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er003_v1_en_direct_vfl_01_generate as vfl01  # get_client()のみ再利用
import er018_fiction_story_dna_e_axis_redesign_01 as e_axis  # save_json等の共通ヘルパー再利用(read-only import)

load_dotenv()

THEME_TAG = "FICTION_EXTERNAL_STORY_SEED_TRIAL_01"
MODEL_LUNA = routing.WRITER_MODEL  # "gpt-5.6-luna"
USD_JPY = e_axis.USD_JPY  # 160.0(既存Trialと同一値)
PRICING_SNAPSHOT_PATH = e_axis.PRICING_SNAPSHOT_PATH

SYSTEMS = [
    {
        "key": "01_life_history",
        "label_en": "Real-life memoir / oral history",
        "label_ja": "実話・人生談",
        "search_hint": (
            "Search for candidates from the U.S. Library of Congress \"American Life "
            "Histories: Manuscripts from the Federal Writers' Project, 1936-1940\" "
            "(loc.gov), or comparable public-domain U.S. government oral-history / "
            "life-history archives. Prefer one ordinary person's concrete, specific "
            "life episode (not a famous person, not a general historical overview)."
        ),
    },
    {
        "key": "02_historical",
        "label_en": "Real historical anecdote",
        "label_ja": "実話・歴史的逸話",
        "search_hint": (
            "Search for a public-domain historical anecdote or oral-history account "
            "with a clear rights statement (e.g. a government archive, a Public-"
            "Domain-flagged history text on Wikisource/Internet Archive/Gutenberg, or "
            "a similarly explicit source). Prefer one small, concrete, human-scale "
            "incident (not a famous battle summary or textbook overview)."
        ),
    },
    {
        "key": "03_japanese_lit",
        "label_en": "Japanese literature (public domain)",
        "label_ja": "日本文学(青空文庫)",
        "search_hint": (
            "Search Aozora Bunko (aozora.gr.jp) for a short story or short episode "
            "from a work whose copyright status is explicitly marked \"著作権なし\" "
            "(author has been dead 70+ years). Prefer a short story or a short, self-"
            "contained episode from a longer work, centered on one concrete "
            "situation involving one or two people."
        ),
    },
    {
        "key": "04_world_lit",
        "label_en": "World literature (public domain)",
        "label_ja": "世界文学",
        "search_hint": (
            "Search Project Gutenberg (gutenberg.org), Standard Ebooks "
            "(standardebooks.org), or Wikisource for a short story, or a short self-"
            "contained episode from a longer public-domain work, with an explicit "
            "public-domain statement on the source page. Prefer one concrete "
            "situation involving one or two people, not a summary/overview of a "
            "whole novel."
        ),
    },
]

# ------------------------------------------------------------
# S-1 候補探索: web_search付きResponses API(低コンテキスト、
# max_tool_calls=3、系統ごとに1 call)
# ------------------------------------------------------------
SEARCH_CONTEXT_SIZE = "low"
SEARCH_MAX_TOOL_CALLS = 3

SEARCH_DEVELOPER_MESSAGE = (
    "You are a literary scout for an English-learning magazine's Fiction article "
    "family. You are looking for real, public-domain (or explicitly CC0 / freely "
    "adaptable-licensed) source material that could be abstracted into a short "
    "English-learning short story. You must NOT treat \"posted publicly on the "
    "web\" as equivalent to free-to-use. For every candidate, you must find and "
    "quote the source's OWN explicit rights statement (for example: a Project "
    "Gutenberg license header, a Standard Ebooks public-domain statement, an Aozora "
    "Bunko \"copyright: none\" notice, a Library of Congress rights statement, a "
    "Wikisource public-domain notice). If you cannot find and quote such a "
    "statement for a candidate, do not include it. Do not use social media, forum, "
    "or Reddit posts as adaptation material (only as idea-discovery leads, and if "
    "used that way, do not include them as a candidate here). Favor material that "
    "centers on one real person's concrete, specific situation or event -- this "
    "converts much better into a short story than a general overview or summary."
)

SEARCH_USER_TEMPLATE = """[Search system]
{label_en} ({label_ja})

[What to search for]
{search_hint}

[Task]
Find 3 to 5 real candidate source texts/episodes. For each candidate, give:
- title: a short descriptive title (your own words, not necessarily the source's own title)
- source_url: the exact URL of the page where you found the rights statement
- rights_status_quote: the exact quoted text from that page confirming the rights status
  (public domain / CC0 / explicitly adaptable). Quote it verbatim, in the language it
  appears in.
- rights_reasoning: 1 sentence, in English, on why this quote establishes the work is
  usable (e.g. "Aozora Bunko marks this author's copyright status as none, i.e. author
  died 70+ years ago").
- story_fit_reason: 1 sentence on why this would convert well into a short story
  centered on one person's concrete situation.
- concern: 1 short sentence on any concern (e.g. summary-only source, unclear author,
  needs more digging) or "none".
"""

CANDIDATES_JSON_SCHEMA = {
    "name": "fiction_external_story_seed_candidates",
    "schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "minItems": 3,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "source_url": {"type": "string"},
                        "rights_status_quote": {"type": "string"},
                        "rights_reasoning": {"type": "string"},
                        "story_fit_reason": {"type": "string"},
                        "concern": {"type": "string"},
                    },
                    "required": [
                        "title", "source_url", "rights_status_quote",
                        "rights_reasoning", "story_fit_reason", "concern",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["candidates"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_search_user_message(system: dict) -> str:
    return SEARCH_USER_TEMPLATE.format(
        label_en=system["label_en"], label_ja=system["label_ja"],
        search_hint=system["search_hint"],
    )


def call_search(client, system: dict, out_dir: str):
    stage = f"search_{system['key']}"
    user_message = build_search_user_message(system)
    kwargs = dict(
        model=MODEL_LUNA,
        reasoning={"effort": "medium"},
        input=[
            {"role": "developer", "content": SEARCH_DEVELOPER_MESSAGE},
            {"role": "user", "content": user_message},
        ],
        text={"format": {"type": "json_schema", **CANDIDATES_JSON_SCHEMA}},
        tools=[{"type": "web_search", "search_context_size": SEARCH_CONTEXT_SIZE}],
        max_tool_calls=SEARCH_MAX_TOOL_CALLS,
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    if response.model != MODEL_LUNA:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={MODEL_LUNA}, actual={response.model})")
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError(f"{stage}: 応答が空です")
    parsed = json.loads(text)
    meta = {
        "developer_message": SEARCH_DEVELOPER_MESSAGE,
        "user_message": user_message,
        "model": response.model,
        "response_id": response.id,
        "web_search_usage": r3.extract_web_search_usage(response),
        "sources": r3.extract_sources(response),
    }
    usage = getattr(response, "usage", None)
    if usage is not None:
        meta["usage"] = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    return parsed, meta


def step_search(out_dir: str, budget_jpy: float) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_search", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    for system in SYSTEMS:
        sys_dir = f"{out_dir}/stories/{system['key']}"
        parsed, meta = call_search(client, system, out_dir)
        e_axis.save_json(f"{sys_dir}/candidates.json", parsed)
        e_axis.save_json(f"{sys_dir}/search_api_meta.json", meta)

        lines = [f"# Candidates — {system['label_en']} ({system['label_ja']})\n",
                 "| 候補 | 出典URL | 権利状態(確認文言) | ストーリー化に向く理由 | 懸念 |",
                 "|---|---|---|---|---|"]
        for c in parsed["candidates"]:
            quote = c["rights_status_quote"].replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {c['title']} | {c['source_url']} | {quote} "
                f"({c['rights_reasoning']}) | {c['story_fit_reason']} | {c['concern']} |"
            )
        e_axis.save_text(f"{sys_dir}/candidates.md", "\n".join(lines) + "\n")
        print(f"[step_search][{system['key']}] DONE. candidates="
              f"{len(parsed['candidates'])} ws_calls="
              f"{meta['web_search_usage']['web_search_call_count']}")
        budget_guard(f"after_search_{system['key']}", out_dir, log_path, budget_jpy)

    print(f"[step_search] ALL DONE -> {out_dir}/stories/*/candidates.md")


# ------------------------------------------------------------
# S-2 代表選定(Sonnetが手動でselection.jsonを作成。ここではロード/検証のみ)
# ------------------------------------------------------------
def load_selection(out_dir: str, system_key: str) -> dict:
    path = f"{out_dir}/stories/{system_key}/selection.json"
    if not os.path.exists(path):
        raise SystemExit(
            f"{path}が存在しません。--step searchのcandidates.mdを読み、代表候補を"
            "1件選び、selection.jsonを手動作成してください。")
    return e_axis.load_json(path)


# ------------------------------------------------------------
# S-2 権利再検証: 実URLをrequestsでfetchし、確認文言が実際にページ内に
# 存在するかをローカル保存する(API課金なし)。最終判断(文言が本当に
# 一致しているか)はSonnetが目視で行う。
# ------------------------------------------------------------
def step_verify(out_dir: str) -> None:
    for system in SYSTEMS:
        selection = load_selection(out_dir, system["key"])
        url = selection["source_url"]
        sys_dir = f"{out_dir}/stories/{system['key']}"
        try:
            resp = requests.get(
                url, timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (research; eigo-radio fiction "
                                        "external story seed trial; non-commercial "
                                        "rights verification)"},
            )
            status = resp.status_code
            body = resp.text
        except Exception as exc:  # noqa: BLE001
            status = None
            body = f"FETCH_FAILED: {exc}"
        e_axis.save_text(f"{sys_dir}/rights_page_fetch.html", body)
        record = {
            "source_url": url,
            "http_status": status,
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "expected_quote": selection.get("rights_status_quote"),
            "quote_found_in_fetch": (
                bool(selection.get("rights_status_quote"))
                and _normalize(selection.get("rights_status_quote", "")) in _normalize(body)
            ),
        }
        e_axis.save_json(f"{sys_dir}/rights_verification.json", record)
        print(f"[step_verify][{system['key']}] status={status} "
              f"quote_found_in_fetch={record['quote_found_in_fetch']}")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------
# S-3 Story Seed化(系統ごと1 call、json_schema strict)
# ------------------------------------------------------------
SEED_DEVELOPER_MESSAGE = (
    "You help an English-learning magazine's Fiction team turn a real, rights-"
    "cleared source into a reusable \"Story Seed\": an abstraction that keeps only "
    "the elements needed to write a NEW short story, and explicitly discards "
    "everything else (names, era-specific detail, subplots). This is not a summary "
    "for readers -- it is an internal planning document. Do not quote long passages "
    "from the source; describe things in your own words."
)

SEED_USER_TEMPLATE = """[Source brief -- written by the editor, in their own words, not quoted from
the original]
{source_brief}

[Task -- produce a Story Seed]
1. original_summary: 3 to 5 sentences, in your own words, summarizing what actually
   happened/what the source is about.
2. seed_elements: up to 5 short bullet-style strings -- the elements worth keeping for
   a new story (character relationships, situation, turning point, emotional core).
   Keep this list tight; do not pad it to 5 if fewer capture it well.
3. discarded_elements: short strings -- proper names, era-specific details, or
   subplots that should NOT carry over into the new story.
4. conversion_plan: 2 to 4 sentences describing how to turn this into an English-
   learning short story: whether to modernize the setting, what setting to use,
   first-person or third-person, and roughly how long/what level."""

SEED_JSON_SCHEMA = {
    "name": "fiction_external_story_seed",
    "schema": {
        "type": "object",
        "properties": {
            "original_summary": {"type": "string"},
            "seed_elements": {
                "type": "array", "minItems": 2, "maxItems": 5,
                "items": {"type": "string"},
            },
            "discarded_elements": {
                "type": "array", "minItems": 1, "maxItems": 6,
                "items": {"type": "string"},
            },
            "conversion_plan": {"type": "string"},
        },
        "required": [
            "original_summary", "seed_elements", "discarded_elements",
            "conversion_plan",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}


def call_seed(client, system: dict, source_brief: str) -> dict:
    stage = f"seed_{system['key']}"
    user_message = SEED_USER_TEMPLATE.format(source_brief=source_brief)
    kwargs = dict(
        model=MODEL_LUNA,
        reasoning={"effort": "medium"},
        input=[
            {"role": "developer", "content": SEED_DEVELOPER_MESSAGE},
            {"role": "user", "content": user_message},
        ],
        text={"format": {"type": "json_schema", **SEED_JSON_SCHEMA}},
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    if response.model != MODEL_LUNA:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={MODEL_LUNA}, actual={response.model})")
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError(f"{stage}: 応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "user_message": user_message, "model": response.model,
            "response_id": response.id}


def step_seed(out_dir: str, budget_jpy: float) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_seed", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    for system in SYSTEMS:
        selection = load_selection(out_dir, system["key"])
        sys_dir = f"{out_dir}/stories/{system['key']}"
        result = call_seed(client, system, selection["source_brief"])
        seed = dict(result["parsed"])
        seed["rights_status"] = {
            "url": selection["source_url"],
            "confirmation_quote": selection["rights_status_quote"],
            "confirmed_date": selection["confirmed_date"],
        }
        e_axis.save_json(f"{sys_dir}/seed.json", seed)
        e_axis.save_json(f"{sys_dir}/seed_api_meta.json", {
            "developer_message": SEED_DEVELOPER_MESSAGE,
            "user_message": result["user_message"], "model": result["model"],
            "response_id": result["response_id"],
        })
        print(f"[step_seed][{system['key']}] DONE.")
        budget_guard(f"after_seed_{system['key']}", out_dir, log_path, budget_jpy)

    print("[step_seed] ALL DONE.")


# ------------------------------------------------------------
# S-4 Story本文生成(系統ごと1 call)。Writer developer message / 4共通原則 /
# [Characters] / [Length and level] / [Listening-friendliness]は
# er018_fiction_story_dna_e_axis_redesign_01.pyから逐語で流用し、
# [Core Provocation]の代わりに[Story Seed]を渡す(Story DNAブロックなし)。
# ------------------------------------------------------------
STORY_PROMPT_TEMPLATE = """[Story Seed -- inspired by a real, rights-cleared source, freely reimagined;
this is NOT a summary to reproduce, just raw material]
{seed_elements_block}

[How to convert it]
{conversion_plan}

[Common principles for this story family]
{common_principles}

[Your single job]
Write a short story inspired by the Story Seed above. Make a reader genuinely feel \
something, want to keep reading, and feel some excitement and a little tension along \
the way. Do not follow any fixed structure, fixed number of scenes, fixed number of \
emotional turns, or a fixed ending shape -- choose whatever narrative shape makes THIS \
Story Seed land most strongly. Do not just retell the original source; reimagine it \
as your own new short story.

[Characters -- keep it simple]
Use 1 or 2 characters as the core of the story; {max_characters} at the absolute most \
if truly needed. Only the main character (the protagonist) may be given a personal \
name. Every other person should be referred to through their relationship to the main \
character (for example: her mother, his father, her friend, their daughter, his \
neighbor) instead of a separate name. Do not add named characters that are not \
necessary for the story.

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary, \
simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text is about {word_target} words (roughly \
{range_low}-{range_high} words is fine).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear at each point whose perspective the reader/listener is in.

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""


def build_story_prompt(seed: dict) -> str:
    seed_elements_block = "\n".join(f"- {e}" for e in seed["seed_elements"])
    return STORY_PROMPT_TEMPLATE.format(
        seed_elements_block=seed_elements_block,
        conversion_plan=seed["conversion_plan"],
        common_principles=e_axis.COMMON_PRINCIPLES,
        max_characters=e_axis.MAX_CHARACTERS, word_target=e_axis.WORD_TARGET,
        range_low=e_axis.WORD_ACCEPTABLE_RANGE[0],
        range_high=e_axis.WORD_ACCEPTABLE_RANGE[1],
    )


def step_story(out_dir: str, budget_jpy: float) -> None:
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start_story", out_dir, log_path, budget_jpy)
    client = vfl01.get_client()

    for system in SYSTEMS:
        sys_dir = f"{out_dir}/stories/{system['key']}"
        seed = e_axis.load_json(f"{sys_dir}/seed.json")
        story_model = routing.require_model_or_override(
            "A2_WRITER", routing.WRITER_MODEL,
            override_reason="FICTION-EXTERNAL-STORY-SEED-TRIAL-01: 外部Public Domain "
                             "ソースをSeed化した短編生成にA2_WRITER Approved Model"
                             "(Luna)を転用(新規process未定義、コスト影響なし、"
                             "DEV/Trial限定)")
        prompt = build_story_prompt(seed)
        e_axis.save_text(f"{sys_dir}/story_prompt.txt", prompt)

        def _call():
            with cl.logging_context(THEME_TAG, f"story_{system['key']}"):
                return e_axis.generate_story(client, story_model, "high", prompt)

        story_result, attempts = e_axis.call_with_retry(_call, max_attempts=2)
        e_axis.save_text(f"{sys_dir}/story.md", story_result["raw_text"].strip() + "\n")
        e_axis.save_json(f"{sys_dir}/api_meta.json", {
            "model": story_result["model"], "response_id": story_result["response_id"],
            "effort": "high", "attempts": attempts,
        })
        word_count = len(story_result["raw_text"].split())
        print(f"[step_story][{system['key']}] DONE. word_count={word_count} "
              f"model={story_result['model']}")
        budget_guard(f"after_story_{system['key']}", out_dir, log_path, budget_jpy)

    print("[step_story] ALL DONE.")


# ------------------------------------------------------------
# 費用計算(Luna token費用 + web_search_callツール費用)
# ------------------------------------------------------------
def load_pricing() -> dict:
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)
    prices = {}
    ws_price = None
    for entry in snapshot["prices"]:
        if entry.get("model") == "gpt-5.6-luna":
            prices[entry["meter"]] = entry["price"]
        if entry.get("meter") == "web_search_call":
            ws_price = entry["price"]
    prices["web_search_call"] = ws_price
    return prices


def compute_cost_jpy(log_path: str) -> dict:
    if not os.path.exists(log_path):
        return {"total_usd": 0.0, "total_jpy": 0.0, "record_count": 0}
    pricing = load_pricing()
    total_usd = 0.0
    record_count = 0
    ws_call_total = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("theme") != THEME_TAG:
                continue
            record_count += 1
            if not rec.get("success", True):
                continue
            ws_calls = rec.get("web_search_call_count") or 0
            ws_call_total += ws_calls
            total_usd += (ws_calls / 1000) * pricing["web_search_call"]
            if rec.get("model_id") != "gpt-5.6-luna":
                continue
            input_tokens = rec.get("input_tokens") or 0
            cached = rec.get("cached_input_tokens") or 0
            output_tokens = rec.get("output_tokens") or 0
            non_cached_input = max(input_tokens - cached, 0)
            total_usd += (non_cached_input / 1_000_000) * pricing["input_tokens"]
            total_usd += (cached / 1_000_000) * pricing["cached_input_tokens"]
            total_usd += (output_tokens / 1_000_000) * pricing["output_tokens"]
    return {
        "total_usd": round(total_usd, 6), "total_jpy": round(total_usd * USD_JPY, 2),
        "record_count": record_count, "web_search_call_total": ws_call_total,
    }


def budget_guard(stage_label: str, out_dir: str, log_path: str, hard_cap_jpy: float) -> dict:
    cost = compute_cost_jpy(log_path)
    print(f"[budget_guard][{stage_label}] 累計={cost['total_jpy']} JPY (上限{hard_cap_jpy})")
    if cost["total_jpy"] > hard_cap_jpy:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] 累計{cost['total_jpy']} JPYが上限"
            f"{hard_cap_jpy} JPYを超過しました。STOP(以降のAPI呼び出しは行わない)。")
    return cost


# ------------------------------------------------------------
# Step: assemble
# ------------------------------------------------------------
def step_assemble(out_dir: str) -> None:
    parts = [
        "# FICTION-EXTERNAL-STORY-SEED-TRIAL-01 -- stories_all.md\n",
        "Trial専用、Production採用ではない。最大Status: VALIDATED。\n",
    ]
    for system in SYSTEMS:
        sys_dir = f"{out_dir}/stories/{system['key']}"
        selection = load_selection(out_dir, system["key"])
        seed = e_axis.load_json(f"{sys_dir}/seed.json")
        story = e_axis.load_text(f"{sys_dir}/story.md")
        parts.append(f"\n## {system['label_en']} ({system['label_ja']})\n")
        parts.append(f"**Source**: {selection['title']} -- {selection['source_url']}\n")
        parts.append(f"**Rights**: {seed['rights_status']['confirmation_quote']} "
                      f"(confirmed {seed['rights_status']['confirmed_date']})\n")
        parts.append(f"**Seed elements**: {'; '.join(seed['seed_elements'])}\n")
        parts.append("```\n" + story.strip() + "\n```\n")
    e_axis.save_text(f"{out_dir}/stories_all.md", "\n".join(parts))

    log_path = f"{out_dir}/raw_usage_log.jsonl"
    final_cost = compute_cost_jpy(log_path)
    e_axis.save_json(f"{out_dir}/cost.json", final_cost)
    print(f"[step_assemble] DONE -> {out_dir}/stories_all.md, cost={final_cost}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["search", "verify", "seed", "story", "assemble"])
    parser.add_argument("--budget-jpy", type=float, default=30.0)
    args = parser.parse_args()

    if args.step == "search":
        step_search(args.out_dir, args.budget_jpy)
    elif args.step == "verify":
        step_verify(args.out_dir)
    elif args.step == "seed":
        step_seed(args.out_dir, args.budget_jpy)
    elif args.step == "story":
        step_story(args.out_dir, args.budget_jpy)
    elif args.step == "assemble":
        step_assemble(args.out_dir)


if __name__ == "__main__":
    main()
