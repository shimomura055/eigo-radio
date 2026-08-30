#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-POINT-ROLE-VS-DIAGNOSTIC-RETRY-11: Experiment B (Diagnostic Full Retry)

仮説: Retry時に単なるOverlap scoreだけでなく、「何が重複していたか」
「前回のどこがNGだったか」を具体的にWriterへ返すことで、全文Retryの
成功率を改善できる。

変更点はRetry prompt / Retry routingのみ:
- Initial生成はExperiment Aとは無関係に、現行仕様(Trial-08のFULL_ARTICLE_
  PROMPT_TEMPLATE・schema)をそのまま使う。Point Role Planningは一切
  追加しない。
- NG時のみ、前回全文・Point One/Two overlap score・重複語(shared_words)
  から構成した簡易diagnosis(既存local checkerの出力のみを使用、追加LLM
  呼び出しは行わない)をRetry promptへ渡す。前回全文は「修正対象」では
  なく「NG例」として明示し、Point-only rewriteやparaphraseを禁止する
  文言を含める。

Retry上限はProduction仕様と同じPOINT_OVERLAP_ARTICLE_RETRY_MAX=2。
Storytelling First / No Jargon仕様は維持。WriterはRouting SSOT経由で
Lunaをfail-closedで使用する。Production本体・Ledger局所Rewriteパイプ
ライン・Hook-aware Checker・Audio再生成への配線は一切行わない
(DEV検証のみ)。
"""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_point_overlap_qa_18 as overlap_qa
import er009_n1_full_writer_ledger_integration_08 as trial08
import er009_n1_routing_governance_10_actual_model_cost as cost_calc

OUT_DIR = "er009_output/diagnostic_retry_11"
COST_LOG_PATH = f"{OUT_DIR}/cost_log.jsonl"
RESULTS_PATH = f"{OUT_DIR}/results.json"

os.makedirs(OUT_DIR, exist_ok=True)
cl.install(COST_LOG_PATH)

client = OpenAI()

WRITER_MODEL = routing.require_model("A2_WRITER", routing.WRITER_MODEL)

POINT_OVERLAP_ARTICLE_RETRY_MAX = 2
NUM_RUNS = 3

# ============================================================
# Diagnosis: 追加LLM呼び出しをせず、overlap_qa.flag_possible_paraphrase()
# が既に返しているshared_wordsだけから、重複の性質を簡易分類する。
# ============================================================
_EVIDENCE_WORDS = frozenset({
    "study", "studies", "survey", "surveys", "report", "reports", "research",
    "said", "says", "percent", "popmenu", "rutgers", "researchers",
})
_IMPLICATION_WORDS = frozenset({
    "pressure", "feel", "feels", "feeling", "choice", "choices", "choose",
    "people", "customer", "customers", "worker", "workers",
})
_CAUSE_WORDS = frozenset({"because", "causes", "caused", "cause", "result", "results"})


def classify_overlap(shared_words: list) -> str:
    s = set(shared_words)
    tags = []
    if s & _EVIDENCE_WORDS:
        tags.append("duplicated evidence/source reference (the same study or survey is restated "
                     "in both places)")
    if s & _IMPLICATION_WORDS:
        tags.append("duplicated implication/consequence (the same reaction, pressure, or choice "
                     "is described in both places)")
    if s & _CAUSE_WORDS:
        tags.append("duplicated cause-and-effect framing")
    if not tags:
        tags.append("general semantic restatement of the Full Story's core logic")
    return "; ".join(tags)


def compose_diagnosis(overlap_result: dict) -> str:
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

DIAGNOSTIC_RETRY_PROMPT_TEMPLATE = """Write a {level} English news-style podcast script about the \
following topic, for eigo-radio.

[Topic background, in Japanese, for your understanding only — write your output in English]
{topic_ja}

[Working title]
{title_en}

{register_note}

{storytelling_first}

{no_jargon}

{hook_guidance}

{point_role_spec}

[Verified Fact Ledger — your ONLY source of facts. Do not use any fact, number, or claim that is \
not in this Ledger]
{ledger_text}

{diagnostic_section}

[Output — respond with the following fields]
- title: a short, engaging episode title for this script (not identical to the working title, \
your own phrasing)
- full_story: the main narrative, 3-6 short paragraphs separated by blank lines, telling the core \
news story. This must stand on its own — a listener who hears only this should understand the \
core news.
- point_one_heading: a short heading for Point One
- point_one_body: the Point One paragraph (roughly 30-70 words), going deeper than the Full Story
- point_two_heading: a short heading for Point Two
- point_two_body: the Point Two paragraph (roughly 30-70 words), going deeper than the Full Story, \
covering different ground from Point One
- in_one_line: one short closing sentence that captures the core insight of the whole piece

Output ONLY the fields above, nothing else."""


def generate_full_article_a2_initial(run_idx: int) -> dict:
    """現行仕様(Trial-08)そのまま。Role Planningは追加しない。"""
    prompt = trial08.FULL_ARTICLE_PROMPT_TEMPLATE.format(
        level="A2", topic_ja=trial08.TOPIC_JA, title_en=trial08.TITLE_EN,
        register_note=trial08.REGISTER_NOTE["A2"], storytelling_first=trial08.STORYTELLING_FIRST,
        no_jargon=trial08.NO_JARGON, hook_guidance=trial08.HOOK_GUIDANCE,
        point_role_spec=trial08.POINT_ROLE_SPEC, ledger_text=trial08.VERIFIED_LEDGER_TEXT,
    )
    stage = f"diagnostic_retry_11_run{run_idx}_writer_initial"
    with cl.logging_context("diagnostic_retry_11", stage):
        response = client.responses.create(
            model=WRITER_MODEL,
            reasoning={"effort": trial08.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **trial08.full_article_schema()}},
            input=[
                {"role": "developer", "content": trial08.FULL_ARTICLE_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    return json.loads(response.output_text)


def generate_full_article_a2_diagnostic_retry(run_idx: int, attempt_label: str, prev: dict) -> dict:
    diagnosis_one = compose_diagnosis(prev["overlap"]["point_one"])
    diagnosis_two = compose_diagnosis(prev["overlap"]["point_two"])
    diagnostic_section = DIAGNOSTIC_SECTION_TEMPLATE.format(
        previous_full_story=prev["full_story_clean"],
        point_one_score=prev["overlap"]["point_one"]["overlap_ratio"],
        point_one_flagged=prev["overlap"]["point_one"]["flagged"],
        previous_point_one=prev["article"]["point_one_body"],
        diagnosis_one=diagnosis_one,
        point_two_score=prev["overlap"]["point_two"]["overlap_ratio"],
        point_two_flagged=prev["overlap"]["point_two"]["flagged"],
        previous_point_two=prev["article"]["point_two_body"],
        diagnosis_two=diagnosis_two,
    )
    prompt = DIAGNOSTIC_RETRY_PROMPT_TEMPLATE.format(
        level="A2", topic_ja=trial08.TOPIC_JA, title_en=trial08.TITLE_EN,
        register_note=trial08.REGISTER_NOTE["A2"], storytelling_first=trial08.STORYTELLING_FIRST,
        no_jargon=trial08.NO_JARGON, hook_guidance=trial08.HOOK_GUIDANCE,
        point_role_spec=trial08.POINT_ROLE_SPEC, ledger_text=trial08.VERIFIED_LEDGER_TEXT,
        diagnostic_section=diagnostic_section,
    )
    stage = f"diagnostic_retry_11_run{run_idx}_writer_{attempt_label}"
    with cl.logging_context("diagnostic_retry_11", stage):
        response = client.responses.create(
            model=WRITER_MODEL,
            reasoning={"effort": trial08.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **trial08.full_article_schema()}},
            input=[
                {"role": "developer", "content": trial08.FULL_ARTICLE_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    return json.loads(response.output_text), diagnosis_one, diagnosis_two


def check_point_overlap(article_clean: dict, full_story_clean: str) -> dict:
    o1 = overlap_qa.flag_possible_paraphrase(article_clean["point_one_body"], full_story_clean)
    o2 = overlap_qa.flag_possible_paraphrase(article_clean["point_two_body"], full_story_clean)
    return {"point_one": o1, "point_two": o2, "flagged": bool(o1["flagged"] or o2["flagged"])}


def run_experiment_b_once(run_idx: int) -> dict:
    attempts_log = []
    final_article_clean = None
    final_full_story_clean = None
    status = None
    both_pass = False
    prev = None

    for attempt in range(0, POINT_OVERLAP_ARTICLE_RETRY_MAX + 1):
        label = "initial" if attempt == 0 else f"retry{attempt}"
        diagnosis_used = None
        print(f"\n{'-'*70}\n[Run {run_idx}] Attempt {attempt} ({label}): "
              f"A2 Full Article生成(model={WRITER_MODEL})\n{'-'*70}")

        if attempt == 0:
            article = generate_full_article_a2_initial(run_idx)
        else:
            article, diag1, diag2 = generate_full_article_a2_diagnostic_retry(run_idx, label, prev)
            diagnosis_used = {"point_one": diag1, "point_two": diag2}

        hooks = trial08.extract_hooks(article["full_story"])
        full_story_clean = trial08.strip_hook_markers(article["full_story"])
        article_clean = dict(article)
        article_clean["full_story"] = full_story_clean

        overlap = check_point_overlap(article_clean, full_story_clean)
        jargon_found = trial08.detect_jargon(" ".join([
            full_story_clean, article["point_one_body"], article["point_two_body"], article["in_one_line"]]))

        print(f"[Run {run_idx}][Attempt {attempt}] Point One overlap="
              f"{overlap['point_one']['overlap_ratio']} Point Two overlap="
              f"{overlap['point_two']['overlap_ratio']} flagged={overlap['flagged']} "
              f"Hooks={len(hooks)} Jargon={jargon_found}")
        if diagnosis_used:
            print(f"[Run {run_idx}][Attempt {attempt}] diagnosis_one={diagnosis_used['point_one']!r}")
            print(f"[Run {run_idx}][Attempt {attempt}] diagnosis_two={diagnosis_used['point_two']!r}")

        attempts_log.append({
            "attempt": attempt, "label": label, "model": WRITER_MODEL,
            "diagnosis_used": diagnosis_used,
            "article_raw": article, "hooks_count": len(hooks), "jargon_found": jargon_found,
            "point_overlap": {
                "point_one_ratio": overlap["point_one"]["overlap_ratio"],
                "point_one_shared_words": overlap["point_one"]["shared_words"],
                "point_two_ratio": overlap["point_two"]["overlap_ratio"],
                "point_two_shared_words": overlap["point_two"]["shared_words"],
                "flagged": overlap["flagged"],
            },
        })

        final_article_clean = article_clean
        final_full_story_clean = full_story_clean
        prev = {"article": article, "full_story_clean": full_story_clean, "overlap": overlap}

        if not overlap["flagged"]:
            status = "PASS"
            both_pass = True
            break
        if attempt >= POINT_OVERLAP_ARTICLE_RETRY_MAX:
            status = "NG_REVIEW_REQUIRED"
            break
        print(f"[Run {run_idx}][Attempt {attempt}] Point overlap NG。"
              f"Diagnostic情報付きで記事全体をWriterから再生成します。")

    article_text_final = trial08.build_article_md("A2", final_article_clean, final_full_story_clean)

    initial_flagged = attempts_log[0]["point_overlap"]["flagged"]
    retry_converted_to_pass = bool(initial_flagged and both_pass)

    return {
        "run_idx": run_idx, "status": status, "both_points_pass": both_pass,
        "initial_flagged": initial_flagged, "retry_converted_to_pass": retry_converted_to_pass,
        "attempts": attempts_log, "final_article_text": article_text_final,
    }


def main():
    runs = []
    for run_idx in range(NUM_RUNS):
        runs.append(run_experiment_b_once(run_idx))

    cost_summary = cost_calc.summarize_cost_log(COST_LOG_PATH)

    both_pass_count = sum(1 for r in runs if r["both_points_pass"])
    initial_ng_count = sum(1 for r in runs if r["initial_flagged"])
    retry_converted_count = sum(1 for r in runs if r["retry_converted_to_pass"])
    output = {
        "experiment": "B_diagnostic_full_retry",
        "writer_model_used": WRITER_MODEL,
        "point_overlap_article_retry_max": POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "num_runs": NUM_RUNS,
        "both_points_pass_count": both_pass_count,
        "both_points_pass_rate": round(both_pass_count / NUM_RUNS, 3),
        "initial_ng_count": initial_ng_count,
        "retry_converted_to_pass_count": retry_converted_count,
        "retry_conversion_rate": (round(retry_converted_count / initial_ng_count, 3)
                                   if initial_ng_count else None),
        "runs": runs,
        "cost_summary": cost_summary,
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n結果を保存しました: {RESULTS_PATH}")
    print(f"両Point同時PASS率: {both_pass_count}/{NUM_RUNS}")
    print(f"Initial NG→Retry PASS転換: {retry_converted_count}/{initial_ng_count}")
    print(f"総Cost: {cost_summary['total_cost_jpy']}円 ({cost_summary['total_calls']} calls)")
    print(f"使用modelの内訳: {sorted(set(c['model_id'] for c in cost_summary['per_call']))}")


if __name__ == "__main__":
    main()
