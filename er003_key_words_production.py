# ============================================================
# er003_key_words_production.py
# ER-003-P2I: B2 Key Words標準方式(L)の本番用selector・validator
# ============================================================
# ER-003-P2HのユーザーによるTop5評価(L=24点/30・U=24点/30で同点)を
# 受け、ER-003-P2Iの決定によりL方式(Listening Blocker Ranking)を
# 標準方式として採用した。本モジュールは、P2Gの10件研究版prompt/
# schema/validatorから、research-only文言(ちょうど10個・Rank6-10・
# research_band等)を取り除いた本番用(ちょうど5個)版を提供する。
#
# 最小学習単位のhard requirement判定ロジック(1〜5語・完全文/節排除・
# 有限助動詞排除・本文対応・重複禁止・日本語グロス必須)は、P2Gの
# er003_key_words_min_unit.validate_min_unit_selection()を
# expected_item_count引数経由でそのまま再利用する(再実装しない)。
# 同様にvalidate_display_phrase_form・_FINITE_AUX_WORDS等の判定関数・
# 定数もP2Gのものをそのまま再利用する。
#
# article_id/strategy_idは、P2Gと同じ原則でmodelのStructured Output
# schemaへ一切含めず、runtimeが決定的に付与する(P2Fのarticle_id
# 誤記問題の再発を構造的に防ぐ)。strategy_idは標準方式Lに固定するが、
# 将来の拡張に備えて引数として受け取る形にする。
#
# Web検索は使用しない。入力は承認済み概要(approved_summary)と確定済み
# B2本文のみで、P2G/P2H/P2Iの過去成果物・ユーザー評価・他記事の内容は
# 一切selectorへ渡さない。

from __future__ import annotations

from typing import Any, Callable, Optional

import er003_b2_key_words as p2d
import er003_key_words_min_unit as p2g
import er003_ja_to_en_translation as er003

STANDARD_STRATEGY_ID = "L"
STANDARD_STRATEGY_NAME = "Listening Blocker Ranking"
PRODUCTION_ITEM_COUNT = 5

# P2D/P2E/P2Gから不変のまま再利用(再定義しない)
SELECTOR_MODEL = p2g.SELECTOR_MODEL
SELECTOR_REASONING_EFFORT = p2g.SELECTOR_REASONING_EFFORT
SELECTOR_DEVELOPER_MESSAGE = p2g.SELECTOR_DEVELOPER_MESSAGE

PRODUCTION_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_key_words_production_l_prompt_template.txt"

# 確定済み入力はP2D/P2E/P2F/P2Gと完全に同一のものを使う。
B2_INPUT_PATHS = p2d.B2_INPUT_PATHS
APPROVED_SUMMARY_PATHS = p2d.APPROVED_SUMMARY_PATHS
load_approved_b2_article = p2d.load_approved_b2_article
load_approved_summary = p2d.load_approved_summary

# P2Gのhard requirement判定ロジック・定数をそのまま再利用する。
PHRASE_TYPES = p2g.PHRASE_TYPES
NORMALIZATION_TYPES = p2g.NORMALIZATION_TYPES
TRI_LEVELS = p2g.TRI_LEVELS
PORTFOLIO_CATEGORIES = p2g.PORTFOLIO_CATEGORIES
DISPLAY_PHRASE_MIN_WORDS = p2g.DISPLAY_PHRASE_MIN_WORDS
DISPLAY_PHRASE_MAX_WORDS = p2g.DISPLAY_PHRASE_MAX_WORDS
validate_display_phrase_form = p2g.validate_display_phrase_form
SelectorModelMismatchError = p2g.SelectorModelMismatchError
parse_selector_json = p2g.parse_selector_json

_ITEM_SCHEMA_PROPERTIES = p2g._ITEM_SCHEMA_PROPERTIES
_ITEM_REQUIRED_FIELDS = p2g._ITEM_REQUIRED_FIELDS

SELECTOR_JSON_SCHEMA = {
    "name": "b2_key_words_production_l_selection",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "minItems": PRODUCTION_ITEM_COUNT,
                "maxItems": PRODUCTION_ITEM_COUNT,
                "items": {
                    "type": "object",
                    "properties": _ITEM_SCHEMA_PROPERTIES,
                    "required": list(_ITEM_REQUIRED_FIELDS),
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}


def load_production_prompt_template() -> str:
    return er003.restore.load_text_file(PRODUCTION_PROMPT_TEMPLATE_PATH)


def build_production_user_message(approved_summary: str, approved_b2_article: str,
                                   template: Optional[str] = None) -> str:
    template = template if template is not None else load_production_prompt_template()
    return template.replace("{approved_summary}", approved_summary).replace(
        "{approved_b2_article}", approved_b2_article)


def make_production_selector_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = SELECTOR_MODEL,
    reasoning_effort: str = SELECTOR_REASONING_EFFORT,
    developer_message: str = SELECTOR_DEVELOPER_MESSAGE,
):
    """strategy_idを引数に取らない(schemaは標準方式L専用に固定されて
    おり、Web検索ツールも使用しない)。"""
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **SELECTOR_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise SelectorModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("selector応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


def attach_runtime_metadata(parsed: dict, article_id: str, strategy_id: str = STANDARD_STRATEGY_ID) -> dict:
    """article_id/strategy_idはmodelの自己申告に一切依存せず、runtimeが
    決定的に付与する(P2Gと同じ原則)。本番版は全件が製品採用範囲の
    ため、P2Gのresearch_band(TOP_5/RANK_6_TO_10)は付与しない。"""
    return {
        "article_id": article_id,
        "strategy_id": strategy_id,
        "production_item_count": PRODUCTION_ITEM_COUNT,
        "items": list(parsed["items"]),
    }


def validate_production_selection(parsed_with_metadata: dict, b2_article_text: str) -> dict:
    """P2Gのhard requirement判定ロジックをexpected_item_count=5で
    そのまま再利用する(判定処理そのものは再実装しない)。"""
    return p2g.validate_min_unit_selection(parsed_with_metadata, b2_article_text,
                                            expected_item_count=PRODUCTION_ITEM_COUNT)


MAX_PRODUCTION_RETRY_ATTEMPTS = 2  # 初回 + 技術的失敗またはhard requirement不適合時の再試行1回のみ


def run_production_selection_gate(
    article_id: str,
    make_selector_factory: Callable[[], Callable],
    b2_article_text: str,
    strategy_id: str = STANDARD_STRATEGY_ID,
    max_attempts: int = MAX_PRODUCTION_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、またはexactly 5・rank1-5整合・1〜5語・完全文/節排除・
    有限助動詞排除・本文対応の不適合であれば、job毎に同一条件で最大1回
    だけ再試行する。article_id/strategy_idはmodelの自己申告に一切
    依存せず、この関数の引数(runtime指定値)をそのまま結果へ付与する。
    内容品質を理由とした再試行・再生成は行わない(P2Gと同じ原則)。

    戻り値: (parsed_with_metadata, final_status, attempts_detail, model_id, response_id)
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

        parsed_with_metadata = attach_runtime_metadata(parsed, article_id, strategy_id)
        validation = validate_production_selection(parsed_with_metadata, b2_article_text)
        attempts_detail.append({
            "attempt": attempt, "status": validation["status"], "validation_reasons": validation["reasons"],
            "item_reasons": validation["item_reasons"], "raw_text": raw_text,
            "parsed": parsed_with_metadata, "model": model_id, "response_id": response_id,
        })
        if validation["status"] == "KEY_WORDS_STRUCTURE_PASS":
            return parsed_with_metadata, "KEY_WORDS_STRUCTURE_PASS", attempts_detail, model_id, response_id
        if attempt < max_attempts:
            continue
        return parsed_with_metadata, "KEY_WORDS_STRUCTURE_INVALID", attempts_detail, model_id, response_id

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None


def build_production_reading_copy(items: list) -> str:
    """検証済みのselection JSON(rank1〜5)から、P2Dと同形式(Number
    One〜Five)のreading copyを決定的に構成する。rank->orderアダプタ
    経由でP2Dのbuild_key_words_reading_copyをそのまま再利用する。"""
    sorted_items = sorted(items, key=lambda it: it["rank"])
    adapted_items = [{**item, "order": item["rank"]} for item in sorted_items]
    return p2d.build_key_words_reading_copy(adapted_items)
