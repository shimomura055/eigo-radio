# ============================================================
# er011_specfix_cost_compute_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01(補助): 実測costの分離集計
# ============================================================
# No.18 spec-fix regeneration(pool_n18_notifications_specfix_v2、Writer+
# Support、B1 retry含む)と、OPEN-107 opened TTS Diagnostic Trial
# (er011_output/open107_opened_tts_diagnostic_trial_01)を、混同せず
# 別々に実測usage(actual)×公式pricing snapshotで集計する。

from __future__ import annotations

import glob
import json
from collections import defaultdict

USD_JPY = 160.0
pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


LUNA_IN, LUNA_CACHED, LUNA_OUT = price("openai", "gpt-5.6-luna", "input_tokens"), \
    price("openai", "gpt-5.6-luna", "cached_input_tokens"), price("openai", "gpt-5.6-luna", "output_tokens")
def price_tiered(provider, model, meter, tier):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier") == tier)


GEMINI_PRO_IN = price_tiered("gemini", "gemini-2.5-pro-preview-tts", "input_tokens", "Standard")
GEMINI_PRO_OUT = price_tiered("gemini", "gemini-2.5-pro-preview-tts", "output_tokens", "Standard")
GEMINI_FLASH_IN = price_tiered("gemini", "gemini-3.1-flash-tts-preview", "input_tokens", "Standard")
GEMINI_FLASH_OUT = price_tiered("gemini", "gemini-3.1-flash-tts-preview", "output_tokens", "Standard")
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Diagnostic Trialの条件8
# (実Production関数generate_news_narration_wide_marginをそのまま呼んだ)
# はsync mode切替をこのTrialでは行わなかったため、実際にBatch API
# (batches.create)経由になった(cost_logger上のprovider="gemini_batch")。
# 公式Batch tier単価(Standardの50%オフ)で正しく計算する。
GEMINI_PRO_BATCH_IN = price_tiered("gemini", "gemini-2.5-pro-preview-tts", "input_tokens", "Batch")
GEMINI_PRO_BATCH_OUT = price_tiered("gemini", "gemini-2.5-pro-preview-tts", "output_tokens", "Batch")
ASR_IN = price("openai_asr", "gpt-4o-mini-transcribe", "input_tokens")
ASR_OUT = price("openai_asr", "gpt-4o-mini-transcribe", "output_tokens")


def call_cost_usd(r: dict) -> float:
    provider, model = r["provider"], r.get("model_id")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    if provider == "openai":
        billable_in = max(it - ct, 0)
        return (billable_in / 1e6) * LUNA_IN + (ct / 1e6) * LUNA_CACHED + (ot / 1e6) * LUNA_OUT
    if provider == "gemini":
        if model == "gemini-2.5-pro-preview-tts":
            return (it / 1e6) * GEMINI_PRO_IN + (ot / 1e6) * GEMINI_PRO_OUT
        if model == "gemini-3.1-flash-tts-preview":
            return (it / 1e6) * GEMINI_FLASH_IN + (ot / 1e6) * GEMINI_FLASH_OUT
        raise ValueError(f"unpriced gemini model: {model}")
    if provider == "gemini_batch":
        if model == "gemini-2.5-pro-preview-tts":
            return (it / 1e6) * GEMINI_PRO_BATCH_IN + (ot / 1e6) * GEMINI_PRO_BATCH_OUT
        raise ValueError(f"unpriced gemini_batch model: {model}")
    if provider == "openai_asr":
        return (it / 1e6) * ASR_IN + (ot / 1e6) * ASR_OUT
    raise ValueError(f"unpriced provider: {provider}")


def categorize(stage) -> str:
    if not stage:
        return "untagged_likely_asr"
    if stage.startswith("writer_b1"):
        return "writer_b1_incl_qa"
    if stage.startswith("writer_a2") or stage.startswith("writer"):
        return "writer_a2_incl_qa" if "a2" in stage else "writer_incl_qa"
    if stage.startswith("support_b1") or stage == "support":
        return "support"
    if stage.startswith("support_a2"):
        return "support_a2"
    if stage.startswith("support"):
        return "support_b1"
    if stage.startswith("phaseA"):
        return "trial_phase_a"
    if stage.startswith("phaseB"):
        return "trial_phase_b"
    return f"OTHER:{stage}"


def summarize(log_path: str) -> dict:
    records = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()]
    for r in records:
        r["_cost_usd"] = call_cost_usd(r)
    cat_totals = defaultdict(float)
    cat_counts = defaultdict(int)
    for r in records:
        cat = categorize(r.get("stage", ""))
        cat_totals[cat] += r["_cost_usd"]
        cat_counts[cat] += 1
    total_usd = sum(cat_totals.values())
    return {
        "log_path": log_path,
        "by_stage_category_jpy": {k: round(v * USD_JPY, 2) for k, v in cat_totals.items()},
        "call_counts": dict(cat_counts),
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * USD_JPY, 1),
        "total_calls": len(records),
    }


if __name__ == "__main__":
    production_logs = [
        "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/raw_usage_log.jsonl",
    ]
    trial_logs = [
        "er011_output/open107_opened_tts_diagnostic_trial_01/raw_usage_log.jsonl",
    ]

    print("=== Production spec-fix regeneration (No.18 specfix_v2) ===")
    prod_summary = summarize(production_logs[0])
    print(json.dumps(prod_summary, ensure_ascii=False, indent=2))

    print("\n=== OPEN-107 opened TTS Diagnostic Trial (isolated from Production) ===")
    trial_summary = summarize(trial_logs[0])
    print(json.dumps(trial_summary, ensure_ascii=False, indent=2))

    with open("er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/cost_summary_specfix.json",
              "w", encoding="utf-8") as f:
        json.dump(prod_summary, f, ensure_ascii=False, indent=2)
    with open("er011_output/open107_opened_tts_diagnostic_trial_01/cost_summary_trial.json",
              "w", encoding="utf-8") as f:
        json.dump(trial_summary, f, ensure_ascii=False, indent=2)

    print(f"\nGRAND TOTAL (Production + Trial, kept separate above): "
          f"Production=Y{prod_summary['total_jpy']} Trial=Y{trial_summary['total_jpy']}")
