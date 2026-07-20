# ============================================================
# er003_key_words_strategy_compare.py
# ER-003-P2E: Key Words選定軸3方式の同時比較
# ============================================================
# ER-003-P2DのA01選定がユーザー感覚と合わなかったため、選定目的関数を
# 3方式(L: Listening Blocker Ranking / P: Difficulty Portfolio /
# U: Observed Learner Profile)で独立に生成し、比較する。
#
# 共通入力はA01の承認済み概要(summary_en_approved.md)と確定済みB2本文
# のみ。日本語原稿・Natural English Source・P1/P1B・現行P2Dの選定結果・
# QA・ユーザーが挙げた具体的な候補表現・Web検索結果・外部辞書・他記事・
# TTS情報はselectorへ一切渡さない。ユーザーの具体例(解説不要/解説希望
# 参照セット)は生成後の比較QA・ブラインドレビューだけに使う。
#
# 3方式は独立1 callずつ、合計3 call。一方式の結果を他方式のprompt/
# 生成へは渡さない。技術的失敗・schema/本文対応不適合のみ、方式ごと
# 最大1回同一条件で再試行する。内容品質(選定価値の主観的な良し悪し)
# を理由とした自動再生成は行わない。
#
# 再利用するもの(再実装しない):
#   - er003_b2_key_words.SELECTOR_MODEL/SELECTOR_REASONING_EFFORT
#     ("gpt-5.6-sol"/"high"。P2Dと不変)
#   - er003_b2_key_words.B2_INPUT_PATHS/APPROVED_SUMMARY_PATHS/
#     load_approved_b2_article/load_approved_summary(確定済み入力は
#     P2Dと完全に同一)
#   - er003_b2_key_words.build_key_words_reading_copy(検証済み
#     selection JSONから決定的に読み上げ原稿を構成するロジックは、
#     order/display_phrase/ja_glossフィールドだけに依存するため方式
#     問わず共通で使える)
#   - er003_ja_to_en_translation.run_json_response_gate(比較QA用)
#   - er003_ja_to_en_translation.sha256_text

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_b2_key_words as p2d
import er003_ja_to_en_translation as er003

EXPERIMENT_VERSION = "ER-003-P2E"
TARGET_TOPIC_ID = "A01"  # ユーザー文中のA02表記は誤記。列挙表現はA01(サッカー記事)に対応する。

# P2Dから不変のまま再利用(再定義しない)
SELECTOR_MODEL = p2d.SELECTOR_MODEL  # "gpt-5.6-sol"
SELECTOR_REASONING_EFFORT = p2d.SELECTOR_REASONING_EFFORT  # "high"
SELECTOR_DEVELOPER_MESSAGE = "英語ポッドキャストの初回リスニング理解を助けるKey Wordsを選定してください。"

STRATEGY_IDS = ("L", "P", "U")

STRATEGY_PROMPT_TEMPLATE_PATHS = {
    "L": "er003_v1_translator_briefs/b2_key_words_strategy_l_prompt_template.txt",
    "P": "er003_v1_translator_briefs/b2_key_words_strategy_p_prompt_template.txt",
    "U": "er003_v1_translator_briefs/b2_key_words_strategy_u_prompt_template.txt",
}
COMPARISON_QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_key_words_strategy_comparison_qa_prompt_template.txt"

# 確定済み入力はP2Dと完全に同一のものを使う(独立に定義しない)。
B2_INPUT_PATHS = p2d.B2_INPUT_PATHS
APPROVED_SUMMARY_PATHS = p2d.APPROVED_SUMMARY_PATHS
load_approved_b2_article = p2d.load_approved_b2_article
load_approved_summary = p2d.load_approved_summary

# 決定的な読み上げ原稿ビルダーはP2Dのものをそのまま使う
# (order/display_phrase/ja_glossだけに依存する共通ロジック)。
build_key_words_reading_copy = p2d.build_key_words_reading_copy

# 比較QAはselectorとは独立実行の技術的失敗+JSON解析/スキーマ不適合
# ゲートを再利用する(用途に依存しない汎用実装のため)。
run_json_response_gate = er003.run_json_response_gate

# 生成後の比較・ブラインドレビューにだけ使う参照セット(selectorへは
# 一切渡さない)。
USER_UNHELPFUL_REFERENCE = (
    "take the lead", "provide an assist", "protect a lead", "go the other way",
)
USER_HELPFUL_REFERENCE = (
    "famous rivalry", "shot on target", "fierce", "substitute", "powered a header into the net",
    "traded places", "took off players", "slipped two keys", "back-to-back titles", "crushing weight",
)

BLIND_MAPPING_SEED = 20260720  # ER-003-P2E固定seed(決定的なブラインド割当のため)


# ============================================================
# ブロック1: 共通schema・方式別prompt構築・API呼び出し
# ============================================================
ITEM_TYPES = ("word", "phrasal_verb", "collocation", "idiomatic_phrase", "technical_term", "listening_chunk")
TRI_LEVELS = ("LOW", "MEDIUM", "HIGH")
PORTFOLIO_CATEGORIES = (
    "general_unknown_word", "domain_expression", "listening_chunk", "figurative_emotional",
    "causal_contrast", "other",
)
KEY_WORDS_ITEM_COUNT = 5


def _strategy_json_schema(strategy_id: str) -> dict:
    return {
        "name": f"b2_key_words_strategy_{strategy_id.lower()}",
        "schema": {
            "type": "object",
            "properties": {
                "strategy_id": {"type": "string", "enum": list(STRATEGY_IDS)},
                "article_id": {"type": "string"},
                "items": {
                    "type": "array",
                    "minItems": KEY_WORDS_ITEM_COUNT,
                    "maxItems": KEY_WORDS_ITEM_COUNT,
                    "items": {
                        "type": "object",
                        "properties": {
                            "order": {"type": "integer"},
                            "display_phrase": {"type": "string"},
                            "source_form": {"type": "string"},
                            "source_sentence": {"type": "string"},
                            "ja_gloss": {"type": "string"},
                            "item_type": {"type": "string", "enum": list(ITEM_TYPES)},
                            "selection_reason": {"type": "string"},
                            "listening_difficulty_reason": {"type": "string"},
                            "inference_transparency": {"type": "string", "enum": list(TRI_LEVELS)},
                            "topic_exposure_dependency": {"type": "string", "enum": list(TRI_LEVELS)},
                            "comprehension_impact": {"type": "string", "enum": list(TRI_LEVELS)},
                            "figurative_or_emotional_value": {"type": "string", "enum": list(TRI_LEVELS)},
                            "spoiler_risk": {"type": "string", "enum": list(TRI_LEVELS)},
                            "portfolio_category": {"type": "string", "enum": list(PORTFOLIO_CATEGORIES)},
                            "portfolio_substitution": {"type": "boolean"},
                            "portfolio_substitution_reason": {"type": "string"},
                        },
                        "required": ["order", "display_phrase", "source_form", "source_sentence", "ja_gloss",
                                     "item_type", "selection_reason", "listening_difficulty_reason",
                                     "inference_transparency", "topic_exposure_dependency", "comprehension_impact",
                                     "figurative_or_emotional_value", "spoiler_risk", "portfolio_category",
                                     "portfolio_substitution", "portfolio_substitution_reason"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["strategy_id", "article_id", "items"],
            "additionalProperties": False,
        },
        "strict": True,
    }


STRATEGY_JSON_SCHEMAS = {strategy_id: _strategy_json_schema(strategy_id) for strategy_id in STRATEGY_IDS}


def load_strategy_prompt_template(strategy_id: str) -> str:
    return er003.restore.load_text_file(STRATEGY_PROMPT_TEMPLATE_PATHS[strategy_id])


def build_strategy_user_message(strategy_id: str, approved_summary: str, approved_b2_article: str,
                                 template: Optional[str] = None) -> str:
    template = template if template is not None else load_strategy_prompt_template(strategy_id)
    return template.replace("{approved_summary}", approved_summary).replace(
        "{approved_b2_article}", approved_b2_article)


class StrategySelectorModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。技術的失敗として扱う。"""


def make_strategy_selector_fn(
    strategy_id: str,
    user_message: str,
    client: Optional[Any] = None,
    model: str = SELECTOR_MODEL,
    reasoning_effort: str = SELECTOR_REASONING_EFFORT,
    developer_message: str = SELECTOR_DEVELOPER_MESSAGE,
):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    schema = STRATEGY_JSON_SCHEMAS[strategy_id]

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **schema}},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise StrategySelectorModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError(f"方式{strategy_id} selector応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    fn.strategy_id = strategy_id
    return fn


# ============================================================
# ブロック2: 決定的validator(本文対応・重複・禁止項目・P固有ルール)
# ============================================================
_REQUIRED_ITEM_FIELDS = (
    "order", "display_phrase", "source_form", "source_sentence", "ja_gloss", "item_type", "selection_reason",
    "listening_difficulty_reason", "inference_transparency", "topic_exposure_dependency", "comprehension_impact",
    "figurative_or_emotional_value", "spoiler_risk", "portfolio_category", "portfolio_substitution",
    "portfolio_substitution_reason",
)
_STRING_FIELDS = ("display_phrase", "source_form", "source_sentence", "ja_gloss",
                   "selection_reason", "listening_difficulty_reason")

_DIGITS_ONLY_RE = re.compile(r"^\d+([.,]\d+)?%?$")
_DATE_ONLY_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+\d{1,2}(,?\s*\d{2,4})?$"
    r"|^\d{1,2}/\d{1,2}(/\d{2,4})?$",
    re.IGNORECASE,
)
_JAPANESE_CHAR_RE = re.compile(r"[ぁ-んァ-ヶ一-龯]")


def _normalize_for_match(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = normalized.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _is_digits_only(text: str) -> bool:
    return bool(_DIGITS_ONLY_RE.match(text.strip()))


def _is_date_only(text: str) -> bool:
    return bool(_DATE_ONLY_RE.match(text.strip()))


def _has_japanese_characters(text: str) -> bool:
    return bool(_JAPANESE_CHAR_RE.search(text or ""))


def validate_strategy_selection(parsed: dict, b2_article_text: str, expected_strategy_id: str) -> dict:
    """selector出力を決定的に検証する。比較・監査のための判定のみを行い、
    項目の追加・修正・入れ替えは一切行わない。方式Pのみ、カテゴリ重複時
    にportfolio_substitution=trueと理由が記録されているかを追加で確認
    する。"""
    reasons = []
    ok = True
    item_reasons: list = []

    if not isinstance(parsed, dict):
        return {"status": "KEY_WORDS_STRUCTURE_INVALID", "reasons": ["トップレベルがオブジェクトでない"],
                "item_reasons": []}

    if parsed.get("strategy_id") != expected_strategy_id:
        reasons.append(f"strategy_idが不一致(期待: {expected_strategy_id}, 実際: {parsed.get('strategy_id')!r})")
        ok = False

    items = parsed.get("items")
    if not isinstance(items, list):
        reasons.append("'items'が配列でない")
        return {"status": "KEY_WORDS_STRUCTURE_INVALID", "reasons": reasons, "item_reasons": []}

    if len(items) != KEY_WORDS_ITEM_COUNT:
        reasons.append(f"itemsが{KEY_WORDS_ITEM_COUNT}件でない(実際: {len(items)}件)")
        ok = False

    plain_article = er003.article_gen.strip_markdown_symbols(b2_article_text)
    normalized_raw_article = _normalize_for_match(b2_article_text)
    normalized_plain_article = _normalize_for_match(plain_article)

    orders = []
    display_phrases = []
    source_forms = []
    categories = []

    for i, item in enumerate(items):
        this_item_reasons = []
        if not isinstance(item, dict):
            item_reasons.append({"index": i, "reasons": ["項目がオブジェクトでない"]})
            ok = False
            continue

        for field in _REQUIRED_ITEM_FIELDS:
            if field not in item:
                this_item_reasons.append(f"必須フィールド'{field}'がない")
                ok = False
        if this_item_reasons:
            item_reasons.append({"index": i, "reasons": this_item_reasons})
            continue

        for field in _STRING_FIELDS:
            if not isinstance(item[field], str) or not item[field].strip():
                this_item_reasons.append(f"'{field}'が空、または文字列でない")
                ok = False

        if item.get("item_type") not in ITEM_TYPES:
            this_item_reasons.append(f"item_typeが不正(実際: {item.get('item_type')!r})")
            ok = False
        for enum_field in ("inference_transparency", "topic_exposure_dependency", "comprehension_impact",
                           "figurative_or_emotional_value", "spoiler_risk"):
            if item.get(enum_field) not in TRI_LEVELS:
                this_item_reasons.append(f"{enum_field}が不正(実際: {item.get(enum_field)!r})")
                ok = False
        if item.get("portfolio_category") not in PORTFOLIO_CATEGORIES:
            this_item_reasons.append(f"portfolio_categoryが不正(実際: {item.get('portfolio_category')!r})")
            ok = False
        if not isinstance(item.get("portfolio_substitution"), bool):
            this_item_reasons.append("portfolio_substitutionがbooleanでない")
            ok = False

        order = item.get("order")
        orders.append(order)
        categories.append(item.get("portfolio_category"))

        display_phrase = item.get("display_phrase", "")
        source_form = item.get("source_form", "")
        source_sentence = item.get("source_sentence", "")
        ja_gloss = item.get("ja_gloss", "")

        if isinstance(display_phrase, str):
            display_phrases.append(_normalize_for_match(display_phrase))
        if isinstance(source_form, str):
            source_forms.append(_normalize_for_match(source_form))

        if isinstance(source_sentence, str) and source_sentence.strip():
            normalized_sentence = _normalize_for_match(source_sentence)
            source_match = (normalized_sentence in normalized_raw_article
                             or normalized_sentence in normalized_plain_article)
            if not source_match:
                this_item_reasons.append("source_sentenceがB2本文に存在しない")
                ok = False
            else:
                if isinstance(source_form, str) and source_form.strip():
                    if _normalize_for_match(source_form) not in normalized_sentence:
                        this_item_reasons.append("source_formがsource_sentence内に存在しない")
                        ok = False

        if isinstance(source_form, str) and source_form.strip():
            if _is_digits_only(source_form) or _is_digits_only(display_phrase):
                this_item_reasons.append("数字だけの項目")
                ok = False
            if _is_date_only(source_form) or _is_date_only(display_phrase):
                this_item_reasons.append("日付だけの項目")
                ok = False

        if isinstance(ja_gloss, str) and ja_gloss.strip():
            if not _has_japanese_characters(ja_gloss):
                this_item_reasons.append("日本語グロスに日本語文字が含まれない(英文の可能性)")
                ok = False

        if this_item_reasons:
            item_reasons.append({"index": i, "reasons": this_item_reasons})

    if orders and (sorted(o for o in orders if isinstance(o, int)) != list(range(1, KEY_WORDS_ITEM_COUNT + 1))
                   or len(orders) != len(set(orders))):
        reasons.append(f"orderが1〜{KEY_WORDS_ITEM_COUNT}の重複・欠番なしの並びでない(実際: {orders})")
        ok = False

    if len(display_phrases) != len(set(display_phrases)):
        reasons.append("display_phraseに重複がある")
        ok = False
    if len(source_forms) != len(set(source_forms)):
        reasons.append("source_formに重複がある")
        ok = False

    category_distribution = {}
    for i, cat in enumerate(categories):
        if cat is None:
            continue
        category_distribution[cat] = category_distribution.get(cat, 0) + 1

    if expected_strategy_id == "P":
        duplicated_categories = [cat for cat, count in category_distribution.items() if count > 1]
        if duplicated_categories:
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                if item.get("portfolio_category") in duplicated_categories:
                    if not item.get("portfolio_substitution"):
                        reasons.append(
                            f"方式Pでカテゴリ'{item.get('portfolio_category')}'が重複しているが、"
                            f"index {i}のportfolio_substitutionがtrueでない")
                        ok = False
                    elif not str(item.get("portfolio_substitution_reason", "")).strip():
                        reasons.append(f"方式Pでportfolio_substitution=trueだがindex {i}の理由が空")
                        ok = False

    if item_reasons:
        ok = False

    return {
        "status": "KEY_WORDS_STRUCTURE_PASS" if ok else "KEY_WORDS_STRUCTURE_INVALID",
        "reasons": reasons,
        "item_reasons": item_reasons,
        "category_distribution": category_distribution,
    }


def parse_selector_json(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    return parsed


MAX_STRATEGY_RETRY_ATTEMPTS = 2  # 初回 + (技術的失敗 または 構造/本文対応不適合)時の再試行1回のみ


def run_strategy_selection_gate(
    strategy_id: str,
    make_selector_factory: Callable[[], Callable],
    b2_article_text: str,
    max_attempts: int = MAX_STRATEGY_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、またはexactly 5・schema・本文対応・(方式Pのみ)
    substitution記録の不適合であれば、方式ごとに同一条件で最大1回だけ
    再試行する。内容品質(選定価値の主観的な良し悪し)を理由とした
    再試行・再生成は行わない。他方式の結果を参照しない。

    戻り値: (parsed, final_status, attempts_detail, model_id, response_id)
    """
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        selector_fn = make_selector_factory()
        try:
            raw_text, model_id, response_id = selector_fn()
        except Exception as e:
            attempts_detail.append({
                "attempt": attempt, "status": "TECHNICAL_GENERATION_FAILED",
                "error": f"{type(e).__name__}: {e}", "raw_text": None,
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None

        try:
            parsed = parse_selector_json(raw_text)
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

        validation = validate_strategy_selection(parsed, b2_article_text, strategy_id)
        attempts_detail.append({
            "attempt": attempt, "status": validation["status"], "validation_reasons": validation["reasons"],
            "item_reasons": validation["item_reasons"], "raw_text": raw_text,
            "parsed": parsed, "model": model_id, "response_id": response_id,
        })
        if validation["status"] == "KEY_WORDS_STRUCTURE_PASS":
            return parsed, "KEY_WORDS_STRUCTURE_PASS", attempts_detail, model_id, response_id
        if attempt < max_attempts:
            continue
        return parsed, "KEY_WORDS_STRUCTURE_INVALID", attempts_detail, model_id, response_id

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None


# ============================================================
# ブロック3: 決定的指標
# ============================================================
def compute_strategy_metrics(items: list, reading_copy: str) -> dict:
    sorted_items = sorted(items, key=lambda it: it["order"])
    item_type_counts = {t: 0 for t in ITEM_TYPES}
    category_counts = {c: 0 for c in PORTFOLIO_CATEGORIES}
    substitution_count = 0
    for item in sorted_items:
        item_type_counts[item["item_type"]] = item_type_counts.get(item["item_type"], 0) + 1
        category_counts[item["portfolio_category"]] = category_counts.get(item["portfolio_category"], 0) + 1
        if item.get("portfolio_substitution"):
            substitution_count += 1
    display_phrases_normalized = [_normalize_for_match(it["display_phrase"]) for it in sorted_items]
    return {
        "item_count": len(sorted_items),
        "item_type_counts": item_type_counts,
        "portfolio_category_counts": category_counts,
        "portfolio_substitution_count": substitution_count,
        "display_phrase_exact_duplicate_count": len(display_phrases_normalized) - len(set(display_phrases_normalized)),
        "reading_copy_word_count": er003.compute_word_count(
            er003.article_gen.strip_markdown_symbols(reading_copy)),
    }


# ============================================================
# ブロック4: 比較QA(3方式生成後、selectorとは独立の新規API実行)
# ============================================================
COMPARISON_QA_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")

COMPARISON_QA_JSON_SCHEMA = {
    "name": "b2_key_words_strategy_comparison_qa",
    "schema": {
        "type": "object",
        "properties": {
            "strategies": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {"type": "string", "enum": list(STRATEGY_IDS)},
                        "unknown_word_capture": {"type": "string", "enum": list(TRI_LEVELS)},
                        "domain_expression_capture": {"type": "string", "enum": list(TRI_LEVELS)},
                        "listening_chunk_capture": {"type": "string", "enum": list(TRI_LEVELS)},
                        "figurative_emotional_capture": {"type": "string", "enum": list(TRI_LEVELS)},
                        "transparent_easy_item_contamination": {"type": "string", "enum": list(TRI_LEVELS)},
                        "comprehension_contribution": {"type": "string", "enum": list(TRI_LEVELS)},
                        "diversity": {"type": "string", "enum": list(TRI_LEVELS)},
                        "overall_spoiler_risk": {"type": "string", "enum": list(TRI_LEVELS)},
                        "gloss_quality": {"type": "string", "enum": list(TRI_LEVELS)},
                        "helpful_reference_matches": {"type": "array", "items": {"type": "string"}},
                        "unhelpful_reference_overlaps": {"type": "array", "items": {"type": "string"}},
                        "notes": {"type": "string"},
                    },
                    "required": ["strategy_id", "unknown_word_capture", "domain_expression_capture",
                                 "listening_chunk_capture", "figurative_emotional_capture",
                                 "transparent_easy_item_contamination", "comprehension_contribution", "diversity",
                                 "overall_spoiler_risk", "gloss_quality", "helpful_reference_matches",
                                 "unhelpful_reference_overlaps", "notes"],
                    "additionalProperties": False,
                },
            },
            "cross_strategy_overlap": {"type": "array", "items": {"type": "string"}},
            "unique_items_by_strategy": {
                "type": "object",
                "properties": {s: {"type": "array", "items": {"type": "string"}} for s in STRATEGY_IDS},
                "required": list(STRATEGY_IDS),
                "additionalProperties": False,
            },
            "provisional_best_fit": {"type": "string", "enum": list(STRATEGY_IDS)},
            "notes": {"type": "string"},
        },
        "required": ["strategies", "cross_strategy_overlap", "unique_items_by_strategy",
                     "provisional_best_fit", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_QA_STRATEGY_REQUIRED_FIELD_TYPES = {
    "strategy_id": str, "unknown_word_capture": str, "domain_expression_capture": str,
    "listening_chunk_capture": str, "figurative_emotional_capture": str,
    "transparent_easy_item_contamination": str, "comprehension_contribution": str, "diversity": str,
    "overall_spoiler_risk": str, "gloss_quality": str, "helpful_reference_matches": list,
    "unhelpful_reference_overlaps": list, "notes": str,
}
_QA_TOP_REQUIRED_FIELD_TYPES = {
    "strategies": list, "cross_strategy_overlap": list, "unique_items_by_strategy": dict,
    "provisional_best_fit": str, "notes": str,
}


def parse_and_validate_comparison_qa_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _QA_TOP_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise er003.QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise er003.QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    if parsed["provisional_best_fit"] not in STRATEGY_IDS:
        raise er003.QaSchemaError(f"provisional_best_fitが不正です(実際: {parsed['provisional_best_fit']!r})")
    if len(parsed["strategies"]) != 3:
        raise er003.QaSchemaError(f"strategiesが3件でありません(実際: {len(parsed['strategies'])}件)")
    seen_strategy_ids = set()
    for strategy_eval in parsed["strategies"]:
        if not isinstance(strategy_eval, dict):
            raise er003.QaSchemaError("strategy評価がオブジェクトでありません")
        for field_name, expected_type in _QA_STRATEGY_REQUIRED_FIELD_TYPES.items():
            if field_name not in strategy_eval:
                raise er003.QaSchemaError(f"strategy評価に必須フィールド'{field_name}'がありません")
            if not isinstance(strategy_eval[field_name], expected_type):
                raise er003.QaSchemaError(f"strategy評価の'{field_name}'の型が不正です")
        if strategy_eval["strategy_id"] not in STRATEGY_IDS:
            raise er003.QaSchemaError(f"strategy_idが不正です(実際: {strategy_eval['strategy_id']!r})")
        seen_strategy_ids.add(strategy_eval["strategy_id"])
    if seen_strategy_ids != set(STRATEGY_IDS):
        raise er003.QaSchemaError(f"3方式すべてが評価されていません(実際: {seen_strategy_ids})")
    for key in STRATEGY_IDS:
        if key not in parsed["unique_items_by_strategy"]:
            raise er003.QaSchemaError(f"unique_items_by_strategyに'{key}'がありません")
    return parsed


def load_comparison_qa_prompt_template(path: str = COMPARISON_QA_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_comparison_qa_prompt(approved_summary: str, approved_b2_article: str,
                                strategy_results_json: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_comparison_qa_prompt_template()
    return (template.replace("{approved_summary}", approved_summary)
            .replace("{approved_b2_article}", approved_b2_article)
            .replace("{strategy_results_json}", strategy_results_json)
            .replace("{helpful_reference}", ", ".join(USER_HELPFUL_REFERENCE))
            .replace("{unhelpful_reference}", ", ".join(USER_UNHELPFUL_REFERENCE)))


def make_comparison_qa_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = SELECTOR_MODEL,
    reasoning_effort: str = SELECTOR_REASONING_EFFORT,
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
            text={"format": {"type": "json_schema", **COMPARISON_QA_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("比較QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


# ============================================================
# ブロック5: ブラインドマッピング(固定seedで決定的に生成)
# ============================================================
_BLIND_SET_LABELS = ("Set X", "Set Y", "Set Z")


def build_blind_mapping(seed: int = BLIND_MAPPING_SEED) -> dict:
    """L/P/UをSet X/Y/Zへ固定seedで決定的に割り当てる。同じseedであれば
    常に同じ割当になる。"""
    import random
    rng = random.Random(seed)
    shuffled_strategies = list(STRATEGY_IDS)
    rng.shuffle(shuffled_strategies)
    return {label: strategy_id for label, strategy_id in zip(_BLIND_SET_LABELS, shuffled_strategies)}
