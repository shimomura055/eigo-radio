# ============================================================
# er013_family_c_future_scaffold_02.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02
# ============================================================
# 目的: Family C(Future)Trial-01からの再設計(作業A項目2「Ledger→
# Writerへの情報の渡し方」)。Layer 1(既存Verified Fact Ledger、無変更・
# 無編集)の生の統計・研究・製品情報をWriterへ直接渡さず、
# 「World Scaffold(世界の足場)」= 数値・出典・固有名詞を含まない
# 平易な文(現在できること/できないこと/変化の方向と条件)へ、LLM 1回で
# 変換する。based_onでLayer1のfact_idへ紐づけ(内部監査用、Writerへは
# 見せない)。
#
# 変換されたWorld Scaffoldのみが、後段のLayer2/3生成
# (er013_family_c_future_ledger_02.py)・Writer
# (er013_family_c_future_writer_02.py)へ渡される。Layer1生テキストは、
# 既存Fact Checker A'・Ledger Deviation Checker(er013_family_c_future_
# qa_02.py経由、無改変で再利用)向けにのみ従来通り使われる(Fact Safetyは
# 緩和しない、EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02指示書§作業A-7)。
#
# 既存Trial-01ファイル(er013_family_c_future_ledger_01.py等)は無編集で
# 残す。本ファイルはそこからNO_SPECIFIC_BASIS等の共有定数のみimportし、
# 独自にLayer1→World Scaffold変換のみを新設する。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json
import re

import er013_family_c_future_ledger_01 as fcl_v1  # NO_SPECIFIC_BASIS等の共有定数のみ再利用(無編集)

NO_SPECIFIC_BASIS = fcl_v1.NO_SPECIFIC_BASIS

SCAFFOLD_CATEGORIES = ("capability_now", "limitation_now", "change_direction")

WORLD_SCAFFOLD_DEVELOPER_MESSAGE = (
    "あなたは、確認済みの現在の事実(Layer 1 Verified Fact Ledger)を、"
    "数値・出典・固有名詞(製品名・企業名・調査名)を一切含まない、平易な"
    "英語の文へ書き換えるアシスタントです。あなたの仕事は、記事のWriterが"
    "「今、何ができて、何ができなくて、どちらの方向に変わりつつあるか」を"
    "理解できるようにすることです。新しい現在の事実を作り出すことは禁止"
    "です。数字(パーセント・台数・年など)や、製品名・企業名・調査機関名を"
    "書き換え後の文に含めないでください(それらは別途product_names_"
    "mentionedフィールドへ、Layer1原文にある通りに抽出してください)。"
)

WORLD_SCAFFOLD_PROMPT_TEMPLATE = """テーマ: {topic}

【Layer 1: 確認済みの現在の事実(Verified Fact Ledger、変更禁止)】
{layer1_ledger_text}

上記Layer 1の各Factを、以下3種類のいずれかに分類し、数値・出典・固有名詞
(製品名・企業名・調査機関名)を一切含まない平易な英語の文(statement)へ
書き換えてください。

1. capability_now: 今、現実にできていること。
2. limitation_now: 今、まだできていない・限界があること。
3. change_direction: 今の事実から読み取れる、変化の方向性・条件
   (数値そのものではなく、「増えつつある」「まだ一部に限られる」のような
   方向性の記述)。

各statementについて、based_onにLayer 1のfact_idを1件以上指定して
ください(1つのstatementが複数のFactをまとめて言い換えたものでも
構いません)。

また、Layer 1原文の中に登場する製品名・ブランド名・型番を、
product_names_mentionedへLayer1原文の表記のまま全て抽出してください
(これは監査用であり、Writerには渡されません)。

出力は指定のJSON形式のみで返してください。"""


WORLD_SCAFFOLD_JSON_SCHEMA = {
    "name": "family_c_future_world_scaffold_v1",
    "schema": {
        "type": "object",
        "properties": {
            "scaffold_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scaffold_id": {"type": "string"},
                        "category": {"type": "string", "enum": list(SCAFFOLD_CATEGORIES)},
                        "statement": {"type": "string"},
                        "based_on": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["scaffold_id", "category", "statement", "based_on"],
                    "additionalProperties": False,
                },
            },
            "product_names_mentioned": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["scaffold_items", "product_names_mentioned"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_world_scaffold_prompt(topic: str, layer1_ledger_text: str) -> str:
    return WORLD_SCAFFOLD_PROMPT_TEMPLATE.format(topic=topic, layer1_ledger_text=layer1_ledger_text)


def run_world_scaffold_generation(client, topic: str, layer1_ledger_text: str, model: str, reasoning_effort: str) -> dict:
    """Layer1→World Scaffold変換(LLM1回、web_search toolなし=Layer1の
    範囲内での言い換え作業のみであり新規調査は行わない)。"""
    prompt = build_world_scaffold_prompt(topic, layer1_ledger_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **WORLD_SCAFFOLD_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": WORLD_SCAFFOLD_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed,
            "model": response.model, "response_id": response.id}


def validate_scaffold_grounding(present_fact_ids: list, scaffold_parsed: dict) -> list:
    """based_onが、Layer1のfact_idにも存在しない場合にissueを返す
    (捏造根拠の検出。NO_SPECIFIC_BASISは許容しない=Scaffold項目は必ず
    具体的なFactへ紐づく設計。空リストなら問題なし)。"""
    issues = []
    fact_id_set = set(present_fact_ids or [])
    for item in scaffold_parsed.get("scaffold_items", []):
        for ref in item.get("based_on") or []:
            if ref not in fact_id_set:
                issues.append({
                    "type": "scaffold_based_on_unknown_fact_id",
                    "scaffold_id": item.get("scaffold_id"), "ref": ref,
                })
    return issues


_DIGIT_RE = re.compile(r"\d")


def validate_scaffold_no_leakage(scaffold_parsed: dict) -> list:
    """World Scaffoldのstatementに、数字または抽出済みproduct_names_
    mentionedの固有名詞が紛れ込んでいないかを機械的に確認する
    (決定的スキャン、¥0)。問題なければ空リスト。"""
    issues = []
    product_names = scaffold_parsed.get("product_names_mentioned") or []
    for item in scaffold_parsed.get("scaffold_items", []):
        statement = item.get("statement") or ""
        if _DIGIT_RE.search(statement):
            issues.append({"type": "digit_in_scaffold_statement", "scaffold_id": item.get("scaffold_id"),
                            "statement": statement})
        lowered = statement.lower()
        for name in product_names:
            if name and name.lower() in lowered:
                issues.append({"type": "product_name_in_scaffold_statement", "scaffold_id": item.get("scaffold_id"),
                                "product_name": name, "statement": statement})
    return issues


def extract_scaffold_ids(scaffold_parsed: dict) -> list:
    return [item.get("scaffold_id") for item in scaffold_parsed.get("scaffold_items", [])]


def build_world_scaffold_text_for_writer(scaffold_parsed: dict) -> str:
    """Writerへ渡す最終テキスト(scaffold_id + category + statementのみ。
    based_on[fact_id]・product_names_mentionedは含めない=Writerへは
    数値・出典・固有名詞の手がかりを一切渡さない設計)。"""
    lines = ["[WORLD_SCAFFOLD]"]
    for item in scaffold_parsed.get("scaffold_items", []):
        lines.append(f"scaffold_id: {item.get('scaffold_id')}")
        lines.append(f"category: {item.get('category')}")
        lines.append(f"statement: {item.get('statement')}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
