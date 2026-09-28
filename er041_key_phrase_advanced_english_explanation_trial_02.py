# ============================================================
# er041_key_phrase_advanced_english_explanation_trial_02.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02 (ユーザー指示Task D,
# 2026-09-28)
# ============================================================
# 目的: Hormuzの既存完成済みAdvanced Key Phrase 5個(Phrase選定は
# 一切再選定しない)について、A(英語Phrase+日本語意味=現行仕様)と
# B(同一英語Phrase+平易な英語解説=Advanced候補)を比較するisolated
# Trial。過去`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`のREJECT主因はPhrase選定
# Prompt v1側(全4セットFAIL)であり、Advanced英語解説そのものは同REPORT
# §7.2で問題なしと実測済み。本Trialはその英語解説仕様
# (`er017_key_phrase_level_spec_trial_01.py` ADVANCED_USER_TEMPLATE の
# explanation_enフィールド定義文)を可能な限りそのまま再利用する
# (詳細: docs/pm/design_key_phrase_advanced_english_explanation_trial_02.md)。
#
# 完全に隔離: Production Key Phrase選定・解説の正式Prompt/schema/
# ロジック(er003_v1_n3_01_scaffold_generate.py run_key_phrases等)は
# 一切import・変更しない。CURRENT_SPEC.mdも無変更。Production Master
# Audio Store(er006_output/master_audio_store_01/)は一切書き込まない。
#
# 入力(読み取りのみ、再選定・再生成しない):
#   er019_output/family_x_audio_production_wiring_01/
#   family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b/
#   key_phrases/keywords_canonicalized.json (5 Key Phrase、
#   display_phrase/japanese_gloss/source_sentence)
#
# 固定: text pipelineは1 call(B解説5件まとめて)+1 call(rubric)。
# model=gpt-5.6-luna、reasoning effort=medium、Web Searchなし。
# 費用上限: --budget-jpy(既定20円)。
#
# 実行方法:
#   .venv/Scripts/python.exe er041_key_phrase_advanced_english_explanation_trial_02.py \
#       --source-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b" \
#       --out-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
#       --budget-jpy 20
#
#   (任意・音声化)
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er041_key_phrase_advanced_english_explanation_trial_02.py \
#       --audio --source-dir "...b1b" \
#       --out-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
#       --trial-store "er041_output/key_phrase_advanced_english_explanation_trial_02/master_store" \
#       --tts-backend speech_metadata_flash_lite --budget-jpy 20
# ============================================================

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import time

import er017_key_phrase_level_spec_trial_01 as prior_trial

MANAGEMENT_ID = "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02"

MODEL = "gpt-5.6-luna"
REASONING_EFFORT = "medium"
USD_TO_JPY = 160
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

# 前回実測(KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md §7.2)ベースの語数
# 上限(新規に決めた閾値ではない、最大観測12語/目安15語以内)。
MAX_WORDS = 15

# 前回Prompt(er017_key_phrase_level_spec_trial_01.ADVANCED_USER_TEMPLATE
# 196行)のexplanation_enフィールド定義文を逐語保持。本Trialのregression
# testで、この文字列が前回Prompt定数の部分文字列であることを検証する
# (前回仕様からの逸脱がないことの機械的な証拠)。
EXPLANATION_EN_SPEC_SENTENCE = (
    "a short, simple English explanation of the meaning — one sentence, "
    "plain words, easier than the phrase itself; not a dictionary "
    "definition. Example style: \"raise privacy concerns\" -> \"to make "
    "people worry about how personal information is used or protected\""
)
assert EXPLANATION_EN_SPEC_SENTENCE in prior_trial.ADVANCED_USER_TEMPLATE, (
    "前回Prompt定数(er017_key_phrase_level_spec_trial_01.ADVANCED_USER_"
    "TEMPLATE)からexplanation_en仕様文が消失/変更されています。本Trialは"
    "前回仕様の逐語再利用が前提のため中断します。")

DEVELOPER_MESSAGE = (
    "You write short English explanations for Key Phrases that Japanese "
    "adult learners are studying in an English-learning news audio "
    "program. The phrases are already chosen; do not change them."
)

USER_TEMPLATE_HEADER = f"""For each of the 5 Key Phrases below, write ONE short English
explanation of its meaning for an ADVANCED (CEFR B1) English learner.

Explanation instruction (reused from a prior approved Trial spec):
{EXPLANATION_EN_SPEC_SENTENCE}

Additional rules for this task:
- The phrase itself must NOT be changed. Return it exactly as given.
- Do not add any name, number, or fact that is not already in the
  phrase or in the source sentence given below.
- Do not just translate the Japanese reference meaning word-for-word.
  Write a natural English explanation of the same meaning.
- The explanation should still make sense if the phrase is used in a
  different context, not only in this one news story.

Key Phrases:
"""

USER_TEMPLATE_FOOTER = (
    '\nReturn JSON only: {"explanations": [ {"phrase": ..., '
    '"english_explanation": ...} x5 ]}'
)

EXPLANATION_JSON_SCHEMA = {
    "name": "key_phrase_advanced_english_explanation_trial_02",
    "schema": {
        "type": "object",
        "properties": {
            "explanations": {
                "type": "array",
                "minItems": 5,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase": {"type": "string"},
                        "english_explanation": {"type": "string"},
                    },
                    "required": ["phrase", "english_explanation"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["explanations"],
        "additionalProperties": False,
    },
    "strict": True,
}

RUBRIC_CRITERIA = [
    "understandable_english_only",
    "not_too_difficult",
    "not_too_long",
    "explanation_simpler_than_phrase",
    "reusability",
    "not_overfit_to_article",
    "meaning_accuracy",
]

RUBRIC_DEVELOPER_MESSAGE = (
    "You are a strict reviewer of English explanations written for "
    "Japanese ADVANCED (CEFR B1) English learners studying Key Phrases "
    "in a news audio program."
)

RUBRIC_USER_HEADER = """Rate each English explanation below on 7 criteria, 1 (poor) to 5
(excellent), each with a one-line reason in English.

Criteria:
- understandable_english_only: can an Advanced (B1) learner understand
  the meaning from the English explanation alone, without translation?
- not_too_difficult: the explanation's own vocabulary is not too hard.
- not_too_long: the explanation is short enough to be useful.
- explanation_simpler_than_phrase: the explanation is not harder to
  understand than the phrase it explains.
- reusability: the explanation would still make sense if the phrase
  were used in a different context/article.
- not_overfit_to_article: the explanation does not depend on details
  that are specific to this one news story.
- meaning_accuracy: the explanation correctly matches the meaning of
  the phrase (compare with the Japanese reference meaning given).

Items:
"""

RUBRIC_USER_FOOTER = (
    '\nReturn JSON only: {"ratings": [ {"phrase": ..., '
    + ", ".join(f'"{c}": {{"score": 1-5, "reason": ...}}' for c in RUBRIC_CRITERIA)
    + "} x5 ]}"
)


def _rubric_item_schema() -> dict:
    props = {"phrase": {"type": "string"}}
    required = ["phrase"]
    for c in RUBRIC_CRITERIA:
        props[c] = {
            "type": "object",
            "properties": {
                "score": {"type": "integer"},
                "reason": {"type": "string"},
            },
            "required": ["score", "reason"],
            "additionalProperties": False,
        }
        required.append(c)
    return {
        "type": "object",
        "properties": props,
        "required": required,
        "additionalProperties": False,
    }


RUBRIC_JSON_SCHEMA = {
    "name": "key_phrase_advanced_english_explanation_trial_02_rubric",
    "schema": {
        "type": "object",
        "properties": {
            "ratings": {
                "type": "array",
                "minItems": 5,
                "maxItems": 5,
                "items": _rubric_item_schema(),
            },
        },
        "required": ["ratings"],
        "additionalProperties": False,
    },
    "strict": True,
}


# ------------------------------------------------------------
# 汎用ヘルパー(前回scriptと同じ実装、独立に保持。Production変更なし)
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _load_pricing():
    return json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]


def _price(pricing, provider, model, meter):
    for p in pricing:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter:
            return p["price"]
    return None


def get_client():
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    return OpenAI()


def keywords_path(source_dir: str) -> str:
    return out_path(source_dir, "key_phrases", "keywords_canonicalized.json")


def load_source_items(source_dir: str) -> list[dict]:
    data = load_json(keywords_path(source_dir))
    items = sorted(data["items"], key=lambda it: it["rank"])
    if len(items) != 5:
        raise SystemExit(f"[STOP] Hormuz b1bのKey Phraseが5個ではありません: {len(items)}")
    return items


# ============================================================
# STEP: inputs (LLM不使用)。A候補は既存確定値をそのまま使う
# (再選定・再生成しない)。
# ============================================================
def cmd_inputs(source_dir: str, out_dir: str) -> None:
    kw_path = keywords_path(source_dir)
    items = load_source_items(source_dir)
    resolved = {
        "source_dir": source_dir,
        "keywords_canonicalized_path": kw_path,
        "keywords_canonicalized_sha256": sha256_of_file(kw_path),
        "item_count": len(items),
    }
    save_json(out_path(out_dir, "inputs_resolved.json"), resolved)

    candidate_a = []
    for it in items:
        candidate_a.append({
            "rank": it["rank"],
            "phrase": it["display_phrase"],
            "source_sentence": it["source_sentence"],
            "japanese_gloss": it["japanese_gloss"],
        })
    save_json(out_path(out_dir, "candidate_a.json"), {"items": candidate_a})
    print(f"[OK] inputs resolved: {kw_path} sha256={resolved['keywords_canonicalized_sha256'][:16]}...")
    for row in candidate_a:
        print(f"  #{row['rank']} phrase={row['phrase']!r} gloss={row['japanese_gloss']!r}")


# ============================================================
# STEP: run (B解説1 call + rubric 1 call)
# ============================================================
def _build_explanation_user_message(items: list[dict]) -> str:
    lines = [USER_TEMPLATE_HEADER]
    for i, it in enumerate(items, start=1):
        lines.append(
            f'{i}. phrase: "{it["display_phrase"]}"\n'
            f'   source_sentence: "{it["source_sentence"]}"\n'
            f'   japanese_reference_meaning (for accuracy check only, do '
            f'not translate literally): "{it["japanese_gloss"]}"\n'
        )
    lines.append(USER_TEMPLATE_FOOTER)
    return "".join(lines)


def _build_rubric_user_message(items: list[dict], explanations_by_phrase: dict) -> str:
    lines = [RUBRIC_USER_HEADER]
    for i, it in enumerate(items, start=1):
        phrase = it["display_phrase"]
        expl = explanations_by_phrase.get(phrase, "")
        lines.append(
            f'{i}. phrase: "{phrase}"\n'
            f'   japanese_reference_meaning: "{it["japanese_gloss"]}"\n'
            f'   english_explanation_to_rate: "{expl}"\n'
        )
    lines.append(RUBRIC_USER_FOOTER)
    return "".join(lines)


def _call_json_schema(client, pricing, developer: str, user_message: str, schema: dict,
                       stage_label: str, expected_array_key: str):
    luna_in = _price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = _price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = _price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    def do_call():
        t0 = time.time()
        response = client.responses.create(
            model=MODEL,
            reasoning={"effort": REASONING_EFFORT},
            text={"format": {"type": "json_schema", **schema}},
            input=[
                {"role": "developer", "content": developer},
                {"role": "user", "content": user_message},
            ],
        )
        elapsed = round(time.time() - t0, 3)
        return response, elapsed

    retried = False
    parse_error = None
    response, elapsed = do_call()
    text = (getattr(response, "output_text", None) or "").strip()
    parsed = None
    if text:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            parse_error = str(e)
    else:
        parse_error = "empty output_text"

    if parsed is None or expected_array_key not in parsed or len(parsed.get(expected_array_key, [])) != 5:
        retried = True
        print(f"[RETRY] stage={stage_label}: schema/parse failure ({parse_error}), retrying once")
        response, elapsed = do_call()
        text = (getattr(response, "output_text", None) or "").strip()
        parsed = None
        parse_error = None
        if text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as e:
                parse_error = str(e)
        else:
            parse_error = "empty output_text"

    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None) if usage else None
    output_tokens = getattr(usage, "output_tokens", None) if usage else None
    cached_tokens = None
    reasoning_tokens = None
    if usage is not None:
        in_details = getattr(usage, "input_tokens_details", None)
        if in_details is not None:
            cached_tokens = getattr(in_details, "cached_tokens", None)
        out_details = getattr(usage, "output_tokens_details", None)
        if out_details is not None:
            reasoning_tokens = getattr(out_details, "reasoning_tokens", None)

    billable_in = max((input_tokens or 0) - (cached_tokens or 0), 0)
    cost_usd = 0.0
    if luna_in is not None:
        cost_usd += (billable_in / 1_000_000) * luna_in
    if luna_cached is not None and cached_tokens:
        cost_usd += (cached_tokens / 1_000_000) * luna_cached
    if luna_out is not None and output_tokens:
        cost_usd += (output_tokens / 1_000_000) * luna_out
    cost_jpy = cost_usd * USD_TO_JPY

    meta = {
        "stage": stage_label,
        "model_requested": MODEL,
        "response_model_actual": response.model,
        "fallback_detected": response.model != MODEL,
        "response_id": response.id,
        "effort_requested": REASONING_EFFORT,
        "usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
        },
        "elapsed_seconds": elapsed,
        "cost_usd": round(cost_usd, 6),
        "cost_jpy": round(cost_jpy, 4),
        "retried": retried,
        "parse_error": parse_error,
        "web_search_used": False,
        "previous_response_id": None,
    }
    return parsed, text, meta


def cmd_run(source_dir: str, out_dir: str, budget_jpy: float, force: bool) -> None:
    items = load_source_items(source_dir)
    client = get_client()
    pricing = _load_pricing()
    total_jpy = 0.0

    b_output_path = out_path(out_dir, "outputs", "b_explanation.json")
    if os.path.exists(b_output_path) and not force:
        existing = load_json(b_output_path)
        total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
        print(f"[SKIP] existing: {b_output_path} (cost so far={round(total_jpy, 4)} JPY)")
        parsed_b = existing["parsed"]
    else:
        user_message = _build_explanation_user_message(items)
        parsed_b, raw_text, meta = _call_json_schema(
            client, pricing, DEVELOPER_MESSAGE, user_message, EXPLANATION_JSON_SCHEMA,
            "b_explanation", "explanations")
        result = {"parsed": parsed_b, "raw_output_text": raw_text, "meta": meta}
        save_json(b_output_path, result)
        save_text(out_path(out_dir, "outputs", "b_explanation_prompt.txt"),
                   "DEVELOPER:\n" + DEVELOPER_MESSAGE + "\n\nUSER:\n" + user_message)
        total_jpy += meta["cost_jpy"]
        print(f"[OK] b_explanation: model={meta['response_model_actual']} "
              f"elapsed={meta['elapsed_seconds']}s cost_jpy={meta['cost_jpy']} "
              f"retried={meta['retried']} cumulative_jpy={round(total_jpy, 4)}")
        if parsed_b is None:
            stop = {"stop_reason": "parse failure after retry (b_explanation)",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print("[STOP] parse failure after retry (b_explanation)")
            raise SystemExit(1)
        if total_jpy > budget_jpy:
            stop = {"stop_reason": "budget exceeded after b_explanation",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": budget_jpy}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after b_explanation: {round(total_jpy, 4)} > {budget_jpy}")
            raise SystemExit(1)

    explanations_by_phrase = {
        row["phrase"]: row["english_explanation"] for row in parsed_b["explanations"]
    }

    rubric_output_path = out_path(out_dir, "outputs", "rubric.json")
    if os.path.exists(rubric_output_path) and not force:
        existing = load_json(rubric_output_path)
        total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
        print(f"[SKIP] existing: {rubric_output_path} (cost so far={round(total_jpy, 4)} JPY)")
    else:
        rubric_user_message = _build_rubric_user_message(items, explanations_by_phrase)
        parsed_rubric, raw_text, meta = _call_json_schema(
            client, pricing, RUBRIC_DEVELOPER_MESSAGE, rubric_user_message, RUBRIC_JSON_SCHEMA,
            "rubric", "ratings")
        result = {"parsed": parsed_rubric, "raw_output_text": raw_text, "meta": meta}
        save_json(rubric_output_path, result)
        save_text(out_path(out_dir, "outputs", "rubric_prompt.txt"),
                   "DEVELOPER:\n" + RUBRIC_DEVELOPER_MESSAGE + "\n\nUSER:\n" + rubric_user_message)
        total_jpy += meta["cost_jpy"]
        print(f"[OK] rubric: model={meta['response_model_actual']} "
              f"elapsed={meta['elapsed_seconds']}s cost_jpy={meta['cost_jpy']} "
              f"retried={meta['retried']} cumulative_jpy={round(total_jpy, 4)}")
        if parsed_rubric is None:
            stop = {"stop_reason": "parse failure after retry (rubric)",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print("[STOP] parse failure after retry (rubric)")
            raise SystemExit(1)
        if total_jpy > budget_jpy:
            stop = {"stop_reason": "budget exceeded after rubric",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": budget_jpy}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after rubric: {round(total_jpy, 4)} > {budget_jpy}")
            raise SystemExit(1)

    print(f"[DONE] run complete. total_cost_jpy={round(total_jpy, 4)} budget_jpy={budget_jpy}")


# ============================================================
# STEP: evaluate (決定論チェック、LLM不使用)
# ============================================================
def _new_fact_candidates(explanation: str, phrase: str, source_sentence: str) -> list[str]:
    """解説文中の大文字語頭語(文頭を除く)・数字トークンのうち、phrase/
    source_sentenceに(大小無視で)出現しないものを新規Fact候補として返す。"""
    haystack = (phrase + " " + source_sentence).lower()
    tokens = re.findall(r"[A-Za-z0-9']+", explanation)
    candidates = []
    for i, tok in enumerate(tokens):
        is_number = tok[0].isdigit()
        is_cap_word = tok[0].isupper() and i > 0 and tok.lower() not in ("i",)
        if not (is_number or is_cap_word):
            continue
        if tok.lower() in haystack:
            continue
        candidates.append(tok)
    return candidates


def cmd_evaluate(source_dir: str, out_dir: str) -> None:
    import wordfreq

    items = load_source_items(source_dir)
    b_result = load_json(out_path(out_dir, "outputs", "b_explanation.json"))
    explanations_by_phrase = {
        row["phrase"]: row["english_explanation"] for row in b_result["parsed"]["explanations"]
    }

    rows = []
    for it in items:
        phrase = it["display_phrase"]
        source_sentence = it["source_sentence"]
        explanation = explanations_by_phrase.get(phrase)
        row = {
            "rank": it["rank"],
            "phrase": phrase,
            "japanese_gloss": it["japanese_gloss"],
            "source_sentence": source_sentence,
            "english_explanation": explanation,
            "phrase_returned_by_model_matches_input": phrase in explanations_by_phrase,
        }
        if explanation is None:
            row["evaluate_error"] = "no matching explanation returned for this phrase"
            rows.append(row)
            continue

        words = re.findall(r"[A-Za-z']+", explanation)
        ranks = []
        for w in words:
            try:
                r = wordfreq.zipf_frequency(w.lower(), "en")
            except Exception:
                r = None
            ranks.append({"word": w, "zipf_frequency": r})
        row["explanation_word_count"] = len(words)
        row["explanation_within_max_words"] = len(words) <= MAX_WORDS
        row["explanation_word_zipf"] = ranks

        phrase_words = re.findall(r"[A-Za-z']+", phrase)
        phrase_min_zipf = min(
            [wordfreq.zipf_frequency(w.lower(), "en") for w in phrase_words] or [None]
        ) if phrase_words else None
        row["phrase_min_zipf_frequency"] = phrase_min_zipf
        harder_words = [
            rr["word"] for rr in ranks
            if rr["zipf_frequency"] is not None and phrase_min_zipf is not None
            and rr["zipf_frequency"] < phrase_min_zipf
        ]
        row["explanation_words_harder_than_phrase"] = harder_words

        row["possible_new_fact_tokens"] = _new_fact_candidates(explanation, phrase, source_sentence)

        rows.append(row)

    match_results = {
        "management_id": MANAGEMENT_ID,
        "max_words": MAX_WORDS,
        "rows": rows,
    }
    save_json(out_path(out_dir, "match_results.json"), match_results)
    print(f"[OK] evaluate: {len(rows)} rows saved to match_results.json")
    for row in rows:
        if "evaluate_error" in row:
            print(f"  #{row['rank']} {row['phrase']!r}: ERROR {row['evaluate_error']}")
            continue
        print(f"  #{row['rank']} {row['phrase']!r}: words={row['explanation_word_count']} "
              f"within_max={row['explanation_within_max_words']} "
              f"harder_words={row['explanation_words_harder_than_phrase']} "
              f"new_fact_candidates={row['possible_new_fact_tokens']}")


# ============================================================
# STEP: assemble (summary.json/summary.md、REPORT/Pages用の素材)
# ============================================================
def cmd_assemble(source_dir: str, out_dir: str) -> None:
    candidate_a = load_json(out_path(out_dir, "candidate_a.json"))["items"]
    match_results = load_json(out_path(out_dir, "match_results.json"))
    rubric_result = load_json(out_path(out_dir, "outputs", "rubric.json"))
    ratings_by_phrase = {r["phrase"]: r for r in rubric_result["parsed"]["ratings"]}

    b_meta = load_json(out_path(out_dir, "outputs", "b_explanation.json"))["meta"]
    rubric_meta = load_json(out_path(out_dir, "outputs", "rubric.json"))["meta"]
    total_cost_jpy = round(b_meta["cost_jpy"] + rubric_meta["cost_jpy"], 4)

    rows_by_phrase = {r["phrase"]: r for r in match_results["rows"]}

    combined = []
    for a in candidate_a:
        phrase = a["phrase"]
        mr = rows_by_phrase.get(phrase, {})
        rt = ratings_by_phrase.get(phrase, {})
        combined.append({
            "rank": a["rank"],
            "phrase": phrase,
            "source_sentence": a["source_sentence"],
            "candidate_a_japanese_meaning": a["japanese_gloss"],
            "candidate_b_english_explanation": mr.get("english_explanation"),
            "deterministic": {
                "word_count": mr.get("explanation_word_count"),
                "within_max_words": mr.get("explanation_within_max_words"),
                "words_harder_than_phrase": mr.get("explanation_words_harder_than_phrase"),
                "possible_new_fact_tokens": mr.get("possible_new_fact_tokens"),
            },
            "rubric": {c: rt.get(c) for c in RUBRIC_CRITERIA} if rt else None,
        })

    summary = {
        "management_id": MANAGEMENT_ID,
        "source_dir": source_dir,
        "total_cost_jpy": total_cost_jpy,
        "items": combined,
    }
    save_json(out_path(out_dir, "summary.json"), summary)

    lines = [f"# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02 summary\n",
             f"total_cost_jpy: {total_cost_jpy}\n\n",
             "| # | phrase | A: japanese meaning | B: english explanation | words | "
             "within_max | harder_words | new_fact_candidates |\n",
             "|---|---|---|---|---|---|---|---|\n"]
    for row in combined:
        d = row["deterministic"]
        lines.append(
            f"| {row['rank']} | {row['phrase']} | {row['candidate_a_japanese_meaning']} | "
            f"{row['candidate_b_english_explanation']} | {d['word_count']} | "
            f"{d['within_max_words']} | {d['words_harder_than_phrase']} | "
            f"{d['possible_new_fact_tokens']} |\n")
    save_text(out_path(out_dir, "summary.md"), "".join(lines))
    print(f"[OK] assemble: summary.json / summary.md saved (total_cost_jpy={total_cost_jpy})")


# ============================================================
# STEP: audio (任意、Trial専用Store。Production Master Store無変更)
# ============================================================
def cmd_audio(source_dir: str, out_dir: str, trial_store: str, tts_backend: str,
              budget_jpy: float) -> None:
    if os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        raise SystemExit(
            "[STOP] --audio実行にはTTS_EXECUTION_MODE=STANDARDの明示が必要です"
            "(delegation T-2)。")

    import er003_v1_repro01_main_generate as repro01
    import er005_cost_logger as cl
    import er019_family_x_audio_production_runner_01 as fx_runner
    import er038_tts_all_spoken_role_style_trial_01 as role_trial

    items = load_source_items(source_dir)
    summary = load_json(out_path(out_dir, "summary.json"))
    rows_by_phrase = {r["phrase"]: r for r in summary["items"]}

    audio_dir = out_path(out_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    narration_src = out_path(source_dir, "narration")
    reused = []
    for it in items:
        rank = it["rank"]
        for suffix, label in ((f"kp{rank}_en.wav", "phrase_en"),
                               (f"kp{rank}_ja_charon.wav", "phrase_ja_gloss")):
            src = out_path(narration_src, suffix)
            dst = out_path(audio_dir, suffix)
            if os.path.exists(src):
                shutil.copyfile(src, dst)
                reused.append({"rank": rank, "label": label, "src": src, "dst": dst,
                                "reused": True, "regenerated": False})
            else:
                reused.append({"rank": rank, "label": label, "src": src, "dst": None,
                                "reused": False, "regenerated": False,
                                "note": "既存artifactが見つからず、Aの再生対象なし"})

    en_style = role_trial.TRIAL_ROLE_STYLE_EN["KEY_PHRASE_EXPLANATION_EN"]
    generated = []
    usage_log_path = out_path(out_dir, "audio_raw_usage_log.jsonl")
    cl.install(usage_log_path)
    with cl.logging_context(MANAGEMENT_ID, "tts"), role_trial.trial_master_audio_store(trial_store):
        for it in items:
            rank = it["rank"]
            phrase = it["display_phrase"]
            row = rows_by_phrase.get(phrase, {})
            explanation = row.get("candidate_b_english_explanation")
            if not explanation:
                continue
            out_wav = out_path(audio_dir, f"kp{rank}_explanation_en.wav")
            with cl.segment_context(f"kp{rank}_explanation_en"):
                r = repro01.generate_narration_snippet_verified_strict(
                    explanation, "en", out_wav, explanation,
                    max_extra_chars=max(20, len(explanation) // 2),
                    max_attempts=2,
                    safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
                    style_prefix_override=en_style, disfluency_qa=True,
                    asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
                    enable_non_latin_cascade=True, tts_backend=tts_backend)
            r["rank"] = rank
            r["phrase"] = phrase
            r["role"] = "KEY_PHRASE_EXPLANATION_EN"
            r["style_prefix_used"] = en_style
            generated.append(r)
            cumulative_jpy, _ = fx_runner.compute_cost_jpy_so_far(usage_log_path)
            print(f"[OK] audio kp{rank}_explanation_en.wav status={r.get('status')} "
                  f"cumulative_jpy={round(cumulative_jpy, 4)}")
            if cumulative_jpy > budget_jpy:
                stop = {"stop_reason": "budget exceeded during audio generation",
                        "total_jpy": round(cumulative_jpy, 4), "budget_jpy": budget_jpy}
                save_json(out_path(out_dir, "audio_stop_reason.json"), stop)
                print(f"[STOP] budget exceeded: {round(cumulative_jpy, 4)} > {budget_jpy}")
                break

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(usage_log_path)
    audio_summary = {
        "management_id": MANAGEMENT_ID, "reused_existing": reused,
        "generated_new_explanation_audio": generated, "total_new_audio_cost_jpy": round(final_jpy, 4),
        "cost_by_provider": by_provider,
    }
    save_json(out_path(out_dir, "audio_summary.json"), audio_summary)
    print(f"[DONE] audio complete. new_cost_jpy={round(final_jpy, 4)} budget_jpy={budget_jpy}")


# ============================================================
# CLI
# ============================================================
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=MANAGEMENT_ID)
    p.add_argument("--source-dir", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=20.0)
    p.add_argument("--force", action="store_true")
    p.add_argument("--audio", action="store_true", help="text pipelineではなく音声化を実行")
    p.add_argument("--trial-store", default=None, help="--audio時のTrial専用Master Store")
    p.add_argument("--tts-backend", default="speech_metadata_flash_lite")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    if args.audio:
        trial_store = args.trial_store or out_path(args.out_dir, "..", "master_store")
        cmd_audio(args.source_dir, args.out_dir, trial_store, args.tts_backend, args.budget_jpy)
        return
    cmd_inputs(args.source_dir, args.out_dir)
    cmd_run(args.source_dir, args.out_dir, args.budget_jpy, args.force)
    cmd_evaluate(args.source_dir, args.out_dir)
    cmd_assemble(args.source_dir, args.out_dir)


if __name__ == "__main__":
    main()
