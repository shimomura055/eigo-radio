# ============================================================
# er015_advanced_vocab_rule_trial_01.py
# ADVANCED-VOCAB-RULE-TRIAL-01 (Fable委任, 管理ID
# NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 2, 2026-09-25)
# ============================================================
# 目的: ユーザー定義のAdvanced難語仕様候補(一般英語頻出順位 約12,000位超
# を原則平易化候補、ただしA[既知の易しい語から推測可能な形態]/B[日本語に
# 定着した外来語]/C[固有名詞]/D[意味・自然さを損なう不可欠語]は例外として
# 残せる)をTrialとして1回だけ検証する。Meta/Sewer Advanced記事2本のみ。
# Production Prompt/Validator/Production pathへは実装しない(Trialのみ)。
#
# 頻度順位: ADVANCED-VOCAB-DIFFICULTY-AUDIT-01が使ったwordfreq
# top_n_list('en', 20000)と同じsource・同じversion(wordfreq 3.1.1)を
# 再利用するが、ランク付けの単位は「lemma」ではなく「記事中に実際に出現
# する表層形(surface form、大小文字を除き活用そのまま)」に変更した
# (新規ロジック、理由は下記)。既存の簡易lemma化(simple_lemma、
# er015_news_standard_a2_vocab_effectiveness_trial_01)には既知のバグ
# (例: 単数 "sewer" が末尾-erを比較級とみなして削られ "sew" という別の
# lemmaに誤って正規化される)があり、ADVANCED-VOCAB-DIFFICULTY-AUDIT-01の
# audit.md 確認事項7(a)で既に明記されている。本Trialでは
# 「順位はコード側で算出しPromptに明記(モデルに順位を推測させない)」と
# いう指示の精度を優先し、このバグを継承しない表層形ベースの順位付けを
# 新たに実装した。band集計(参考値、regressionチェックの補助)のみ、
# 既存のlemmaベースbmod.measure_bandsをそのまま再利用する(既知の限界を
# 継承した参考値であることをmetrics.json/REPORTに明記)。
#
# 依存(re-use):
#   - er015_news_standard_a2_vocab_effectiveness_trial_01 (v3mod):
#       extract_content_words, capitalized_positions (無変更)
#   - er015_news_standard_a2_vocab_banding_trial_01 (bmod, band参考値のみ):
#       measure_bands, _build_lemma_rank_map
#   - bmod.v1mod (= er015_news_natural_advanced_standard_a2_trial_01):
#       out_path/save_text/save_json/load_text/load_json/_strip_title/
#       _level_metrics/install_logger
#   - wordfreq (既存install再利用、追加installなし): top_n_list,
#       zipf_frequency
#   - openai (既存install再利用): client.responses.create
#     (text.format=json_schema strict、er017_key_phrase_level_spec_
#     trial_01と同じAPI呼び出し形のみ倣う、Production Key Phrase実装とは
#     完全に独立)
#
# 固定: 2 call(Meta 1回 + Sewer 1回)。技術的失敗(空応答・JSON parse
# 失敗・schema件数不一致)時のみ同一条件で1回まで再試行。
# previous_response_idなし、Web Searchなし、model=gpt-5.6-luna、
# reasoning effort=high。費用上限: 累計JPY 5円(--budget-jpyで超過見込み
# ならSTOP、実行前チェック)。
#
# サブコマンド (--step):
#   candidates : 閾値超(rank>12000またはtop20000圏外)語リストと
#                BORDERLINE参考語リスト(10000<=rank<=12000)をコード側で
#                算出(candidates_meta.json / candidates_sewer.json)。
#                LLM不使用。
#   run        : Meta/Sewer各1 call実行(--budget-jpy 上限あり)。
#                {article}_raw_response.json に保存。
#   analyze    : after_text構造契約チェック・語数文数差・After新出難語
#                regressionチェック・band参考値Before/After・diff算出。
#                {article}_before.md/_after.md/_decision_log.md/_diff.md/
#                _metrics.json を保存。
#   assemble   : cost.json
#
# 実行方法:
#   .venv/Scripts/python.exe er015_advanced_vocab_rule_trial_01.py \
#       --out-dir er015_output/advanced_vocab_rule_trial_01 --step candidates
# ============================================================
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import time
from collections import Counter

import er015_news_standard_a2_vocab_effectiveness_trial_01 as v3mod
import er015_news_standard_a2_vocab_banding_trial_01 as bmod

v1mod = bmod.v1mod

MODEL = "gpt-5.6-luna"
REASONING_EFFORT = "high"
USD_TO_JPY = 160
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
RANK_THRESHOLD = 12000
BORDERLINE_LOW = 10000
BORDERLINE_HIGH = 12000

ARTICLE_PATHS = {
    "meta": os.path.join(
        "er012_output", "e_family_two_level_wiring_01", "meta", "b1b",
        "article.md"),
    "sewer": os.path.join(
        "er015_output", "news_natural_advanced_standard_a2_trial_01",
        "a1_advanced_sewer.md"),
}

ARTICLE_SOURCE_NOTE = {
    "meta": ("Production E2E版、採用済み本文(Phase Bで\"some of the calls\""
              "修正済みの版)。"),
    "sewer": ("Sewerはユーザー判断でProduction代表記事から除外済み。本Trial"
              "の語彙検証素材としてのみ使用(er015_output/news_natural_"
              "advanced_standard_a2_trial_01/a1_advanced_sewer.md)。"),
}


def out_path(out_dir: str, *parts: str) -> str:
    return v1mod.out_path(out_dir, *parts)


def save_text(path: str, text: str) -> None:
    v1mod.save_text(path, text)


def load_text(path: str) -> str:
    return v1mod.load_text(path)


def save_json(path: str, obj) -> None:
    v1mod.save_json(path, obj)


def load_json(path: str):
    return v1mod.load_json(path)


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


# ------------------------------------------------------------
# 仕様候補 日本語原文(逐語、ユーザー委任文からそのまま転記)
# ------------------------------------------------------------
SPEC_CANDIDATE_JA = """\
## Advanced難語仕様候補(ユーザー定義、逐語)

- Advanced: 一般英語頻出順位 約12,000位超を原則として平易化候補とする
  (機械的禁止リストではない)。Standard v5の思想と同様「必ず置換ではなく、
  より簡単で自然な表現がある場合に平易化を強く優先し、意味・自然さを
  損なう場合は強制しない」。
- 閾値超でも除外できる条件:
  - A. 既知の易しい語から意味を容易に推測できる語(onstage=on+stage、
    wastewater=waste+water、understandable=understand+-able)。形だけ
    分解可能で意味が導けないものは除外しない。
  - B. 日本語として十分定着し、英語の発音から意味を容易に推測できる語
    (piano, curtain, privacy)。カタカナ表記があるだけでは不十分。一般的
    な日本語として意味が定着し、音から容易に分かること。
  - C. 固有名詞(人名・企業名・製品名・地名)。
  - D. 簡単な語へ置換すると意味精度または英語の自然さを明確に損なう
    不可欠語。「専門語だから残す」ではない。簡単で自然かつ意味保持できる
    言い換えがあるなら原則平易化。
- 採用しない例外: 「定型表現・熟語の一部だから除外」は設けない
  (behind the curtainのcurtainを許すのはBの理由であって定型だからでは
  ない)。定型内の推測困難語は通常どおり判定対象。
- 期待: artery型(12,000超・推測困難・日本語未定着)は原則平易化候補。
  Writerが不可欠と判断して残すなら理由を記録。
"""

# ------------------------------------------------------------
# Prompt(英訳、逐語相当。DEVELOPER/USER共通ルール部分は記事非依存)
# ------------------------------------------------------------
DEVELOPER_MESSAGE = (
    "You are an editor testing a candidate vocabulary-difficulty rule for "
    "CEFR B1 (\"Advanced\") level news articles written for Japanese adult "
    "English learners. This rule is a draft under evaluation, not yet "
    "approved. For the specific difficult words listed below, you decide "
    "word by word whether to keep the word or replace it with a simpler, "
    "natural alternative, following the rule exactly. You must not change "
    "anything else in the article."
)

RULE_BLOCK_EN = """Candidate difficulty rule (draft, under evaluation):

Words that rank below roughly the top 12,000 most frequent general English \
words are, in principle, candidates for simplification. This is NOT a \
mechanical ban list. As with the existing Standard-level vocabulary policy, \
simplification should be strongly preferred only when a simpler, natural \
expression exists without harming meaning or naturalness; it must not be \
forced when it would.

A word ranked beyond ~12,000 may still be KEPT (not simplified) if one of \
these applies:
A. Its meaning can easily be guessed from an already-easy word it is built \
from (for example: "onstage" = on + stage, "wastewater" = waste + water, \
"understandable" = understand + -able). Do not exclude a word just because \
it LOOKS decomposable if the meaning cannot actually be guessed that way.
B. It is a word that has become well established in Japanese, and its \
meaning can easily be guessed from its English pronunciation (for example: \
piano, curtain, privacy). Simply having a katakana spelling is not enough \
-- the word must be an established, commonly understood Japanese word, \
easily connected to its English sound.
C. It is a proper noun (a person's name, a company or product name, a \
place name).
D. Replacing it with an easier word would clearly hurt meaning precision \
or the naturalness of the English -- it is indispensable. Do not keep a \
word only because "it is a technical term" -- if a simple, natural, \
meaning-preserving substitute exists, simplify it.

Do NOT use "it is part of a fixed expression / idiom" as its own exception \
category. (For example, if "curtain" in "behind the curtain" is kept, the \
reason must be B [established Japanese loanword], never "it is part of an \
idiom.") A word inside a fixed expression that is still hard to guess \
should be judged normally, exactly like any other word.

For each candidate word listed below, decide:
- "KEEP -- predictable morphology/compound" (reason A)
- "KEEP -- established Japanese loanword" (reason B)
- "KEEP -- proper noun" (reason C)
- "KEEP -- indispensable / natural replacement unavailable" (reason D)
- "SIMPLIFY" (replace it with a simpler, natural word or phrase)
- "BORDERLINE" (only if you are genuinely unsure; explain why in \
notes_on_ambiguous_cases)
"""

STRUCTURE_BLOCK = {
    "meta": (
        "Structure contract (must not change): one `# ` title line, then "
        "body paragraphs, then exactly two `### ` subheadings each "
        "followed by its paragraph, then a `## In one line` section with "
        "its one closing sentence. Keep every heading's text unchanged "
        "unless a heading itself contains a candidate word you decide to "
        "SIMPLIFY (none of the candidate words appear in a heading in this "
        "article). Keep the same number of paragraphs and, as much as "
        "possible, the same sentence count."
    ),
    "sewer": (
        "Structure contract (must not change): this article has NO "
        "markdown headings (no `#`, `###`, or `##` lines) -- it is a plain "
        "title line followed by flowing body paragraphs. Keep it exactly "
        "that way: one plain title line, then the same number of body "
        "paragraphs in the same order, with the same paragraph breaks. Do "
        "not add any heading."
    ),
}

TASK_TAIL = """\
Only change the specific candidate words you decide to SIMPLIFY (and, only \
where grammatically necessary, a minimal amount of immediately surrounding \
wording so the sentence still reads naturally). Do not do a general \
rewrite of sentences that contain no candidate word. Do not add new facts, \
explanations, examples, or opinions. Do not remove any fact. Do not change \
the meaning, the tone, the storytelling, the central metaphor, or the \
ending logic. Keep the title unchanged unless it contains a candidate word \
you decide to SIMPLIFY.

Output:
- "decisions": exactly one entry per candidate word listed below, in the \
same order, each with word, actual_form, frequency_rank (copy the \
frequency_rank value exactly as given below -- do not recompute or guess \
it), decision, reasoning (one or two sentences, in English), \
before_sentence (the exact original sentence that contains this word), \
after_sentence (the resulting sentence in your rewritten article -- for \
KEEP decisions this should be identical or nearly identical to \
before_sentence).
- "after_text": the full rewritten article (title + body), in the same \
format as the original.
- "notes_on_ambiguous_cases": a short note (can be empty) on any word \
where the KEEP/SIMPLIFY line was genuinely hard to draw.

[Candidate words -- rank below ~12,000, decide KEEP or SIMPLIFY for each]
{candidates_block}

[Reference only -- words ranked 10,000-12,000 (near the threshold), shown \
so you can calibrate the rule; these are NOT candidates and do not need a \
decision unless they also appear in the candidate list above]
{borderline_block}

[Article]
{article_text}
"""


def _decision_item_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "word": {"type": "string"},
            "actual_form": {"type": "string"},
            "frequency_rank": {"type": "string"},
            "decision": {
                "type": "string",
                "enum": [
                    "KEEP -- predictable morphology/compound",
                    "KEEP -- established Japanese loanword",
                    "KEEP -- proper noun",
                    "KEEP -- indispensable / natural replacement unavailable",
                    "SIMPLIFY",
                    "BORDERLINE",
                ],
            },
            "reasoning": {"type": "string"},
            "before_sentence": {"type": "string"},
            "after_sentence": {"type": "string"},
        },
        "required": ["word", "actual_form", "frequency_rank", "decision",
                     "reasoning", "before_sentence", "after_sentence"],
        "additionalProperties": False,
    }


def build_json_schema(n_candidates: int) -> dict:
    return {
        "name": "advanced_vocab_rule_trial",
        "schema": {
            "type": "object",
            "properties": {
                "decisions": {
                    "type": "array",
                    "minItems": n_candidates,
                    "maxItems": n_candidates,
                    "items": _decision_item_schema(),
                },
                "after_text": {"type": "string"},
                "notes_on_ambiguous_cases": {"type": "string"},
            },
            "required": ["decisions", "after_text", "notes_on_ambiguous_cases"],
            "additionalProperties": False,
        },
        "strict": True,
    }


# ------------------------------------------------------------
# 候補語抽出(新規ロジック: 表層形[surface form]ベースの順位付け。
# lemma化バグ[sew/sewer分裂]を継承しない。固有名詞除外は既存
# v3mod.capitalized_positionsヒューリスティックをそのまま再利用)
# ------------------------------------------------------------
def _rank_of_map(top20000: list) -> dict:
    return {w: i + 1 for i, w in enumerate(top20000)}


def _format_rank(rank, zipf) -> str:
    if rank is None:
        return f"> 20,000 (zipf={zipf:.2f}, extremely rare)"
    return f"{rank:,}"


def build_candidates(text: str, rank_of: dict) -> dict:
    import wordfreq

    tokens = v3mod.extract_content_words(text)
    groups = {}
    for t in tokens:
        lw = t.lower()
        groups.setdefault(lw, []).append(t)

    candidates = []
    borderline = []
    excluded_proper = []
    all_words = {}
    for lw, forms in groups.items():
        most_common = Counter(forms).most_common(1)[0][0]
        cap = v3mod.capitalized_positions(text, lw)
        is_proper = cap["capitalized_non_sentence_initial"] > 0
        rank = rank_of.get(lw)
        zf = None
        if rank is None:
            zf = wordfreq.zipf_frequency(lw, "en")

        entry = {
            "word": lw,
            "actual_form": most_common,
            "surface_forms": sorted(set(forms)),
            "count": len(forms),
            "rank": rank,
            "zipf_frequency": zf,
            "rank_display": _format_rank(rank, zf),
        }
        all_words[lw] = entry

        if is_proper:
            excluded_proper.append(entry)
            continue
        if rank is None or rank > RANK_THRESHOLD:
            candidates.append(entry)
        elif BORDERLINE_LOW <= rank <= BORDERLINE_HIGH:
            borderline.append(entry)

    def sort_key(e):
        return (0, e["zipf_frequency"]) if e["rank"] is None else (1, e["rank"])

    candidates.sort(key=sort_key)
    borderline.sort(key=lambda e: e["rank"])

    return {
        "content_word_token_total": len(tokens),
        "distinct_word_total": len(groups),
        "candidate_count": len(candidates),
        "borderline_count": len(borderline),
        "excluded_proper_noun_count": len(excluded_proper),
        "candidates": candidates,
        "borderline_reference": borderline,
        "excluded_proper_nouns": excluded_proper,
        "all_words_by_lower": all_words,
    }


def _candidates_block_text(candidates: list) -> str:
    lines = []
    for e in candidates:
        lines.append(f"- word=\"{e['word']}\" actual_form=\"{e['actual_form']}\" "
                      f"frequency_rank=\"{e['rank_display']}\"")
    return "\n".join(lines) if lines else "(none)"


def _borderline_block_text(borderline: list) -> str:
    lines = []
    for e in borderline:
        lines.append(f"- word=\"{e['word']}\" actual_form=\"{e['actual_form']}\" "
                      f"frequency_rank=\"{e['rank_display']}\"")
    return "\n".join(lines) if lines else "(none in this band for this article)"


# ------------------------------------------------------------
# STEP: candidates
# ------------------------------------------------------------
def cmd_candidates(out_dir: str) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    save_json(out_path(out_dir, "frequency_rank_top20000_source.json"), {
        "source_package": "wordfreq",
        "source_package_version": "3.1.1",
        "license": "Apache-2.0",
        "method": "wordfreq.top_n_list('en', 20000) (既存install再利用、"
                  "追加installなし。ADVANCED-VOCAB-DIFFICULTY-AUDIT-01と同一"
                  "method・同一version)",
        "ranking_unit": "surface form (表層形、大小文字を除き活用そのまま。"
                        "lemma化は行わない。理由はer015_advanced_vocab_"
                        "rule_trial_01.py冒頭コメント参照、既存simple_"
                        "lemma()のsew/sewer分裂バグを継承しないため)",
        "rank_threshold": RANK_THRESHOLD,
        "borderline_band": [BORDERLINE_LOW, BORDERLINE_HIGH],
    })

    save_text(out_path(out_dir, "spec_candidate_ja.md"),
              "# spec_candidate_ja.md\n\n" + SPEC_CANDIDATE_JA)

    for key, path in ARTICLE_PATHS.items():
        text = load_text(path)
        result = build_candidates(text, rank_of)
        save_json(out_path(out_dir, f"candidates_{key}.json"), result)
        print(f"[OK] candidates_{key}.json written. "
              f"candidate_count={result['candidate_count']} "
              f"borderline_count={result['borderline_count']} "
              f"excluded_proper={result['excluded_proper_noun_count']}")


# ------------------------------------------------------------
# STEP: run (Meta 1 call, Sewer 1 call)
# ------------------------------------------------------------
def _call_and_parse(client, pricing, developer: str, user_message: str,
                     schema: dict, stage_label: str, n_candidates: int):
    luna_in = _price(pricing, "openai", MODEL, "input_tokens")
    luna_cached = _price(pricing, "openai", MODEL, "cached_input_tokens")
    luna_out = _price(pricing, "openai", MODEL, "output_tokens")

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

    def try_parse(response):
        text = (getattr(response, "output_text", None) or "").strip()
        if not text:
            return None, text, "empty output_text"
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            return None, text, str(e)
        if (not isinstance(parsed, dict) or "decisions" not in parsed
                or len(parsed.get("decisions", [])) != n_candidates):
            return None, text, ("schema count mismatch: expected "
                                 f"{n_candidates} decisions, got "
                                 f"{len(parsed.get('decisions', []))}")
        return parsed, text, None

    retried = False
    response, elapsed = do_call()
    parsed, raw_text, parse_error = try_parse(response)
    if parsed is None:
        retried = True
        print(f"[RETRY] stage={stage_label}: technical failure "
              f"({parse_error}), retrying once (same conditions)")
        response, elapsed = do_call()
        parsed, raw_text, parse_error = try_parse(response)

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
    return parsed, raw_text, meta


def cmd_run(out_dir: str, budget_jpy: float, force: bool) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    v1mod.install_logger(out_dir)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    client = get_client()
    pricing = _load_pricing()
    total_jpy = 0.0

    for key, path in ARTICLE_PATHS.items():
        dst = out_path(out_dir, f"{key}_raw_response.json")
        if os.path.exists(dst) and not force:
            existing = load_json(dst)
            total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
            print(f"[SKIP] existing: {dst} (cost so far={round(total_jpy, 4)} JPY)")
            continue

        article_text = load_text(path)
        cand_result = build_candidates(article_text, rank_of)
        n_candidates = cand_result["candidate_count"]
        candidates_block = _candidates_block_text(cand_result["candidates"])
        borderline_block = _borderline_block_text(cand_result["borderline_reference"])

        user_message = (RULE_BLOCK_EN + "\n" + STRUCTURE_BLOCK[key] + "\n\n" +
                         TASK_TAIL.format(candidates_block=candidates_block,
                                           borderline_block=borderline_block,
                                           article_text=article_text))
        schema = build_json_schema(n_candidates)

        save_text(out_path(out_dir, f"prompt_advanced_vocab_rule_v1_{key}.txt"),
                  "DEVELOPER:\n" + DEVELOPER_MESSAGE + "\n\nUSER:\n" + user_message)

        parsed, raw_text, meta = _call_and_parse(
            client, pricing, DEVELOPER_MESSAGE, user_message, schema, key, n_candidates)
        meta["article_path"] = path
        meta["article_sha256"] = sha256_of_file(path)
        meta["candidate_count"] = n_candidates

        result = {"article": key, "candidates_input": cand_result,
                  "parsed": parsed, "raw_output_text": raw_text, "meta": meta}
        save_json(dst, result)

        total_jpy += meta["cost_jpy"]
        print(f"[OK] {key}: model={meta['response_model_actual']} "
              f"elapsed={meta['elapsed_seconds']}s cost_jpy={meta['cost_jpy']} "
              f"retried={meta['retried']} n_candidates={n_candidates} "
              f"cumulative_jpy={round(total_jpy, 4)}")

        if parsed is None:
            stop = {"stop_reason": f"parse/technical failure after retry ({key})",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] parse/technical failure after retry ({key})")
            raise SystemExit(1)

        if total_jpy > budget_jpy:
            stop = {"stop_reason": f"budget exceeded after {key}",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": budget_jpy}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after {key}: "
                  f"{round(total_jpy, 4)} > {budget_jpy}")
            raise SystemExit(1)

    print(f"[DONE] run complete. total_cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={budget_jpy}")


# ------------------------------------------------------------
# STEP: analyze
# ------------------------------------------------------------
def _paragraphs(body: str) -> list:
    return [p.strip() for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]


def _headings(text: str) -> list:
    return [line.strip() for line in text.splitlines() if line.strip().startswith("#")]


def structure_check(key: str, before_text: str, after_text: str) -> dict:
    before_headings = _headings(before_text)
    after_headings = _headings(after_text)
    before_title, before_body = v1mod._strip_title(before_text)
    after_title, after_body = v1mod._strip_title(after_text)
    before_paras = _paragraphs(before_body)
    after_paras = _paragraphs(after_body)

    checks = {
        "headings_before": before_headings,
        "headings_after": after_headings,
        "headings_match": before_headings == after_headings,
        "title_before": before_title,
        "title_after": after_title,
        "title_changed": before_title != after_title,
        "paragraph_count_before": len(before_paras),
        "paragraph_count_after": len(after_paras),
        "paragraph_count_match": len(before_paras) == len(after_paras),
    }
    if key == "sewer":
        checks["no_heading_contract_kept"] = (len(after_headings) == 0)
    return checks


def new_rare_words_in_after(before_cand: dict, after_words: dict) -> list:
    before_candidate_lowers = {e["word"] for e in before_cand["candidates"]}
    before_all_lowers = set(before_cand["all_words_by_lower"].keys())
    new_words = []
    for lw, e in after_words.items():
        if lw in before_all_lowers:
            continue
        if e["rank"] is None or e["rank"] > RANK_THRESHOLD:
            new_words.append(e)
    new_words.sort(key=lambda e: (0, e["zipf_frequency"]) if e["rank"] is None
                    else (1, e["rank"]))
    return new_words


def _diff_lines(before_text: str, after_text: str) -> list:
    before_lines = before_text.splitlines()
    after_lines = after_text.splitlines()
    diff = difflib.unified_diff(before_lines, after_lines, lineterm="",
                                 fromfile="before", tofile="after")
    return list(diff)


def _decision_log_md(article_label: str, decisions: list) -> str:
    lines = [f"### {article_label} Decision Log\n",
             "| Word | Frequency Rank | 判定 | 理由 | Before | After |",
             "|---|---|---|---|---|---|"]
    for d in decisions:
        before = d["before_sentence"].replace("|", "\\|")
        after = d["after_sentence"].replace("|", "\\|")
        reasoning = d["reasoning"].replace("|", "\\|")
        lines.append(f"| {d['actual_form']} | {d['frequency_rank']} | "
                     f"{d['decision']} | {reasoning} | {before} | {after} |")
    return "\n".join(lines)


def cmd_analyze(out_dir: str) -> None:
    import wordfreq

    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)
    lemma_rank_map = bmod._build_lemma_rank_map(top20000)

    for key, path in ARTICLE_PATHS.items():
        raw = load_json(out_path(out_dir, f"{key}_raw_response.json"))
        before_text = load_text(path)
        after_text = raw["parsed"]["after_text"]
        decisions = raw["parsed"]["decisions"]
        notes = raw["parsed"]["notes_on_ambiguous_cases"]
        before_cand = raw["candidates_input"]

        save_text(out_path(out_dir, f"{key}_before.md"), before_text)
        save_text(out_path(out_dir, f"{key}_after.md"), after_text)

        after_cand = build_candidates(after_text, rank_of)
        struct = structure_check(key, before_text, after_text)
        new_rare = new_rare_words_in_after(
            before_cand, after_cand["all_words_by_lower"])

        before_levels = v1mod._level_metrics(before_text)
        after_levels = v1mod._level_metrics(after_text)

        band_before = bmod.measure_bands(before_text, lemma_rank_map)
        band_after = bmod.measure_bands(after_text, lemma_rank_map)

        decision_counts = Counter(d["decision"] for d in decisions)
        diff_lines = _diff_lines(before_text, after_text)

        metrics = {
            "article": key,
            "candidate_count": before_cand["candidate_count"],
            "decision_counts": dict(decision_counts),
            "structure_check": struct,
            "word_count_before": before_levels["word_count"],
            "word_count_after": after_levels["word_count"],
            "word_count_diff": after_levels["word_count"] - before_levels["word_count"],
            "sentence_count_before": before_levels["sentence_count"],
            "sentence_count_after": after_levels["sentence_count"],
            "sentence_count_diff": after_levels["sentence_count"] - before_levels["sentence_count"],
            "new_rare_words_gt12000_in_after": new_rare,
            "band_before_lemma_reference": band_before["bucket_token_counts"],
            "band_after_lemma_reference": band_after["bucket_token_counts"],
            "notes_on_ambiguous_cases": notes,
            "cost_jpy": raw["meta"]["cost_jpy"],
            "retried": raw["meta"]["retried"],
        }
        save_json(out_path(out_dir, f"{key}_metrics.json"), metrics)

        label = "Meta" if key == "meta" else "Sewer"
        save_text(out_path(out_dir, f"{key}_decision_log.md"),
                  f"# {key}_decision_log.md\n\n" + _decision_log_md(label, decisions) +
                  f"\n\n### notes_on_ambiguous_cases\n\n{notes}\n")

        diff_md = [f"# {key}_diff.md\n",
                   "## unified diff (Before -> After, full text)\n",
                   "```diff", *diff_lines, "```\n",
                   "## SIMPLIFY decisions のみ(宣言された変更文)\n"]
        for d in decisions:
            if d["decision"] == "SIMPLIFY":
                diff_md.append(f"- **{d['actual_form']}**\n"
                               f"  - Before: {d['before_sentence']}\n"
                               f"  - After: {d['after_sentence']}\n")
        save_text(out_path(out_dir, f"{key}_diff.md"), "\n".join(diff_md))

        print(f"[OK] {key}: analyze done. decision_counts={dict(decision_counts)} "
              f"structure_match(heading={struct['headings_match']}, "
              f"paragraph={struct['paragraph_count_match']}) "
              f"word_diff={metrics['word_count_diff']} "
              f"new_rare_words={len(new_rare)}")


# ------------------------------------------------------------
# STEP: assemble
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    calls = []
    total_jpy = 0.0
    for key in ARTICLE_PATHS:
        raw_path = out_path(out_dir, f"{key}_raw_response.json")
        if not os.path.exists(raw_path):
            print(f"[WARN] missing: {raw_path}")
            continue
        raw = load_json(raw_path)
        calls.append(raw["meta"])
        total_jpy += raw["meta"].get("cost_jpy", 0.0)
    cost = {
        "calls": calls,
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 5,
        "within_budget": total_jpy <= 5,
    }
    save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["candidates", "run", "analyze", "assemble"])
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "candidates":
        cmd_candidates(args.out_dir)
    elif args.step == "run":
        cmd_run(args.out_dir, args.budget_jpy, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
