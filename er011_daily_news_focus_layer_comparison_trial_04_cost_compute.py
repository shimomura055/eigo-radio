# ============================================================
# er011_daily_news_focus_layer_comparison_trial_04_cost_compute.py
# FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04 (Lane A) 補助
# ============================================================
# raw_usage_log.jsonl(cl.install()による全API call実測)を、公式pricing
# snapshot(er005_output/cost_baseline_01/pricing_snapshot.json、既存
# Trial-02/Trial-03 cost_computeと同一参照元・同一算出ロジック)で集計する。
from __future__ import annotations

import json
from collections import defaultdict

USD_JPY = 160.0
THEME_ID = "daily_news_focus_layer_comparison_trial_04"
LOG_PATH = f"er011_output/{THEME_ID}/raw_usage_log.jsonl"

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


LUNA_IN, LUNA_CACHED, LUNA_OUT = price("openai", "gpt-5.6-luna", "input_tokens"), \
    price("openai", "gpt-5.6-luna", "cached_input_tokens"), price("openai", "gpt-5.6-luna", "output_tokens")
SOL_IN, SOL_CACHED, SOL_OUT = price("openai", "gpt-5.6-sol", "input_tokens"), \
    price("openai", "gpt-5.6-sol", "cached_input_tokens"), price("openai", "gpt-5.6-sol", "output_tokens")
WEB_SEARCH_CALL = price("openai", "N/A (tool, all models)", "web_search_call")


def call_cost_usd(r: dict) -> float:
    provider, model = r["provider"], r.get("model_id")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    if provider == "openai":
        billable_in = max(it - ct, 0)
        if model == "gpt-5.6-luna":
            cost = (billable_in / 1e6) * LUNA_IN + (ct / 1e6) * LUNA_CACHED + (ot / 1e6) * LUNA_OUT
        elif model == "gpt-5.6-sol":
            cost = (billable_in / 1e6) * SOL_IN + (ct / 1e6) * SOL_CACHED + (ot / 1e6) * SOL_OUT
        else:
            raise ValueError(f"unpriced openai model: {model}")
        web_search_calls = r.get("web_search_call_count") or 0
        cost += (web_search_calls / 1000) * WEB_SEARCH_CALL
        return cost
    raise ValueError(f"unpriced provider (text-only trial, no TTS/ASR expected): {provider}")


records = [json.loads(l) for l in open(LOG_PATH, encoding="utf-8")]
for r in records:
    r["_cost_usd"] = call_cost_usd(r)

by_theme = defaultdict(float)
counts = defaultdict(int)
for r in records:
    by_theme[r["theme"]] += r["_cost_usd"]
    counts[r["theme"]] += 1

# theme名は f"{THEME_ID}_{condition}_{level_dir}_run{run_idx}" 形式のため、
# run番号・condition・level別の内訳もパースして提示する。
by_run = defaultdict(float)
by_condition = defaultdict(float)
by_level = defaultdict(float)
for theme, cost in by_theme.items():
    # 例: daily_news_focus_layer_comparison_trial_04_baseline_b1b_run1
    rest = theme[len(THEME_ID) + 1:]
    parts = rest.rsplit("_run", 1)
    if len(parts) == 2:
        cond_level, run_idx = parts
        cond_parts = cond_level.rsplit("_", 1)
        if len(cond_parts) == 2:
            condition, level = cond_parts
            by_run[f"run{run_idx}"] += cost
            by_condition[condition] += cost
            by_level[level] += cost

result = {
    "usd_jpy_rate": USD_JPY,
    "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/pricing_snapshot.json"
                   "(OFFICIAL_SOURCE、Trial-02/Trial-03 cost_computeと同一参照元・同一ロジック)。"
                   "text-onlyのためprovider=openai (Writer/FactCheck/LedgerDeviation/PointOverlapQA/"
                   "PointRolePlanning等)のみを想定。TTS/ASRのproviderが記録されていた場合はValueErrorで"
                   "停止する(想定外API callの見落とし検出)。",
    "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
    "by_run_jpy": {k: round(v * USD_JPY, 1) for k, v in by_run.items()},
    "by_condition_jpy": {k: round(v * USD_JPY, 1) for k, v in by_condition.items()},
    "by_level_jpy": {k: round(v * USD_JPY, 1) for k, v in by_level.items()},
    "call_counts": dict(counts),
    "total_usd": round(sum(by_theme.values()), 4),
    "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
    "total_calls": len(records),
}

with open(f"er011_output/{THEME_ID}/cost_summary.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(result, ensure_ascii=False, indent=2))
