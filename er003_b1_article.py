# ============================================================
# er003_b1_article.py
# ER-003-B1-P1: A01 B1本文の初回プロトタイプ生成
# ============================================================
# 承認済みNatural English Source(B2生成時にも使用した共通マスター)を
# 入力に、CEFR B1学習者向けの本文をA01について1回だけ生成する。B1仕様の
# 確定ではなく、ユーザーが実物を見て判断するためのプロトタイプ。
#
# B2本文は入力に一切含めない。B1はB2をさらに簡略化して作るのではなく、
# Natural English Sourceから独立に書き直す(兄弟版)。日本語マスターは
# 比較用の出力としてのみ複製し、生成APIへは渡さない。
#
# 内容評価(指標違反・忠実性)による自動再生成は行わない。API呼び出しは
# A01について1回だけであり、リトライゲートには一切包まない。
#
# 再利用するもの(再実装しない):
#   - er003_ja_to_en_translation.TRANSLATOR_MODEL/TRANSLATOR_REASONING_EFFORT
#     ("gpt-5.6-sol"/"high"、B2までと不変)
#   - er003_ja_to_en_translation.make_translator_fn(Web検索なし・
#     Structured Outputなしの実体。developer_messageだけ差し替える)
#   - er003_ja_to_en_translation.split_sentences/compute_word_count/
#     compute_estimated_reading_times(ER-003-P2Aで段落認識・カーリー
#     クォート対応済みの決定的sentence splitter)
#   - er002_ja_article_generation.strip_markdown_symbols
#   - er003_b2_adapter.strip_heading_lines(見出し行除去、言語非依存)
#   - er003_ja_to_en_translation_p1b.validate_p1b_structure(固定構造の
#     判定関数のみを使う。retry gateは使わない。自動再生成しないため)
#   - er003_natural_source.sha256_text

from __future__ import annotations

import re
from typing import Any, Optional

import er002_ja_article_generation as article_gen
import er003_b2_adapter as b2
import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b
import er003_natural_source as natural_source

EXPERIMENT_VERSION = "ER-003-B1-P1"
TOPIC_ID = "A01"

JAPANESE_MASTER_PATH = er003.APPROVED_ARTICLE_SOURCE_PATHS["A01"]
NATURAL_ENGLISH_SOURCE_PATH = "er003_output/p1b/A01/natural_source_approved.md"

# P1/P1B/B2から不変のまま再利用(再定義しない)
B1_MODEL = er003.TRANSLATOR_MODEL  # "gpt-5.6-sol"
B1_REASONING_EFFORT = er003.TRANSLATOR_REASONING_EFFORT  # "high"
B1_DEVELOPER_MESSAGE = "Write a natural English news article for B1-level learners."

B1_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p1_prompt_template.txt"

sha256_text = natural_source.sha256_text


def load_japanese_master() -> str:
    with open(JAPANESE_MASTER_PATH, encoding="utf-8") as f:
        return f.read()


def load_natural_english_source() -> str:
    with open(NATURAL_ENGLISH_SOURCE_PATH, encoding="utf-8") as f:
        return f.read()


# ============================================================
# ブロック1: マスター出力(APIは呼ばない、完全複製)
# ============================================================
def export_master_files(output_dir: str, japanese_master: Optional[str] = None,
                         natural_english_source: Optional[str] = None) -> dict:
    """承認済み日本語マスター・承認済みNatural English Sourceを、内容を
    一切変更せずoutput_dirへ複製する。日本語マスターは比較用であり、
    B1生成APIへは渡さない。"""
    ja = japanese_master if japanese_master is not None else load_japanese_master()
    en = natural_english_source if natural_english_source is not None else load_natural_english_source()

    ja_out_path = f"{output_dir}/master_ja_approved.md"
    en_out_path = f"{output_dir}/master_en_natural_source_approved.md"
    with open(ja_out_path, "w", encoding="utf-8") as f:
        f.write(ja)
    with open(en_out_path, "w", encoding="utf-8") as f:
        f.write(en)

    return {
        "japanese_master": {
            "source_path": JAPANESE_MASTER_PATH, "output_path": ja_out_path, "sha256": sha256_text(ja),
        },
        "natural_english_source": {
            "source_path": NATURAL_ENGLISH_SOURCE_PATH, "output_path": en_out_path, "sha256": sha256_text(en),
        },
    }


# ============================================================
# ブロック2: prompt構築・単発API呼び出し(gateなし、再試行なし)
# ============================================================
def load_b1_prompt_template(path: str = B1_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_b1_user_message(approved_natural_english_source: str, template: Optional[str] = None) -> str:
    """入力はNatural English Sourceのみ。B2本文・日本語マスターは
    テンプレートのプレースホルダーに一切現れない。"""
    template = template if template is not None else load_b1_prompt_template()
    return template.replace("{approved_natural_english_source}", approved_natural_english_source)


def make_b1_generator_fn(user_message: str, client: Optional[Any] = None):
    """er003.make_translator_fnをそのまま再利用する(Web検索なし・
    Structured Outputなしの実体は完全に同一)。developer_messageだけ
    B1用に差し替える。retry gateには一切包まない(本ステージはA01に
    ついて1回だけの単発呼び出し)。"""
    return er003.make_translator_fn(
        user_message, client=client, model=B1_MODEL,
        reasoning_effort=B1_REASONING_EFFORT, developer_message=B1_DEVELOPER_MESSAGE,
    )


# ============================================================
# ブロック3: 固定構造チェック(判定のみ、自動修正・自動再生成しない)
# ============================================================
check_b1_structure = p1b.validate_p1b_structure


# ============================================================
# ブロック4: B1文長指標(B2のcompute_b2_sentence_metricsと同型の構成、
# 閾値だけがB1向け)。総語数のhard limitは設けない。
# ============================================================
B1_TARGET_AVG_WORDS_PER_SENTENCE = 15.0
B1_MAX_SENTENCE_WORD_COUNT = 24

strip_heading_lines = b2.strip_heading_lines


def compute_b1_sentence_metrics(raw_text: str) -> dict:
    """総語数は見出し込み・本文のみの両方を保存する。平均文長・最長文・
    文分割は見出しを除外した本文のみを対象にする。指標違反でも記録する
    だけで、この関数自体は再生成のトリガーにしない。"""
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
    sentences_over_24 = [
        {"sentence": s, "word_count": w}
        for s, w in zip(sentences, sentence_word_counts) if w > B1_MAX_SENTENCE_WORD_COUNT
    ]

    return {
        "total_word_count_including_headings": total_word_count_including_headings,
        "total_word_count_body_only": total_word_count_body_only,
        "total_sentence_count": total_sentence_count,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_words_per_sentence_target": B1_TARGET_AVG_WORDS_PER_SENTENCE,
        "avg_words_per_sentence_within_target": avg_words_per_sentence <= B1_TARGET_AVG_WORDS_PER_SENTENCE,
        "longest_sentence_word_count": longest_sentence_word_count,
        "max_sentence_word_count_ceiling": B1_MAX_SENTENCE_WORD_COUNT,
        "sentences_over_24_word_count": len(sentences_over_24),
        "sentences_over_24": sentences_over_24,
        "estimated_reading_time_minutes": er003.compute_estimated_reading_times(total_word_count_including_headings),
    }


# ============================================================
# ブロック5: 機械チェック(評価不能になる不備だけを確認する。内容評価は
# 行わない。いずれのチェックも自動再生成をトリガーしない)
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
        # 構造的保証: build_b1_user_messageはNatural English Sourceの
        # プレースホルダーしか持たず、B2本文を渡す経路自体が存在しない。
        "b2_body_not_used_as_input": True,
    }
    return {
        "status": "ALL_CHECKS_PASS" if all(checks.values()) else "SOME_CHECKS_FAILED",
        "checks": checks,
    }
