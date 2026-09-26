# ============================================================
# er015_vocab_abcd_strict_exception_trial_01.py
# VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01 (Trialのみ、最大VALIDATED、
# Production Prompt/path変更禁止、2026-09-26)
# ============================================================
# 目的: STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 / ADVANCED-VOCAB-RULE-
# TRIAL-01(v2)で使ったA/B/C/D例外構造のうち、B(日本語定着語)・
# C(固有名詞)・D(不可欠語)の運用が緩すぎたため、前回Trial(Standard
# 6,000位版)でSewer記事の一般名詞 "septic"(「combined septic tank」という
# 記事内の引用符付きフレーズの一部にすぎない)が C(固有名詞/固有の引用
# 名称)として誤ってKEEPされる事例が生じた。本Trialはユーザーが逐語で確定
# した厳格なB/C/D定義(下記SPEC_STRICT_JA)へPrompt文言を差し替え、
# Standard/Advanced両方で同一記事(前回と同一素材、新規Researchなし)へ
# 再適用した場合の判定を検証する。Production Prompt
# (er003_v1_n3_01_standard_a2_generate.py /
# er003_v1_n3_01_advanced_adaptation_generate.py)は一切変更しない。
#
# 前回誤判定の原因(cmd_misjudgment_analysisで詳細分析、$0):
# ADVANCED-VOCAB-RULE-TRIAL-01 v2 (er015_advanced_vocab_rule_trial_01_v2.py)
# でC(固有名詞)の適用範囲を明確化した際に追加した一文
#   "Words that appear inside quotation marks in the article, ... are facts
#   of the article. Do not simplify such a word even if it appears in the
#   candidate list below; treat it under exception C ..."
# が、「記事中で引用符に入っている語」というだけで固有名詞/固有の引用名称
# と同列に扱えてしまう構造になっていた。Meta記事の "human concierges"
# (Metaが実際にそう呼んだという事実)を守るための追記だったが、Sewer記事の
# "combined septic tank"(単にWriterが読者への導入として引用符を使った
# 一般名詞句)まで誤って救済してしまった。本Trialの厳格C定義は、
# 「引用符に入っているだけ」では不十分であることを明記し、個別語名
# (septic)はPromptに書かず定義文のみで正しい判定へ導けるかを検証する。
#
# 依存(re-use、新規ロジックは閾値・スキーマ・Prompt文言のみ):
#   - er015_advanced_vocab_rule_trial_01 (v1trial): out_path/save_text/
#     load_text/save_json/load_json/sha256_of_file/get_client/
#     _load_pricing/_call_and_parse/structure_check/_diff_lines/
#     _format_rank/_rank_of_map/STRUCTURE_BLOCK/new_rare_words_in_after
#   - er015_advanced_vocab_rule_trial_01_v2 (v2mod): lemma_candidates_v2/
#     rank_of_word_v2/fact_tokens_check (修正A・修正Bのlemma順位ロジックを
#     Standard/Advanced両方でそのまま流用し、思想差ゼロを維持する)
#   - er015_news_standard_a2_vocab_effectiveness_trial_01 (v3mod、
#     v2mod経由): extract_content_words/capitalized_positions
#   - er015_news_standard_a2_vocab_banding_trial_01 (bmod、v2mod経由):
#     measure_bands/_build_lemma_rank_map (band参考値のみ)
#
# 入力(前回と同一、Before、新規Researchなし):
#   - Standard Meta: er012_output/e_family_two_level_wiring_01/meta/a2/
#     article.md
#   - Standard Sewer: er015_output/news_standard_a2_vocab_6000_cutoff_
#     trial_01/a2v5_standard_sewer.md
#   - Advanced Meta: er012_output/e_family_two_level_wiring_01/meta/b1b/
#     article.md
#   - Advanced Sewer: er015_output/news_natural_advanced_standard_a2_
#     trial_01/a1_advanced_sewer.md
# 順位ソース: wordfreq 3.1.1 top_n_list('en', 20000)(既存install再利用)。
# rank = min(rank(surface), rank(best lemma candidate))、v2mod同一ロジック。
#
# 固定: 4 call(Standard Meta/Sewer, Advanced Meta/Sewer)。
# previous_response_idなし、Web Searchなし、model=gpt-5.6-luna、
# reasoning effort=high。費用上限 JPY 10円(本Trial単独の予算)。
#
# 実行方法:
#   .venv/Scripts/python.exe er015_vocab_abcd_strict_exception_trial_01.py \
#       --out-dir er015_output/vocab_abcd_strict_exception_trial_01 \
#       --step candidates
# ============================================================
from __future__ import annotations

import argparse
import difflib
import os
from collections import Counter

import er015_advanced_vocab_rule_trial_01 as v1trial
import er015_advanced_vocab_rule_trial_01_v2 as v2mod

v3mod = v2mod.v3mod
bmod = v2mod.bmod

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
_format_rank = v1trial._format_rank
_rank_of_map = v1trial._rank_of_map
STRUCTURE_BLOCK = v1trial.STRUCTURE_BLOCK

lemma_candidates_v2 = v2mod.lemma_candidates_v2
rank_of_word_v2 = v2mod.rank_of_word_v2
fact_tokens_check = v2mod.fact_tokens_check

BUDGET_TOTAL_JPY = 10.0

# ------------------------------------------------------------
# ユーザー決定の厳格仕様(日本語原文、逐語。spec_strict_ja.md へ保存)
# ------------------------------------------------------------
SPEC_STRICT_JA = """\
## ユーザー決定の厳格仕様(逐語、2026-09-26)

- 閾値: Standard 約6,000位 / Advanced 約12,000位(閾値超を原則平易化候補。\
必ず置換ではなく、より簡単で自然な表現がある場合に平易化を強く優先)。\
B/C/D定義は両Levelで同一。
- A(維持): 易しい既知語から構成され、英語学習者が構造から意味を自然に推測\
できる形態・複合語。単に形態素分解できるだけではKEEPしない。
- B(厳格): 日本語で使われているだけでは不十分。日本人英語学習者がその\
英語の語形・発音を見聞きしたとき、日本語として知っている語と自然に結び付き、\
意味をほぼ迷わず理解できる場合だけB。Bにしない: 英語語形との対応が分かり\
にくい/日本語で専門領域にしか定着していない/英語文中で理解しにくい/\
「カタカナ語として存在する」だけ。特に leak / pause / curtain を再判定。
- C(厳格): 本当の固有名詞・公式名称・固有の引用名称だけ(人名・地名・\
組織名・商品/サービス名・公式名称・報道上その呼称自体がFactになっている\
固有の引用名称[例: Metaが実際に "human concierges" と呼んだ])。Cにしない: \
一般名詞が引用符に入っているだけ/一般的な技術用語/記事中で引用されている\
だけ/Writerが強調のため引用符を付けただけ。septic / septic tank をCと\
判定してはならない(Promptに個別語名は書かず、定義で導く)。
- D(厳格): より易しい自然な語・表現へ置換すると、記事の意味の核心・事実\
精度・必要なニュアンスが明確に壊れる場合だけKEEP。Dにしない: 専門用語\
だから/元記事で使われているから/比喩として少し自然だから/Writerの表現\
として気に入っているから/置換すると少し雰囲気が変わるから。可能な簡単語\
があればSIMPLIFY優先。特に artery / sewer(s) / flush / septic を再評価。

## 対象(既存本文、新規Researchなし)
- Standard: Meta er012_output/e_family_two_level_wiring_01/meta/a2/\
article.md、Sewer er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/\
a2v5_standard_sewer.md(前回と同一)
- Advanced: Meta er012_output/e_family_two_level_wiring_01/meta/b1b/\
article.md、Sewer er015_output/news_natural_advanced_standard_a2_trial_01/\
a1_advanced_sewer.md(Advanced v2 Trialと同一)
"""

# ------------------------------------------------------------
# レベル別設定(閾値のみ差、B/C/D定義文言は完全同一)
# ------------------------------------------------------------
LEVEL_THRESHOLD = {"standard": 6000, "advanced": 12000}
LEVEL_BORDERLINE = {"standard": (5000, 6000), "advanced": (10000, 12000)}
LEVEL_CEFR_LABEL = {
    "standard": "CEFR A2 (\"Standard\")",
    "advanced": "CEFR B1 (\"Advanced\")",
}

ARTICLE_SPECS = {
    "standard_meta": {
        "level": "standard", "key": "meta",
        "path": os.path.join(
            "er012_output", "e_family_two_level_wiring_01", "meta", "a2",
            "article.md"),
    },
    "standard_sewer": {
        "level": "standard", "key": "sewer",
        "path": os.path.join(
            "er015_output", "news_standard_a2_vocab_6000_cutoff_trial_01",
            "a2v5_standard_sewer.md"),
    },
    "advanced_meta": {
        "level": "advanced", "key": "meta",
        "path": os.path.join(
            "er012_output", "e_family_two_level_wiring_01", "meta", "b1b",
            "article.md"),
    },
    "advanced_sewer": {
        "level": "advanced", "key": "sewer",
        "path": os.path.join(
            "er015_output", "news_natural_advanced_standard_a2_trial_01",
            "a1_advanced_sewer.md"),
    },
}

# 前回Trialの結果(旧判定の参照先、比較専用。読み込み専用、上書きしない)
PREVIOUS_RAW_RESPONSE = {
    "standard_meta": os.path.join(
        "er015_output", "standard_vocab_abcd_alignment_trial_01",
        "meta_raw_response.json"),
    "standard_sewer": os.path.join(
        "er015_output", "standard_vocab_abcd_alignment_trial_01",
        "sewer_raw_response.json"),
    "advanced_meta": os.path.join(
        "er015_output", "advanced_vocab_rule_trial_01", "v2",
        "meta_raw_response.json"),
    "advanced_sewer": os.path.join(
        "er015_output", "advanced_vocab_rule_trial_01", "v2",
        "sewer_raw_response.json"),
}
PREVIOUS_LABEL = {
    "standard_meta": "STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 (閾値6,000版)",
    "standard_sewer": "STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 (閾値6,000版)",
    "advanced_meta": "ADVANCED-VOCAB-RULE-TRIAL-01 v2 (閾値12,000版)",
    "advanced_sewer": "ADVANCED-VOCAB-RULE-TRIAL-01 v2 (閾値12,000版)",
}


# ------------------------------------------------------------
# Prompt: 厳格A/B/C/D定義(英訳、逐語相当)。閾値のみ{threshold}で差し替え。
# ------------------------------------------------------------
DEVELOPER_MESSAGE_TEMPLATE = (
    "You are an editor testing a STRICT candidate vocabulary-difficulty "
    "rule for {cefr_label} level news articles written for Japanese adult "
    "English learners. This rule is a draft under evaluation, not yet "
    "approved. For the specific difficult words listed below, you decide "
    "word by word whether to keep the word or replace it with a simpler, "
    "natural alternative, following the rule exactly. You must apply the "
    "KEEP exceptions (A/B/C/D) narrowly and strictly, exactly as defined "
    "below -- do not use them as convenient excuses to avoid "
    "simplification. You must not change anything else in the article."
)

RULE_BLOCK_EN_STRICT_TEMPLATE = """\
Candidate difficulty rule (STRICT definitions, user-confirmed 2026-09-26):

Words that rank below roughly the top {threshold} most frequent general \
English words are, in principle, candidates for simplification. This is \
NOT a mechanical ban list: simplification must not be a forced, automatic \
replacement, but whenever a simpler and more natural expression exists \
without harming meaning, simplification should be strongly preferred. The \
definitions of exceptions B, C, and D below are identical for both the \
Standard and the Advanced level; only the threshold number differs between \
levels.

A word ranked beyond ~{threshold} may still be KEPT (not simplified) only \
if one of these STRICT conditions applies. Treat B, C, and D narrowly: \
each is a strict exception, not a convenient escape hatch.

A (KEEP -- predictable morphology/compound). The word is a form or \
compound built from an already-easy, already-known word or word part, \
such that an English learner can naturally guess its meaning from that \
structure (for example: "onstage" = on + stage, "wastewater" = waste + \
water, "understandable" = understand + -able). Being decomposable into \
morphemes is NOT enough by itself to KEEP a word; the learner must \
actually be able to guess the meaning that way.

B (KEEP -- established Japanese loanword, STRICT). It is NOT enough that \
the word happens to be used in Japanese somewhere. This is B only when, \
on seeing or hearing this English word's form and pronunciation, a \
Japanese English learner naturally and almost unambiguously connects it to \
a word they already know in Japanese, and understands its meaning with \
little doubt. Do NOT use reason B when any of the following is true: the \
correspondence between the English word-form and the Japanese loanword is \
hard to recognize; the word is established in Japanese only within a \
narrow specialist/technical field, not in everyday Japanese; the word is \
hard to understand when it is actually read here in this English \
sentence, even though a loanword exists; or the only support you can \
offer is that "a katakana spelling of this word exists." In particular, \
re-judge the words "leak", "pause", and "curtain" carefully against this \
strict standard rather than assuming that a katakana form is automatically \
enough.

C (KEEP -- proper noun / genuine quoted designation, STRICT). Use this \
ONLY for a genuine proper noun or an official/specific quoted designation: \
a real person's name, a real place name, a real organization's name, a \
specific product or service name, an official name, or a specific quoted \
designation that is itself reported as a fact of the article (for \
example, if the article reports that Meta actually called certain workers \
"human concierges", the phrase "human concierges" is that reported fact \
and must be kept exactly). Do NOT use reason C when any of the following \
is true: the word is simply a common noun that happens to appear inside \
quotation marks in the article; it is an ordinary general or technical \
term, even if quoted; it is merely quoted somewhere in the article (for \
example, quoting how a news report phrased something) without being a \
specific person's or organization's own name or designation; or the \
writer added quotation marks only for emphasis or to introduce a term to \
the reader. A common, general technical term is never C merely because it \
appears inside quotation marks.

D (KEEP -- indispensable / natural replacement unavailable, STRICT). KEEP \
under D ONLY when replacing the word with an easier, natural word or \
expression would clearly and demonstrably break the article's core \
meaning, factual precision, or a nuance that a reader actually needs in \
order to understand the point. Do NOT use reason D merely because: the \
word is a technical term; it was the word used in the source article; it \
works reasonably well as part of a metaphor or storytelling image; you \
(the model) like it as a stylistic choice; or replacing it would only \
slightly change the mood or flavor of the sentence. If a simpler, \
natural, meaning-preserving word or phrase is available, SIMPLIFY is \
strongly preferred over D. In particular, re-evaluate the words "artery", \
"sewer"/"sewers", "flush", and "septic" carefully against this strict \
standard; keep them under D only if you can demonstrate that a simpler \
alternative would truly break meaning, factual precision, or a nuance the \
reader needs -- not merely because they are the precise technical term or \
part of a metaphor.

Do NOT use "it is part of a fixed expression / idiom" as its own exception \
category. A word inside a fixed expression that is still hard to guess \
should be judged normally under A/B/C/D above, exactly like any other \
word.
"""

TASK_TAIL_STRICT = """\
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
it), decision (exactly one of "KEEP-A", "KEEP-B", "KEEP-C", "KEEP-D", \
"SIMPLIFY", "BORDERLINE", matching exception A/B/C/D above), reasoning \
(one or two sentences, in English, explicitly stating which strict \
condition is met and, if relevant, why the "do NOT use this reason when" \
cases above do not apply here), replacement_if_simplify (the simpler word \
or phrase you actually used in after_text, or the exact string "N/A" if \
the decision is not SIMPLIFY), meaning_or_fact_change (exactly one of \
"none", "minor", "major" -- your own honest assessment of how much the \
resulting sentence's meaning or factual precision changed from the \
original; for KEEP decisions this should normally be "none"), \
before_sentence (the exact original sentence that contains this word), \
after_sentence (the resulting sentence in your rewritten article -- for \
KEEP decisions this should be identical or nearly identical to \
before_sentence).
- "after_text": the full rewritten article (title + body), in the same \
format as the original.
- "notes_on_ambiguous_cases": a short note (can be empty) on any word \
where the KEEP/SIMPLIFY line was genuinely hard to draw.

[Candidate words -- rank below ~{threshold}, decide KEEP-A/KEEP-B/KEEP-C/\
KEEP-D/SIMPLIFY/BORDERLINE for each]
{candidates_block}

[Reference only -- words ranked {borderline_range} (near the threshold), \
shown so you can calibrate the rule; these are NOT candidates and do not \
need a decision unless they also appear in the candidate list above]
{borderline_block}

[Article]
{article_text}
"""


def _unified_diff_md(label: str, before: str, after: str) -> list:
    return list(difflib.unified_diff(
        before.splitlines(), after.splitlines(),
        fromfile=f"{label} (v2, threshold=12,000)",
        tofile=f"{label} (strict, threshold=12,000)", lineterm=""))


def write_prompt_diff(out_dir: str) -> None:
    strict_at_12000 = RULE_BLOCK_EN_STRICT_TEMPLATE.format(threshold="12,000")
    lines = [
        "# prompt_diff_v2_vs_strict.md\n",
        "## 目的\n",
        "前回Trial(ADVANCED-VOCAB-RULE-TRIAL-01 v2 /"
        " STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01が流用したv2の"
        "RULE_BLOCK_EN_V2)と、本Trialの厳格版RULE_BLOCK_EN_STRICTの"
        "差分を、閾値を12,000に揃えたうえで逐語diffとして示す"
        "(数字の違いによる差分ノイズを除去するため)。\n",
        "## 結論\n",
        "- 一般原則(閾値超は原則平易化候補、機械的禁止リストではない)と"
        "Aの定義は実質変更なし。\n",
        "- Bの定義に、「カタカナ語が存在するだけでは不十分」「英語語形との"
        "対応が分かりにくい/専門領域限定/文中で理解しにくい場合はBに"
        "しない」という否定条件と、leak/pause/curtainの再判定指示を明示的に"
        "追加した。\n",
        "- Cの定義から、v2で追加した「記事中で引用符に入っている語は"
        "(固有名詞と同列に)事実として保護する」という一般化された条件を"
        "削除し、「本当の固有名詞・公式名称・固有の引用名称」のみに"
        "限定した。「一般名詞が引用符に入っているだけ」「一般的な技術用語」"
        "「記事中で引用されているだけ」「Writerが強調のため引用符を付けた"
        "だけ」は明示的にCの否定条件とした(個別語名septicはPromptに"
        "書かず、定義文のみで導けるかを検証する)。\n",
        "- Dの定義に、「専門用語だから/元記事で使われているから/比喩として"
        "少し自然だから/Writerの表現として気に入っているから/置換すると"
        "少し雰囲気が変わるから」は理由にしない、という否定条件と、"
        "artery/sewer(s)/flush/septicの再評価指示を明示的に追加した。\n",
        "\n## RULE_BLOCK_EN diff (v2 -> strict、閾値は両方12,000に揃えて"
        "比較)\n",
        "```diff",
        *_unified_diff_md("RULE_BLOCK_EN", v2mod.RULE_BLOCK_EN_V2,
                           strict_at_12000),
        "```\n",
    ]
    save_text(out_path(out_dir, "prompt_diff_v2_vs_strict.md"),
              "\n".join(lines))


def write_spec_strict_ja(out_dir: str) -> None:
    save_text(out_path(out_dir, "spec_strict_ja.md"),
              "# spec_strict_ja.md\n\n" + SPEC_STRICT_JA)


# ------------------------------------------------------------
# 候補語抽出(v2のlemma順位ロジックを流用、閾値のみレベル別)
# ------------------------------------------------------------
def build_candidates(text: str, rank_of: dict, threshold: int,
                      borderline_low: int, borderline_high: int) -> dict:
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
        rk = rank_of_word_v2(lw, rank_of)
        rank = rk["rank"]
        zf = None
        if rank is None:
            zf = wordfreq.zipf_frequency(lw, "en")

        entry = {
            "word": lw,
            "actual_form": most_common,
            "surface_forms": sorted(set(forms)),
            "count": len(forms),
            "surface_rank": rk["surface_rank"],
            "lemma_candidates_considered": rk["lemma_candidates_considered"],
            "lemma_used": rk["lemma_used"],
            "lemma_rank": rk["lemma_rank"],
            "rank": rank,
            "rank_source": rk["rank_source"],
            "zipf_frequency": zf,
            "rank_display": _format_rank(rank, zf),
        }
        all_words[lw] = entry

        if is_proper:
            excluded_proper.append(entry)
            continue
        if rank is None or rank > threshold:
            candidates.append(entry)
        elif borderline_low <= rank <= borderline_high:
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


def new_rare_words_in_after(before_cand: dict, after_words: dict,
                             threshold: int) -> list:
    before_all_lowers = set(before_cand["all_words_by_lower"].keys())
    new_words = []
    for lw, e in after_words.items():
        if lw in before_all_lowers:
            continue
        if e["rank"] is None or e["rank"] > threshold:
            new_words.append(e)
    new_words.sort(key=lambda e: (0, e["zipf_frequency"]) if e["rank"] is None
                    else (1, e["rank"]))
    return new_words


# ------------------------------------------------------------
# JSON schema (decision enumをKEEP-A/B/C/D形式へ、replacement_if_simplify/
# meaning_or_fact_changeを追加)
# ------------------------------------------------------------
def _decision_item_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "word": {"type": "string"},
            "actual_form": {"type": "string"},
            "frequency_rank": {"type": "string"},
            "decision": {
                "type": "string",
                "enum": ["KEEP-A", "KEEP-B", "KEEP-C", "KEEP-D",
                          "SIMPLIFY", "BORDERLINE"],
            },
            "reasoning": {"type": "string"},
            "replacement_if_simplify": {"type": "string"},
            "meaning_or_fact_change": {
                "type": "string",
                "enum": ["none", "minor", "major"],
            },
            "before_sentence": {"type": "string"},
            "after_sentence": {"type": "string"},
        },
        "required": ["word", "actual_form", "frequency_rank", "decision",
                     "reasoning", "replacement_if_simplify",
                     "meaning_or_fact_change", "before_sentence",
                     "after_sentence"],
        "additionalProperties": False,
    }


def build_json_schema(n_candidates: int) -> dict:
    return {
        "name": "vocab_abcd_strict_exception_trial",
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
                  "追加installなし、STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01/"
                  "ADVANCED-VOCAB-RULE-TRIAL-01 v2と同一method・同一"
                  "version)",
        "ranking_unit": ("rank = min(rank(surface form), rank(best lemma "
                          "candidate))。lemma候補は-s/-es/-ies/-ed/-ing/-ly "
                          "の単純規則のみ(-er/-est比較級除去は使わない)。"
                          "er015_advanced_vocab_rule_trial_01_v2.pyの"
                          "lemma_candidates_v2/rank_of_word_v2をそのまま"
                          "流用、Standard/Advanced共通(思想差ゼロ)。"),
        "level_threshold": LEVEL_THRESHOLD,
        "level_borderline_band": LEVEL_BORDERLINE,
    })

    write_spec_strict_ja(out_dir)
    write_prompt_diff(out_dir)

    for combo_key, spec in ARTICLE_SPECS.items():
        level = spec["level"]
        threshold = LEVEL_THRESHOLD[level]
        b_low, b_high = LEVEL_BORDERLINE[level]
        text = load_text(spec["path"])
        result = build_candidates(text, rank_of, threshold, b_low, b_high)
        save_json(out_path(out_dir, f"candidates_{combo_key}.json"), result)
        print(f"[OK] candidates_{combo_key}.json written. "
              f"candidate_count={result['candidate_count']} "
              f"borderline_count={result['borderline_count']} "
              f"excluded_proper={result['excluded_proper_noun_count']}")


# ------------------------------------------------------------
# STEP: run (4 call)
# ------------------------------------------------------------
def cmd_run(out_dir: str, force: bool) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    v1trial.v1mod.install_logger(out_dir)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    client = get_client()
    pricing = _load_pricing()
    total_jpy = 0.0
    print(f"[INFO] budget={BUDGET_TOTAL_JPY} JPY (本Trial単独、4 call想定)")

    for combo_key, spec in ARTICLE_SPECS.items():
        level = spec["level"]
        key = spec["key"]
        path = spec["path"]
        threshold = LEVEL_THRESHOLD[level]
        b_low, b_high = LEVEL_BORDERLINE[level]

        dst = out_path(out_dir, f"{combo_key}_raw_response.json")
        if os.path.exists(dst) and not force:
            existing = load_json(dst)
            total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
            print(f"[SKIP] existing: {dst} (cumulative so far="
                  f"{round(total_jpy, 4)} JPY)")
            continue

        article_text = load_text(path)
        cand_result = build_candidates(article_text, rank_of, threshold,
                                        b_low, b_high)
        n_candidates = cand_result["candidate_count"]
        candidates_block = _candidates_block_text(cand_result["candidates"])
        borderline_block = _borderline_block_text(
            cand_result["borderline_reference"])

        rule_block = RULE_BLOCK_EN_STRICT_TEMPLATE.format(
            threshold=f"{threshold:,}")
        developer_message = DEVELOPER_MESSAGE_TEMPLATE.format(
            cefr_label=LEVEL_CEFR_LABEL[level])
        borderline_range = f"{b_low:,}-{b_high:,}"

        user_message = (rule_block + "\n" + STRUCTURE_BLOCK[key] + "\n\n" +
                         TASK_TAIL_STRICT.format(
                             candidates_block=candidates_block,
                             borderline_block=borderline_block,
                             article_text=article_text,
                             threshold=f"{threshold:,}",
                             borderline_range=borderline_range))
        schema = build_json_schema(n_candidates)

        save_text(out_path(out_dir, f"prompt_{combo_key}.txt"),
                  "DEVELOPER:\n" + developer_message +
                  "\n\nUSER:\n" + user_message)

        parsed, raw_text, meta = _call_and_parse(
            client, pricing, developer_message, user_message, schema,
            combo_key, n_candidates)
        meta["article_path"] = path
        meta["article_sha256"] = sha256_of_file(path)
        meta["candidate_count"] = n_candidates
        meta["level"] = level
        meta["threshold"] = threshold

        result = {"article": combo_key, "level": level, "key": key,
                  "candidates_input": cand_result,
                  "parsed": parsed, "raw_output_text": raw_text, "meta": meta}
        save_json(dst, result)

        total_jpy += meta["cost_jpy"]
        print(f"[OK] {combo_key}: model={meta['response_model_actual']} "
              f"elapsed={meta['elapsed_seconds']}s cost_jpy={meta['cost_jpy']} "
              f"retried={meta['retried']} n_candidates={n_candidates} "
              f"cumulative_jpy={round(total_jpy, 4)}")

        if parsed is None:
            stop = {"stop_reason": f"parse/technical failure after retry "
                                    f"({combo_key})",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] parse/technical failure after retry ({combo_key})")
            raise SystemExit(1)

        if total_jpy > BUDGET_TOTAL_JPY:
            stop = {"stop_reason": f"budget exceeded after {combo_key}",
                    "total_jpy": round(total_jpy, 4),
                    "budget_jpy": BUDGET_TOTAL_JPY}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after {combo_key}: "
                  f"{round(total_jpy, 4)} > {BUDGET_TOTAL_JPY}")
            raise SystemExit(1)

    print(f"[DONE] run complete. total_cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={BUDGET_TOTAL_JPY}")


# ------------------------------------------------------------
# STEP: analyze
# ------------------------------------------------------------
def _old_decisions_by_word(combo_key: str) -> dict:
    path = PREVIOUS_RAW_RESPONSE[combo_key]
    if not os.path.exists(path):
        return {}
    raw = load_json(path)
    out = {}
    for d in raw["parsed"]["decisions"]:
        out[d["word"]] = d.get("decision", "(unknown)")
    return out


def _keep_or_simplify(decision: str) -> str:
    if decision.startswith("KEEP"):
        return "KEEP"
    if decision == "SIMPLIFY":
        return "SIMPLIFY"
    return "BORDERLINE"


def _decision_log_md(combo_key: str, level: str, decisions: list,
                      cand_by_word: dict) -> str:
    old_by_word = _old_decisions_by_word(combo_key)
    old_label = PREVIOUS_LABEL[combo_key]
    lines = [
        f"### {combo_key} Decision Log (strict)\n",
        f"旧判定の出典: {old_label}\n",
        "| surface | lemma | rank | level | 旧判定 | 新判定 | KEEP/SIMPLIFY "
        "| 理由 | 置換案 | 意味差・Fact差 |",
        "|---|---|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        c = cand_by_word.get(d["word"], {})
        surface_rank = c.get("surface_rank")
        surface_disp = f"{surface_rank:,}" if surface_rank else "(none in top20000)"
        lemma_used = c.get("lemma_used")
        lemma_rank = c.get("lemma_rank")
        if lemma_used and lemma_rank:
            lemma_disp = f"{lemma_used}:{lemma_rank:,}"
        elif lemma_used:
            lemma_disp = f"{lemma_used}:(none in top20000)"
        else:
            lemma_disp = "(none)"
        old_decision = old_by_word.get(d["word"], "(no candidate previously)")
        new_decision = d["decision"]
        reasoning = d["reasoning"].replace("|", "\\|")
        replacement = d.get("replacement_if_simplify", "N/A").replace("|", "\\|")
        meaning_change = d.get("meaning_or_fact_change", "(n/a)")
        lines.append(
            f"| {surface_disp} | {lemma_disp} | {d['frequency_rank']} | "
            f"{level} | {old_decision} | {new_decision} | "
            f"{_keep_or_simplify(new_decision)} | {reasoning} | "
            f"{replacement} | {meaning_change} |")
    return "\n".join(lines)


def cmd_analyze(out_dir: str) -> None:
    import wordfreq

    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)
    lemma_rank_map = bmod._build_lemma_rank_map(top20000)

    for combo_key, spec in ARTICLE_SPECS.items():
        level = spec["level"]
        key = spec["key"]
        path = spec["path"]
        threshold = LEVEL_THRESHOLD[level]

        raw = load_json(out_path(out_dir, f"{combo_key}_raw_response.json"))
        before_text = load_text(path)
        after_text = raw["parsed"]["after_text"]
        decisions = raw["parsed"]["decisions"]
        notes = raw["parsed"]["notes_on_ambiguous_cases"]
        before_cand = raw["candidates_input"]
        cand_by_word = before_cand["all_words_by_lower"]

        save_text(out_path(out_dir, f"{combo_key}_before.md"), before_text)
        save_text(out_path(out_dir, f"{combo_key}_after.md"), after_text)

        b_low, b_high = LEVEL_BORDERLINE[level]
        after_cand = build_candidates(after_text, rank_of, threshold,
                                       b_low, b_high)
        struct = structure_check(key, before_text, after_text)
        new_rare = new_rare_words_in_after(
            before_cand, after_cand["all_words_by_lower"], threshold)

        before_levels = v1trial.v1mod._level_metrics(before_text)
        after_levels = v1trial.v1mod._level_metrics(after_text)

        band_before = bmod.measure_bands(before_text, lemma_rank_map)
        band_after = bmod.measure_bands(after_text, lemma_rank_map)

        decision_counts = Counter(d["decision"] for d in decisions)
        diff_lines = _diff_lines(before_text, after_text)
        fact_check = fact_tokens_check(before_text, after_text)

        metrics = {
            "article": combo_key,
            "level": level,
            "rank_threshold": threshold,
            "borderline_band": [b_low, b_high],
            "candidate_count": before_cand["candidate_count"],
            "decision_counts": dict(decision_counts),
            "structure_check": struct,
            "word_count_before": before_levels["word_count"],
            "word_count_after": after_levels["word_count"],
            "word_count_diff": after_levels["word_count"] - before_levels["word_count"],
            "sentence_count_before": before_levels["sentence_count"],
            "sentence_count_after": after_levels["sentence_count"],
            "sentence_count_diff": after_levels["sentence_count"] - before_levels["sentence_count"],
            "new_rare_words_gt_threshold_in_after": new_rare,
            "band_before_lemma_reference": band_before["bucket_token_counts"],
            "band_after_lemma_reference": band_after["bucket_token_counts"],
            "notes_on_ambiguous_cases": notes,
            "cost_jpy": raw["meta"]["cost_jpy"],
            "retried": raw["meta"]["retried"],
            "fact_tokens_check": fact_check,
        }
        save_json(out_path(out_dir, f"{combo_key}_metrics.json"), metrics)
        save_json(out_path(out_dir, f"{combo_key}_fact_tokens_check.json"),
                  fact_check)

        save_text(out_path(out_dir, f"{combo_key}_decision_log.md"),
                  f"# {combo_key}_decision_log.md\n\n"
                  "凡例: surface=表層形のtop20000内順位, lemma=採用された"
                  "lemma候補(word:順位、未使用または表外は(none)), "
                  "rank=min(surface,lemma)としてモデルへ渡した値, "
                  "level=standard/advanced, 旧判定=前回Trial(閾値のみ異なる"
                  "同一素材)での判定, 新判定=本Trial(厳格定義)での判定, "
                  "KEEP/SIMPLIFY=新判定の粗い分類, 理由=モデルの判定理由, "
                  "置換案=replacement_if_simplify, "
                  "意味差・Fact差=meaning_or_fact_change。\n\n" +
                  _decision_log_md(combo_key, level, decisions, cand_by_word) +
                  f"\n\n### notes_on_ambiguous_cases\n\n{notes}\n")

        diff_md = [f"# {combo_key}_diff.md\n",
                   "## unified diff (Before -> After, full text)\n",
                   "```diff", *diff_lines, "```\n",
                   "## SIMPLIFY decisions のみ(宣言された変更文)\n"]
        for d in decisions:
            if d["decision"] == "SIMPLIFY":
                diff_md.append(f"- **{d['actual_form']}** -> "
                               f"{d.get('replacement_if_simplify', '?')}\n"
                               f"  - Before: {d['before_sentence']}\n"
                               f"  - After: {d['after_sentence']}\n")
        save_text(out_path(out_dir, f"{combo_key}_diff.md"), "\n".join(diff_md))

        print(f"[OK] {combo_key}: analyze done. "
              f"decision_counts={dict(decision_counts)} "
              f"structure_match(heading={struct['headings_match']}, "
              f"paragraph={struct['paragraph_count_match']}) "
              f"word_diff={metrics['word_count_diff']} "
              f"new_rare_words={len(new_rare)} "
              f"fact_tokens_match={fact_check['overall_fact_tokens_match']}")


# ------------------------------------------------------------
# STEP: cross-compare (Standard vs Advanced 同一語の判定対照)
# ------------------------------------------------------------
def cmd_cross_compare(out_dir: str) -> None:
    pairs = [("standard_meta", "advanced_meta", "Meta"),
             ("standard_sewer", "advanced_sewer", "Sewer")]
    lines = ["# cross_level_comparison.md\n",
             "目的: 同一(または実質同一)本文のStandard版/Advanced版で、"
             "同じ語に閾値差以外の判定差が出ていないかを確認する"
             "(B/C/D定義文言は両Levelで完全同一のため、判定差があれば"
             "閾値をまたいだ結果、またはモデルの非決定性のいずれかを"
             "疑うべき)。\n"]
    for std_key, adv_key, label in pairs:
        std_raw = load_json(out_path(out_dir, f"{std_key}_raw_response.json"))
        adv_raw = load_json(out_path(out_dir, f"{adv_key}_raw_response.json"))
        std_by_word = {d["word"]: d for d in std_raw["parsed"]["decisions"]}
        adv_by_word = {d["word"]: d for d in adv_raw["parsed"]["decisions"]}
        std_threshold = LEVEL_THRESHOLD["standard"]
        adv_threshold = LEVEL_THRESHOLD["advanced"]
        all_words = sorted(set(std_by_word) | set(adv_by_word))

        lines.append(f"\n## {label}\n")
        lines.append("| word | Standard rank(候補入力時) | Standard判定 | "
                      "Advanced rank(候補入力時) | Advanced判定 | 対照所見 |")
        lines.append("|---|---|---|---|---|---|")
        std_cand = std_raw["candidates_input"]["all_words_by_lower"]
        adv_cand = adv_raw["candidates_input"]["all_words_by_lower"]
        for w in all_words:
            sd = std_by_word.get(w)
            ad = adv_by_word.get(w)
            s_rank = std_cand.get(w, {}).get("rank_display", "-")
            a_rank = adv_cand.get(w, {}).get("rank_display", "-")
            s_dec = sd["decision"] if sd else "(not a Standard candidate)"
            a_dec = ad["decision"] if ad else "(not an Advanced candidate)"
            if sd and ad:
                if s_dec == a_dec:
                    note = "同一判定"
                else:
                    note = ("判定が異なる -- 閾値差では説明できない場合は"
                            "要確認")
            else:
                note = "片方のLevelのみ候補(閾値差により候補セット自体が"
                note += "異なる可能性)"
            lines.append(f"| {w} | {s_rank} | {s_dec} | {a_rank} | {a_dec} | "
                          f"{note} |")
    save_text(out_path(out_dir, "cross_level_comparison.md"), "\n".join(lines))
    print("[OK] cross_level_comparison.md written.")


# ------------------------------------------------------------
# STEP: misjudgment-analysis ($0、前回septic->C誤判定の原因分析)
# ------------------------------------------------------------
def cmd_misjudgment_analysis(out_dir: str) -> None:
    prev_path = os.path.join(
        "er015_output", "standard_vocab_abcd_alignment_trial_01",
        "sewer_decision_log.md")
    prev_text = load_text(prev_path) if os.path.exists(prev_path) else "(not found)"

    # 誤判定を生んだv2 RULE_BLOCK_ENの該当節を逐語抽出
    marker_start = "Words that appear inside quotation marks in the article"
    idx = v2mod.RULE_BLOCK_EN_V2.find(marker_start)
    if idx >= 0:
        end_idx = v2mod.RULE_BLOCK_EN_V2.find(
            "Do NOT use \"it is part of a fixed expression", idx)
        culprit_clause = v2mod.RULE_BLOCK_EN_V2[idx:end_idx].strip()
    else:
        culprit_clause = "(clause not found -- see v2mod.RULE_BLOCK_EN_V2 directly)"

    lines = [
        "# c_misjudgment_analysis.md\n",
        "## 前回誤判定の事実\n",
        "STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01(v2閾値6,000版)のSewer "
        "Decision Logより、`septic`(記事内では「combined septic tank」と"
        "いう一般名詞句の一部としてのみ登場、固有名詞・公式名称ではない)が"
        "\"KEEP -- proper noun\"(C)と判定された。該当行を逐語引用する:\n",
        "```",
        [ln for ln in prev_text.splitlines() if ln.strip().startswith("| septic")][0]
        if any(ln.strip().startswith("| septic") for ln in prev_text.splitlines())
        else "(該当行が見つからない)",
        "```\n",
        "モデル自身の理由付け(逐語): \"‘Septic’ appears inside the quoted "
        "designation ‘combined septic tank,’ which the article reports as "
        "wording used by a news report and must keep exactly.\"\n",
        "## 構造上の原因\n",
        "原因は当時のRULE_BLOCK_EN_V2(ADVANCED-VOCAB-RULE-TRIAL-01 v2で"
        "Fable差し戻し修正Bとして追加、STANDARD-VOCAB-ABCD-ALIGNMENT-"
        "TRIAL-01がそのまま流用)のC(固有名詞)節に、Meta記事の "
        "\"human concierges\"(Metaが実際にそう呼んだ、という記事内の"
        "Factそのもの)を守るために追加された、以下の一文にある"
        "(逐語引用):\n",
        "```",
        culprit_clause,
        "```\n",
        "この一文は「Metaのような特定の人物・組織が実際に使った呼称」を"
        "想定していたが、文言上は **\"Words that appear inside quotation "
        "marks in the article\"** という条件が、後半の「特定の人物・組織が"
        "実際に使った呼称」という条件から独立した、単独で十分な条件として"
        "読める構造になっていた。結果として、モデルは「記事内で引用符に"
        "入っている語 = C(固有名詞/固有の引用名称)として保護してよい」と"
        "解釈できてしまい、Sewer記事のWriterが読者への導入表現として"
        "引用符を使っただけの一般名詞句 \"combined septic tank\" にまで"
        "この保護を適用した。これは:\n",
        "- 固有名詞と「単なる引用」の区別が定義上なされていなかった\n"
        "- Fact不変の一般原則(記事の事実を変えない)と、C(固有名詞)という"
        "個別の例外カテゴリとの境界が曖昧だった(引用符内の語なら何でも"
        "Factとして固定してよい、という拡大解釈を許した)\n"
        "という2点に起因する。\n",
        "## 本Trialでの是正\n",
        "本TrialのRULE_BLOCK_EN_STRICTでは、C定義を「本当の固有名詞・"
        "公式名称・固有の引用名称だけ」に限定し、「一般名詞が引用符に入っ"
        "ているだけ」「一般的な技術用語」「記事中で引用されているだけ」"
        "「Writerが強調のため引用符を付けただけ」を明示的な否定条件として"
        "追加した(個別語名\"septic\"はPromptに書かず、定義文のみで正しい"
        "判定へ導けるかを検証する)。実際の再判定結果は"
        "standard_sewer_decision_log.md / advanced_sewer_decision_log.md の"
        "septicの行、および本REPORT §7を参照。\n",
    ]
    save_text(out_path(out_dir, "c_misjudgment_analysis.md"), "\n".join(lines))
    print("[OK] c_misjudgment_analysis.md written ($0, no API call).")


# ------------------------------------------------------------
# STEP: assemble
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    calls = []
    total_jpy = 0.0
    for combo_key in ARTICLE_SPECS:
        raw_path = out_path(out_dir, f"{combo_key}_raw_response.json")
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
                     choices=["candidates", "run", "analyze",
                              "cross-compare", "misjudgment-analysis",
                              "assemble"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "candidates":
        cmd_candidates(args.out_dir)
    elif args.step == "run":
        cmd_run(args.out_dir, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "cross-compare":
        cmd_cross_compare(args.out_dir)
    elif args.step == "misjudgment-analysis":
        cmd_misjudgment_analysis(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
