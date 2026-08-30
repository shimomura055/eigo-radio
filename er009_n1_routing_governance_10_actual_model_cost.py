# ============================================================
# er009_n1_routing_governance_10_actual_model_cost.py
# ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10: 実使用modelベースCost計算
# ============================================================
# 背景: Trial-08(er009_n1_full_writer_ledger_integration_08.py)の
# call_cost_jpy()は、raw_usage_logに記録された実際のmodel_idを一切見ず、
# 常にSol単価をhardcodeして計算していた。実際に呼ばれたmodelはRouting
# SSOT変更の伝播漏れによりgpt-5.6-solのままだったため結果的に一致して
# いたが、これは偶然であり、Lunaが実際に使われていてもSol単価で計算され
# ていた設計上のバグである。
#
# 本モジュールは、cost_log.jsonl(er005_cost_logger形式)に記録された
# 「実際のAPI応答のmodel」だけから単価を引く。model_idが未登録/不明な
# 場合は、他modelの単価へ黙ってfallbackせず例外を送出する(fail-closed)。
# 単価出典: er005_output/cost_baseline_01/pricing_snapshot.json
# (2026-08-23、OFFICIAL_SOURCE)。1 USD = 160 JPY固定(タスク仕様指定)。
from __future__ import annotations

import json

USD_TO_JPY = 160.0

# (provider, model_id) -> (input, cached_input, output) USD/1M tokens
PRICING_USD_PER_M = {
    ("openai", "gpt-5.6-luna"): (0.20, 0.02, 1.20),
    ("openai", "gpt-5.6-sol"): (5.00, 0.50, 30.00),
}


class UnknownModelPricingError(Exception):
    """model_idに対応する単価が見つからない場合に送出する。"""


def cost_jpy_for_call(provider: str, model_id: str | None, input_tokens, cached_input_tokens,
                       output_tokens) -> float:
    if not model_id:
        raise UnknownModelPricingError(
            f"provider={provider}: model_idが記録されていないcallのCostは計算できません"
            "(不明modelへの単価fallbackは禁止)。")
    key = (provider, model_id)
    if key not in PRICING_USD_PER_M:
        raise UnknownModelPricingError(
            f"provider={provider} model_id={model_id!r} の単価がPRICING_USD_PER_Mに"
            "登録されていません。未知modelへ他modelの単価を流用することは禁止されて"
            "いるため、まずpricing_snapshot.jsonを確認し単価を追加してください。")
    in_price, cached_price, out_price = PRICING_USD_PER_M[key]
    input_tokens = input_tokens or 0
    cached_input_tokens = cached_input_tokens or 0
    output_tokens = output_tokens or 0
    billable_in = max(input_tokens - cached_input_tokens, 0)
    usd = (billable_in / 1_000_000) * in_price
    usd += (cached_input_tokens / 1_000_000) * cached_price
    usd += (output_tokens / 1_000_000) * out_price
    return round(usd * USD_TO_JPY, 4)


def summarize_cost_log(log_path: str) -> dict:
    """cost_log.jsonl(er005_cost_logger形式)を読み、stage別/合計costを
    JPYで集計する。openai providerのみ対象(TTS/ASR等は別料金体系のため
    対象外)。model_idは各callの実際のAPI応答から記録された値をそのまま
    使う(想定modelではない)。"""
    entries = []
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    per_call = []
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success"):
            continue
        cost_jpy = cost_jpy_for_call(
            e.get("provider"), e.get("model_id"),
            e.get("input_tokens"), e.get("cached_input_tokens"), e.get("output_tokens"))
        per_call.append({
            "stage": e.get("stage"), "model_id": e.get("model_id"),
            "input_tokens": e.get("input_tokens"), "cached_input_tokens": e.get("cached_input_tokens"),
            "output_tokens": e.get("output_tokens"), "cost_jpy": cost_jpy,
        })

    by_stage: dict = {}
    for c in per_call:
        b = by_stage.setdefault(c["stage"], {"calls": 0, "cost_jpy": 0.0, "models_used": set()})
        b["calls"] += 1
        b["cost_jpy"] = round(b["cost_jpy"] + c["cost_jpy"], 4)
        b["models_used"].add(c["model_id"])
    for b in by_stage.values():
        b["models_used"] = sorted(b["models_used"])

    total_cost_jpy = round(sum(c["cost_jpy"] for c in per_call), 4)
    return {"by_stage": by_stage, "total_cost_jpy": total_cost_jpy, "total_calls": len(per_call),
            "per_call": per_call}
