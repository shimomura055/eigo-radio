# ============================================================
# er002_editorial_angle_adapter.py
# ER-002-v1.1A: 編集アングル生成アダプター
# ============================================================
# 既存OpenAI台本生成モデル(er002_script_adapter.MODEL_WRITE)を使い、
# 1回の構造化出力で3案の編集アングル候補を生成する。この呼び出しは
# 生成のみを行い、採点・合否判定は一切行わない(評価は別モデル・別呼び出し
# のer002_editorial_common.classify_angle_evaluationが担う)。
#
# 記事ごとの専用プロンプトを作らない: テンプレート自体は完全に共通で、
# 記事固有の情報は{topic}/{facts_block}という差し込み穴だけに限定する。

from __future__ import annotations

import hashlib
import json
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

import er002_editorial_common as ec
import er002_script_adapter as script_adapter

MODEL_ROLE = ec.ANGLE_GENERATION_MODEL_ROLE
MODEL_NAME = script_adapter.MODEL_WRITE  # 既存OpenAI台本生成モデルを流用(責務分離ルール)
PROMPT_VERSION = "er002-editorial-angle-adapter-v1"

ANGLE_GENERATION_PROMPT_TEMPLATE = """You are an editorial strategist for a short English-language audio news segment for Japanese learners of English. You are NOT writing the script yet - you are proposing THREE DIFFERENT editorial angles for how the story could be told.

TOPIC:
{topic}

VERIFIED FACTS (each has a stable ID; you may ONLY cite these IDs, never invent new facts, and never cite background/context information as if it were a verified fact):
{facts_block}

Propose exactly 3 DIFFERENT editorial angles. Each angle must:
- Use only the VERIFIED FACTS above (cite them by ID in every field that requires fact IDs)
- Choose an opening_mode from exactly these four values: "verified_event", "hypothetical", "direct_question", "contrast"
  - If opening_mode is "hypothetical", you MUST set hypothetical_disclosure_required to true (the eventual script must clearly signal to the listener that this is a hypothetical, not a reported fact)
  - If opening_mode is "verified_event" or "contrast", opening_fact_ids must NOT be empty (the opening must be grounded in a specific cited fact)
- Assign point_one_editorial_role and point_two_editorial_role from exactly these six values: "cause_explanation", "consequence_or_stakes", "counterpoint_or_tension", "human_or_concrete_detail", "context_or_comparison", "mechanism_or_process"
  - point_one_editorial_role and point_two_editorial_role MUST be different values
  - point_one_core_claim and point_two_core_claim MUST be substantively different claims (not the same idea reworded)
- List unsupported_assumptions honestly: if the angle relies on ANY inference not directly stated in the VERIFIED FACTS, list it here (an empty list is only correct if there are truly zero such assumptions)

The 3 angles MUST be genuinely different from each other, not the same angle reworded in different language:
- central_tension_or_question must differ substantively across all 3
- the (point_one_editorial_role, point_two_editorial_role) combination must differ across all 3
- non_obvious_takeaway must differ substantively across all 3

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "candidates": [
    {{
      "angle_id": "angle_1",
      "listener_relevance": "...",
      "central_tension_or_question": "...",
      "concrete_opening": "...",
      "opening_mode": "verified_event",
      "opening_fact_ids": ["F01"],
      "hypothetical_disclosure_required": false,
      "non_obvious_takeaway": "...",
      "point_one_editorial_role": "cause_explanation",
      "point_one_core_claim": "...",
      "point_one_fact_ids": ["F02"],
      "point_two_editorial_role": "consequence_or_stakes",
      "point_two_core_claim": "...",
      "point_two_fact_ids": ["F03"],
      "listener_payoff": "...",
      "in_one_line_target": "...",
      "fact_support_map": [{{"fact_id": "F01", "used_for": "..."}}],
      "unsupported_assumptions": []
    }},
    {{ "angle_id": "angle_2", ... same shape ... }},
    {{ "angle_id": "angle_3", ... same shape ... }}
  ]
}}"""


def sha256_text(text: str) -> str:
    return ec.sha256_text(text)


def build_facts_block(fact_id_map: dict) -> str:
    return "\n".join(f"{fid}: {text}" for fid, text in fact_id_map.items())


def build_prompt(topic: str, fact_id_map: dict) -> str:
    return ANGLE_GENERATION_PROMPT_TEMPLATE.format(topic=topic, facts_block=build_facts_block(fact_id_map))


def parse_angle_generation_response(raw_text: str) -> list[dict]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    parsed = json.loads(cleaned.strip())
    candidates = parsed.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        raise ValueError(f"アングル生成応答のcandidatesが3件のリストではありません: {candidates!r}")
    return candidates


def make_angle_generation_fn(article_id: str, topic: str, fact_id_map: dict, client: Optional[OpenAI] = None):
    """呼び出すたびに新規の3案を生成するangle_generation_fn(config)->list[dict]を
    返す。生成のみを行い、採点はしない(責務分離)。"""
    if client is None:
        load_dotenv()
        client = OpenAI()

    prompt = build_prompt(topic, fact_id_map)
    prompt_sha256 = sha256_text(prompt)

    def angle_generation_fn(config: dict) -> list[dict]:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        candidates = parse_angle_generation_response(response.choices[0].message.content)
        for c in candidates:
            c["article_id"] = article_id
        return candidates

    angle_generation_fn.prompt_text = prompt
    angle_generation_fn.prompt_sha256 = prompt_sha256
    angle_generation_fn.prompt_version = PROMPT_VERSION
    angle_generation_fn.model = MODEL_NAME
    angle_generation_fn.model_role = MODEL_ROLE
    return angle_generation_fn
