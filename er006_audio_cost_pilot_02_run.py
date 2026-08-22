# ============================================================
# er006_audio_cost_pilot_02_run.py
# ER-006-AUDIO-COST-PILOT-02: Public Benches Audio Pilot再生成
# ============================================================
# Writer/Support/Key Phrase(Luna版)は既存(pool_benches_luna)の成果物を
# 再利用する(新規paid LLM呼び出しなし。b1b/parts.json・b1_support_
# texts.json・key_phrases/keywords_canonicalized.json (kp5 gloss修正済み)、
# a2側も同様、既にこのスクリプト実行前にコピー済み)。
# 本スクリプトが新たに実行するのはAudio(TTS+ASR+Assembly)段階のみで、
# 以下すべての新規配線が有効な状態で走る:
#   - ER-006-KP5-CANONICAL-BUG-01のcanonical placeholderゲート
#   - ER-006-ASR-OPENAI-PILOT-01のASR Provider Routing(英語=OpenAI mini)
#   - ER-006-ASR-VALIDATION-RESIDUAL-02のstreet/St.吸収
#   - ER-006-MASTER-AUDIO-STORE-01のMaster Audio Store

from __future__ import annotations

import sys
import time

sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er006_pool_pilot_01_audio as audio_mod
import er003_v1_n3_01_tts_generate as tts_gen

THEME_ID = "pool_benches_pilot_02"
OUT_DIR = "er006_output/pool_pilot_01/pool_benches_pilot_02"

tts_gen.JAPANESE_TITLES[THEME_ID] = "公共のベンチ、なぜ今見直されているのか"

theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}

t_start = time.time()
print("=== Audio(TTS+ASR+Assembly) Pilot再生成 ===")
audio_result = audio_mod.run_audio_for_theme(theme)

total_elapsed = round(time.time() - t_start, 1)
print(f"TOTAL_ELAPSED_SECONDS={total_elapsed}")
print("PILOT_02_AUDIO_RUN_DONE")
