# ============================================================
# er006_model_routing_contract_01_cost_recompute.py
# ER-006-MODEL-ROUTING-CONTRACT-01: Historical Actual vs Counterfactual(Approved
# Routing)Costの再計算
# ============================================================
# 重要: Historical Actual Spend(実際にSolへ支払った金額)は書き換えない。
# ここではCounterfactual(Approved Model RoutingがLunaだった場合の理論値)を
# 別途算出するだけであり、Historical Actualの上書きではない。
from __future__ import annotations

import json
from collections import defaultdict

USD_JPY = 160.0
LUNA_IN, LUNA_CACHED, LUNA_OUT = 0.20, 0.02, 1.20
SOL_IN, SOL_CACHED, SOL_OUT = 5.00, 0.50, 30.00
GEMINI_IN, GEMINI_OUT = 1.00, 20.00
AZURE_HOUR = 1.00
SEARCH_PER_1K = 10.00

THEMES = ["pool_benches", "pool_subscriptions", "pool_startups"]


def openai_cost(r, in_price, cached_price, out_price):
    it, ct, ot = r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0
    billable_in = max(it - ct, 0)
    return (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price


def search_cost(r):
    return ((r.get("web_search_call_count") or 0) / 1000) * SEARCH_PER_1K


def gemini_cost(r):
    return (r.get("input_tokens", 0) or 0) / 1e6 * GEMINI_IN + (r.get("output_tokens", 0) or 0) / 1e6 * GEMINI_OUT


def azure_cost(r):
    return (r.get("audio_duration_submitted_seconds", 0) or 0) / 3600 * AZURE_HOUR


with open("er006_output/pool_pilot_01/raw_usage_log.jsonl", encoding="utf-8") as f:
    RECORDS = [json.loads(l) for l in f]

actual_by_theme_stage = defaultdict(float)
counterfactual_by_theme_stage = defaultdict(float)
sol_excess_by_theme_stage = defaultdict(float)

for r in RECORDS:
    if not r.get("success"):
        continue
    theme, stage, provider, model_id = r["theme"], r["stage"], r["provider"], r.get("model_id") or ""
    if stage == "verify_hardening_01":
        continue  # ER-006-POOL-PREPROD-HARDENING-01の検証run(6episode本体ではない)
    key = (theme, stage)

    if provider == "openai":
        actual_usd = openai_cost(r, SOL_IN, SOL_CACHED, SOL_OUT) if "sol" in model_id else \
            openai_cost(r, LUNA_IN, LUNA_CACHED, LUNA_OUT)
        actual_usd += search_cost(r)
        # Counterfactual: Approved RoutingならこのProcessは常にLuna(Web検索は
        # 元々Approved RoutingでもWriter Fact Checkにweb_search toolが必要か
        # どうかは今回のスコープ外なので、実際に発生したsearch callの件数は
        # そのまま維持し、tokenのmodel単価だけをLunaへ置き換える)
        counterfactual_usd = openai_cost(r, LUNA_IN, LUNA_CACHED, LUNA_OUT) + search_cost(r)
        excess_usd = actual_usd - counterfactual_usd
    elif provider == "gemini":
        actual_usd = counterfactual_usd = gemini_cost(r)
        excess_usd = 0.0
    elif provider == "azure":
        actual_usd = counterfactual_usd = azure_cost(r)
        excess_usd = 0.0
    else:
        actual_usd = counterfactual_usd = excess_usd = 0.0

    actual_by_theme_stage[key] += actual_usd * USD_JPY
    counterfactual_by_theme_stage[key] += counterfactual_usd * USD_JPY
    sol_excess_by_theme_stage[key] += excess_usd * USD_JPY

# ------------------------------------------------------------
# 6episode合計
# ------------------------------------------------------------
total_actual = sum(actual_by_theme_stage.values())
total_counterfactual = sum(counterfactual_by_theme_stage.values())
total_excess = sum(sol_excess_by_theme_stage.values())

# stage別内訳(Writer/Writer FC/Support/Support FCに相当するstageのみ)
stage_breakdown = defaultdict(lambda: {"actual_jpy": 0.0, "counterfactual_jpy": 0.0, "excess_jpy": 0.0})
for (theme, stage), v in actual_by_theme_stage.items():
    cat = None
    if stage.startswith("writer_"):
        cat = "Writer(FactCheck/DeviationCheck込み)"
    elif stage.startswith("support_"):
        cat = "Support(Key Phrase/FactCheck込み)"
    elif stage.startswith("research_"):
        cat = "Research(元々Luna、影響なし)"
    elif stage.startswith("tts_"):
        cat = "TTS/ASR(元々Gemini/Azure、影響なし)"
    if cat:
        stage_breakdown[cat]["actual_jpy"] += v
        stage_breakdown[cat]["counterfactual_jpy"] += counterfactual_by_theme_stage[(theme, stage)]
        stage_breakdown[cat]["excess_jpy"] += sol_excess_by_theme_stage[(theme, stage)]

# ------------------------------------------------------------
# トピック別
# ------------------------------------------------------------
per_topic = {}
for theme in THEMES:
    keys = [k for k in actual_by_theme_stage if k[0] == theme]
    per_topic[theme] = {
        "actual_jpy": round(sum(actual_by_theme_stage[k] for k in keys), 1),
        "counterfactual_jpy": round(sum(counterfactual_by_theme_stage[k] for k in keys), 1),
        "excess_jpy": round(sum(sol_excess_by_theme_stage[k] for k in keys), 1),
    }

result = {
    "note": "Historical Actual Spendは実際に支払った金額(書き換えない)。Counterfactualは"
            "Approved Model Routing(Writer/Support系を全てLunaで統一)だった場合の理論値。",
    "six_episode_total": {
        "historical_actual_jpy": round(total_actual, 1),
        "counterfactual_approved_routing_jpy": round(total_counterfactual, 1),
        "sol_excess_loss_jpy": round(total_excess, 1),
    },
    "stage_breakdown": {k: {kk: round(vv, 1) for kk, vv in v.items()} for k, v in stage_breakdown.items()},
    "per_topic": per_topic,
}

with open("er006_output/pool_pilot_01/model_routing_cost_recompute.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(result, ensure_ascii=False, indent=2))
