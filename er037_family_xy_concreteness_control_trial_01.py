# ============================================================
# er037_family_xy_concreteness_control_trial_01.py
# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01(ユーザー承認済みTrial、Trialのみ)
# ============================================================
# 目的: Family X(Meta/Hormuz)記事で観測された、数字・時刻・固有名詞の
# 過度な前景化(音声として聞きづらくなる問題)を抑制できるか検証する。
#
# 本ファイルはTrial専用の新規スクリプトであり、既存Production
# Prompt定数(er019_family_x_ja_writer_o_r1_r2_01.R0_PROMPT/
# REVISION_INSTRUCTIONS、er003_v1_n3_01_advanced_adaptation_generate.
# ADVANCED_*ブロック)は一切変更しない。Pattern文言はこのファイル内でのみ
# 定義し、既存定数へ「追記」する形でPromptを組み立てる(既存定数自体の
# 書き換え・.replace()による改変はしない)。
#
# 既存Production関数の再利用(無変更import):
#   - er019_family_x_ja_writer_o_r1_r2_01: R0_PROMPT / DEVELOPER_MESSAGE /
#     REVISION_INSTRUCTIONS / SYMBOL_PREVENTION_BLOCK_JA /
#     build_original_prompt / call_fresh / call_with_previous_response_id /
#     WRITER_MODEL / WRITER_EFFORT
#   - er003_v1_n3_01_advanced_adaptation_generate: build_prompt /
#     ADVANCED_DEVELOPER / generate_advanced_adaptation (A0 baseline再現用)
#   - er003_v1_en_direct_vfl_01_generate: run_deviation_check /
#     deviation_audit_record / get_client / MODEL / REASONING_EFFORT
#   - er019_family_x_entertainment_production_runner_01: compute_stage_
#     cost_breakdown(既存cost集計ロジックの再利用)
#   - er005_cost_logger: install(raw usage記録、既存モジュール)
#
# 設計書: docs/pm/design_family_xy_concreteness_control_trial_01.md
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er005_cost_logger as cl
import er019_family_x_entertainment_production_runner_01 as fxrunner
import er019_family_x_ja_writer_o_r1_r2_01 as jaw

TRIAL_TAG = "FAMILY_XY_CONCRETENESS_CONTROL_TRIAL_01"

# ------------------------------------------------------------
# 入力artifact(既存Family X production run、再生成しない)
# ------------------------------------------------------------
ARTICLE_SOURCES = {
    "meta": {
        "source_dir": "er019_output/family_x_b3_production_wiring_01/run_01",
    },
    "hormuz": {
        "source_dir": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02",
    },
}


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_article_inputs(article: str) -> dict:
    src = ARTICLE_SOURCES[article]["source_dir"]
    evidence = load_json(f"{src}/storyline_b3/fact_selection_evidence.json")
    return {
        "source_dir": src,
        "selected_storyline": evidence["selected_storyline"],
        "selected_fact_brief_text": evidence["selected_fact_brief_text"],
        "full_ledger_text": load_text(f"{src}/research_ledger/verified_fact_ledger.txt"),
        "ja_r1_current": load_text(f"{src}/ja_writer/revision1.md"),
        "ja_r2_current": load_text(f"{src}/ja_writer/revision2.md"),
        "advanced_baseline_text": load_text(f"{src}/b1b/article.md"),
        "advanced_baseline_deviation": (
            load_json(f"{src}/b1b/audit/deviation_check.json")
            if os.path.exists(f"{src}/b1b/audit/deviation_check.json") else None
        ),
    }


# ------------------------------------------------------------
# Pattern文言(delegation逐語、追記のみ・既存定数は無改変)
# ------------------------------------------------------------
PATTERNS_A = {
    "A0": "",
    "A1": "記事の理解に必要な数字だけを使ってください。",
    "A2": "細かい数字や時刻は基本使わず、話の理解に必要な場合だけ使ってください。",
    "A3": "数字・時刻は基本的に使わないでください。記事の理解に本当に必要な場合だけ、最小限に使ってください。",
    "A4": "数字・時刻は原則使わないでください。省くと話の意味が変わる場合に限り、必要最小限だけ使ってください。",
    "A5": "数字・時刻は原則書かないでください。主旨の理解に不可欠なものだけ、最小限残してください。",
}
PATTERNS_N = {
    "N1": "固有名詞は、記事の理解に必要なものだけを使ってください。",
    "N2": "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方にしてください。",
}
TASK_B_CLEANUP_INSTRUCTION = (
    "この記事から、話の理解に不要な細かい数字・時刻・固有名詞を減らしてください。"
    "事実関係・意味・因果関係は変えないでください。"
)
TASK_C_IMPROVED_R2_INSTRUCTION_SUFFIX = (
    "新しい数字・時刻・固有名詞をLedgerから新たに掘り起こさないでください。"
    "面白さは、構成・対比・場面・人の反応・テンポで作ってください。事実自体は変えないでください。"
)


# 組合せPattern(delegation指定: 「最も効いたA系+N系」1組)。
# JA sweep決定論指標(Meta+Hormuz両記事実測)に基づき選定: 数字抑制はA3が
# 両記事でnumeric_token_count/over_precision_countとも0件に到達した最も
# 緩い文言(A1/A2は記事によって残存)。固有名詞抑制はN2が両記事で安定して
# entity_countを削減した(Meta: N1=13[baselineと同値、効果なし]/N2=10、
# Hormuz: N1=10/N2=10で同点)。N1はMetaで効果が出なかったため、両記事で
# 再現したN2を採用する。
COMBO_PATTERNS = {
    "AN": PATTERNS_A["A3"] + "\n" + PATTERNS_N["N2"],
}


def pattern_text(pattern_id: str) -> str:
    if pattern_id in PATTERNS_A:
        return PATTERNS_A[pattern_id]
    if pattern_id in PATTERNS_N:
        return PATTERNS_N[pattern_id]
    if pattern_id in COMBO_PATTERNS:
        return COMBO_PATTERNS[pattern_id]
    raise ValueError(f"unknown pattern_id: {pattern_id}")


# ------------------------------------------------------------
# 決定論的指標(API不要)
# ------------------------------------------------------------
_TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b|(午前|午後)?\d{1,2}時\d{1,2}分")
_PERCENT_RE = re.compile(r"\d+(\.\d+)?\s?[%％]")
_DECIMAL_RE = re.compile(r"\d+\.\d+")
_DIGIT_RE = re.compile(r"\d+")
_KATAKANA_ENTITY_RE = re.compile(r"[゠-ヿ]{2,}")
_ROMAN_ENTITY_RE = re.compile(r"[A-Za-z][A-Za-z.]{1,}")

_EN_STOPWORDS_CAPWORD = {
    "I", "The", "A", "An", "This", "That", "These", "Those", "He", "She", "It",
    "They", "We", "You", "In", "On", "At", "After", "Before", "When", "While",
    "If", "But", "And", "So", "Because", "With", "For", "To", "As", "Also",
    "Then", "Now", "Still", "Yet", "Even", "Meanwhile", "However", "Some",
    "Many", "Most", "One", "Two", "Three", "Its", "Their", "His", "Her",
    "Not", "No", "Yes", "There", "Here", "What", "Why", "How", "Who",
    "Instead", "Until", "Once", "Unlike", "Like", "Despite", "Rather",
    "According", "Today", "Later", "Soon", "First", "Second", "Third",
    "Point", "In one line", "Full Story",
}


def word_count(text: str) -> int:
    # 日英混在テキストの簡易語数(空白区切り+日本語文字は1文字1語相当として加算しない、
    # 英語の分量比較を主目的とした粗い指標であることを明記)。
    ascii_words = len(re.findall(r"[A-Za-z0-9']+", text))
    ja_chars = len(re.findall(r"[぀-ヿ一-鿿]", text))
    return ascii_words + ja_chars // 2  # JA記事はおよそ2文字/語相当として近似


def count_numeric_tokens(text: str) -> dict:
    digit_tokens = _DIGIT_RE.findall(text)
    over_precision = len(_TIME_RE.findall(text)) + len(_PERCENT_RE.findall(text)) + len(_DECIMAL_RE.findall(text))
    return {"numeric_token_count": len(digit_tokens), "over_precision_count": over_precision,
            "numeric_tokens": digit_tokens}


def extract_entities_ja(text: str) -> set:
    return set(_KATAKANA_ENTITY_RE.findall(text)) | set(
        t for t in _ROMAN_ENTITY_RE.findall(text) if len(t) >= 2)


def extract_entities_en(text: str) -> set:
    lines = text.split("\n")
    entities = set()
    for line in lines:
        # 見出し記号(#, ###, ##)除去後、文頭語を除外するため簡易文分割
        clean = re.sub(r"^#+\s*", "", line).strip()
        if not clean:
            continue
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        for sent in sentences:
            words = sent.split()
            for idx, w in enumerate(words):
                w_clean = w.strip(".,!?\"'()[]")
                if not w_clean or not w_clean[0].isupper():
                    continue
                if idx == 0:
                    continue  # 文頭語は除外(sentence-initial capitalizationのnoise回避)
                if w_clean in _EN_STOPWORDS_CAPWORD:
                    continue
                entities.add(w_clean)
    return entities


def diff_new_tokens(prev_entities: set, cur_entities: set, ledger_text: str) -> list:
    new_tokens = sorted(cur_entities - prev_entities)
    return [t for t in new_tokens if t in ledger_text]


def deterministic_metrics(text: str, lang: str, prev_text_entities: set | None,
                           ledger_text: str) -> dict:
    numeric = count_numeric_tokens(text)
    entities = extract_entities_ja(text) if lang == "ja" else extract_entities_en(text)
    newly_foregrounded = (
        diff_new_tokens(prev_text_entities, entities, ledger_text)
        if prev_text_entities is not None else None
    )
    return {
        "word_count": word_count(text),
        "numeric_token_count": numeric["numeric_token_count"],
        "over_precision_count": numeric["over_precision_count"],
        "entity_count": len(entities),
        "entities": sorted(entities),
        "newly_foregrounded_vs_prev": newly_foregrounded,
    }


# ------------------------------------------------------------
# Task A: JA Original(+Pattern追記)-> R1(現行) -> R2(現行)
# ------------------------------------------------------------
def run_ja_original_with_pattern(client, article_inputs: dict, pattern_id: str) -> dict:
    base_prompt = jaw.build_original_prompt(
        article_inputs["selected_storyline"], article_inputs["selected_fact_brief_text"])
    extra = pattern_text(pattern_id)
    prompt = base_prompt if not extra else base_prompt + "\n\n" + extra
    t0 = time.time()
    response = jaw.call_fresh(client, jaw.DEVELOPER_MESSAGE, prompt, jaw.WRITER_EFFORT,
                               f"trial_original_{pattern_id}")
    text = response.output_text.strip()
    return {"text": text, "response_id": response.id, "elapsed_seconds": round(time.time() - t0, 3)}


def run_ja_revision(client, previous_response_id: str, instruction: str, stage_tag: str) -> dict:
    t0 = time.time()
    response = jaw.call_with_previous_response_id(client, instruction, jaw.WRITER_EFFORT,
                                                    previous_response_id, stage_tag)
    text = response.output_text.strip()
    return {"text": text, "response_id": response.id, "elapsed_seconds": round(time.time() - t0, 3)}


def run_ja_chain_for_pattern(client, article_inputs: dict, pattern_id: str,
                              r2_instruction_override: str | None = None) -> dict:
    """Original(+pattern追記) -> R1(現行、または上書き) -> R2(現行、または上書き)。
    r2_instruction_override指定時(Task C)は、R2のみ差し替え、R1は現行のまま。"""
    original = run_ja_original_with_pattern(client, article_inputs, pattern_id)
    r1 = run_ja_revision(client, original["response_id"], jaw.REVISION_INSTRUCTIONS["r1"],
                          f"trial_r1_{pattern_id}")
    r2_instruction = r2_instruction_override or jaw.REVISION_INSTRUCTIONS["r2"]
    r2 = run_ja_revision(client, r1["response_id"], r2_instruction, f"trial_r2_{pattern_id}")
    return {"original": original, "r1": r1, "r2": r2}


# ------------------------------------------------------------
# Advanced(English)生成(既存build_prompt()を再利用、追記文言なし=production同一)
# ------------------------------------------------------------
def run_advanced_translation(client, ja_r2_text: str) -> dict:
    result = adv_gen.generate_advanced_adaptation(ja_r2_text, client=client)
    return {"text": result.text, "cost_jpy": result.cost_jpy, "model": result.model_id_actual,
            "attempts": result.attempts}


def run_advanced_cleanup_rewrite(client, advanced_baseline_text: str) -> dict:
    """Task B: 既存Advanced本文への単発cleanup rewrite(previous_response_idなし、
    プレーンな1回callで完結、新しい多段パイプラインは作らない)。"""
    prompt = (
        "Below is an English article. " + TASK_B_CLEANUP_INSTRUCTION_EN + "\n\n[Article]\n" +
        advanced_baseline_text
    )
    t0 = time.time()
    response = jaw.call_fresh(client, adv_gen.ADVANCED_DEVELOPER, prompt, "medium",
                               "trial_task_b_cleanup")
    text = response.output_text.strip()
    return {"text": text, "elapsed_seconds": round(time.time() - t0, 3)}


TASK_B_CLEANUP_INSTRUCTION_EN = (
    "Reduce fine-grained numbers, precise times, and unnecessary proper nouns that are "
    "not needed to understand the story. Do not change the facts, meaning, or causal "
    "relationships. Output only the English title and the English body, same format as "
    "the input."
)


# ------------------------------------------------------------
# LLM評価: Essential Fact(既存run_deviation_check再利用)+ rubric(Trial専用1 call)
# ------------------------------------------------------------
RUBRIC_DEVELOPER = (
    "You are a strict editorial reviewer. You do NOT reward removing numbers or proper "
    "nouns for its own sake. A lower number of numbers/names is NOT automatically better."
)
RUBRIC_JSON_SCHEMA = {
    "name": "concreteness_rubric",
    "schema": {
        "type": "object",
        "properties": {
            "storyline_causality_score": {"type": "integer"},
            "storyline_causality_quote": {"type": "string"},
            "entertainment_score": {"type": "integer"},
            "entertainment_quote": {"type": "string"},
            "comprehension_score": {"type": "integer"},
            "comprehension_quote": {"type": "string"},
            "thinness_score": {"type": "integer"},
            "thinness_quote": {"type": "string"},
        },
        "required": ["storyline_causality_score", "storyline_causality_quote",
                      "entertainment_score", "entertainment_quote",
                      "comprehension_score", "comprehension_quote",
                      "thinness_score", "thinness_quote"],
        "additionalProperties": False,
    },
    "strict": True,
}
RUBRIC_PROMPT_TEMPLATE = """Compare the CANDIDATE article against the BASELINE article (same story,
same underlying facts). Score the CANDIDATE on a 1-5 scale for each item below and quote
the exact sentence from the CANDIDATE that best supports your score.

1. storyline_causality_score (5=storyline/cause-and-effect fully preserved vs baseline,
   1=storyline or causality clearly changed or broken)
2. entertainment_score (5=as entertaining/engaging as baseline or more, using structure,
   contrast, scene, reaction, or tempo -- NOT by adding new numbers/names; 1=flat, boring)
3. comprehension_score (5=very easy to understand on a single listen, 1=confusing)
4. thinness_score (5=information is NOT too thin compared to baseline, still substantive;
   1=information has become noticeably thin/vague compared to baseline)

Do not give bonus points simply because the CANDIDATE has fewer numbers or proper nouns.
If removing a number or name makes the story harder to follow or hides who-did-what, that
must lower comprehension_score and/or storyline_causality_score.

[BASELINE]
{baseline_text}

[CANDIDATE]
{candidate_text}
"""


def run_rubric_eval(client, baseline_text: str, candidate_text: str) -> dict:
    prompt = RUBRIC_PROMPT_TEMPLATE.format(baseline_text=baseline_text, candidate_text=candidate_text)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": "medium"},
        text={"format": {"type": "json_schema", **RUBRIC_JSON_SCHEMA}},
        input=[{"role": "developer", "content": RUBRIC_DEVELOPER},
               {"role": "user", "content": prompt}],
    )
    return json.loads(response.output_text)


def run_essential_fact_check(client, ledger_text: str, article_text: str,
                              source_article_text: str | None = None) -> dict:
    check = vfl01.run_deviation_check(client, ledger_text, article_text, hook_aware=False,
                                       include_related_fact_id=True,
                                       source_article_text=source_article_text)
    return vfl01.deviation_audit_record(check)


# ------------------------------------------------------------
# Runner
# ------------------------------------------------------------
def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def merge_save_json(path: str, new_entries: dict) -> None:
    """既存summary.json(前回runで保存済みのPattern結果)があれば読み込み、
    今回のPattern結果でマージ更新する(複数回に分けて--patternsを実行しても
    以前の結果を上書き消去しないための追記保存)。"""
    existing = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
    existing.update(new_entries)
    save_json(path, existing)


def budget_check(out_dir: str, budget_jpy: float) -> float:
    cost = fxrunner.compute_stage_cost_breakdown(f"{out_dir}/raw_usage_log.jsonl")
    total = cost["total_jpy"]
    print(f"[BUDGET] total_jpy={total:.3f} (guardrail={budget_jpy})")
    return total


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--article", required=True, choices=list(ARTICLE_SOURCES.keys()))
    p.add_argument("--task", required=True, choices=["a_ja_sweep", "a_advanced", "b_cleanup", "c_revision"])
    p.add_argument("--patterns", default="")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=80.0)
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    out_dir = f"{args.out_dir}/{args.article}"
    os.makedirs(out_dir, exist_ok=True)
    cl.install(f"{out_dir}/raw_usage_log.jsonl")

    client = vfl01.get_client()
    inputs = load_article_inputs(args.article)
    ledger_text = inputs["full_ledger_text"]

    if args.task == "a_ja_sweep":
        patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
        summary = {}
        for pid in patterns:
            if pid == "A0":
                chain = {
                    "original": {"text": ""},
                    "r1": {"text": inputs["ja_r1_current"]},
                    "r2": {"text": inputs["ja_r2_current"]},
                }
                reused = True
            else:
                chain = run_ja_chain_for_pattern(client, inputs, pid)
                reused = False
            orig_entities = extract_entities_ja(chain["original"]["text"]) if chain["original"]["text"] else set()
            r1_metrics = deterministic_metrics(chain["r1"]["text"], "ja", orig_entities, ledger_text)
            r2_metrics = deterministic_metrics(
                chain["r2"]["text"], "ja",
                extract_entities_ja(chain["r1"]["text"]), ledger_text)
            save_text(f"{out_dir}/task_a_ja/{pid}_original.md", chain["original"]["text"])
            save_text(f"{out_dir}/task_a_ja/{pid}_r1.md", chain["r1"]["text"])
            save_text(f"{out_dir}/task_a_ja/{pid}_r2.md", chain["r2"]["text"])
            summary[pid] = {"reused_baseline": reused, "r1_metrics": r1_metrics, "r2_metrics": r2_metrics}
            budget_check(out_dir, args.budget_jpy)
        merge_save_json(f"{out_dir}/task_a_ja/summary.json", summary)

    elif args.task == "a_advanced":
        patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
        summary = {}
        baseline_en_entities = extract_entities_en(inputs["advanced_baseline_text"])
        for pid in patterns:
            if pid == "A0":
                text = inputs["advanced_baseline_text"]
                deviation = inputs["advanced_baseline_deviation"]
                reused = True
            else:
                ja_r2_path = f"{out_dir}/task_a_ja/{pid}_r2.md"
                ja_r2_text = load_text(ja_r2_path)
                adv = run_advanced_translation(client, ja_r2_text)
                text = adv["text"]
                deviation = run_essential_fact_check(client, ledger_text, text, source_article_text=ja_r2_text)
                reused = False
            en_metrics = deterministic_metrics(text, "en", baseline_en_entities, ledger_text)
            rubric = run_rubric_eval(client, inputs["advanced_baseline_text"], text) if not reused else None
            save_text(f"{out_dir}/task_a_advanced/{pid}.md", text)
            save_json(f"{out_dir}/task_a_advanced/{pid}_deviation.json", deviation)
            if rubric is not None:
                save_json(f"{out_dir}/task_a_advanced/{pid}_rubric.json", rubric)
            summary[pid] = {"reused_baseline": reused, "en_metrics": en_metrics,
                             "deviation_overall_status": (deviation or {}).get("parsed", {}).get("overall_status")
                             if deviation else None,
                             "rubric": rubric}
            budget_check(out_dir, args.budget_jpy)
        merge_save_json(f"{out_dir}/task_a_advanced/summary.json", summary)

    elif args.task == "b_cleanup":
        baseline_en_entities = extract_entities_en(inputs["advanced_baseline_text"])
        result = run_advanced_cleanup_rewrite(client, inputs["advanced_baseline_text"])
        text = result["text"]
        deviation = run_essential_fact_check(client, ledger_text, text,
                                              source_article_text=inputs["advanced_baseline_text"])
        en_metrics = deterministic_metrics(text, "en", baseline_en_entities, ledger_text)
        rubric = run_rubric_eval(client, inputs["advanced_baseline_text"], text)
        save_text(f"{out_dir}/task_b_cleanup/B1.md", text)
        save_json(f"{out_dir}/task_b_cleanup/B1_deviation.json", deviation)
        save_json(f"{out_dir}/task_b_cleanup/B1_rubric.json", rubric)
        save_json(f"{out_dir}/task_b_cleanup/summary.json",
                  {"en_metrics": en_metrics,
                   "deviation_overall_status": deviation["parsed"].get("overall_status"),
                   "rubric": rubric})
        budget_check(out_dir, args.budget_jpy)

    elif args.task == "c_revision":
        # R1は既存artifactをそのまま使う(previous_response_id連鎖ではなく、
        # jaw自身のフォールバック方式[直前本文をplain textで貼る]と同型で継続)。
        r1_text = inputs["ja_r1_current"]
        improved_instruction = jaw.REVISION_INSTRUCTIONS["r2"] + "\n\n" + TASK_C_IMPROVED_R2_INSTRUCTION_SUFFIX
        fallback_user = f"以下の記事:\n\n{r1_text}\n\n{improved_instruction}"
        t0 = time.time()
        response = jaw.call_fresh(client, jaw.DEVELOPER_MESSAGE, fallback_user, jaw.WRITER_EFFORT,
                                   "trial_task_c_r2_improved")
        c1_ja_text = response.output_text.strip()
        save_text(f"{out_dir}/task_c_revision/C1_r2_improved_ja.md", c1_ja_text)

        c0_ja_text = inputs["ja_r2_current"]
        adv_c1 = run_advanced_translation(client, c1_ja_text)
        c1_en_text = adv_c1["text"]
        save_text(f"{out_dir}/task_c_revision/C1_r2_improved_advanced.md", c1_en_text)

        c0_en_text = inputs["advanced_baseline_text"]
        r1_entities_ja = extract_entities_ja(r1_text)
        c0_metrics_ja = deterministic_metrics(c0_ja_text, "ja", r1_entities_ja, ledger_text)
        c1_metrics_ja = deterministic_metrics(c1_ja_text, "ja", r1_entities_ja, ledger_text)
        c0_en_entities = extract_entities_en(c0_en_text)
        c1_metrics_en = deterministic_metrics(c1_en_text, "en", c0_en_entities, ledger_text)

        deviation_c1 = run_essential_fact_check(client, ledger_text, c1_en_text, source_article_text=c1_ja_text)
        rubric_c1 = run_rubric_eval(client, c0_en_text, c1_en_text)
        save_json(f"{out_dir}/task_c_revision/C1_deviation.json", deviation_c1)
        save_json(f"{out_dir}/task_c_revision/C1_rubric.json", rubric_c1)
        save_json(f"{out_dir}/task_c_revision/summary.json", {
            "C0_metrics_ja": c0_metrics_ja,
            "C1_metrics_ja": c1_metrics_ja,
            "C1_metrics_en": c1_metrics_en,
            "C1_deviation_overall_status": deviation_c1["parsed"].get("overall_status"),
            "C1_rubric": rubric_c1,
        })
        budget_check(out_dir, args.budget_jpy)

    final_cost = budget_check(out_dir, args.budget_jpy)
    save_json(f"{out_dir}/cost_{args.task}.json",
              fxrunner.compute_stage_cost_breakdown(f"{out_dir}/raw_usage_log.jsonl"))
    print(f"[DONE] article={args.article} task={args.task} total_jpy={final_cost:.3f}")


if __name__ == "__main__":
    main()
