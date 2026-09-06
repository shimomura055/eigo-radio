# ============================================================
# er011_kp_en_asr_false_rejection_prod_wiring_01_runtime_evidence.py
# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01: Runtime evidence
# ============================================================
# Gate 3のRuntime evidence取得用script(実API・小額課金)。
#
# 陽性(2件): 実際のProduction call site
# (er003_v1_repro01_main_generate.py::generate_key_phrase_component_
# verified)を、隔離出力先(OUT_DIR、本番narration_dirではない)で
# 「new normal」「cashless」に対して実行する。TTS_EXECUTION_MODE=STANDARD
# (前面同期、er011_tts_execution_mode_switch_wiring_01_runtime_evidence_
# run.pyと同じ方針)。既存の完成音声には一切触れない。
#
# 陰性(1件): KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-TRIAL-01で生成
# 済みの既存音声(日本語TTSで「新常態」を発話、canonical="new normal"、
# er011_output/kp_en_asr_false_rejection_cascade_trial_01/audio/
# neg_ja_shinjoutai.wav)を再利用し、新規TTSは行わない。実際のProduction
# Cascade関数(er006_secondary_asr_01.evaluate_attempt_with_cascade_
# detail、enable_non_latin_cascade=True)を直接呼び、reject維持を確認する
# (generate_key_phrase_component_verified自体は既存wavを受け付けず毎回
# 新規TTSを行う設計のため、Cascade層を直接呼ぶことで既存資産を再利用する)。

from __future__ import annotations

import json
import os
import shutil
import time

import er003_v1_repro01_main_generate as repro01
import er005_cost_logger as cost_logger
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_secondary_asr_01 as secondary_asr

MODE = os.environ.get("TTS_EXECUTION_MODE", "BATCH").strip().upper() or "BATCH"
OUT_DIR = "er011_output/kp_en_asr_false_rejection_prod_wiring_01"
os.makedirs(OUT_DIR, exist_ok=True)
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"
cost_logger.install(LOG_PATH)

result_summary = {"tts_execution_mode_requested": os.environ.get("TTS_EXECUTION_MODE"), "positive": {}, "negative": {}}

# ------------------------------------------------------------
# 陽性(2件): 実Production経路、実TTS+実ASR
# ------------------------------------------------------------
resolved_mode = batch_wiring.resolve_tts_execution_mode()
result_summary["tts_execution_mode_resolved"] = resolved_mode

for text, fname in [("new normal", "kp_new_normal_english.wav"), ("cashless", "kp_cashless_english.wav")]:
    out_path = f"{OUT_DIR}/{fname}"
    with cost_logger.logging_context("kp_en_asr_false_rejection_prod_wiring_evidence", f"positive_{fname}"):
        t0 = time.time()
        r = repro01.generate_key_phrase_component_verified(text, out_path)
        wall_seconds = round(time.time() - t0, 2)
    attempts_log = r.get("attempts_log") or []
    first_attempt = attempts_log[0] if attempts_log else {}
    result_summary["positive"][text] = {
        "status": r.get("status"), "fallback_used": r.get("fallback_used"),
        "primary_instruction_type": r.get("primary_instruction_type"),
        "wall_seconds": wall_seconds,
        "attempts_log": attempts_log,
        "asr_prompt_applied_attempt1": first_attempt.get("asr_prompt_applied"),
        "non_latin_cascade_enabled_attempt1": first_attempt.get("non_latin_cascade_enabled"),
        "non_latin_cascade_invoked_any_attempt": any(a.get("non_latin_cascade_invoked") for a in attempts_log),
    }
    print(f"[EVIDENCE][POSITIVE][{text}] status={r.get('status')} "
          f"asr_text(attempt1)={first_attempt.get('asr_text')!r} "
          f"asr_prompt_applied={first_attempt.get('asr_prompt_applied')} "
          f"non_latin_cascade_invoked_any={result_summary['positive'][text]['non_latin_cascade_invoked_any_attempt']} "
          f"wall_seconds={wall_seconds}s")

# ------------------------------------------------------------
# 陰性(1件): 既存音声を再利用、Cascade層を実際に直接実行
# ------------------------------------------------------------
neg_src = "er011_output/kp_en_asr_false_rejection_cascade_trial_01/audio/neg_ja_shinjoutai.wav"
neg_dst = f"{OUT_DIR}/neg_ja_shinjoutai_reused.wav"
shutil.copy2(neg_src, neg_dst)

with cost_logger.logging_context("kp_en_asr_false_rejection_prod_wiring_evidence", "negative_ja_shinjoutai"):
    # 実Production Primary ASR呼び出し(promptあり、KP経路と同一の
    # 呼び出し方)をそのまま使う。
    asr_text, asr_err = routing.transcribe(
        neg_dst, language="en-US", prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)
    detail_out = {}
    verified, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
        "new normal", asr_text, [], neg_dst, language="en-US",
        cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED,
        enable_non_latin_cascade=True, detail_out=detail_out)

result_summary["negative"]["ja_shinjoutai_vs_new_normal"] = {
    "source_wav": neg_src, "primary_asr_text_with_prompt": asr_text, "primary_asr_error": asr_err,
    "verified": verified, "final_classification": detail_out.get("final_status"),
    "non_latin_cascade_invoked": detail_out.get("non_latin_cascade_invoked"),
    "steps": detail_out.get("steps"),
}
print(f"[EVIDENCE][NEGATIVE][ja_shinjoutai] primary_asr_text_with_prompt={asr_text!r} "
      f"verified={verified} final_classification={detail_out.get('final_status')} "
      f"non_latin_cascade_invoked={detail_out.get('non_latin_cascade_invoked')}")

with open(f"{OUT_DIR}/evidence_result.json", "w", encoding="utf-8") as f:
    json.dump(result_summary, f, ensure_ascii=False, indent=2, default=str)

# ------------------------------------------------------------
# player.html(file:///形式、試聴用)
# ------------------------------------------------------------
audio_files = [f for f in os.listdir(OUT_DIR) if f.endswith(".wav")]
rows = "\n".join(
    f'<tr><td>{f}</td><td><audio controls src="{f}"></audio></td></tr>' for f in sorted(audio_files))
with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
    f.write(f"<html><body><h1>KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01</h1>"
            f"<table>{rows}</table></body></html>")

print("EVIDENCE_RUN_DONE")
print(f"player: file:///{os.path.abspath(OUT_DIR).replace(os.sep, '/')}/player.html")
