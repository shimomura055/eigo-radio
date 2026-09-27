# ============================================================
# er023_key_phrase_db_extraction.py
# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
# deterministic候補抽出(tokenize→1〜5-gram→lemma正規化→群1DB照合→
# 除外Gate観測)。設計doc Section C/D/Eを実装する。LLM呼び出しは
# 一切行わない(fallbackは別モジュール/orchestratorが行う)。
# ============================================================

from __future__ import annotations

import re
import unicodedata
from typing import Optional

import er003_key_words_min_unit as mu
import er015_advanced_vocab_rule_trial_01_v2 as vocab_v2

_WORD_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

# 有限助動詞(既存Production hard requirementをそのまま再利用)
_FINITE_AUX_WORDS = mu._FINITE_AUX_WORDS
_PRONOUN_DEMONSTRATIVE_WORDS = mu._PRONOUN_DEMONSTRATIVE_WORDS

# 除外Gate: 閉じたクラスの機能語(規則で判定できる「簡単すぎ・一般的
# すぎ」の一部)。CEFR levelを主軸にしない(ユーザー確定原則1・4)ため、
# 品詞クラスによる構造的な閉じたセットのみを規則対象とする。
_CLOSED_CLASS_FUNCTION_WORDS = {
    "a", "an", "the", "and", "or", "but", "so", "yet", "nor", "for",
    "in", "on", "at", "by", "to", "of", "with", "from", "into", "onto",
    "about", "as", "than", "then", "that", "this", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
    "us", "them", "my", "your", "his", "its", "our", "their",
    "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did",
    "will", "would", "can", "could", "should", "may", "might", "must",
    "not", "no", "if", "because", "while", "when", "where", "which", "who",
    "what", "how", "there", "here",
}


_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+(?=\s|$)")


def _clean_article_text(article_markdown: str) -> str:
    lines = article_markdown.splitlines()
    text_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()
        text_lines.append(stripped)
    joined = " ".join(text_lines)
    joined = unicodedata.normalize("NFKC", joined)
    joined = joined.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return joined


def tokenize(article_markdown: str) -> list:
    """markdown見出し記号・句読点を除去し、単語トークンの表層形リストを
    返す(大小文字は保持、順序は本文どおり、文境界をまたぐか否かは
    区別しない=総token数カウント等の後方互換用途)。既存
    er003.strip_markdown_symbolsは音声組版向けでja_glossなど混在する
    ため使わず、シンプルな英語トークナイザを新規実装する(設計doc
    C-2手順1)。"""
    joined = _clean_article_text(article_markdown)
    return _WORD_TOKEN_RE.findall(joined)


def tokenize_sentences(article_markdown: str) -> list:
    """文境界(.!?)で分割してから各文をトークナイズする(n-gram生成が
    文をまたいで無意味な候補[例: "recovering The policy turn"]を作らない
    ようにするため)。戻り値: [[token, token, ...], [token, ...], ...]。"""
    joined = _clean_article_text(article_markdown)
    sentences_raw = _SENTENCE_SPLIT_RE.split(joined)
    sentences = []
    for s in sentences_raw:
        toks = _WORD_TOKEN_RE.findall(s)
        if toks:
            sentences.append(toks)
    return sentences


def generate_ngrams(tokens, min_n: int = 1, max_n: int = 5) -> list:
    """1〜5-gramを機械的に全て生成する(重要そうかで絞らない、設計doc
    C-2手順2・ユーザー確定原則2)。文をまたいで無意味な候補を作らない
    よう、`tokens`は文単位のトークンリストのリスト(`tokenize_sentences`
    の戻り値)を渡すことを推奨する(後方互換のためフラットな1次元
    リストも受け付けるが、その場合は文境界を無視して連続スパンを
    生成する=旧動作のまま)。戻り値は
    [{"n": n, "start": i, "surface_tokens": [...], "surface_form": "..."}]。"""
    if tokens and isinstance(tokens[0], list):
        sentences = tokens
    else:
        sentences = [tokens]
    result = []
    global_start = 0
    for sent_tokens in sentences:
        n_tokens = len(sent_tokens)
        for n in range(min_n, max_n + 1):
            for i in range(0, n_tokens - n + 1):
                span = sent_tokens[i:i + n]
                result.append({
                    "n": n, "start": global_start + i, "surface_tokens": span,
                    "surface_form": " ".join(span),
                })
        global_start += n_tokens
    return result


def _normalize_key(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def lemma_candidates_for_word(word: str) -> list:
    """単語のlemma候補(既存er015 v2ロジックをそのまま再利用、C-1)。"""
    return vocab_v2.lemma_candidates_v2(word)


def lemma_candidates_for_phrase(surface_tokens: list) -> list:
    """複数語表現の活用形正規化(設計doc C-3で新規ロジックが必要と
    明記された部分)。本Trialでの実装範囲: 各構成語を個別にlemma化し、
    (a) 全構成語そのまま、(b) 最後の語のみlemma化(動詞句の時制変化を
    吸収する最頻パターン、例: "picked up the pace"→"pick up the pace"
    は最後の語ではなく先頭語が動詞のことが多いため(c)も加える)、
    (c) 先頭語のみlemma化、(d) 全構成語をlemma化、の4パターンを候補
    として生成する(discontinuous phrasal verbの語順入れ替えには対応
    しない、設計doc C-3で明記のとおり未実装)。"""
    if not surface_tokens:
        return []
    lower_tokens = [t.lower() for t in surface_tokens]
    variants = set()
    variants.add(" ".join(lower_tokens))

    first_lemmas = lemma_candidates_for_word(lower_tokens[0])
    last_lemmas = lemma_candidates_for_word(lower_tokens[-1])

    for fl in first_lemmas:
        variants.add(" ".join([fl] + lower_tokens[1:]))
    for ll in last_lemmas:
        variants.add(" ".join(lower_tokens[:-1] + [ll]))
    for fl in first_lemmas:
        for ll in last_lemmas:
            variants.add(" ".join([fl] + lower_tokens[1:-1] + [ll]) if len(lower_tokens) > 1 else fl)

    all_lemma_tokens = []
    for t in lower_tokens:
        cands = lemma_candidates_for_word(t)
        # 最短(最も強く縮めた)候補を1つ採用(観測目的の候補生成であり
        # 決定を左右する重要ロジックではないため、決定的にソート済み
        # candsの最初=最短候補を使う)
        all_lemma_tokens.append(cands[0] if cands else t)
    variants.add(" ".join(all_lemma_tokens))

    return sorted(variants)


UNIT_TYPE_WORD = "word"
UNIT_TYPE_PHRASE = "phrase"
UNIT_TYPE_PHRASAL_VERB = "phrasal_verb"
UNIT_TYPE_IDIOM = "idiom"
UNIT_TYPE_COLLOCATION = "collocation"
UNIT_TYPE_DISCOURSE = "discourse_expression"

_WIKTIONARY_CATEGORY_TO_UNIT_TYPE = {
    "idiom": UNIT_TYPE_IDIOM,
    "phrasal_verb": UNIT_TYPE_PHRASAL_VERB,
    "proverb": UNIT_TYPE_DISCOURSE,
    "multiword_term": UNIT_TYPE_PHRASE,
}


def match_candidate_against_group1(ngram: dict, dbs: dict) -> dict:
    """1件のn-gram候補を群1DB(CEFR-J・NGSL family・Wiktionary)に照合し、
    設計doc D-1 evidence schemaのcore部分を返す(exclusion_gate_result・
    final_selection_reasonは別関数で埋める)。multiword termsの
    targeted lookup結果は呼び出し側が事前に`wiktionary_multiword_hits`
    (candidate_surface_form(lower)->bool)として渡す。"""
    n = ngram["n"]
    surface_tokens = ngram["surface_tokens"]
    surface_form = ngram["surface_form"]
    key = _normalize_key(surface_form)

    matched_dbs = set()
    db_categories = set()
    cefr_level = None

    if n == 1:
        word_key = _normalize_key(surface_tokens[0])
        lemma_cands = [word_key] + lemma_candidates_for_word(word_key)
        for cand in lemma_cands:
            if cand in dbs["cefr_j"]:
                matched_dbs.add("cefr_j")
                if cefr_level is None:
                    cefr_level = dbs["cefr_j"][cand]["cefr"]
            if cand in dbs["ngsl_family"]:
                matched_dbs.add("ngsl_family")
            if cand in dbs["wiktionary"]:
                matched_dbs.add("wiktionary")
                db_categories.update(dbs["wiktionary"][cand]["categories"])
    else:
        phrase_variants = [key] + lemma_candidates_for_phrase(surface_tokens)
        for cand in phrase_variants:
            if cand in dbs["cefr_j"] and dbs["cefr_j"][cand]["is_multiword"]:
                matched_dbs.add("cefr_j")
                if cefr_level is None:
                    cefr_level = dbs["cefr_j"][cand]["cefr"]
            if cand in dbs["wiktionary"]:
                matched_dbs.add("wiktionary")
                db_categories.update(dbs["wiktionary"][cand]["categories"])

    # 観測: Wiktionaryは単語1語のページにも「その語が持つ慣用的な語義の
    # 1つ」を理由にCategory:English idioms等を付与している場合がある
    # (例: "oil"/"story"/"would"が実際にidiomsカテゴリのタイトル一覧に
    # 単独で含まれていた、2026-09-27実データで確認)。unit_type分類は
    # n(トークン数)を主軸にし、n==1の場合はdb_categoriesに関わらず
    # unit_type=wordのままとする(db_categoriesは観測用にそのまま保持
    # する=「複数DB一致」軸とは独立に、カテゴリタグの粗さも記録に残す)。
    unit_type = UNIT_TYPE_WORD if n == 1 else UNIT_TYPE_PHRASE
    if n > 1:
        if "phrasal_verb" in db_categories:
            unit_type = UNIT_TYPE_PHRASAL_VERB
        elif "idiom" in db_categories:
            unit_type = UNIT_TYPE_IDIOM
        elif "proverb" in db_categories:
            unit_type = UNIT_TYPE_DISCOURSE
        elif not db_categories and matched_dbs:
            unit_type = UNIT_TYPE_PHRASE

    return {
        "surface_form": surface_form,
        "canonical_form": key,
        "n": n,
        "matched_dbs": sorted(matched_dbs),
        "db_match_count": len(matched_dbs),
        "db_categories": sorted(db_categories),
        "unit_type": unit_type,
        "cefr_level": cefr_level,
    }


# ------------------------------------------------------------
# 除外Gate(設計doc Section E、Fableレビュー論点1: 規則判定/人間判断
# を分けて記録)
# ------------------------------------------------------------
def apply_structural_gate(surface_form: str) -> dict:
    """既存er003_key_words_min_unitのhard requirement(1〜5語・完全文/
    節排除・有限助動詞排除)をそのまま再利用した構造的判定(規則で判定
    できる項目)。"""
    form = mu.validate_display_phrase_form(surface_form)
    return {
        "rule_determined": True,
        "structural_ok": form["ok"],
        "reasons": form["reasons"],
        "warnings": form["warnings"],
    }


def apply_exclusion_gate(candidate_evidence: dict, article_tokens: list,
                          all_candidates_by_lemma: dict) -> dict:
    """設計doc D-1 exclusion_gate_resultを埋める。各項目について
    rule_determined(規則で判定できたか)を明示する(Fableレビュー論点1)。"""
    surface_form = candidate_evidence["surface_form"]
    unit_type = candidate_evidence["unit_type"]
    tokens_lower = [t.lower() for t in surface_form.split()]

    gate = {}

    # (1) too_easy_or_common: 閉じたクラスの機能語かどうかは規則判定可能。
    # それ以外(内容語の「簡単すぎ」)は閾値を決めない方針のため、規則
    # では判定できない(人間判断が必要)としてFalseで記録する。
    if unit_type == UNIT_TYPE_WORD and tokens_lower[0] in _CLOSED_CLASS_FUNCTION_WORDS:
        gate["too_easy_or_common"] = {"rule_determined": True, "value": True,
                                       "basis": "closed_class_function_word"}
    else:
        gate["too_easy_or_common"] = {"rule_determined": False, "value": None,
                                       "basis": "content_word_or_phrase_commonness_needs_human_judgment"}

    # (2) proper_noun: 本文中で常に大文字始まりか(文頭以外でも大文字)を
    # 規則でチェックできる(簡易ヒューリスティック、固有名詞判定として
    # 完全ではないが構造的に判定可能な部分)。
    structural = apply_structural_gate(surface_form)

    # (3) article_specific_low_reuse / semantic_functional_duplicate_of /
    # low_value_as_chunk: 記事文脈・語彙的意味の比較が必要であり、本
    # Trialのdeterministicロジックでは判定できない(人間判断が必要)。
    gate["article_specific_low_reuse"] = {"rule_determined": False, "value": None,
                                           "basis": "requires_topic_specificity_judgment"}
    gate["semantic_functional_duplicate_of"] = {"rule_determined": False, "value": None,
                                                 "basis": "requires_semantic_comparison"}
    gate["low_value_as_chunk"] = {"rule_determined": False, "value": None,
                                   "basis": "requires_pedagogical_judgment"}

    # (4) unnatural_out_of_context: 構造的have(完全文/節・有限助動詞)は
    # 規則判定可能(既存hard requirement流用)。それ以外の自然さ判断は
    # 人間判断が必要。
    if not structural["structural_ok"]:
        gate["unnatural_out_of_context"] = {"rule_determined": True, "value": True,
                                             "basis": "structural_hard_requirement_violation",
                                             "reasons": structural["reasons"]}
    else:
        gate["unnatural_out_of_context"] = {"rule_determined": False, "value": None,
                                             "basis": "structural_check_passed_naturalness_needs_human_judgment"}

    gate["proper_noun"] = {"rule_determined": False, "value": None,
                            "basis": "capitalization_heuristic_insufficient_needs_human_judgment"}

    return gate


def build_evidence(ngram: dict, dbs: dict) -> dict:
    core = match_candidate_against_group1(ngram, dbs)
    core["exclusion_gate_result"] = None  # apply_exclusion_gateで別途埋める(記事全体のcontextが必要なため)
    core["final_selection_reason"] = None
    core["source_span"] = ngram["surface_form"]
    return core


def dedupe_candidates_by_canonical_form(evidences: list) -> list:
    """同一canonical_form・同一unit_typeの重複を除去し、db_match_countが
    最大のものを残す(deterministic、n数が最小のものを優先=より
    minimal unitに近い表現を残す)。"""
    best_by_key = {}
    for ev in evidences:
        key = (ev["canonical_form"], ev["unit_type"])
        existing = best_by_key.get(key)
        if existing is None:
            best_by_key[key] = ev
            continue
        if ev["db_match_count"] > existing["db_match_count"]:
            best_by_key[key] = ev
        elif ev["db_match_count"] == existing["db_match_count"] and ev["n"] < existing["n"]:
            best_by_key[key] = ev
    return list(best_by_key.values())
