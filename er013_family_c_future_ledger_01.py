# ============================================================
# er013_family_c_future_ledger_01.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01
# ============================================================
# 目的: 新Family C(Future、独立経路)向けの3層Ledgerスキーマと、
# Research/Ledger Verification出力(Layer 1=既存Verified Fact Ledger、
# 既存経路をそのまま再利用・無変更)から、Layer 2(FUTURE_ASSUMPTION)・
# Layer 3(IMAGINED_FUTURE)の材料をLLM 1回で生成し、3層Ledger本文へ
# 組み立てる処理を提供する。
#
# 既存Production/A-Family/B-Family/Discoveryの各ファイルはimportしない
# (独立経路)。Research自体(Researcher/Verification呼び出し)は既存
# er003_v1_en_direct_vfl_01_generate.py(vfl01)を呼び出し側(driver)が
# そのままimportして使う想定であり、本ファイルはその後段(Layer 1
# テキスト→3層Ledger化)のみを担当する。
#
# 設計根拠: EDITORIAL-FUTURE-ARTICLE-DESIGN-01_REPORT.md §3、
# er013_future_article_design_draft_01.md §2。
# Status: 本ファイルの文言・スキーマは全て未承認draftの実装であり、
# `APPROVED_FOR_PRODUCTION`ではない(Trial専用)。
# ============================================================
from __future__ import annotations

import json
import re
from typing import Any, Optional

PRESENT_FACT_TAG = "[PRESENT_FACT]"
FUTURE_ASSUMPTION_TAG = "[FUTURE_ASSUMPTION]"
IMAGINED_FUTURE_TAG = "[IMAGINED_FUTURE]"

NO_SPECIFIC_BASIS = "NONE_GENERAL_INFERENCE"  # based_on/grounded_inに具体的IDがない場合の明示的sentinel


def build_layer1_ledger_text(verified_ledger_text: str) -> str:
    """既存Verified Fact Ledger本文(vfl01.build_verified_ledger_text()等、
    既存Research/Ledger Verification経路の出力)を、フォーマットは一切
    変更せずLayer 1タグで囲むだけ。Layer 1のFactは既存の厳格な
    Fact Checker A' / Ledger Deviation Checker検証対象のまま(緩和なし)。"""
    body = (verified_ledger_text or "").strip("\n")
    return f"{PRESENT_FACT_TAG}\n{body}\n"


_FACT_ID_RE = re.compile(r"^\[VERIFIED\]\s*(?P<fact_id>[A-Za-z0-9_\-]+):", re.MULTILINE)


def extract_present_fact_ids(verified_ledger_text: str) -> list:
    """Layer1テキストから既存フォーマット `[VERIFIED] <fact_id>: ...` の
    fact_id一覧を抽出する(based_on/grounded_inの照合先IDセット用)。"""
    return _FACT_ID_RE.findall(verified_ledger_text or "")


# ------------------------------------------------------------
# Layer 2/3生成プロンプト(LLM 1回、Structured Output)
# ------------------------------------------------------------
LAYER23_DEVELOPER_MESSAGE = (
    "あなたは、確認済みの現在の事実(Layer 1)だけを根拠として、記事の"
    "Writerが使うための「未来の仮定」と「想像した未来の場面材料」を"
    "整理するアシスタントです。あなた自身が新しい現在の事実を作り出す"
    "ことは禁止です。Layer 1に書かれていない具体的な現在の事実・数字・"
    "固有名詞を、FUTURE_ASSUMPTIONやIMAGINED_FUTUREの中に紛れ込ませない"
    "でください(想像は未来についてのみ許されます)。"
)

LAYER23_PROMPT_TEMPLATE = """テーマ: {topic}

【Layer 1: 確認済みの現在の事実(Verified Fact Ledger、変更禁止)】
{layer1_ledger_text}

上記Layer 1のFactだけを根拠として、以下2種類の材料を作成してください。

1. FUTURE_ASSUMPTION(明示的な仮定・条件): 「もしこの流れが続けば」
   「この技術が実用化されれば」のような、読み手にも仮定だとわかる
   仮定を1〜4件。各仮定について、based_onにLayer 1のfact_idを1件以上
   指定してください(Layer 1の複数Factからの一般的な推論で、特定の
   単一Factに紐づけられない場合のみ、based_onへ"{no_basis}"を使って
   ください)。

2. IMAGINED_FUTURE(想像した未来の場面材料): 意味のある1〜3通りの
   未来の下書き材料。数合わせの分岐は作らないでください。各scene
   について、grounded_inにFUTURE_ASSUMPTIONのassumption_id、または
   Layer 1のfact_idを1件以上指定してください(未来の場面自体は想像で
   構いませんが、その場面が何を根拠にした延長かを明示するためです)。
   timeframeには、このテーマに合う具体的な時間軸表現(例: "around
   2035"のような)を入れてください。scene_summaryは短い日本語の
   下書きで構いません(実際の英語本文はこの後Writerが別途執筆します)。

出力は指定のJSON形式のみで返してください。"""


LAYER23_JSON_SCHEMA = {
    "name": "family_c_future_layer23_v1",
    "schema": {
        "type": "object",
        "properties": {
            "future_assumptions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "assumption_id": {"type": "string"},
                        "assumption": {"type": "string"},
                        "based_on": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["assumption_id", "assumption", "based_on"],
                    "additionalProperties": False,
                },
            },
            "imagined_futures": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scene_id": {"type": "string"},
                        "timeframe": {"type": "string"},
                        "scene_summary": {"type": "string"},
                        "grounded_in": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["scene_id", "timeframe", "scene_summary", "grounded_in"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["future_assumptions", "imagined_futures"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_layer23_generation_prompt(topic: str, layer1_ledger_text: str) -> str:
    return LAYER23_PROMPT_TEMPLATE.format(
        topic=topic, layer1_ledger_text=layer1_ledger_text, no_basis=NO_SPECIFIC_BASIS)


def run_layer23_generation(client, topic: str, layer1_ledger_text: str, model: str, reasoning_effort: str) -> dict:
    """Layer 2/3材料生成(LLM 1回、web_search toolなし=Layer1の範囲内での
    整理作業のみであり新規調査は行わない)。呼び出し元(driver)がmodel/
    reasoning_effortを既存Model Routing Contract経由の値で明示指定する
    こと(本関数はhardcoded modelを持たない、fail-closedの一部を呼び出し
    側に委ねる設計)。"""
    prompt = build_layer23_generation_prompt(topic, layer1_ledger_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **LAYER23_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": LAYER23_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed,
            "model": response.model, "response_id": response.id}


def validate_layer23_grounding(present_fact_ids: list, layer23_parsed: dict) -> list:
    """based_on/grounded_inが、Layer1のfact_id・Layer2のassumption_id・
    NO_SPECIFIC_BASISのいずれでもない場合に issue を返す(捏造根拠の検出)。
    問題なければ空リスト。"""
    issues = []
    fact_id_set = set(present_fact_ids or [])
    assumption_ids = {a.get("assumption_id") for a in layer23_parsed.get("future_assumptions", [])}
    valid_layer12_ids = fact_id_set | assumption_ids | {NO_SPECIFIC_BASIS}

    for a in layer23_parsed.get("future_assumptions", []):
        for ref in a.get("based_on") or []:
            if ref not in fact_id_set and ref != NO_SPECIFIC_BASIS:
                issues.append({
                    "type": "assumption_based_on_unknown_fact_id",
                    "assumption_id": a.get("assumption_id"), "ref": ref,
                })
    for s in layer23_parsed.get("imagined_futures", []):
        for ref in s.get("grounded_in") or []:
            if ref not in valid_layer12_ids:
                issues.append({
                    "type": "scene_grounded_in_unknown_id",
                    "scene_id": s.get("scene_id"), "ref": ref,
                })
    return issues


def assemble_three_layer_ledger_text(layer1_ledger_text: str, layer23_parsed: dict) -> str:
    """Layer1本文(既存フォーマット、無変更)+Layer2+Layer3をタグ区切りで
    連結した、Writerへ渡す最終Ledger本文を組み立てる。"""
    lines = [layer1_ledger_text.rstrip("\n"), "", FUTURE_ASSUMPTION_TAG]
    for a in layer23_parsed.get("future_assumptions", []):
        lines.append(f"assumption_id: {a.get('assumption_id')}")
        lines.append(f"assumption: {a.get('assumption')}")
        lines.append(f"based_on: {', '.join(a.get('based_on') or [])}")
        lines.append("")
    lines.append(IMAGINED_FUTURE_TAG)
    for s in layer23_parsed.get("imagined_futures", []):
        lines.append(f"scene_id: {s.get('scene_id')}")
        lines.append(f"timeframe: {s.get('timeframe')}")
        lines.append(f"scene_summary: {s.get('scene_summary')}")
        lines.append(f"grounded_in: {', '.join(s.get('grounded_in') or [])}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
