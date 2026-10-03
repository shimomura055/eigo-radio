# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage2_production_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ④、委任_07)
# ============================================================
# 目的: design書§4(Stage 2 Second Judge)の入力設計(§4-4確定版: Ledger
# 全文+source context+対象claim+対象claimを含む段落±1段落。explanation/
# severity/10 flagsはStage1出力から除外)に沿った「本来のStage2」(claim
# 単位、Stage1出力[origin/related_fact_id]を受け取る版)を実装し、
# per-claim call(claim 1件=1 call)とinstance batch call(claim配列=1 call)
# を同一入力で比較する(§3-5 A9、§9-1④)。あわせてprompt caching
# (Ledger全文を固定prefixとして連続callし、cached_tokensの有無を実測)を
# 検証する(§9-1④、A12)。
#
# 重要な設計制約:
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
# - Model Routing Contractは経由しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
from __future__ import annotations

import hashlib
import json
import time

import er003_v1_en_direct_vfl_01_generate as vfl01

MODEL = "gpt-6-luna"
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50
USD_JPY = 156.88

STAGE2_PROD_DEVELOPER_MESSAGE = (
    "あなたはVerified Fact LedgerとFact Safetyの独立監査担当(Second Judge)です。"
    "一次チェッカー(Stage 1)が既にBLOCKING-candidateとして検出した特定のclaimについて、"
    "本当にProductionを止めるべきmaterial errorかを、あなた自身の判断で再評価してください。"
)

MATERIALITY_RUBRIC = """【材料性(materiality)の判定基準】
- BLOCKING: Ledgerのclaim/scope/numeric_value/date_or_period/conditionsのいずれかと矛盾する、
  またはLedgerが別の原因・別の主体を明記しているのに異なるものを述べる、またはnotes_for_writer
  が明示的に禁じた断定をしている。
- QUALITY: Ledgerの観測と矛盾しないが、Ledgerが保証していない関係付け(因果接続詞・動機の
  帰属・強調)が加わっている。
- ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果を一切加えず(Ledgerに既出の
  固有名詞を繰り返すことはこの制約に抵触しない)、Ledgerが確認した事象の一般常識レベルの
  背景説明・条件付きの一般論にとどまる。
- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。"""

# 委任_55(2026-10-03、ユーザー決定=線引きの正式採用、`APPROVED_FOR_PRODUCTION`、
# `PRODUCTION_WIRED`未達): 上記`MATERIALITY_RUBRIC`の末尾「迷う場合はBLOCKING
# (fail-closed)」を、「重大な誤解になるかで決める」へ置き換えた版。旧版
# (`MATERIALITY_RUBRIC`)は定数として残す。QUALITYの「動機の帰属」は変更しない。
_V7_OLD_TIEBREAK = "- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。"
_V7_NEW_TIEBREAK = """- 上記のどれに該当するか迷う場合は、読者(英語学習者)がこの文を信じたときに事実関係の
  重大な誤解につながるかで決めてください。つながるならBLOCKING、つながらないならQUALITY
  としてください。数値・主体・否定・比較・時期の差は、この原則の対象外で、従来どおり
  機械的にBLOCKINGとします。"""
MATERIALITY_RUBRIC_V7 = MATERIALITY_RUBRIC.replace(_V7_OLD_TIEBREAK, _V7_NEW_TIEBREAK)
assert MATERIALITY_RUBRIC_V7 != MATERIALITY_RUBRIC

REWRITE_HINT_INSTRUCTION = """
【rewrite_hint(委任_10で追加)】
materialityがBLOCKINGの場合のみ、rewrite_hintに以下を全て含めてください:
1. 対象文を一意に特定できる、記事本文からの逐語引用(10〜30語程度、対象claimの
   核心部分をそのまま抜き出す。要約・言い換えは禁止)。
2. どう直すべきかの具体的な修正指示(削除するのか、Ledgerのどの値へ置換すべきか、
   範囲をどう狭めるべきか)。
3. 参照したLedgerのfact_id(related_fact_idと一致させる)。
BLOCKING以外(QUALITY/ACCEPTABLE)の場合、rewrite_hintは空文字列にしてください。"""

PER_CLAIM_PROMPT_TEMPLATE = """これはStage 1が既にBLOCKING-candidateとして検出したclaimの再評価です。
Stage 1の判定理由(explanation/severity/10種類のフラグ)はここでは一切提示しません。
以下のLedger全文・対象claim・そのローカル文脈のみを見て、あなた自身の判断で
materialityを判定してください。

【Verified Fact Ledger(全文)】
{verified_ledger_text}

【記事の日本語原文(参考、逸脱の発生源特定用。無ければ「(なし)」)】
{source_article_text}

【対象claim】
{claim_text}

【対象claimを含む段落±1段落(ローカル文脈)】
{local_context}

【関連情報(Stage1出力より、判定根拠には使わずbasis確認用のみ)】
origin: {origin}
related_fact_id: {related_fact_id}

{materiality_rubric}
{rewrite_hint_instruction}

上記claimについてmateriality/basis/rewrite_kind/rewrite_hintを判定してください。"""

BATCH_PROMPT_TEMPLATE = """これはStage 1が既にBLOCKING-candidateとして検出した複数claimの一括
再評価です。Stage 1の判定理由(explanation/severity/10種類のフラグ)はここでは
一切提示しません。以下のLedger全文・対象claim配列・各claimのローカル文脈のみを
見て、あなた自身の判断でclaimごとにmaterialityを判定してください(claim間で
互いに影響を与えず、各claimを独立に評価してください)。

【Verified Fact Ledger(全文)】
{verified_ledger_text}

【記事の日本語原文(参考、逸脱の発生源特定用。無ければ「(なし)」)】
{source_article_text}

【対象claim配列(各claimのローカル文脈・関連情報を付す)】
{claims_block}

{materiality_rubric}
{rewrite_hint_instruction}

claim配列と同じ順序・同じ件数で、claim_indexを付けてmateriality/basis/
rewrite_kind/rewrite_hintを判定してください。"""

_ITEM_PROPS = {
    "materiality": {"type": "string", "enum": ["BLOCKING", "QUALITY", "ACCEPTABLE"]},
    "basis": {
        "type": "string",
        "enum": [
            "ledger_claim", "ledger_scope", "ledger_numeric_value",
            "ledger_date_or_period", "ledger_conditions",
            "notes_for_writer", "unsupported_relationship", "none",
        ],
    },
    "rewrite_kind": {
        "type": "string",
        "enum": ["delete", "replace_with_ledger_value", "narrow_scope", "none"],
    },
    # 委任_10で追加: 対象文の特定に十分な逐語引用+修正指示+参照fact_id
    # (BLOCKING時のみ非空、それ以外は空文字列)。§4-5。
    "rewrite_hint": {"type": "string"},
}

PER_CLAIM_JSON_SCHEMA = {
    "name": "open233_self_recovery_stage2_prod_per_claim_v1",
    "schema": {
        "type": "object",
        "properties": dict(_ITEM_PROPS),
        "required": ["materiality", "basis", "rewrite_kind", "rewrite_hint"],
        "additionalProperties": False,
    },
    "strict": True,
}

BATCH_JSON_SCHEMA = {
    "name": "open233_self_recovery_stage2_prod_batch_v1",
    "schema": {
        "type": "object",
        "properties": {
            "judgments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim_index": {"type": "integer"}, **_ITEM_PROPS},
                    "required": ["claim_index", "materiality", "basis", "rewrite_kind", "rewrite_hint"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["judgments"],
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


def split_paragraphs(article_text: str) -> list:
    return [p for p in article_text.split("\n\n") if p.strip()]


_WRAP_QUOTE_CHARS = "「」『』“”‘’\"'"


def _strip_wrapping_quotes(s: str) -> str:
    """Stage1出力のclaim_in_articleは「...」等の引用符で本文を囲むことが多い
    (本文中には引用符自体は存在しない場合がある)。段落一致のため、両端の
    引用符・空白のみを機械的に除去する(claim本文の意味は変更しない)。"""
    return s.strip().strip(_WRAP_QUOTE_CHARS).strip()


def build_local_context(article_text: str, claim_text: str) -> tuple:
    """対象claimを含む段落±1段落を抽出する(§4-4)。claimの部分文字列一致で
    段落を特定できない場合は記事全文をfallbackとして返し、fallback_used=True
    を記録する(Trial観測用、委任_04改訂/A8のfail-closed拡張条件の簡易版)。
    Stage1のclaim_in_articleが「...」等で本文を囲んでいるだけの場合(引用符
    自体は本文中に存在しない)は、両端の引用符を除去したうえで再照合する。"""
    paragraphs = split_paragraphs(article_text)
    probe_variants = []
    raw = claim_text.strip()
    if raw:
        probe_variants.append(raw[:40])
        stripped = _strip_wrapping_quotes(raw)
        if stripped and stripped[:40] not in probe_variants:
            probe_variants.append(stripped[:40])

    target_idx = None
    for probe in probe_variants:
        if not probe:
            continue
        for i, p in enumerate(paragraphs):
            if probe in p:
                target_idx = i
                break
        if target_idx is not None:
            break
    if target_idx is None:
        return article_text, True
    lo = max(0, target_idx - 1)
    hi = min(len(paragraphs), target_idx + 2)
    return "\n\n".join(paragraphs[lo:hi]), False


def _extract_usage(response) -> dict:
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
    return {
        "input_tokens": input_tokens, "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens, "reasoning_tokens": reasoning_tokens,
    }


def run_stage2_per_claim(client, verified_ledger_text: str, source_article_text: str | None,
                          claim_text: str, origin: str | None, related_fact_id: str | None,
                          local_context: str, model: str = MODEL) -> dict:
    prompt = PER_CLAIM_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        source_article_text=source_article_text or "(なし)",
        claim_text=claim_text,
        local_context=local_context,
        origin=origin or "(不明)",
        related_fact_id=related_fact_id or "(不明)",
        materiality_rubric=MATERIALITY_RUBRIC_V7,
        rewrite_hint_instruction=REWRITE_HINT_INSTRUCTION,
    )
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **PER_CLAIM_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": STAGE2_PROD_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage_dict = _extract_usage(response)
    return {
        "prompt_sha256": sha256_text(prompt), "parsed": parsed, "model": response.model,
        "response_id": response.id, "usage": usage_dict,
        "cost_jpy": round(official_cost_jpy(usage_dict), 4), "elapsed_seconds": elapsed,
    }


def run_stage2_batch(client, verified_ledger_text: str, source_article_text: str | None,
                      claims: list, model: str = MODEL) -> dict:
    """claims: list of dict{claim_text, origin, related_fact_id, local_context}"""
    blocks = []
    for i, c in enumerate(claims):
        blocks.append(
            f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
            f"ローカル文脈(段落±1): {c['local_context']}\n"
            f"origin: {c.get('origin') or '(不明)'}\n"
            f"related_fact_id: {c.get('related_fact_id') or '(不明)'}"
        )
    claims_block = "\n\n".join(blocks)
    prompt = BATCH_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        source_article_text=source_article_text or "(なし)",
        claims_block=claims_block,
        materiality_rubric=MATERIALITY_RUBRIC_V7,
        rewrite_hint_instruction=REWRITE_HINT_INSTRUCTION,
    )
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **BATCH_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": STAGE2_PROD_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage_dict = _extract_usage(response)
    return {
        "prompt_sha256": sha256_text(prompt), "parsed": parsed, "model": response.model,
        "response_id": response.id, "usage": usage_dict,
        "cost_jpy": round(official_cost_jpy(usage_dict), 4), "elapsed_seconds": elapsed,
    }
