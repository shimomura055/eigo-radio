# ============================================================
# er006_pool_benches_luna_run.py
# ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Luna版Public Benches生成
# ============================================================
# Researchは再利用する(既存のEvidence Pack/VFL/Verification/Ledgerを再実行
# しない)。Writer/Support/Key PhraseはModel Routing Contractにより自動的に
# Luna(SSOT)を使う(このスクリプト側でのmodel指定は不要、run_one_pattern等
# 本番関数側で既にfail-closed検証済み)。
from __future__ import annotations

import sys
import time

sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er003_v1_en_direct_ab_01_generate as ab01
import er006_pool_pilot_01_writer as writer_mod
import er006_pool_pilot_01_support as support_mod
import er006_pool_pilot_01_audio as audio_mod
import er006_pool_pilot_01_topics as topics
import er003_v1_en_direct_vfl_01_generate as vfl01

THEME_ID = "pool_benches_luna"  # Cost/Logをpool_benches(Sol版)と分離するため専用theme_idを使う
OUT_DIR = "er006_output/pool_pilot_01/pool_benches_luna"
LEDGER_PATH = "er006_output/pool_pilot_01/pool_benches/research/verified_fact_ledger.txt"
TOPIC = topics.TOPIC_JA["pool_benches"]

client = vfl01.get_client()
master_full_text = ab01.load_master_full_text()

t_start = time.time()

print("=== [1/3] Writer(B1/A2)+Fact Check+Deviation Check(Luna) ===")
writer_result = writer_mod.run_writer_for_theme(
    client, master_full_text, THEME_ID, TOPIC, LEDGER_PATH, OUT_DIR)
print("writer done:", {k: v.get("status") for k, v in writer_result["results"].items()})

print("=== [2/3] Support(B1/A2)+Key Phrase+Support Fact Check(Luna) ===")
ledger_text = open(LEDGER_PATH, encoding="utf-8").read()
support_result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text)

print("=== [3/3] TTS+ASR+Assembly(Audio Validation配線済み) ===")
theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
audio_result = audio_mod.run_audio_for_theme(theme)

total_elapsed = round(time.time() - t_start, 1)
print(f"TOTAL_ELAPSED_SECONDS={total_elapsed}")
print("LUNA_RUN_DONE")
