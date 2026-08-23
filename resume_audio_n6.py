# -*- coding: utf-8 -*-
import sys, time, json
sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er006_pool_pilot_01_audio  # noqa: F401  (side effect: JAPANESE_TITLES.update for pool_n4/n5/n6)
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_n3_01_assemble as asm

theme = {"theme_id": "pool_n6_delivery", "out_dir": "er006_output/pool_pilot_01/pool_n6_delivery"}
timing = {}

t1 = time.time()
with cl.logging_context(theme["theme_id"], "tts_a2"):
    a2_tts = tts_gen.generate_a2_segments(theme)
timing["tts_a2"] = round(time.time() - t1, 2)
print("A2 TTS:", a2_tts)

t2 = time.time()
with cl.logging_context(theme["theme_id"], "assemble_a2"):
    a2_assemble = asm.stage_assemble_a2(theme)
timing["assemble_a2"] = round(time.time() - t2, 2)
print("A2 assemble:", a2_assemble)

print("RESUME_DONE", json.dumps(timing))
