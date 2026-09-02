# ============================================================
# er011_no18_cost_compute_01.py
# ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01(補助)
# ============================================================
# No.18のraw_usage_log.jsonl(per-theme、cl.install()による全API call実測)を、
# 既存の公式pricing snapshot(er005_output/cost_baseline_01/pricing_snapshot.json、
# compute_topic_cost.pyと同一の参照元)で集計する。Trial/推測priceは使わない。
# 本runのlogにはsegment名が記録されているため(cl.segment_context経由)、
# 旧3-topic集計(er006_pool_pilot_01_cost_time_compute.py)と異なり、
# retry/fallback overheadをsegment単位の実測(2回目以降の呼び出し)で
# 判定できる(推定ではなく実測)。
from __future__ import annotations

import json
from collections import defaultdict

USD_JPY = 160.0
THEME_ID = "pool_n18_notifications"
LOG_PATH = f"er006_output/pool_pilot_01/{THEME_ID}/raw_usage_log.jsonl"

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


LUNA_IN, LUNA_CACHED, LUNA_OUT = price("openai", "gpt-5.6-luna", "input_tokens"), \
    price("openai", "gpt-5.6-luna", "cached_input_tokens"), price("openai", "gpt-5.6-luna", "output_tokens")
GEMINI_PRO_IN = price("gemini", "gemini-2.5-pro-preview-tts", "input_tokens")
GEMINI_PRO_OUT = price("gemini", "gemini-2.5-pro-preview-tts", "output_tokens")
GEMINI_FLASH_IN = price("gemini", "gemini-3.1-flash-tts-preview", "input_tokens")
GEMINI_FLASH_OUT = price("gemini", "gemini-3.1-flash-tts-preview", "output_tokens")
ASR_IN = price("openai_asr", "gpt-4o-mini-transcribe", "input_tokens")
ASR_OUT = price("openai_asr", "gpt-4o-mini-transcribe", "output_tokens")

records = [json.loads(l) for l in open(LOG_PATH, encoding="utf-8")]


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
    if provider == "openai_asr":
        return (it / 1e6) * ASR_IN + (ot / 1e6) * ASR_OUT
    raise ValueError(f"unpriced provider: {provider}")


for r in records:
    r["_cost_usd"] = call_cost_usd(r)

STAGE_CATEGORY = {
    "research_evidence_pack": "research", "research_vfl": "research", "research_verification": "research",
    "writer_a2": "writer_a2_incl_qa", "writer_b1": "writer_b1_incl_qa",
    "support_a2": "support_a2", "support_b1": "support_b1", "support_b1_kp_retry": "support_b1",
    "tts_a2_sync": "tts_a2", "tts_b1_sync": "tts_b1",
}

cat_totals = defaultdict(float)
cat_counts = defaultdict(int)
for r in records:
    cat = STAGE_CATEGORY.get(r["stage"], f"OTHER:{r['stage']}")
    cat_totals[cat] += r["_cost_usd"]
    cat_counts[cat] += 1

# --- Audio(TTS/ASR)のretry/fallback実測分離: segment単位で2回目以降を retry とする ---
seg_seen = defaultdict(int)
audio_clean_usd = defaultdict(float)
audio_retry_usd = defaultdict(float)
retry_segments = defaultdict(list)
for r in records:
    if r["stage"] not in ("tts_a2_sync", "tts_b1_sync"):
        continue
    level = "a2" if r["stage"] == "tts_a2_sync" else "b1"
    seg_key = (level, r.get("segment"), r["provider"], r.get("api"))
    seg_seen[seg_key] += 1
    if seg_seen[seg_key] == 1:
        audio_clean_usd[level] += r["_cost_usd"]
    else:
        audio_retry_usd[level] += r["_cost_usd"]
        retry_segments[level].append({"segment": r.get("segment"), "provider": r["provider"],
                                       "occurrence": seg_seen[seg_key], "cost_usd": round(r["_cost_usd"], 6)})

result = {
    "usd_jpy_rate": USD_JPY,
    "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/pricing_snapshot.json"
                   "(OFFICIAL_SOURCE/PROJECT_INTERNAL_RECORD、compute_topic_cost.pyと同一参照元)。"
                   "TTS/ASRのretry/fallback判定は、本runのlogにsegment名が記録されている"
                   "ため実測(segment単位で2回目以降の呼び出しをretryとみなす。推定ではない)。"
                   "Writer段階(writer_a2/writer_b1)はPoint overlap QA・Fact Checker・"
                   "Ledger Deviation Checker・Local Rewrite Loopが同一logging_context内で"
                   "呼ばれるため、この粒度ではArticle生成本体とQA系呼び出しを個別に分離できない"
                   "(全てactual、合算のみ)。B1 Key Phrase retry(kp_retry補助script)はSupportに含む。",
    "by_stage_category_usd": {k: round(v, 4) for k, v in cat_totals.items()},
    "by_stage_category_jpy": {k: round(v * USD_JPY, 1) for k, v in cat_totals.items()},
    "call_counts": dict(cat_counts),
    "audio_clean_vs_retry_usd": {
        "a2_clean_usd": round(audio_clean_usd["a2"], 4), "a2_retry_usd": round(audio_retry_usd["a2"], 4),
        "b1_clean_usd": round(audio_clean_usd["b1"], 4), "b1_retry_usd": round(audio_retry_usd["b1"], 4),
    },
    "audio_clean_vs_retry_jpy": {
        "a2_clean_jpy": round(audio_clean_usd["a2"] * USD_JPY, 1), "a2_retry_jpy": round(audio_retry_usd["a2"] * USD_JPY, 1),
        "b1_clean_jpy": round(audio_clean_usd["b1"] * USD_JPY, 1), "b1_retry_jpy": round(audio_retry_usd["b1"] * USD_JPY, 1),
    },
    "retry_segment_detail": dict(retry_segments),
    "total_usd": round(sum(cat_totals.values()), 4),
    "total_jpy": round(sum(cat_totals.values()) * USD_JPY, 1),
    "total_calls": len(records),
}

report_table = {
    "Research": round(cat_totals.get("research", 0) * USD_JPY, 1),
    "Writer+QA/FactCheck/Rewrite (A2)": round(cat_totals.get("writer_a2_incl_qa", 0) * USD_JPY, 1),
    "Writer+QA/FactCheck/Rewrite (B1)": round(cat_totals.get("writer_b1_incl_qa", 0) * USD_JPY, 1),
    "Support (A2)": round(cat_totals.get("support_a2", 0) * USD_JPY, 1),
    "Support (B1, incl. KP retry)": round(cat_totals.get("support_b1", 0) * USD_JPY, 1),
    "A2 TTS+ASR (clean)": round(audio_clean_usd["a2"] * USD_JPY, 1),
    "A2 TTS+ASR (retry/fallback)": round(audio_retry_usd["a2"] * USD_JPY, 1),
    "B1 TTS+ASR (clean)": round(audio_clean_usd["b1"] * USD_JPY, 1),
    "B1 TTS+ASR (retry/fallback, incl. STOPPED in_one_line)": round(audio_retry_usd["b1"] * USD_JPY, 1),
    "TOTAL": round(sum(cat_totals.values()) * USD_JPY, 1),
}
result["report_table_jpy"] = report_table

with open(f"er006_output/pool_pilot_01/{THEME_ID}/cost_summary.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(report_table, ensure_ascii=False, indent=2))
print("TOTAL_JPY:", result["total_jpy"], "TOTAL_USD:", result["total_usd"], "TOTAL_CALLS:", result["total_calls"])
