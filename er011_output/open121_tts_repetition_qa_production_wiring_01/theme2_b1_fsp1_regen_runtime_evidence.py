# ============================================================
# theme2_b1_fsp1_regen_runtime_evidence.py
# OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01
# ============================================================
# 実行方法(root直下から):
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er011_output/open121_tts_repetition_qa_production_wiring_01/\
#     theme2_b1_fsp1_regen_runtime_evidence.py
#
# 目的: Theme2 B1 full_story_part1(false startが実在した記録済み
# segment、OPEN-112-THEME2-AUDIO-REVIEW-FIX-02サブタスクD)を、
# OPEN-121で配線後の実Production関数(news_tail_fix.
# generate_news_narration_wide_margin、enable_repetition_qa=True)で
# 実際に再生成する。既存のPASS音声・player.htmlは一切上書きせず、
# 本ディレクトリ配下の新しい出力先へ保存する。Episode全体の再Assembly
# は今回行わない(FSP1単体のPASS音声+run-summaryのみ)。
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as n3
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er011_open121_repetition_qa_production_01 as repetition_qa

RERUN02_PARTS = "er011_output/open112_trend_theme2_b_final_audio_rerun_02/b1b/parts.json"
OUT_DIR = "er011_output/open121_tts_repetition_qa_production_wiring_01/theme2_b1_fsp1_regen"
NARRATION_DIR = f"{OUT_DIR}/narration"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること"
        "(タスク仕様: Standard同期を明示)。"
    )
    os.makedirs(NARRATION_DIR, exist_ok=True)
    parts = json.load(open(RERUN02_PARTS, encoding="utf-8"))
    canonical_text = parts["part1"]
    tts_input = n3.tts_safe_news_en(canonical_text)
    out_path = f"{NARRATION_DIR}/full_story_part1.wav"

    cl.install(COST_LOG_PATH)
    t0 = time.time()
    with cl.logging_context("OPEN-121-PRODUCTION-WIRING", "theme2_b1_fsp1_regen"), \
            cl.segment_context("full_story_part1"):
        result = news_tail_fix.generate_news_narration_wide_margin(
            tts_input, out_path,
            # 実Production配線と同一のopt-in(full_story_part1/2・point_one・
            # point_twoのみ対象)。
            enable_repetition_qa=True,
        )
    elapsed = time.time() - t0

    summary = {
        "theme": "open112_trend_theme2_b (Hormuz Strait / Iran)",
        "segment": "b1b/full_story_part1",
        "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
        "canonical_text": canonical_text,
        "tts_input": tts_input,
        "out_path": out_path,
        "elapsed_seconds": round(elapsed, 2),
        "status": result.get("status"),
        "asr_verified": result.get("asr_verified"),
        "repetition_qa_checked": result.get("repetition_qa_checked"),
        "repetition_qa_evidence": result.get("repetition_qa_evidence"),
        "disfluency_checked": result.get("disfluency_checked"),
        "attempts_log_summary": [
            {
                "attempt": a.get("attempt"), "status": a.get("status"),
                "verified": a.get("verified"),
                "repetition_qa_checked": a.get("repetition_qa_checked"),
                "repetition_qa_flagged": (
                    (a.get("repetition_qa_evidence") or {}).get("flagged")
                    if a.get("repetition_qa_evidence") else None
                ),
                "method_d_prime_best_run_seconds": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_d_prime_spectral_short_lag") or {}).get("best_run_length_seconds")
                    if a.get("repetition_qa_evidence") else None
                ),
            }
            for a in (result.get("attempts_log") or [])
        ],
    }
    out_summary_path = f"{OUT_DIR}/run_summary.json"
    with open(out_summary_path, "w", encoding="utf-8") as f:
        json.dump({**summary, "full_result": result}, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n[theme2_b1_fsp1_regen] summary -> {out_summary_path}")


if __name__ == "__main__":
    main()
