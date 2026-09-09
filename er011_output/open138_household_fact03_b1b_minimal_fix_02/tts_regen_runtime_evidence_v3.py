# ============================================================
# tts_regen_runtime_evidence_v3.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続)
# ============================================================
# revision3a(Fact Checker PASS・Ledger Deviation COMPLIANT確認済み)へ
# 差し替え後のparts.json[point_one_body]を、現行Productionの実生成関数
# (generate_news_narration_wide_margin、enable_connected_speech_
# equivalence_layer=True、enable_repetition_qa=True、disfluency_qa=False
# ―― point_one/point_twoが実際に使っているのと同一の組み合わせ)へ通し、
# narration/point_one.wavのみ上書きする。TTS/ASR経路自体は無変更。
# 費用はrevision2時と分離してraw_usage_log_revision3_tts.jsonlへ記録する。
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er003_v1_n3_01_tts_generate as n3
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er005_cost_logger as cl

OUT_DIR = "er003_output/n3_01/household/fact03_fix_02/b1b"
NARRATION_DIR = f"{OUT_DIR}/narration"
PARTS_PATH = f"{OUT_DIR}/parts.json"
TTS_RESULTS_PATH = f"{OUT_DIR}/audit/tts_generation_results.json"
COST_LOG_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/raw_usage_log_revision3_tts.jsonl"
RUN_SUMMARY_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/point_one_regen_run_summary_v3.json"

TARGETS = [
    ("point_one", "point_one_body"),
]


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること。"
    )
    parts = json.load(open(PARTS_PATH, encoding="utf-8"))
    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))

    cl.install(COST_LOG_PATH)

    summaries = {}
    lock_triggered = False
    for name, field in TARGETS:
        canonical_text = parts[field]
        tts_input = n3.tts_safe_news_en(canonical_text)
        out_path = f"{NARRATION_DIR}/{name}.wav"
        old_sha256 = sha256_of(out_path) if os.path.exists(out_path) else None

        t0 = time.time()
        with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02-REVISION3", "point_one_regen_v3"), \
                cl.segment_context(name):
            result = news_tail_fix.generate_news_narration_wide_margin(
                tts_input, out_path,
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True,
            )
        elapsed = time.time() - t0

        new_sha256 = sha256_of(out_path) if os.path.exists(out_path) else None
        result["canonical_text"] = canonical_text
        result["sha256"] = new_sha256
        result["source_note"] = (
            "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続): revision3a"
            "(TTSが省略しやすい'the low-humidity one'反復を回避した文言、Fact "
            "Checker PASS・Ledger Deviation v4 COMPLIANT)で再生成した。"
        )
        tts_results["segments"][name] = result

        full_result_snapshot = json.loads(json.dumps(result, ensure_ascii=False, default=str))
        summaries[name] = {
            "full_result": full_result_snapshot,
            "segment": name,
            "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
            "canonical_text": canonical_text,
            "tts_input": tts_input,
            "out_path": out_path,
            "elapsed_seconds": round(elapsed, 2),
            "status": result.get("status"),
            "asr_verified": result.get("asr_verified"),
            "asr_text": result.get("asr_text"),
            "audio_classification": result.get("audio_classification"),
            "connected_speech_info": result.get("connected_speech_info"),
            "disfluency_checked": result.get("disfluency_checked"),
            "repetition_qa_checked": result.get("repetition_qa_checked"),
            "repetition_qa_evidence": result.get("repetition_qa_evidence"),
            "old_sha256": old_sha256,
            "new_sha256": new_sha256,
            "attempts_log_summary": [
                {
                    "attempt": a.get("attempt"), "status": a.get("status"),
                    "verified": a.get("verified"),
                    "asr_text": a.get("asr_text"),
                    "repetition_qa_checked": a.get("repetition_qa_checked"),
                    "repetition_qa_flagged": (
                        (a.get("repetition_qa_evidence") or {}).get("flagged")
                        if a.get("repetition_qa_evidence") else None
                    ),
                }
                for a in (result.get("attempts_log") or [])
            ],
        }

        if result.get("status") != "OK":
            lock_triggered = True

    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    with open(RUN_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(summaries, ensure_ascii=True, indent=2, default=str))
    print(f"\n[point_one_regen_v3] summary -> {RUN_SUMMARY_PATH}")
    print(f"[point_one_regen_v3] tts_generation_results.json更新 -> {TTS_RESULTS_PATH}")
    print(f"[point_one_regen_v3] lock_triggered={lock_triggered}")


if __name__ == "__main__":
    main()
