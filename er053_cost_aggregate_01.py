# -*- coding: utf-8 -*-
"""er053_cost_aggregate_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。stage別コスト集計の非OpenAI(Gemini)対応版(G-3)。

既存 er019_family_x_entertainment_production_runner_01.compute_stage_cost_breakdown は provider=="openai" のみを
集計する。その関数は**変更しない**(挙動を変えると既存runの費用表示が変わるため)。本moduleは同じ式の
「openai+gemini対応版」を新規関数として提供する。呼び出し側の切替(runnerのcost.json生成をこちらへ)はC3で行う。

式は既存関数と同じ(input×in + output×out [+ web_search])。cached tokenの割引は適用しない(保守側、既存と同じ)。
単価未登録は efam._load_pricing() の price() が PricingNotFoundError(fail-closed)。
stage tag は RF module が `risk_flag.<model_key>.<A3|A4>.<level>` を付ける(Level別・model別・条件別に集計できる)。
"""
from __future__ import annotations

import json
import os

import er012_e_family_entertainment_two_level_runner_01 as efam

BILLED_PROVIDERS = ("openai", "gemini")


def compute_stage_cost_breakdown_multi(cost_log_path: str) -> dict:
    """{"by_stage_jpy": {stage: jpy}, "total_jpy": jpy, "by_provider_jpy": {provider: jpy}}。ログ無しは空。"""
    if not os.path.exists(cost_log_path):
        return {"by_stage_jpy": {}, "total_jpy": 0.0, "by_provider_jpy": {}}
    price = efam._load_pricing()
    by_stage, by_provider, total = {}, {}, 0.0
    with open(cost_log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            stage = rec.get("stage") or "UNTAGGED"
            usd = 0.0
            if provider in BILLED_PROVIDERS and model:
                if rec.get("success") is False:
                    continue                      # 失敗呼出はusageが無い(課金されない)
                usd += (rec.get("input_tokens") or 0) * price(provider, model, "input_tokens") / 1e6
                usd += (rec.get("output_tokens") or 0) * price(provider, model, "output_tokens") / 1e6
                if provider == "openai":
                    usd += efam.web_search_call_usd(rec, price)
            total += usd
            by_stage[stage] = by_stage.get(stage, 0.0) + usd
            if usd:
                by_provider[provider] = by_provider.get(provider, 0.0) + usd
    j = efam.USD_JPY
    return {"by_stage_jpy": {k: round(v * j, 3) for k, v in by_stage.items()},
            "total_jpy": round(total * j, 3),
            "by_provider_jpy": {k: round(v * j, 3) for k, v in by_provider.items()}}


def rf_stage_summary(by_stage_jpy: dict) -> dict:
    """by_stage_jpy から risk_flag.<model_key>.<cond>.<level> だけを {level: {model_key: {cond: jpy}}} に整理する。"""
    out = {}
    for stage, jpy in by_stage_jpy.items():
        parts = stage.split(".")
        if len(parts) == 4 and parts[0] == "risk_flag":
            _, mk, cd, level = parts
            out.setdefault(level, {}).setdefault(mk, {})[cd] = jpy
    return out
