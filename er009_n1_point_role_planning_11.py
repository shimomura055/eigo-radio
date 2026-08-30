#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-POINT-ROLE-VS-DIAGNOSTIC-RETRY-11: Experiment A (Point Role Planning)

仮説: 全文生成前にPoint One/TwoのSemantic Roleを明示的に設計させることで、
Initial生成時点からPoint間の意味重複を減らせる。

変更点はPoint Role Planningのみ:
- Writerは本文(full_story/point_one_body/point_two_body/...)を書く前に、
  point_one_role / point_two_role / distinction / avoid_overlap という4つの
  内部設計フィールドを同一API呼び出し内で先に出力する(json_schemaのproperty
  順序により、本文フィールドより先に生成させる)。
- Role固定templateは強制しない。Ledger内容に応じてWriter自身が設計する。
- Planningフィールドはfinal_article_text(Production article.md相当)には
  含めない。debug用にattempts_logへ保存する。

Retry方式はProduction仕様(POINT_OVERLAP_ARTICLE_RETRY_MAX=2、Point-only
regeneration禁止、NGなら全文Retry)から変更しない。Diagnostic情報を
Retry promptへ加えることはしない(Experiment Bとの独立性を保つ)。

Storytelling First / No Jargon仕様は維持(Trial-08の同一定数をそのまま再利用)。
WriterはRouting SSOT経由でLunaをfail-closedで使用する。
Production本体・Ledger局所Rewriteパイプライン・Hook-aware Checker・Audio
再生成への配線は一切行わない(DEV検証のみ)。
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

OUT_DIR = "er009_output/point_role_planning_11"
COST_LOG_PATH = f"{OUT_DIR}/cost_log.jsonl"
RESULTS_PATH = f"{OUT_DIR}/results.json"

os.makedirs(OUT_DIR, exist_ok=True)
cl.install(COST_LOG_PATH)

client = OpenAI()

WRITER_MODEL = routing.require_model("A2_WRITER", routing.WRITER_MODEL)

POINT_OVERLAP_ARTICLE_RETRY_MAX = 2
NUM_RUNS = 3

# ============================================================
# Point Role Planning: 追加guidanceのみ。Storytelling First/No Jargon/Hook/
# Point Role Specはtrial08から無変更で再利用する。
# ============================================================
ROLE_PLANNING_GUIDANCE = (
    "Point Role Planning: Before writing the final fields below, first design the roles of Point "
    "One and Point Two based on the Verified Fact Ledger. Decide: point_one_role (the specific "
    "role Point One plays in this piece - for example a surprising detail, a methodological "
    "nuance, a historical contrast, a limitation of the evidence - chosen to fit this Ledger, not "
    "a fixed template), point_two_role (a distinct role for Point Two that covers clearly "
    "different ground from Point One), distinction (one concrete sentence stating how Point One "
    "and Point Two differ in what they explain), and avoid_overlap (one concrete sentence naming "
    "the specific meaning or content that must NOT appear in both points, and must not simply "
    "restate the Full Story's core logic). Then write point_one_body and point_two_body so that "
    "each strictly follows its assigned role and respects avoid_overlap. These four planning "
    "fields are for your own internal design only - they will not be shown to the listener - but "
    "you must still fill them in seriously, in your own words based on this specific Ledger, "
    "before writing the final story fields."
)

ROLE_PLANNING_PROMPT_TEMPLATE = """Write a {level} English news-style podcast script about the \
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

{role_planning_guidance}

[Verified Fact Ledger — your ONLY source of facts. Do not use any fact, number, or claim that is \
not in this Ledger]
{ledger_text}

[Output — respond with the following fields, IN THIS ORDER]
- point_one_role: your internal one-sentence design decision for what Point One's role is (not \
shown to the listener)
- point_two_role: your internal one-sentence design decision for what Point Two's role is (not \
shown to the listener)
- distinction: one sentence stating concretely how Point One and Point Two differ
- avoid_overlap: one sentence naming the specific content that must not appear in both points
- title: a short, engaging episode title for this script (not identical to the working title, \
your own phrasing)
- full_story: the main narrative, 3-6 short paragraphs separated by blank lines, telling the core \
news story. This must stand on its own — a listener who hears only this should understand the \
core news.
- point_one_heading: a short heading for Point One
- point_one_body: the Point One paragraph (roughly 30-70 words), following point_one_role exactly
- point_two_heading: a short heading for Point Two
- point_two_body: the Point Two paragraph (roughly 30-70 words), following point_two_role exactly \
and respecting avoid_overlap
- in_one_line: one short closing sentence that captures the core insight of the whole piece

Output ONLY the fields above, nothing else."""


def role_planning_schema():
    fields = ["point_one_role", "point_two_role", "distinction", "avoid_overlap",
              "title", "full_story", "point_one_heading", "point_one_body",
              "point_two_heading", "point_two_body", "in_one_line"]
    return {
        "name": "full_article_role_planning_v1",
        "schema": {
            "type": "object",
            "properties": {k: {"type": "string"} for k in fields},
            "required": fields,
            "additionalProperties": False,
        },
        "strict": True,
    }


def generate_full_article_a2_role_planning(run_idx: int, attempt_label: str) -> dict:
    prompt = ROLE_PLANNING_PROMPT_TEMPLATE.format(
        level="A2", topic_ja=trial08.TOPIC_JA, title_en=trial08.TITLE_EN,
        register_note=trial08.REGISTER_NOTE["A2"], storytelling_first=trial08.STORYTELLING_FIRST,
        no_jargon=trial08.NO_JARGON, hook_guidance=trial08.HOOK_GUIDANCE,
        point_role_spec=trial08.POINT_ROLE_SPEC, role_planning_guidance=ROLE_PLANNING_GUIDANCE,
        ledger_text=trial08.VERIFIED_LEDGER_TEXT,
    )
    stage = f"point_role_planning_11_run{run_idx}_writer_{attempt_label}"
    with cl.logging_context("point_role_planning_11", stage):
        response = client.responses.create(
            model=WRITER_MODEL,
            reasoning={"effort": trial08.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **role_planning_schema()}},
            input=[
                {"role": "developer", "content": trial08.FULL_ARTICLE_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    return json.loads(response.output_text)


def check_point_overlap(article_clean: dict, full_story_clean: str) -> dict:
    o1 = overlap_qa.flag_possible_paraphrase(article_clean["point_one_body"], full_story_clean)
    o2 = overlap_qa.flag_possible_paraphrase(article_clean["point_two_body"], full_story_clean)
    return {"point_one": o1, "point_two": o2, "flagged": bool(o1["flagged"] or o2["flagged"])}


def run_experiment_a_once(run_idx: int) -> dict:
    attempts_log = []
    final_article_clean = None
    final_full_story_clean = None
    status = None
    both_pass = False

    for attempt in range(0, POINT_OVERLAP_ARTICLE_RETRY_MAX + 1):
        label = "initial" if attempt == 0 else f"retry{attempt}"
        print(f"\n{'-'*70}\n[Run {run_idx}] Attempt {attempt} ({label}): "
              f"Role Planning + A2 Full Article生成(model={WRITER_MODEL})\n{'-'*70}")
        article = generate_full_article_a2_role_planning(run_idx, label)
        hooks = trial08.extract_hooks(article["full_story"])
        full_story_clean = trial08.strip_hook_markers(article["full_story"])
        article_clean = dict(article)
        article_clean["full_story"] = full_story_clean

        overlap = check_point_overlap(article_clean, full_story_clean)
        jargon_found = trial08.detect_jargon(" ".join([
            full_story_clean, article["point_one_body"], article["point_two_body"], article["in_one_line"]]))

        print(f"[Run {run_idx}][Attempt {attempt}] role1={article['point_one_role']!r} "
              f"role2={article['point_two_role']!r}")
        print(f"[Run {run_idx}][Attempt {attempt}] Point One overlap="
              f"{overlap['point_one']['overlap_ratio']} Point Two overlap="
              f"{overlap['point_two']['overlap_ratio']} flagged={overlap['flagged']} "
              f"Hooks={len(hooks)} Jargon={jargon_found}")

        attempts_log.append({
            "attempt": attempt, "label": label, "model": WRITER_MODEL,
            "planning": {
                "point_one_role": article["point_one_role"],
                "point_two_role": article["point_two_role"],
                "distinction": article["distinction"],
                "avoid_overlap": article["avoid_overlap"],
            },
            "article_raw": {k: v for k, v in article.items() if k not in
                             ("point_one_role", "point_two_role", "distinction", "avoid_overlap")},
            "hooks_count": len(hooks), "jargon_found": jargon_found,
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

        if not overlap["flagged"]:
            status = "PASS"
            both_pass = True
            break
        if attempt >= POINT_OVERLAP_ARTICLE_RETRY_MAX:
            status = "NG_REVIEW_REQUIRED"
            break
        print(f"[Run {run_idx}][Attempt {attempt}] Point overlap NG。"
              f"Role Planningを含め記事全体をWriterから再生成します。")

    article_text_final = trial08.build_article_md("A2", final_article_clean, final_full_story_clean)

    return {
        "run_idx": run_idx, "status": status, "both_points_pass": both_pass,
        "attempts": attempts_log, "final_article_text": article_text_final,
    }


def main():
    runs = []
    for run_idx in range(NUM_RUNS):
        runs.append(run_experiment_a_once(run_idx))

    cost_summary = cost_calc.summarize_cost_log(COST_LOG_PATH)

    both_pass_count = sum(1 for r in runs if r["both_points_pass"])
    output = {
        "experiment": "A_point_role_planning",
        "writer_model_used": WRITER_MODEL,
        "point_overlap_article_retry_max": POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "num_runs": NUM_RUNS,
        "both_points_pass_count": both_pass_count,
        "both_points_pass_rate": round(both_pass_count / NUM_RUNS, 3),
        "runs": runs,
        "cost_summary": cost_summary,
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n結果を保存しました: {RESULTS_PATH}")
    print(f"両Point同時PASS率: {both_pass_count}/{NUM_RUNS}")
    print(f"総Cost: {cost_summary['total_cost_jpy']}円 ({cost_summary['total_calls']} calls)")
    print(f"使用modelの内訳: {sorted(set(c['model_id'] for c in cost_summary['per_call']))}")


if __name__ == "__main__":
    main()
