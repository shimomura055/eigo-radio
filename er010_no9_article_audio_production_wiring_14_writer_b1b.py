# Temporary diagnostic/execution script for ER-010-NO9-ARTICLE-AUDIO-PRODUCTION-WIRING-14.
# Runs the official Production writer path (gen.run_one_pattern via
# er006_pool_pilot_01_writer's exact prompt-building logic) for B1B only,
# against the canonical No.9 out_dir, with unbuffered stdout for live progress.
import sys
import time

import er009_n1_production_integration_01 as n9
import er003_v1_n3_01_articles_generate as gen
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_pool_pilot_01_writer as writer_mod

print("start", flush=True)
client = vfl01.get_client()
master_full_text = ab01.load_master_full_text()
ledger_path = f"{n9.OUT_DIR}/research/verified_fact_ledger.txt"
verified_ledger_text = writer_mod.load_text(ledger_path)
print("loaded inputs", flush=True)

level_out_dir = f"{n9.OUT_DIR}/b1b"
common_block = gen.build_common_block(master_full_text, n9.TOPIC_JA, verified_ledger_text,
                                       shared_point_blueprint_block="", evidence_compression=False)
prompt = gen.build_prompt(common_block, gen.B1_B_DIRECT_INSTRUCTION)
print("built prompt, calling run_one_pattern...", flush=True)
t0 = time.time()
result = gen.run_one_pattern(client, n9.THEME_ID, "B1B", prompt, verified_ledger_text,
                              n9.TOPIC_JA, level_out_dir, apply_evidence_compression=True)
print(f"DONE elapsed={time.time()-t0:.1f}s status={result.get('status')} "
      f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')}", flush=True)
