# ============================================================
# standard_sync_1segment_runtime_evidence.py
# OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01
# ============================================================
# 実行方法(root直下から):
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er011_output/open128_method_d_local_asr_wiring_01/\
#     standard_sync_1segment_runtime_evidence.py
#
# 目的: A-Family既存Production関数(news_tail_fix.
# generate_news_narration_wide_margin、無変更)をenable_repetition_qa=True
# で実際に1 segment(短文、費用上限¥20以内)呼び出し、方式A→方式D
# (ASR共有・局所ASR確認2段判定)→apply_repetition_qa_gateのANDゲートまで
# 実発火することを確認する(Production初回path、Standard同期TTS)。
# 既存音声・player.htmlは一切上書きせず、本ディレクトリ配下の新しい
# 出力先へのみ保存する。
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

OUT_DIR = "er011_output/open128_method_d_local_asr_wiring_01/standard_sync_1segment"
NARRATION_DIR = f"{OUT_DIR}/narration"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

# 短文(費用最小化、実際のnews記事本文と同スタイルのダミー1文)。
CANONICAL_TEXT = ("City buses in the area will run on a slightly different "
                   "schedule this month.")


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること"
        "(タスク仕様: Standard同期を明示)。"
    )
    os.makedirs(NARRATION_DIR, exist_ok=True)
    tts_input = n3.tts_safe_news_en(CANONICAL_TEXT)
    out_path = f"{NARRATION_DIR}/full_story_part1.wav"

    cl.install(COST_LOG_PATH)
    t0 = time.time()
    with cl.logging_context("OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01",
                             "standard_sync_1segment"), \
            cl.segment_context("full_story_part1"):
        result = news_tail_fix.generate_news_narration_wide_margin(
            tts_input, out_path,
            # 実Production配線と同一のopt-in(full_story_part1/2・point_one・
            # point_twoのみ対象、A2/B1本文4segmentループが渡すのと同じ引数)。
            enable_repetition_qa=True,
        )
    elapsed = time.time() - t0

    cost_total_jpy = None
    if os.path.exists(COST_LOG_PATH):
        # 生ログにcost_jpyフィールドは存在しない(er005_cost_logger.pyは
        # usage記録専用)。compute_topic_cost.pyと同一手法で
        # pricing_snapshot.json(SSOT pricing)からUSD算出しJPY換算する。
        with open(COST_LOG_PATH, encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
        pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json",
                                  encoding="utf-8"))["prices"]

        def _price(provider, model, meter):
            return next(p["price"] for p in pricing
                        if p["provider"] == provider and p["model"] == model and p["meter"] == meter)

        USD_TO_JPY = 160
        total_usd = 0.0
        for e in entries:
            provider, model = e.get("provider"), e.get("model_id")
            it, ot = e.get("input_tokens") or 0, e.get("output_tokens") or 0
            try:
                total_usd += (it / 1e6) * _price(provider, model, "input_tokens")
                total_usd += (ot / 1e6) * _price(provider, model, "output_tokens")
            except StopIteration:
                pass
        cost_total_jpy = round(total_usd * USD_TO_JPY, 4)

    summary = {
        "management_id": "OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01",
        "segment": "standard_sync_1segment/full_story_part1 (短文、費用最小化のためのダミー1文)",
        "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
        "canonical_text": CANONICAL_TEXT,
        "tts_input": tts_input,
        "out_path": out_path,
        "elapsed_seconds": round(elapsed, 2),
        "status": result.get("status"),
        "asr_verified": result.get("asr_verified"),
        "repetition_qa_checked": result.get("repetition_qa_checked"),
        "repetition_qa_evidence": result.get("repetition_qa_evidence"),
        "cost_total_jpy": cost_total_jpy,
        "cost_upper_bound_jpy": 20,
        "cost_within_upper_bound": (cost_total_jpy is not None and cost_total_jpy <= 20),
        "attempts_log_summary": [
            {
                "attempt": a.get("attempt"), "status": a.get("status"),
                "verified": a.get("verified"),
                "repetition_qa_checked": a.get("repetition_qa_checked"),
                "repetition_qa_flagged": (
                    (a.get("repetition_qa_evidence") or {}).get("flagged")
                    if a.get("repetition_qa_evidence") else None
                ),
                "method_a_ngram_flagged": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_a_ngram") or {}).get("flagged")
                    if a.get("repetition_qa_evidence") else None
                ),
                "method_d_acoustic_flagged": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_d_spectral_long_lag") or {}).get("acoustic_flagged")
                    if a.get("repetition_qa_evidence") else None
                ),
                "method_d_local_asr_confirmation": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_d_spectral_long_lag") or {}).get("local_asr_confirmation")
                    if a.get("repetition_qa_evidence") else None
                ),
                "method_d_final_flagged": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_d_spectral_long_lag") or {}).get("flagged")
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
    print(f"\n[standard_sync_1segment] summary -> {out_summary_path}")


if __name__ == "__main__":
    main()
