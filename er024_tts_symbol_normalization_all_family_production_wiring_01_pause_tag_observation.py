# -*- coding: utf-8 -*-
"""TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01
Fable design decision #5: pause-tag observation trial (OBSERVATION ONLY,
not adopted as a mechanism). Sends exactly 2 short JA texts containing the
inline "<short pause>" tag to the current Production JA TTS model
(gemini-3.1-flash-tts-preview, voice=Charon) and records the ASR transcript
to see whether the tag is read aloud literally, produces a genuine pause,
or is silently dropped. standard_attempts=1/max_attempts=1 pins each call
to exactly one TTS + one ASR round trip (no retry loop, no fallback
budget), so this script makes exactly 2 TTS calls + 2 ASR calls total.
"""
import json
import os

import er005_cost_logger as cl
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = "er024_output/tts_symbol_normalization_all_family_production_wiring_01"
NARR_DIR = f"{OUT_DIR}/narration"
os.makedirs(NARR_DIR, exist_ok=True)
cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

CASES = [
    ("pause_tag_mid", "それは正しいです<short pause>でも待ってください。"),
    ("pause_tag_mid_2", "こんにちは<short pause>今日はいい天気ですね。"),
]

results = {}
for name, text in CASES:
    with cl.segment_context(name):
        r = voice01.generate_charon_japanese(
            text, f"{NARR_DIR}/{name}.wav", expected_substring="",
            max_attempts=1, standard_attempts=1)
    results[name] = {
        "input_text": text,
        "status": r.get("status"),
        "asr_text": r.get("asr_text"),
        "asr_verified": r.get("asr_verified"),
        "standard_attempts_log": r.get("standard_attempts_log") or r.get("attempts_log"),
    }
    print(f"[PAUSE-TAG][{name}] status={r.get('status')} asr_text={r.get('asr_text')!r}")

with open(f"{OUT_DIR}/pause_tag_observation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("DONE")
