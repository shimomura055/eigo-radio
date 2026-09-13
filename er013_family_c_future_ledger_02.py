# ============================================================
# er013_family_c_future_ledger_02.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02
# ============================================================
# 目的: Trial-01(er013_family_c_future_ledger_01.py、無編集で保持)からの
# 再設計(作業A項目2)。Layer2(FUTURE_ASSUMPTION)・Layer3(IMAGINED_FUTURE)
# の生成材料を、Layer1の生テキストではなく World Scaffold
# (er013_family_c_future_scaffold_02.py)を根拠として生成する。これにより
# Layer2/3(および、そこから作られる最終Writer入力)に、数値・出典・
# 製品名が混入する経路をそもそも作らない(前回=Layer1直接参照、
# 今回=World Scaffold経由のみ)。
#
# Layer1生テキスト・fact_idベースの3層Ledger組み立て(既存Fact Checker A'/
# Ledger Deviation Checker向け)は、従来通りer013_family_c_future_
# ledger_01.pyの関数を無編集のままimportして使う(Fact Safetyは緩和
# しない、指示書§作業A-7)。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json

import er013_family_c_future_ledger_01 as fcl_v1  # PRESENT_FACT_TAG等、無編集で再利用
import er013_family_c_future_scaffold_02 as fcs

NO_SPECIFIC_BASIS = fcl_v1.NO_SPECIFIC_BASIS

LAYER23_V2_DEVELOPER_MESSAGE = (
    "あなたは、World Scaffold(現在できること/できないこと/変化の方向、"
    "数値・出典・固有名詞を含まない平易な文)だけを根拠として、記事の"
    "Writerが使うための「未来の仮定」と「想像した未来の場面材料」を"
    "整理するアシスタントです。あなた自身が新しい現在の事実・数字・"
    "固有名詞を作り出すことは禁止です。未来の場面材料や仮定の中にも、"
    "数字・製品名・企業名・調査名を含めないでください(想像は未来に"
    "ついてのみ、平易な言葉で行ってください)。"
)

LAYER23_V2_PROMPT_TEMPLATE = """テーマ: {topic}

【World Scaffold(現在できること/できないこと/変化の方向。数値・出典・
固有名詞は含まれていません。変更禁止)】
{world_scaffold_text}

上記World Scaffoldだけを根拠として、以下2種類の材料を作成してください。

1. FUTURE_ASSUMPTION(明示的な仮定・条件): 「もしこの流れが続けば」
   「この技術が実用化されれば」のような、読み手にも仮定だとわかる
   仮定を1〜4件。各仮定について、based_onにWorld Scaffoldのscaffold_idを
   1件以上指定してください(複数のscaffold項目からの一般的な推論で、
   特定の単一項目に紐づけられない場合のみ、based_onへ"{no_basis}"を
   使ってください)。

2. IMAGINED_FUTURE(想像した未来の場面材料): このテーマにとって最も
   意味のある未来の描き方を選んでください。数年後→10年後のような複数
   時点、複数の別未来(希望/不安などの分岐)、単一の時点を深く描く、など
   構成は自由です。機械的に3時点へ当てはめる必要はありません(意味が
   なければ1通りでも十分です)。各sceneについて、grounded_inに
   FUTURE_ASSUMPTIONのassumption_id、またはWorld Scaffoldのscaffold_idを
   1件以上指定してください。timeframeには、このテーマに合う具体的な
   時間軸表現を入れてください。scene_summaryは短い日本語の下書きで
   構いません(実際の英語本文はこの後Writerが別途執筆します)。また、
   なぜこの時点数・構成を選んだかを一言でstructure_rationaleに記して
   ください(このrationaleはWriterへの参考メモであり、読者向け本文には
   出しません)。

出力は指定のJSON形式のみで返してください。"""


LAYER23_V2_JSON_SCHEMA = {
    "name": "family_c_future_layer23_v2",
    "schema": {
        "type": "object",
        "properties": {
            "structure_rationale": {"type": "string"},
            "future_assumptions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "assumption_id": {"type": "string"},
                        "assumption": {"type": "string"},
                        "based_on": {"type": "array", "items": {"type": "string"}},
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
                        "grounded_in": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["scene_id", "timeframe", "scene_summary", "grounded_in"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["structure_rationale", "future_assumptions", "imagined_futures"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_layer23_v2_prompt(topic: str, world_scaffold_text: str) -> str:
    return LAYER23_V2_PROMPT_TEMPLATE.format(topic=topic, world_scaffold_text=world_scaffold_text, no_basis=NO_SPECIFIC_BASIS)


def run_layer23_v2_generation(client, topic: str, world_scaffold_text: str, model: str, reasoning_effort: str) -> dict:
    prompt = build_layer23_v2_prompt(topic, world_scaffold_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **LAYER23_V2_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": LAYER23_V2_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed,
            "model": response.model, "response_id": response.id}


def validate_layer23_v2_grounding(scaffold_ids: list, layer23_parsed: dict) -> list:
    """based_on/grounded_inが、World Scaffoldのscaffold_id・Layer2の
    assumption_id・NO_SPECIFIC_BASISのいずれでもない場合にissueを返す。"""
    issues = []
    scaffold_id_set = set(scaffold_ids or [])
    assumption_ids = {a.get("assumption_id") for a in layer23_parsed.get("future_assumptions", [])}
    valid_ids = scaffold_id_set | assumption_ids | {NO_SPECIFIC_BASIS}

    for a in layer23_parsed.get("future_assumptions", []):
        for ref in a.get("based_on") or []:
            if ref not in scaffold_id_set and ref != NO_SPECIFIC_BASIS:
                issues.append({"type": "assumption_based_on_unknown_scaffold_id",
                                "assumption_id": a.get("assumption_id"), "ref": ref})
    for s in layer23_parsed.get("imagined_futures", []):
        for ref in s.get("grounded_in") or []:
            if ref not in valid_ids:
                issues.append({"type": "scene_grounded_in_unknown_id",
                                "scene_id": s.get("scene_id"), "ref": ref})
    return issues


def assemble_world_package_text(world_scaffold_text: str, layer23_parsed: dict) -> str:
    """Writerへ渡す最終テキスト(World Scaffold + Layer2 + Layer3。Layer1
    生テキストは一切含めない)。structure_rationaleは読者向け本文用ではなく
    Writerへの参考メモとして末尾に添える。"""
    lines = [world_scaffold_text.rstrip("\n"), "", "[FUTURE_ASSUMPTION]"]
    for a in layer23_parsed.get("future_assumptions", []):
        lines.append(f"assumption_id: {a.get('assumption_id')}")
        lines.append(f"assumption: {a.get('assumption')}")
        lines.append(f"based_on: {', '.join(a.get('based_on') or [])}")
        lines.append("")
    lines.append("[IMAGINED_FUTURE]")
    for s in layer23_parsed.get("imagined_futures", []):
        lines.append(f"scene_id: {s.get('scene_id')}")
        lines.append(f"timeframe: {s.get('timeframe')}")
        lines.append(f"scene_summary: {s.get('scene_summary')}")
        lines.append(f"grounded_in: {', '.join(s.get('grounded_in') or [])}")
        lines.append("")
    lines.append("[STRUCTURE_RATIONALE_REFERENCE_ONLY]")
    lines.append(layer23_parsed.get("structure_rationale") or "")
    return "\n".join(lines).rstrip("\n") + "\n"
