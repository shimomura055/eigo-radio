# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_s1d_trial_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ③、委任_07)
# ============================================================
# 目的: design_open233_self_recovery_flow_01.md §14-2 S1-D
# (「Stage1に直接materialityを出させる一体型」、前Phaseでは委任_03時点で
# いったん不採用と判定していたもの)を、委任_07のFable判定「採用は実測
# 結果で決める」に基づき、実際にTrial実装し、V0/V4-Aと同一fixtureで
# 比較測定する。
#
# 入力/出力(委任_07 §2で確定): 入力=Ledger全文+source context(JA原文)+
# 記事全文(対象claim未特定のためStage2診断Promptと同じく全文渡し)。
# 出力=claim配列(claim, 10 flags相当のカテゴリ、materiality
# BLOCKING/QUALITY/ACCEPTABLE、basis、rewrite_kind hint)。迷ったら
# BLOCKING(fail-closed)。Stage1 explanationなし(コスト削減、委任文明記)。
#
# 重要な設計制約:
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
#   本ファイルはvfl01.get_client()/vfl01.REASONING_EFFORT/
#   vfl01.DEVIATION_FLAG_KEYSのみread-only参照する。
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

S1D_DEVELOPER_MESSAGE = (
    "あなたはLedger Fact Safetyの一体型監査担当です。記事の面白さやスタイルは評価せず、"
    "意味上のFactがVerified Fact Ledgerの範囲内に収まっているかを、検出(detection)と"
    "重要度判定(materiality)を同時に、独立した1回の判定として行ってください。"
)

# カテゴリ定義本文はvfl01.DEVIATION_PROMPT_TEMPLATEの該当ブロックと同一の
# 定義文を用いる(Production Prompt本体は一切変更しない、本文字列は
# 本Trialファイル内に独立コピーを保持するのみ)。
S1D_CATEGORY_DEFINITIONS = """- changed_fact: Ledgerに存在しない、またはLedgerと矛盾する具体的事実を主張している
- changed_scope: Ledgerが確認した対象(誰が・どこで・いつ・どの集団か)を超えて一般化・拡張している
- changed_causality: 相関を因果に変えている、または因果の方向を変えている
- changed_certainty: Ledgerでは仮説・自己申告・専門家の解釈にすぎないものを、断定的な事実であるかのように強めている
- changed_number: 数値・割合・件数をLedgerと異なる値に変えている(単位の違いだけの言い換えは含まない)
- changed_actor: 発言主体・調査主体をLedgerと異なる人物・組織にすり替えている
- changed_negation: 肯定・否定を反転させている
- changed_comparison: 比較の方向(より多い/少ない、より高い/低い等)を反転・変更している
- changed_time: 時期・年代をLedgerと異なるものに変えている
- unsupported_new_claim: Ledgerに全く存在しない新しい具体的主張を追加している"""

S1D_PROMPT_TEMPLATE = """以下の記事本文を、Verified Fact Ledgerと照らし合わせ、意味上の
食い違い(deviation)を全て検出し、それぞれについて種類(10種類のカテゴリ
フラグ)と重要度(materiality)を同時に判定してください。1つの逸脱の内容が
複数カテゴリの定義に同時に該当する場合は、該当するカテゴリを全てtrueに
してください(最も強く該当する1つだけに絞る必要はありません)。

【Verified Fact Ledger】
{verified_ledger_text}

【記事の日本語原文(参考、逸脱の発生源特定用。無ければ「(なし)」)】
{source_article_text}

【検証対象の記事(英語)】
{article_text}

【10種類のカテゴリフラグ】
{category_definitions}

【deviationとして報告しないもの(許容範囲)】
- 自然なparaphrase、平易な言い換え、語順変更、同義語への置換
- 出典名を一般的な言い方(a report, a studyなど)に置き換えること自体
- 意味を変えない軽いbridge sentence
- Ledgerの特定の一文と一字一句一致しないが、同じ意味を保っている表現

【材料性(materiality)の判定基準】
- BLOCKING: Ledgerのclaim/scope/numeric_value/date_or_period/conditionsのいずれかと矛盾する、
  またはLedgerが別の原因・別の主体を明記しているのに異なるものを述べる、またはnotes_for_writer
  が明示的に禁じた断定をしている。
- QUALITY: Ledgerの観測と矛盾しないが、Ledgerが保証していない関係付け(因果接続詞・動機の
  帰属・強調)が加わっている。
- ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果を一切加えず(Ledgerに既出の
  固有名詞を繰り返すことはこの制約に抵触しない)、Ledgerが確認した事象の一般常識レベルの
  背景説明・条件付きの一般論にとどまる。
- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。

各deviationについて、rewrite_kind(delete=Ledger外の付加物を削るだけで解消する型、
replace_with_ledger_value=Ledgerの正しい値へ置換する型、narrow_scope=範囲の再限定が
必要な型、none=BLOCKING以外またはRewrite方針未定の場合)も出力してください
(BLOCKING時のみdelete/replace_with_ledger_value/narrow_scopeのいずれかを選び、
それ以外はnoneにしてください)。

疑わしいclaimが無ければ、deviationsを空配列にしてください。explanationのような
自由記述の理由文は出力しないでください(コスト削減のため、reasoning_summaryも
不要です)。"""

S1D_JSON_SCHEMA = {
    "name": "open233_self_recovery_s1d_v1",
    "schema": {
        "type": "object",
        "properties": {
            "deviations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim_in_article": {"type": "string"},
                        "related_fact_id_guess": {"type": "string"},
                        "changed_fact": {"type": "boolean"},
                        "changed_scope": {"type": "boolean"},
                        "changed_causality": {"type": "boolean"},
                        "changed_certainty": {"type": "boolean"},
                        "changed_number": {"type": "boolean"},
                        "changed_actor": {"type": "boolean"},
                        "changed_negation": {"type": "boolean"},
                        "changed_comparison": {"type": "boolean"},
                        "changed_time": {"type": "boolean"},
                        "unsupported_new_claim": {"type": "boolean"},
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
                    },
                    "required": [
                        "claim_in_article", "related_fact_id_guess",
                        "changed_fact", "changed_scope", "changed_causality", "changed_certainty",
                        "changed_number", "changed_actor", "changed_negation", "changed_comparison",
                        "changed_time", "unsupported_new_claim",
                        "materiality", "basis", "rewrite_kind",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["deviations"],
        "additionalProperties": False,
    },
    "strict": True,
}

# vfl01.DEVIATION_FLAG_KEYSと同一集合であることをtestで検証する(read-only参照)。
S1D_FLAG_KEYS = list(vfl01.DEVIATION_FLAG_KEYS)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def official_cost_jpy(usage: dict) -> float:
    it = usage.get("input_tokens") or 0
    ct = usage.get("cached_input_tokens") or 0
    ot = usage.get("output_tokens") or 0
    billable_in = max(it - ct, 0)
    cost_usd = billable_in / 1e6 * PRICE_IN + ct / 1e6 * PRICE_CACHED + ot / 1e6 * PRICE_OUT
    return cost_usd * USD_JPY


def build_s1d_prompt(verified_ledger_text: str, article_text: str, source_article_text: str | None) -> str:
    return S1D_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        article_text=article_text,
        source_article_text=source_article_text or "(なし)",
        category_definitions=S1D_CATEGORY_DEFINITIONS,
    )


def overall_status_from_deviations(deviations: list) -> str:
    """委任_07の「一体型」定義: materiality=="BLOCKING"のdeviationが1件でも
    あればLEDGER_DEVIATION、それ以外はLEDGER_COMPLIANT(V0/V4Aの
    overall_status語彙に合わせ、比較を可能にする)。"""
    if any(d.get("materiality") == "BLOCKING" for d in deviations):
        return "LEDGER_DEVIATION"
    return "LEDGER_COMPLIANT"


def run_s1d_check(client, verified_ledger_text: str, article_text: str,
                   source_article_text: str | None = None, model: str = MODEL) -> dict:
    prompt = build_s1d_prompt(verified_ledger_text, article_text, source_article_text)

    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **S1D_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": S1D_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    text = response.output_text
    parsed = json.loads(text)
    deviations = parsed.get("deviations", [])
    overall_status = overall_status_from_deviations(deviations)

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
        "parsed": {"deviations": deviations, "overall_status": overall_status},
        "model": response.model,
        "response_id": response.id,
        "usage": usage_dict,
        "cost_jpy": round(official_cost_jpy(usage_dict), 4),
        "elapsed_seconds": elapsed,
    }
