# ============================================================
# er002_ja_web_research_r4.py
# ER-002-v1.2M-R4: 記事長制約と複数記事同時生成の比較検証【実験記録】
# ============================================================
# ★★★ このファイルは実験記録として保持しているものであり、通常の記事
# ★★★ 生成フローからは呼び出されない。正式採用された記事生成パイプ
# ★★★ ラインは er002_ja_article_generation.py を参照すること。
#
# ER-002-v1.2M-R4-FINALIZEにより、次の決定がなされた:
#   - 条件L(1テーマにつきwriterを1回実行+長さ指示)を正式採用
#   - 条件LB(複数テーマを1回のwriter実行で同時生成)は不採用
# 条件Lのロジック(正規化・プロンプト構築・技術ゲート・診断分類)は
# er002_ja_article_generation.pyへ移設し、このファイルはそこから
# re-exportして後方互換を保っている(既存のR4テストを変更せずに動作
# させるため)。条件LB専用のコード(プロンプト構築・バッチ分割・
# citation再配分・調査証跡判定)は、実験の再現性のためにこのファイルに
# だけ残しており、正式フローには一切組み込まれていない。
#
# R3(writer自身によるWeb検索・自己取材)は一切変更しない。
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

import re
from typing import Optional

import er002_ja_article_generation as article_gen
import er002_ja_free_markdown_restore_r2 as restore_r2
import er002_ja_web_research_r3 as r3

EXPERIMENT_VERSION = "ER-002-v1.2M-R4"
BASE_EXPERIMENT_VERSION = "ER-002-v1.2M-R3"

# R3から不変のまま再利用(再定義しない・値を変更しない)
WRITER_MODEL = r3.WRITER_MODEL  # "gpt-5.6-sol"
WRITER_REASONING_EFFORT = r3.WRITER_REASONING_EFFORT  # "high"
NEUTRAL_DEVELOPER_MESSAGE = r3.NEUTRAL_DEVELOPER_MESSAGE  # "日本語の記事を作成してください。"

R4_L_LENGTH_SUFFIX_PATH = article_gen.LENGTH_INSTRUCTION_SUFFIX_PATH
R4_LB_WRITER_PROMPT_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template_r4_lb.txt"

R4_LB_TOPIC_ORDER = ["A01", "A02", "ADD03"]

sha256_text = article_gen.sha256_text

# ============================================================
# ブロック1: 読み上げ文字数(spoken_text_char_count)の正規化
# ============================================================
# 正式採用モジュール(er002_ja_article_generation.py)からの再エクスポート。
# ここでは再実装しない(単一の情報源を保つため)。
extract_citation_annotations = article_gen.extract_citation_annotations
remove_citation_spans = article_gen.remove_citation_spans
strip_markdown_symbols = article_gen.strip_markdown_symbols
normalize_for_char_count = article_gen.normalize_for_char_count
compute_spoken_text_char_count = article_gen.compute_spoken_text_char_count
compute_master_char_count_result = article_gen.compute_master_char_count_result

LENGTH_TOLERANCE_LOWER = article_gen.LENGTH_TOLERANCE_LOWER_RATIO
LENGTH_TOLERANCE_UPPER = article_gen.LENGTH_TOLERANCE_UPPER_RATIO


def compute_length_bounds(master_count: int) -> tuple:
    return article_gen.compute_length_bounds(
        master_count, article_gen.LENGTH_TOLERANCE_LOWER_RATIO, article_gen.LENGTH_TOLERANCE_UPPER_RATIO)


def validate_length(count_result: dict, lower_bound: int, upper_bound: int) -> str:
    return article_gen.validate_length(count_result, lower_bound, upper_bound)


# ============================================================
# ブロック2: 条件L(個別生成+長さ制約)のプロンプト構築
# ============================================================
# 正式採用モジュールからの再エクスポート(条件Lは正式仕様そのもののため)。
load_length_instruction_suffix_template = article_gen.load_length_instruction_suffix_template
build_length_instruction_suffix = article_gen.build_length_instruction_suffix


def build_writer_user_message_r4_l(master_full_text: str, topic: str, master_count: int,
                                    lower_bound: int, upper_bound: int) -> str:
    return article_gen.build_writer_user_message(master_full_text, topic, master_count, lower_bound, upper_bound)


# ============================================================
# ブロック3【実験専用・不採用】: 条件LB(3記事同時生成+長さ制約)の
# プロンプト構築。正式フローからは呼び出さないこと。
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
# ブロック4: writer技術的失敗のみ再試行するゲート
# ============================================================
# 正式採用モジュールからの再エクスポート(条件Lで採用されたゲートを
# 条件LBの単一バッチ呼び出しにもそのまま使い回すため)。
MAX_TECHNICAL_RETRY_ATTEMPTS = article_gen.MAX_TECHNICAL_RETRY_ATTEMPTS
run_writer_technical_gate = article_gen.run_writer_technical_gate
classify_writer_diagnostics = article_gen.classify_writer_diagnostics


# ============================================================
# ブロック5【実験専用・不採用】: 条件LB出力の分割(3記事へ機械分割)
# 正式フローからは呼び出さないこと。
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
