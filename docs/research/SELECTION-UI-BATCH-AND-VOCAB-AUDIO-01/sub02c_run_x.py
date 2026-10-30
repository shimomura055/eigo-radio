# SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02C 実TTS証跡(X)。CLIの`--stage tts`が実行する本番関数
# generate_family_x_b1_segments / generate_family_x_a2_segments をそのまま呼ぶ(CLIのRF/予算確認以外は同一)。
# 対象=月のしわ run_reselect_01 のコピーrun(元runは不変)。cwd=主worktree(実wav/Master Audio Storeがある場所)、コードは一時worktree。
import json
import os
import shutil
import sys

WT = sys.argv[1]
MAIN = sys.argv[2]
sys.path.insert(0, WT)
os.chdir(MAIN)
os.environ.setdefault("PYTHONUTF8", "1")
from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(MAIN, ".env"))   # find_dotenvは呼出ファイル基準のため主worktreeの.envを明示
import er019_family_x_audio_production_runner_01 as xr  # noqa: E402
import er005_cost_logger as cl  # noqa: E402

OUT = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_vocab_ev_02c_01"
BACKEND = "speech_metadata_flash_lite"
PROFILE = "fx_20261017"
ep = json.load(open(f"{OUT}/entry_point.json", encoding="utf-8"))
if os.path.exists(f"{OUT}/raw_usage_log.jsonl") and not os.path.exists(f"{OUT}/raw_usage_log_orig_copy.jsonl"):
    shutil.move(f"{OUT}/raw_usage_log.jsonl", f"{OUT}/raw_usage_log_orig_copy.jsonl")
cl.install(f"{OUT}/raw_usage_log.jsonl")
with cl.logging_context("moon_shrinking", "tts"):
    xr.generate_family_x_b1_segments(OUT, tts_backend=BACKEND, style_profile=PROFILE)
    xr.generate_family_x_a2_segments(OUT, japanese_title=ep["japanese_title"], tts_backend=BACKEND, style_profile=PROFILE)
jpy, by = xr.compute_cost_jpy_so_far(f"{OUT}/raw_usage_log.jsonl")
print("COST_JPY", jpy, by)
