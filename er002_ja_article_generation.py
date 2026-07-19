# ============================================================
# er002_ja_article_generation.py
# ER-002-v1.2M-R4-FINALIZE: 正式採用された記事生成パイプライン
# ============================================================
# ER-002-v1.2M-R4で比較検証した「条件L」(1テーマにつきwriterを1回実行し、
# 阪神マスターと同程度の読み上げ分量に収める長さ指示を追加する方式)を、
# ER-002の正式仕様として整理したモジュール。
#
# 正式採用: このモジュールの内容全て。
# 不採用  : 条件LB(複数テーマの同時生成・機械分割)は、このモジュールには
#           一切含まれていない。条件LBのコードは実験記録として
#           er002_ja_web_research_r4.py に残しているが、通常の記事生成
#           フローからは呼び出されない。
#
# 変更しないもの(R3から完全に不変のまま再利用する):
#   - er002_ja_web_research_r3.WRITER_MODEL/WRITER_REASONING_EFFORT/
#     NEUTRAL_DEVELOPER_MESSAGE/make_writer_research_fn/
#     build_writer_user_message_r3/make_fact_checker_fn/
#     build_fact_check_prompt/run_fact_checker_with_gates/
#     parse_and_validate_fact_check_output/FACT_CHECK_JSON_SCHEMA/
#     FACT_CHECK_VERDICTS/FACT_CHECKER_MODEL/FACT_CHECKER_REASONING_EFFORT
#   - er002_ja_free_markdown_restore_r2.validate_point_structure(構造ゲート)
#
# 読み上げ文字数の基準値・許容範囲は er002_v1_2m_length_spec.json を
# 単一の情報源として読み込む(コード内に592/802/697等のマジックナンバー
# を分散させない)。将来値を変更する場合は、このJSONを再計算・上書き
# するだけでよい。

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from typing import Any, Callable, Optional

import er002_ja_free_markdown_restore_r2 as restore_r2
import er002_ja_web_research_r3 as r3

SPEC_VERSION = "ER-002-v1.2M-R4-FINALIZE"

# R3から不変のまま再利用(再定義しない・値を変更しない)
WRITER_MODEL = r3.WRITER_MODEL  # "gpt-5.6-sol"
WRITER_REASONING_EFFORT = r3.WRITER_REASONING_EFFORT  # "high"
NEUTRAL_DEVELOPER_MESSAGE = r3.NEUTRAL_DEVELOPER_MESSAGE  # "日本語の記事を作成してください。"

WRITER_EXECUTIONS_PER_ARTICLE = 1  # 1テーマにつきwriterを1回実行する(バッチ生成はしない)

LENGTH_INSTRUCTION_SUFFIX_PATH = "er002_v1_2m_restore_briefs/length_instruction_suffix_r4.txt"
LENGTH_SPEC_PATH = "er002_v1_2m_length_spec.json"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# ブロック1: 読み上げ文字数(spoken_text_char_count)の正規化
# ============================================================
# citation annotationのstart_index/end_indexは、OpenAI Responses APIの
# 実際の応答(ER-002-v1.2M-R3で保存したraw_response.jsonで実測・確認済み)
# で、output_text中の引用表示スパン(例: "([fifa.com](https://...))")を
# 正確に指す。このスパンをindexベースで除去することで、引用表示を安全に
# 分離したreading copyを作る。

_MD_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```")
_MD_INLINE_CODE_RE = re.compile(r"`([^`]*)`")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_URL_RE = re.compile(r"https?://\S+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MD_HEADING_RE = re.compile(r"(?m)^#{1,6}[ \t]*")
_MD_BLOCKQUOTE_RE = re.compile(r"(?m)^>[ \t]?")
_MD_HR_RE = re.compile(r"(?m)^[ \t]*([-*_])(?:[ \t]*\1){2,}[ \t]*$")
_MD_EMPHASIS_RE = re.compile(r"\*\*\*|\*\*|\*|___|__|_")
_WHITESPACE_RE = re.compile(r"[\s　]+")


def extract_citation_annotations(response: Any) -> Optional[list]:
    """response.output中のmessageアイテムからurl_citation annotationを
    (start_index, end_index, title, url)のまま(重複除去せず、出現順で)
    取り出す。message/contentの構造が見つからない場合はNoneを返す
    (「取得できず」を明示し、以降で推測削除をしないようにするため)。"""
    messages = [item for item in getattr(response, "output", []) or [] if getattr(item, "type", None) == "message"]
    if not messages:
        return None
    annotations = []
    found_content = False
    for item in messages:
        for content in getattr(item, "content", None) or []:
            found_content = True
            for ann in getattr(content, "annotations", None) or []:
                if getattr(ann, "type", None) != "url_citation":
                    continue
                start = getattr(ann, "start_index", None)
                end = getattr(ann, "end_index", None)
                if start is None or end is None:
                    continue
                annotations.append({
                    "start_index": start, "end_index": end,
                    "title": getattr(ann, "title", None), "url": getattr(ann, "url", None),
                })
    if not found_content:
        return None
    return annotations


def remove_citation_spans(text: str, annotations: list) -> str:
    """開始位置の降順でspanを除去する(除去のたびに後続indexがずれない
    ようにするため)。"""
    spans = sorted(
        {(a["start_index"], a["end_index"]) for a in annotations
         if a.get("start_index") is not None and a.get("end_index") is not None},
        key=lambda s: s[0], reverse=True,
    )
    result = text
    for start, end in spans:
        if 0 <= start <= end <= len(result):
            result = result[:start] + result[end:]
    return result


def strip_markdown_symbols(text: str) -> str:
    """Markdown記号そのもの・URL・HTMLタグを除去する。任意の丸括弧書きは
    一律削除しない(citation annotationとして特定できたスパンだけを
    remove_citation_spansで既に除去済みという前提)。"""
    text = _MD_CODE_FENCE_RE.sub(" ", text)
    text = _MD_INLINE_CODE_RE.sub(r"\1", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _URL_RE.sub("", text)
    text = _HTML_TAG_RE.sub("", text)
    text = _MD_HEADING_RE.sub("", text)
    text = _MD_BLOCKQUOTE_RE.sub("", text)
    text = _MD_HR_RE.sub("", text)
    text = _MD_EMPHASIS_RE.sub("", text)
    return text


def normalize_for_char_count(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _WHITESPACE_RE.sub("", text)
    return text


def compute_spoken_text_char_count(raw_text: str, annotations: Optional[list]) -> dict:
    """annotationsがNone(=citation annotationを取得できなかった)場合は
    推測で本文を削らず、COUNT_EXTRACTION_UNCERTAINを返す。annotationsが
    空リスト(=citationが0件と確定)の場合は、そのまま(除去対象なし)で
    計測を続行する。"""
    if annotations is None:
        return {
            "status": "COUNT_EXTRACTION_UNCERTAIN",
            "spoken_text_char_count": None,
            "reading_copy": None,
        }
    reading_copy = remove_citation_spans(raw_text, annotations)
    normalized = normalize_for_char_count(strip_markdown_symbols(reading_copy))
    return {
        "status": "COUNT_OK",
        "spoken_text_char_count": len(normalized),
        "reading_copy": reading_copy,
    }


def compute_master_char_count_result(master_text: str) -> dict:
    """阪神マスターは固定の著者記述テキストであり、citation annotationは
    そもそも存在しない(=0件確定)。compute_spoken_text_char_countへ空
    リストを渡し、同じ正規化ロジックで計測する。"""
    return compute_spoken_text_char_count(master_text, annotations=[])


# ============================================================
# ブロック2: 読み上げ文字数の基準値・許容範囲(単一の情報源から読み込む)
# ============================================================
def load_length_spec(path: str = LENGTH_SPEC_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_length_bounds(master_count: int, tolerance_lower_ratio: float, tolerance_upper_ratio: float) -> tuple:
    lower_bound = math.floor(master_count * tolerance_lower_ratio)
    upper_bound = math.ceil(master_count * tolerance_upper_ratio)
    return lower_bound, upper_bound


def recompute_length_spec_from_master(master_path: Optional[str] = None,
                                       tolerance_lower_ratio: Optional[float] = None,
                                       tolerance_upper_ratio: Optional[float] = None) -> dict:
    """凍結済みJSONを使わず、阪神マスターから基準値を再計算する(凍結値との
    整合性検証・将来の値更新に使う)。"""
    spec = load_length_spec()
    master_path = master_path or spec["master_path"]
    tolerance_lower_ratio = tolerance_lower_ratio if tolerance_lower_ratio is not None else spec["tolerance_lower_ratio"]
    tolerance_upper_ratio = tolerance_upper_ratio if tolerance_upper_ratio is not None else spec["tolerance_upper_ratio"]
    with open(master_path, encoding="utf-8") as f:
        master_text = f.read()
    count_result = compute_master_char_count_result(master_text)
    lower_bound, upper_bound = compute_length_bounds(
        count_result["spoken_text_char_count"], tolerance_lower_ratio, tolerance_upper_ratio)
    return {
        "master_spoken_text_char_count": count_result["spoken_text_char_count"],
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
    }


_LENGTH_SPEC = load_length_spec()
MASTER_SPOKEN_TEXT_CHAR_COUNT = _LENGTH_SPEC["master_spoken_text_char_count"]
LENGTH_LOWER_BOUND = _LENGTH_SPEC["lower_bound"]
LENGTH_UPPER_BOUND = _LENGTH_SPEC["upper_bound"]
LENGTH_TOLERANCE_LOWER_RATIO = _LENGTH_SPEC["tolerance_lower_ratio"]
LENGTH_TOLERANCE_UPPER_RATIO = _LENGTH_SPEC["tolerance_upper_ratio"]


def validate_length(count_result: dict, lower_bound: int = LENGTH_LOWER_BOUND,
                     upper_bound: int = LENGTH_UPPER_BOUND) -> str:
    if count_result["status"] != "COUNT_OK":
        return "COUNT_EXTRACTION_UNCERTAIN"
    count = count_result["spoken_text_char_count"]
    return "LENGTH_PASS" if lower_bound <= count <= upper_bound else "LENGTH_FAIL"


# ============================================================
# ブロック3: writerプロンプト構築(1テーマ1writer実行、長さ指示付き)
# ============================================================
def load_length_instruction_suffix_template(path: str = LENGTH_INSTRUCTION_SUFFIX_PATH) -> str:
    return r3.restore.load_text_file(path)


def build_length_instruction_suffix(master_count: int = MASTER_SPOKEN_TEXT_CHAR_COUNT,
                                     lower_bound: int = LENGTH_LOWER_BOUND,
                                     upper_bound: int = LENGTH_UPPER_BOUND,
                                     template: Optional[str] = None) -> str:
    template = template if template is not None else load_length_instruction_suffix_template()
    return template.format(master_count=master_count, lower_bound=lower_bound, upper_bound=upper_bound)


def build_writer_user_message(master_full_text: str, topic: str,
                               master_count: int = MASTER_SPOKEN_TEXT_CHAR_COUNT,
                               lower_bound: int = LENGTH_LOWER_BOUND,
                               upper_bound: int = LENGTH_UPPER_BOUND) -> str:
    """R3のwriter promptをそのまま使用し、末尾へ長さ指示3文だけを追加する
    (正式仕様)。1テーマにつき1回のこの関数呼び出し・1回のwriter実行で
    完結する。複数テーマの同時投入はサポートしない。"""
    r3_message = r3.build_writer_user_message_r3(master_full_text, topic)
    suffix = build_length_instruction_suffix(master_count, lower_bound, upper_bound)
    return r3_message + "\n\n" + suffix


# ============================================================
# ブロック4: writer技術的失敗のみ再試行するゲート(正式仕様)
# ============================================================
# 文字数超過・構造不適合・内容不満を理由とした自動再生成は行わない
# (今回の仕様に含めない、との正式決定による)。再試行するのは通信エラー・
# タイムアウト・応答本文取得不可(技術的失敗)のみ、最大1回。

MAX_TECHNICAL_RETRY_ATTEMPTS = 2  # 初回 + 技術的失敗時の再試行1回のみ


def run_writer_technical_gate(
    make_writer_fn: Callable[[], Callable],
    max_attempts: int = MAX_TECHNICAL_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗(通信エラー・タイムアウト・応答本文取得不可)のみ最大1回
    再試行する。Web検索未使用・構造不適合・文字数逸脱はここでは判定せず、
    技術的に応答を得られたらそのまま確定して返す(呼び出し側が別途、
    診断的に分類する)。

    戻り値: (raw_text, final_status, attempts_detail, model_id, response_id,
             search_usage, sources)
    final_status: "WRITER_CALL_SUCCEEDED" / "TECHNICAL_GENERATION_FAILED"
    """
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        writer_fn = make_writer_fn()
        try:
            raw_text, model_id, response_id, search_usage, sources = writer_fn()
        except Exception as e:
            attempts_detail.append({
                "content_attempt": attempt, "status": "TECHNICAL_GENERATION_FAILED",
                "error": f"{type(e).__name__}: {e}", "raw_text": None,
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None, None, None

        attempts_detail.append({
            "content_attempt": attempt, "status": "WRITER_CALL_SUCCEEDED",
            "search_usage": search_usage, "sources": sources,
            "raw_text": raw_text, "model": model_id, "response_id": response_id,
        })
        return raw_text, "WRITER_CALL_SUCCEEDED", attempts_detail, model_id, response_id, search_usage, sources

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None, None, None


def classify_writer_diagnostics(raw_text: str, search_usage: dict, count_result: dict,
                                 lower_bound: int = LENGTH_LOWER_BOUND,
                                 upper_bound: int = LENGTH_UPPER_BOUND) -> dict:
    """技術的に成功した1回の出力を、Web検索使用・構造・文字数の3軸で診断
    する(再試行トリガーではなく記録のためだけの分類)。"""
    web_search_status = "WEB_SEARCH_USED" if search_usage["web_search_call_count"] >= 1 else "WRITER_WEB_SEARCH_NOT_USED"
    structure = restore_r2.validate_point_structure(raw_text)
    length_status = validate_length(count_result, lower_bound, upper_bound)
    eligible_for_fact_check = (
        web_search_status == "WEB_SEARCH_USED" and structure.status == "STRUCTURE_PASS"
    )
    return {
        "web_search_status": web_search_status,
        "structure_status": structure.status,
        "structure_headings": structure.headings,
        "structure_reasons": structure.reasons,
        "length_status": length_status,
        "eligible_for_fact_check": eligible_for_fact_check,
    }


# ============================================================
# ブロック5: fact checker(R3から完全に不変のまま再利用)
# ============================================================
# 以下はこのモジュールで再定義せず、呼び出し側がr3経由でそのまま使う:
#   r3.build_fact_check_prompt / r3.make_fact_checker_fn /
#   r3.run_fact_checker_with_gates / r3.parse_and_validate_fact_check_output
# PASS/REVIEW_REQUIRED/FAILの扱い(FAILは採用しない、REVIEW_REQUIREDを
# 自動的にPASSへ読み替えない)は、呼び出し側の判定ロジックで維持する。
FACT_CHECK_INCLUDE_VERDICTS = ("PASS", "REVIEW_REQUIRED")  # FAILは含めない
