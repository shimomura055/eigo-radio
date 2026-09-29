# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage2_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ②、委任_06)
# ============================================================
# 目的: design_open233_self_recovery_flow_01.md §4のStage 2 Second Judge
# Prompt/schemaを土台に、「Stage 1が検出しなかった(deviations=[])記事に
# 対し、Stage 1の出力を一切見せずに独立した第二の視点だけでLedgerとの
# 実質的な矛盾を拾えるか」を確認する診断目的のTrial実装。
#
# 通常のStage 2(§4)はStage 1がBLOCKING-candidateと判定したclaim単位で
# 発火する設計だが、本スクリプトはその前提(対象claim・origin・
# related_fact_id・rewrite_hint入力)が存在しない診断シナリオ専用
# (「Stage 1 recallの穴を後段で埋められるか」の実験、委任_06 §5)。
# 通常設計の入力(段落±1)ではなく、対象claim未特定のため記事全文を渡す
# (委任文明記)。
#
# 重要な設計制約:
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
#   本ファイルはvfl01.get_client()/vfl01.REASONING_EFFORTのみread-only参照。
# - Model Routing Contractは経由しない(既存er051/er052系Trialと同一方式)。
# - API keyは環境変数のみ(vfl01.get_client()経由、本文表示・保存禁止)。
# - 保存jsonにはprompt本体ではなくprompt_sha256のみを記録する(委任文明記)。
from __future__ import annotations

import hashlib
import json
import time

import er003_v1_en_direct_vfl_01_generate as vfl01

MODEL = "gpt-6-luna"

# 公式単価(design書§9-1/前Phase Trial実測と同一値、$/1M tokens)
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50
USD_JPY = 156.88

STAGE2_DIAGNOSTIC_DEVELOPER_MESSAGE = (
    "あなたはVerified Fact LedgerとFact Safetyの独立監査担当です。記事の面白さや"
    "スタイルは評価せず、記事がLedgerの範囲内に収まっているかだけを、他の判定結果を"
    "一切参照せず、あなた自身の独立した視点だけで判定してください。"
)

STAGE2_DIAGNOSTIC_PROMPT_TEMPLATE = """これは、既存の一次チェッカーとは別の、独立した第二の再評価です。一次
チェッカーの判定結果はここでは一切提示しません。あなた自身の判断のみで、
以下の記事本文全体を、Verified Fact Ledgerと照らし合わせ、実質的な事実の
食い違い(claim)を見つけてください。

【Verified Fact Ledger】
{verified_ledger_text}

【記事の日本語原文(参考、逸脱の発生源特定用。無ければ「(なし)」)】
{source_article_text}

【検証対象の記事(英語)】
{article_text}

【材料性(materiality)の判定基準】
- BLOCKING: Ledgerのclaim/scope/numeric_value/date_or_period/conditionsの
  いずれかと矛盾する、またはLedgerが別の原因・別の主体を明記しているのに
  異なるものを述べる、またはnotes_for_writerが明示的に禁じた断定をしている。
- QUALITY: Ledgerの観測と矛盾しないが、Ledgerが保証していない関係付け
  (因果接続詞・動機の帰属・強調)が加わっている。
- ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果を一切加えず
  (Ledgerに既出の固有名詞[例: 記事の主題となっている地名・組織名]を
  繰り返すことはこの制約に抵触しない)、Ledgerが確認した事象の一般常識
  レベルの背景説明・条件付きの一般論にとどまる。
- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。

記事中でLedgerとの関係が疑わしいclaimを全て挙げ、それぞれについて
BLOCKING/QUALITY/ACCEPTABLEのいずれかで判定してください。疑わしいclaimが
無ければ、candidate_deviationsを空配列にしてください。"""

STAGE2_DIAGNOSTIC_JSON_SCHEMA = {
    "name": "open233_self_recovery_stage2_diagnostic_v1",
    "schema": {
        "type": "object",
        "properties": {
            "candidate_deviations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim_in_article": {"type": "string"},
                        "related_fact_id_guess": {"type": "string"},
                        "materiality": {"type": "string", "enum": ["BLOCKING", "QUALITY", "ACCEPTABLE"]},
                        "basis": {
                            "type": "string",
                            "enum": [
                                "ledger_claim", "ledger_scope", "ledger_numeric_value",
                                "ledger_date_or_period", "ledger_conditions",
                                "notes_for_writer", "unsupported_relationship", "none",
                            ],
                        },
                        "reasoning_summary": {"type": "string"},
                    },
                    "required": [
                        "claim_in_article", "related_fact_id_guess", "materiality",
                        "basis", "reasoning_summary",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["candidate_deviations"],
        "additionalProperties": False,
    },
    "strict": True,
}


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def official_cost_jpy(usage: dict) -> float:
    it = usage.get("input_tokens") or 0
    ct = usage.get("cached_input_tokens") or 0
    ot = usage.get("output_tokens") or 0
    billable_in = max(it - ct, 0)
    cost_usd = billable_in / 1e6 * PRICE_IN + ct / 1e6 * PRICE_CACHED + ot / 1e6 * PRICE_OUT
    return cost_usd * USD_JPY


def build_stage2_diagnostic_prompt(verified_ledger_text: str, article_text: str,
                                    source_article_text: str | None) -> str:
    return STAGE2_DIAGNOSTIC_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        article_text=article_text,
        source_article_text=source_article_text or "(なし)",
    )


def run_stage2_diagnostic(client, verified_ledger_text: str, article_text: str,
                           source_article_text: str | None = None, model: str = MODEL) -> dict:
    prompt = build_stage2_diagnostic_prompt(verified_ledger_text, article_text, source_article_text)

    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **STAGE2_DIAGNOSTIC_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": STAGE2_DIAGNOSTIC_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    text = response.output_text
    parsed = json.loads(text)

    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None) if usage else None
    output_tokens = getattr(usage, "output_tokens", None) if usage else None
    cached_tokens = None
    reasoning_tokens = None
    if usage is not None:
        in_details = getattr(usage, "input_tokens_details", None)
        if in_details is not None:
            cached_tokens = getattr(in_details, "cached_tokens", None)
        out_details = getattr(usage, "output_tokens_details", None)
        if out_details is not None:
            reasoning_tokens = getattr(out_details, "reasoning_tokens", None)

    usage_dict = {
        "input_tokens": input_tokens, "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens, "reasoning_tokens": reasoning_tokens,
    }
    return {
        "prompt_sha256": sha256_text(prompt),
        "parsed": parsed,
        "model": response.model,
        "response_id": response.id,
        "usage": usage_dict,
        "cost_jpy": round(official_cost_jpy(usage_dict), 4),
        "elapsed_seconds": elapsed,
    }
