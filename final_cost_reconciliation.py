# -*- coding: utf-8 -*-
import json

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"]==provider and p["model"]==model and p["meter"]==meter)
LUNA_IN = price("openai","gpt-5.6-luna","input_tokens")
LUNA_CACHED = price("openai","gpt-5.6-luna","cached_input_tokens")
LUNA_OUT = price("openai","gpt-5.6-luna","output_tokens")
ASR_IN = price("openai_asr","gpt-4o-mini-transcribe","input_tokens")
ASR_OUT = price("openai_asr","gpt-4o-mini-transcribe","output_tokens")
AZURE_HOUR = next(p["price"] for p in pricing if p["provider"]=="azure")
USD_TO_JPY = 160

log = [json.loads(l) for l in open("er006_output/pool_pilot_01/raw_usage_log.jsonl", encoding="utf-8")]

def load_tts(theme, level):
    return json.load(open(f"er006_output/pool_pilot_01/{theme}/{level}/audit/tts_generation_results.json", encoding="utf-8"))

THEMES = ["pool_n4_supermarket", "pool_n5_cafes", "pool_n6_delivery"]

# 1. TTS/ASR unit vs attempt counts (precise, per-segment)
tts_additional_ratio = {}
for theme in THEMES:
    unit_count = 0
    total_attempts = 0
    for level in ("b1b", "a2"):
        d = load_tts(theme, level)
        for name, entry in d["segments"].items():
            n = max(len((entry.get("attempts_log") or entry.get("standard_attempts_log") or [])) +
                    len(entry.get("fallback_attempts_log") or []), 1)
            unit_count += 1; total_attempts += n
        for rank, kp in d.get("key_phrases", {}).items():
            for lang in ("english","japanese"):
                e = kp.get(lang, {})
                n = max(len((e.get("attempts_log") or e.get("standard_attempts_log") or [])) +
                        len(e.get("fallback_attempts_log") or []), 1)
                unit_count += 1; total_attempts += n
    tts_additional_ratio[theme] = {"unit": unit_count, "total": total_attempts,
                                     "additional_frac": (total_attempts-unit_count)/total_attempts}

# 2. Luna (Research+Writer+Support) actual totals
def luna_usd(theme):
    total = 0.0
    for e in log:
        if e.get("theme")==theme and e.get("provider")=="openai":
            it=e.get("input_tokens") or 0; ct=e.get("cached_input_tokens") or 0; ot=e.get("output_tokens") or 0
            total += (max(it-ct,0)/1e6)*LUNA_IN + (ct/1e6)*LUNA_CACHED + (ot/1e6)*LUNA_OUT
    return total

def batch_usd(theme):
    return sum(e.get("cost_usd") or 0 for e in log if e.get("theme")==theme and e.get("provider")=="gemini_batch")

def asr_openai_usd(theme):
    total=0.0
    for e in log:
        if e.get("theme")==theme and e.get("provider")=="openai_asr":
            it=e.get("input_tokens") or 0; ot=e.get("output_tokens") or 0
            total += (it/1e6)*ASR_IN + (ot/1e6)*ASR_OUT
    return total

def asr_azure_usd(theme):
    secs = sum(e.get("audio_duration_submitted_seconds") or 0 for e in log if e.get("theme")==theme and e.get("provider")=="azure")
    return (secs/3600)*AZURE_HOUR

# Research+Writer+Support clean benchmark = avg(No.5, No.6) actual (both converged in 1 round)
rws_actual = {t: luna_usd(t)*USD_TO_JPY for t in THEMES}
clean_benchmark_rws = (rws_actual["pool_n5_cafes"] + rws_actual["pool_n6_delivery"]) / 2

print("=== Research+Writer+Support ===")
for t in THEMES:
    actual = rws_actual[t]
    clean = clean_benchmark_rws if t == "pool_n4_supermarket" else actual
    additional = max(actual - clean, 0)
    print(f"{t}: actual=¥{actual:.1f} clean_est=¥{clean:.1f} additional_est=¥{additional:.1f}")

print("\n=== TTS(Batch) ===")
tts_jpy = {}
for t in THEMES:
    actual = batch_usd(t)*USD_TO_JPY
    frac = tts_additional_ratio[t]["additional_frac"]
    additional = actual*frac
    clean = actual - additional
    tts_jpy[t] = {"actual": actual, "clean": clean, "additional": additional}
    print(f"{t}: actual=¥{actual:.1f} clean=¥{clean:.1f} additional=¥{additional:.1f} (additional_frac={frac:.3f}, units={tts_additional_ratio[t]['unit']}, attempts={tts_additional_ratio[t]['total']})")

print("\n=== ASR (English OpenAI + Japanese Azure combined) ===")
asr_jpy = {}
for t in THEMES:
    actual = asr_openai_usd(t)*USD_TO_JPY + asr_azure_usd(t)*USD_TO_JPY
    frac = tts_additional_ratio[t]["additional_frac"]  # ASR calls pair 1:1 with TTS attempts
    additional = actual*frac
    clean = actual - additional
    asr_jpy[t] = {"actual": actual, "clean": clean, "additional": additional}
    print(f"{t}: actual=¥{actual:.1f} clean=¥{clean:.1f} additional=¥{additional:.1f}")

print("\n=== GRAND TOTAL per Topic ===")
grand = {}
for t in THEMES:
    rws_a = rws_actual[t]
    rws_c = clean_benchmark_rws if t == "pool_n4_supermarket" else rws_a
    rws_add = max(rws_a-rws_c,0)
    total_clean = rws_c + tts_jpy[t]["clean"] + asr_jpy[t]["clean"]
    total_additional = rws_add + tts_jpy[t]["additional"] + asr_jpy[t]["additional"]
    total_actual = total_clean + total_additional
    grand[t] = (total_clean, total_additional, total_actual)
    print(f"{t}: Clean=¥{total_clean:.1f} Additional=¥{total_additional:.1f} Total=¥{total_actual:.1f} Additional%={total_additional/total_actual*100:.1f}%")

avg_clean = sum(g[0] for g in grand.values())/3
avg_add = sum(g[1] for g in grand.values())/3
avg_total = sum(g[2] for g in grand.values())/3
print(f"\n3-Topic AVERAGE: Clean=¥{avg_clean:.1f} Additional=¥{avg_add:.1f} Total=¥{avg_total:.1f} Additional%={avg_add/avg_total*100:.1f}%")
