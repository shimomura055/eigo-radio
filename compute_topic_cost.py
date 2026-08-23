# -*- coding: utf-8 -*-
import json, sys

USD_TO_JPY = 160
theme_id = sys.argv[1] if len(sys.argv) > 1 else "pool_n4_supermarket"

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"]==provider and p["model"]==model and p["meter"]==meter)

LUNA_IN = price("openai","gpt-5.6-luna","input_tokens")
LUNA_CACHED = price("openai","gpt-5.6-luna","cached_input_tokens")
LUNA_OUT = price("openai","gpt-5.6-luna","output_tokens")
ASR_IN = price("openai_asr","gpt-4o-mini-transcribe","input_tokens")
ASR_OUT = price("openai_asr","gpt-4o-mini-transcribe","output_tokens")
AZURE_HOUR = next(p["price"] for p in pricing if p["provider"]=="azure")

log = [json.loads(l) for l in open("er006_output/pool_pilot_01/raw_usage_log.jsonl", encoding="utf-8")]
entries = [e for e in log if e.get("theme") == theme_id]

luna_usd = 0.0
for e in entries:
    if e.get("provider") != "openai":
        continue
    it = e.get("input_tokens") or 0
    ct = e.get("cached_input_tokens") or 0
    ot = e.get("output_tokens") or 0
    billable_in = max(it - ct, 0)
    luna_usd += (billable_in/1_000_000)*LUNA_IN + (ct/1_000_000)*LUNA_CACHED + (ot/1_000_000)*LUNA_OUT

asr_openai_usd = 0.0
for e in entries:
    if e.get("provider") != "openai_asr":
        continue
    it = e.get("input_tokens") or 0
    ot = e.get("output_tokens") or 0
    asr_openai_usd += (it/1_000_000)*ASR_IN + (ot/1_000_000)*ASR_OUT

azure_seconds = sum(e.get("audio_duration_submitted_seconds") or 0 for e in entries if e.get("provider")=="azure")
azure_usd = (azure_seconds/3600) * AZURE_HOUR

batch_usd = sum(e.get("cost_usd") or 0 for e in entries if e.get("provider")=="gemini_batch")

batch_entries = [e for e in entries if e.get("provider")=="gemini_batch"]
batch_success = sum(1 for e in batch_entries if e.get("success"))
batch_fail = sum(1 for e in batch_entries if not e.get("success"))
openai_asr_calls = sum(1 for e in entries if e.get("provider")=="openai_asr")
azure_calls = sum(1 for e in entries if e.get("provider")=="azure")

total_usd = luna_usd + asr_openai_usd + azure_usd + batch_usd

print(f"=== {theme_id} Cost Summary ===")
print(f"Research+Writer+Support (Luna): ${round(luna_usd,4)} = ¥{round(luna_usd*USD_TO_JPY,1)}")
print(f"TTS (Gemini Batch): {len(batch_entries)} calls ({batch_success} success, {batch_fail} fail) = ${round(batch_usd,4)} = ¥{round(batch_usd*USD_TO_JPY,1)}")
print(f"ASR English (OpenAI, {openai_asr_calls} calls): ${round(asr_openai_usd,4)} = ¥{round(asr_openai_usd*USD_TO_JPY,1)}")
print(f"ASR Japanese (Azure, {azure_calls} calls, {round(azure_seconds,1)}s): ${round(azure_usd,4)} = ¥{round(azure_usd*USD_TO_JPY,1)}")
print(f"TOTAL: ${round(total_usd,4)} = ¥{round(total_usd*USD_TO_JPY,1)}")

with open(f"er006_output/pool_pilot_01/{theme_id}/cost_summary.json", "w", encoding="utf-8") as f:
    json.dump({
        "theme_id": theme_id,
        "research_writer_support_luna_jpy": round(luna_usd*USD_TO_JPY,1),
        "tts_batch_jpy": round(batch_usd*USD_TO_JPY,1),
        "tts_batch_calls": len(batch_entries), "tts_batch_success": batch_success, "tts_batch_fail": batch_fail,
        "asr_english_openai_jpy": round(asr_openai_usd*USD_TO_JPY,1), "asr_english_calls": openai_asr_calls,
        "asr_japanese_azure_jpy": round(azure_usd*USD_TO_JPY,1), "asr_japanese_calls": azure_calls,
        "total_jpy": round(total_usd*USD_TO_JPY,1),
    }, f, ensure_ascii=False, indent=2)
