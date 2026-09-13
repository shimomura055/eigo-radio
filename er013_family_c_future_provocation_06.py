# ============================================================
# er013_family_c_future_provocation_06.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
# ============================================================
# 目的: 新原則「Provocative Future Premise -> Core Provocation -> Story ->
# Evidence / Safety Boundary Check」の最初の段階。記事本文を書く前に、
# Core Provocation候補を5〜10件生成し、6軸(Future Leap/Excitement/
# Tension/Thought-provokingness/現在実現済みとの距離/Evidenceとの
# 接続可能性)でスコア化し、LLM自身に「最も面白く、かつSafety boundary
# 内に置ける」候補を1つ選ばせる(一番安全な案を選ばせるのではない、と
# ユーザーが明示)。
#
# 既存er013_family_c_future_*_01〜05.pyは一切編集しない(新規ファイル)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json

CORE_PROVOCATION_JSON_SCHEMA = {
    "name": "core_provocation_candidates",
    "schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "minItems": 5,
                "maxItems": 10,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "premise": {"type": "string"},
                        "core_provocation": {"type": "string"},
                        "future_leap_score": {"type": "integer"},
                        "excitement_score": {"type": "integer"},
                        "tension_score": {"type": "integer"},
                        "thought_provoking_score": {"type": "integer"},
                        "distance_from_current_score": {"type": "integer"},
                        "evidence_connection_score": {"type": "integer"},
                        "safety_boundary_note": {"type": "string"},
                    },
                    "required": [
                        "id", "premise", "core_provocation", "future_leap_score",
                        "excitement_score", "tension_score", "thought_provoking_score",
                        "distance_from_current_score", "evidence_connection_score",
                        "safety_boundary_note",
                    ],
                    "additionalProperties": False,
                },
            },
            "selected_id": {"type": "string"},
            "selection_rationale": {"type": "string"},
        },
        "required": ["candidates", "selected_id", "selection_rationale"],
        "additionalProperties": False,
    },
    "strict": True,
}

PROVOCATION_DEVELOPER_MESSAGE = (
    "You are a Provocative Future Premise ideation specialist for an English-learning "
    "magazine. Your only job here is to generate Core Provocation candidates, not to "
    "write the article itself. A Core Provocation is the single strongest central "
    "question that makes a reader think 'wait, what would actually happen if this "
    "became true?'. Research and evidence are guardrails that define the boundary of "
    "the imagined future, not the main subject of the article. Do not pick the safest, "
    "most cautious idea by default -- pick for genuine excitement and tension, while "
    "still keeping each idea inside a defensible safety boundary (an imagined future, "
    "clearly distinguishable from present fact, not a real prediction stated as fact)."
)

PROVOCATION_PROMPT_TEMPLATE = """[Theme]
{theme_label}

[Inspiration note -- an idea a human reader found genuinely exciting in an unrelated \
free-form draft. Use only the *thinking style* below as inspiration. Do not reuse its \
wording, and do not write about this exact idea if the theme above points elsewhere.]
{inspiration_note}

[Verified current-fact material -- background only, a guardrail for how far you may \
plausibly leap, not the subject of the article]
{ledger_context}

[Task]
Generate {n_min} to {n_max} distinct Core Provocation candidates about the theme above.
For each candidate, write:
- id: a short id like "CP-01"
- premise: 1-2 sentences describing a Provocative Future Premise (a vivid, concrete
  future situation)
- core_provocation: exactly ONE sentence -- the strongest central question this future
  situation raises for a reader
- six scores from 0 (none) to 3 (very strong): future_leap_score (how far this is from
  something that ordinarily already happens today -- 0 means it is basically already
  happening, 3 means it is a genuine leap), excitement_score, tension_score,
  thought_provoking_score, distance_from_current_score (distance from what is already
  realized in the real world today), evidence_connection_score (how well this can still
  be connected to the verified current-fact material above as a plausible starting
  point, without being fact-checked itself)
- safety_boundary_note: one sentence on why this stays inside a safety boundary (it
  must remain clearly an imagined future, not something stated as if it is already true
  today)

Then choose exactly one candidate as selected_id, and explain in selection_rationale
why it is the single most interesting and thought-provoking choice that still stays
inside a safety boundary -- explicitly NOT simply the safest or most cautious option."""


def build_provocation_prompt(theme_label: str, inspiration_note: str, ledger_context: str,
                              n_min: int = 5, n_max: int = 10) -> str:
    return PROVOCATION_PROMPT_TEMPLATE.format(
        theme_label=theme_label, inspiration_note=inspiration_note,
        ledger_context=ledger_context, n_min=n_min, n_max=n_max)


def generate_core_provocation_candidates(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **CORE_PROVOCATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": PROVOCATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Core Provocation候補生成の応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id}


SIX_AXES = [
    "future_leap_score", "excitement_score", "tension_score",
    "thought_provoking_score", "distance_from_current_score", "evidence_connection_score",
]


def build_score_table(parsed: dict) -> list:
    """6軸スコア表(合計点を含む、決定的な集計のみ・追加API呼び出しなし)。"""
    rows = []
    for c in parsed.get("candidates", []):
        total = sum(int(c.get(axis, 0)) for axis in SIX_AXES)
        rows.append({
            "id": c["id"], "core_provocation": c["core_provocation"],
            **{axis: c.get(axis) for axis in SIX_AXES},
            "total_score": total,
            "is_selected": c["id"] == parsed.get("selected_id"),
        })
    return rows


def get_selected_candidate(parsed: dict) -> dict:
    selected_id = parsed.get("selected_id")
    for c in parsed.get("candidates", []):
        if c["id"] == selected_id:
            return c
    raise RuntimeError(f"selected_id '{selected_id}' が候補一覧に見つかりません(技術的失敗)")
