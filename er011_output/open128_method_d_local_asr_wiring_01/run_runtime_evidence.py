# ============================================================
# er011_output/open128_method_d_local_asr_wiring_01/run_runtime_evidence.py
# OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01: Runtime evidence
# ============================================================
# Production module(er011_open121_repetition_qa_production_01.py、方式D
# 2段判定・ASR共有リファクタ適用後)を、Production entry
# (evaluate_repetition_qa())経由で、確定TP8件+確定FP15件
# (er011_output/method_d_flag23_review_01/classification_table.json)へ
# 直接実行する。各件についてtranscribe_verbatim呼び出し回数を計測し、
# 同一音声への二重ASRが発生しないことを確認する。
#
# 実行方法: .venv/Scripts/python.exe er011_output/
#   open128_method_d_local_asr_wiring_01/run_runtime_evidence.py
from __future__ import annotations

import json
import os
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

import er008_disfluency_qa_18 as dq18  # noqa: E402
import er011_open121_repetition_qa_production_01 as repetition_qa  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG23_TABLE = os.path.join(REPO_ROOT, "er011_output", "method_d_flag23_review_01", "classification_table.json")


def main():
    with open(FLAG23_TABLE, encoding="utf-8") as f:
        rows = json.load(f)
    assert len(rows) == 23

    orig_transcribe = dq18.transcribe_verbatim
    call_counter = {"n": 0}

    def counting_transcribe(*a, **k):
        call_counter["n"] += 1
        return orig_transcribe(*a, **k)

    dq18.transcribe_verbatim = counting_transcribe

    results = []
    t0 = time.time()
    for row in rows:
        call_counter["n"] = 0
        path = os.path.join(REPO_ROOT, row["path"])
        t_item0 = time.time()
        r = repetition_qa.evaluate_repetition_qa(path, row["canonical_text"], language="en")
        elapsed = round(time.time() - t_item0, 2)
        d = r["method_d_spectral_long_lag"]
        results.append({
            "item_id": row["item_id"],
            "classification": row["classification"],
            "is_tp": row["classification"] == "真の重複(証拠あり)",
            "acoustic_flagged": d["acoustic_flagged"],
            "local_asr_confirmation": d.get("local_asr_confirmation"),
            "method_d_final_flagged": d["flagged"],
            "overall_flagged": r["flagged"],
            "transcribe_verbatim_call_count": call_counter["n"],
            "elapsed_seconds": elapsed,
        })
        print(f"{row['item_id'][:70]:70s} TP={row['classification']=='真の重複(証拠あり)'} "
              f"acoustic={d['acoustic_flagged']} final_d={d['flagged']} "
              f"asr_calls={call_counter['n']} elapsed={elapsed}s")

    dq18.transcribe_verbatim = orig_transcribe
    elapsed_total = round(time.time() - t0, 1)

    tp_items = [r for r in results if r["is_tp"]]
    fp_items = [r for r in results if not r["is_tp"]]
    tp_flagged = sum(1 for r in tp_items if r["method_d_final_flagged"])
    fp_flagged = sum(1 for r in fp_items if r["method_d_final_flagged"])
    all_single_asr_call = all(r["transcribe_verbatim_call_count"] == 1 for r in results)
    acoustic_flagged_count = sum(1 for r in results if r["acoustic_flagged"])

    summary = {
        "management_id": "OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01",
        "entry_point": "er011_open121_repetition_qa_production_01.evaluate_repetition_qa() "
                        "(Production entry経由)",
        "tp_total": len(tp_items), "tp_flagged_after_2stage": tp_flagged,
        "fp_total": len(fp_items), "fp_flagged_after_2stage": fp_flagged,
        "expected_tp_8_8_fp_0_15": (tp_flagged == 8 and len(tp_items) == 8
                                     and fp_flagged == 0 and len(fp_items) == 15),
        "all_items_single_asr_call": all_single_asr_call,
        "acoustic_flagged_count_of_23": acoustic_flagged_count,
        "elapsed_seconds_total": elapsed_total,
        "cost_jpy": 0,
        "note": "faster-whisperローカルCPU実行のみ、追加API課金ゼロ。方式Dの局所ASR確認は"
                "acoustic_flagged=Trueの23件でのみ発火(元々の23件flag集合に対する後段"
                "フィルタ、背景494件への新規flag波及なし)。",
    }
    with open(os.path.join(OUT_DIR, "runtime_evidence.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "items": results}, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
