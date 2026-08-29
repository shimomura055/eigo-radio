# ============================================================
# er003_key_words_research10.py
# ER-003-P2F: A02・ADD03におけるKey Words 3方式×10件の比較調査
# ============================================================
# ER-003-P2EのA01比較(L/P/U、各5件)を、A02・ADD03へ拡張する。今回だけ
# 候補数を5件から10件へ拡大する調査であり、製品仕様のKey Words数は
# 5件のまま変更しない。10件は配信・TTS・正式仕様へは反映しない。
#
# 共通入力は各記事の承認済み概要(summary_en_approved.md)と確定済み
# B2本文のみ。日本語原稿・Natural English Source・P1/P1B・P2Dの選定
# 結果・P2EのA01選定結果/比較QA/ユーザー評価・ユーザーが挙げた具体的
# 候補語・Web検索結果・外部辞書・他記事・TTS情報はselectorへ一切渡さ
# ない。一方式の結果を、別方式または別記事のselectorへ渡さない。
#
# 記事2件×方式3件=selector 6 call(独立)。技術的失敗・schema/本文
# 対応不適合のみ、call毎に最大1回同一条件で再試行する。内容品質を
# 理由とした自動再生成は行わない。
#
# 再利用するもの(再実装しない):
#   - er003_key_words_strategy_compare.SELECTOR_MODEL/
#     SELECTOR_REASONING_EFFORT/SELECTOR_DEVELOPER_MESSAGE(P2Eと不変)
#   - er003_key_words_strategy_compare.STRATEGY_IDS/ITEM_TYPES/
#     TRI_LEVELS/PORTFOLIO_CATEGORIES(P2Eの評価軸をそのまま使う)
#   - er003_b2_key_words.B2_INPUT_PATHS/APPROVED_SUMMARY_PATHS/
#     load_approved_b2_article/load_approved_summary(確定済み入力は
#     P2D/P2Eと完全に同一)
#   - er003_b2_key_words.build_key_words_reading_copy(rankをorderへ
#     読み替えるアダプタ経由で再利用する)
#   - er003_ja_to_en_translation.run_json_response_gate(比較QA用)
#   - er003_ja_to_en_translation.sha256_text

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_b2_key_words as p2d
import er003_key_words_strategy_compare as p2e
import er003_ja_to_en_translation as er003

EXPERIMENT_VERSION = "ER-003-P2F"
ARTICLE_IDS = ("A02", "ADD03")  # A01はP2Eで実施済み、今回は再実行しない

RESEARCH_ITEM_COUNT = 10
PRODUCTION_ITEM_COUNT_UNCHANGED = 5  # 製品仕様のKey Words数は5件のまま(調査のみ拡張)

STRATEGY_IDS = p2e.STRATEGY_IDS  # ("L", "P", "U")
ITEM_TYPES = p2e.ITEM_TYPES
TRI_LEVELS = p2e.TRI_LEVELS
PORTFOLIO_CATEGORIES = p2e.PORTFOLIO_CATEGORIES
RESEARCH_BANDS = ("TOP_5", "RANK_6_TO_10")

# P2D/P2Eから不変のまま再利用(再定義しない)
SELECTOR_MODEL = p2e.SELECTOR_MODEL  # "gpt-5.6-sol"
SELECTOR_REASONING_EFFORT = p2e.SELECTOR_REASONING_EFFORT  # "high"
SELECTOR_DEVELOPER_MESSAGE = p2e.SELECTOR_DEVELOPER_MESSAGE

STRATEGY_PROMPT_TEMPLATE_PATHS = {
    "L": "er003_v1_translator_briefs/b2_key_words_research10_l_prompt_template.txt",
    "P": "er003_v1_translator_briefs/b2_key_words_research10_p_prompt_template.txt",
    "U": "er003_v1_translator_briefs/b2_key_words_research10_u_prompt_template.txt",
}
COMPARISON_QA_PROMPT_TEMPLATE_PATH = (
    "er003_v1_translator_briefs/b2_key_words_research10_comparison_qa_prompt_template.txt"
)

# 確定済み入力はP2D/P2Eと完全に同一のものを使う(独立に定義しない)。
B2_INPUT_PATHS = p2d.B2_INPUT_PATHS
APPROVED_SUMMARY_PATHS = p2d.APPROVED_SUMMARY_PATHS
load_approved_b2_article = p2d.load_approved_b2_article
load_approved_summary = p2d.load_approved_summary

# 比較QAはP2Eと同じ汎用ゲートを再利用する。
run_json_response_gate = er003.run_json_response_gate

# 生成後の比較・ブラインドレビューにだけ使う参照セットはP2Eから流用
# しない(A01固有の表現であり、A02・ADD03には無関係のため)。今回は
# 参照セットなしで比較QAを行う。

# 記事ごとに別々の固定seedを使う(A01のP2Eとも異なるseed)。
BLIND_MAPPING_SEEDS = {
    "A02": 20260721,
    "ADD03": 20260722,
}


# ============================================================
# ブロック1: 共通schema(exactly 10・rank・research_band)・prompt構築
# ============================================================
def _research10_json_schema(strategy_id: str) -> dict:
    return {
        "name": f"b2_key_words_research10_{strategy_id.lower()}",
        "schema": {
            "type": "object",
            "properties": {
                "strategy_id": {"type": "string", "enum": list(STRATEGY_IDS)},
                "article_id": {"type": "string", "enum": list(ARTICLE_IDS)},
                "research_item_count": {"type": "integer", "enum": [RESEARCH_ITEM_COUNT]},
                "production_item_count_unchanged": {"type": "integer", "enum": [PRODUCTION_ITEM_COUNT_UNCHANGED]},
                "items": {
                    "type": "array",
                    "minItems": RESEARCH_ITEM_COUNT,
                    "maxItems": RESEARCH_ITEM_COUNT,
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer"},
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
                            "research_band": {"type": "string", "enum": list(RESEARCH_BANDS)},
                        },
                        "required": ["rank", "display_phrase", "source_form", "source_sentence", "ja_gloss",
                                     "item_type", "selection_reason", "listening_difficulty_reason",
                                     "inference_transparency", "topic_exposure_dependency", "comprehension_impact",
                                     "figurative_or_emotional_value", "spoiler_risk", "portfolio_category",
                                     "portfolio_substitution", "portfolio_substitution_reason", "research_band"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["strategy_id", "article_id", "research_item_count",
                         "production_item_count_unchanged", "items"],
            "additionalProperties": False,
        },
        "strict": True,
    }


RESEARCH10_JSON_SCHEMAS = {strategy_id: _research10_json_schema(strategy_id) for strategy_id in STRATEGY_IDS}


def load_strategy_prompt_template(strategy_id: str) -> str:
    return er003.restore.load_text_file(STRATEGY_PROMPT_TEMPLATE_PATHS[strategy_id])


def build_strategy_user_message(strategy_id: str, approved_summary: str, approved_b2_article: str,
                                 template: Optional[str] = None) -> str:
    template = template if template is not None else load_strategy_prompt_template(strategy_id)
    return template.replace("{approved_summary}", approved_summary).replace(
        "{approved_b2_article}", approved_b2_article)


class Research10SelectorModelMismatchError(RuntimeError):
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

    schema = RESEARCH10_JSON_SCHEMAS[strategy_id]

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
            raise Research10SelectorModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError(f"方式{strategy_id} 10件調査selector応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    fn.strategy_id = strategy_id
    return fn


# ============================================================
# ブロック2: 決定的validator(exactly 10・rank・band・本文対応・
# 方式Pの2件/カテゴリquota substitutionルール)
# ============================================================
_REQUIRED_ITEM_FIELDS = (
    "rank", "display_phrase", "source_form", "source_sentence", "ja_gloss", "item_type", "selection_reason",
    "listening_difficulty_reason", "inference_transparency", "topic_exposure_dependency", "comprehension_impact",
    "figurative_or_emotional_value", "spoiler_risk", "portfolio_category", "portfolio_substitution",
    "portfolio_substitution_reason", "research_band",
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
# ER-008-N8-FINAL-QA-HARDENING-21 Item 2: 全角/半角括弧による補足書きを
# 検知する(No.8実例:「搭乗前に列に並ぶ人（俗称）」)。
_JA_GLOSS_PARENTHETICAL_RE = re.compile(r"[（(].+?[）)]")

# 方式Pの「原則各カテゴリ2件」ルール: 実質カテゴリ数(otherを除く5種)で
# 均等割りした値を上回るカテゴリの超過分項目には、substitution記録を必須とする。
_PORTFOLIO_QUOTA_CATEGORIES = tuple(c for c in PORTFOLIO_CATEGORIES if c != "other")
_EXPECTED_PER_CATEGORY = RESEARCH_ITEM_COUNT // len(_PORTFOLIO_QUOTA_CATEGORIES)  # 10 // 5 = 2


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


def _expected_band(rank: int) -> str:
    return "TOP_5" if 1 <= rank <= 5 else "RANK_6_TO_10"


def validate_research10_selection(parsed: dict, b2_article_text: str, expected_strategy_id: str,
                                   expected_article_id: str) -> dict:
    """selector出力を決定的に検証する。比較・監査のための判定のみを行い、
    項目の追加・修正・入れ替えは一切行わない。"""
    reasons = []
    ok = True
    item_reasons: list = []

    if not isinstance(parsed, dict):
        return {"status": "KEY_WORDS_STRUCTURE_INVALID", "reasons": ["トップレベルがオブジェクトでない"],
                "item_reasons": []}

    if parsed.get("strategy_id") != expected_strategy_id:
        reasons.append(f"strategy_idが不一致(期待: {expected_strategy_id}, 実際: {parsed.get('strategy_id')!r})")
        ok = False
    if parsed.get("article_id") != expected_article_id:
        reasons.append(f"article_idが不一致(期待: {expected_article_id}, 実際: {parsed.get('article_id')!r})")
        ok = False
    if parsed.get("research_item_count") != RESEARCH_ITEM_COUNT:
        reasons.append(f"research_item_countが{RESEARCH_ITEM_COUNT}でない(実際: {parsed.get('research_item_count')!r})")
        ok = False
    if parsed.get("production_item_count_unchanged") != PRODUCTION_ITEM_COUNT_UNCHANGED:
        reasons.append(
            f"production_item_count_unchangedが{PRODUCTION_ITEM_COUNT_UNCHANGED}でない"
            f"(実際: {parsed.get('production_item_count_unchanged')!r})")
        ok = False

    items = parsed.get("items")
    if not isinstance(items, list):
        reasons.append("'items'が配列でない")
        return {"status": "KEY_WORDS_STRUCTURE_INVALID", "reasons": reasons, "item_reasons": []}

    if len(items) != RESEARCH_ITEM_COUNT:
        reasons.append(f"itemsが{RESEARCH_ITEM_COUNT}件でない(実際: {len(items)}件)")
        ok = False

    plain_article = er003.article_gen.strip_markdown_symbols(b2_article_text)
    normalized_raw_article = _normalize_for_match(b2_article_text)
    normalized_plain_article = _normalize_for_match(plain_article)

    ranks = []
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

        rank = item.get("rank")
        ranks.append(rank)
        categories.append(item.get("portfolio_category"))

        if isinstance(rank, int):
            expected_band = _expected_band(rank)
            if item.get("research_band") != expected_band:
                this_item_reasons.append(
                    f"research_bandがrank({rank})と整合しない(期待: {expected_band}, "
                    f"実際: {item.get('research_band')!r})")
                ok = False
        else:
            this_item_reasons.append("rankが整数でない")
            ok = False

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
            # ER-008-N8-FINAL-QA-HARDENING-21 Item 2: ja_glossは音声のみで
            # 読み上げられるため、「（俗称）」のような括弧書きの補足は
            # 音声にすると不自然で、意味の理解も助けない(No.8実データで
            # 発見)。プロンプト側の指示追加に加え、機械的にも検知する。
            if _JA_GLOSS_PARENTHETICAL_RE.search(ja_gloss):
                this_item_reasons.append(
                    "日本語グロスに括弧書きの補足が含まれている(音声だけで意味が"
                    "成立する自然な表現にすること)")
                ok = False

        if this_item_reasons:
            item_reasons.append({"index": i, "reasons": this_item_reasons})

    if ranks and (sorted(r for r in ranks if isinstance(r, int)) != list(range(1, RESEARCH_ITEM_COUNT + 1))
                  or len(ranks) != len(set(ranks))):
        reasons.append(f"rankが1〜{RESEARCH_ITEM_COUNT}の重複・欠番なしの並びでない(実際: {ranks})")
        ok = False

    if len(display_phrases) != len(set(display_phrases)):
        reasons.append("display_phraseに重複がある")
        ok = False
    if len(source_forms) != len(set(source_forms)):
        reasons.append("source_formに重複がある")
        ok = False

    category_distribution = {}
    for cat in categories:
        if cat is None:
            continue
        category_distribution[cat] = category_distribution.get(cat, 0) + 1

    if expected_strategy_id == "P":
        over_quota_categories = [cat for cat, count in category_distribution.items()
                                  if count > _EXPECTED_PER_CATEGORY]
        if over_quota_categories:
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                if item.get("portfolio_category") in over_quota_categories:
                    if not item.get("portfolio_substitution"):
                        reasons.append(
                            f"方式Pでカテゴリ'{item.get('portfolio_category')}'が定員"
                            f"({_EXPECTED_PER_CATEGORY}件)を超過しているが、index {i}のportfolio_substitutionがtrueでない")
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


MAX_RESEARCH10_RETRY_ATTEMPTS = 2  # 初回 + (技術的失敗 または 構造/本文対応不適合)時の再試行1回のみ


def run_research10_selection_gate(
    strategy_id: str,
    article_id: str,
    make_selector_factory: Callable[[], Callable],
    b2_article_text: str,
    max_attempts: int = MAX_RESEARCH10_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、またはexactly 10・schema・rank/band整合・本文対応・
    (方式Pのみ)quota超過時のsubstitution記録不適合であれば、call毎に
    同一条件で最大1回だけ再試行する。内容品質を理由とした再試行・
    再生成は行わない。他方式・他記事の結果を参照しない。

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

        validation = validate_research10_selection(parsed, b2_article_text, strategy_id, article_id)
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
# ブロック3: 読み上げ原稿(P2Dのビルダーをrank->orderアダプタ経由で再利用)
# ============================================================
def build_research_reading_copy(items: list) -> str:
    """検証済みのselection JSONから、製品仕様と同形式(Number One〜Five)
    のreading copyを決定的に構成する。P2Dのbuild_key_words_reading_copy
    は5項目固定(Number One〜Five)のため、rank 1〜5(TOP_5)の項目だけを
    対象とする(6〜10位は製品形式に存在しない順位のため、Number Six〜
    Tenのような新規固定文字列を独自に発明しない)。rankフィールドを
    order名へ読み替えるだけの薄いアダプタで、実際の構築ロジックは
    P2Dの関数をそのまま再利用する。"""
    top5_items = sorted([it for it in items if it["research_band"] == "TOP_5"], key=lambda it: it["rank"])
    adapted_items = [{**item, "order": item["rank"]} for item in top5_items]
    return p2d.build_key_words_reading_copy(adapted_items)


# ============================================================
# ブロック4: 決定的指標
# ============================================================
def compute_research10_metrics(items: list) -> dict:
    sorted_items = sorted(items, key=lambda it: it["rank"])
    top5 = [it for it in sorted_items if it["research_band"] == "TOP_5"]
    rank_6_10 = [it for it in sorted_items if it["research_band"] == "RANK_6_TO_10"]
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
        "top5_count": len(top5),
        "rank_6_10_count": len(rank_6_10),
        "item_type_counts": item_type_counts,
        "portfolio_category_counts": category_counts,
        "portfolio_substitution_count": substitution_count,
        "display_phrase_exact_duplicate_count": len(display_phrases_normalized) - len(set(display_phrases_normalized)),
    }


# ============================================================
# ブロック5: 記事別比較QA(3方式まとめて、selectorとは独立の新規API実行)
# ============================================================
QA_TRIAGE_LEVELS = ("LOW", "MEDIUM", "HIGH")

COMPARISON_QA_JSON_SCHEMA = {
    "name": "b2_key_words_research10_comparison_qa",
    "schema": {
        "type": "object",
        "properties": {
            "article_id": {"type": "string", "enum": list(ARTICLE_IDS)},
            "strategies": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "strategy_id": {"type": "string", "enum": list(STRATEGY_IDS)},
                        "top5_unknown_word_capture": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "top5_domain_expression_capture": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "top5_listening_chunk_capture": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "top5_figurative_emotional_capture": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "top5_transparent_easy_item_contamination": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "top5_low_value_items": {"type": "array", "items": {"type": "string"}},
                        "top5_spoiler_risk": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "top5_diversity": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "rank_6_10_promotion_candidates": {"type": "array", "items": {"type": "string"}},
                        "rank_6_10_demotion_candidates_from_top5": {"type": "array", "items": {"type": "string"}},
                        "rank_6_10_low_value_increase": {"type": "string", "enum": list(QA_TRIAGE_LEVELS)},
                        "notes": {"type": "string"},
                    },
                    "required": ["strategy_id", "top5_unknown_word_capture", "top5_domain_expression_capture",
                                 "top5_listening_chunk_capture", "top5_figurative_emotional_capture",
                                 "top5_transparent_easy_item_contamination", "top5_low_value_items",
                                 "top5_spoiler_risk", "top5_diversity", "rank_6_10_promotion_candidates",
                                 "rank_6_10_demotion_candidates_from_top5", "rank_6_10_low_value_increase", "notes"],
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
        "required": ["article_id", "strategies", "cross_strategy_overlap", "unique_items_by_strategy",
                     "provisional_best_fit", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_QA_STRATEGY_REQUIRED_FIELD_TYPES = {
    "strategy_id": str, "top5_unknown_word_capture": str, "top5_domain_expression_capture": str,
    "top5_listening_chunk_capture": str, "top5_figurative_emotional_capture": str,
    "top5_transparent_easy_item_contamination": str, "top5_low_value_items": list, "top5_spoiler_risk": str,
    "top5_diversity": str, "rank_6_10_promotion_candidates": list, "rank_6_10_demotion_candidates_from_top5": list,
    "rank_6_10_low_value_increase": str, "notes": str,
}
_QA_TOP_REQUIRED_FIELD_TYPES = {
    "article_id": str, "strategies": list, "cross_strategy_overlap": list, "unique_items_by_strategy": dict,
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
    if parsed["article_id"] not in ARTICLE_IDS:
        raise er003.QaSchemaError(f"article_idが不正です(実際: {parsed['article_id']!r})")
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
            .replace("{strategy_results_json}", strategy_results_json))


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
            raise er003.restore.GenerationEmptyOrBrokenError("10件調査比較QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


# ============================================================
# ブロック6: 記事別ブラインドマッピング(固定seedで決定的に生成)
# ============================================================
_BLIND_SET_LABELS = ("Set X", "Set Y", "Set Z")


def build_blind_mapping(article_id: str) -> dict:
    """L/P/UをSet X/Y/Zへ、記事別の固定seedで決定的に割り当てる。"""
    import random
    seed = BLIND_MAPPING_SEEDS[article_id]
    rng = random.Random(seed)
    shuffled_strategies = list(STRATEGY_IDS)
    rng.shuffle(shuffled_strategies)
    return {label: strategy_id for label, strategy_id in zip(_BLIND_SET_LABELS, shuffled_strategies)}
