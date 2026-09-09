# ============================================================
# tts_regen_runtime_evidence.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(OPEN-138)
# ============================================================
# 実行方法(root直下から):
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er011_output/open138_household_fact03_b1b_minimal_fix_02/tts_regen_runtime_evidence.py
#
# 目的: textfix.py(revision 2、qa_runtime_evidence.pyでFact Checker
# verdict=PASS・Ledger Deviation=LEDGER_COMPLIANT確認済み)後のparts.json
# [point_one_body]を、現行Productionの実生成関数(er003_v1_n3_01_tts_
# generate.py::generate_b1_segments()がpoint_one/point_twoに対して実際に
# 使っているのと同一のenable_connected_speech_equivalence_layer=True・
# enable_repetition_qa=True・disfluency_qa=Falseの組み合わせ)へ通し、
# narration/point_one.wavのみ上書きする(point_two等、他segmentは一切
# 呼ばない)。TTS/ASR経路自体は無変更(既存Production関数をそのまま呼ぶ
# だけ)。
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
COST_LOG_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/raw_usage_log.jsonl"
RUN_SUMMARY_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/point_one_regen_run_summary.json"

TARGETS = [
    ("point_one", "point_one_body"),
]


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること"
        "(タスク仕様: Standard同期を明示)。"
    )
    parts = json.load(open(PARTS_PATH, encoding="utf-8"))
    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))

    cl.install(COST_LOG_PATH)

    summaries = {}
    for name, field in TARGETS:
        canonical_text = parts[field]
        tts_input = n3.tts_safe_news_en(canonical_text)
        out_path = f"{NARRATION_DIR}/{name}.wav"
        old_sha256 = sha256_of(out_path) if os.path.exists(out_path) else None

        t0 = time.time()
        with cl.logging_context("HOUSEHOLD-FACT-03-MINIMAL-FIX-02", "point_one_regen"), \
                cl.segment_context(name):
            # er003_v1_n3_01_tts_generate.py::generate_b1_segments()が
            # point_one/point_twoに対して実際に渡している引数と同一
            # (disfluency_qa=False既定、enable_connected_speech_equivalence_
            # layer=True、enable_repetition_qa=True)。
            result = news_tail_fix.generate_news_narration_wide_margin(
                tts_input, out_path,
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True,
            )
        elapsed = time.time() - t0

        assert result.get("status") == "OK", (
            f"{name}の生成がstatus={result.get('status')}で終了しました。"
            "Human Review Lock等が発動した可能性があるため、承認代行せず停止します。"
            f" result={result}"
        )

        new_sha256 = sha256_of(out_path)
        result["canonical_text"] = canonical_text
        result["sha256"] = new_sha256
        result["source_note"] = (
            "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02: FACT-03 v4"
            "(usable: no、イチゴ・柑橘類=高湿度という家庭用設定の断定を削除)に"
            "基づき、parts.json[point_one_body]をLedger v4の範囲(メーカー間で"
            "イチゴの扱いが割れているという事実)へ最小翻案した後、現行Production"
            "関数(generate_news_narration_wide_margin、"
            "enable_connected_speech_equivalence_layer=True、"
            "enable_repetition_qa=True)で再生成した。"
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

    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    with open(RUN_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(summaries, ensure_ascii=True, indent=2, default=str))
    print(f"\n[point_one_regen] summary -> {RUN_SUMMARY_PATH}")
    print(f"[point_one_regen] tts_generation_results.json更新 -> {TTS_RESULTS_PATH}")


if __name__ == "__main__":
    main()
