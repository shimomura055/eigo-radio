# ============================================================
# er003_key_words_canonicalization.py
# ER-003-KP-01: Key Phrase境界正規化(Pedagogical Phrase Canonicalization)
# ============================================================
# 方式L(Listening Blocker Ranking)は「どの表現を選ぶか」を決める工程で
# あり、この工程は変更しない。本モジュールは、方式Lが選んだ後の
# display_phraseを、意味・文法的なまとまりを壊さずに、他の文脈でも
# 再利用可能な最小の自然な学習単位(key_phrase)へ正規化する、独立した
# 後段工程を実装する。
#
# 正規化の判断(冠詞・限定詞を削るかどうか)は、単純な正規表現や品詞
# ブラックリストでは行わない。LLM(方式Lの選定と同一モデル設定)による
# 個別文脈判断に委ね、本モジュールの決定的validatorは構造的な安全性
# (key_phraseが空でない、display_phrase内の連続部分文字列である、
# 1〜5語である、有限助動詞を含まない)のみを検査する。
#
# データモデル:
#   source_span      … 方式Lが本文中で特定した原文span(方式L選定結果の
#                       そのままの値、この工程では変更しない)
#   display_phrase   … 方式L選定時点でのcanonical_english(正規化前の
#                       候補、この工程の入力)
#   key_phrase       … この工程が正規化した、教材表示用の学習単位
#   used_form        … 実際に音声・Key Phrasesセクション等で使用する
#                       表現。現段階ではkey_phraseと同一値を採用する
#                       (将来TTS都合等で分岐する場合のための独立フィールド)
#
# 再利用するもの(再実装しない):
#   - er003_key_words_production.SELECTOR_MODEL/SELECTOR_REASONING_EFFORT
#     ("gpt-5.6-sol"/"high"、方式L選定と同一設定)
#   - er003_key_words_min_unit.DISPLAY_PHRASE_MIN_WORDS/MAX_WORDS/
#     _FINITE_AUX_WORDS相当の判定基準(値のみ再利用、関数は本モジュール
#     専用に定義しなおす。入力フィールド名がdisplay_phraseではなく
#     key_phraseであるため)

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_key_words_min_unit as p2g
import er003_key_words_production as prod
import er003_ja_to_en_translation as er003

CANONICALIZATION_VERSION = "ER-003-KP-01"

# 方式L選定と同一のモデル設定を再利用する(新しいモデル選定は行わない)。
SELECTOR_MODEL = prod.SELECTOR_MODEL
SELECTOR_REASONING_EFFORT = prod.SELECTOR_REASONING_EFFORT
DEVELOPER_MESSAGE = ("英語学習教材のKey Phrase境界を、意味を保ったまま"
                     "最小の自然な学習単位へ正規化してください。")

PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt"

QA_VERDICTS = ("PASS", "FAIL")
QA_FIELDS = (
    "qa_standalone_natural_unit",
    "qa_no_residual_context_word",
    "qa_meaning_or_usage_unchanged",
    "qa_reusable_other_context",
    "qa_traceable_contiguous_span",
    "qa_listening_blocker_value_preserved",
)

_ITEM_SCHEMA_PROPERTIES = {
    "rank": {"type": "integer"},
    "key_phrase": {"type": "string"},
    "changed_from_display_phrase": {"type": "boolean"},
    "reasoning": {"type": "string"},
    **{field: {"type": "string", "enum": list(QA_VERDICTS)} for field in QA_FIELDS},
}
_ITEM_REQUIRED_FIELDS = tuple(_ITEM_SCHEMA_PROPERTIES.keys())

CANONICALIZATION_JSON_SCHEMA = {
    "name": "key_words_canonicalization",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
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

# 最小単位の判定基準は方式L/P2Gの1〜5語制約をそのまま再利用する(値のみ、
# 関数はkey_phrase専用にこのモジュール内で定義する)。
KEY_PHRASE_MIN_WORDS = p2g.DISPLAY_PHRASE_MIN_WORDS
KEY_PHRASE_MAX_WORDS = p2g.DISPLAY_PHRASE_MAX_WORDS
_FINITE_AUX_WORDS = p2g._FINITE_AUX_WORDS
_WORD_TOKEN_RE = p2g._WORD_TOKEN_RE


def load_prompt_template(path: str = PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_user_message(items: list, article_text: str, template: Optional[str] = None) -> str:
    """itemsは方式L選定結果の各要素(rank/display_phrase/source_span/
    source_sentence/ja_gloss等)をそのまま渡す。この工程では選定内容
    (どの5件か)を一切変更しないため、items自体には手を加えない。"""
    template = template if template is not None else load_prompt_template()
    items_for_prompt = [
        {
            "rank": it["rank"],
            "display_phrase": it.get("display_phrase") or it.get("canonical_english"),
            "source_span": it.get("source_span", ""),
            "source_sentence": it.get("source_sentence", ""),
        }
        for it in items
    ]
    items_json = json.dumps(items_for_prompt, ensure_ascii=False, indent=2)
    return template.replace("{article_text}", article_text).replace("{items_json}", items_json)


class CanonicalizationModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。技術的失敗として扱う。"""


def make_canonicalization_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = SELECTOR_MODEL,
    reasoning_effort: str = SELECTOR_REASONING_EFFORT,
    developer_message: str = DEVELOPER_MESSAGE,
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
            text={"format": {"type": "json_schema", **CANONICALIZATION_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise CanonicalizationModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("canonicalization応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


def parse_canonicalization_json(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict) or "items" not in parsed:
        raise er003.QaSchemaError("'items'フィールドがありません")
    return parsed


def _normalize_for_match(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _word_count(text: str) -> int:
    return len([t for t in (text or "").strip().split() if t])


def _contains_finite_auxiliary(text: str) -> bool:
    tokens = [t.lower() for t in _WORD_TOKEN_RE.findall(text or "")]
    return any(t in _FINITE_AUX_WORDS for t in tokens)


def _is_contiguous_substring(needle: str, haystack: str) -> bool:
    """空白正規化・大小文字を無視した連続部分文字列判定
    (Rule 5: display_phrase内に存在しない別の辞書形を生成していないかの
    構造的チェック。冠詞を削るべきかどうかの意味判断はしない)。"""
    return _normalize_for_match(needle) in _normalize_for_match(haystack)


def validate_canonicalization_item(key_phrase: str, display_phrase: str) -> dict:
    """LLMが提案したkey_phraseの構造的安全性のみを検査する。冠詞削除の
    要否そのものは判定しない(それはLLMの役割)。ここで弾くのは、
    (a) 空文字、(b) display_phraseに存在しない文字列の捏造、
    (c) 1〜5語の範囲外、(d) 有限助動詞混入、の4種類のみ。"""
    reasons = []
    if not isinstance(key_phrase, str) or not key_phrase.strip():
        reasons.append("key_phraseが空、または文字列でない")
        return {"ok": False, "reasons": reasons}

    if not _is_contiguous_substring(key_phrase, display_phrase):
        reasons.append(
            f"key_phrase({key_phrase!r})がdisplay_phrase({display_phrase!r})内の連続部分文字列でない"
            "(Rule5: 本文に存在しない別の辞書形を勝手に生成しない)")

    word_count = _word_count(key_phrase)
    if word_count < KEY_PHRASE_MIN_WORDS or word_count > KEY_PHRASE_MAX_WORDS:
        reasons.append(f"key_phraseが{KEY_PHRASE_MIN_WORDS}〜{KEY_PHRASE_MAX_WORDS}語でない"
                       f"(実際: {word_count}語)")

    if _contains_finite_auxiliary(key_phrase):
        reasons.append("有限助動詞が含まれている")

    return {"ok": len(reasons) == 0, "reasons": reasons}


def validate_canonicalization_response(parsed: dict, original_items: list) -> dict:
    """itemsの件数・rank整合、各itemの構造的安全性を検査する。QA verdict
    フィールド(qa_*)がFAILであること自体は不合格の理由にしない
    (LLM自身の自己申告として記録・保存するのみで、人間確認の材料と
    する)。"""
    reasons = []
    item_reasons = []
    ok = True

    items = parsed.get("items")
    if not isinstance(items, list):
        return {"status": "CANONICALIZATION_INVALID", "reasons": ["'items'が配列でない"], "item_reasons": []}

    expected_ranks = sorted(it["rank"] for it in original_items)
    actual_ranks = sorted(it.get("rank") for it in items if isinstance(it, dict))
    if actual_ranks != expected_ranks:
        reasons.append(f"rankの集合が選定結果と一致しない(期待: {expected_ranks}, 実際: {actual_ranks})")
        ok = False

    display_phrase_by_rank = {
        it["rank"]: (it.get("display_phrase") or it.get("canonical_english")) for it in original_items
    }

    for i, item in enumerate(items):
        this_reasons = []
        if not isinstance(item, dict):
            item_reasons.append({"index": i, "reasons": ["項目がオブジェクトでない"]})
            ok = False
            continue
        for field in _ITEM_REQUIRED_FIELDS:
            if field not in item:
                this_reasons.append(f"必須フィールド'{field}'がない")
        if this_reasons:
            item_reasons.append({"index": i, "reasons": this_reasons})
            ok = False
            continue

        for field in QA_FIELDS:
            if item[field] not in QA_VERDICTS:
                this_reasons.append(f"{field}が不正(実際: {item[field]!r})")

        display_phrase = display_phrase_by_rank.get(item.get("rank"), "")
        structural = validate_canonicalization_item(item["key_phrase"], display_phrase)
        this_reasons.extend(structural["reasons"])

        if this_reasons:
            item_reasons.append({"index": i, "rank": item.get("rank"), "reasons": this_reasons})
            ok = False

    return {
        "status": "CANONICALIZATION_PASS" if ok else "CANONICALIZATION_INVALID",
        "reasons": reasons,
        "item_reasons": item_reasons,
    }


MAX_CANONICALIZATION_RETRY_ATTEMPTS = 2  # 初回 + 技術的失敗/構造不適合時の再試行1回のみ


def run_canonicalization_gate(
    make_canonicalization_factory: Callable[[], Callable],
    original_items: list,
    max_attempts: int = MAX_CANONICALIZATION_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、または構造的不適合(item数・rank不整合、Rule5違反等)で
    あれば、同一条件で最大1回だけ再試行する。内容品質(qa_*フィールドの
    PASS/FAIL自体)を理由とした再試行は行わない(そのまま記録する)。

    戻り値: (parsed, final_status, attempts_detail, model_id, response_id)
    """
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        fn = make_canonicalization_factory()
        try:
            raw_text, model_id, response_id = fn()
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
            parsed = parse_canonicalization_json(raw_text)
        except Exception as e:
            attempts_detail.append({
                "attempt": attempt, "status": "PARSE_FAILED", "error": str(e), "raw_text": raw_text,
                "model": model_id, "response_id": response_id,
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "PARSE_FAILED", attempts_detail, model_id, response_id

        validation = validate_canonicalization_response(parsed, original_items)
        attempts_detail.append({
            "attempt": attempt, "status": validation["status"], "reasons": validation["reasons"],
            "item_reasons": validation["item_reasons"], "raw_text": raw_text, "parsed": parsed,
            "model": model_id, "response_id": response_id,
        })
        if validation["status"] == "CANONICALIZATION_PASS":
            return parsed, "CANONICALIZATION_PASS", attempts_detail, model_id, response_id
        if attempt < max_attempts:
            continue
        return parsed, "CANONICALIZATION_INVALID", attempts_detail, model_id, response_id

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None


def merge_canonicalization_result(original_items: list, canonicalization_items: list) -> dict:
    """source_span/display_phrase(選定結果、無変更)と、key_phrase/
    used_form/QA/reasoning(この工程の出力)を1つのproduction artifactへ
    まとめる。used_formは現段階ではkey_phraseと同一値(将来TTS都合等で
    分岐する場合のための独立フィールドとして保持する)。"""
    canon_by_rank = {it["rank"]: it for it in canonicalization_items}
    merged_items = []
    for original in sorted(original_items, key=lambda it: it["rank"]):
        rank = original["rank"]
        canon = canon_by_rank[rank]
        display_phrase = original.get("display_phrase") or original.get("canonical_english")
        merged_items.append({
            "rank": rank,
            "source_span": original.get("source_span", ""),
            "source_sentence": original.get("source_sentence", ""),
            "display_phrase": display_phrase,
            "key_phrase": canon["key_phrase"],
            "used_form": canon["key_phrase"],
            "japanese_gloss": original.get("ja_gloss") or original.get("japanese_gloss"),
            "changed_from_display_phrase": canon["changed_from_display_phrase"],
            "qa": {field: canon[field] for field in QA_FIELDS},
            "reasoning": canon["reasoning"],
        })
    return {"items": merged_items}
