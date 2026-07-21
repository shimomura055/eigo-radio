# ============================================================
# er003_key_words_min_unit.py
# ER-003-P2G: Key Words最小単位化＋3記事×3方式ブラインド再比較
# ============================================================
# ER-003-P2E/P2Fでは、difficult箇所の発見とKey Wordとして表示する
# 学習単位の抽出が分離されておらず、ほぼ一文に近い長い抜粋が
# display_phraseとして返ることがあった。本モジュールでは、
# display_phraseを1〜5語の最小学習単位(単語・句・コロケーション)へ
# 強制し、完全文・節・時制付き動詞句を決定的validatorで拒否する。
#
# また、P2Fで発生した「モデルが自己申告するarticle_idの誤記だけで
# job全体が失敗する」問題を防ぐため、article_id/strategy_id/
# research_item_count/production_item_count_unchangedはモデルの
# Structured Output schemaから完全に除外し、実行時(runtime)に
# Pythonが決定的に付与する。モデルの自己申告をこれらの識別子として
# 一切使用しない。
#
# 対象はA01・A02・ADD03の3記事。A01もER-003-P2Eの旧成果物を再利用
# せず、新しい最小単位仕様で独立に再実行する。共通入力は各記事の
# 承認済み概要(summary_en_approved.md)と確定済みB2本文のみ。日本語
# 原稿・Natural English Source・P1/P1B・P2D/P2E/P2Fの選定結果・過去の
# 比較QA・ユーザーが挙げた具体的候補語・ユーザーによる方式順位・
# 他記事の本文/概要・Web検索結果・外部辞書・TTS情報はselectorへ
# 一切渡さない。一方式の結果を、他方式または他記事のselectorへ渡さ
# ない。
#
# ユーザー評価前に、SetとL/P/Uのmapping・QAによる暫定best・方式別の
# 強み弱み・strategy analysisは一切開示しない(完了報告にも含めない)。
#
# 再利用するもの(再実装しない):
#   - er003_key_words_strategy_compare.SELECTOR_MODEL/
#     SELECTOR_REASONING_EFFORT(P2E/P2Fと不変)
#   - er003_b2_key_words.B2_INPUT_PATHS/APPROVED_SUMMARY_PATHS/
#     load_approved_b2_article/load_approved_summary(確定済み入力は
#     P2D/P2E/P2Fと完全に同一)
#   - er003_ja_to_en_translation.run_json_response_gate(Extraction
#     Form QA用)
#   - er003_ja_to_en_translation.sha256_text

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_b2_key_words as p2d
import er003_key_words_strategy_compare as p2e
import er003_ja_to_en_translation as er003

EXPERIMENT_VERSION = "ER-003-P2G"
ARTICLE_IDS = ("A01", "A02", "ADD03")
STRATEGY_IDS = p2e.STRATEGY_IDS  # ("L", "P", "U")

RESEARCH_ITEM_COUNT = 10
PRODUCTION_ITEM_COUNT_UNCHANGED = 5
RESEARCH_BANDS = ("TOP_5", "RANK_6_TO_10")

DISPLAY_PHRASE_MIN_WORDS = 1
DISPLAY_PHRASE_MAX_WORDS = 5

# P2D/P2Eから不変のまま再利用(再定義しない)
SELECTOR_MODEL = p2e.SELECTOR_MODEL  # "gpt-5.6-sol"
SELECTOR_REASONING_EFFORT = p2e.SELECTOR_REASONING_EFFORT  # "high"
SELECTOR_DEVELOPER_MESSAGE = "英語ポッドキャストの初回リスニング理解を助ける、短いKey Wordsを選定してください。"

STRATEGY_PROMPT_TEMPLATE_PATHS = {
    "L": "er003_v1_translator_briefs/b2_key_words_min_unit_l_prompt_template.txt",
    "P": "er003_v1_translator_briefs/b2_key_words_min_unit_p_prompt_template.txt",
    "U": "er003_v1_translator_briefs/b2_key_words_min_unit_u_prompt_template.txt",
}
FORM_QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_key_words_min_unit_form_qa_prompt_template.txt"

# 確定済み入力はP2D/P2E/P2Fと完全に同一のものを使う(独立に定義しない)。
B2_INPUT_PATHS = p2d.B2_INPUT_PATHS
APPROVED_SUMMARY_PATHS = p2d.APPROVED_SUMMARY_PATHS
load_approved_b2_article = p2d.load_approved_b2_article
load_approved_summary = p2d.load_approved_summary

run_json_response_gate = er003.run_json_response_gate

# 記事ごとに異なる固定seedを使う(P2E/P2Fのseedとも異なる)。mappingは
# 保存するが、ユーザー評価完了までレビュー文書・完了報告からは開示
# しない。
BLIND_MAPPING_SEEDS = {
    "A01": 20260723,
    "A02": 20260724,
    "ADD03": 20260725,
}
_BLIND_SET_LABELS = ("Set A", "Set B", "Set C")


def build_blind_mapping(article_id: str) -> dict:
    import random
    seed = BLIND_MAPPING_SEEDS[article_id]
    rng = random.Random(seed)
    shuffled = list(STRATEGY_IDS)
    rng.shuffle(shuffled)
    return {label: sid for label, sid in zip(_BLIND_SET_LABELS, shuffled)}


# ============================================================
# ブロック1: 共通schema(modelはitemsのみ出力。article_id/strategy_id/
# research_item_count/production_item_count_unchangedはmodel schemaへ
# 一切含めず、runtimeが決定的に付与する)
# ============================================================
PHRASE_TYPES = ("word", "noun_phrase", "phrasal_verb", "collocation", "idiom", "technical_term",
                "prepositional_phrase")
NORMALIZATION_TYPES = ("none", "lemma", "verb_base", "passive_base", "collocation_core", "idiom_core",
                       "noun_canonical", "other")
TRI_LEVELS = ("LOW", "MEDIUM", "HIGH")
PORTFOLIO_CATEGORIES = ("general_unknown_word", "domain_expression", "compact_listening_pattern",
                        "figurative_emotional", "causal_contrast", "other")

_ITEM_SCHEMA_PROPERTIES = {
    "rank": {"type": "integer"},
    "display_phrase": {"type": "string"},
    "source_span": {"type": "string"},
    "source_sentence": {"type": "string"},
    "ja_gloss": {"type": "string"},
    "phrase_type": {"type": "string", "enum": list(PHRASE_TYPES)},
    "normalization_type": {"type": "string", "enum": list(NORMALIZATION_TYPES)},
    "normalization_note": {"type": "string"},
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
}
_ITEM_REQUIRED_FIELDS = tuple(_ITEM_SCHEMA_PROPERTIES.keys())

SELECTOR_JSON_SCHEMA = {
    "name": "b2_key_words_min_unit_selection",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "minItems": RESEARCH_ITEM_COUNT,
                "maxItems": RESEARCH_ITEM_COUNT,
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


def load_strategy_prompt_template(strategy_id: str) -> str:
    return er003.restore.load_text_file(STRATEGY_PROMPT_TEMPLATE_PATHS[strategy_id])


def build_strategy_user_message(strategy_id: str, approved_summary: str, approved_b2_article: str,
                                 template: Optional[str] = None) -> str:
    template = template if template is not None else load_strategy_prompt_template(strategy_id)
    return template.replace("{approved_summary}", approved_summary).replace(
        "{approved_b2_article}", approved_b2_article)


class SelectorModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。技術的失敗として扱う。"""


def make_strategy_selector_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = SELECTOR_MODEL,
    reasoning_effort: str = SELECTOR_REASONING_EFFORT,
    developer_message: str = SELECTOR_DEVELOPER_MESSAGE,
):
    """strategy_idを引数に取らない(schemaがstrategy固有ではなく共通の
    ためschema名も固定。strategy識別はruntimeメタデータとして呼び出し
    元が保持する)。"""
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


def attach_runtime_metadata(parsed: dict, article_id: str, strategy_id: str) -> dict:
    """article_id/strategy_id/research_item_count/production_item_count_
    unchangedはmodelの自己申告に一切依存せず、runtimeが決定的に付与
    する。rank 1〜5をTOP_5、6〜10をRANK_6_TO_10として付与する
    (research_bandもmodel schemaには含まれない)。"""
    items_with_band = []
    for item in parsed["items"]:
        band = "TOP_5" if isinstance(item.get("rank"), int) and 1 <= item["rank"] <= 5 else "RANK_6_TO_10"
        items_with_band.append({**item, "research_band": band})
    return {
        "article_id": article_id,
        "strategy_id": strategy_id,
        "research_item_count": RESEARCH_ITEM_COUNT,
        "production_item_count_unchanged": PRODUCTION_ITEM_COUNT_UNCHANGED,
        "items": items_with_band,
    }


# ============================================================
# ブロック2: 決定的validator(最小単位・完全文/節排除・本文対応)
# ============================================================
_DIGITS_ONLY_RE = re.compile(r"^\d+([.,]\d+)?%?$")
_DATE_ONLY_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+\d{1,2}(,?\s*\d{2,4})?$"
    r"|^\d{1,2}/\d{1,2}(/\d{2,4})?$",
    re.IGNORECASE,
)
_JAPANESE_CHAR_RE = re.compile(r"[ぁ-んァ-ヶ一-龯]")
_TERMINAL_PUNCT_RE = re.compile(r"[.?!;]")
_ELLIPSIS_RE = re.compile(r"\.\.\.|…")
_NEWLINE_RE = re.compile(r"[\r\n]")
_QUOTE_CHARS = "\"'‘’“”"

# 仕様(section 12)に明記された有限助動詞のみ。bare "be"は
# passive_base見出し形として許可するため、このリストには含めない。
_FINITE_AUX_WORDS = {"is", "are", "was", "were", "has", "have", "had",
                     "will", "would", "can", "could", "should", "may", "might", "must"}
_PRONOUN_DEMONSTRATIVE_WORDS = {"i", "you", "he", "she", "it", "we", "they", "this", "that", "these", "those"}

_WORD_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _normalize_for_match(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = normalized.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _display_phrase_word_count(text: str) -> int:
    """空白区切りで数える。ハイフン語・contractionは内部に空白を含まない
    ため自動的に1語として数えられる。"""
    return len([t for t in text.strip().split() if t])


def _has_quote_wrapper(text: str) -> bool:
    t = text.strip()
    return len(t) >= 2 and t[0] in _QUOTE_CHARS and t[-1] in _QUOTE_CHARS


def _contains_finite_auxiliary(text: str) -> bool:
    tokens = [t.lower() for t in _WORD_TOKEN_RE.findall(text)]
    return any(t in _FINITE_AUX_WORDS for t in tokens)


def _starts_with_pronoun_or_demonstrative(text: str) -> bool:
    tokens = [t.lower() for t in _WORD_TOKEN_RE.findall(text)]
    return bool(tokens) and tokens[0] in _PRONOUN_DEMONSTRATIVE_WORDS


def _is_digits_only(text: str) -> bool:
    return bool(_DIGITS_ONLY_RE.match(text.strip()))


def _is_date_only(text: str) -> bool:
    return bool(_DATE_ONLY_RE.match(text.strip()))


def _has_japanese_characters(text: str) -> bool:
    return bool(_JAPANESE_CHAR_RE.search(text or ""))


def validate_display_phrase_form(display_phrase: str) -> dict:
    """display_phraseが最小学習単位のhard requirementを満たすかを判定
    する。reasonsは不合格に直結する項目、warningsは記録のみで不合格に
    しない項目(personal pronoun/demonstrative始まり等)。"""
    reasons = []
    warnings = []
    text = display_phrase or ""

    if _NEWLINE_RE.search(text):
        reasons.append("改行が含まれている")
    if _TERMINAL_PUNCT_RE.search(text):
        reasons.append("終端記号(. ? ! ;)が含まれている")
    if _ELLIPSIS_RE.search(text):
        reasons.append("省略記号(...)が含まれている")
    if _has_quote_wrapper(text):
        reasons.append("引用符で囲まれている(quotation wrapper)")

    word_count = _display_phrase_word_count(text)
    if word_count < DISPLAY_PHRASE_MIN_WORDS or word_count > DISPLAY_PHRASE_MAX_WORDS:
        reasons.append(f"display_phraseが{DISPLAY_PHRASE_MIN_WORDS}〜{DISPLAY_PHRASE_MAX_WORDS}語でない"
                       f"(実際: {word_count}語)")

    if _contains_finite_auxiliary(text):
        reasons.append("有限助動詞(is/are/was/were/has/have/had/will/would/can/could/should/may/might/must)"
                       "が含まれている")

    if _starts_with_pronoun_or_demonstrative(text):
        warnings.append("personal pronoun/demonstrativeで始まっている(節らしさの警告)")

    return {"ok": len(reasons) == 0, "reasons": reasons, "warnings": warnings, "word_count": word_count}


_REQUIRED_ITEM_FIELDS = _ITEM_REQUIRED_FIELDS
_STRING_FIELDS = ("display_phrase", "source_span", "source_sentence", "ja_gloss",
                  "normalization_note", "selection_reason", "listening_difficulty_reason")


def validate_min_unit_selection(parsed_with_metadata: dict, b2_article_text: str,
                                 expected_item_count: int = RESEARCH_ITEM_COUNT) -> dict:
    """runtimeメタデータ付与後のselectionを決定的に検証する。比較・
    監査のための判定のみを行い、項目の追加・修正・入れ替えは一切
    行わない。article_id/strategy_idはruntime付与値を前提とし、model
    の自己申告には一切依存しない(P2Fのarticle_id誤記問題を構造的に
    回避する)。

    expected_item_countはP2Gの研究版(10件)がデフォルトだが、この
    hard requirement判定ロジック自体はitem数に依存しないため、ER-003-
    P2Iの本番版(5件)validatorからもそのまま再利用できるよう引数化
    している。"""
    reasons = []
    ok = True
    item_reasons: list = []

    items = parsed_with_metadata.get("items")
    if not isinstance(items, list):
        return {"status": "KEY_WORDS_STRUCTURE_INVALID", "reasons": ["'items'が配列でない"], "item_reasons": []}

    if len(items) != expected_item_count:
        reasons.append(f"itemsが{expected_item_count}件でない(実際: {len(items)}件)")
        ok = False

    plain_article = er003.article_gen.strip_markdown_symbols(b2_article_text)
    normalized_raw_article = _normalize_for_match(b2_article_text)
    normalized_plain_article = _normalize_for_match(plain_article)

    ranks = []
    display_phrases = []

    for i, item in enumerate(items):
        this_item_reasons = []
        this_item_warnings = []
        if not isinstance(item, dict):
            item_reasons.append({"index": i, "reasons": ["項目がオブジェクトでない"], "warnings": []})
            ok = False
            continue

        for field in _REQUIRED_ITEM_FIELDS:
            if field not in item:
                this_item_reasons.append(f"必須フィールド'{field}'がない")
        if this_item_reasons:
            item_reasons.append({"index": i, "reasons": this_item_reasons, "warnings": []})
            ok = False
            continue

        for field in _STRING_FIELDS:
            if not isinstance(item[field], str) or not item[field].strip():
                this_item_reasons.append(f"'{field}'が空、または文字列でない")

        if item.get("phrase_type") not in PHRASE_TYPES:
            this_item_reasons.append(f"phrase_typeが不正(実際: {item.get('phrase_type')!r})")
        if item.get("normalization_type") not in NORMALIZATION_TYPES:
            this_item_reasons.append(f"normalization_typeが不正(実際: {item.get('normalization_type')!r})")
        for enum_field in ("inference_transparency", "topic_exposure_dependency", "comprehension_impact",
                          "figurative_or_emotional_value", "spoiler_risk"):
            if item.get(enum_field) not in TRI_LEVELS:
                this_item_reasons.append(f"{enum_field}が不正(実際: {item.get(enum_field)!r})")
        if item.get("portfolio_category") not in PORTFOLIO_CATEGORIES:
            this_item_reasons.append(f"portfolio_categoryが不正(実際: {item.get('portfolio_category')!r})")
        if not isinstance(item.get("portfolio_substitution"), bool):
            this_item_reasons.append("portfolio_substitutionがbooleanでない")

        rank = item.get("rank")
        ranks.append(rank)

        display_phrase = item.get("display_phrase", "")
        source_span = item.get("source_span", "")
        source_sentence = item.get("source_sentence", "")
        ja_gloss = item.get("ja_gloss", "")

        if isinstance(display_phrase, str):
            display_phrases.append(_normalize_for_match(display_phrase))
            form = validate_display_phrase_form(display_phrase)
            this_item_reasons.extend(form["reasons"])
            this_item_warnings.extend(form["warnings"])

            if _is_digits_only(display_phrase) or _is_digits_only(source_span):
                this_item_reasons.append("数字だけの項目")
            if _is_date_only(display_phrase) or _is_date_only(source_span):
                this_item_reasons.append("日付だけの項目")

        if isinstance(source_sentence, str) and source_sentence.strip():
            normalized_sentence = _normalize_for_match(source_sentence)
            source_match = (normalized_sentence in normalized_raw_article
                            or normalized_sentence in normalized_plain_article)
            if not source_match:
                this_item_reasons.append("source_sentenceがB2本文に存在しない")
            else:
                if isinstance(source_span, str) and source_span.strip():
                    if _normalize_for_match(source_span) not in normalized_sentence:
                        this_item_reasons.append("source_spanがsource_sentence内に存在しない")

        if isinstance(ja_gloss, str) and ja_gloss.strip():
            if not _has_japanese_characters(ja_gloss):
                this_item_reasons.append("日本語グロスに日本語文字が含まれない(英文の可能性)")

        if this_item_reasons or this_item_warnings:
            item_reasons.append({"index": i, "reasons": this_item_reasons, "warnings": this_item_warnings})
        if this_item_reasons:
            ok = False

    if ranks and (sorted(r for r in ranks if isinstance(r, int)) != list(range(1, expected_item_count + 1))
                 or len(ranks) != len(set(ranks))):
        reasons.append(f"rankが1〜{expected_item_count}の重複・欠番なしの並びでない(実際: {ranks})")
        ok = False

    if len(display_phrases) != len(set(display_phrases)):
        reasons.append("display_phraseに重複がある")
        ok = False

    if item_reasons and any(r["reasons"] for r in item_reasons):
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
    if "items" not in parsed:
        raise er003.QaSchemaError("'items'フィールドがありません")
    return parsed


MAX_MIN_UNIT_RETRY_ATTEMPTS = 2  # 初回 + (技術的失敗 または hard requirement不適合)時の再試行1回のみ


def run_min_unit_selection_gate(
    article_id: str,
    strategy_id: str,
    make_selector_factory: Callable[[], Callable],
    b2_article_text: str,
    max_attempts: int = MAX_MIN_UNIT_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、またはexactly 10・rank整合・1〜5語・完全文/節排除・
    有限助動詞排除・本文対応の不適合であれば、job毎に同一条件で最大1回
    だけ再試行する。article_id/strategy_idはmodelの自己申告に一切
    依存せず、この関数の引数(runtime指定値)をそのまま結果へ付与する。
    内容品質を理由とした再試行・再生成は行わない。

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
        validation = validate_min_unit_selection(parsed_with_metadata, b2_article_text)
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


# ============================================================
# ブロック3: 読み上げ原稿(RESEARCH_ONLY_10_ITEMS、TOP_5のみ生成)
# ============================================================
def build_research_reading_copy(items: list) -> str:
    """検証済みのselection JSONから、製品仕様と同形式(Number One〜Five)
    のreading copyを決定的に構成する。rank 1〜5(TOP_5)の項目だけを
    対象とし、P2Dのbuild_key_words_reading_copyをrank->orderアダプタ
    経由で再利用する。metadataとしてRESEARCH_ONLY_10_ITEMS/
    PRODUCTION_SPEC_REMAINS_5を別途保存する(本関数はreading copy本文
    のみを返す)。"""
    top5_items = sorted([it for it in items if it["research_band"] == "TOP_5"], key=lambda it: it["rank"])
    adapted_items = [{**item, "order": item["rank"]} for item in top5_items]
    return p2d.build_key_words_reading_copy(adapted_items)


READING_COPY_METADATA = {
    "research_only": "RESEARCH_ONLY_10_ITEMS",
    "production_spec": "PRODUCTION_SPEC_REMAINS_5",
}


# ============================================================
# ブロック4: 決定的指標
# ============================================================
def compute_min_unit_metrics(items: list) -> dict:
    sorted_items = sorted(items, key=lambda it: it["rank"])
    top5 = [it for it in sorted_items if it["research_band"] == "TOP_5"]
    rank_6_10 = [it for it in sorted_items if it["research_band"] == "RANK_6_TO_10"]
    phrase_type_counts = {t: 0 for t in PHRASE_TYPES}
    category_counts = {c: 0 for c in PORTFOLIO_CATEGORIES}
    word_count_distribution = {n: 0 for n in range(DISPLAY_PHRASE_MIN_WORDS, DISPLAY_PHRASE_MAX_WORDS + 1)}
    substitution_count = 0
    for item in sorted_items:
        phrase_type_counts[item["phrase_type"]] = phrase_type_counts.get(item["phrase_type"], 0) + 1
        category_counts[item["portfolio_category"]] = category_counts.get(item["portfolio_category"], 0) + 1
        wc = _display_phrase_word_count(item["display_phrase"])
        word_count_distribution[wc] = word_count_distribution.get(wc, 0) + 1
        if item.get("portfolio_substitution"):
            substitution_count += 1
    return {
        "item_count": len(sorted_items),
        "top5_count": len(top5),
        "rank_6_10_count": len(rank_6_10),
        "phrase_type_counts": phrase_type_counts,
        "portfolio_category_counts": category_counts,
        "word_count_distribution": word_count_distribution,
        "portfolio_substitution_count": substitution_count,
    }


# ============================================================
# ブロック5: Extraction Form QA(記事ごとに3方式・30項目まとめて実行、
# selectorとは独立の新規API実行。方式比較・best fitは一切行わない)
# ============================================================
FORM_QA_VERDICTS = ("PASS", "FAIL")

FORM_QA_ITEM_SCHEMA_PROPERTIES = {
    "rank": {"type": "integer"},
    "form_verdict": {"type": "string", "enum": list(FORM_QA_VERDICTS)},
    "minimal_unit": {"type": "string", "enum": list(FORM_QA_VERDICTS)},
    "not_a_clause": {"type": "string", "enum": list(FORM_QA_VERDICTS)},
    "canonical_form": {"type": "string", "enum": list(FORM_QA_VERDICTS)},
    "source_fidelity": {"type": "string", "enum": list(FORM_QA_VERDICTS)},
    "gloss_match": {"type": "string", "enum": list(FORM_QA_VERDICTS)},
    "notes": {"type": "string"},
}

FORM_QA_JSON_SCHEMA = {
    "name": "b2_key_words_min_unit_form_qa",
    "schema": {
        "type": "object",
        "properties": {
            "sets": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "runtime_strategy_id": {"type": "string", "enum": list(STRATEGY_IDS)},
                        "items": {
                            "type": "array",
                            "minItems": RESEARCH_ITEM_COUNT,
                            "maxItems": RESEARCH_ITEM_COUNT,
                            "items": {
                                "type": "object",
                                "properties": FORM_QA_ITEM_SCHEMA_PROPERTIES,
                                "required": list(FORM_QA_ITEM_SCHEMA_PROPERTIES.keys()),
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["runtime_strategy_id", "items"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["sets"],
        "additionalProperties": False,
    },
    "strict": True,
}


def parse_and_validate_form_qa_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    if "sets" not in parsed or not isinstance(parsed["sets"], list):
        raise er003.QaSchemaError("'sets'フィールドがありません")
    if len(parsed["sets"]) != 3:
        raise er003.QaSchemaError(f"setsが3件でありません(実際: {len(parsed['sets'])}件)")
    seen_strategy_ids = set()
    for set_eval in parsed["sets"]:
        if not isinstance(set_eval, dict):
            raise er003.QaSchemaError("set評価がオブジェクトでありません")
        if "runtime_strategy_id" not in set_eval or set_eval["runtime_strategy_id"] not in STRATEGY_IDS:
            raise er003.QaSchemaError(f"runtime_strategy_idが不正です(実際: {set_eval.get('runtime_strategy_id')!r})")
        seen_strategy_ids.add(set_eval["runtime_strategy_id"])
        items = set_eval.get("items")
        if not isinstance(items, list) or len(items) != RESEARCH_ITEM_COUNT:
            raise er003.QaSchemaError(f"set内のitemsが{RESEARCH_ITEM_COUNT}件でありません")
        for item in items:
            if not isinstance(item, dict):
                raise er003.QaSchemaError("Form QA itemがオブジェクトでありません")
            for field_name in FORM_QA_ITEM_SCHEMA_PROPERTIES:
                if field_name not in item:
                    raise er003.QaSchemaError(f"Form QA itemに必須フィールド'{field_name}'がありません")
    if seen_strategy_ids != set(STRATEGY_IDS):
        raise er003.QaSchemaError(f"3方式すべてが評価されていません(実際: {seen_strategy_ids})")
    return parsed


def load_form_qa_prompt_template(path: str = FORM_QA_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_form_qa_prompt(approved_b2_article: str, sets_json: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_form_qa_prompt_template()
    return template.replace("{approved_b2_article}", approved_b2_article).replace("{sets_json}", sets_json)


def make_form_qa_fn(
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
            text={"format": {"type": "json_schema", **FORM_QA_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("Extraction Form QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn
