#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-DIAGNOSTIC-FULL-RETRY-MODULES-12

Diagnostic Full Retry の診断生成ロジック（LLM不要、既存overlap dataのみ使用）
をProduction pathで再利用可能なmoduleとして提供。

er003_v1_n3_01_articles_generate.py など、本体scripts から import して使用。
"""

from __future__ import annotations

# ============================================================
# Diagnosis: 追加LLM呼び出しをせず、overlap_qa.flag_possible_paraphrase()
# が既に返しているshared_wordsだけから、重複の性質を簡易分類する。
# ============================================================

_EVIDENCE_WORDS = frozenset({
    "study", "studies", "survey", "surveys", "report", "reports", "research",
    "said", "says", "percent", "popmenu", "rutgers", "researchers", "data",
})

_IMPLICATION_WORDS = frozenset({
    "pressure", "feel", "feels", "feeling", "choice", "choices", "choose",
    "people", "customer", "customers", "worker", "workers", "guilty", "guilt",
})

_CAUSE_WORDS = frozenset({
    "because", "causes", "caused", "cause", "result", "results",
})


def classify_overlap(shared_words: list) -> str:
    """Overlap typeの簡易分類"""
    s = set(shared_words)
    tags = []
    if s & _EVIDENCE_WORDS:
        tags.append("duplicated evidence/source reference (the same study or survey is "
                     "restated in both places)")
    if s & _IMPLICATION_WORDS:
        tags.append("duplicated implication/consequence (the same reaction, pressure, or "
                     "choice is described in both places)")
    if s & _CAUSE_WORDS:
        tags.append("duplicated cause-and-effect framing")
    if not tags:
        tags.append("generic semantic restatement of the Full Story's core logic")
    return "; ".join(tags)


def compose_diagnosis(overlap_result: dict) -> str:
    """Overlap resultから診断テキストを構成"""
    shared = overlap_result["shared_words"]
    shown = shared[:12]
    more = "" if len(shared) <= 12 else f" (+{len(shared) - 12} more)"
    return (f"shared content words with the Full Story: {', '.join(shown)}{more}. "
            f"Likely overlap type: {classify_overlap(shared)}.")


DIAGNOSTIC_SECTION_TEMPLATE = """[Previous attempt — NG example of semantic overlap, do NOT patch \
or reuse]
The following was a previous attempt at this same script. It failed an automatic Point-overlap \
check: Point One and/or Point Two repeated meaning that was already in the Full Story, instead of \
each going deeper in a distinct way. Read it ONLY to understand what NOT to repeat — it is a \
failure example, not a draft to edit.

Previous Full Story:
{previous_full_story}

Previous Point One (overlap_ratio={point_one_score}, flagged={point_one_flagged}):
{previous_point_one}
Diagnosis: {diagnosis_one}

Previous Point Two (overlap_ratio={point_two_score}, flagged={point_two_flagged}):
{previous_point_two}
Diagnosis: {diagnosis_two}

Rules for this new attempt:
- Do not patch the previous story.
- Do not rewrite only Point One or Point Two.
- Do not merely paraphrase the failed Points.
- Regenerate the entire story from the Ledger.
- Preserve Storytelling First.
- Preserve No Jargon.
- Create two clearly distinct listener takeaways.
- Use the previous attempt only as an NG example of semantic overlap that must not be repeated."""


def build_diagnostic_section(previous_article_text: str, point_one_overlap: dict,
                              point_two_overlap: dict) -> str:
    """Diagnostic section を構成する"""
    diagnosis_one = compose_diagnosis(point_one_overlap)
    diagnosis_two = compose_diagnosis(point_two_overlap)

    return DIAGNOSTIC_SECTION_TEMPLATE.format(
        previous_full_story=previous_article_text,
        point_one_score=point_one_overlap["overlap_ratio"],
        point_one_flagged=point_one_overlap["flagged"],
        previous_point_one="(Point One body from previous attempt)",
        diagnosis_one=diagnosis_one,
        point_two_score=point_two_overlap["overlap_ratio"],
        point_two_flagged=point_two_overlap["flagged"],
        previous_point_two="(Point Two body from previous attempt)",
        diagnosis_two=diagnosis_two,
    ), {
        "diagnosis_one": diagnosis_one,
        "diagnosis_two": diagnosis_two,
    }
