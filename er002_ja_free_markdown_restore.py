# ============================================================
# er002_ja_free_markdown_restore.py
# ER-002-v1.2M-R1: ChatGPT生成条件の一括復元(自由Markdown生成)
# ============================================================
# ER-002-v1.2M-J1(Structured Output・完全fact registryをwriterへ投入)が
# ユーザー品質評価で不合格となったため、以下3条件を一括して過去のChatGPT
# 生成条件へ近づける復元パッケージを実装する:
#   1. writer入力から完全fact registryを外し、短いconcise briefだけを渡す
#   2. Structured Outputをやめ、記事全体を自由Markdownとして生成する
#   3. GPT-5.6 Thinkingに対応する公式APIモデル(gpt-5.6-sol)を使用する
#
# 以下は一切importしない・再利用しない(ER-002-v1.2M-R1の指示どおり):
#   - er002_editorial_common.py / er002_editorial_angle_adapter.py /
#     er002_editorial_runner.py(Editorial Brief・アングル生成・評価)
#   - er002_ja_master_imitation.pyのbuild_prompt/MINIMAL_JA_GENERATION_
#     PROMPT_TEMPLATE/JA_ARTICLE_JSON_SCHEMA/make_ja_article_generation_fn/
#     validate_structure/EVALUATION_REASONS(J1のwriter入力組み立てと
#     Structured Outputスキーマそのもの)
# 以下だけはer002_ja_master_imitation.pyから再利用する(既存の最小事実QA):
#   - build_minimal_fact_qa_prompt / evaluate_fact_qa / classify_fact_qa /
#     MINIMAL_FACT_QA_PROMPT_TEMPLATE / MINIMAL_FACT_QA_REQUIRED_FIELDS

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from dotenv import load_dotenv

import er002_common as common
import er002_ja_master_imitation as jami  # 事実QAのみ再利用(writer入力組み立ては再利用しない)

EXPERIMENT_VERSION = "ER-002-v1.2M-R1"
BASE_EXPERIMENT_VERSION = "ER-002-v1.2M-JA"

# ============================================================
# ブロック1: writerモデル設定(D1/J1確認済みの公式APIモデルID・
# 事前検証済みのreasoning effort値のみを使う。推測でハードコードしない)
# ============================================================
WRITER_MODEL = "gpt-5.6-sol"
WRITER_MODEL_FAMILY = "GPT-5.6 Sol"
WRITER_MODEL_INTENDED_MATCH = "GPT-5.6 Thinkingに最も近い公式APIモデル(OpenAI公式発表で「flagship」と説明されるGPT-5.6ファミリーの最上位モデル)"
WRITER_MODEL_EXACT_CHATGPT_PARITY = "NOT_GUARANTEED"
WRITER_REASONING_EFFORT = "high"  # OpenAI公式Reasoning modelsガイドで確認済みの正式な値(none/low/medium/high/xhigh/max)
NEUTRAL_DEVELOPER_MESSAGE = "日本語の記事を作成してください。"

PROMPT_TEMPLATE_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template.txt"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# ブロック2: 入力読み込み(マスター・concise brief・プロンプトテンプレート)
# ============================================================
def load_text_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_prompt_template(path: str = PROMPT_TEMPLATE_PATH) -> str:
    return load_text_file(path)


def build_writer_user_message(master_full_text: str, concise_news_brief: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_prompt_template()
    return template.format(master_full_text=master_full_text, concise_news_brief=concise_news_brief)


# ============================================================
# ブロック3: 自由Markdown生成(Structured Output不使用。response_format等を
# 一切渡さない。Responses APIへdeveloper/userメッセージのみを渡す)
# ============================================================
class GenerationEmptyOrBrokenError(RuntimeError):
    """応答が空、または明らかに壊れている場合に送出する(技術的失敗として
    1回だけ再試行の対象になる。内容不満とは無関係)。"""


def make_free_markdown_generation_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = WRITER_MODEL,
    reasoning_effort: str = WRITER_REASONING_EFFORT,
    developer_message: str = NEUTRAL_DEVELOPER_MESSAGE,
):
    if client is None:
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def generation_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise GenerationEmptyOrBrokenError("応答が空です")
        return text, response.model, response.id

    generation_fn.model = model
    generation_fn.reasoning_effort = reasoning_effort
    generation_fn.developer_message = developer_message
    generation_fn.response_format_used = False
    return generation_fn


MAX_GENERATION_TECHNICAL_RETRY = 1  # 通信障害・API一時障害・空応答・明らかな途中切れの場合のみ、同一条件で1回だけ


def run_generation_with_technical_retry(
    generation_fn: Callable[[], tuple],
    max_technical_retry: int = MAX_GENERATION_TECHNICAL_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """内容不満での再生成は行わない。技術的理由(通信障害/空応答/明らかな
    途中切れ)のときだけ、同一条件(モデル・reasoning・プロンプト)で
    1回だけ再試行する。"""
    last_error = None
    for attempt in range(1, max_technical_retry + 2):
        try:
            raw_text, model_id, response_id = generation_fn()
            return raw_text, model_id, response_id, attempt, True, None
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            if attempt <= max_technical_retry:
                if sleep_fn:
                    sleep_fn(2)
                continue
    return None, None, None, max_technical_retry + 1, False, last_error


# ============================================================
# ブロック4: 最小構造抽出(読み取り専用。raw Markdownを一切変更しない。
# 抽出失敗はFAILEDとして記録するだけで、記事は保持し不合格化しない)
# ============================================================
ONE_LINE_SUMMARY_KEYWORDS = ["一言で", "一言まとめ", "まとめると"]


@dataclass
class StructureExtractionResult:
    status: str  # "OK" / "FAILED"
    title_candidate: Optional[str] = None
    heading_candidates: list = field(default_factory=list)
    heading_candidate_count: int = 0
    one_line_summary_candidate: Optional[str] = None
    has_two_heading_candidates: bool = False
    has_one_line_summary_candidate: bool = False


def extract_structure(raw_markdown: str) -> StructureExtractionResult:
    """title/本文/二見出し/一言まとめ相当の結びを機械抽出する。抽出処理は
    raw_markdownを読むだけで、一切書き換えない(呼び出し元もこの関数の
    戻り値でraw_markdownを上書きしてはならない)。"""
    stripped_full = raw_markdown.strip("\n")
    lines = stripped_full.split("\n")

    title_candidate = None
    for line in lines:
        s = line.strip()
        if s:
            title_candidate = s.lstrip("#").strip()
            break

    all_headings = re.findall(r"^#{1,6}\s*(.+)$", raw_markdown, flags=re.MULTILINE)
    if all_headings and title_candidate and all_headings[0].strip() == title_candidate:
        heading_candidates = all_headings[1:]
    else:
        heading_candidates = all_headings

    one_line_summary_candidate = None
    for kw in ONE_LINE_SUMMARY_KEYWORDS:
        idx = raw_markdown.find(kw)
        if idx != -1:
            one_line_summary_candidate = raw_markdown[idx:idx + 200].strip()
            break
    if one_line_summary_candidate is None and lines:
        # 明示的なキーワードが無い場合、末尾の非空行を結び候補とする(あくまで候補)
        for line in reversed(lines):
            s = line.strip()
            if s:
                one_line_summary_candidate = s
                break

    has_two = len(heading_candidates) >= 2
    has_summary = one_line_summary_candidate is not None
    status = "OK" if (title_candidate and has_two) else "FAILED"

    return StructureExtractionResult(
        status=status,
        title_candidate=title_candidate,
        heading_candidates=heading_candidates,
        heading_candidate_count=len(heading_candidates),
        one_line_summary_candidate=one_line_summary_candidate,
        has_two_heading_candidates=has_two,
        has_one_line_summary_candidate=has_summary,
    )


# ============================================================
# ブロック5: 文字数計測(既存ユーティリティの再利用。合否には使わない)
# ============================================================
def compute_character_metrics(raw_markdown: str, master_full_text: str) -> dict:
    total_characters = len(raw_markdown)
    stripped = len(jami._strip_markdown_and_whitespace(raw_markdown))
    master_stripped = len(jami._strip_markdown_and_whitespace(master_full_text))
    ratio = round(stripped / master_stripped, 3) if master_stripped else None
    return {
        "total_characters": total_characters,
        "characters_excluding_whitespace_and_markdown": stripped,
        "ratio_to_master": ratio,
    }


# ============================================================
# ブロック6: 事実QA(既存の最小事実QAをそのまま再利用。QAプロンプト・
# 判定区分・判定範囲は一切変更しない)
# ============================================================
def build_fact_qa_prompt(raw_markdown: str, fact_id_map: dict) -> str:
    return jami.build_minimal_fact_qa_prompt(raw_markdown, fact_id_map)


def evaluate_fact_qa(prompt: str, fact_qa_call_fn: Callable[[str], str], **kwargs) -> dict:
    return jami.evaluate_fact_qa(prompt, fact_qa_call_fn, **kwargs)
