# ============================================================
# er011_no18_evidence_compression_a_precision_21r_cost_compute.py
# ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R
# ============================================================
# er011_specfix_cost_compute_01.pyと同一の実測usage×公式pricing snapshot
# 集計手法を、今回のarticles再生成(Writer reuse-stub+Evidence Compression
# +QA一式)・audio stage(変更segmentのみ再TTS+Assembly)の2ログへ適用する。
# Writerは新規LLM呼び出しをしていない(reuse-stub)ため、articles側costは
# Point Role Planning・Evidence Compression Editor・Point Overlap/Value QA・
# Fact Checker・Ledger Deviation・Local Rewriteのみを反映する。

from __future__ import annotations

import json
from collections import defaultdict

USD_JPY = 160.0
pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


def price_tiered(provider, model, meter, tier):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier") == tier)


LUNA_IN = price("openai", "gpt-5.6-luna", "input_tokens")
LUNA_CACHED = price("openai", "gpt-5.6-luna", "cached_input_tokens")
LUNA_OUT = price("openai", "gpt-5.6-luna", "output_tokens")
GEMINI_PRO_IN = price_tiered("gemini", "gemini-2.5-pro-preview-tts", "input_tokens", "Standard")
GEMINI_PRO_OUT = price_tiered("gemini", "gemini-2.5-pro-preview-tts", "output_tokens", "Standard")
GEMINI_FLASH_IN = price_tiered("gemini", "gemini-3.1-flash-tts-preview", "input_tokens", "Standard")
GEMINI_FLASH_OUT = price_tiered("gemini", "gemini-3.1-flash-tts-preview", "output_tokens", "Standard")
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
        return 0.0
    if provider == "openai_asr":
        return (it / 1e6) * ASR_IN + (ot / 1e6) * ASR_OUT
    return 0.0


def summarize(log_path: str) -> dict:
    records = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()]
    for r in records:
        r["_cost_usd"] = call_cost_usd(r)
    cat_totals = defaultdict(float)
    cat_counts = defaultdict(int)
    for r in records:
        cat = r.get("stage") or "untagged"
        cat_totals[cat] += r["_cost_usd"]
        cat_counts[cat] += 1
    total_usd = sum(cat_totals.values())
    return {
        "log_path": log_path,
        "by_stage_jpy": {k: round(v * USD_JPY, 2) for k, v in cat_totals.items()},
        "call_counts": dict(cat_counts),
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * USD_JPY, 1),
        "total_calls": len(records),
    }


if __name__ == "__main__":
    import os
    OUT_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r"
    logs = {
        "articles": f"{OUT_DIR}/raw_usage_log_21r_articles.jsonl",
        "audio": f"{OUT_DIR}/raw_usage_log_21r_audio.jsonl",
    }
    grand_total_jpy = 0.0
    all_summaries = {}
    for label, path in logs.items():
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            print(f"=== {label}: ログなし/空(スキップ) ===")
            continue
        s = summarize(path)
        all_summaries[label] = s
        grand_total_jpy += s["total_jpy"]
        print(f"=== {label} ===")
        print(json.dumps(s, ensure_ascii=False, indent=2))

    with open(f"{OUT_DIR}/cost_summary_21r.json", "w", encoding="utf-8") as f:
        json.dump({"summaries": all_summaries, "grand_total_jpy": round(grand_total_jpy, 1)},
                   f, ensure_ascii=False, indent=2)
    print(f"\nGRAND TOTAL (articles + audio): Y{round(grand_total_jpy, 1)}")
