# -*- coding: utf-8 -*-
import json

def load_tts(theme, level):
    return json.load(open(f"er006_output/pool_pilot_01/{theme}/{level}/audit/tts_generation_results.json", encoding="utf-8"))

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
USD_TO_JPY = 160

log = [json.loads(l) for l in open("er006_output/pool_pilot_01/raw_usage_log.jsonl", encoding="utf-8")]

for theme in ("pool_n4_supermarket", "pool_n5_cafes", "pool_n6_delivery"):
    unit_count = 0
    total_attempts = 0
    for level in ("b1b", "a2"):
        d = load_tts(theme, level)
        segs = d["segments"]
        kps = d.get("key_phrases", {})
        for name, entry in segs.items():
            log_a = entry.get("attempts_log") or entry.get("standard_attempts_log") or []
            fb = entry.get("fallback_attempts_log") or []
            n = max(len(log_a) + len(fb), 1)
            unit_count += 1
            total_attempts += n
        for rank, kp in kps.items():
            for lang in ("english", "japanese"):
                e = kp.get(lang, {})
                log_a = e.get("attempts_log") or e.get("standard_attempts_log") or []
                fb = e.get("fallback_attempts_log") or []
                n = max(len(log_a) + len(fb), 1)
                unit_count += 1
                total_attempts += n
    additional_attempts = total_attempts - unit_count
    theme_batch_entries = [e for e in log if e.get("theme")==theme and e.get("provider")=="gemini_batch"]
    total_batch_jpy = sum(e.get("cost_jpy") or 0 for e in theme_batch_entries)
    avg_cost_per_call = total_batch_jpy/len(theme_batch_entries) if theme_batch_entries else 0
    clean_jpy = unit_count * avg_cost_per_call
    additional_jpy = additional_attempts * avg_cost_per_call
    print(f"{theme}: units(clean baseline)={unit_count} total_attempts={total_attempts} additional_attempts={additional_attempts}")
    print(f"   batch_jpy_total={round(total_batch_jpy,1)} avg_per_call={round(avg_cost_per_call,3)} -> clean_est={round(clean_jpy,1)} additional_est={round(additional_jpy,1)}")
