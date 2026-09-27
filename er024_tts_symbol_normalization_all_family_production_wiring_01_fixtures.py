# -*- coding: utf-8 -*-
"""
TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01 Phase 2:
Runtime evidence(実TTS+実ASR、TTS_EXECUTION_MODE=STANDARD前提)。
代表fixtureを、実Production wrapper関数(n3_tts.generate_charon_japanese_
with_reading_safety / voice01.generate_charon_english)へそのまま通し、
Normalizer適用後のテキストが実際に読み上げられ、ASR検証(既存
Production Validatorそのもの)がPASSすることを確認する。
"""
import json
import os

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = "er024_output/tts_symbol_normalization_all_family_production_wiring_01"
NARR_DIR = f"{OUT_DIR}/narration"
os.makedirs(NARR_DIR, exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

CASES_JA = [
    ("ja_tilde_leading", "～を示す"),
    ("ja_tilde_mid", "地元の店を〜と結びつける"),
    ("ja_tilde_range", "中〜高強度"),
    ("ja_ellipsis_mid", "それは…違う"),
    ("ja_ellipsis_end", "それは違う…"),
    ("ja_colon", "理由は3つ:予算、人手、時間"),
]

CASES_EN = [
    ("en_ellipsis_mid", "Wait... that's wrong."),
    ("en_colon", "Three reasons: budget, staff, time."),
    ("en_semicolon", "Argentina advanced; England were sent home."),
]

results = {}

for name, text in CASES_JA:
    with cl.segment_context(name):
        r = n3_tts.generate_charon_japanese_with_reading_safety(
            text, f"{NARR_DIR}/{name}.wav", n3_tts.expected_substring_ja(text))
    results[name] = {
        "language": "ja", "input_text": text, "status": r.get("status"),
        "tts_input_text_after_reading_safety": r.get("tts_input_text_after_reading_safety"),
        "asr_text": r.get("asr_text"), "asr_verified": r.get("asr_verified"),
        "reason": r.get("reason"),
    }
    print(f"[FIXTURE][{name}] status={r.get('status')} tts_input={r.get('tts_input_text_after_reading_safety')!r} "
          f"asr_text={r.get('asr_text')!r}")

for name, text in CASES_EN:
    safe_text = n3_tts.tts_safe_en(text)
    with cl.segment_context(name):
        r = voice01.generate_charon_english(safe_text, f"{NARR_DIR}/{name}.wav")
    results[name] = {
        "language": "en", "input_text": text, "tts_input_text": safe_text,
        "status": r.get("status"), "asr_text": r.get("asr_text"),
    }
    print(f"[FIXTURE][{name}] status={r.get('status')} tts_input={safe_text!r} asr_text={r.get('asr_text')!r}")

with open(f"{OUT_DIR}/fixture_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("DONE")
