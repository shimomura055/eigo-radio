# ============================================================
# er003_b2_adapter.py
# ER-003-P2 Part B: B2本文調整パイロット
# ============================================================
# ER-003-P2 Part Aで確定したNatural English Source(3記事)を入力とし、
# CEFR B2学習者向けに語彙・文長・情報密度を調整する。日本語原稿・P1/P1B
# の生応答・fact-QA・難易度評価結果はadapterへ渡さない(事後の整合性QAに
# 日本語原稿を使うのみ)。
#
# 最大限、既存の汎用ロジックを再利用する(再実装しない):
#   - er003_ja_to_en_translation.make_translator_fn(Web検索なし・
#     Structured Outputなしの実体。developer_messageだけ差し替える)
#   - er003_ja_to_en_translation.run_json_response_gate(技術的失敗+
#     JSON解析/スキーマ不適合を最大1回再試行する汎用ゲート)
#   - er003_ja_to_en_translation.compute_word_count/split_sentences
#     (決定的な語数・文分割ロジック)
#   - er003_ja_to_en_translation_p1b.validate_p1b_structure(固定構造
#     検証。B2版がテーマ表現・Point見出しの文言をB2向けに自然に言い換え
#     ても、固定文字列(Today's/Points/Point One:/Point Two:/In One Line)
#     自体の検証ロジックは変わらないため、そのまま使える)
#   - er003_ja_to_en_translation_p1b.run_translator_structure_gate
#     (構造不適合時のみ最大1回再試行するゲート。技術的失敗の扱いも
#     P1Bと同一のため再実装しない)

from __future__ import annotations

import json
import re
from typing import Any, Optional

import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b

EXPERIMENT_VERSION = "ER-003-P2"

B2_ADAPTER_MODEL = er003.TRANSLATOR_MODEL  # "gpt-5.6-sol"(P1/P1Bと不変)
B2_ADAPTER_REASONING_EFFORT = er003.TRANSLATOR_REASONING_EFFORT  # "high"(P1/P1Bと不変)
B2_ADAPTER_DEVELOPER_MESSAGE = "英語ポッドキャスト原稿を、CEFR B2学習者向けの自然な英語に調整してください。"

B2_ADAPTER_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_adapter_prompt_template.txt"
B2_FIDELITY_QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_fidelity_qa_prompt_template.txt"
B2_DIFFICULTY_QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_difficulty_qa_prompt_template.txt"

NATURAL_SOURCE_PATHS = {
    "A01": "er003_output/p1b/A01/natural_source_approved.md",
    "A02": "er003_output/p1b/A02/natural_source_approved.md",
    "ADD03": "er003_output/p1b/ADD03/natural_source_approved.md",
}
ARTICLE_TOPICS = er003.ARTICLE_TOPICS

# run_json_response_gateはtranslator/fidelity QA/難易度評価いずれの
# 用途にも依存しない汎用実装のため、そのまま再利用する。
run_json_response_gate = er003.run_json_response_gate

# 構造検証・構造ゲートはP1Bと完全に同一(固定文字列の検証ロジックは
# B2化で変わらない)。
validate_b2_structure = p1b.validate_p1b_structure
run_b2_adapter_structure_gate = p1b.run_translator_structure_gate


def load_natural_english_source(topic_id: str) -> str:
    with open(NATURAL_SOURCE_PATHS[topic_id], encoding="utf-8") as f:
        return f.read()


# ============================================================
# ブロック1: B2 adapterプロンプト構築・API呼び出し
# ============================================================
def load_b2_adapter_prompt_template(path: str = B2_ADAPTER_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_b2_adapter_user_message(approved_natural_english_source: str, template: Optional[str] = None) -> str:
    """テンプレート中にはTheme表現やPoint見出しの書式例など、モデルへの
    指示としての文字通りの中括弧書きが複数含まれるため、.format()では
    なく単一プレースホルダーだけを対象にした.replace()を使う。"""
    template = template if template is not None else load_b2_adapter_prompt_template()
    return template.replace("{approved_natural_english_source}", approved_natural_english_source)


def make_b2_adapter_fn(user_message: str, client: Optional[Any] = None):
    """er003.make_translator_fnをそのまま再利用する(Web検索なし・
    Structured Outputなしの実体は完全に同一。developer_messageだけ
    B2 adapter用に差し替える)。"""
    return er003.make_translator_fn(
        user_message, client=client, model=B2_ADAPTER_MODEL,
        reasoning_effort=B2_ADAPTER_REASONING_EFFORT, developer_message=B2_ADAPTER_DEVELOPER_MESSAGE,
    )


# ============================================================
# ブロック2: 決定的な文章指標(B2境界値をここでチェックする)
# ============================================================
B2_MAX_AVG_WORDS_PER_SENTENCE = 19.00
B2_MAX_SENTENCE_WORD_COUNT = 32

_HEADING_LINE_RE = re.compile(r"(?m)^#{1,6}[ \t].*$")


def strip_heading_lines(text: str) -> str:
    """Markdown見出し行そのものを除去する(strip_markdown_symbolsは
    見出し記号だけを取り、見出しテキスト自体は残すため、平均文長計算
    からMarkdown見出しを除外する目的には別途この関数を使う)。"""
    return _HEADING_LINE_RE.sub("", text)


def compute_b2_sentence_metrics(raw_text: str) -> dict:
    """総語数は見出し込み・本文のみの両方を保存する。平均文長・最長文・
    文分割は見出しを除外した本文のみを対象にする(引用符内のIn One Line
    本文は通常の文として計測対象に含まれる)。"""
    plain_with_headings = er003.article_gen.strip_markdown_symbols(raw_text)
    body_only_raw = strip_heading_lines(raw_text)
    plain_body_only = er003.article_gen.strip_markdown_symbols(body_only_raw)

    total_word_count_including_headings = er003.compute_word_count(plain_with_headings)
    total_word_count_body_only = er003.compute_word_count(plain_body_only)

    sentences = er003.split_sentences(plain_body_only)
    sentence_word_counts = [er003.compute_word_count(s) for s in sentences]
    total_sentence_count = len(sentences)
    avg_words_per_sentence = round(sum(sentence_word_counts) / total_sentence_count, 2) if total_sentence_count else 0.0
    longest_sentence_word_count = max(sentence_word_counts) if sentence_word_counts else 0
    sentences_over_32 = [w for w in sentence_word_counts if w > B2_MAX_SENTENCE_WORD_COUNT]
    at_or_under_19_ratio = (
        round(sum(1 for w in sentence_word_counts if w <= 19) / total_sentence_count, 4)
        if total_sentence_count else 0.0
    )

    avg_status = "PASS" if avg_words_per_sentence <= B2_MAX_AVG_WORDS_PER_SENTENCE else "FAIL"
    longest_status = "PASS" if longest_sentence_word_count <= B2_MAX_SENTENCE_WORD_COUNT else "FAIL"
    overall_status = "B2_SENTENCE_METRICS_PASS" if (avg_status == "PASS" and longest_status == "PASS") else "B2_SENTENCE_METRICS_FAIL"

    return {
        "total_word_count_including_headings": total_word_count_including_headings,
        "total_word_count_body_only": total_word_count_body_only,
        "total_sentence_count": total_sentence_count,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_words_per_sentence_status": avg_status,
        "longest_sentence_word_count": longest_sentence_word_count,
        "longest_sentence_status": longest_status,
        "sentences_over_32_word_count": len(sentences_over_32),
        "sentences_at_or_under_19_ratio": at_or_under_19_ratio,
        "estimated_reading_time_minutes": er003.compute_estimated_reading_times(total_word_count_including_headings),
        "overall_status": overall_status,
    }


# ============================================================
# ブロック3: B2整合性QA(adapterとは別の新規API実行、Web検索なし)
# ============================================================
B2_FIDELITY_QA_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")

B2_FIDELITY_QA_JSON_SCHEMA = {
    "name": "b2_translation_fidelity_qa",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": list(B2_FIDELITY_QA_VERDICTS)},
            "meaning_changes": {"type": "array", "items": {"type": "string"}},
            "important_omissions": {"type": "array", "items": {"type": "string"}},
            "unsupported_additions": {"type": "array", "items": {"type": "string"}},
            "number_name_negation_issues": {"type": "array", "items": {"type": "string"}},
            "causality_changes": {"type": "array", "items": {"type": "string"}},
            "angle_preservation_notes": {"type": "array", "items": {"type": "string"}},
            "in_one_line_preservation_notes": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["verdict", "meaning_changes", "important_omissions", "unsupported_additions",
                     "number_name_negation_issues", "causality_changes", "angle_preservation_notes",
                     "in_one_line_preservation_notes", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_B2_FIDELITY_QA_REQUIRED_FIELD_TYPES = {
    "verdict": str,
    "meaning_changes": list,
    "important_omissions": list,
    "unsupported_additions": list,
    "number_name_negation_issues": list,
    "causality_changes": list,
    "angle_preservation_notes": list,
    "in_one_line_preservation_notes": list,
    "notes": str,
}
_B2_FIDELITY_QA_STRING_LIST_FIELDS = tuple(
    k for k, v in _B2_FIDELITY_QA_REQUIRED_FIELD_TYPES.items() if v is list
)


def parse_and_validate_b2_fidelity_qa_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _B2_FIDELITY_QA_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise er003.QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise er003.QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    for list_field in _B2_FIDELITY_QA_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise er003.QaSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")
    if parsed["verdict"] not in B2_FIDELITY_QA_VERDICTS:
        raise er003.QaSchemaError(
            f"verdictは{B2_FIDELITY_QA_VERDICTS}のいずれかである必要があります(実際: {parsed['verdict']!r})")
    return parsed


def load_b2_fidelity_qa_prompt_template(path: str = B2_FIDELITY_QA_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_b2_fidelity_qa_prompt(japanese_article: str, natural_english_source: str, b2_version: str,
                                 template: Optional[str] = None) -> str:
    template = template if template is not None else load_b2_fidelity_qa_prompt_template()
    return template.format(
        japanese_article=japanese_article, natural_english_source=natural_english_source, b2_version=b2_version)


def make_b2_fidelity_qa_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = B2_ADAPTER_MODEL,
    reasoning_effort: str = B2_ADAPTER_REASONING_EFFORT,
):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **B2_FIDELITY_QA_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("B2 fidelity QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


# ============================================================
# ブロック4: B2難易度QA(adapter・fidelity QAとは別の新規API実行)
# ============================================================
B2_DIFFICULTY_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")
B2_DIFFICULTY_CEFR_LEVELS = er003.DIFFICULTY_CEFR_LEVELS

B2_DIFFICULTY_JSON_SCHEMA = {
    "name": "b2_difficulty_qa",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": list(B2_DIFFICULTY_VERDICTS)},
            "estimated_cefr": {"type": "string", "enum": list(B2_DIFFICULTY_CEFR_LEVELS)},
            "above_b2_candidates": {"type": "array", "items": {"type": "string"}},
            "essential_technical_terms": {"type": "array", "items": {"type": "string"}},
            "complex_sentence_notes": {"type": "array", "items": {"type": "string"}},
            "information_density_notes": {"type": "array", "items": {"type": "string"}},
            "over_simplification_notes": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["verdict", "estimated_cefr", "above_b2_candidates", "essential_technical_terms",
                     "complex_sentence_notes", "information_density_notes", "over_simplification_notes", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_B2_DIFFICULTY_REQUIRED_FIELD_TYPES = {
    "verdict": str,
    "estimated_cefr": str,
    "above_b2_candidates": list,
    "essential_technical_terms": list,
    "complex_sentence_notes": list,
    "information_density_notes": list,
    "over_simplification_notes": list,
    "notes": str,
}
_B2_DIFFICULTY_STRING_LIST_FIELDS = tuple(
    k for k, v in _B2_DIFFICULTY_REQUIRED_FIELD_TYPES.items() if v is list
)


def parse_and_validate_b2_difficulty_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _B2_DIFFICULTY_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise er003.QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise er003.QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    for list_field in _B2_DIFFICULTY_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise er003.QaSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")
    if parsed["verdict"] not in B2_DIFFICULTY_VERDICTS:
        raise er003.QaSchemaError(
            f"verdictは{B2_DIFFICULTY_VERDICTS}のいずれかである必要があります(実際: {parsed['verdict']!r})")
    if parsed["estimated_cefr"] not in B2_DIFFICULTY_CEFR_LEVELS:
        raise er003.QaSchemaError(
            f"estimated_cefrは{B2_DIFFICULTY_CEFR_LEVELS}のいずれかである必要があります"
            f"(実際: {parsed['estimated_cefr']!r})")
    return parsed


def load_b2_difficulty_qa_prompt_template(path: str = B2_DIFFICULTY_QA_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_b2_difficulty_qa_prompt(b2_version: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_b2_difficulty_qa_prompt_template()
    return template.format(b2_version=b2_version)


def make_b2_difficulty_qa_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = B2_ADAPTER_MODEL,
    reasoning_effort: str = B2_ADAPTER_REASONING_EFFORT,
):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **B2_DIFFICULTY_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("B2難易度QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn
