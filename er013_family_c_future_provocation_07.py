# ============================================================
# er013_family_c_future_provocation_07.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07
# ============================================================
# 目的: v6(絶対点6軸スコアで1件選定)を、複数スケール/レンズからの
# 候補生成 + 相対比較・強制ランキングへ再設計する。
#
# 5つのスケール/レンズ:
#   A_intimate      : 一人・一家族の日常/感情/選択/関係性が変わる未来
#   B_societal      : 仕事/教育/法律/住宅/家族制度/経済などのルールが変わる未来
#   C_radical       : 現在の生活概念・常識そのものが崩れる未来
#   D_second_order  : その技術が完全に普通になった後の二次・三次変化(並立評価レンズ)
#   E_inversion     : 便利さ・メリットの成功そのものが新しい問題を生む未来(並立評価レンズ)
# D/EはA/B/Cへの制約ではなく、有望ならA/B/Cと組み合わせてもよい
# (combined_withフィールドで示す)。ただし組合せを網羅的に生成しない。
#
# 評価は「相対比較・強制ランキング」を主手段にする(前回Trial-06は絶対点
# 6軸合計が16〜18点に集中し判別力がなかったため)。v6の6軸絶対点は
# reference_six_axis_scoresとして残すが、選定根拠にはしない(コードは
# ランキング結果のみから代表案を決定的に計算する)。
#
# 既存er013_family_c_future_*_01〜06.pyは一切編集しない(新規ファイル)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json

SCALES = ["A_intimate", "B_societal", "C_radical"]
LENSES = ["D_second_order", "E_inversion"]
ALL_SCALE_LENS = SCALES + LENSES

SCALE_LENS_DEFINITIONS = {
    "A_intimate": (
        "Intimate Future -- one person or one family's daily life, emotions, choices, "
        "and relationships change. Example seed: 'What if a robot understood your own "
        "daily life better than you do?'"
    ),
    "B_societal": (
        "Societal Future -- society-wide rules change: work, education, law, housing, "
        "family structure, the economy. Example seed: 'When home robots become "
        "completely normal, will the ability to do housework stop being counted as a "
        "life skill?'"
    ),
    "C_radical": (
        "Radical Future -- today's basic concept of daily life or common sense itself "
        "breaks down. Example seed: 'What if it is not the human who manages the "
        "house, but the house itself that autonomously runs a person's life?'"
    ),
    "D_second_order": (
        "Second-order Future (a parallel lens, not a constraint) -- the second- or "
        "third-order changes that happen only after the technology has become "
        "completely normal. Example seed: 'What happens 20 years after nobody has "
        "learned how to do housework anymore?'"
    ),
    "E_inversion": (
        "Inversion Future (a parallel lens, not a constraint) -- the success of the "
        "convenience/benefit itself becomes the new problem. Example seed: 'A robot "
        "understands a person so well that it starts prioritizing what is best for "
        "them over what they actually want.'"
    ),
}

SIX_AXES_REFERENCE = [
    "future_leap_score", "excitement_score", "tension_score",
    "thought_provoking_score", "distance_from_current_score", "evidence_connection_score",
]

# ------------------------------------------------------------
# Stage 1: 候補生成(スケール/レンズ別、相対比較のための素材)
# ------------------------------------------------------------
CANDIDATE_JSON_SCHEMA = {
    "name": "scale_lens_provocation_candidates",
    "schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "minItems": 9,
                "maxItems": 16,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "scale": {"type": "string", "enum": ALL_SCALE_LENS},
                        "combined_with": {"type": ["string", "null"], "enum": SCALES + [None]},
                        "premise": {"type": "string"},
                        "core_provocation": {"type": "string"},
                        "what_is_the_future": {"type": "string"},
                        "what_is_interesting": {"type": "string"},
                        "what_would_surprise_the_reader": {"type": "string"},
                        "what_happens_as_a_story": {"type": "string"},
                        "reference_six_axis_scores": {
                            "type": "object",
                            "properties": {axis: {"type": "integer"} for axis in SIX_AXES_REFERENCE},
                            "required": SIX_AXES_REFERENCE,
                            "additionalProperties": False,
                        },
                        "safety_boundary_note": {"type": "string"},
                    },
                    "required": [
                        "id", "scale", "combined_with", "premise", "core_provocation",
                        "what_is_the_future", "what_is_interesting", "what_would_surprise_the_reader",
                        "what_happens_as_a_story", "reference_six_axis_scores", "safety_boundary_note",
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

CANDIDATE_DEVELOPER_MESSAGE = (
    "You are a Core Provocation ideation specialist for an English-learning magazine's "
    "'Future' article family. Your only job here is to generate Core Provocation "
    "candidates across five different scales/lenses of imagined future, not to write "
    "the article itself. A Core Provocation is the single strongest central question "
    "that makes a reader think 'wait, what would actually happen if this became "
    "true?'. Do not default to the safest or most cautious idea -- aim for genuine "
    "excitement and tension in each scale, while keeping every idea inside a "
    "defensible safety boundary (an imagined future, clearly distinguishable from "
    "present fact, not a real prediction stated as fact). Do not make all candidates "
    "converge on the same underlying idea just told at different scales -- each scale "
    "should surface a genuinely different kind of future."
)

CANDIDATE_PROMPT_TEMPLATE = """[Theme]
{theme_label}

[Inspiration note -- an idea a human reader found genuinely exciting in an unrelated \
free-form draft. Use only the *thinking style* below as inspiration. Do not reuse its \
wording, and do not write about this exact idea if the theme above points elsewhere.]
{inspiration_note}

[Verified current-fact material -- background only, a guardrail for how far you may \
plausibly leap, not the subject of the article]
{ledger_context}

[Five scales/lenses -- generate candidates for ALL FIVE]
A_intimate: {def_a}
B_societal: {def_b}
C_radical: {def_c}
D_second_order (parallel lens): {def_d}
E_inversion (parallel lens): {def_e}

[Task]
Generate Core Provocation candidates about the theme above, distributed like this:
- 3 to 4 candidates with scale="A_intimate"
- 3 to 4 candidates with scale="B_societal"
- 3 to 4 candidates with scale="C_radical"
- 1 to 2 candidates with scale="D_second_order"
- 1 to 2 candidates with scale="E_inversion"

For a D_second_order or E_inversion candidate, you may optionally combine it with one
of A_intimate/B_societal/C_radical (set combined_with to that scale's id, e.g. a
D_second_order candidate combined with B_societal, or an E_inversion candidate
combined with A_intimate or C_radical). Do NOT generate every possible combination --
only combine when the combination is genuinely stronger than the lens alone. Otherwise
set combined_with to null.

For EACH candidate, write:
- id: a short id like "CP-A1", "CP-B2", "CP-D1"
- scale: one of the five scale/lens ids above
- combined_with: null, or one of A_intimate/B_societal/C_radical (only for D/E candidates)
- premise: 1-2 sentences describing a vivid, concrete Provocative Future Premise
- core_provocation: exactly ONE sentence -- the strongest central question this future
  situation raises for a reader
- what_is_the_future: 1 short sentence -- what, concretely, is different from today
- what_is_interesting: 1 short sentence -- why this is interesting, not just plausible
- what_would_surprise_the_reader: 1 short sentence -- the specific twist or turn a
  reader would not expect going in
- what_happens_as_a_story: 1-2 short sentences -- concretely, what kind of scene or
  event this would become if turned into a short story
- reference_six_axis_scores: six scores from 0 (none) to 3 (very strong) -- these are
  ONLY a secondary reference, NOT how you should decide which idea is best:
  future_leap_score, excitement_score, tension_score, thought_provoking_score,
  distance_from_current_score, evidence_connection_score
- safety_boundary_note: one sentence on why this stays inside a safety boundary (it
  must remain clearly an imagined future, not something stated as if it is already
  true today)

Do NOT select a single winner here -- that will be done separately, by relative
ranking across all candidates."""


def build_candidate_prompt(theme_label: str, inspiration_note: str, ledger_context: str) -> str:
    return CANDIDATE_PROMPT_TEMPLATE.format(
        theme_label=theme_label, inspiration_note=inspiration_note, ledger_context=ledger_context,
        def_a=SCALE_LENS_DEFINITIONS["A_intimate"], def_b=SCALE_LENS_DEFINITIONS["B_societal"],
        def_c=SCALE_LENS_DEFINITIONS["C_radical"], def_d=SCALE_LENS_DEFINITIONS["D_second_order"],
        def_e=SCALE_LENS_DEFINITIONS["E_inversion"],
    )


def generate_candidates(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **CANDIDATE_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": CANDIDATE_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Core Provocation候補生成(スケール/レンズ別)の応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id}


def build_score_table_reference(parsed: dict) -> list:
    """v6互換の参考6軸合計点表(選定根拠にはしない、記録用のみ)。"""
    rows = []
    for c in parsed.get("candidates", []):
        scores = c["reference_six_axis_scores"]
        total = sum(int(scores.get(axis, 0)) for axis in SIX_AXES_REFERENCE)
        rows.append({
            "id": c["id"], "scale": c["scale"], "combined_with": c.get("combined_with"),
            "core_provocation": c["core_provocation"],
            **{axis: scores.get(axis) for axis in SIX_AXES_REFERENCE},
            "reference_total_score": total,
        })
    return rows


# ------------------------------------------------------------
# Stage 2: 相対比較・強制ランキング(主評価手段)
# ------------------------------------------------------------
RANKING_JSON_SCHEMA = {
    "name": "core_provocation_forced_ranking",
    "schema": {
        "type": "object",
        "properties": {
            "ranking": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rank": {"type": "integer"},
                        "id": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["rank", "id", "reason"],
                    "additionalProperties": False,
                },
            },
            "extra_lens_recommendation": {
                "type": "object",
                "properties": {
                    "recommended": {"type": "boolean"},
                    "id": {"type": ["string", "null"]},
                    "reason": {"type": "string"},
                },
                "required": ["recommended", "id", "reason"],
                "additionalProperties": False,
            },
        },
        "required": ["ranking", "extra_lens_recommendation"],
        "additionalProperties": False,
    },
    "strict": True,
}

RANKING_DEVELOPER_MESSAGE = (
    "You are an independent judge comparing Core Provocation candidates against each "
    "other for the same theme. Do NOT score each candidate in isolation on an absolute "
    "scale. Instead, rank ALL candidates against each other from most to least "
    "interesting, exciting, and thought-provoking as the seed of a short story a real "
    "reader would want to read. Every candidate must get a distinct rank -- ties are "
    "not allowed, you must make a call even between close candidates. Judge on how "
    "genuinely surprising and story-worthy each idea is, not on how safe or plausible "
    "it is."
)

RANKING_PROMPT_TEMPLATE = """[Theme]
{theme_label}

[Candidates to rank against each other]
{candidate_summaries}

[Task]
1. Produce a strict, total ranking of ALL {n} candidates from 1 (most interesting) to
   {n} (least interesting). No ties. For each rank, give a short reason (1 sentence)
   comparing it to its neighbors in the ranking, not just describing the idea again.
2. Separately, judge extra_lens_recommendation: is there a D_second_order or
   E_inversion candidate that is CLEARLY stronger than the top-ranked A_intimate,
   B_societal, and C_radical candidates -- strong enough that it deserves a 4th
   article in addition to the three scales? If yes, recommended=true and id=that
   candidate's id. If no clearly strong case exists, recommended=false and id=null.
   Do not recommend an extra article by default -- only when it is clearly justified."""


def build_ranking_prompt(theme_label: str, candidates: list) -> str:
    lines = []
    for c in candidates:
        combo = f" (combined with {c['combined_with']})" if c.get("combined_with") else ""
        lines.append(
            f"- id={c['id']} scale={c['scale']}{combo}\n"
            f"  core_provocation: {c['core_provocation']}\n"
            f"  what_is_the_future: {c['what_is_the_future']}\n"
            f"  what_is_interesting: {c['what_is_interesting']}\n"
            f"  what_would_surprise_the_reader: {c['what_would_surprise_the_reader']}\n"
            f"  what_happens_as_a_story: {c['what_happens_as_a_story']}"
        )
    return RANKING_PROMPT_TEMPLATE.format(
        theme_label=theme_label, candidate_summaries="\n".join(lines), n=len(candidates))


def generate_ranking(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **RANKING_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": RANKING_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("強制ランキングの応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id}


def validate_ranking(ranking_parsed: dict, candidate_ids: list) -> None:
    """技術的検証(同順位禁止・全候補が1回ずつ登場するか)。違反は技術的失敗として扱う。"""
    ranking = ranking_parsed["ranking"]
    n = len(candidate_ids)
    if len(ranking) != n:
        raise RuntimeError(f"ランキング件数不一致: ranking={len(ranking)} candidates={n}")
    ranks = [r["rank"] for r in ranking]
    ids = [r["id"] for r in ranking]
    if sorted(ranks) != list(range(1, n + 1)):
        raise RuntimeError(f"ランキングに同順位または欠番があります: ranks={sorted(ranks)}")
    if sorted(ids) != sorted(candidate_ids):
        raise RuntimeError(f"ランキングのidが候補一覧と一致しません: ranking_ids={sorted(ids)} "
                            f"candidate_ids={sorted(candidate_ids)}")


def compute_representative_selection(candidates: list, ranking_parsed: dict) -> dict:
    """代表案選定(決定的計算、選定自体はLLMに委ねずコード側でランキング結果から
    機械的に算出する): A/B/Cは各スケール内で最上位(最小rank)を1件、D/Eは
    extra_lens_recommendation.recommended=Trueの場合のみ最大1件追加。"""
    rank_by_id = {r["id"]: r["rank"] for r in ranking_parsed["ranking"]}
    reason_by_id = {r["id"]: r["reason"] for r in ranking_parsed["ranking"]}
    candidates_by_id = {c["id"]: c for c in candidates}

    top_pick_by_scale = {}
    for scale in SCALES:
        scale_ids = [c["id"] for c in candidates if c["scale"] == scale]
        if not scale_ids:
            continue
        best_id = min(scale_ids, key=lambda cid: rank_by_id[cid])
        top_pick_by_scale[scale] = best_id

    extra = ranking_parsed["extra_lens_recommendation"]
    extra_lens_id = None
    if extra.get("recommended") and extra.get("id") and extra["id"] in candidates_by_id:
        candidate_scale = candidates_by_id[extra["id"]]["scale"]
        if candidate_scale in LENSES:
            extra_lens_id = extra["id"]

    return {
        "top_pick_by_scale": top_pick_by_scale,
        "top_pick_reason_by_scale": {s: reason_by_id[cid] for s, cid in top_pick_by_scale.items()},
        "extra_lens_included": extra_lens_id is not None,
        "extra_lens_id": extra_lens_id,
        "extra_lens_recommendation_raw": extra,
        "rank_by_id": rank_by_id,
        "reason_by_id": reason_by_id,
    }


def build_ranking_md(theme_label: str, candidates: list, ranking_parsed: dict, selection: dict) -> str:
    candidates_by_id = {c["id"]: c for c in candidates}
    lines = [f"# Core Provocation 相対ランキング -- {theme_label}\n",
             "| rank | id | scale | combined_with | core_provocation | reason |",
             "|---|---|---|---|---|---|"]
    for r in sorted(ranking_parsed["ranking"], key=lambda x: x["rank"]):
        c = candidates_by_id[r["id"]]
        lines.append(
            f"| {r['rank']} | {r['id']} | {c['scale']} | {c.get('combined_with') or ''} | "
            f"{c['core_provocation']} | {r['reason']} |")
    lines.append("\n## 代表案選定(決定的計算、ランキング結果のみから算出)\n")
    for scale, cid in selection["top_pick_by_scale"].items():
        c = candidates_by_id[cid]
        lines.append(f"- **{scale}** 採用: {cid}(rank {selection['rank_by_id'][cid]})\n"
                      f"  - core_provocation: {c['core_provocation']}\n"
                      f"  - 順位理由: {selection['reason_by_id'][cid]}\n")
    if selection["extra_lens_included"]:
        cid = selection["extra_lens_id"]
        c = candidates_by_id[cid]
        lines.append(f"- **追加レンズ** 採用: {cid}(scale={c['scale']}, "
                      f"combined_with={c.get('combined_with') or 'none'})\n"
                      f"  - core_provocation: {c['core_provocation']}\n"
                      f"  - 採用理由(LLM): {selection['extra_lens_recommendation_raw']['reason']}\n")
    else:
        lines.append(f"- 追加レンズ: 採用なし(理由: "
                      f"{selection['extra_lens_recommendation_raw']['reason']})\n")
    return "\n".join(lines)
