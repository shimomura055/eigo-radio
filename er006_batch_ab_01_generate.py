# ============================================================
# er006_batch_ab_01_generate.py
# ER-006-TTS-BATCH-HUMAN-AB-01: Standard vs Batch 実コンテンツA/B
# ============================================================
# 代表segment(最低限の指定分)を、Standard(既にPilot本番runで生成済みの
# ものをそのまま使う、新規Standard呼び出しはしない)とBatch(本スクリプトで
# 新規生成)で比較する。spoken text/voice/style instruction/Structured
# Separation/speaker/pacingはすべて本番と完全に同一(p4c.build_tts_prompt
# 経由で本番と同じprompt構築関数を再利用)。

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, '.')
import er002_common as common
import er002_gemini_client as gc
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
from google.genai import types

OUT_DIR = "er006_output/pool_pilot_01/pool_benches_pilot_02"
BATCH_OUT_DIR = f"{OUT_DIR}/batch_ab"
os.makedirs(BATCH_OUT_DIR, exist_ok=True)

client = gc.make_client()

parts_b1 = json.load(open(f"{OUT_DIR}/b1b/parts.json", encoding="utf-8"))
support_a2 = json.load(open(f"{OUT_DIR}/a2/a2_support_texts.json", encoding="utf-8"))
kp_b1 = json.load(open(f"{OUT_DIR}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
kp1 = next(it for it in kp_b1["items"] if it["rank"] == 1)

AOEDE = "Aoede"
CHARON = "Charon"

# (label, text, style_prefix, voice, model, standard_wav_path)
SEGMENTS = [
    ("english_long_story", parts_b1["part1"], p9a.ENGLISH_STYLE_PREFIX, AOEDE, p9a.ENGLISH_MODEL_NAME,
     f"{OUT_DIR}/b1b/narration/full_story_part1.wav"),
    ("english_point", parts_b1["point_one_body"], p9a.ENGLISH_STYLE_PREFIX, AOEDE, p9a.ENGLISH_MODEL_NAME,
     f"{OUT_DIR}/b1b/narration/point_one.wav"),
    ("english_key_phrase", kp1["used_form"], p9a.ENGLISH_STYLE_PREFIX, AOEDE, p9a.ENGLISH_MODEL_NAME,
     f"{OUT_DIR}/b1b/narration/kp1_en.wav"),
    ("japanese_support_preview", support_a2["preview"], p9a.JAPANESE_STYLE_PREFIX, AOEDE, p9a.JAPANESE_MODEL_NAME,
     f"{OUT_DIR}/a2/narration/preview.wav"),
    ("japanese_key_phrase_meaning", kp1["japanese_gloss"], p9a.JAPANESE_STYLE_PREFIX, CHARON, p9a.JAPANESE_MODEL_NAME,
     f"{OUT_DIR}/b1b/narration/kp1_ja_charon.wav"),
]


def build_request(text, style_prefix, voice, model):
    prompt = p4c.build_tts_prompt(text, style_prefix)
    speech_config = gc.build_speech_config(voice)
    return types.InlinedRequest(
        model=model,
        contents=[types.Content(parts=[types.Part(text=prompt)], role="user")],
        config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=speech_config),
    )


results = []
jobs = []
for label, text, style_prefix, voice, model, standard_wav in SEGMENTS:
    req = build_request(text, style_prefix, voice, model)
    job = client.batches.create(model=model, src=[req])
    print(f"[{label}] batch job created: {job.name} state={job.state}")
    jobs.append((label, text, voice, model, standard_wav, job.name))

print("=== waiting for batch jobs to complete ===")
for label, text, voice, model, standard_wav, job_name in jobs:
    t0 = time.time()
    while True:
        job = client.batches.get(name=job_name)
        state = str(job.state)
        if state.endswith("SUCCEEDED") or state.endswith("FAILED") or state.endswith("CANCELLED"):
            break
        time.sleep(3)
        if time.time() - t0 > 180:
            print(f"[{label}] TIMEOUT waiting for batch job")
            break
    elapsed = round(time.time() - t0, 1)
    entry = {"label": label, "voice": voice, "model": model, "job_name": job_name,
              "state": str(job.state), "elapsed_seconds": elapsed, "standard_wav": standard_wav}
    if state.endswith("SUCCEEDED"):
        resp = job.dest.inlined_responses[0]
        if resp.error:
            entry["error"] = str(resp.error)
        else:
            audio_part = next(p for p in resp.response.candidates[0].content.parts if p.inline_data)
            pcm = audio_part.inline_data.data
            batch_wav_path = f"{BATCH_OUT_DIR}/{label}_batch.wav"
            samples = common.pcm_bytes_to_float_mono(pcm)
            common.write_wav_float(batch_wav_path, samples, common.SAMPLE_RATE, 1)
            entry["batch_wav"] = batch_wav_path
            entry["batch_duration_seconds"] = round(len(samples) / common.SAMPLE_RATE, 3)
            usage = resp.response.usage_metadata
            entry["usage"] = {
                "prompt_token_count": usage.prompt_token_count,
                "candidates_token_count": usage.candidates_token_count,
            }
    results.append(entry)
    print(f"[{label}] {entry.get('state')} elapsed={elapsed}s -> {entry.get('batch_wav', entry.get('error'))}")

with open(f"{BATCH_OUT_DIR}/batch_ab_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("BATCH_AB_DONE")
