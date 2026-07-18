# ============================================================
# er002_ja_free_markdown_restore_r2.py
# ER-002-v1.2M-R2: 重要ポイント2件の構造ゲート実装
# ============================================================
# ER-002-v1.2M-R1(自由Markdown・完全fact registryをwriterへ渡さない・
# gpt-5.6-sol・reasoning effort=high)は変更しない。このモジュールは
# er002_ja_free_markdown_restore.py(R1)の生成関数・事実QA関数をそのまま
# 再利用し、生成後の決定的な構造バリデーション(レベル3見出しがちょうど
# 2件で、各Pointに空でない本文があること)と、構造不適合時の最大1回の
# 再生成ロジックだけを追加する。
#
# 主観的な内容品質(面白さ・勢い等)のbest-of選択ではない。構造仕様
# (Point数)への機械的な適合再試行のみを行う。

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

import er002_ja_free_markdown_restore as restore

EXPERIMENT_VERSION = "ER-002-v1.2M-R2"
BASE_EXPERIMENT_VERSION = "ER-002-v1.2M-R1"

# R1の凍結プロンプト(er002_v1_2m_restore_briefs/writer_prompt_template.txt)は
# 変更しない。R2ではこのファイルの末尾へ1文だけを追加した別ファイルを使う。
R2_PROMPT_TEMPLATE_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template_r2.txt"
POINT_COUNT_INSTRUCTION_SENTENCE = "ポイント部分には、Markdownの「###」見出しをちょうど2つ置いてください。"


def load_r2_prompt_template(path: str = R2_PROMPT_TEMPLATE_PATH) -> str:
    return restore.load_text_file(path)


def build_writer_user_message_r2(master_full_text: str, concise_news_brief: str, template: Optional[str] = None) -> str:
    template = template if template is not None else load_r2_prompt_template()
    return template.format(master_full_text=master_full_text, concise_news_brief=concise_news_brief)


# ============================================================
# ブロック1: 決定的な構造バリデーション(Point数がちょうど2件か)
# ============================================================
def _strip_code_fences(text: str) -> str:
    """```...```で囲まれたコードフェンス内の文字列を除いたテキストを返す
    (フェンス内の###をPoint見出しとして誤カウントしないため)。"""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


@dataclass
class PointStructureResult:
    status: str  # "STRUCTURE_PASS" / "STRUCTURE_INVALID_POINT_COUNT_OR_BODY"
    h3_count: int
    headings: list = field(default_factory=list)
    reasons: list = field(default_factory=list)


def validate_point_structure(raw_markdown: str) -> PointStructureResult:
    """raw_markdownを一切変更せず、読み取りだけで判定する。タイトル・親見出し・
    一言まとめの表現差では不合格にしない(見出し数と本文の有無だけを見る)。"""
    text = _strip_code_fences(raw_markdown)
    matches = list(re.finditer(r"^#{3}[ \t]*(.*)$", text, flags=re.MULTILINE))
    h3_count = len(matches)

    if h3_count != 2:
        return PointStructureResult(
            status="STRUCTURE_INVALID_POINT_COUNT_OR_BODY", h3_count=h3_count,
            headings=[m.group(1).strip() for m in matches],
            reasons=[f"h3_count_is_{h3_count}_not_2"],
        )

    reasons = []
    headings = []
    for i, m in enumerate(matches):
        heading_text = m.group(1).strip()
        headings.append(heading_text)
        if not heading_text:
            reasons.append(f"point_{i + 1}_heading_empty")

        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        if not body:
            reasons.append(f"point_{i + 1}_body_empty")

    status = "STRUCTURE_PASS" if not reasons else "STRUCTURE_INVALID_POINT_COUNT_OR_BODY"
    return PointStructureResult(status=status, h3_count=h3_count, headings=headings, reasons=reasons)


# ============================================================
# ブロック2: 構造ゲート付き生成(最大1回だけの構造再試行。内容不満での
# 再生成とは別物。技術的失敗(通信障害等)はR1既存のrun_generation_with_
# technical_retryが1回だけ吸収する)
# ============================================================
MAX_STRUCTURE_CONTENT_ATTEMPTS = 2  # 初回 + 構造不適合時の再生成1回のみ


def run_generation_with_structure_gate(
    make_generation_fn: Callable[[], Callable],
    max_structure_attempts: int = MAX_STRUCTURE_CONTENT_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """make_generation_fn: 呼ぶたびに新しいgeneration_fn(同一条件・新規API
    呼び出し用のクロージャ)を返すファクトリ。

    戻り値: (final_raw_text, final_status, attempts_detail, model_id, response_id)
    final_status: "STRUCTURE_PASS" / "STRUCTURE_INVALID" / "TECHNICAL_GENERATION_FAILED"
    attempts_detailの各要素にはraw_text(証跡)を含む。"""
    attempts_detail = []
    last_raw_text = None
    last_model_id = None
    last_response_id = None

    for attempt in range(1, max_structure_attempts + 1):
        gen_fn = make_generation_fn()
        raw_text, model_id, response_id, tech_attempts, gen_ok, gen_err = restore.run_generation_with_technical_retry(
            gen_fn, sleep_fn=sleep_fn)

        if not gen_ok:
            attempts_detail.append({
                "content_attempt": attempt, "generation_status": "TECHNICAL_GENERATION_FAILED",
                "technical_attempts": tech_attempts, "error": gen_err, "raw_text": None,
            })
            return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None

        structure = validate_point_structure(raw_text)
        last_raw_text, last_model_id, last_response_id = raw_text, model_id, response_id
        attempts_detail.append({
            "content_attempt": attempt, "generation_status": "OK", "technical_attempts": tech_attempts,
            "model": model_id, "response_id": response_id,
            "structure_status": structure.status, "h3_count": structure.h3_count,
            "headings": structure.headings, "reasons": structure.reasons, "raw_text": raw_text,
        })
        if structure.status == "STRUCTURE_PASS":
            return raw_text, "STRUCTURE_PASS", attempts_detail, model_id, response_id

    return last_raw_text, "STRUCTURE_INVALID", attempts_detail, last_model_id, last_response_id
