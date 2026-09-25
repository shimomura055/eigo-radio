# ============================================================
# er017_key_phrase_level_spec_trial_01.py
# KEY-PHRASE-LEVEL-SPEC-TRIAL-01 (ユーザー指示、2026-09-25)
# ============================================================
# 目的: Key Phrase選定・解説方針の新Trial案(汎用性/学習価値/自然な
# 英語のまとまり優先、Topic Wordは最大1個まで任意、Standard=日本語
# 解説・Advanced=平易な英語解説)を、Sewer/Meta記事のStandard/Advanced
# 各1本ずつ(計4 call)で試作評価する。今回はTrialのみ。
#
# 完全に隔離: 既存Production Key Phrase仕様
# (er003_v1_n3_01_scaffold_generate.py の run_key_phrases /
# run_key_phrase_selection、内部で使う er003_b1_p2_keywords /
# er003_key_words_canonicalization / er003_key_words_production の
# Prompt・schema・選定ロジック)は一切import・変更しない。API呼び出しの
# 形(client.responses.create + text.format=json_schema strict)のみ、
# 同じOpenAI Responses APIの使い方に倣うが、本Trial専用の独立した
# developer/userプロンプト・schemaを新規定義する。
#
# 想定ターゲット(expected_sets、評価専用): このモジュールのグローバル
# 定数としては保持しない。--step evaluate 実行時にのみ evaluate_only()
# 内のローカル変数として構築し、outputs/expected_sets.json へ保存する
# (Promptを構築する関数・定数とは物理的に別関数に置き、Promptへ混入
# しないようにする)。
#
# 対象記事(読み取りのみ、他タスクの出力は一切変更しない):
#   Meta Advanced: er012_output/e_family_two_level_wiring_01/meta/b1b/article.md
#   Meta Standard: er012_output/e_family_two_level_wiring_01/meta/a2/article.md
#   Sewer Advanced: er012_output/e_family_two_level_wiring_01/sewer/b1b/article.md
#                   (無ければ er015_output/news_natural_advanced_standard_a2_trial_01/
#                   a1_advanced_sewer.md)
#   Sewer Standard: er012_output/e_family_two_level_wiring_01/sewer/a2/article.md
#                   (無ければ er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
#                   a2v5_standard_sewer.md)
#
# 固定: 4 call(Sewer/Meta × Standard/Advanced)+ schema失敗時のみ同一
# 条件で1回まで再試行。model=gpt-5.6-luna、reasoning effort=medium、
# previous_response_idなし、Web Searchなし。費用上限: 累計JPY 20円
# (--budget-jpyで超過見込みならSTOP)。
#
# サブコマンド (--step):
#   inputs    : 4記事の入力パス解決(存在するものを優先順で採用)+sha256を
#               記録(inputs_resolved.json)。LLM不使用。
#   run       : 4 call実行(--budget-jpy 上限あり)。outputs/*.json
#               (parsed + raw response text + usage + cost + latency +
#               response.model)を保存。
#   evaluate  : 機械一致判定(仮判定、最終はFable/ユーザー)。
#               expected_sets.json / match_results.json / match_results.md
#               を保存。wordfreqでAdvanced解説の語数・難度も機械チェック。
#   assemble  : outputs一式・match_results・cost集計をまとめた
#               summary.json / summary.md を保存(REPORT執筆用の素材)。
#
# 実行方法:
#   .venv/Scripts/python.exe er017_key_phrase_level_spec_trial_01.py \
#       --out-dir er017_output/key_phrase_level_spec_trial_01 --step inputs
# ============================================================

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time

MODEL = "gpt-5.6-luna"
REASONING_EFFORT = "medium"
USD_TO_JPY = 160
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

# ------------------------------------------------------------
# 入力記事パス(優先順、存在するものを採用。読み取りのみ)
# ------------------------------------------------------------
INPUT_CANDIDATES = {
    "meta_advanced": [
        "er012_output/e_family_two_level_wiring_01/meta/b1b/article.md",
    ],
    "meta_standard": [
        "er012_output/e_family_two_level_wiring_01/meta/a2/article.md",
    ],
    "sewer_advanced": [
        "er012_output/e_family_two_level_wiring_01/sewer/b1b/article.md",
        "er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md",
    ],
    "sewer_standard": [
        "er012_output/e_family_two_level_wiring_01/sewer/a2/article.md",
        "er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/a2v5_standard_sewer.md",
    ],
}

# combo key -> (article_group, level)
COMBOS = [
    ("sewer", "standard"),
    ("sewer", "advanced"),
    ("meta", "standard"),
    ("meta", "advanced"),
]


# ------------------------------------------------------------
# 汎用ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def resolve_input(key: str) -> str:
    for cand in INPUT_CANDIDATES[key]:
        if os.path.exists(cand):
            return cand
    raise SystemExit(f"[STOP] 入力記事が見つかりません: {key} candidates={INPUT_CANDIDATES[key]}")


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


# ============================================================
# Trial専用 Prompt(記事非依存、逐語。ユーザー委任文から一字一句転記)
# ============================================================
DEVELOPER_MESSAGE = (
    "You choose Key Phrases for an English-learning news audio program for "
    "Japanese adult learners. The goal of Key Phrases is not only to "
    "understand this article, but to take away English that the learner "
    "can reuse in other situations."
)

STANDARD_USER_TEMPLATE = """Choose exactly 5 Key Phrases from the article below for STANDARD level learners (CEFR A2).

Priorities:
- Reusability: prefer basic expressions that the learner can use again in everyday life or in news on other topics.
- Learning value and natural English chunks (e.g., phrasal verbs, common collocations, useful function phrases).
- Fit for A2 level. Do not choose a word only because it is difficult, and do not choose a word only because it is specific to this article.
- Keep each phrase short: one learning point per phrase. Do not pack two grammar or vocabulary points into one phrase. Do not attach article-specific nouns to a general phrase when the general phrase is the real learning point. Use "..." for a slot when needed (for example, "put ... on hold").
- At most ONE of the 5 may be a Topic Word: a theme-specific word that is worth learning for this article even though it is not a general expression. A Topic Word is optional, not required.

For each phrase give: phrase (as written in the article, with "..." for slots), is_topic_word (true/false), example_sentence (the sentence from the article that contains it), reason_ja (one short line in Japanese on why it was chosen), explanation_ja (a short Japanese explanation of the meaning and how to use it).

Return JSON only: {{"key_phrases": [ {{...}} x5 ]}}.

[Article]
{article}"""

ADVANCED_USER_TEMPLATE = """Choose exactly 5 Key Phrases from the article below for ADVANCED level learners (CEFR B1).

Priorities:
- Compared with basic level, prefer slightly more advanced vocabulary, natural collocations, and expressions that are easy to reuse in news or explanatory writing and speech.
- Reusability and learning value come first. Do not choose a word only because it is difficult, and do not choose a word only because it is specific to this article.
- "Advanced" does not mean longer. Keep each phrase about as short as a basic-level phrase: one learning point per phrase. Do not pack two points into one phrase (for example, do not combine "consider" and "replace A with B"). Do not attach unnecessary words when the real learning point is shorter (for example, "take care of", not "take care of the rest"). But keep a natural collocation together when it is worth learning as a unit (for example, "raise privacy concerns").
- Do not fix article-specific nouns into a general phrase if that lowers reusability. Use "A", "B", or "..." for slots (for example, "replace A with B").
- At most ONE of the 5 may be a Topic Word: a theme-specific word that is worth learning for this article even though it is not a general expression. A Topic Word is optional, not required.

For each phrase give: phrase, is_topic_word (true/false), example_sentence (the sentence from the article that contains it), reason_ja (one short line in Japanese on why it was chosen), explanation_en (a short, simple English explanation of the meaning — one sentence, plain words, easier than the phrase itself; not a dictionary definition. Example style: "raise privacy concerns" -> "to make people worry about how personal information is used or protected").

Return JSON only: {{"key_phrases": [ {{...}} x5 ]}}.

[Article]
{article}"""


def _item_schema(explanation_field: str) -> dict:
    return {
        "type": "object",
        "properties": {
            "phrase": {"type": "string"},
            "is_topic_word": {"type": "boolean"},
            "example_sentence": {"type": "string"},
            "reason_ja": {"type": "string"},
            explanation_field: {"type": "string"},
        },
        "required": ["phrase", "is_topic_word", "example_sentence", "reason_ja", explanation_field],
        "additionalProperties": False,
    }


STANDARD_JSON_SCHEMA = {
    "name": "key_phrase_level_spec_trial_standard",
    "schema": {
        "type": "object",
        "properties": {
            "key_phrases": {
                "type": "array",
                "minItems": 5,
                "maxItems": 5,
                "items": _item_schema("explanation_ja"),
            },
        },
        "required": ["key_phrases"],
        "additionalProperties": False,
    },
    "strict": True,
}

ADVANCED_JSON_SCHEMA = {
    "name": "key_phrase_level_spec_trial_advanced",
    "schema": {
        "type": "object",
        "properties": {
            "key_phrases": {
                "type": "array",
                "minItems": 5,
                "maxItems": 5,
                "items": _item_schema("explanation_en"),
            },
        },
        "required": ["key_phrases"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_user_message(level: str, article_text: str) -> str:
    template = STANDARD_USER_TEMPLATE if level == "standard" else ADVANCED_USER_TEMPLATE
    return template.format(article=article_text)


def schema_for_level(level: str) -> dict:
    return STANDARD_JSON_SCHEMA if level == "standard" else ADVANCED_JSON_SCHEMA


# ============================================================
# STEP: inputs
# ============================================================
def cmd_inputs(out_dir: str) -> None:
    resolved = {}
    for group in ("sewer", "meta"):
        for level in ("standard", "advanced"):
            key = f"{group}_{level}"
            path = resolve_input(key)
            resolved[key] = {
                "path": path,
                "sha256": sha256_of_file(path),
                "char_count": len(load_text(path)),
            }
    save_json(out_path(out_dir, "inputs_resolved.json"), resolved)
    for k, v in resolved.items():
        print(f"[OK] {k}: path={v['path']} sha256={v['sha256'][:16]}... chars={v['char_count']}")


# ============================================================
# STEP: run (4 call)
# ============================================================
def _call_key_phrases(client, pricing, developer: str, user_message: str, schema: dict,
                       stage_label: str):
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

    if parsed is None or "key_phrases" not in parsed or len(parsed.get("key_phrases", [])) != 5:
        retried = True
        print(f"[RETRY] stage={stage_label}: schema/parse failure "
              f"({parse_error}), retrying once (same conditions)")
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


def cmd_run(out_dir: str, budget_jpy: float, force: bool) -> None:
    client = get_client()
    pricing = _load_pricing()
    total_jpy = 0.0

    for group, level in COMBOS:
        key = f"{group}_{level}"
        stage_label = f"{group}_{level}"
        dst_output = out_path(out_dir, "outputs", f"{stage_label}.json")
        if os.path.exists(dst_output) and not force:
            existing = load_json(dst_output)
            total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
            print(f"[SKIP] existing: {dst_output} (cost so far={round(total_jpy, 4)} JPY)")
            continue

        article_path = resolve_input(key)
        article_text = load_text(article_path)
        user_message = build_user_message(level, article_text)
        schema = schema_for_level(level)

        parsed, raw_text, meta = _call_key_phrases(
            client, pricing, DEVELOPER_MESSAGE, user_message, schema, stage_label)
        meta["article_path"] = article_path
        meta["article_sha256"] = sha256_of_file(article_path)

        result = {"group": group, "level": level, "parsed": parsed, "raw_output_text": raw_text,
                  "meta": meta}
        save_json(dst_output, result)
        save_text(out_path(out_dir, "outputs", f"{stage_label}_prompt.txt"),
                  "DEVELOPER:\n" + DEVELOPER_MESSAGE + "\n\nUSER:\n" + user_message)

        total_jpy += meta["cost_jpy"]
        print(f"[OK] {stage_label}: model={meta['response_model_actual']} "
              f"elapsed={meta['elapsed_seconds']}s cost_jpy={meta['cost_jpy']} "
              f"retried={meta['retried']} cumulative_jpy={round(total_jpy, 4)}")

        if parsed is None:
            stop = {"stop_reason": f"parse failure after retry ({stage_label})",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] parse failure after retry ({stage_label})")
            raise SystemExit(1)

        if total_jpy > budget_jpy:
            stop = {"stop_reason": f"budget exceeded after {stage_label}",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": budget_jpy}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after {stage_label}: "
                  f"{round(total_jpy, 4)} > {budget_jpy}")
            raise SystemExit(1)

    print(f"[DONE] run complete. total_cost_jpy={round(total_jpy, 4)} budget_jpy={budget_jpy}")


# ============================================================
# STEP: evaluate (機械一致判定の仮判定 + wordfreqチェック。LLM不使用)
# ============================================================
def _build_expected_sets() -> dict:
    """想定ターゲット(評価専用)。Promptを構築するどの関数からも参照
    されない(build_user_message/STANDARD_USER_TEMPLATE/ADVANCED_USER_
    TEMPLATEとは独立)。この関数はevaluate系のコードからのみ呼ばれる。"""
    return {
        "sewer_standard": {
            "phrases": ["take care of", "instead of", "keep ... going",
                        "treatment plant", "sewer"],
            "topic_word": "sewer",
        },
        "meta_standard": {
            "phrases": ["in other words", "put ... on hold", "raise concerns",
                        "there is nothing wrong with ...", "AI agent"],
            "topic_word": "AI agent",
        },
        "sewer_advanced": {
            "phrases": ["replace A with B", "be connected to", "main artery",
                        "treatment plant", "septic tank"],
            "topic_word": "septic tank",
        },
        "meta_advanced": {
            "phrases": ["raise privacy concerns", "put ... on hold",
                        "behind the curtain", "personal information",
                        "human concierge"],
            "topic_word": "human concierge",
        },
    }


def _normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[.…]{2,}", "...", s)
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".")
    return s


def _machine_match_label(actual: str, expected_list: list) -> tuple:
    """(label, matched_expected_phrase_or_None)。exact/substring一致の
    機械的一次判定のみ。同義・学習単位の近さの最終判定はSonnetがREPORT
    本文で目視により行う(このラベルは仮判定)。"""
    na = _normalize(actual)
    for exp in expected_list:
        ne = _normalize(exp)
        if na == ne:
            return "EXACT", exp
    for exp in expected_list:
        ne = _normalize(exp)
        core_a = na.replace("...", "").strip()
        core_e = ne.replace("...", "").strip()
        if core_a and core_e and (core_a in core_e or core_e in core_a):
            return "MACHINE_PARTIAL", exp
    return "NO_MACHINE_MATCH", None


def cmd_evaluate(out_dir: str) -> None:
    expected_sets = _build_expected_sets()
    save_json(out_path(out_dir, "expected_sets.json"), expected_sets)

    import wordfreq

    match_results = {}
    for group, level in COMBOS:
        stage_label = f"{group}_{level}"
        result = load_json(out_path(out_dir, "outputs", f"{stage_label}.json"))
        parsed = result["parsed"]
        expected = expected_sets[stage_label]["phrases"]
        rows = []
        for item in parsed["key_phrases"]:
            label, matched = _machine_match_label(item["phrase"], expected)
            row = {
                "phrase": item["phrase"],
                "is_topic_word": item["is_topic_word"],
                "machine_match_label": label,
                "machine_matched_expected": matched,
            }
            explanation_field = "explanation_ja" if level == "standard" else "explanation_en"
            explanation = item.get(explanation_field, "")
            row["explanation_field"] = explanation_field
            row["explanation_text"] = explanation
            if level == "advanced":
                words = re.findall(r"[A-Za-z']+", explanation)
                ranks = []
                for w in words:
                    try:
                        r = wordfreq.zipf_frequency(w.lower(), "en")
                    except Exception:
                        r = None
                    ranks.append({"word": w, "zipf_frequency": r})
                row["explanation_word_count"] = len(words)
                row["explanation_word_zipf"] = ranks
                phrase_words = re.findall(r"[A-Za-z']+", item["phrase"])
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
            rows.append(row)
        machine_match_count = sum(1 for r in rows if r["machine_match_label"] in
                                   ("EXACT", "MACHINE_PARTIAL"))
        match_results[stage_label] = {
            "group": group, "level": level, "rows": rows,
            "machine_match_count_of_5": machine_match_count,
            "note": "machine_match_countは仮の機械一致数(exact/substringのみ)。"
                    "同義・学習単位の近さを含む最終PASS/STRONG PASS/FAIL判定は"
                    "REPORT本文でSonnetが目視により行う。",
        }

    save_json(out_path(out_dir, "match_results.json"), match_results)

    md_lines = ["# match_results.md — 機械一致判定(仮)+ Advanced解説チェック\n",
                "機械判定はexact/substringのみ。同義・学習単位の近さを含む最終"
                "PASS/STRONG PASS/FAILはREPORTでSonnetが目視判定する。\n"]
    total_machine_match = 0
    for group, level in COMBOS:
        stage_label = f"{group}_{level}"
        r = match_results[stage_label]
        total_machine_match += r["machine_match_count_of_5"]
        md_lines.append(f"\n## {stage_label} "
                         f"(machine_match={r['machine_match_count_of_5']}/5)\n")
        md_lines.append("| phrase | is_topic_word | machine_match_label | "
                         "matched_expected |")
        md_lines.append("|---|---|---|---|")
        for row in r["rows"]:
            md_lines.append(f"| {row['phrase']} | {row['is_topic_word']} | "
                             f"{row['machine_match_label']} | "
                             f"{row['machine_matched_expected']} |")
    md_lines.append(f"\n## 全体機械一致率(仮) {total_machine_match}/20\n")
    save_text(out_path(out_dir, "match_results.md"), "\n".join(md_lines))

    print(f"[OK] evaluate complete. total_machine_match(仮)={total_machine_match}/20")


# ============================================================
# STEP: assemble (REPORT執筆用の素材まとめ)
# ============================================================
def cmd_assemble(out_dir: str) -> None:
    calls = []
    total_jpy = 0.0
    for group, level in COMBOS:
        stage_label = f"{group}_{level}"
        p = out_path(out_dir, "outputs", f"{stage_label}.json")
        if os.path.exists(p):
            r = load_json(p)
            calls.append({"stage": stage_label, "meta": r["meta"]})
            total_jpy += r["meta"].get("cost_jpy", 0.0)
        else:
            print(f"[WARN] missing output: {p}")

    cost = {
        "calls": calls,
        "call_count": len(calls),
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 20,
        "within_budget": total_jpy <= 20,
    }
    save_json(out_path(out_dir, "cost.json"), cost)

    match_results = load_json(out_path(out_dir, "match_results.json")) \
        if os.path.exists(out_path(out_dir, "match_results.json")) else {}

    summary = {
        "cost": cost,
        "match_results_summary": {
            k: {"machine_match_count_of_5": v["machine_match_count_of_5"]}
            for k, v in match_results.items()
        },
    }
    save_json(out_path(out_dir, "summary.json"), summary)
    print(f"[OK] assemble complete. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']} call_count={len(calls)}")


# ============================================================
# main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["inputs", "run", "evaluate", "assemble"])
    ap.add_argument("--budget-jpy", type=float, default=20.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    print(f"[INFO] out_dir(resolved)={os.path.abspath(args.out_dir)}")

    if args.step == "inputs":
        cmd_inputs(args.out_dir)
    elif args.step == "run":
        cmd_run(args.out_dir, args.budget_jpy, args.force)
    elif args.step == "evaluate":
        cmd_evaluate(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
