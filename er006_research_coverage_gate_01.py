# ============================================================
# er006_research_coverage_gate_01.py
# ER-006-COST-WASTE-RCA-RESEARCH-COVERAGE-GATE-01: Research Coverage Gate(検証用、Production未配線)
# ============================================================
# Writer実行前に、Verified Fact Ledgerが「そのTopicの中心的な問い・
# 説明ロジックをLedgerの範囲内だけで書くために十分か」を判定する。
# Source数のような機械的な閾値は使わない(Source Count Gateではなく
# Coverage Gate)。判定はCOVERAGE_PASS / MORE_RESEARCH_REQUIREDの2値。
#
# 本タスクの検証時点ではProductionへ本配線していない(実験用スクリプト)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01

GATE_MODEL = "gpt-5.6-luna"  # 検証用固定。Production本配線時は
                              # er006_model_routing_contract_01経由に切替える

GATE_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのResearch Coverage Gate担当です。Writerが記事を書き始める前に、"
    "与えられたVerified Fact Ledger(と対象Topicのタイトル)だけを根拠に、"
    "そのTopicの中心的な問い・説明ロジックを、Ledgerの範囲内だけで自然に書けるだけの"
    "証拠(Evidence Coverage)が揃っているかを判定してください。\n\n"
    "判定基準(Source数のような機械的な閾値は使わないでください):\n"
    "1. Topicの中心的な問い(タイトルが示す問い)に、Ledgerだけで答えられるか\n"
    "2. 中心的な説明ロジック(なぜそうなるのか)が、Evidenceで裏付けられているか\n"
    "3. Writerが記事化する際に自然に触れそうな主要論点が、Ledgerに存在するか\n"
    "4. 重要な因果説明について、Evidenceが十分か\n"
    "5. 一方向(例:消費者側だけ、企業側だけ)にEvidenceが偏っていないか\n"
    "6. 重要な反証・限定条件(例:効果が有意でなかった点、一般化できない範囲)が"
    "欠けていないか\n"
    "7. Evidence不足をWriterが自分の推論・一般知識で埋めなければ記事が成立しない"
    "状態になっていないか\n\n"
    "注意: 記事に使わない可能性が高い周辺情報まで網羅することは要求しません。"
    "過剰なResearchを誘発しないでください。Ledgerの記述が慎重・限定的であること"
    "自体は問題ではありません(むしろ望ましい)。問題にすべきは、記事の中心的な"
    "主張を支える具体的なEvidenceが欠けている場合のみです。"
)

GATE_PROMPT_TEMPLATE = """【対象Topic】
{title}

【Verified Fact Ledger】
{ledger_text}

【あなたのタスク】
上記のLedgerが、このTopicの中心的な問い・説明ロジックをWriterがLedgerの
範囲内だけで書くために十分かを判定してください。"""


def gate_schema():
    missing_item = {
        "type": "object",
        "properties": {
            "missing_coverage": {"type": "string"},
            "why_it_matters": {"type": "string"},
            "evidence_or_source_type_needed": {"type": "string"},
        },
        "required": ["missing_coverage", "why_it_matters", "evidence_or_source_type_needed"],
        "additionalProperties": False,
    }
    return {
        "name": "research_coverage_gate",
        "schema": {
            "type": "object",
            "properties": {
                "verdict": {"type": "string", "enum": ["COVERAGE_PASS", "MORE_RESEARCH_REQUIRED"]},
                "central_question": {"type": "string"},
                "reasoning": {"type": "string"},
                "missing_items": {"type": "array", "items": missing_item},
            },
            "required": ["verdict", "central_question", "reasoning", "missing_items"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def run_coverage_gate(title: str, ledger_text: str) -> dict:
    client = vfl01.get_client()
    prompt = GATE_PROMPT_TEMPLATE.format(title=title, ledger_text=ledger_text)
    resp = client.responses.create(
        model=GATE_MODEL,
        reasoning={"effort": "medium"},
        text={"format": {"type": "json_schema", **gate_schema()}},
        input=[
            {"role": "developer", "content": GATE_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = json.loads(resp.output_text)
    return {
        "parsed": parsed, "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }


if __name__ == "__main__":
    import sys
    title = sys.argv[1]
    ledger_path = sys.argv[2]
    ledger_text = open(ledger_path, encoding="utf-8").read()
    result = run_coverage_gate(title, ledger_text)
    print(json.dumps(result["parsed"], ensure_ascii=False, indent=2))
    print(f"model={result['model']} input_tokens={result['input_tokens']} output_tokens={result['output_tokens']}")
