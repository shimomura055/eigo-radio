# ============================================================
# er011_tts_execution_mode_switch_wiring_01_runtime_evidence_run.py
# ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01: Runtime evidence
# ============================================================
# Gate 3のRuntime evidence取得用script。実際のGemini API/ASRを使う
# (小額課金)。環境変数TTS_EXECUTION_MODEは、このプロセス自身に対して
# のみ有効(このscript実行時に呼び出し元shellがexportした値をそのまま
# 読むだけで、このscript自体は他プロセス/.env/グローバル環境を一切
# 変更しない)。
#
# 実際のProduction call site(er003_v1_repro01_main_generate.py::
# generate_key_phrase_component_verified、A02正式承認済みKey Phrase
# "opt out"のテキストを再利用、er006_tts_batch_wiring_01_smoke_run.pyと
# 同じ方針)を1件だけ実行し、専用出力先(OUT_DIR、本番narration_dirでは
# ない)へ書く。既存の完成音声には一切触れない。
from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cost_logger
import er006_batch_tts_wiring_01 as batch_wiring
import er003_v1_repro01_main_generate as repro01

MODE = os.environ.get("TTS_EXECUTION_MODE", "BATCH").strip().upper() or "BATCH"
OUT_DIR = f"er011_output/tts_execution_mode_switch_wiring_01/{MODE.lower()}"
os.makedirs(OUT_DIR, exist_ok=True)
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

# 前回runの残骸で"すでにinstall済み"にならないよう、このprocessは
# 常に新規に起動される前提(subprocessごとに1回だけ実行)。
cost_logger.install(LOG_PATH)

result_summary = {"requested_env_value": os.environ.get("TTS_EXECUTION_MODE"), "resolved_mode": None}

with cost_logger.logging_context("tts_execution_mode_switch_evidence", f"runtime_evidence_{MODE.lower()}"):
    with cost_logger.segment_context("kp_opt_out_english"):
        resolved_mode = batch_wiring.resolve_tts_execution_mode()
        result_summary["resolved_mode"] = resolved_mode
        t0 = time.time()
        r = repro01.generate_key_phrase_component_verified("opt out", f"{OUT_DIR}/kp_opt_out_english.wav")
        wall_seconds = round(time.time() - t0, 2)
        result_summary["result"] = {**r, "wall_seconds": wall_seconds}
        print(f"[EVIDENCE][{MODE}] status={r.get('status')} wall_seconds={wall_seconds}s "
              f"resolved_mode={resolved_mode}")

with open(f"{OUT_DIR}/evidence_result.json", "w", encoding="utf-8") as f:
    json.dump(result_summary, f, ensure_ascii=False, indent=2, default=str)

# raw_usage_log.jsonlからtts_execution_modeタグの記録有無を確認する。
with open(LOG_PATH, encoding="utf-8") as f:
    log_entries = [json.loads(l) for l in f]

tagged = [e for e in log_entries if e.get("tts_execution_mode") is not None]
print(f"[EVIDENCE][{MODE}] raw_usage_log.jsonl entries={len(log_entries)} "
      f"tts_execution_mode-tagged={len(tagged)}")
for e in tagged:
    print(f"  - provider={e.get('provider')} api={e.get('api')} tts_execution_mode={e.get('tts_execution_mode')} "
          f"elapsed_seconds={e.get('elapsed_seconds')} success={e.get('success')}")

print("EVIDENCE_RUN_DONE")
