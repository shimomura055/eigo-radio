# ============================================================
# er002_ja_web_research_r4.py
# ER-002-v1.2M-R4: 記事長制約と複数記事同時生成の比較検証
# ============================================================
# R3(writer自身によるWeb検索・自己取材)は一切変更しない。R3で明らかに
# なった「記事が阪神マスターより明らかに長い」という課題に対して、次の
# 2条件を比較する:
#   条件L : A01/A02/ADD03を1記事ずつ生成 + 長さ指示を追加
#   条件LB: A01/A02/ADD03を1回のwriter実行で同時生成 + 同じ長さ指示
#
# R4で新たに導入する重要な違い(R3からの変更点):
#   - writerの再試行は「技術的失敗(通信エラー・タイムアウト・応答本文
#     取得不可)」のみ最大1回。Web検索未使用・構造不適合・文字数逸脱は
#     初回遵守率を測定するため一切再試行しない(R3のrun_writer_with_gates
#     は再利用しない。技術的失敗のみを扱う新しいゲートを実装する)。
#   - fact checker側のロジック(run_fact_checker_with_gates等)はR3から
#     完全に不変のまま再利用する。
#
# 以下は一切importしない・再実装しない:
#   - er002_editorial_common.py / er002_editorial_angle_adapter.py /
#     er002_editorial_runner.py(Editorial Brief系)
#   - concise brief関連の処理(R1/R2のbuild_writer_user_message系)
# 以下はR3からそのまま再利用する(再実装しない):
#   - er002_ja_web_research_r3.WRITER_MODEL/WRITER_REASONING_EFFORT/
#     NEUTRAL_DEVELOPER_MESSAGE/make_writer_research_fn/
#     build_writer_user_message_r3/extract_web_search_usage/
#     extract_sources/make_fact_checker_fn/build_fact_check_prompt/
#     run_fact_checker_with_gates/parse_and_validate_fact_check_output/
#     FactCheckSchemaError/FACT_CHECK_JSON_SCHEMA/FACT_CHECK_VERDICTS
#   - er002_ja_free_markdown_restore_r2.validate_point_structure(構造ゲート)

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import er002_ja_free_markdown_restore_r2 as restore_r2
import er002_ja_web_research_r3 as r3

EXPERIMENT_VERSION = "ER-002-v1.2M-R4"
BASE_EXPERIMENT_VERSION = "ER-002-v1.2M-R3"

# R3から不変のまま再利用(再定義しない・値を変更しない)
WRITER_MODEL = r3.WRITER_MODEL  # "gpt-5.6-sol"
WRITER_REASONING_EFFORT = r3.WRITER_REASONING_EFFORT  # "high"
NEUTRAL_DEVELOPER_MESSAGE = r3.NEUTRAL_DEVELOPER_MESSAGE  # "日本語の記事を作成してください。"

R4_L_LENGTH_SUFFIX_PATH = "er002_v1_2m_restore_briefs/length_instruction_suffix_r4.txt"
R4_LB_WRITER_PROMPT_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template_r4_lb.txt"

R4_LB_TOPIC_ORDER = ["A01", "A02", "ADD03"]


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


LENGTH_TOLERANCE_LOWER = 0.85
LENGTH_TOLERANCE_UPPER = 1.15


def compute_length_bounds(master_count: int) -> tuple:
    lower_bound = math.floor(master_count * LENGTH_TOLERANCE_LOWER)
    upper_bound = math.ceil(master_count * LENGTH_TOLERANCE_UPPER)
    return lower_bound, upper_bound


def validate_length(count_result: dict, lower_bound: int, upper_bound: int) -> str:
    if count_result["status"] != "COUNT_OK":
        return "COUNT_EXTRACTION_UNCERTAIN"
    count = count_result["spoken_text_char_count"]
    return "LENGTH_PASS" if lower_bound <= count <= upper_bound else "LENGTH_FAIL"


# ============================================================
# ブロック2: 条件L(個別生成+長さ制約)のプロンプト構築
# ============================================================
def load_length_instruction_suffix_template(path: str = R4_L_LENGTH_SUFFIX_PATH) -> str:
    return r3.restore.load_text_file(path)


def build_length_instruction_suffix(master_count: int, lower_bound: int, upper_bound: int,
                                     template: Optional[str] = None) -> str:
    template = template if template is not None else load_length_instruction_suffix_template()
    return template.format(master_count=master_count, lower_bound=lower_bound, upper_bound=upper_bound)


def build_writer_user_message_r4_l(master_full_text: str, topic: str, master_count: int,
                                    lower_bound: int, upper_bound: int) -> str:
    """R3のwriter promptをそのまま使用し、末尾へ長さ指示3文だけを追加する。
    R3との差分がこの3文だけであることをテストで保証できるよう、
    r3.build_writer_user_message_r3の出力へ文字列連結するだけに留める。"""
    r3_message = r3.build_writer_user_message_r3(master_full_text, topic)
    suffix = build_length_instruction_suffix(master_count, lower_bound, upper_bound)
    return r3_message + "\n\n" + suffix


# ============================================================
# ブロック3: 条件LB(3記事同時生成+長さ制約)のプロンプト構築
# ============================================================
def load_r4_lb_writer_prompt_template(path: str = R4_LB_WRITER_PROMPT_PATH) -> str:
    return r3.restore.load_text_file(path)


def build_writer_user_message_r4_lb(master_full_text: str, master_count: int,
                                     lower_bound: int, upper_bound: int,
                                     template: Optional[str] = None) -> str:
    template = template if template is not None else load_r4_lb_writer_prompt_template()
    return template.format(
        hanshin_master_full_text=master_full_text,
        master_count=master_count, lower_bound=lower_bound, upper_bound=upper_bound,
    )


# ============================================================
# ブロック4: writer技術的失敗のみ再試行するゲート(R4新規)
# ============================================================
# R3のrun_writer_with_gatesは「Web検索未使用」「構造不適合」でも再試行
# したが、R4は初回遵守率を測定する比較実験のため、これらでは再試行しない。
# 再試行するのは通信エラー・タイムアウト・応答本文取得不可(技術的失敗)
# のみ、最大1回。

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
                                 lower_bound: int, upper_bound: int) -> dict:
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
# ブロック5: 条件LB出力の分割(3記事へ機械分割)
# ============================================================
# 記事ID見出しは"## "の直後に英数字トークンのみが続く行として識別する
# (記事自身が持つ内部見出し、例えば"## 今回の深夜モードポイント🌙"は
# 日本語・絵文字を含むため、このパターンには一致しない)。既知の3ID以外
# が来た場合も一致させ、BATCH_PARSE_INVALIDの「未知の記事ID」判定へ
# 回せるようにする。
_BATCH_HEADING_RE = re.compile(r"^##[ \t]+([A-Za-z0-9]+)[ \t]*$", re.MULTILINE)


def parse_batch_articles(raw_text: str) -> dict:
    """`## A01` / `## A02` / `## ADD03`のレベル2見出しを境界として3記事へ
    機械分割する。見出し行自体は各記事のraw_textに含めない(管理用の
    ため)。順序違反・重複・欠落・未知IDがあれば本文を推測で分割せず
    BATCH_PARSE_INVALIDを返す。"""
    matches = list(_BATCH_HEADING_RE.finditer(raw_text))
    found_ids = [m.group(1) for m in matches]

    reasons = []
    if len(found_ids) != len(R4_LB_TOPIC_ORDER):
        reasons.append(f"見出し数が{len(R4_LB_TOPIC_ORDER)}件ではない(実際: {len(found_ids)}件)")
    if len(set(found_ids)) != len(found_ids):
        reasons.append("記事IDが重複している")
    missing = set(R4_LB_TOPIC_ORDER) - set(found_ids)
    if missing:
        reasons.append(f"記事IDが欠落している: {sorted(missing)}")
    unknown = set(found_ids) - set(R4_LB_TOPIC_ORDER)
    if unknown:
        reasons.append(f"未知の記事IDがある: {sorted(unknown)}")
    if not reasons and found_ids != R4_LB_TOPIC_ORDER:
        reasons.append(f"記事の順序が期待と異なる(期待: {R4_LB_TOPIC_ORDER}, 実際: {found_ids})")

    if reasons:
        return {"status": "BATCH_PARSE_INVALID", "reasons": reasons, "articles": None}

    articles = {}
    for i, m in enumerate(matches):
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        segment = raw_text[content_start:content_end]
        stripped = segment.strip("\n")
        leading_ws = len(segment) - len(segment.lstrip("\n"))
        articles[m.group(1)] = {
            "raw_text": stripped,
            "segment_start_offset": content_start + leading_ws,
            "segment_end_offset": content_start + leading_ws + len(stripped),
        }
    return {"status": "BATCH_PARSE_OK", "reasons": [], "articles": articles}


def attribute_annotations_to_batch_articles(articles: dict, annotations: Optional[list]) -> dict:
    """バッチ全体のannotation(start_index/end_indexはバッチ全文基準)を、
    分割済み各記事の座標系(記事ごとのローカルindex)へ再配分する。
    annotationsがNone(取得不能)の場合は、各記事のcitation_annotationsも
    Noneのままとし、以降の文字数計測でCOUNT_EXTRACTION_UNCERTAINとして
    扱われるようにする。1件のannotationが単一の記事segmentへ完全に
    収まらない場合は、そのannotationだけ安全側に倒して割り当てない
    (=引用として除去されない)。"""
    result = {topic_id: {**info, "citation_annotations": (None if annotations is None else [])}
              for topic_id, info in articles.items()}
    if annotations is None:
        return result
    for ann in annotations:
        start, end = ann.get("start_index"), ann.get("end_index")
        if start is None or end is None:
            continue
        for topic_id, info in articles.items():
            seg_start, seg_end = info["segment_start_offset"], info["segment_end_offset"]
            if seg_start <= start and end <= seg_end:
                result[topic_id]["citation_annotations"].append({
                    "start_index": start - seg_start, "end_index": end - seg_start,
                    "title": ann.get("title"), "url": ann.get("url"),
                })
                break
    return result


def classify_batch_topic_evidence(citation_annotations: Optional[list]) -> str:
    """テーマ別の調査証跡を、そのテーマのsegmentへ実際に帰属した引用
    annotationの有無で監査可能に判定する(自由記述の検索クエリ文字列と
    テーマ名をキーワード照合するような不安定な推定は行わない)。
    Noneの場合(=そもそもannotationを取得できなかった)は安全側に倒し
    未確認として扱う。"""
    if not citation_annotations:
        return "BATCH_TOPIC_RESEARCH_NOT_CONFIRMED"
    return "TOPIC_RESEARCH_CONFIRMED"


def classify_batch_article_diagnostics(raw_text: str, batch_web_search_status: str,
                                        citation_annotations: Optional[list],
                                        count_result: dict, lower_bound: int, upper_bound: int) -> dict:
    """条件LBの分割済み1記事を、構造・文字数・調査証跡確認の3軸で診断
    する。writer Web検索そのものはバッチ全体で1回しか判定できないため
    batch_web_search_statusとして引数で受け取る。"""
    structure = restore_r2.validate_point_structure(raw_text)
    length_status = validate_length(count_result, lower_bound, upper_bound)
    topic_evidence_status = classify_batch_topic_evidence(citation_annotations)
    eligible_for_fact_check = (
        batch_web_search_status == "WEB_SEARCH_USED"
        and structure.status == "STRUCTURE_PASS"
        and topic_evidence_status == "TOPIC_RESEARCH_CONFIRMED"
    )
    return {
        "structure_status": structure.status,
        "structure_headings": structure.headings,
        "structure_reasons": structure.reasons,
        "length_status": length_status,
        "topic_evidence_status": topic_evidence_status,
        "eligible_for_fact_check": eligible_for_fact_check,
    }
