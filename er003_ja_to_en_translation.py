# ============================================================
# er003_ja_to_en_translation.py
# ER-003-P1: 制約なし自然英訳ベースライン検証
# ============================================================
# ER-002-v1.2M-R4-FINALIZEで正式採用された条件Lにより承認済みの日本語
# 記事(A01/A02/ADD03)を、CEFR・語彙・文長・語数などの制約を一切与えず、
# 短い自然文の指示だけで英語ポッドキャスト原稿へ翻訳する。
#
# 1テーマにつきtranslatorを1回実行する。複数記事の同時翻訳はしない。
# 英語マスター・阪神マスター・fact registryはtranslator入力に含めない。
# translatorにWeb検索ツールは与えない(日本語記事は既にR3/R4のWeb検索・
# fact-QA・ユーザー確認を通過済みであり、再検索は新情報混入のリスクに
# なるため)。
#
# 翻訳整合性QA・難易度評価は、translatorとは別の新規API実行として行う。
# いずれもWeb検索は使用しない。QA結果・難易度評価結果を理由とした
# 英訳の自動再生成は行わない。
#
# 再利用するもの(再実装しない):
#   - er002_ja_article_generation.WRITER_MODEL/WRITER_REASONING_EFFORT
#     (「gpt-5.6-sol」「high」— ER-002で確認済みの値をそのまま使う)
#   - er002_ja_article_generation.run_writer_technical_gate(技術的失敗
#     のみ最大1回再試行する汎用ゲート。テーマ横断で完全に同じロジック)
#   - er002_ja_free_markdown_restore_r2.validate_point_structure
#     (英語本文のH3見出し数チェックにもそのまま使える言語非依存の
#     チェック)
#   - er002_ja_article_generation.strip_markdown_symbols(難易度計測前の
#     Markdown記号除去)

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable, Optional

import er002_ja_article_generation as article_gen
import er002_ja_free_markdown_restore as restore
import er002_ja_free_markdown_restore_r2 as restore_r2

EXPERIMENT_VERSION = "ER-003-P1"

# ER-002で確認済みの値をそのまま使う(再定義しない)
TRANSLATOR_MODEL = article_gen.WRITER_MODEL  # "gpt-5.6-sol"
TRANSLATOR_REASONING_EFFORT = article_gen.WRITER_REASONING_EFFORT  # "high"

# fact QA・難易度評価も同一モデル・同一reasoning effortを使う(新しい
# モデルを検証なしに追加しないための判断)
FIDELITY_QA_MODEL = TRANSLATOR_MODEL
FIDELITY_QA_REASONING_EFFORT = TRANSLATOR_REASONING_EFFORT
DIFFICULTY_MODEL = TRANSLATOR_MODEL
DIFFICULTY_REASONING_EFFORT = TRANSLATOR_REASONING_EFFORT

TRANSLATOR_DEVELOPER_MESSAGE = "日本語の記事を自然な英語に翻訳してください。"

TRANSLATOR_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/translator_prompt_template.txt"
FIDELITY_QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/fidelity_qa_prompt_template.txt"
DIFFICULTY_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/difficulty_assessment_prompt_template.txt"

ARTICLE_TOPICS = {
    "A01": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
    "A02": "英国の未成年向け夜間SNS設定",
    "ADD03": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
}

# 翻訳元は条件Lの保存済みreading_copy.md(citation annotationで既に
# 引用表示を除去済みの確定日本語本文)を使う。R3の長文版・条件LB・
# 阪神マスターは翻訳対象として使用しない。
APPROVED_ARTICLE_SOURCE_PATHS = {
    "A01": "er002_output/v1_2m_r4/condition_l/A01/reading_copy.md",
    "A02": "er002_output/v1_2m_r4/condition_l/A02/reading_copy.md",
    "ADD03": "er002_output/v1_2m_r4/condition_l/ADD03/reading_copy.md",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_approved_japanese_article(topic_id: str) -> str:
    path = APPROVED_ARTICLE_SOURCE_PATHS[topic_id]
    return restore.load_text_file(path)


# ============================================================
# ブロック1: translatorプロンプト構築
# ============================================================
def load_translator_prompt_template(path: str = TRANSLATOR_PROMPT_TEMPLATE_PATH) -> str:
    return restore.load_text_file(path)


def build_translator_user_message(approved_japanese_article: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_translator_prompt_template()
    return template.format(approved_japanese_article=approved_japanese_article)


# ============================================================
# ブロック2: translator呼び出し(Web検索なし・Structured Outputなし)
# ============================================================
class TranslatorModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。技術的
    失敗として扱う(section 6の「指定モデル不一致」)。"""


def make_translator_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = TRANSLATOR_MODEL,
    reasoning_effort: str = TRANSLATOR_REASONING_EFFORT,
    developer_message: str = TRANSLATOR_DEVELOPER_MESSAGE,
):
    """Web検索ツールを一切与えない、自由Markdown出力のtranslator呼び出し
    関数を返す。日本語記事は既に検索・fact-QA・ユーザー確認済みであり、
    翻訳工程で新たな取材・記事設計は行わせない。"""
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def translator_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise TranslatorModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise restore.GenerationEmptyOrBrokenError("翻訳応答が空です")
        search_usage = {"web_search_call_count": 0, "queries": []}
        return text, response.model, response.id, search_usage, []

    translator_fn.model = model
    translator_fn.reasoning_effort = reasoning_effort
    translator_fn.developer_message = developer_message
    translator_fn.uses_web_search_tool = False
    translator_fn.response_format_used = False
    return translator_fn


# run_writer_technical_gateは完全に汎用(通信エラー・タイムアウト・
# 応答本文なし・モデル不一致のいずれでもtranslator_fnが例外を送出すれば
# 技術的失敗として最大1回だけ再試行する)。テーマ固有のロジックを一切
# 含まないため、そのまま再利用する。
run_translator_technical_gate = article_gen.run_writer_technical_gate


# ============================================================
# ブロック3: 英語構造チェック(記録のみ・自動修正しない)
# ============================================================
def _closing_summary_present_heuristic(text: str) -> bool:
    """レベル3見出し(###)の最後のセクション内に、Point本文以外の段落
    (一言まとめ相当)が存在するかどうかの簡易ヒューリスティック。
    見出し名称は固定せず、意味的な検証も行わない(あくまで参考情報)。"""
    parts = re.split(r"(?m)^###[ \t].*$", text)
    if len(parts) < 3:
        return False
    after_last_point_heading = parts[-1]
    paragraphs = [p for p in after_last_point_heading.split("\n\n") if p.strip()]
    return len(paragraphs) >= 2


def _ends_with_terminal_punctuation_heuristic(text: str) -> bool:
    """途中で切れていないかの簡易ヒューリスティック(文末の終端記号の
    有無を見るだけで、意味的な完結性は判定しない)。"""
    stripped = text.strip()
    return bool(re.search(r"[.!?\"'”。！？)]\s*$", stripped))


def check_english_structure(text: str) -> dict:
    """比較・監査のための記録のみを目的とする。構造不適合であっても、
    見出しの追加・修正やPointの選択・統合は一切行わない。"""
    structure = restore_r2.validate_point_structure(text)
    return {
        "not_empty": bool(text and text.strip()),
        "h3_heading_count": len(structure.headings),
        "structure_status": structure.status,
        "structure_headings": structure.headings,
        "structure_reasons": structure.reasons,
        "closing_summary_present_heuristic": _closing_summary_present_heuristic(text),
        "ends_with_terminal_punctuation_heuristic": _ends_with_terminal_punctuation_heuristic(text),
    }


# ============================================================
# ブロック4: JSON応答共通ゲート(技術的失敗+JSON解析/スキーマ不適合の
# いずれも最大1回だけ再試行する。Web検索の使用有無はチェックしない
# ―― fidelity QA・難易度評価のいずれにもWeb検索ツール自体を与えて
# いないため)
# ============================================================
MAX_JSON_RESPONSE_ATTEMPTS = 2  # 初回 + (技術的失敗 または JSON解析/スキーマ不適合)時の再試行1回のみ


def run_json_response_gate(
    make_fn: Callable[[], Callable],
    parse_and_validate_fn: Callable[[str], dict],
    max_attempts: int = MAX_JSON_RESPONSE_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """戻り値: (parsed_result, final_status, attempts_detail, model_id, response_id)
    final_status: "COMPLETED" / "TECHNICAL_FAILED" / "PARSE_FAILED"
    parsed_resultはCOMPLETED時のみ辞書、それ以外は必ずNone。"""
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        fn = make_fn()
        try:
            raw_text, model_id, response_id = fn()
        except Exception as e:
            attempts_detail.append({
                "attempt": attempt, "status": "TECHNICAL_FAILED",
                "error": f"{type(e).__name__}: {e}",
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "TECHNICAL_FAILED", attempts_detail, None, None

        try:
            parsed = parse_and_validate_fn(raw_text)
        except Exception as e:
            attempts_detail.append({
                "attempt": attempt, "status": "PARSE_FAILED", "error": str(e),
                "raw_text": raw_text, "model": model_id, "response_id": response_id,
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "PARSE_FAILED", attempts_detail, model_id, response_id

        attempts_detail.append({
            "attempt": attempt, "status": "COMPLETED",
            "model": model_id, "response_id": response_id,
        })
        return parsed, "COMPLETED", attempts_detail, model_id, response_id

    return None, "TECHNICAL_FAILED", attempts_detail, None, None


# ============================================================
# ブロック5: 翻訳整合性QA(translatorとは別の新規API実行、Web検索なし)
# ============================================================
class QaSchemaError(ValueError):
    """QA/難易度評価の出力がJSONとして解析できない、またはスキーマ要件
    を満たさない場合。"""


FIDELITY_QA_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")

FIDELITY_QA_JSON_SCHEMA = {
    "name": "translation_fidelity_qa",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": list(FIDELITY_QA_VERDICTS)},
            "meaning_changes": {"type": "array", "items": {"type": "string"}},
            "important_omissions": {"type": "array", "items": {"type": "string"}},
            "unsupported_additions": {"type": "array", "items": {"type": "string"}},
            "number_name_negation_issues": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["verdict", "meaning_changes", "important_omissions",
                     "unsupported_additions", "number_name_negation_issues", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_FIDELITY_QA_REQUIRED_FIELD_TYPES = {
    "verdict": str,
    "meaning_changes": list,
    "important_omissions": list,
    "unsupported_additions": list,
    "number_name_negation_issues": list,
    "notes": str,
}
_FIDELITY_QA_STRING_LIST_FIELDS = (
    "meaning_changes", "important_omissions", "unsupported_additions", "number_name_negation_issues",
)


def parse_and_validate_fidelity_qa_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _FIDELITY_QA_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    for list_field in _FIDELITY_QA_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise QaSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")
    if parsed["verdict"] not in FIDELITY_QA_VERDICTS:
        raise QaSchemaError(
            f"verdictは{FIDELITY_QA_VERDICTS}のいずれかである必要があります(実際: {parsed['verdict']!r})")
    return parsed


def load_fidelity_qa_prompt_template(path: str = FIDELITY_QA_PROMPT_TEMPLATE_PATH) -> str:
    return restore.load_text_file(path)


def build_fidelity_qa_prompt(japanese_article: str, english_translation: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_fidelity_qa_prompt_template()
    return template.format(japanese_article=japanese_article, english_translation=english_translation)


def make_fidelity_qa_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = FIDELITY_QA_MODEL,
    reasoning_effort: str = FIDELITY_QA_REASONING_EFFORT,
):
    """translatorの会話状態を一切引き継がない、新規・独立したResponses
    API呼び出し。Web検索ツールは与えない。Structured Outputを使う。"""
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fidelity_qa_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **FIDELITY_QA_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise restore.GenerationEmptyOrBrokenError("fidelity QA応答が空です")
        return text, response.model, response.id

    fidelity_qa_fn.model = model
    fidelity_qa_fn.reasoning_effort = reasoning_effort
    fidelity_qa_fn.uses_web_search_tool = False
    fidelity_qa_fn.uses_structured_output = True
    return fidelity_qa_fn


# ============================================================
# ブロック6: 難易度評価(translator・fidelity QAとは別の新規API実行、
# Web検索なし、英文は書き換えない)
# ============================================================
DIFFICULTY_CEFR_LEVELS = ("A2", "B1", "B1-B2", "B2", "B2-C1", "C1")

DIFFICULTY_JSON_SCHEMA = {
    "name": "difficulty_assessment",
    "schema": {
        "type": "object",
        "properties": {
            "estimated_cefr": {"type": "string", "enum": list(DIFFICULTY_CEFR_LEVELS)},
            "cefr_reasoning": {"type": "string"},
            "b2_exceeding_expressions": {"type": "array", "items": {"type": "string"}},
            "unavoidable_proper_nouns_or_technical_terms": {"type": "array", "items": {"type": "string"}},
            "complex_clause_examples": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["estimated_cefr", "cefr_reasoning", "b2_exceeding_expressions",
                     "unavoidable_proper_nouns_or_technical_terms", "complex_clause_examples"],
        "additionalProperties": False,
    },
    "strict": True,
}

_DIFFICULTY_REQUIRED_FIELD_TYPES = {
    "estimated_cefr": str,
    "cefr_reasoning": str,
    "b2_exceeding_expressions": list,
    "unavoidable_proper_nouns_or_technical_terms": list,
    "complex_clause_examples": list,
}
_DIFFICULTY_STRING_LIST_FIELDS = (
    "b2_exceeding_expressions", "unavoidable_proper_nouns_or_technical_terms", "complex_clause_examples",
)


def parse_and_validate_difficulty_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _DIFFICULTY_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    for list_field in _DIFFICULTY_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise QaSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")
    if parsed["estimated_cefr"] not in DIFFICULTY_CEFR_LEVELS:
        raise QaSchemaError(
            f"estimated_cefrは{DIFFICULTY_CEFR_LEVELS}のいずれかである必要があります"
            f"(実際: {parsed['estimated_cefr']!r})")
    return parsed


def load_difficulty_prompt_template(path: str = DIFFICULTY_PROMPT_TEMPLATE_PATH) -> str:
    return restore.load_text_file(path)


def build_difficulty_prompt(english_translation: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_difficulty_prompt_template()
    return template.format(english_translation=english_translation)


def make_difficulty_assessment_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = DIFFICULTY_MODEL,
    reasoning_effort: str = DIFFICULTY_REASONING_EFFORT,
):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def difficulty_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **DIFFICULTY_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise restore.GenerationEmptyOrBrokenError("難易度評価応答が空です")
        return text, response.model, response.id

    difficulty_fn.model = model
    difficulty_fn.reasoning_effort = reasoning_effort
    difficulty_fn.uses_web_search_tool = False
    difficulty_fn.uses_structured_output = True
    return difficulty_fn


# ============================================================
# ブロック7: 決定的な文章指標(LLMに数えさせず、Pythonで計測する)
# ============================================================
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")

READING_SPEEDS_WPM = (130, 145, 160)


def compute_word_count(plain_text: str) -> int:
    return len(_WORD_RE.findall(plain_text))


def split_sentences(plain_text: str) -> list:
    normalized = re.sub(r"\s+", " ", plain_text.strip())
    if not normalized:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(normalized) if s.strip()]


def compute_sentence_metrics(plain_text: str) -> dict:
    """Markdown記号を除去したプレーンテキストを対象に計測する
    (見出し記号・強調記号が単語や文境界として誤カウントされないため)。"""
    sentences = split_sentences(plain_text)
    sentence_word_counts = [compute_word_count(s) for s in sentences]
    total_words = compute_word_count(plain_text)
    total_sentences = len(sentences)
    avg_words_per_sentence = (sum(sentence_word_counts) / total_sentences) if total_sentences else 0.0
    longest_sentence_word_count = max(sentence_word_counts) if sentence_word_counts else 0
    return {
        "total_word_count": total_words,
        "total_sentence_count": total_sentences,
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "longest_sentence_word_count": longest_sentence_word_count,
    }


def compute_estimated_reading_times(total_word_count: int) -> dict:
    """計算値は音声時間の保証ではない(参考値)。"""
    return {
        f"{wpm}_wpm_minutes": round(total_word_count / wpm, 2)
        for wpm in READING_SPEEDS_WPM
    }


def compute_difficulty_metrics(raw_english_text: str) -> dict:
    plain_text = article_gen.strip_markdown_symbols(raw_english_text)
    sentence_metrics = compute_sentence_metrics(plain_text)
    reading_times = compute_estimated_reading_times(sentence_metrics["total_word_count"])
    return {**sentence_metrics, "estimated_reading_time_minutes": reading_times}
