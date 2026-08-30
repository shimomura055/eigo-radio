#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-12

Diagnostic Full Retry を正式Production経路へ統合・検証する。
No.9 A2テーマで検証し、Ledger Deviation Check、runtime証拠、cost計測を実施。

実装: diagnostic_retry_11 の実装パターンをそのまま Production validation に転用。
- Initial生成: trial08 template (診断情報なし)
- Retry生成: diagnostic section 付き prompt
- Overlap check / Ledger deviation check / Fact check を実行
"""

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_point_overlap_qa_18 as overlap_qa
import er009_n1_full_writer_ledger_integration_08 as trial08
import er009_n1_routing_governance_10_actual_model_cost as cost_calc

OUT_DIR = "er009_output/diagnostic_full_retry_production_12"
COST_LOG_PATH = f"{OUT_DIR}/cost_log.jsonl"
RESULTS_PATH = f"{OUT_DIR}/results.json"

os.makedirs(OUT_DIR, exist_ok=True)
cl.install(COST_LOG_PATH)

client = OpenAI()

WRITER_MODEL = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
POINT_OVERLAP_ARTICLE_RETRY_MAX = 2

# ============================================================
# Diagnosis generation (追加LLM呼び出しなし)
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
story (typically 4 paragraphs)
- point_one_heading: a short, punchy section title (5 words or fewer) for Point One
- point_one_body: a single paragraph, 1-3 sentences, narrowing down to the first small takeaway; \
this must NOT restate the full_story's logic
- point_two_heading: a short, punchy section title (5 words or fewer) for Point Two
- point_two_body: a single paragraph, 1-3 sentences, offering a second, distinct takeaway; this \
must NOT restate the full_story's logic or the point_one takeaway
- in_one_line: a single sentence capturing the episode's core message, written for the listener
Output ONLY the fields above, nothing else."""


def generate_full_article_initial(run_idx: int, model: str) -> dict:
    """Initial generation (診断なし)"""
    prompt = trial08.FULL_ARTICLE_PROMPT_TEMPLATE.format(
        level="A2", topic_ja=trial08.TOPIC_JA, title_en=trial08.TITLE_EN,
        register_note=trial08.REGISTER_NOTE["A2"], storytelling_first=trial08.STORYTELLING_FIRST,
        no_jargon=trial08.NO_JARGON, hook_guidance=trial08.HOOK_GUIDANCE,
        point_role_spec=trial08.POINT_ROLE_SPEC, ledger_text=trial08.VERIFIED_LEDGER_TEXT,
    )
    stage = f"diagnostic_production_12_run{run_idx}_writer_initial"
    with cl.logging_context("diagnostic_production_12", stage):
        response = client.responses.create(
            model=model,
            reasoning={"effort": trial08.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **trial08.full_article_schema()}},
            input=[
                {"role": "developer", "content": trial08.FULL_ARTICLE_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    return json.loads(response.output_text)


def generate_full_article_diagnostic_retry(run_idx: int, attempt_label: str,
                                            previous_article: dict, previous_overlap: dict,
                                            model: str) -> tuple:
    """Diagnostic Retry generation"""
    diagnosis_one = compose_diagnosis(previous_overlap["point_one"])
    diagnosis_two = compose_diagnosis(previous_overlap["point_two"])

    diagnostic_section = DIAGNOSTIC_SECTION_TEMPLATE.format(
        previous_full_story=previous_article["full_story"],
        point_one_score=previous_overlap["point_one"]["overlap_ratio"],
        point_one_flagged=previous_overlap["point_one"]["flagged"],
        previous_point_one=previous_article["point_one_body"],
        diagnosis_one=diagnosis_one,
        point_two_score=previous_overlap["point_two"]["overlap_ratio"],
        point_two_flagged=previous_overlap["point_two"]["flagged"],
        previous_point_two=previous_article["point_two_body"],
        diagnosis_two=diagnosis_two,
    )

    prompt = DIAGNOSTIC_RETRY_PROMPT_TEMPLATE.format(
        level="A2", topic_ja=trial08.TOPIC_JA, title_en=trial08.TITLE_EN,
        register_note=trial08.REGISTER_NOTE["A2"], storytelling_first=trial08.STORYTELLING_FIRST,
        no_jargon=trial08.NO_JARGON, hook_guidance=trial08.HOOK_GUIDANCE,
        point_role_spec=trial08.POINT_ROLE_SPEC, ledger_text=trial08.VERIFIED_LEDGER_TEXT,
        diagnostic_section=diagnostic_section,
    )

    stage = f"diagnostic_production_12_run{run_idx}_writer_{attempt_label}"
    with cl.logging_context("diagnostic_production_12", stage):
        response = client.responses.create(
            model=model,
            reasoning={"effort": trial08.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **trial08.full_article_schema()}},
            input=[
                {"role": "developer", "content": trial08.FULL_ARTICLE_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    article = json.loads(response.output_text)
    return article, diagnosis_one, diagnosis_two


def check_point_overlap(article: dict, full_story_clean: str) -> dict:
    o1 = overlap_qa.flag_possible_paraphrase(article["point_one_body"], full_story_clean)
    o2 = overlap_qa.flag_possible_paraphrase(article["point_two_body"], full_story_clean)
    return {"point_one": o1, "point_two": o2, "flagged": bool(o1["flagged"] or o2["flagged"])}


def run_diagnostic_full_retry_workflow() -> dict:
    """メインワークフロー"""
    attempts_log = []
    final_article = None
    prev = None

    for attempt in range(0, POINT_OVERLAP_ARTICLE_RETRY_MAX + 1):
        label = "initial" if attempt == 0 else f"retry{attempt}"
        print(f"\n[PROD-12] Attempt {attempt} ({label})")

        if attempt == 0:
            article = generate_full_article_initial(0, WRITER_MODEL)
            diagnosis_used = None
        else:
            article, diag1, diag2 = generate_full_article_diagnostic_retry(
                0, label, prev["article"], prev["overlap"], WRITER_MODEL)
            diagnosis_used = {"point_one": diag1, "point_two": diag2}

        # Hook extraction
        hooks = trial08.extract_hooks(article["full_story"])
        full_story_clean = trial08.strip_hook_markers(article["full_story"])

        # Overlap check
        overlap = check_point_overlap(article, full_story_clean)

        # Jargon check
        jargon_found = trial08.detect_jargon(" ".join([
            full_story_clean, article["point_one_body"], article["point_two_body"],
            article["in_one_line"]]))

        print(f"[PROD-12] Attempt {attempt}: P1={overlap['point_one']['overlap_ratio']:.3f}, "
              f"P2={overlap['point_two']['overlap_ratio']:.3f}, "
              f"flagged={overlap['flagged']}, hooks={len(hooks)}, jargon={len(jargon_found)}")

        attempts_log.append({
            "attempt": attempt,
            "label": label,
            "model": WRITER_MODEL,
            "diagnosis_used": diagnosis_used,
            "article": article,
            "hooks_count": len(hooks),
            "jargon_found": jargon_found,
            "overlap": {
                "point_one_ratio": overlap["point_one"]["overlap_ratio"],
                "point_two_ratio": overlap["point_two"]["overlap_ratio"],
                "flagged": overlap["flagged"],
            }
        })

        final_article = article
        prev = {"article": article, "full_story_clean": full_story_clean, "overlap": overlap}

        # Check if both pass
        if not overlap["flagged"]:
            print(f"[PROD-12] Both points PASS. Stopping.")
            break

    # Result determination
    final_overlap = attempts_log[-1]["overlap"]
    both_pass = not final_overlap["flagged"]
    status = "PASS" if both_pass else "NG_REVIEW_REQUIRED"

    return {
        "status": status,
        "attempts": attempts_log,
        "final_article": final_article,
        "both_points_pass": both_pass,
        "attempts_count": len(attempts_log),
    }


def run_ledger_deviation_check(article: dict) -> dict:
    """Ledger Deviation Check"""
    print("[PROD-12] Running Ledger Deviation Check...")
    article_md = trial08.build_article_md("A2", article,
                                           trial08.strip_hook_markers(article["full_story"]))
    result = vfl01.run_deviation_check(client, trial08.VERIFIED_LEDGER_TEXT, article_md,
                                       model=WRITER_MODEL)
    return result


def run_fact_check(article: dict) -> dict:
    """Fact Check"""
    print("[PROD-12] Running Fact Check...")
    article_md = trial08.build_article_md("A2", article,
                                           trial08.strip_hook_markers(article["full_story"]))
    fc_prompt = r3.build_fact_check_prompt("Digital tipping screens in restaurants", article_md, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt, model=WRITER_MODEL)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)

    return {
        "status": fc_status,
        "result": fc_result,
        "attempts": len(fc_attempts) if fc_attempts else 0,
    }


def main():
    print("[PROD-12] === ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-12 ===")
    print(f"[PROD-12] Writer Model: {WRITER_MODEL}")

    # Workflow
    workflow_result = run_diagnostic_full_retry_workflow()

    # Post-checks
    if workflow_result["final_article"]:
        ledger_result = run_ledger_deviation_check(workflow_result["final_article"])
        workflow_result["ledger_result"] = ledger_result.get("parsed", {})

        fact_result = run_fact_check(workflow_result["final_article"])
        workflow_result["fact_result"] = fact_result

    # Save results
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        # Serialize-safe result (no raw article text)
        safe_result = {
            "status": workflow_result["status"],
            "both_points_pass": workflow_result["both_points_pass"],
            "attempts_count": workflow_result["attempts_count"],
            "writer_model": WRITER_MODEL,
            "attempts": [
                {
                    "attempt": a["attempt"],
                    "label": a["label"],
                    "overlap": a["overlap"],
                    "diagnosis_used": a["diagnosis_used"],
                    "hooks_count": a["hooks_count"],
                    "jargon_count": len(a["jargon_found"]),
                }
                for a in workflow_result["attempts"]
            ],
            "ledger_result": workflow_result.get("ledger_result"),
            "fact_result": workflow_result.get("fact_result"),
        }
        json.dump(safe_result, f, ensure_ascii=False, indent=2, default=str)

    # Cost summary
    cost_summary = cost_calc.summarize_cost_log(COST_LOG_PATH)
    print(f"[PROD-12] Total Cost: ¥{cost_summary['total_cost_jpy']:.4f} ({cost_summary['total_calls']} calls)")

    print(f"[PROD-12] Status: {workflow_result['status']}")
    print(f"[PROD-12] Both Points PASS: {workflow_result['both_points_pass']}")
    print("[PROD-12] === Complete ===")


if __name__ == "__main__":
    main()
