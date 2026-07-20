# ============================================================
# er003_b2_key_words.py
# ER-003-P2D: B2 Key Words 5個の選定・日本語グロス検証
# ============================================================
# 承認済みのBefore You Listen概要(summary_en_approved.md)と確定済み
# B2本文(er003_output/p2/<TOPIC>/b2_version_raw.md)のみをselectorへ
# 入力し、本編を聞く前に知っていると理解しやすくなる英語表現をちょうど
# 5個選ぶ。日本語原稿・Natural English Source・P1/P1Bの生応答・Web検索
# 結果・fact registry・fidelity QA・difficulty QA・既存のKey Words例・
# 外部辞書・外部語彙リスト・TTS情報・他記事の本文/概要/Key Wordsは
# selectorへ一切渡さない。
#
# Key Wordsは単語に限定せず、句動詞・コロケーション・慣用的なまとまり・
# 専門表現を対象とする。選定は必ず本文中の実際の表現(source_form)に
# 対応させ、display_phraseは活用形を基本形へ直す程度の正規化のみ許容
# する(意味の異なる別表現への意訳は不可)。
#
# 固定構造(exactly 5 items・schema)・本文対応(source_sentence/
# source_formの実在)はプロダクト上の明示要件のため、これらの不適合の
# みAPI技術的失敗と合わせて最大1回だけ同一条件で再試行する。内容品質
# (選定価値の高低、専門語偏重、グロスの不自然さ等)を理由とした自動
# 再生成は行わない。
#
# Key Words読み上げ原稿はLLMに自由生成させず、検証済みのselection JSON
# から決定的に構成する。
#
# 独立QAはselectorとは別の新規API実行として行う。QA結果を理由とした
# 選定の自動再生成・書き換えは行わない。
#
# 再利用するもの(再実装しない):
#   - er003_b2_summary.B2_INPUT_PATHS/load_approved_b2_article(確定
#     済みB2本文のパス・読み込み関数はP2Bと完全に同一)
#   - er003_ja_to_en_translation.TRANSLATOR_MODEL/TRANSLATOR_REASONING_
#     EFFORT("gpt-5.6-sol"/"high"。P1/P1B/B2 adapter/P2Bと不変)
#   - er003_ja_to_en_translation.run_json_response_gate(独立QA用。
#     技術的失敗+JSON解析/スキーマ不適合を最大1回再試行する汎用ゲート)
#   - er003_ja_to_en_translation.compute_word_count/sha256_text

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_b2_summary as summary_mod
import er003_ja_to_en_translation as er003

EXPERIMENT_VERSION = "ER-003-P2D"

# P1/P1B/B2 adapter/P2Bから不変のまま再利用(再定義しない)
SELECTOR_MODEL = er003.TRANSLATOR_MODEL  # "gpt-5.6-sol"
SELECTOR_REASONING_EFFORT = er003.TRANSLATOR_REASONING_EFFORT  # "high"
SELECTOR_DEVELOPER_MESSAGE = "英語ポッドキャスト本編の理解を助けるKey Wordsを選定してください。"

SELECTOR_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_key_words_selector_prompt_template.txt"
QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_key_words_qa_prompt_template.txt"

# 確定済みB2本文はP2Bと完全に同一のパスを使う(独立に定義しない)。
B2_INPUT_PATHS = summary_mod.B2_INPUT_PATHS
ARTICLE_TOPICS = summary_mod.ARTICLE_TOPICS
load_approved_b2_article = summary_mod.load_approved_b2_article

# ER-003-P2Cで確定した正式参照先(Before You Listenの承認済み確定文面)。
APPROVED_SUMMARY_PATHS = {
    "A01": "er003_output/p2b/A01/summary_en_approved.md",
    "A02": "er003_output/p2b/A02/summary_en_approved.md",
    "ADD03": "er003_output/p2b/ADD03/summary_en_approved.md",
}


def load_approved_summary(topic_id: str) -> str:
    with open(APPROVED_SUMMARY_PATHS[topic_id], encoding="utf-8") as f:
        return f.read()


# ============================================================
# ブロック1: selector schema・prompt構築・API呼び出し
# ============================================================
ITEM_TYPES = ("word", "phrasal_verb", "collocation", "idiomatic_phrase", "technical_term")
REUSE_VALUES = ("HIGH", "MEDIUM", "LOW")
SPOILER_RISKS = ("LOW", "MEDIUM", "HIGH")
KEY_WORDS_ITEM_COUNT = 5

KEY_WORDS_JSON_SCHEMA = {
    "name": "b2_key_words_selection",
    "schema": {
        "type": "object",
        "properties": {
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
                        "difficulty_reason": {"type": "string"},
                        "reuse_value": {"type": "string", "enum": list(REUSE_VALUES)},
                        "spoiler_risk": {"type": "string", "enum": list(SPOILER_RISKS)},
                    },
                    "required": ["order", "display_phrase", "source_form", "source_sentence", "ja_gloss",
                                 "item_type", "selection_reason", "difficulty_reason", "reuse_value",
                                 "spoiler_risk"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["article_id", "items"],
        "additionalProperties": False,
    },
    "strict": True,
}


def load_selector_prompt_template(path: str = SELECTOR_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_selector_user_message(approved_summary: str, approved_b2_article: str,
                                 template: Optional[str] = None) -> str:
    template = template if template is not None else load_selector_prompt_template()
    return template.replace("{approved_summary}", approved_summary).replace(
        "{approved_b2_article}", approved_b2_article)


class SelectorModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。技術的失敗として扱う。"""


def make_selector_fn(
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

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **KEY_WORDS_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise SelectorModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("Key Words selector応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


# ============================================================
# ブロック2: 決定的validator(本文対応・重複・禁止項目の検証)
# ============================================================
_REQUIRED_ITEM_FIELDS = ("order", "display_phrase", "source_form", "source_sentence", "ja_gloss",
                          "item_type", "selection_reason", "difficulty_reason", "reuse_value", "spoiler_risk")
_STRING_FIELDS = ("display_phrase", "source_form", "source_sentence", "ja_gloss",
                   "selection_reason", "difficulty_reason")

_DIGITS_ONLY_RE = re.compile(r"^\d+([.,]\d+)?%?$")
_DATE_ONLY_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+\d{1,2}(,?\s*\d{2,4})?$"
    r"|^\d{1,2}/\d{1,2}(/\d{2,4})?$",
    re.IGNORECASE,
)
_JAPANESE_CHAR_RE = re.compile(r"[ぁ-んァ-ヶ一-龯]")


def _normalize_for_match(text: str) -> str:
    """Unicode正規化(NFKC)・カーリークォート→ストレート・小文字化・空白圧縮のみを
    行う正規化比較。意味的な言い換えは吸収しない(厳密な実在確認のため)。"""
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = normalized.translate(str.maketrans({
        "‘": "'", "’": "'", "“": '"', "”": '"',
    }))
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _is_digits_only(text: str) -> bool:
    return bool(_DIGITS_ONLY_RE.match(text.strip()))


def _is_date_only(text: str) -> bool:
    return bool(_DATE_ONLY_RE.match(text.strip()))


def _has_japanese_characters(text: str) -> bool:
    return bool(_JAPANESE_CHAR_RE.search(text or ""))


def validate_key_words_selection(parsed: dict, b2_article_text: str) -> dict:
    """selector出力を決定的に検証する。比較・監査のための判定のみを行い、
    項目の追加・修正・入れ替えは一切行わない。固有名詞判定は誤判定の
    可能性があるため、数字のみ・日付のみの機械的に確実な範囲のみを
    自動不合格とし、それ以外の固有名詞疑いはQAへ回す(reasonsに記録
    するが、それ単独では不合格にしない)。"""
    reasons = []
    ok = True
    item_reasons: list = []

    items = parsed.get("items") if isinstance(parsed, dict) else None
    if not isinstance(items, list):
        return {"status": "KEY_WORDS_STRUCTURE_INVALID", "reasons": ["'items'が配列でない"], "item_reasons": []}

    if len(items) != KEY_WORDS_ITEM_COUNT:
        reasons.append(f"itemsが{KEY_WORDS_ITEM_COUNT}件でない(実際: {len(items)}件)")
        ok = False

    plain_article = er003.article_gen.strip_markdown_symbols(b2_article_text)
    normalized_raw_article = _normalize_for_match(b2_article_text)
    normalized_plain_article = _normalize_for_match(plain_article)

    orders = []
    display_phrases = []
    source_forms = []

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
        if item.get("reuse_value") not in REUSE_VALUES:
            this_item_reasons.append(f"reuse_valueが不正(実際: {item.get('reuse_value')!r})")
            ok = False
        if item.get("spoiler_risk") not in SPOILER_RISKS:
            this_item_reasons.append(f"spoiler_riskが不正(実際: {item.get('spoiler_risk')!r})")
            ok = False

        order = item.get("order")
        orders.append(order)

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

    if item_reasons:
        ok = False

    return {
        "status": "KEY_WORDS_STRUCTURE_PASS" if ok else "KEY_WORDS_STRUCTURE_INVALID",
        "reasons": reasons,
        "item_reasons": item_reasons,
    }


def parse_selector_json(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    return parsed


MAX_SELECTION_RETRY_ATTEMPTS = 2  # 初回 + (技術的失敗 または 構造/本文対応不適合)時の再試行1回のみ


def run_key_words_selection_gate(
    make_selector_factory: Callable[[], Callable],
    b2_article_text: str,
    max_attempts: int = MAX_SELECTION_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、またはexactly 5・schema・本文対応の不適合であれば、
    同一条件(同一model・同一reasoning effort・同一prompt・同一入力)で
    最大1回だけ再試行する。内容品質(選定価値、専門語偏重、グロスの
    不自然さ等)を理由とした再試行・再生成は行わない。再試行時に追加の
    エラーメッセージや修正指示をpromptへ加えない。

    戻り値: (parsed, final_status, attempts_detail, model_id, response_id)
    final_status: "KEY_WORDS_STRUCTURE_PASS" / "KEY_WORDS_STRUCTURE_INVALID"
                  / "TECHNICAL_GENERATION_FAILED" / "PARSE_FAILED"
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

        validation = validate_key_words_selection(parsed, b2_article_text)
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
# ブロック3: Key Words読み上げ原稿(決定的生成。LLMに自由生成させない)
# ============================================================
_NUMBER_WORDS = ("One", "Two", "Three", "Four", "Five")


def build_key_words_reading_copy(items: list) -> str:
    """検証済みのselection JSONから決定的に構成する。display phrase・
    日本語グロスを書き換えず、例文・発音記号も追加しない。音声順は
    英語→日本語→英語(display_phraseを前後で繰り返す)。"""
    sorted_items = sorted(items, key=lambda it: it["order"])
    lines = ["## Key Words", ""]
    for idx, item in enumerate(sorted_items):
        lines.append(f"### Number {_NUMBER_WORDS[idx]}")
        lines.append("")
        lines.append(item["display_phrase"])
        lines.append("")
        lines.append(item["ja_gloss"])
        lines.append("")
        lines.append(item["display_phrase"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ============================================================
# ブロック4: 決定的な指標(Pythonで計測。LLMには数えさせない)
# ============================================================
def compute_key_words_metrics(items: list, reading_copy: str) -> dict:
    sorted_items = sorted(items, key=lambda it: it["order"])
    item_type_counts = {t: 0 for t in ITEM_TYPES}
    reuse_value_counts = {v: 0 for v in REUSE_VALUES}
    spoiler_risk_counts = {r: 0 for r in SPOILER_RISKS}
    per_item = []
    for item in sorted_items:
        item_type_counts[item["item_type"]] = item_type_counts.get(item["item_type"], 0) + 1
        reuse_value_counts[item["reuse_value"]] = reuse_value_counts.get(item["reuse_value"], 0) + 1
        spoiler_risk_counts[item["spoiler_risk"]] = spoiler_risk_counts.get(item["spoiler_risk"], 0) + 1
        per_item.append({
            "order": item["order"],
            "display_phrase_word_count": er003.compute_word_count(item["display_phrase"]),
            "ja_gloss_char_count": len(item["ja_gloss"]),
        })
    display_phrases_normalized = [_normalize_for_match(it["display_phrase"]) for it in sorted_items]
    return {
        "item_count": len(sorted_items),
        "item_type_counts": item_type_counts,
        "reuse_value_counts": reuse_value_counts,
        "spoiler_risk_counts": spoiler_risk_counts,
        "per_item": per_item,
        "display_phrase_exact_duplicate_count": len(display_phrases_normalized) - len(set(display_phrases_normalized)),
        "reading_copy_word_count": er003.compute_word_count(
            er003.article_gen.strip_markdown_symbols(reading_copy)),
    }


# ============================================================
# ブロック5: 独立Key Words QA(selectorとは別の新規API実行、Web検索なし)
# ============================================================
run_json_response_gate = er003.run_json_response_gate

QA_TRIAGE_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")
QA_VALUE_LEVELS = ("HIGH", "MEDIUM", "LOW")
QA_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")

KEY_WORDS_QA_JSON_SCHEMA = {
    "name": "b2_key_words_qa",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": list(QA_TRIAGE_VERDICTS)},
            "items": {
                "type": "array",
                "minItems": KEY_WORDS_ITEM_COUNT,
                "maxItems": KEY_WORDS_ITEM_COUNT,
                "items": {
                    "type": "object",
                    "properties": {
                        "order": {"type": "integer"},
                        "source_match": {"type": "string", "enum": list(QA_TRIAGE_VERDICTS)},
                        "display_phrase_match": {"type": "string", "enum": list(QA_TRIAGE_VERDICTS)},
                        "gloss_accuracy": {"type": "string", "enum": list(QA_TRIAGE_VERDICTS)},
                        "comprehension_value": {"type": "string", "enum": list(QA_VALUE_LEVELS)},
                        "difficulty_value": {"type": "string", "enum": list(QA_VALUE_LEVELS)},
                        "reuse_value": {"type": "string", "enum": list(QA_VALUE_LEVELS)},
                        "spoiler_risk": {"type": "string", "enum": list(QA_RISK_LEVELS)},
                        "duplicate_risk": {"type": "string", "enum": list(QA_RISK_LEVELS)},
                        "notes": {"type": "string"},
                    },
                    "required": ["order", "source_match", "display_phrase_match", "gloss_accuracy",
                                 "comprehension_value", "difficulty_value", "reuse_value", "spoiler_risk",
                                 "duplicate_risk", "notes"],
                    "additionalProperties": False,
                },
            },
            "set_balance": {"type": "string", "enum": list(QA_TRIAGE_VERDICTS)},
            "low_value_filler_risk": {"type": "array", "items": {"type": "string"}},
            "technical_term_overload": {"type": "array", "items": {"type": "string"}},
            "missing_high_value_candidates": {"type": "array", "items": {"type": "string"}},
            "standalone_summary_dependency": {"type": "string", "enum": list(QA_TRIAGE_VERDICTS)},
            "notes": {"type": "string"},
        },
        "required": ["verdict", "items", "set_balance", "low_value_filler_risk", "technical_term_overload",
                     "missing_high_value_candidates", "standalone_summary_dependency", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_QA_REQUIRED_ITEM_FIELD_TYPES = {
    "order": int, "source_match": str, "display_phrase_match": str, "gloss_accuracy": str,
    "comprehension_value": str, "difficulty_value": str, "reuse_value": str, "spoiler_risk": str,
    "duplicate_risk": str, "notes": str,
}
_QA_REQUIRED_TOP_FIELD_TYPES = {
    "verdict": str, "items": list, "set_balance": str, "low_value_filler_risk": list,
    "technical_term_overload": list, "missing_high_value_candidates": list,
    "standalone_summary_dependency": str, "notes": str,
}
_QA_STRING_LIST_FIELDS = ("low_value_filler_risk", "technical_term_overload", "missing_high_value_candidates")


def parse_and_validate_key_words_qa_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _QA_REQUIRED_TOP_FIELD_TYPES.items():
        if field_name not in parsed:
            raise er003.QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise er003.QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    for list_field in _QA_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise er003.QaSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")
    if parsed["verdict"] not in QA_TRIAGE_VERDICTS:
        raise er003.QaSchemaError(f"verdictが不正です(実際: {parsed['verdict']!r})")
    if parsed["set_balance"] not in QA_TRIAGE_VERDICTS:
        raise er003.QaSchemaError(f"set_balanceが不正です(実際: {parsed['set_balance']!r})")
    if parsed["standalone_summary_dependency"] not in QA_TRIAGE_VERDICTS:
        raise er003.QaSchemaError(
            f"standalone_summary_dependencyが不正です(実際: {parsed['standalone_summary_dependency']!r})")
    if len(parsed["items"]) != KEY_WORDS_ITEM_COUNT:
        raise er003.QaSchemaError(f"itemsが{KEY_WORDS_ITEM_COUNT}件でありません(実際: {len(parsed['items'])}件)")
    for item in parsed["items"]:
        if not isinstance(item, dict):
            raise er003.QaSchemaError("QA itemがオブジェクトでありません")
        for field_name, expected_type in _QA_REQUIRED_ITEM_FIELD_TYPES.items():
            if field_name not in item:
                raise er003.QaSchemaError(f"QA itemに必須フィールド'{field_name}'がありません")
            if not isinstance(item[field_name], expected_type):
                raise er003.QaSchemaError(f"QA itemの'{field_name}'の型が不正です")
    return parsed


def load_qa_prompt_template(path: str = QA_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_qa_prompt(approved_summary: str, approved_b2_article: str, key_words_json: str,
                     template: Optional[str] = None) -> str:
    template = template if template is not None else load_qa_prompt_template()
    return (template.replace("{approved_summary}", approved_summary)
            .replace("{approved_b2_article}", approved_b2_article)
            .replace("{key_words_json}", key_words_json))


def make_qa_fn(
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
            text={"format": {"type": "json_schema", **KEY_WORDS_QA_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("Key Words QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn
