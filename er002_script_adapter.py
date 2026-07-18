# ============================================================
# er002_script_adapter.py
# ER-002-S2-P1: 台本生成アダプター
# ============================================================
# er002_common.run_script_attempts が呼び出す script_write_fn(config)->dict
# インターフェースの背後に、実際の台本生成ロジックを実装する。
#
# generate_test.py は直接import・直接拡張しない。理由(ER-002-S1のer002_runner.py
# 冒頭コメントに記載、ER-002-S0調査結果を踏襲):generate_test.pyはモジュール
# トップレベルでOpenAIクライアントを生成し、--level/--topicのCLI引数が無いと
# SystemExitする構造で、if __name__=="__main__"のガードも無いため、安全に
# importできるライブラリ構造になっていない。
#
# 「同じ情報源から日本語・英語台本を生成する」既存方針は、本リポジトリ内に
# 見当たらなかった(generate_test.pyは英語台本のみを生成しており、日本語台本
# 生成の実装は存在しない)。そのため本アダプターも英語台本のみを生成し、
# 日本語台本生成のポリシーを新規に作らない(script_ja.jsonは今回未使用のまま)。
#
# 「記事ごとの専用プロンプトを作らない」の実装方法: プロンプト文面
# (COMMON_SCRIPT_PROMPT_TEMPLATE)はすべての記事で完全に同一のテンプレート
# であり、記事固有の情報は{topic}/{facts}という差し込み穴だけに限定する。
# 見出し文言("Today's ... Points"の"..."部分)はテンプレートが記事内容から
# 動的に導出するよう指示しているだけで、テンプレート自体は変更しない。

from __future__ import annotations

import hashlib
import json
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

import er002_common as common

MODEL_WRITE = "gpt-5.6-terra"  # generate_test.pyのMODEL_WRITEと同じ品質重視モデル
PROMPT_VERSION = "er002-script-adapter-v1"

COMMON_SCRIPT_PROMPT_TEMPLATE = """You are writing a script for a short English-language audio news segment aimed at Japanese learners of English (intermediate level). This is for LISTENING ONLY - the audience cannot see any images, charts, or screens, so nothing in the script may depend on something being shown visually.

TOPIC:
{topic}

FACTS (do not add any factual claim - name, number, date, or event - that is not present here):
{facts}

Write a script with exactly this structure:
1. A short attention-grabbing title (not a full sentence, no ending punctuation).
2. An opening/body section: several short paragraphs (plain sentences, no headings) that introduce and explain the story in a way that is fully understandable by ear alone.
3. A short heading in the exact pattern "Today's <2-3 word topic-appropriate noun phrase> Points" (choose the noun phrase based on this specific story - do not reuse a generic placeholder word).
4. Exactly two distinct discussion points under that heading, each with its own short sub-heading and 1-3 short paragraphs. The two points MUST cover clearly different aspects of the story (not the same idea reworded) - for example one point might explain what happened and why it matters, and the other might explain what could happen next or a different angle entirely.
5. A final section headed exactly "In One Line" containing a short one-sentence summary of the body content (not a summary of the two points), plus 1-3 additional short closing sentences.

Target length for the WHOLE script (title + body + both points + In One Line, combined) is {target_min}-{target_max} English words. Do not go below {accept_min} or above {accept_max} words under any circumstance.

Do not include any stage directions, acting notes, or instructions about how to perform the narration - only the words to be spoken. Do not reference images, charts, screens, or anything the listener would need to see.

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "title": "...",
  "body_paragraphs": ["...", "..."],
  "points_heading": "Today's ... Points",
  "point_one_heading": "...",
  "point_one_paragraphs": ["...", "..."],
  "point_two_heading": "...",
  "point_two_paragraphs": ["...", "..."],
  "in_one_line_paragraphs": ["...", "..."]
}}"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_prompt(topic_package: dict) -> str:
    return COMMON_SCRIPT_PROMPT_TEMPLATE.format(
        topic=topic_package["topic"],
        facts=topic_package["facts"],
        target_min=common.WORD_COUNT_TARGET_MIN,
        target_max=common.WORD_COUNT_TARGET_MAX,
        accept_min=common.WORD_COUNT_ACCEPT_MIN,
        accept_max=common.WORD_COUNT_ACCEPT_MAX,
    )


def convert_to_er002_schema(raw: dict) -> dict:
    """LLMの自由形式JSON出力を、er002_common.validate_script_structureが
    受け付けるER-002共通台本スキーマ(er001b5_*_script.jsonと同一形式)へ変換する。"""
    required_keys = [
        "title", "body_paragraphs", "points_heading",
        "point_one_heading", "point_one_paragraphs",
        "point_two_heading", "point_two_paragraphs",
        "in_one_line_paragraphs",
    ]
    missing = [k for k in required_keys if k not in raw]
    if missing:
        raise ValueError(f"台本生成モデルの出力に必須キーが不足しています: {missing}")

    return {
        "title": raw["title"],
        "sections": [
            {"type": "body", "paragraphs": raw["body_paragraphs"]},
            {
                "type": "section",
                "heading": raw["points_heading"],
                "subsections": [
                    {"heading": raw["point_one_heading"], "paragraphs": raw["point_one_paragraphs"]},
                    {"heading": raw["point_two_heading"], "paragraphs": raw["point_two_paragraphs"]},
                ],
            },
            {"type": "section", "heading": "In One Line", "paragraphs": raw["in_one_line_paragraphs"]},
        ],
    }


def parse_script_json(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


def make_script_write_fn(topic_package: dict, client: Optional[OpenAI] = None):
    """er002_common.run_script_attempts(config, script_write_fn, ...) へ渡す
    script_write_fn(config) -> dict を返す。configは呼び出し規約上受け取るが、
    記事ごとのプロンプトカスタマイズには使わない(全記事で同一プロンプト)。

    戻り値の関数オブジェクトには prompt_text/prompt_sha256/prompt_version を
    属性として付与しており、呼び出し側がマニフェストへ記録できるようにしている。
    """
    if client is None:
        load_dotenv()
        client = OpenAI()

    prompt = build_prompt(topic_package)
    prompt_sha256 = sha256_text(prompt)

    def script_write_fn(config: dict) -> dict:
        response = client.chat.completions.create(
            model=MODEL_WRITE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw = parse_script_json(response.choices[0].message.content)
        return convert_to_er002_schema(raw)

    script_write_fn.prompt_text = prompt
    script_write_fn.prompt_sha256 = prompt_sha256
    script_write_fn.prompt_version = PROMPT_VERSION
    script_write_fn.model = MODEL_WRITE
    return script_write_fn
