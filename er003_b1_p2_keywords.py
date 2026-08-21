# ============================================================
# er003_b1_p2_keywords.py
# ER-003-B1-P2 Part A: A01 B1本文へのL方式Key Words選定
# ============================================================
# ER-003-P2Iで正式採用した標準方式(L: Listening Blocker Ranking)の
# production selector・validator・runtime metadataの仕組みを、入力を
# 承認済みA01 B1本文(ER-003-B1-P1)へ差し替えて再利用する。新しい選定
# ロジックは一切設計しない。
#
# B2本文・B2で承認済みのKey Wordsは一切使わない(承認済み5件を候補として
# 固定する、B2選定語を流用する、いずれも行わない)。B2から引き継ぐのは
# 「選定語」ではなく、L方式のロジック(schema/validator/runtime
# metadata付与)そのものである。
#
# 自動再選定・自動再実行は行わない(このステージではmax_attempts=1を
# 明示的に使う)。

from __future__ import annotations

from typing import Any, Optional

import er003_key_words_production as prod
import er003_ja_to_en_translation as er003

ARTICLE_ID = "A01"
STRATEGY_ID = prod.STANDARD_STRATEGY_ID  # "L"
SOURCE_LEVEL = "B1"

B1_ARTICLE_PATH = "er003_output/b1_p1/A01/b1_article_raw.md"

# P2I production selectorと不変のまま再利用(再定義しない)
SELECTOR_MODEL = prod.SELECTOR_MODEL
SELECTOR_REASONING_EFFORT = prod.SELECTOR_REASONING_EFFORT
SELECTOR_DEVELOPER_MESSAGE = prod.SELECTOR_DEVELOPER_MESSAGE
SELECTOR_JSON_SCHEMA = prod.SELECTOR_JSON_SCHEMA
SelectorModelMismatchError = prod.SelectorModelMismatchError
parse_selector_json = prod.parse_selector_json

PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt"

# 本ステージは自動再選定・自動再実行を行わない(P2Iのdefault=2から
# 明示的に1へ変更する)。
MAX_SELECTOR_ATTEMPTS = 1


def load_b1_article() -> str:
    with open(B1_ARTICLE_PATH, encoding="utf-8") as f:
        return f.read()


def load_prompt_template(path: str = PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_user_message(approved_b1_article: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_prompt_template()
    return template.replace("{approved_b1_article}", approved_b1_article)


def make_selector_fn(user_message: str, client: Optional[Any] = None, model: str = None):
    """P2I production selectorの実体(model/reasoning_effort/
    developer_message/schema)をそのまま再利用する。modelを明示指定した
    場合はそちらを使う(ER-006-MODEL-ROUTING-CONTRACT-01、未指定時は
    prod.make_production_selector_fnの既定値)。"""
    kwargs = {"client": client}
    if model is not None:
        kwargs["model"] = model
    return prod.make_production_selector_fn(user_message, **kwargs)


# P2Iのruntime metadata付与・hard requirement validatorをそのまま再利用する。
attach_runtime_metadata = prod.attach_runtime_metadata
validate_selection = prod.validate_production_selection


def run_selection_gate(make_selector_factory, b1_article_text: str, sleep_fn=None):
    """P2Iのrun_production_selection_gateをそのまま再利用し、
    max_attempts=1(自動再実行なし)で呼び出す。"""
    return prod.run_production_selection_gate(
        ARTICLE_ID, make_selector_factory, b1_article_text,
        strategy_id=STRATEGY_ID, max_attempts=MAX_SELECTOR_ATTEMPTS, sleep_fn=sleep_fn,
    )


def build_selected_keywords_json(parsed_with_metadata: dict) -> dict:
    """section 7で指定された簡略schemaへ変換する(rawの全項目は
    別途keywords_runtime_metadata.jsonとして保存し、削らない)。"""
    items = sorted(parsed_with_metadata["items"], key=lambda it: it["rank"])
    return {
        "article_id": parsed_with_metadata["article_id"],
        "strategy_id": parsed_with_metadata["strategy_id"],
        "source_level": SOURCE_LEVEL,
        "items": [
            {
                "rank": item["rank"],
                "canonical_english": item["display_phrase"],
                "japanese_gloss": item["ja_gloss"],
                "source_evidence": item["source_sentence"],
            }
            for item in items
        ],
    }


def build_selected_keywords_reading_copy(selected_json: dict) -> str:
    """canonical_english / japanese_glossを、rank順に単純に列挙する
    (P2Dの5項目reading copy形式を新規設計せず、最小限の一覧に留める)。"""
    lines = ["## B1 Key Words / Phrases (A01)", ""]
    for item in selected_json["items"]:
        lines.append(f"{item['rank']}. {item['canonical_english']} — {item['japanese_gloss']}")
        lines.append(f"   source: {item['source_evidence']}")
    return "\n".join(lines) + "\n"
