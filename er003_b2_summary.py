# ============================================================
# er003_b2_summary.py
# ER-003-P2B: B2向け「Before You Listen」概要パイロット
# ============================================================
# ER-003-P2で確定済みのB2 reading copy(b2_version_raw.md)3記事のみを
# 入力とし、本編を聞く前に流す短い英語概要(固定見出し`## Before You
# Listen`)を生成する。日本語原稿・Natural English Source・P1/P1Bの生
# 応答・Web検索結果・fact registry・fidelity QA・difficulty QA・Key
# Words候補・TTS情報・英語マスター・阪神マスター・他記事の概要や本文は
# summary generatorへ一切渡さない。
#
# 概要は「短い要約」ではなく、本文を聞くための地図として設計する。結論・
# 意外な展開・二つのPointの具体的な答え・In One Lineの内容は明かさない。
#
# 固定構造・語数(25〜35語)・文数(2または3文)はプロダクト上の明示要件
# のため、これらの不適合のみ最大1回だけ同一条件で再試行する。内容品質
# (面白さ、B1相当かどうか、ネタバレの可能性等)を理由とした自動再生成
# は行わない。
#
# 概要整合性QAはgeneratorとは別の新規API実行として行う。QA結果を理由と
# した概要の自動再生成・書き換えは行わない。
#
# 再利用するもの(再実装しない):
#   - er003_ja_to_en_translation.TRANSLATOR_MODEL/TRANSLATOR_REASONING_
#     EFFORT("gpt-5.6-sol"/"high"。P1/P1B/B2 adapterと不変)
#   - er003_ja_to_en_translation.make_translator_fn(Web検索なし・
#     Structured Outputなしの実体はそのまま。developer_messageだけ
#     差し替える)
#   - er003_ja_to_en_translation.run_json_response_gate(概要QA用。
#     技術的失敗+JSON解析/スキーマ不適合を最大1回再試行する汎用ゲート)
#   - er003_ja_to_en_translation.compute_word_count/split_sentences/
#     compute_estimated_reading_times(ER-003-P2Aで修正済みの決定的な
#     語数・文分割・推定読み上げ時間ロジック)
#   - er003_ja_to_en_translation.sha256_text

from __future__ import annotations

import json
import re
from typing import Any, Callable, Optional

import er003_ja_to_en_translation as er003

EXPERIMENT_VERSION = "ER-003-P2B"

# P1/P1B/B2 adapterから不変のまま再利用(再定義しない)
SUMMARY_MODEL = er003.TRANSLATOR_MODEL  # "gpt-5.6-sol"
SUMMARY_REASONING_EFFORT = er003.TRANSLATOR_REASONING_EFFORT  # "high"
SUMMARY_DEVELOPER_MESSAGE = "英語ポッドキャスト本編の前に流す、短く分かりやすい英語概要を作成してください。"

SUMMARY_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_summary_prompt_template.txt"
SUMMARY_QA_PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b2_summary_qa_prompt_template.txt"

# ER-003-P2で確定済みのB2 reading copyのみを入力とする。
B2_INPUT_PATHS = {
    "A01": "er003_output/p2/A01/b2_version_raw.md",
    "A02": "er003_output/p2/A02/b2_version_raw.md",
    "ADD03": "er003_output/p2/ADD03/b2_version_raw.md",
}
ARTICLE_TOPICS = er003.ARTICLE_TOPICS

# run_json_response_gateは用途に依存しない汎用実装のため、そのまま再利用する。
run_json_response_gate = er003.run_json_response_gate


def load_approved_b2_article(topic_id: str) -> str:
    with open(B2_INPUT_PATHS[topic_id], encoding="utf-8") as f:
        return f.read()


# ============================================================
# ブロック1: summary generatorプロンプト構築・API呼び出し
# ============================================================
def load_summary_prompt_template(path: str = SUMMARY_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_summary_user_message(approved_b2_article: str, template: Optional[str] = None) -> str:
    """テンプレート中の{概要本文}はモデルへの出力形式の指示であり、
    Pythonの置換対象ではないため、.format()ではなく単一プレースホルダー
    だけを対象にした.replace()を使う(P1B/B2 adapterと同じ理由)。"""
    template = template if template is not None else load_summary_prompt_template()
    return template.replace("{approved_b2_article}", approved_b2_article)


def make_summary_generator_fn(user_message: str, client: Optional[Any] = None):
    """er003.make_translator_fnをそのまま再利用する(Web検索なし・
    Structured Outputなしの実体は完全に同一。developer_messageだけ
    summary generator用に差し替える)。"""
    return er003.make_translator_fn(
        user_message, client=client, model=SUMMARY_MODEL,
        reasoning_effort=SUMMARY_REASONING_EFFORT, developer_message=SUMMARY_DEVELOPER_MESSAGE,
    )


# ============================================================
# ブロック2: 固定構造・語数・文数ゲート(P2B新規)
# ============================================================
FIXED_HEADING = "Before You Listen"
SUMMARY_MIN_WORDS = 25
SUMMARY_MAX_WORDS = 35
SUMMARY_MIN_SENTENCES = 2
SUMMARY_MAX_SENTENCES = 3

_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```")
_HEADING_RE = re.compile(r"(?m)^(#{1,6})[ \t]+(.*)$")
_BULLET_LINE_RE = re.compile(r"(?m)^[ \t]*[-*+][ \t]+")
_NON_ENGLISH_CHAR_RE = re.compile(r"[぀-ヿ一-鿿＀-￯]")

# ER-003-P2C: 概要はPodcastへ一緒に入っていく語り口にするため、第一文は
# ナレーターとリスナーを含む"We"を主語にした"We'll look at ..."で始める
# (ASCII/typographicどちらのアポストロフィも同一扱い)。教材紹介の
# ような"This episode ..."的な開始表現は禁止する。
REQUIRED_OPENING_RE = re.compile(r"^We['’]ll look at\b")
FORBIDDEN_OPENING_PREFIXES = ("This episode", "This lesson", "This story", "In this episode", "The episode")


def _ends_with_terminal_punctuation_heuristic(text: str) -> bool:
    stripped = text.strip()
    return bool(re.search(r"[.!?\"'”’)]\s*$", stripped))


def validate_summary_structure(raw_text: str) -> dict:
    """固定見出し'## Before You Listen'が正確に1件であること、見出し
    以外が英語本文のみであること、語数25〜35語・文数2〜3文であることを
    検証する。比較・監査のための判定のみを行い、見出しの追加・修正や
    本文の書き換えは一切行わない。コードフェンス内は解析対象から除く。"""
    reasons = []
    raw_text = raw_text or ""
    stripped = _CODE_FENCE_RE.sub(" ", raw_text)

    headings = [
        {"level": len(m.group(1)), "text": m.group(2).strip(), "start": m.start(), "end": m.end()}
        for m in _HEADING_RE.finditer(stripped)
    ]

    heading_matches = [(i, h) for i, h in enumerate(headings) if h["level"] == 2 and h["text"] == FIXED_HEADING]

    ok = True
    body = ""
    if len(heading_matches) != 1:
        reasons.append(f"'## {FIXED_HEADING}'見出しが1件でない(実際: {len(heading_matches)}件)")
        ok = False
    else:
        idx, h = heading_matches[0]
        next_start = headings[idx + 1]["start"] if idx + 1 < len(headings) else len(stripped)
        body = stripped[h["end"]:next_start].strip()

    other_headings = [h for h in headings if not (h["level"] == 2 and h["text"] == FIXED_HEADING)]
    if other_headings:
        reasons.append(f"'## {FIXED_HEADING}'以外の見出しが存在する: {[h['text'] for h in other_headings]}")
        ok = False

    if _BULLET_LINE_RE.search(body):
        reasons.append("箇条書きが含まれている")
        ok = False

    if _CODE_FENCE_RE.search(raw_text):
        reasons.append("コードフェンスが含まれている")
        ok = False

    word_count = 0
    sentence_count = 0
    sentences: list = []

    if not body:
        reasons.append("概要本文が空")
        ok = False
    else:
        if _NON_ENGLISH_CHAR_RE.search(body):
            reasons.append("英語以外の説明(日本語等)が混入している可能性がある")
            ok = False
        plain_body = er003.article_gen.strip_markdown_symbols(body)
        word_count = er003.compute_word_count(plain_body)
        sentences = er003.split_sentences(plain_body)
        sentence_count = len(sentences)

        if word_count < SUMMARY_MIN_WORDS or word_count > SUMMARY_MAX_WORDS:
            reasons.append(
                f"概要本文の語数が{SUMMARY_MIN_WORDS}〜{SUMMARY_MAX_WORDS}語の範囲外(実際: {word_count}語)")
            ok = False

        if sentence_count < SUMMARY_MIN_SENTENCES or sentence_count > SUMMARY_MAX_SENTENCES:
            reasons.append(
                f"文数が{SUMMARY_MIN_SENTENCES}〜{SUMMARY_MAX_SENTENCES}文の範囲外(実際: {sentence_count}文)")
            ok = False

        if not _ends_with_terminal_punctuation_heuristic(body):
            reasons.append("概要本文が途中で切れている可能性がある(終端記号なし)")
            ok = False

    opening_ok = True
    if sentences:
        first_sentence = sentences[0]
        opening_ok = bool(REQUIRED_OPENING_RE.match(first_sentence))
        if not opening_ok:
            reasons.append(
                f"第一文が'We'll look at ...'(教材紹介的な'This episode ...'等は不可)で"
                f"始まっていない(実際の書き出し: {first_sentence[:40]!r})")
            ok = False

    return {
        "status": "B2_SUMMARY_STRUCTURE_PASS" if ok else "B2_SUMMARY_STRUCTURE_INVALID",
        "reasons": reasons,
        "heading_present": len(heading_matches) == 1,
        "opening_ok": opening_ok,
        "body": body,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "sentences": sentences,
    }


MAX_STRUCTURE_RETRY_ATTEMPTS = 2  # 初回 + (技術的失敗 または 構造/語数/文数不適合)時の再試行1回のみ


def run_summary_structure_gate(
    make_generator_factory: Callable[[], Callable],
    max_attempts: int = MAX_STRUCTURE_RETRY_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """技術的失敗、または固定構造・語数(25〜35語)・文数(2〜3文)の
    いずれかの不適合であれば、同一条件(同一model・同一reasoning
    effort・同一prompt・同一B2本文)で最大1回だけ再試行する。内容品質
    (面白さ、B1相当かどうか、ネタバレの可能性、QA結果等)を理由とした
    再試行・再生成は行わない。再試行時に追加のエラーメッセージや修正
    指示をpromptへ加えない。

    戻り値: (raw_text, final_status, attempts_detail, model_id, response_id)
    final_status: "B2_SUMMARY_STRUCTURE_PASS" / "B2_SUMMARY_STRUCTURE_INVALID"
                  / "TECHNICAL_GENERATION_FAILED"
    """
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        generator_fn = make_generator_factory()
        try:
            raw_text, model_id, response_id, search_usage, sources = generator_fn()
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

        structure = validate_summary_structure(raw_text)
        attempts_detail.append({
            "attempt": attempt, "status": structure["status"], "structure_reasons": structure["reasons"],
            "raw_text": raw_text, "model": model_id, "response_id": response_id,
            "word_count": structure["word_count"], "sentence_count": structure["sentence_count"],
        })
        if structure["status"] == "B2_SUMMARY_STRUCTURE_PASS":
            return raw_text, "B2_SUMMARY_STRUCTURE_PASS", attempts_detail, model_id, response_id
        if attempt < max_attempts:
            continue
        return raw_text, "B2_SUMMARY_STRUCTURE_INVALID", attempts_detail, model_id, response_id

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None


# ============================================================
# ブロック3: 決定的な指標(Pythonで計測。LLMには数えさせない)
# ============================================================
def compute_summary_metrics(raw_text: str) -> dict:
    """見出しを除く概要本文のみを対象に計測する。見出し込み総語数は
    別途保存する(見出し自体は語数25〜35語の対象に含めない)。sentence
    splitterはER-003-P2Aで修正・確定したものをそのまま使う。"""
    structure = validate_summary_structure(raw_text)
    body = structure["body"]
    plain_with_heading = er003.article_gen.strip_markdown_symbols(raw_text or "")
    sentence_word_counts = [er003.compute_word_count(s) for s in structure["sentences"]]

    return {
        "word_count": structure["word_count"],
        "total_word_count_including_heading": er003.compute_word_count(plain_with_heading),
        "sentence_count": structure["sentence_count"],
        "sentence_word_counts": sentence_word_counts,
        "avg_words_per_sentence": (
            round(sum(sentence_word_counts) / len(sentence_word_counts), 2) if sentence_word_counts else 0.0
        ),
        "longest_sentence_word_count": max(sentence_word_counts) if sentence_word_counts else 0,
        "estimated_reading_time_minutes": er003.compute_estimated_reading_times(structure["word_count"]),
        "sentences": structure["sentences"],
        "body": body,
    }


# ============================================================
# ブロック4: 概要QA(generatorとは別の新規API実行、Web検索なし)
# ============================================================
SUMMARY_QA_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")

SUMMARY_QA_JSON_SCHEMA = {
    "name": "b2_summary_qa",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": list(SUMMARY_QA_VERDICTS)},
            "unsupported_additions": {"type": "array", "items": {"type": "string"}},
            "contradictions": {"type": "array", "items": {"type": "string"}},
            "spoilers": {"type": "array", "items": {"type": "string"}},
            "point_answer_leakage": {"type": "array", "items": {"type": "string"}},
            "in_one_line_leakage": {"type": "array", "items": {"type": "string"}},
            "above_b1_candidates": {"type": "array", "items": {"type": "string"}},
            "unexplained_technical_terms": {"type": "array", "items": {"type": "string"}},
            "standalone_comprehension_notes": {"type": "array", "items": {"type": "string"}},
            "information_overload_notes": {"type": "array", "items": {"type": "string"}},
            "information_gap_notes": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["verdict", "unsupported_additions", "contradictions", "spoilers",
                     "point_answer_leakage", "in_one_line_leakage", "above_b1_candidates",
                     "unexplained_technical_terms", "standalone_comprehension_notes",
                     "information_overload_notes", "information_gap_notes", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

_SUMMARY_QA_REQUIRED_FIELD_TYPES = {
    "verdict": str,
    "unsupported_additions": list,
    "contradictions": list,
    "spoilers": list,
    "point_answer_leakage": list,
    "in_one_line_leakage": list,
    "above_b1_candidates": list,
    "unexplained_technical_terms": list,
    "standalone_comprehension_notes": list,
    "information_overload_notes": list,
    "information_gap_notes": list,
    "notes": str,
}
_SUMMARY_QA_STRING_LIST_FIELDS = tuple(k for k, v in _SUMMARY_QA_REQUIRED_FIELD_TYPES.items() if v is list)


def parse_and_validate_summary_qa_output(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict):
        raise er003.QaSchemaError("トップレベルがJSONオブジェクトではありません")
    for field_name, expected_type in _SUMMARY_QA_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise er003.QaSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise er003.QaSchemaError(f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")
    for list_field in _SUMMARY_QA_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise er003.QaSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")
    if parsed["verdict"] not in SUMMARY_QA_VERDICTS:
        raise er003.QaSchemaError(
            f"verdictは{SUMMARY_QA_VERDICTS}のいずれかである必要があります(実際: {parsed['verdict']!r})")
    return parsed


def load_summary_qa_prompt_template(path: str = SUMMARY_QA_PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_summary_qa_prompt(b2_article: str, summary: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_summary_qa_prompt_template()
    return template.format(b2_article=b2_article, summary=summary)


def make_summary_qa_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = SUMMARY_MODEL,
    reasoning_effort: str = SUMMARY_REASONING_EFFORT,
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
            text={"format": {"type": "json_schema", **SUMMARY_QA_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("概要QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn
