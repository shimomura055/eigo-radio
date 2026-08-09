# ============================================================
# er003_a2_article.py
# ER-003-A2-01: A2暫定仕様でのCEFR-A2本文テキスト生成・検証(汎用モジュール)
# ============================================================
# Natural English Sourceから、A01専用コードのコピーではなく汎用関数として
# A2本文を生成する。B1本文は入力に一切使わない(B1をさらに削ってA2化
# しない、Natural English Sourceからの独立生成)。
#
# 内容評価(指標)による自動再生成は行わない。API呼び出しは記事ごとに
# 1回だけであり、リトライゲートには一切包まない(ER-003-B1-P1と同じ方針)。
#
# 再利用するもの(再実装しない):
#   - er003_ja_to_en_translation.TRANSLATOR_MODEL/TRANSLATOR_REASONING_EFFORT
#   - er003_ja_to_en_translation.make_translator_fn
#   - er003_ja_to_en_translation.split_sentences/compute_word_count/
#     compute_estimated_reading_times
#   - er002_ja_article_generation.strip_markdown_symbols
#   - er003_b2_adapter.strip_heading_lines
#   - er003_ja_to_en_translation_p1b.validate_p1b_structure(固定構造の
#     判定のみ。B1/B2/A2いずれもCEFR非依存の同一構造)
#   - er003_natural_source.sha256_text
#
# 文法・語彙QA(relative clause/passive/perfect tense/participle/難語候補)
# は、NLPパーサー(spacy等)がこの環境に存在しないため、正規表現による
# ヒューリスティック検出とする。**機械判定のみでA2適合と断定しない**
# という本ステージの前提のとおり、これらの数値は目安・スクリーニング
# 用途に限定し、最終判断はユーザーの通読に委ねる。

from __future__ import annotations

import re
from typing import Any, Optional

import er002_ja_article_generation as article_gen
import er003_b2_adapter as b2
import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b
import er003_natural_source as natural_source

A2_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/a2_p1_prompt_template.txt"

A2_MODEL = er003.TRANSLATOR_MODEL  # "gpt-5.6-sol"
A2_REASONING_EFFORT = er003.TRANSLATOR_REASONING_EFFORT  # "high"
A2_DEVELOPER_MESSAGE = "Write a natural English news article for A2-level learners."

sha256_text = natural_source.sha256_text
strip_heading_lines = b2.strip_heading_lines
check_a2_structure = p1b.validate_p1b_structure


# ============================================================
# ブロック1: prompt構築・単発API呼び出し(gateなし、再試行なし)
# ============================================================
def load_a2_prompt_template(path: str = A2_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_a2_user_message(approved_natural_english_source: str, template: Optional[str] = None) -> str:
    """入力はNatural English Sourceのみ。B1・B2本文はテンプレートの
    プレースホルダーに一切現れない。"""
    template = template if template is not None else load_a2_prompt_template()
    return template.replace("{approved_natural_english_source}", approved_natural_english_source)


def make_a2_generator_fn(user_message: str, client: Optional[Any] = None):
    return er003.make_translator_fn(
        user_message, client=client, model=A2_MODEL,
        reasoning_effort=A2_REASONING_EFFORT, developer_message=A2_DEVELOPER_MESSAGE,
    )


# ============================================================
# ブロック2: A2文長指標(B1/B2のcompute_*_sentence_metricsと同型の構成、
# 閾値だけがA2向け・暫定仕様)。総語数のhard limitは今回設けない
# (「6. 全体語数」で明示のとおり、まず実測してから後でレンジを決める)。
# ============================================================
A2_TARGET_AVG_WORDS_PER_SENTENCE = 11.0
A2_MAX_SENTENCE_WORD_COUNT = 18


def compute_a2_sentence_metrics(raw_text: str) -> dict:
    """指標違反でも記録するだけで、この関数自体は再生成のトリガーには
    しない(B1と同じ方針。今回は暫定仕様の検証段階のため)。"""
    plain_with_headings = article_gen.strip_markdown_symbols(raw_text)
    body_only_raw = strip_heading_lines(raw_text)
    plain_body_only = article_gen.strip_markdown_symbols(body_only_raw)

    total_word_count_including_headings = er003.compute_word_count(plain_with_headings)
    total_word_count_body_only = er003.compute_word_count(plain_body_only)

    sentences = er003.split_sentences(plain_body_only)
    sentence_word_counts = [er003.compute_word_count(s) for s in sentences]
    total_sentence_count = len(sentences)
    avg_words_per_sentence = (
        round(sum(sentence_word_counts) / total_sentence_count, 2) if total_sentence_count else 0.0
    )
    longest_sentence_word_count = max(sentence_word_counts) if sentence_word_counts else 0
    sentences_over_18 = [
        {"sentence": s, "word_count": w}
        for s, w in zip(sentences, sentence_word_counts) if w > A2_MAX_SENTENCE_WORD_COUNT
    ]

    return {
        "sentences": sentences,
        "sentence_word_counts": sentence_word_counts,
        "total_word_count_including_headings": total_word_count_including_headings,
        "total_word_count_body_only": total_word_count_body_only,
        "total_sentence_count": total_sentence_count,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_words_per_sentence_target": A2_TARGET_AVG_WORDS_PER_SENTENCE,
        "avg_words_per_sentence_within_target": avg_words_per_sentence <= A2_TARGET_AVG_WORDS_PER_SENTENCE,
        "longest_sentence_word_count": longest_sentence_word_count,
        "max_sentence_word_count_ceiling": A2_MAX_SENTENCE_WORD_COUNT,
        "sentences_over_18_word_count": len(sentences_over_18),
        "sentences_over_18": sentences_over_18,
        "estimated_reading_time_minutes": er003.compute_estimated_reading_times(total_word_count_including_headings),
    }


# ============================================================
# ブロック3: 文法・語彙ヒューリスティックQA(正規表現ベース、目安のみ)
# ============================================================
_RELATIVE_PRONOUN_RE = re.compile(
    r"\b(who|whom|whose|which)\b|\bthat\b(?=\s+\w+\s+\w+)", re.IGNORECASE)
_PASSIVE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+\w+ed\b|\b(is|are|was|were|be|been|being)\s+"
    r"(made|known|given|taken|seen|found|said|held|told|sent|shown|written|done|paid|announced)\b",
    re.IGNORECASE,
)
_PRESENT_PERFECT_RE = re.compile(r"\b(has|have)\s+(?:not\s+|never\s+)?\w+(ed|en)\b", re.IGNORECASE)
_PAST_PERFECT_RE = re.compile(r"\bhad\s+(?:not\s+|never\s+)?\w+(ed|en)\b", re.IGNORECASE)
_PARTICIPIAL_PHRASE_RE = re.compile(
    r"(,\s*\w+ing\b)|(^\w+ing\b[^,.]{0,40},)|(,\s*\w+ed\s+by\b)", re.IGNORECASE | re.MULTILINE)
_SUBORDINATE_MARKER_RE = re.compile(
    r"\b(because|although|though|while|since|if|when|after|before|unless|whereas)\b", re.IGNORECASE)

_COMMON_SHORT_WORDS = {
    "the", "a", "an", "and", "but", "so", "because", "of", "to", "in", "on", "at",
    "for", "with", "as", "is", "was", "were", "are", "be", "been", "it", "its",
}


def _long_word_candidates(plain_body_only: str, min_len: int = 9) -> list:
    """語頻度リストが存在しないため、語長ヒューリスティックのみで
    難語候補を抽出する(粗い近似。CEFR頻度検証ではない、目安のみ)。"""
    words = re.findall(r"[A-Za-z][A-Za-z\-']+", plain_body_only)
    seen = []
    seen_set = set()
    for w in words:
        lw = w.lower()
        if len(lw) >= min_len and lw not in seen_set:
            seen_set.add(lw)
            seen.append(w)
    return seen


def compute_a2_grammar_vocab_heuristics(raw_text: str) -> dict:
    """relative clause/passive/perfect/participle/従属節/難語候補の
    ヒューリスティック件数。NLPパーサーを使わない正規表現ベースの
    近似値であり、確定判定ではない(目視確認が必須)。"""
    body_only_raw = strip_heading_lines(raw_text)
    plain_body_only = article_gen.strip_markdown_symbols(body_only_raw)

    relative_clause_matches = _RELATIVE_PRONOUN_RE.findall(plain_body_only)
    passive_matches = _PASSIVE_RE.findall(plain_body_only)
    present_perfect_matches = _PRESENT_PERFECT_RE.findall(plain_body_only)
    past_perfect_matches = _PAST_PERFECT_RE.findall(plain_body_only)
    participial_matches = _PARTICIPIAL_PHRASE_RE.findall(plain_body_only)
    subordinate_marker_matches = _SUBORDINATE_MARKER_RE.findall(plain_body_only)
    long_words = _long_word_candidates(plain_body_only)

    return {
        "relative_clause_candidate_count": len(relative_clause_matches),
        "passive_candidate_count": len(passive_matches),
        "present_perfect_candidate_count": len(present_perfect_matches),
        "past_perfect_candidate_count": len(past_perfect_matches),
        "participial_phrase_candidate_count": len(participial_matches),
        "subordinate_marker_count": len(subordinate_marker_matches),
        "long_word_candidate_count": len(long_words),
        "long_word_candidates": long_words,
        "method": "regex_heuristic_not_nlp_parser",
    }


# ============================================================
# ブロック3-2: セクション別語数(Full Story vs Points)
# ER-003-A2-02: 「Pointsが本文の代替にならないこと」を計測で確認するため、
# Full Story(タイトル〜Today's...Points見出し直前)とPoints
# (Point One〜Point Two本文、In One Line手前まで)を分離して計測する。
# ============================================================
_SECTION_HEADING_RE = re.compile(r"(?m)^(#{1,3})[ \t]+(.*)$")
_SECTION_TODAYS_POINTS_RE = re.compile(r"^Today's\s+(.+?)\s+Points$")
_SECTION_IN_ONE_LINE_RE = re.compile(r"^In One Line$")


def split_article_sections(raw_text: str) -> dict:
    """Full Story(タイトル+Introduction、Today's...Points見出しの手前まで)、
    Points(Today's...Points見出しの直後からIn One Line見出しの手前まで、
    Point One/Point Twoの小見出し・本文を含む)、In One Lineの3区間へ
    分割する。構造妥当性の判定はp1b.validate_p1b_structureに委ねる
    (本関数は妥当な構造であることを前提としたテキスト抽出のみ行う)。"""
    headings = [
        {"level": len(m.group(1)), "text": m.group(2).strip(), "start": m.start(), "end": m.end()}
        for m in _SECTION_HEADING_RE.finditer(raw_text)
    ]

    todays_idx = next(
        (i for i, h in enumerate(headings) if h["level"] == 2 and _SECTION_TODAYS_POINTS_RE.match(h["text"])), None)
    in_one_line_idx = next(
        (i for i, h in enumerate(headings) if h["level"] == 2 and _SECTION_IN_ONE_LINE_RE.match(h["text"])), None)

    if todays_idx is None or in_one_line_idx is None:
        return {"full_story": raw_text, "points": "", "in_one_line": "", "section_split_valid": False}

    full_story_text = raw_text[:headings[todays_idx]["start"]].strip()
    points_text = raw_text[headings[todays_idx]["end"]:headings[in_one_line_idx]["start"]].strip()
    in_one_line_text = raw_text[headings[in_one_line_idx]["end"]:].strip()

    return {
        "full_story": full_story_text,
        "points": points_text,
        "in_one_line": in_one_line_text,
        "section_split_valid": True,
    }


def compute_section_word_counts(raw_text: str) -> dict:
    sections = split_article_sections(raw_text)
    full_story_words = er003.compute_word_count(article_gen.strip_markdown_symbols(sections["full_story"]))
    points_words = er003.compute_word_count(article_gen.strip_markdown_symbols(sections["points"]))
    in_one_line_words = er003.compute_word_count(article_gen.strip_markdown_symbols(sections["in_one_line"]))
    total = full_story_words + points_words + in_one_line_words
    return {
        "full_story_word_count": full_story_words,
        "points_word_count": points_words,
        "in_one_line_word_count": in_one_line_words,
        "full_story_to_points_ratio": (
            round(full_story_words / points_words, 2) if points_words else None
        ),
        "full_story_share_of_total": round(full_story_words / total, 3) if total else None,
        "section_split_valid": sections["section_split_valid"],
    }


# ============================================================
# ブロック4: 機械チェック(評価不能になる不備だけを確認する)
# ============================================================
_HEADING_PRESENT_RE = re.compile(r"(?m)^#{1,6}[ \t]")


def run_machine_checks(raw_text: str, structure: dict, metrics: dict, uses_web_search_tool: bool) -> dict:
    checks = {
        "api_response_not_empty": bool(raw_text and raw_text.strip()),
        "markdown_structure_present": bool(_HEADING_PRESENT_RE.search(raw_text or "")),
        "point_one_present": structure.get("point_one_heading") is not None,
        "point_two_present": structure.get("point_two_heading") is not None,
        "in_one_line_present": bool(structure.get("in_one_line_present")),
        "sentence_length_measurable": metrics.get("total_sentence_count", 0) > 0,
        "web_search_not_used": not uses_web_search_tool,
        "b1_b2_body_not_used_as_input": True,
    }
    return {
        "status": "ALL_CHECKS_PASS" if all(checks.values()) else "SOME_CHECKS_FAILED",
        "checks": checks,
    }
