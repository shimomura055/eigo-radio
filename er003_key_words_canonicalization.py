# ============================================================
# er003_key_words_canonicalization.py
# ER-003-KP-01/KP-02: Key Phrase境界正規化(Pedagogical Phrase Canonicalization)
# ============================================================
# 方式L(Listening Blocker Ranking)は「どの表現を選ぶか」を決める工程で
# あり、この工程は変更しない。本モジュールは、方式Lが選んだ後の
# display_phraseを、意味・文法的なまとまりを壊さずに、学習教材として
# 提示するのに最も自然な学習単位(key_phrase)へ正規化する、独立した
# 後段工程を実装する。
#
# 2026-08-08(ER-003-KP-02)追記: 当初(KP-01)は「最小の再利用可能単位」を
# 目標にしていたが、"the urge to"→"urge to"のように、display_phraseを
# 削った結果、単独で聞くと意味が欠けた断片になる事例が見つかった。
# 目標を「最小」から「最小十分(Minimal Sufficient Unit)」へ修正した:
# 1〜5語の範囲で、意味理解に必要な語(source_span内に存在するものに
# 限る)は復元してよい。「短いほど良い」という最適化にはしない。
#
# 正規化の判断(冠詞・限定詞を削るか、逆にsource_spanから語を復元するか)
# は、単純な正規表現や品詞ブラックリストでは行わない。LLM(方式Lの選定と
# 同一モデル設定)による個別文脈判断に委ね、本モジュールの決定的
# validatorは構造的な安全性(key_phraseが空でない、source_span内の連続
# 部分文字列である、1〜5語である、有限助動詞を含まない)のみを検査する。
#
# データモデル:
#   source_span      … 方式Lが本文中で特定した原文span(方式L選定結果の
#                       そのままの値、この工程では変更しない)。
#                       canonicalizationはこのspanの範囲内でのみ語を
#                       復元できる(spanの外や本文にない語は生成しない)。
#   display_phrase   … 方式L選定時点でのcanonical_english(正規化前の
#                       候補、この工程の入力の出発点)
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
#     key_phraseであるため)。この1〜5語の範囲自体はKP-02でも変更しない
#     (根拠: er003_key_words_min_unit.pyのP2G「display_phraseを1〜5語の
#     最小学習単位へ強制し、完全文・節を拒否する」という決定。変更した
#     のは「範囲内でどこまで削るか」の目標であり、範囲そのものではない)

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_key_words_min_unit as p2g
import er003_key_words_production as prod
import er003_ja_to_en_translation as er003

CANONICALIZATION_VERSION = "ER-003-KP-02-R1"

# 方式L選定と同一のモデル設定を再利用する(新しいモデル選定は行わない)。
SELECTOR_MODEL = prod.SELECTOR_MODEL
SELECTOR_REASONING_EFFORT = prod.SELECTOR_REASONING_EFFORT
DEVELOPER_MESSAGE = ("英語学習教材のKey Phrase境界を、1〜5語の範囲で"
                     "意味理解に必要十分な自然な学習単位(最小十分)へ"
                     "正規化してください。短いほど良いわけではありません。")

PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt"

QA_VERDICTS = ("PASS", "FAIL")
QA_FIELDS = (
    "qa_standalone_natural_unit",
    "qa_no_residual_context_word",
    "qa_meaning_or_usage_unchanged",
    "qa_reusable_other_context",
    "qa_traceable_contiguous_span",
    "qa_listening_blocker_value_preserved",
    # 2026-08-08(ER-003-KP-02)追加: 過剰短縮を検出するための3項目。
    "qa_standalone_comprehensibility",
    "qa_not_over_minimized",
    "qa_context_sufficiency",
    # 2026-08-08(ER-003-KP-02-R1)追加: 意味保持を明示的に評価する2項目。
    # "the risk of losing jobs"→"losing jobs"のように、riskという意味の
    # 核(意味役割: risk/possibility/obligation/pressure/attempt/refusal等)
    # を丸ごと落とす短縮を、特定語のブラックリストではなく意味的判定で
    # 検出する。
    "qa_core_meaning_preserved",
    "qa_no_semantic_role_loss",
    # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01追加: No.18で"catch their
    # attention"/"a piece of your attention"のように、本文中の特定の人物
    # (your/their等)に依存した文脈依存形がKey Phraseとしてそのまま採用
    # された(単独では再利用しにくい)。display_phrase/key_phraseに
    # 本文固有の人称代名詞・所有格が残っており、それが辞書的な一般形
    # (one's/someone's等)へ正規化されていない、または特定の代名詞を
    # 保持する必要性が説明されていない場合はFAILとする。
    "qa_person_reference_generalized",
)

# canonicalizationがdisplay_phraseに対して行った変換の種類(監査用、
# 固定enum)。既存の方式L選定時点のnormalization_type(P2G、"lemma"/
# "verb_base"等)と同じ思想の、canonicalization工程専用の分類。
NORMALIZATION_REASONS = (
    "none",  # 無変更(display_phraseがそのままkey_phrase)
    "remove_contextual_determiner",  # the/a/an/this/that等の文脈限定詞を除去
    "restore_semantic_complement",  # 意味理解に必要な語をsource_spanから復元(例: watch)
    "inherit_selection_normalization",  # 無変更だが、方式L選定時点で既に
                                        # lemma化・時制正規化・phrasal verb整理等が
                                        # 行われている(例: take a player off)
    # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01追加: 本文固有の人称代名詞・
    # 所有格(my/your/his/her/their/our/you/they等)を、辞書的な一般形
    # (one's/someone's/oneself等)へ置換する場合に使う。「除去」
    # (remove_contextual_determiner)とは異なり「置換」であることに注意。
    "generalize_person_dependent_reference",
    "other",
)

_ITEM_SCHEMA_PROPERTIES = {
    "rank": {"type": "integer"},
    "key_phrase": {"type": "string"},
    "changed_from_display_phrase": {"type": "boolean"},
    "normalization_reason": {"type": "string", "enum": list(NORMALIZATION_REASONS)},
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
    (Rule 7: source_spanに存在しない別の辞書形を生成していないかの
    構造的チェック。冠詞を削る・語を復元するかどうかの意味判断はしない)。"""
    return _normalize_for_match(needle) in _normalize_for_match(haystack)


# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: 人称代名詞・所有格の一般化
# ============================================================
# No.18の"catch their attention"/"a piece of your attention"は、本文の
# 文脈(誰の注意か)に依存した人称形のまま採用されたKey Phraseだった。
# 単独の学習教材として提示するKey Phraseは、原則として辞書的な一般形
# (例: catch/grab someone's attention、in one's opinion)にすべきである。
# ただし、記事のみのハードコード(「your」「their」専用の分岐)ではなく、
# 閉じた語彙集合(一般的な人称代名詞・所有格とその辞書的一般形の対応表)
# による構造的な置換のみを許可する。1対1のトークン置換のみを対象とし、
# 語の削除は別カテゴリ(remove_contextual_determiner)の対象のまま
# 変更しない。
_PERSON_DEPENDENT_TO_GENERIC = {
    "my": {"one's"},
    "your": {"one's", "someone's", "somebody's"},
    "his": {"one's", "someone's", "somebody's"},
    "her": {"one's", "someone's", "somebody's"},
    "its": {"one's"},
    "their": {"one's", "someone's", "somebody's"},
    "our": {"one's"},
    "you": {"someone", "somebody", "one"},
    "they": {"someone", "somebody", "one"},
    "he": {"someone", "somebody", "one"},
    "she": {"someone", "somebody", "one"},
    "yourself": {"oneself"},
    "himself": {"oneself"},
    "herself": {"oneself"},
    "themselves": {"oneself"},
    "yours": {"one's"},
    "theirs": {"one's"},
}


def _is_valid_person_generalization(key_phrase: str, display_phrase: str) -> bool:
    """display_phraseとkey_phraseの語数が同じで、異なるトークンが全て
    _PERSON_DEPENDENT_TO_GENERICで許可された1対1置換である場合のみTrueを
    返す(該当なしはFalse。空変更[全トークン一致]もFalse、それは
    'none'の対象であり本カテゴリの対象ではない)。"""
    key_tokens = [t.lower() for t in p2g._WORD_TOKEN_RE.findall(key_phrase or "")]
    display_tokens = [t.lower() for t in p2g._WORD_TOKEN_RE.findall(display_phrase or "")]
    if len(key_tokens) != len(display_tokens) or not key_tokens:
        return False
    changed_any = False
    for k_tok, d_tok in zip(key_tokens, display_tokens):
        if k_tok == d_tok:
            continue
        allowed = _PERSON_DEPENDENT_TO_GENERIC.get(d_tok)
        if not allowed or k_tok not in allowed:
            return False
        changed_any = True
    return changed_any


def validate_canonicalization_item(key_phrase: str, display_phrase: str, source_span: str,
                                    normalization_reason: Optional[str] = None) -> dict:
    """LLMが提案したkey_phraseの構造的安全性のみを検査する。冠詞削除・
    語の復元の要否そのものは判定しない(それはLLMの役割)。ここで弾くのは、
    (a) 空文字、(b) source_spanにもdisplay_phraseにも存在しない文字列の
    捏造、(c) 1〜5語の範囲外、(d) 有限助動詞混入、の4種類のみ。

    2026-08-08(ER-003-KP-02): key_phraseがdisplay_phraseと完全一致する
    場合(無変更)は常に安全とみなす。display_phrase自体は方式Lの選定
    時点で既に確立された値であり(例: A01の"take a player off"は元の
    source_span"took off players"の語順を変えた正規化形で、文字列としては
    一致しない)、無変更であればcanonicalization工程が新たに何かを捏造した
    ことにはならない。変更する場合は、source_span(本文中の元のspan、
    display_phraseより広い範囲から語を復元できる)内の連続部分文字列で
    あることを要求する(Rule7)。"""
    reasons = []
    if not isinstance(key_phrase, str) or not key_phrase.strip():
        reasons.append("key_phraseが空、または文字列でない")
        return {"ok": False, "reasons": reasons}

    unchanged = _normalize_for_match(key_phrase) == _normalize_for_match(display_phrase)
    if not unchanged and not _is_contiguous_substring(key_phrase, source_span):
        is_valid_person_generalization = (
            normalization_reason == "generalize_person_dependent_reference"
            and _is_valid_person_generalization(key_phrase, display_phrase)
        )
        if not is_valid_person_generalization:
            reasons.append(
                f"key_phrase({key_phrase!r})がdisplay_phraseと一致せず、"
                f"source_span({source_span!r})内の連続部分文字列でもない"
                "(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)"
                "(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)")

    word_count = _word_count(key_phrase)
    if word_count < KEY_PHRASE_MIN_WORDS or word_count > KEY_PHRASE_MAX_WORDS:
        reasons.append(f"key_phraseが{KEY_PHRASE_MIN_WORDS}〜{KEY_PHRASE_MAX_WORDS}語でない"
                       f"(実際: {word_count}語)")

    if _contains_finite_auxiliary(key_phrase):
        reasons.append("有限助動詞が含まれている")

    return {"ok": len(reasons) == 0, "reasons": reasons}


def validate_canonicalization_response(parsed: dict, original_items: list) -> dict:
    """itemsの件数・rank整合、各itemの構造的安全性を検査する。

    ステータスは3段階(2026-08-08、ER-003-KP-01ユーザー受入時の修正で導入):
      - CANONICALIZATION_PASS: 構造validator合格 かつ QA6項目すべてPASS
      - CANONICALIZATION_REVIEW_REQUIRED: 構造validator合格 かつ QAに
        1件以上FAILがある(自動採用しない。人間確認後に採用可能とする)
      - CANONICALIZATION_INVALID: 構造validator不合格

    QA verdictフィールド(qa_*)のFAILは、それ自体を構造不合格の理由には
    しない(REVIEW_REQUIREDへ倒す)。"""
    reasons = []
    item_reasons = []
    ok = True
    has_qa_fail = False
    items_requiring_review = []

    items = parsed.get("items")
    if not isinstance(items, list):
        return {"status": "CANONICALIZATION_INVALID", "reasons": ["'items'が配列でない"], "item_reasons": [],
                "items_requiring_review": []}

    expected_ranks = sorted(it["rank"] for it in original_items)
    actual_ranks = sorted(it.get("rank") for it in items if isinstance(it, dict))
    if actual_ranks != expected_ranks:
        reasons.append(f"rankの集合が選定結果と一致しない(期待: {expected_ranks}, 実際: {actual_ranks})")
        ok = False

    display_phrase_by_rank = {
        it["rank"]: (it.get("display_phrase") or it.get("canonical_english")) for it in original_items
    }
    source_span_by_rank = {it["rank"]: it.get("source_span", "") for it in original_items}

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

        if item["normalization_reason"] not in NORMALIZATION_REASONS:
            this_reasons.append(f"normalization_reasonが不正(実際: {item['normalization_reason']!r})")

        display_phrase = display_phrase_by_rank.get(item.get("rank"), "")
        source_span = source_span_by_rank.get(item.get("rank"), "")
        structural = validate_canonicalization_item(
            item["key_phrase"], display_phrase, source_span,
            normalization_reason=item.get("normalization_reason"))
        this_reasons.extend(structural["reasons"])

        if this_reasons:
            item_reasons.append({"index": i, "rank": item.get("rank"), "reasons": this_reasons})
            ok = False
        elif any(item[field] == "FAIL" for field in QA_FIELDS):
            has_qa_fail = True
            items_requiring_review.append(item.get("rank"))

    if not ok:
        status = "CANONICALIZATION_INVALID"
    elif has_qa_fail:
        status = "CANONICALIZATION_REVIEW_REQUIRED"
    else:
        status = "CANONICALIZATION_PASS"

    return {
        "status": status,
        "reasons": reasons,
        "item_reasons": item_reasons,
        "items_requiring_review": items_requiring_review,
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
            "item_reasons": validation["item_reasons"],
            "items_requiring_review": validation["items_requiring_review"],
            "raw_text": raw_text, "parsed": parsed, "model": model_id, "response_id": response_id,
        })
        # PASS/REVIEW_REQUIREDはいずれも構造validator合格であり、自動
        # 再試行はしない(REVIEW_REQUIREDは人間確認後に採用する運用のため、
        # 再試行しても解決しない)。再試行するのはCANONICALIZATION_INVALID
        # (構造不適合)のときだけ。
        if validation["status"] in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            return parsed, validation["status"], attempts_detail, model_id, response_id
        if attempt < max_attempts:
            continue
        return parsed, "CANONICALIZATION_INVALID", attempts_detail, model_id, response_id

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None


def merge_canonicalization_result(original_items: list, canonicalization_items: list) -> dict:
    """source_span/display_phrase(選定結果、無変更)と、key_phrase/
    used_form/QA/reasoning(この工程の出力)を1つのproduction artifactへ
    まとめる。used_formは現段階ではkey_phraseと同一値(将来TTS都合等で
    分岐する場合のための独立フィールドとして保持する)。

    項目ごとのqa_overall_status(PASS/REVIEW_REQUIRED)、全体の
    overall_status(全項目PASSならPASS、1件でもFAILがあればREVIEW_
    REQUIRED)を付与する。REVIEW_REQUIRED項目は自動採用せず、人間確認後に
    採用する運用とする(構造的には既にvalidを通過済み)。"""
    canon_by_rank = {it["rank"]: it for it in canonicalization_items}
    merged_items = []
    any_review_required = False
    for original in sorted(original_items, key=lambda it: it["rank"]):
        rank = original["rank"]
        canon = canon_by_rank[rank]
        display_phrase = original.get("display_phrase") or original.get("canonical_english")
        qa = {field: canon[field] for field in QA_FIELDS}
        item_review_required = any(v == "FAIL" for v in qa.values())
        any_review_required = any_review_required or item_review_required
        merged_items.append({
            "rank": rank,
            "source_span": original.get("source_span", ""),
            "source_sentence": original.get("source_sentence", ""),
            "display_phrase": display_phrase,
            "key_phrase": canon["key_phrase"],
            "used_form": canon["key_phrase"],
            "japanese_gloss": original.get("ja_gloss") or original.get("japanese_gloss"),
            "changed_from_display_phrase": canon["changed_from_display_phrase"],
            "normalization_reason": canon["normalization_reason"],
            "qa": qa,
            "qa_overall_status": "REVIEW_REQUIRED" if item_review_required else "PASS",
            "reasoning": canon["reasoning"],
        })
    return {
        "items": merged_items,
        "overall_status": "REVIEW_REQUIRED" if any_review_required else "PASS",
    }
