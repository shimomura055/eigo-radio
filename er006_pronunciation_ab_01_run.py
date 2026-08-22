# ============================================================
# er006_pronunciation_ab_01_run.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: 4条件A/B/C/D検証
# ============================================================
# Condition A: 既存TTS(pronunciation hintなし) -> OpenAI Primary
#              (既存Pilot-02の実測結果を再利用、新規TTS/ASRなし)
# Condition B: Pronunciation-aware TTS(新規生成) -> OpenAI Primary
# Condition C: Condition Bの音声 -> Azure Secondary(Phrase Listなし)
# Condition D: Condition Bの音声 -> Azure Secondary(Phrase Listあり)

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

import er002_common as common
import er002_gemini_client as gc
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_pronunciation_ledger_01 as ledger
import er006_pronunciation_tts_injection_01 as inject
import er006_secondary_asr_01 as secondary

cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

OUT_DIR = "er006_output/pool_pilot_01/pool_benches_pilot_02"
FIXTURE_DIR = f"{OUT_DIR}/pronunciation/fixtures"
os.makedirs(FIXTURE_DIR, exist_ok=True)

FIXTURES = [
    {
        "name": "ottoni_b1_point_one",
        "entities": ["Ottoni"],
        "canonical_text": json.load(open(f"{OUT_DIR}/b1b/parts.json", encoding="utf-8"))["point_one_body"],
        "existing_wav": f"{OUT_DIR}/b1b/narration/point_one.wav",
        "known_failing": True,
    },
    {
        "name": "malmo_triangeln_mta_b1_point_two",
        "entities": ["Malmö", "Triangeln", "MTA"],
        "canonical_text": json.load(open(f"{OUT_DIR}/b1b/parts.json", encoding="utf-8"))["point_two_body"],
        "existing_wav": f"{OUT_DIR}/b1b/narration/point_two.wav",
        "known_failing": False,  # 前回Pilotで既にOK(Validator修正済み)、hintが更に安定させるか確認
    },
    {
        "name": "boavida_a2_full_story_part2_control",
        "entities": ["Boavida"],
        "canonical_text": json.load(open(f"{OUT_DIR}/a2/parts.json", encoding="utf-8"))["part2"],
        "existing_wav": f"{OUT_DIR}/a2/narration/full_story_part2.wav",
        "known_failing": False,  # 既にOK、hintが劣化させないことの確認用control
    },
]


def generate_condition_b(text: str, out_path: str, entities: list[str]) -> dict:
    """Pronunciation-aware TTS(voice=Aoede、本番と同じmodel)。
    spoken text(text)自体は一切変更しない。style_prefixだけhint付与。"""
    augmented_prefix, hints_used = inject.augment_style_prefix_with_pronunciation(
        p9a.ENGLISH_STYLE_PREFIX, text)
    prompt = p4c.build_tts_prompt(text, augmented_prefix)
    client = gc.make_client()
    speech_config = gc.build_speech_config("Aoede")
    call_fn = gc.make_tts_call_fn("Aoede", client=client)
    pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": str(err)}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE, safety_margin_seconds=0.35)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間検出失敗"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    return {"status": "OK", "path": out_path, "hints_used": hints_used, "augmented_prefix": augmented_prefix,
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 3)}


results = []
for fixture in FIXTURES:
    print(f"=== {fixture['name']} ===")
    entry = {"name": fixture["name"], "entities": fixture["entities"], "canonical_text": fixture["canonical_text"]}

    # --- Condition A: 既存音声 -> Primary(OpenAI mini) ---
    with cl.logging_context("pool_benches_pilot_02", "pronunciation_ab_condition_a"):
        text_a, err_a = routing.transcribe(fixture["existing_wav"], language="en-US")
    cls_a = val.classify_asr_match(fixture["canonical_text"], text_a) if text_a else None
    entry["condition_a"] = {"asr_text": text_a, "error": err_a,
                              "classification": cls_a.classification if cls_a else "TTS_FAILURE",
                              "should_pass": cls_a.should_pass if cls_a else False}
    print("  Condition A:", entry["condition_a"]["classification"])

    # --- Condition B: Pronunciation-aware TTS(新規生成) -> Primary ---
    b_wav = f"{FIXTURE_DIR}/{fixture['name']}_condition_b.wav"
    gen_b = generate_condition_b(fixture["canonical_text"], b_wav, fixture["entities"])
    entry["condition_b_generation"] = {k: v for k, v in gen_b.items() if k != "augmented_prefix"}
    entry["augmented_style_prefix"] = gen_b.get("augmented_prefix")
    if gen_b["status"] != "OK":
        entry["condition_b"] = {"error": "TTS generation failed"}
        results.append(entry)
        continue
    with cl.logging_context("pool_benches_pilot_02", "pronunciation_ab_condition_b"):
        text_b, err_b = routing.transcribe(b_wav, language="en-US")
    cls_b = val.classify_asr_match(fixture["canonical_text"], text_b) if text_b else None
    entry["condition_b"] = {"asr_text": text_b, "error": err_b,
                              "classification": cls_b.classification if cls_b else "TTS_FAILURE",
                              "should_pass": cls_b.should_pass if cls_b else False}
    print("  Condition B:", entry["condition_b"]["classification"])

    # --- Condition C: Condition Bの音声 -> Azure Secondary(Phrase Listなし) ---
    with cl.logging_context("pool_benches_pilot_02", "pronunciation_ab_condition_c"):
        text_c, err_c = secondary.get_full_text_via_azure_stt_with_phrase_list(
            b_wav, language="en-US", phrases=None)
    cls_c = val.classify_asr_match(fixture["canonical_text"], text_c) if text_c else None
    entry["condition_c"] = {"asr_text": text_c, "error": err_c,
                              "classification": cls_c.classification if cls_c else "TTS_FAILURE",
                              "should_pass": cls_c.should_pass if cls_c else False}
    print("  Condition C:", entry["condition_c"]["classification"])

    # --- Condition D: Condition Bの音声 -> Azure Secondary(Phrase Listあり) ---
    ledger_entries = []
    for e in fixture["entities"]:
        hits = ledger.get_hint_for_text(e, min_confidence="low")
        ledger_entries.extend(hits)
    phrase_list = [h["canonical_spelling"] for h in ledger_entries] or fixture["entities"]
    with cl.logging_context("pool_benches_pilot_02", "pronunciation_ab_condition_d"):
        text_d, err_d = secondary.get_full_text_via_azure_stt_with_phrase_list(
            b_wav, language="en-US", phrases=phrase_list)
    cls_d = val.classify_asr_match(fixture["canonical_text"], text_d) if text_d else None
    entry["condition_d"] = {"asr_text": text_d, "error": err_d,
                              "classification": cls_d.classification if cls_d else "TTS_FAILURE",
                              "should_pass": cls_d.should_pass if cls_d else False,
                              "phrase_list": phrase_list}
    print("  Condition D:", entry["condition_d"]["classification"], "phrase_list=", phrase_list)

    results.append(entry)

with open(f"{OUT_DIR}/pronunciation/ab_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("PRONUNCIATION_AB_DONE")
