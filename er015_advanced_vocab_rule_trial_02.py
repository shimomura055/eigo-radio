# ============================================================
# er015_advanced_vocab_rule_trial_02.py
# ADVANCED-VOCAB-RULE-TRIAL-02 (Fable委任, 管理ID
# ADVANCED-VOCAB-RULE-TRIAL-02, 2026-09-26)
# ============================================================
# 目的: ADVANCED-VOCAB-RULE-TRIAL-01(v1/fix01=v2)で残った
# USER_DECISION_REQUIRED論点(artery型がD[比喩保持]でKEEPされ、ユーザー
# 期待「artery型は原則平易化候補」と食い違った)を受け、ユーザーが定義した
# 仕様候補v2(Topic Core Word例外の新設 + Metaphor単独理由でのKEEP禁止 +
# 優先順位「テーマの根幹語 > 比喩表現 > その他」)をTrialとして検証する。
# Production Prompt/Validator/Production path/Standard側/既存Advanced本文
# artifactへは一切実装しない(Trialのみ)。個別語(sewer/artery等)を
# Promptへ名指しで指示することは一切しない(意味上の役割による一般ルールの
# みを与える)。
#
# 依存(re-use、変更しない):
#   - er015_advanced_vocab_rule_trial_01 (v1trial): ARTICLE_PATHS,
#       STRUCTURE_BLOCK, DEVELOPER_MESSAGE, sha256_of_file, get_client,
#       _load_pricing, _call_and_parse, structure_check, _diff_lines,
#       _format_rank, RANK_THRESHOLD, BORDERLINE_LOW/HIGH, out_path/
#       save_text/save_json/load_text/load_json
#   - er015_advanced_vocab_rule_trial_01_v2 (v2trial): lemma_candidates_v2,
#       rank_of_word_v2, build_candidates_v2 (lemma順位 min(surface,
#       lemma)、-er除去なしロジックをそのまま流用), fact_tokens_check,
#       _rank_of_map (v1trial経由)
# v1/v1_v2の成果物・スクリプトはどちらも変更しない。新規出力は
# er015_output/advanced_vocab_rule_trial_02/ のみに書く。
#
# 固定: 2 call(Meta 1回 + Sewer 1回)。previous_response_idなし、
# Web Searchなし、model=gpt-5.6-luna、reasoning effort=high。技術的失敗時
# のみ同一条件で1回まで再試行。費用上限: このTrial単体でJPY 5円
# (前回trial_01 v2実績JPY 1.9875、参考値。累計ではなくtrial_02単体の予算)。
#
# 実行方法:
#   .venv/Scripts/python.exe er015_advanced_vocab_rule_trial_02.py \
#       --out-dir er015_output/advanced_vocab_rule_trial_02 --step candidates
# ============================================================
from __future__ import annotations

import argparse
import os
from collections import Counter

import er015_advanced_vocab_rule_trial_01 as v1trial
import er015_advanced_vocab_rule_trial_01_v2 as v2trial

v1mod = v1trial.v1mod
v3mod = v1trial.v3mod
bmod = v1trial.bmod

RANK_THRESHOLD = v1trial.RANK_THRESHOLD
BORDERLINE_LOW = v1trial.BORDERLINE_LOW
BORDERLINE_HIGH = v1trial.BORDERLINE_HIGH
ARTICLE_PATHS = v1trial.ARTICLE_PATHS
STRUCTURE_BLOCK = v1trial.STRUCTURE_BLOCK
DEVELOPER_MESSAGE = v1trial.DEVELOPER_MESSAGE

out_path = v1trial.out_path
save_text = v1trial.save_text
load_text = v1trial.load_text
save_json = v1trial.save_json
load_json = v1trial.load_json
sha256_of_file = v1trial.sha256_of_file
get_client = v1trial.get_client
_load_pricing = v1trial._load_pricing
_call_and_parse = v1trial._call_and_parse
structure_check = v1trial.structure_check
_diff_lines = v1trial._diff_lines

build_candidates_v2 = v2trial.build_candidates_v2
lemma_candidates_v2 = v2trial.lemma_candidates_v2
rank_of_word_v2 = v2trial.rank_of_word_v2
fact_tokens_check = v2trial.fact_tokens_check
_rank_of_map = v1trial._rank_of_map

BUDGET_TOTAL_JPY = 5.0

V1_V2_DIR = os.path.join("er015_output", "advanced_vocab_rule_trial_01", "v2")


# ------------------------------------------------------------
# 仕様候補v2 日本語原文(逐語、ユーザー委任文からそのまま転記)
# ------------------------------------------------------------
SPEC_CANDIDATE_V2_JA = """\
# spec_candidate_v2_ja.md

## 仕様候補の修正(ユーザー定義、逐語、ADVANCED-VOCAB-RULE-TRIAL-02)

基本原則: 一般英語頻度順位 約12,000位超は原則平易化候補。既存例外A(既知の
易しい語から意味を容易に推測できる語)/B(日本語として十分定着し音から
意味が分かる語)/C(固有名詞・引用符内の実際の呼称)/D(簡単な語へ置換する
と意味精度または英語の自然さを明確に損なう不可欠語)は維持。定型表現例外
なし。その上で:

- **Topic Core Word**: 記事テーマの根幹に関わり、その語を失うと「何に
  ついての記事なのか」「そのTopicを学ぶ意味」が弱くなる中核Topic語は
  12,000位超でもKEEP可。単なる「記事中によく出る語」ではない。判断基準:
  Topicそのものを指す語/記事理解・Topic理解の中心にある語/将来的に
  Topic Word等で意味解説する価値が高い語。**AIがTopic Core Wordと判定
  した場合、なぜその語が記事Topicの根幹なのかを具体的に説明させる**
  (schemaに`topic_core_justification`必須)。
- **Metaphor**: AI Writerが説明・Storytellingのために作った比喩表現は、
  「比喩を維持したい」「Storytelling上きれいだから」という理由だけでは
  KEEPしない。12,000位超で他の例外に該当しなければ原則平易化対象。
- 優先順位: **テーマの根幹に関わる語 ＞ 比喩表現 ＞ その他**(個別語の
  決め打ちではなく意味上の役割で判断)。
- 判定ラベル: `KEEP — topic core word` / `KEEP — predictable
  morphology/compound` / `KEEP — established Japanese loanword` /
  `KEEP — proper noun / quoted designation` / `KEEP — indispensable /
  natural replacement unavailable` / `SIMPLIFY` / `BORDERLINE`。Dを
  使う場合は「比喩維持」を理由にしていないことをreasoningで明示させる
  (schemaに`is_metaphor: bool`、`exception_used`を追加)。

## 実装上の注記(Sonnet、Prompt翻訳時)

- 判定ラベル文字列は既存schema enumとの一貫性のため "KEEP -- X"
  (ハイフン2つ)表記をそのまま踏襲した(ユーザー原文の "KEEP — X"
  [emダッシュ]と意味は同一、表記のみ既存v1/v2 enumスタイルに合わせた)。
- `exception_used` の値は "A"/"B"/"C"/"D"/"E"(Topic Core Word)/"none"
  とした(Eという記号自体はユーザー原文にはなく、Sonnetが実装上付与した
  内部ラベル。Prompt本文ではTopic Core Wordという名称で説明している)。
"""

# ------------------------------------------------------------
# Prompt v3(英訳、v1のRULE_BLOCK_ENをベースに、C[固有名詞]へv2の
# 引用符内呼称の明確化を統合し、新たにE[Topic Core Word]とMetaphor制限・
# 優先順位・新フィールドを追加)
# ------------------------------------------------------------
RULE_BLOCK_EN_V3 = """Candidate difficulty rule (draft, under evaluation, v2 revision):

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
place name), OR it is a word inside quotation marks, or a title, \
designation, or nickname that a specific person or organization is \
reported to have actually used (for example, if the article states that \
Meta called certain workers "human concierges", the word "concierges" \
here is part of that reported fact, not an ordinary vocabulary choice). \
Such reported facts must not be simplified even if the word appears in the \
candidate list below.
D. Replacing it with an easier word would clearly hurt meaning precision \
or the naturalness of the English -- it is indispensable. Do not keep a \
word only because "it is a technical term" -- if a simple, natural, \
meaning-preserving substitute exists, simplify it.

Do NOT use "it is part of a fixed expression / idiom" as its own exception \
category. (For example, if "curtain" in "behind the curtain" is kept, the \
reason must be B [established Japanese loanword], never "it is part of an \
idiom.") A word inside a fixed expression that is still hard to guess \
should be judged normally, exactly like any other word.

In addition to A/B/C/D above, this revision of the rule (v2) adds one more \
exception and one restriction:

E. Topic Core Word: a word ranked beyond ~12,000 may also be KEPT if it is \
so central to what THIS SPECIFIC article's theme actually is that losing \
it would weaken "what this article is about" or "the reason for learning \
this topic." This is NOT simply "a word that appears often in the \
article." Judge it by: (i) whether the word names the topic itself, (ii) \
whether it is central to understanding the article or the topic, (iii) \
whether it would have high value for a future Topic Word / meaning \
explanation about this topic. If, and only if, you decide a word is a \
Topic Core Word, you must give a concrete, article-specific explanation \
of exactly why this word is central to THIS article's topic, in the \
"topic_core_justification" output field. A vague or generic statement \
(for example, "it's an important word in the article") is not acceptable \
and must not be used as the justification.

Metaphor restriction: if a word's use in the article is part of a \
metaphor or storytelling device that the AI writer created for \
explanatory or storytelling effect, do NOT keep the word only because \
"the metaphor should be preserved" or "it reads nicely as storytelling." \
Beyond ~12,000, a word used only for such a metaphor is, by default, a \
candidate for simplification, unless one of exceptions A/B/C/D/E \
genuinely applies to it for a reason that is independent of the metaphor \
itself. If you rely on exception D for a word that is part of a metaphor, \
your reasoning must explicitly state that you are NOT keeping it merely \
to preserve the metaphor or the storytelling, and must instead name the \
specific, non-metaphor reason the word is indispensable.

Priority when more than one consideration could apply to the same word: \
judge each word by its actual semantic role in this article, not by \
deciding individual words in advance. A word that is central to the \
article's theme (exception E, Topic Core Word) outranks a word that is \
merely part of a metaphor, which in turn outranks other considerations.

For each candidate word listed below, decide:
- "KEEP -- topic core word" (exception E)
- "KEEP -- predictable morphology/compound" (exception A)
- "KEEP -- established Japanese loanword" (exception B)
- "KEEP -- proper noun / quoted designation" (exception C)
- "KEEP -- indispensable / natural replacement unavailable" (exception D)
- "SIMPLIFY" (replace it with a simpler, natural word or phrase)
- "BORDERLINE" (only if you are genuinely unsure; explain why in \
notes_on_ambiguous_cases)

For each candidate word, also fill in these additional fields:
- "is_metaphor" (boolean): true if this word's use in the article is part \
of a metaphor or storytelling device created by the AI writer, false \
otherwise.
- "exception_used" (string): which single reason this decision is \
actually based on -- "A", "B", "C", "D", "E", or "none" (use "none" for \
SIMPLIFY/BORDERLINE decisions).
- "topic_core_justification" (string): if exception_used is "E", a \
concrete, article-specific explanation (as described above) of why this \
word is central to the article's topic; otherwise leave this field as an \
empty string.
"""

TASK_TAIL_V3 = """\
Only change the specific candidate words you decide to SIMPLIFY (and, only \
where grammatically necessary, a minimal amount of immediately surrounding \
wording so the sentence still reads naturally). Do not do a general \
rewrite of sentences that contain no candidate word. Do not add new facts, \
explanations, examples, or opinions. Do not remove any fact. Do not change \
the meaning, the tone, the storytelling, or the ending logic -- except \
that, under this rule, a word used only for a metaphor or storytelling \
device is a normal simplification candidate once it ranks beyond ~12,000, \
unless exception A/B/C/D/E genuinely applies to it for a reason \
independent of the metaphor (see the Metaphor restriction above). Keep \
the title unchanged unless it contains a candidate word you decide to \
SIMPLIFY.

Output:
- "decisions": exactly one entry per candidate word listed below, in the \
same order, each with word, actual_form, frequency_rank (copy the \
frequency_rank value exactly as given below -- do not recompute or guess \
it), decision, is_metaphor, exception_used, topic_core_justification, \
reasoning (one or two sentences, in English), before_sentence (the exact \
original sentence that contains this word), after_sentence (the resulting \
sentence in your rewritten article -- for KEEP decisions this should be \
identical or nearly identical to before_sentence).
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


DECISION_ENUM_V3 = [
    "KEEP -- topic core word",
    "KEEP -- predictable morphology/compound",
    "KEEP -- established Japanese loanword",
    "KEEP -- proper noun / quoted designation",
    "KEEP -- indispensable / natural replacement unavailable",
    "SIMPLIFY",
    "BORDERLINE",
]


def _decision_item_schema_v3() -> dict:
    return {
        "type": "object",
        "properties": {
            "word": {"type": "string"},
            "actual_form": {"type": "string"},
            "frequency_rank": {"type": "string"},
            "decision": {"type": "string", "enum": DECISION_ENUM_V3},
            "is_metaphor": {"type": "boolean"},
            "exception_used": {
                "type": "string",
                "enum": ["A", "B", "C", "D", "E", "none"],
            },
            "topic_core_justification": {"type": "string"},
            "reasoning": {"type": "string"},
            "before_sentence": {"type": "string"},
            "after_sentence": {"type": "string"},
        },
        "required": ["word", "actual_form", "frequency_rank", "decision",
                     "is_metaphor", "exception_used",
                     "topic_core_justification", "reasoning",
                     "before_sentence", "after_sentence"],
        "additionalProperties": False,
    }


def build_json_schema_v3(n_candidates: int) -> dict:
    return {
        "name": "advanced_vocab_rule_trial_v2",
        "schema": {
            "type": "object",
            "properties": {
                "decisions": {
                    "type": "array",
                    "minItems": n_candidates,
                    "maxItems": n_candidates,
                    "items": _decision_item_schema_v3(),
                },
                "after_text": {"type": "string"},
                "notes_on_ambiguous_cases": {"type": "string"},
            },
            "required": ["decisions", "after_text", "notes_on_ambiguous_cases"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def _candidates_block_text(candidates: list) -> str:
    return v2trial._candidates_block_text(candidates)


def _borderline_block_text(borderline: list) -> str:
    return v2trial._borderline_block_text(borderline)


# ------------------------------------------------------------
# STEP: candidates (v2ロジックそのまま流用)
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
        "method": "wordfreq.top_n_list('en', 20000) (v1/v2と同一method・"
                  "同一version)",
        "ranking_unit": ("rank = min(rank(surface form), rank(best lemma "
                          "candidate)). ADVANCED-VOCAB-RULE-TRIAL-01 v2 "
                          "(fix01)のlemma_candidates_v2()をそのまま再利用 "
                          "(-s/-es/-ies/-ed/-ing/-lyの単純規則のみ、-er/-est "
                          "比較級除去は使わない)。"),
        "rank_threshold": RANK_THRESHOLD,
        "borderline_band": [BORDERLINE_LOW, BORDERLINE_HIGH],
    })

    save_text(out_path(out_dir, "spec_candidate_v2_ja.md"), SPEC_CANDIDATE_V2_JA)

    for key, path in ARTICLE_PATHS.items():
        text = load_text(path)
        result = build_candidates_v2(text, rank_of)
        save_json(out_path(out_dir, f"candidates_{key}.json"), result)
        print(f"[OK] candidates_{key}.json written. "
              f"candidate_count={result['candidate_count']} "
              f"borderline_count={result['borderline_count']} "
              f"excluded_proper={result['excluded_proper_noun_count']}")


# ------------------------------------------------------------
# STEP: run (Meta 1 call, Sewer 1 call)
# ------------------------------------------------------------
def cmd_run(out_dir: str, force: bool) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    v1mod.install_logger(out_dir)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    client = get_client()
    pricing = _load_pricing()
    total_jpy = 0.0
    print(f"[INFO] trial_02 standalone budget={BUDGET_TOTAL_JPY} JPY "
          f"(reference only, prior trial_01 v2 actual=1.9875 JPY)")

    for key, path in ARTICLE_PATHS.items():
        dst = out_path(out_dir, f"{key}_raw_response.json")
        if os.path.exists(dst) and not force:
            existing = load_json(dst)
            total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
            print(f"[SKIP] existing: {dst} (cumulative so far="
                  f"{round(total_jpy, 4)} JPY)")
            continue

        article_text = load_text(path)
        cand_result = build_candidates_v2(article_text, rank_of)
        n_candidates = cand_result["candidate_count"]
        candidates_block = _candidates_block_text(cand_result["candidates"])
        borderline_block = _borderline_block_text(cand_result["borderline_reference"])

        user_message = (RULE_BLOCK_EN_V3 + "\n" + STRUCTURE_BLOCK[key] + "\n\n" +
                         TASK_TAIL_V3.format(candidates_block=candidates_block,
                                              borderline_block=borderline_block,
                                              article_text=article_text))
        schema = build_json_schema_v3(n_candidates)

        save_text(out_path(out_dir, f"prompt_advanced_vocab_rule_v3_{key}.txt"),
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
              f"cumulative_jpy(trial_02)={round(total_jpy, 4)}")

        if parsed is None:
            stop = {"stop_reason": f"parse/technical failure after retry ({key})",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] parse/technical failure after retry ({key})")
            raise SystemExit(1)

        if total_jpy > BUDGET_TOTAL_JPY:
            stop = {"stop_reason": f"budget (trial_02) exceeded after {key}",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": BUDGET_TOTAL_JPY}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after {key}: "
                  f"{round(total_jpy, 4)} > {BUDGET_TOTAL_JPY}")
            raise SystemExit(1)

    print(f"[DONE] run complete. total_cost_jpy(trial_02)={round(total_jpy, 4)} "
          f"budget_jpy={BUDGET_TOTAL_JPY}")


# ------------------------------------------------------------
# STEP: analyze
# ------------------------------------------------------------
def _decision_log_md_v3(article_label: str, decisions: list, cand_by_word: dict) -> str:
    lines = [f"### {article_label} Decision Log (v3, ADVANCED-VOCAB-RULE-TRIAL-02)\n",
             "| Word | surface | lemma | 採用rank | 判定 | "
             "使用した例外/理由(Topic Coreならjustification全文) | "
             "is_metaphor | Before | After |",
             "|---|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        before = d["before_sentence"].replace("|", "\\|").replace("\n", " ")
        after = d["after_sentence"].replace("|", "\\|").replace("\n", " ")
        c = cand_by_word.get(d["word"], {})
        surface = c.get("surface", d["word"])
        surface_rank = c.get("surface_rank")
        lemma_used = c.get("lemma_used") or "(none)"
        reason_cell = d["reasoning"].replace("|", "\\|")
        if d.get("exception_used") == "E":
            tcj = d.get("topic_core_justification", "").replace("|", "\\|")
            reason_cell = (f"exception_used=E (Topic Core Word); "
                            f"topic_core_justification: {tcj}; reasoning: "
                            f"{reason_cell}")
        else:
            reason_cell = (f"exception_used={d.get('exception_used')}; "
                            f"{reason_cell}")
        lines.append(
            f"| {d['actual_form']} | {surface} | {lemma_used} | "
            f"{d['frequency_rank']} | {d['decision']} | {reason_cell} | "
            f"{d.get('is_metaphor')} | {before} | {after} |")
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
        cand_by_word = before_cand["all_words_by_lower"]

        save_text(out_path(out_dir, f"{key}_before.md"), before_text)
        save_text(out_path(out_dir, f"{key}_after.md"), after_text)

        after_cand = build_candidates_v2(after_text, rank_of)
        struct = structure_check(key, before_text, after_text)
        new_rare = v1trial.new_rare_words_in_after(
            before_cand, after_cand["all_words_by_lower"])

        before_levels = v1mod._level_metrics(before_text)
        after_levels = v1mod._level_metrics(after_text)

        band_before = bmod.measure_bands(before_text, lemma_rank_map)
        band_after = bmod.measure_bands(after_text, lemma_rank_map)

        decision_counts = Counter(d["decision"] for d in decisions)
        exception_counts = Counter(d.get("exception_used") for d in decisions)
        metaphor_counts = Counter(d.get("is_metaphor") for d in decisions)
        diff_lines = _diff_lines(before_text, after_text)
        fact_check = fact_tokens_check(before_text, after_text)

        metrics = {
            "article": key,
            "candidate_count": before_cand["candidate_count"],
            "decision_counts": dict(decision_counts),
            "exception_used_counts": {str(k): v for k, v in exception_counts.items()},
            "is_metaphor_counts": {str(k): v for k, v in metaphor_counts.items()},
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
            "fact_tokens_check": fact_check,
        }
        save_json(out_path(out_dir, f"{key}_metrics.json"), metrics)
        save_json(out_path(out_dir, f"{key}_fact_tokens_check.json"), fact_check)

        label = "Meta" if key == "meta" else "Sewer"
        save_text(out_path(out_dir, f"{key}_decision_log.md"),
                  f"# {key}_decision_log.md (v3, TRIAL-02)\n\n" +
                  _decision_log_md_v3(label, decisions, cand_by_word) +
                  f"\n\n### notes_on_ambiguous_cases\n\n{notes}\n")

        diff_md = [f"# {key}_diff.md (v3, TRIAL-02)\n",
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
              f"exception_used_counts={dict(exception_counts)} "
              f"structure_match(heading={struct['headings_match']}, "
              f"paragraph={struct['paragraph_count_match']}) "
              f"word_diff={metrics['word_count_diff']} "
              f"new_rare_words={len(new_rare)} "
              f"fact_tokens_match={fact_check['overall_fact_tokens_match']}")


# ------------------------------------------------------------
# STEP: compare (旧v2[trial_01/v2] vs 今回[trial_02] 比較表)
# ------------------------------------------------------------
def cmd_compare(out_dir: str) -> None:
    for key in ARTICLE_PATHS:
        old_raw_path = os.path.join(V1_V2_DIR, f"{key}_raw_response.json")
        new_raw_path = out_path(out_dir, f"{key}_raw_response.json")
        if not os.path.exists(old_raw_path) or not os.path.exists(new_raw_path):
            print(f"[WARN] missing raw response for compare: {key}")
            continue
        old_raw = load_json(old_raw_path)
        new_raw = load_json(new_raw_path)
        old_by_word = {d["word"]: d for d in old_raw["parsed"]["decisions"]}
        new_by_word = {d["word"]: d for d in new_raw["parsed"]["decisions"]}
        new_cand_by_word = new_raw["candidates_input"]["all_words_by_lower"]

        all_words = sorted(set(old_by_word) | set(new_by_word))
        lines = [f"# {key}_v1v2_vs_trial02_compare.md\n",
                 "| Word | Rank | 旧判定(trial_01 v2) | 新判定(trial_02) | "
                 "新しい判断理由 | Before->After |",
                 "|---|---|---|---|---|---|"]
        for w in all_words:
            old_d = old_by_word.get(w)
            new_d = new_by_word.get(w)
            rank = new_cand_by_word.get(w, {}).get("rank_display", "-")
            old_decision = old_d["decision"] if old_d else "(候補外)"
            new_decision = new_d["decision"] if new_d else "(候補外)"
            if new_d:
                reason = new_d["reasoning"].replace("|", "\\|")
                if new_d.get("exception_used") == "E":
                    reason = (f"[Topic Core] {new_d.get('topic_core_justification', '').replace('|', chr(92)+'|')} "
                               f"| {reason}")
                reason = f"is_metaphor={new_d.get('is_metaphor')}; {reason}"
                before_after = (f"{new_d['before_sentence'].replace(chr(10), ' ')} "
                                 f"-> {new_d['after_sentence'].replace(chr(10), ' ')}").replace("|", "\\|")
            else:
                reason = "(trial_02では候補外)"
                before_after = "-"
            lines.append(f"| {w} | {rank} | {old_decision} | {new_decision} | "
                          f"{reason} | {before_after} |")
        save_text(out_path(out_dir, f"{key}_v1v2_vs_trial02_compare.md"),
                  "\n".join(lines))
        print(f"[OK] {key}_v1v2_vs_trial02_compare.md written. "
              f"words={len(all_words)}")


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
        "budget_jpy": BUDGET_TOTAL_JPY,
        "within_budget": total_jpy <= BUDGET_TOTAL_JPY,
        "reference_prior_trial_01_v2_cost_jpy": 1.9875,
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
                     choices=["candidates", "run", "analyze", "compare",
                              "assemble"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "candidates":
        cmd_candidates(args.out_dir)
    elif args.step == "run":
        cmd_run(args.out_dir, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "compare":
        cmd_compare(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
