# ============================================================
# er002_topic_adapter.py
# ER-002-S3-P0: トピック取得・採点プロンプト(バージョン管理・凍結用)
# ============================================================
# ER-002-S2-P2で実行したMeta技術記事の調査で使ったリサーチプロンプトを、
# ジャンルを差し込み可能な共通テンプレートへ一般化したもの。
# 「記事ごとの専用プロンプトを作らない」という方針(er002_script_adapter.py
# と同じ)を踏襲し、ジャンル名以外の記事固有情報はテンプレートへ書き込まない。
#
# このモジュールは実APIを呼び出す関数の定義のみを提供し、ER-002-S3-P0の
# 時点では実行していない(non-scope: 実トピック取得)。

from __future__ import annotations

import hashlib
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

MODEL_SEARCH = "gpt-5.6-luna"  # gather_topic.py / generate_test.pyのMODEL_PLANと同じ格
PROMPT_VERSION = "er002-topic-adapter-v1"

TOPIC_RESEARCH_PROMPT_TEMPLATE = """You are a news researcher for a Japanese English-learning podcast, gathering candidate stories in the {genre_label} genre.
Today is {today}.

Search the web for recent {genre_label_lower} news (prioritize the last 7 days).

Find exactly 3 CANDIDATE stories that each satisfy ALL of these conditions:
- A recent, concrete event or announcement (not a broad ongoing trend with no single anchor event)
- NOT breaking news still developing, NOT rumor, NOT leak/unconfirmed report
- Meaningful to a general listener (not a niche insider-only topic)
- Fully understandable by EAR ALONE (no chart/screenshot/table reference needed)
- Can naturally split into TWO distinct discussion points (not one flat idea repeated twice)
- Does not require referencing any image, chart, or screen
- Not overloaded with jargon or an excessive number of proper nouns/technical terms
- Major facts are confirmed by MULTIPLE independent reliable sources
- Includes primary-source information where possible (official statement, press release, filing, etc.), not just secondhand commentary

For each of the 3 candidates, gather from AT LEAST 3 independent, reputable sources where possible and report:
- A one-sentence description of the story
- For each source: outlet name, paraphrased headline (never quote verbatim - this is a strict copyright requirement), paraphrased lead/gist, and publish date
- VERIFIED FACTS: numbers, dates, names, outcomes explicitly confirmed by at least one source
- Whether this is primary-source information (official statement/filing/press release) or secondhand reporting
- A brief note on how this story could naturally split into two distinct discussion points

Then, for EACH candidate, score it 1-5 (5=best) on these EXACT six criteria, with a one-line justification for each score:
1. clear_hook: does it have an attention-grabbing angle?
2. two_point_fit: does it naturally split into two clearly different discussion points?
3. general_user_impact: how much does this affect or interest an ordinary listener (not just industry insiders)?
4. audio_only_comprehensibility: how well can this be explained with words alone, no visuals?
5. source_reliability: how reliable/reputable are the confirming sources?
6. fact_stability: how unlikely are the core facts to change, be retracted, or turn out wrong?

Write your findings in plain text under these exact headings, repeated for each of the 3 candidates:

## CANDIDATE 1
### DESCRIPTION
### SOURCES
(one per line: "Outlet: paraphrased headline (date) - paraphrased gist")
### VERIFIED FACTS
### PRIMARY SOURCE PRESENT
(yes/no, and what it is)
### TWO POINT SPLIT NOTE
### SCORES
clear_hook: X - reason
two_point_fit: X - reason
general_user_impact: X - reason
audio_only_comprehensibility: X - reason
source_reliability: X - reason
fact_stability: X - reason

## CANDIDATE 2
(same structure)

## CANDIDATE 3
(same structure)
"""

GENRE_LABELS = {
    "sports": "SPORTS",
    "social_life": "SOCIAL / EVERYDAY LIFE",
    "entertainment": "ENTERTAINMENT",
    "technology": "TECHNOLOGY",
    "business_consumer": "BUSINESS & CONSUMER TRENDS",
    "politics_public": "POLITICS / PUBLIC AFFAIRS",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_research_prompt(genre: str, today: str) -> str:
    genre_label = GENRE_LABELS.get(genre, genre.upper())
    return TOPIC_RESEARCH_PROMPT_TEMPLATE.format(
        genre_label=genre_label, genre_label_lower=genre_label.lower(), today=today,
    )


def make_topic_research_fn(genre: str, client: Optional[OpenAI] = None):
    """genreを固定した「調査を実行する関数」を返す(呼び出すまで実APIは叩かない)。
    実際の実行はER-002-S3-P0の非対象範囲であり、ここでは定義のみ提供する。"""
    if client is None:
        load_dotenv()
        client = OpenAI()

    def research_fn(today: str) -> str:
        prompt = build_research_prompt(genre, today)
        response = client.responses.create(
            model=MODEL_SEARCH,
            input=prompt,
            tools=[{"type": "web_search"}],
        )
        return response.output_text.strip()

    research_fn.prompt_version = PROMPT_VERSION
    research_fn.genre = genre
    return research_fn
