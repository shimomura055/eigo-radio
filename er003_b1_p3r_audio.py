# ============================================================
# er003_b1_p3r_audio.py
# ER-003-B1-P3R: A01 Listening Preview + B1本文 通し音声プロトタイプ
# ============================================================
# ER-003-B1-P2で生成したPattern A(Story/Drama)と、ER-003-B1-P1でACCEPT
# 済みのA01 B1本文を、B2までに採用済みのナレーション仕様(Aoede /
# Emotional+Connected / Level2 / 全見出し読み上げ / セクション間0.8秒
# 無音 / 全文結合後にDynamics3を一度だけ適用)でそのまま音声化する。
#
# 新しいTTS演技指示・Preview専用style・speed/pitch指定は一切追加しない。
# 品質評価を理由とした自動再生成もしない(技術的失敗時のみ、同一payload
# で1回まで再試行)。
#
# 再利用するもの(再実装しない):
#   - er002_common.build_style_prefix/build_narration_plan/
#     assemble_audio/_call_tts_with_retry/normalize_pcm/
#     pcm_to_wav_bytes/pcm_bytes_to_float_mono/write_wav_float/
#     read_wav_float/measure_metrics/apply_dynamics3_once/
#     SAMPLE_RATE/SECTION_JOIN_PAUSE_SECONDS/DYNAMICS3_PARAMS
#   - er002_gemini_client.make_tts_call_fn(voice_name)
#   - er002_ja_article_generation.strip_markdown_symbols
#   - er003_natural_source.sha256_text
#
# 新規に追加するのは、B1本文markdownをer002_commonの台本schema
# ({"title", "sections": [...]})へ変換する最小限のparserのみ
# (この変換を行う既存実装がないため)。TTS演技指示・音声処理は
# 一切新規追加しない。

from __future__ import annotations

import json
import re
from typing import Optional

import er002_common as common
import er002_ja_article_generation as article_gen
import er003_natural_source as natural_source

ARTICLE_ID = "A01"
VOICE_NAME = "Aoede"

PATTERN_A_SOURCE_PATH = "er003_output/b1_p2/A01/listening_preview_raw.md"
B1_ARTICLE_SOURCE_PATH = "er003_output/b1_p1/A01/b1_article_raw.md"

sha256_text = natural_source.sha256_text

# 技術的失敗時のみ、同一payloadで最大1回まで再試行する(品質目的の
# 再生成は行わない)。er002_common.MAX_TTS_API_RETRY(既定2)を、本
# ステージでは明示的に1へ変更する。
MAX_TTS_TECHNICAL_RETRY = 1


# ============================================================
# ブロック1: source読み込み
# ============================================================
def load_pattern_a_text(raw_json_path: str = PATTERN_A_SOURCE_PATH) -> str:
    """ER-003-B1-P2の構造化raw出力からPattern Aのtextだけを取り出す。
    markdown見出しの正規表現抽出ではなく、構造化JSONから直接読むことで
    誤抽出を避ける。"""
    with open(raw_json_path, encoding="utf-8") as f:
        raw_text = f.read()
    parsed = json.loads(raw_text)
    pattern_a = next((p for p in parsed["patterns"] if p["pattern_id"] == "A"), None)
    if pattern_a is None:
        raise ValueError("Pattern Aがlistening_preview_raw.md内に見つかりません")
    return pattern_a["text"]


def load_b1_article_text(path: str = B1_ARTICLE_SOURCE_PATH) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# ブロック2: B1本文markdown → er002_common台本schemaへの変換(新規、
# 最小限)。既存のmarkdown→script変換ロジックはないため、ここでのみ
# 実装する。TTS演技指示・音声処理ロジックには一切踏み込まない。
# ============================================================
_TITLE_RE = re.compile(r"^#\s+(.+)$")
_H2_RE = re.compile(r"^##\s+(.+)$")
_POINT_ONE_RE = re.compile(r"^###\s+Point One:\s*(.+)$")
_POINT_TWO_RE = re.compile(r"^###\s+Point Two:\s*(.+)$")


def _clean(text: str) -> str:
    return article_gen.strip_markdown_symbols(text).strip()


def parse_b1_markdown_to_script(markdown_text: str) -> dict:
    """B1本文(# Title / intro / ## Today's...Points / ### Point One:.../
    ### Point Two:... / ## In One Line固定構造)を、er002_common.
    build_narration_planが受け取れる台本dictへ変換する。見出し・本文の
    追加・削除・要約は一切行わない(Markdown記号除去のみ)。"""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", markdown_text.strip()) if b.strip()]

    title = None
    body_paragraphs: list = []
    points_heading = None
    point_one_heading = None
    point_two_heading = None
    point_one_paragraphs: list = []
    point_two_paragraphs: list = []
    in_one_line_paragraphs: list = []

    bucket = None  # "body" / "point_one" / "point_two" / "in_one_line"

    for block in blocks:
        m_title = _TITLE_RE.match(block)
        if m_title and title is None:
            title = _clean(m_title.group(1))
            bucket = "body"
            continue

        m_p1 = _POINT_ONE_RE.match(block)
        if m_p1:
            point_one_heading = _clean(m_p1.group(1))
            bucket = "point_one"
            continue

        m_p2 = _POINT_TWO_RE.match(block)
        if m_p2:
            point_two_heading = _clean(m_p2.group(1))
            bucket = "point_two"
            continue

        m_h2 = _H2_RE.match(block)
        if m_h2:
            heading_text = _clean(m_h2.group(1))
            if heading_text == "In One Line":
                bucket = "in_one_line"
            else:
                points_heading = heading_text
                bucket = None  # "## Today's...Points"見出し自体は段落を持たない
            continue

        cleaned = _clean(block)
        if bucket == "body":
            body_paragraphs.append(cleaned)
        elif bucket == "point_one":
            point_one_paragraphs.append(cleaned)
        elif bucket == "point_two":
            point_two_paragraphs.append(cleaned)
        elif bucket == "in_one_line":
            in_one_line_paragraphs.append(cleaned)
        else:
            raise ValueError(f"見出しの外側に段落があります(想定外の構造): {block!r}")

    missing = [name for name, value in (
        ("title", title), ("points_heading", points_heading),
        ("point_one_heading", point_one_heading), ("point_two_heading", point_two_heading),
    ) if not value]
    if missing:
        raise ValueError(f"B1本文から必要な見出しを抽出できませんでした: {missing}")

    return {
        "title": title,
        "sections": [
            {"type": "body", "paragraphs": body_paragraphs},
            {
                "type": "section", "heading": points_heading,
                "subsections": [
                    {"heading": point_one_heading, "paragraphs": point_one_paragraphs},
                    {"heading": point_two_heading, "paragraphs": point_two_paragraphs},
                ],
            },
            {"type": "section", "heading": "In One Line", "paragraphs": in_one_line_paragraphs},
        ],
    }


# ============================================================
# ブロック3: 採用済みTTS instruction/payloadの再利用(新規定義なし)
# ============================================================
def build_style_prefix() -> str:
    """er002_common.build_style_prefix()をそのまま返す(Preview・B1本文
    共通、Preview専用の追加指示は作らない)。"""
    return common.build_style_prefix()


def build_tts_prompt(text: str, style_prefix: Optional[str] = None) -> str:
    prefix = style_prefix if style_prefix is not None else build_style_prefix()
    return prefix + text
