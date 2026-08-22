# ============================================================
# er006_tts_batch_wiring_01_smoke_run.py
# ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: 最小限の実API配線確認
# ============================================================
# 目的(タスク仕様§15): Full Episode再生成は不要、代表segment数件のみで
# Production wiringが本当に動くかを確認する。品質自体は既存のA/B確認
# (ER-006-AUDIO-COST-OPTIMIZATION-01)で承認済みのため、ここでの確認は
# 品質再確認ではなく「実際にProductionコードパスからBatch API経由で
# 音声が生成され、既存のtrim/ASR検証を通ることの動作確認」に限定する。
#
# 既存の承認済みKey Phraseテキスト(A02: "opt out"英語/「参加・適用を
# 断る」日本語)を再利用する(er006_batch_ab_01_generate.pyと同じ方針:
# 新規テキストを作らず、実在の承認済み本番文言をそのまま使う)。出力は
# 本番のnarration_dirではなく専用の出力先(OUT_DIR)へ書き、既存の
# 完成音声ファイルには一切触れない。
from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cost_logger
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er006_output/tts_batch_wiring_01_smoke"
os.makedirs(OUT_DIR, exist_ok=True)
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

cost_logger.install(LOG_PATH)

STANDARD_PRICE = {
    "gemini-2.5-pro-preview-tts": {"input": 1.00, "output": 20.00},
    "gemini-3.1-flash-tts-preview": {"input": 1.00, "output": 20.00},
}

results = {}

with cost_logger.logging_context("smoke_wiring_check", "batch_tts_wiring_smoke"):
    with cost_logger.segment_context("kp_opt_out_english"):
        t0 = time.time()
        r = repro01.generate_key_phrase_component_verified("opt out", f"{OUT_DIR}/kp_opt_out_english.wav")
        results["english_key_phrase"] = {**r, "wall_seconds": round(time.time() - t0, 2)}
        print(f"[SMOKE] english_key_phrase: status={r.get('status')} wall={results['english_key_phrase']['wall_seconds']}s")

    with cost_logger.segment_context("kp_opt_out_japanese_gloss"):
        t0 = time.time()
        r = repro01.generate_narration_snippet_verified_strict(
            "参加・適用を断る", "ja", f"{OUT_DIR}/kp_opt_out_japanese.wav", "断る", max_attempts=6)
        results["japanese_gloss"] = {**r, "wall_seconds": round(time.time() - t0, 2)}
        print(f"[SMOKE] japanese_gloss: status={r.get('status')} wall={results['japanese_gloss']['wall_seconds']}s")

with open(f"{OUT_DIR}/smoke_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

# --- raw_usage_log.jsonlからGemini Batch呼び出しのみ集計し、Standard換算と比較 ---
with open(LOG_PATH, encoding="utf-8") as f:
    log_entries = [json.loads(l) for l in f]

batch_entries = [e for e in log_entries if e.get("provider") == "gemini_batch" and e.get("success")]
total_batch_usd = 0.0
total_standard_equiv_usd = 0.0
per_call = []
for e in batch_entries:
    model = e["model_id"]
    in_tok = e.get("input_tokens") or 0
    out_tok = e.get("output_tokens") or 0
    batch_usd = e.get("cost_usd") or 0.0
    standard_usd = (in_tok / 1_000_000) * STANDARD_PRICE[model]["input"] + (out_tok / 1_000_000) * STANDARD_PRICE[model]["output"]
    total_batch_usd += batch_usd
    total_standard_equiv_usd += standard_usd
    per_call.append({
        "segment": e.get("segment"), "model": model, "input_tokens": in_tok, "output_tokens": out_tok,
        "batch_usd": round(batch_usd, 6), "standard_equiv_usd": round(standard_usd, 6),
        "batch_job_id": e.get("batch_job_id"), "elapsed_seconds": e.get("elapsed_seconds"),
    })

USD_TO_JPY = 160
reduction_pct = (1 - total_batch_usd / total_standard_equiv_usd) * 100 if total_standard_equiv_usd > 0 else None

summary = {
    "batch_api_call_count": len(batch_entries),
    "per_call": per_call,
    "total_batch_usd": round(total_batch_usd, 6),
    "total_standard_equivalent_usd": round(total_standard_equiv_usd, 6),
    "total_batch_jpy": round(total_batch_usd * USD_TO_JPY, 3),
    "total_standard_equivalent_jpy": round(total_standard_equiv_usd * USD_TO_JPY, 3),
    "reduction_percent": round(reduction_pct, 2) if reduction_pct is not None else None,
}
with open(f"{OUT_DIR}/cost_comparison.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\n[SMOKE] Batch API call件数: {summary['batch_api_call_count']}")
print(f"[SMOKE] Batch実コスト: ${summary['total_batch_usd']} (¥{summary['total_batch_jpy']})")
print(f"[SMOKE] Standard換算コスト: ${summary['total_standard_equivalent_usd']} (¥{summary['total_standard_equivalent_jpy']})")
print(f"[SMOKE] 削減率: {summary['reduction_percent']}%")
print("SMOKE_RUN_DONE")
