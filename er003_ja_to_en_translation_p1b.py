# ============================================================
# er003_ja_to_en_translation_p1b.py
# ER-003-P1B: Natural English Sourceの固定構造付き再翻訳検証
# ============================================================
# P1(制約なし自然英訳)で、日英整合性・自然さは合格したが、「二つの
# 切り口」と「一言まとめ」の英語表現が記事ごとに揺れた(音声リスナーが
# 現在位置を把握するためのナビゲーション表現の問題)。P1Bでは、P1の
# 自然な英訳方式を維持したまま、次の固定構造だけを追加する:
#   - `## Today's {記事ごとの短いテーマ表現} Points`
#   - `### Point One: {切り口見出し}`
#   - `### Point Two: {切り口見出し}`
#   - `## In One Line`
# 中央のテーマ表現・各Pointの切り口見出しはtranslator自身が記事内容に
# 応じて作る(Claude Codeが辞書化・固定・後処理で書き換えることはしない)。
#
# P1から変更しないもの(再利用・再実装しない):
#   - er003_ja_to_en_translation.TRANSLATOR_MODEL/TRANSLATOR_REASONING_EFFORT
#   - er003_ja_to_en_translation.TRANSLATOR_DEVELOPER_MESSAGE
#   - er003_ja_to_en_translation.make_translator_fn(Web検索なし・
#     Structured Outputなしの実体はそのまま)
#   - er003_ja_to_en_translation.make_fidelity_qa_fn/
#     build_fidelity_qa_prompt/run_json_response_gate/
#     parse_and_validate_fidelity_qa_output(日英整合性QAは完全に不変)
#   - er003_ja_to_en_translation.make_difficulty_assessment_fn/
#     build_difficulty_prompt/parse_and_validate_difficulty_output/
#     compute_difficulty_metrics(難易度評価・決定的指標も完全に不変)
#   - er003_ja_to_en_translation.APPROVED_ARTICLE_SOURCE_PATHS(P1と
#     完全に同一の日本語原稿を使う。P1英訳を入力にはしない)
#
# P1から変更するのはtranslator user promptだけ(固定構造の指示を追加)。
# 固定構造はプロダクト上の明示要件のため、P1と異なり、構造ゲート不合格
# の場合は同一条件で最大1回だけ再試行する(内容品質を理由とした再試行
# は行わない)。

from __future__ import annotations

import re
from typing import Callable, Optional

import er003_ja_to_en_translation as er003

EXPERIMENT_VERSION = "ER-003-P1B"
BASE_EXPERIMENT_VERSION = "ER-003-P1"

# P1から不変のまま再利用(再定義しない)
TRANSLATOR_MODEL = er003.TRANSLATOR_MODEL
TRANSLATOR_REASONING_EFFORT = er003.TRANSLATOR_REASONING_EFFORT
TRANSLATOR_DEVELOPER_MESSAGE = er003.TRANSLATOR_DEVELOPER_MESSAGE

TRANSLATOR_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/translator_prompt_template_p1b.txt"

# P1と完全に同一(翻訳元をP1と独立に定義しない)
APPROVED_ARTICLE_SOURCE_PATHS = er003.APPROVED_ARTICLE_SOURCE_PATHS
ARTICLE_TOPICS = er003.ARTICLE_TOPICS


def load_approved_japanese_article(topic_id: str) -> str:
    return er003.load_approved_japanese_article(topic_id)


# ============================================================
# ブロック1: P1B translatorプロンプト構築(固定構造指示を追加)
# ============================================================
def load_translator_prompt_template_p1b(path: str = TRANSLATOR_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_translator_user_message_p1b(approved_japanese_article: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_translator_prompt_template_p1b()
    return template.format(approved_japanese_article=approved_japanese_article)


# make_translator_fnはP1の実体をそのまま使う(Web検索なし・Structured
# Outputなしの制約はprompt文面に依存しないため、再実装不要)。
make_translator_fn = er003.make_translator_fn


# ============================================================
# ブロック2: 固定構造ゲート(P1B新規)
# ============================================================
_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```")
_HEADING_RE = re.compile(r"(?m)^(#{2,3})[ \t]+(.*)$")
_TODAYS_POINTS_RE = re.compile(r"^Today's\s+(.+?)\s+Points$")
_POINT_ONE_RE = re.compile(r"^Point One:\s*(.*)$")
_POINT_TWO_RE = re.compile(r"^Point Two:\s*(.*)$")
_IN_ONE_LINE_RE = re.compile(r"^In One Line$")

_DUPLICATION_TAIL_WORDS = ("point", "points")


def _ends_with_terminal_punctuation_heuristic(text: str) -> bool:
    stripped = text.strip()
    return bool(re.search(r"[.!?\"'”。！？)]\s*$", stripped))


def validate_p1b_structure(raw_text: str) -> dict:
    """固定構造(Today's...Points / Point One / Point Two / In One Line)を
    検証する。比較・監査のための判定のみを行い、見出しの追加・修正・
    Pointの選択統合は一切行わない。コードフェンス内は解析対象から除く。"""
    reasons = []
    stripped = _CODE_FENCE_RE.sub(" ", raw_text or "")

    headings = [
        {"level": len(m.group(1)), "text": m.group(2).strip(), "start": m.start(), "end": m.end()}
        for m in _HEADING_RE.finditer(stripped)
    ]

    def body_between(idx: int) -> str:
        h = headings[idx]
        next_start = headings[idx + 1]["start"] if idx + 1 < len(headings) else len(stripped)
        return stripped[h["end"]:next_start].strip()

    todays_matches = [(i, h) for i, h in enumerate(headings) if h["level"] == 2 and _TODAYS_POINTS_RE.match(h["text"])]
    point_one_matches = [(i, h) for i, h in enumerate(headings) if h["level"] == 3 and _POINT_ONE_RE.match(h["text"])]
    point_two_matches = [(i, h) for i, h in enumerate(headings) if h["level"] == 3 and _POINT_TWO_RE.match(h["text"])]
    in_one_line_matches = [(i, h) for i, h in enumerate(headings) if h["level"] == 2 and _IN_ONE_LINE_RE.match(h["text"])]

    ok = True
    todays_points_heading = None
    point_one_heading = None
    point_two_heading = None

    if len(todays_matches) != 1:
        reasons.append(f"'Today's ... Points'見出しが1件でない(実際: {len(todays_matches)}件)")
        ok = False
    else:
        idx, h = todays_matches[0]
        todays_points_heading = h["text"]
        phrase = _TODAYS_POINTS_RE.match(h["text"]).group(1).strip()
        if not phrase:
            reasons.append("'Today's'と'Points'の間のテーマ表現が空")
            ok = False
        else:
            last_word = phrase.split()[-1].lower().strip(".,!?")
            if last_word in _DUPLICATION_TAIL_WORDS:
                reasons.append(f"'Point Points'的な不自然な重複がある(テーマ表現: {phrase!r})")
                ok = False

    if len(point_one_matches) != 1:
        reasons.append(f"'Point One:'見出しが1件でない(実際: {len(point_one_matches)}件)")
        ok = False
    else:
        idx, h = point_one_matches[0]
        point_one_heading = h["text"]
        angle = _POINT_ONE_RE.match(h["text"]).group(1).strip()
        if not angle:
            reasons.append("Point Oneの切り口見出しが空")
            ok = False
        if not body_between(idx):
            reasons.append("Point One本文が空")
            ok = False

    if len(point_two_matches) != 1:
        reasons.append(f"'Point Two:'見出しが1件でない(実際: {len(point_two_matches)}件)")
        ok = False
    else:
        idx, h = point_two_matches[0]
        point_two_heading = h["text"]
        angle = _POINT_TWO_RE.match(h["text"]).group(1).strip()
        if not angle:
            reasons.append("Point Twoの切り口見出しが空")
            ok = False
        if not body_between(idx):
            reasons.append("Point Two本文が空")
            ok = False

    if len(point_one_matches) == 1 and len(point_two_matches) == 1:
        if point_one_matches[0][0] >= point_two_matches[0][0]:
            reasons.append("Point OneがPoint Twoより前にない")
            ok = False

    in_one_line_present = len(in_one_line_matches) == 1
    if len(in_one_line_matches) != 1:
        reasons.append(f"'In One Line'見出しが1件でない(実際: {len(in_one_line_matches)}件)")
        ok = False
    else:
        idx, h = in_one_line_matches[0]
        if not body_between(idx):
            reasons.append("In One Line本文が空")
            ok = False

    if len(in_one_line_matches) == 1 and len(point_two_matches) == 1:
        if in_one_line_matches[0][0] <= point_two_matches[0][0]:
            reasons.append("In One LineがPoint Twoより後にない")
            ok = False

    seen = {}
    for h in headings:
        key = (h["level"], h["text"])
        seen[key] = seen.get(key, 0) + 1
    duplicate_headings = [{"level": lvl, "text": txt, "count": c} for (lvl, txt), c in seen.items() if c > 1]
    if duplicate_headings:
        reasons.append(f"見出しが重複している: {duplicate_headings}")
        ok = False

    if not _ends_with_terminal_punctuation_heuristic(stripped):
        reasons.append("記事本文が途中で切れている可能性がある(終端記号なし)")
        ok = False

    return {
        "status": "TRANSLATION_STRUCTURE_PASS" if ok else "TRANSLATION_STRUCTURE_INVALID",
        "reasons": reasons,
        "todays_points_heading": todays_points_heading,
        "point_one_heading": point_one_heading,
        "point_two_heading": point_two_heading,
        "in_one_line_present": in_one_line_present,
    }


MAX_STRUCTURE_RETRY_ATTEMPTS = 2  # 初回 + (技術的失敗 または 構造不適合)時の再試行1回のみ


def run_translator_structure_gate(
    make_translator_factory: Callable[[], Callable],
    max_attempts: int = MAX_STRUCTURE_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、または固定構造(Today's...Points/Point One/Point Two/
    In One Line)の不適合のいずれかであれば、同一条件(同一prompt・同一
    日本語原稿)で最大1回だけ再試行する。内容品質を理由とした再試行は
    行わない。

    戻り値: (raw_text, final_status, attempts_detail, model_id, response_id,
             search_usage, sources)
    final_status: "TRANSLATION_STRUCTURE_PASS" / "TRANSLATION_STRUCTURE_INVALID"
                  / "TECHNICAL_GENERATION_FAILED"
    """
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        translator_fn = make_translator_factory()
        try:
            raw_text, model_id, response_id, search_usage, sources = translator_fn()
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

        structure = validate_p1b_structure(raw_text)
        attempts_detail.append({
            "content_attempt": attempt, "status": structure["status"],
            "structure_reasons": structure["reasons"], "search_usage": search_usage, "sources": sources,
            "raw_text": raw_text, "model": model_id, "response_id": response_id,
            "todays_points_heading": structure["todays_points_heading"],
            "point_one_heading": structure["point_one_heading"],
            "point_two_heading": structure["point_two_heading"],
            "in_one_line_present": structure["in_one_line_present"],
        })
        if structure["status"] == "TRANSLATION_STRUCTURE_PASS":
            return raw_text, "TRANSLATION_STRUCTURE_PASS", attempts_detail, model_id, response_id, search_usage, sources
        if attempt < max_attempts:
            continue
        return raw_text, "TRANSLATION_STRUCTURE_INVALID", attempts_detail, model_id, response_id, search_usage, sources

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None, None, None
