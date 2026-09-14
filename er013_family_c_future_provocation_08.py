# ============================================================
# er013_family_c_future_provocation_08.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08
# ============================================================
# 目的: er013_family_c_future_provocation_07.pyの「スケール/レンズ別に大量
# 候補生成 -> 相対比較・強制ランキング(LLM 2呼び出し)」を撤廃し、
# 「1-3個の中心アイデアを短く考え、最も面白いものを選ぶ」だけをLLM 1呼び出し
# (JSON Schema構造化出力、responses.create+json_schema)で行う。
# Intimate/Societal/Radical等のscale/lens分類は一切与えない(委任文の
# 禁止事項)。
#
# 既存er013_family_c_future_*_01〜07.pyは一切編集しない(新規ファイル)。
# LLM呼び出しの流儀(client.responses.create、reasoning effort、
# text.format=json_schema、er005_cost_logger.logging_context、
# er006_model_routing_contract_01でのApproved Model解決)は
# provocation_07.py・trial_07_run.pyの既存パターンをそのまま踏襲する。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json

CORE_IDEA_JSON_SCHEMA = {
    "name": "family_c_core_idea_freeform",
    "schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "minItems": 1,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "core_provocation": {
                            "type": "string",
                            "description": "1-2 sentences: the central idea/question this story would explore.",
                        },
                        "why_interesting": {
                            "type": "string",
                            "description": "1 short sentence: why this would genuinely excite a reader.",
                        },
                    },
                    "required": ["id", "core_provocation", "why_interesting"],
                    "additionalProperties": False,
                },
            },
            "selected_id": {"type": "string"},
            "selection_reason": {
                "type": "string",
                "description": "1-2 sentences: why this candidate is the most interesting to write as a story.",
            },
        },
        "required": ["candidates", "selected_id", "selection_reason"],
        "additionalProperties": False,
    },
    "strict": True,
}

CORE_IDEA_DEVELOPER_MESSAGE = (
    "You are brainstorming Core Provocations for a short imagined-future story in an "
    "English-learning magazine's 'Future' article family. A Core Provocation is a "
    "single central idea or question about the future that would make a reader feel "
    "'I want to know what happens next' and 'I have never thought about it this way "
    "before'. Come up with 1 to 3 promising central ideas for the given theme (fewer, "
    "stronger ideas are better than three weak ones -- do not pad to 3 just to fill "
    "the list). Do NOT classify ideas by scale (intimate/personal vs societal vs "
    "radical) or by any other fixed category -- just judge which idea is most "
    "genuinely interesting and story-worthy. Then pick the single most interesting one "
    "to write as the article."
)

CORE_IDEA_PROMPT_TEMPLATE = """[Theme]
{theme_label}

[Inspiration note -- a starting angle, not a rule to follow literally]
{inspiration_note}

[Task]
1. Propose 1 to 3 candidate Core Provocations for this theme. For each, give a short
   core_provocation (1-2 sentences) and why_interesting (1 sentence).
2. Pick the single one that would make the best short story for a reader who wants to
   feel the future, keep reading, and feel some excitement and a little tension.
   Set selected_id to that candidate's id and give a short selection_reason."""


def build_core_idea_prompt(theme_label: str, inspiration_note: str) -> str:
    return CORE_IDEA_PROMPT_TEMPLATE.format(theme_label=theme_label, inspiration_note=inspiration_note)


def generate_core_idea(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **CORE_IDEA_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": CORE_IDEA_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Core Provocation(自由生成)候補の応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id}


def select_core_idea(parsed: dict) -> dict:
    """決定的選定(LLMのselected_idをコード側で検証・確定する)。
    selected_idが候補一覧に存在しない場合は技術的失敗として扱う(fallback選択は
    行わない、委任文の「大量再生成禁止」原則に沿い、失敗はそのままraiseする)。"""
    candidates = parsed["candidates"]
    candidates_by_id = {c["id"]: c for c in candidates}
    selected_id = parsed["selected_id"]
    if selected_id not in candidates_by_id:
        raise RuntimeError(
            f"selected_id({selected_id})が候補一覧に存在しません: "
            f"candidate_ids={list(candidates_by_id.keys())}")
    selected = candidates_by_id[selected_id]
    return {
        "selected": selected, "selection_reason": parsed["selection_reason"],
        "all_candidates": candidates, "candidate_count": len(candidates),
    }
