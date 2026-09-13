# ============================================================
# point_one_runtime_evidence.py
# OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01
# ============================================================
# 実行方法(root直下から):
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er011_output/open121_method_d_prime_production_wiring_01/\
#     point_one_runtime_evidence.py
#
# 目的: 方式D'(既に本番配線済み、evaluate_repetition_qa内
# analyze_profile_d_prime_short_lag)が実際のProduction経路
# (n3.generate_a2_segment_with_slowdown、enable_repetition_qa=True)で
# 評価されるログをこの委任タスク自身のセッションで新規取得する
# (既存OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01のevidenceの
# 再掲ではなく、独立した新規実行)。既存の記事出力・player.htmlは
# 一切上書きせず、本ディレクトリ配下にのみ保存する。
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as n3

OUT_DIR = "er011_output/open121_method_d_prime_production_wiring_01"
NARRATION_DIR = f"{OUT_DIR}/narration"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

# family_a_completion_a2_trend_end_to_end_01/a2/rerun_01のpoint_one
# canonical text(既存PASS済みA2本文segment、短めのpoint_one)を再利用。
CANONICAL_TEXT = ("Here, slow does not always mean a long holiday. Among men aged 29 and under, "
                   "about one in 4 chose solo travel, and a similar share chose a hobby-focused trip. "
                   "Another survey found that about 90% of people aged 19 to 25 wanted free time in an "
                   "overseas tour; most wanted half a day or more. This suggests that open time may "
                   "matter as much as trip length.")


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること。"
    )
    os.makedirs(NARRATION_DIR, exist_ok=True)
    tts_input = n3.tts_safe_number_words_en(n3.tts_safe_en(CANONICAL_TEXT))
    out_path = f"{NARRATION_DIR}/point_one.wav"

    def first_words(text, n=3):
        return " ".join(text.split()[:n])

    cl.install(COST_LOG_PATH)
    t0 = time.time()
    with cl.logging_context("OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01", "point_one_runtime_evidence"), \
            cl.segment_context("point_one"):
        result = n3.generate_a2_segment_with_slowdown(
            tts_input, out_path, first_words(CANONICAL_TEXT),
            style_prefix_override=n3.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            # 実Production配線と同一のopt-in(A2本文segmentのみ)。
            enable_repetition_qa=True,
        )
    elapsed = time.time() - t0

    summary = {
        "segment": "a2/point_one (runtime evidence, standalone)",
        "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
        "canonical_text": CANONICAL_TEXT,
        "tts_input": tts_input,
        "out_path": out_path,
        "elapsed_seconds": round(elapsed, 2),
        "status": result.get("status"),
        "asr_verified": result.get("asr_verified"),
        "repetition_qa_checked": result.get("repetition_qa_checked"),
        "repetition_qa_evidence": result.get("repetition_qa_evidence"),
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
                "method_d_prime_flagged": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_d_prime_spectral_short_lag") or {}).get("flagged")
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
    print(f"\n[point_one_runtime_evidence] summary -> {out_summary_path}")


if __name__ == "__main__":
    main()
