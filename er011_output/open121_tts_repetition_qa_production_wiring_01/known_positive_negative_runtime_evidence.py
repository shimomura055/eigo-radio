# ============================================================
# known_positive_negative_runtime_evidence.py
# OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01
# ============================================================
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_output/open121_tts_repetition_qa_
#     production_wiring_01/known_positive_negative_runtime_evidence.py
#
# 目的: 修正後のProduction関数(er011_open121_repetition_qa_production_
# 01.evaluate_repetition_qa、Trial-01/02からロジック無変更で移植)を、
# (a) 既知陽性3件(Theme2 A2 Point Two/In One Line重複[保全済attempt]、
#     B1 FSP1 false start[保全済])
# (b) 既知陰性(Trial-02陰性セットのEN本文相当代表10件)
# へ実際に投入し、flag結果を記録する(受入条件3(a)(b))。読み取りのみ
# (既存Trial成果物・保全音声は一切変更しない)。追加API課金なし
# (方式A/D/D'はいずれもローカルCPU計算のみ)。
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er011_open121_repetition_qa_production_01 as repetition_qa

TRIAL01_DIR = "er011_output/open121_tts_repetition_general_qa_trial_01"
OUT_DIR = "er011_output/open121_tts_repetition_qa_production_wiring_01"


def load_manifest():
    return {m["item_id"]: m for m in
            json.load(open(f"{TRIAL01_DIR}/test_set/manifest.json", encoding="utf-8"))}


def run_known_positives(manifest):
    targets = [
        ("real_point_two_buggy", "Theme2 A2 Point Two(句・文まるごと反復、保全済attempt)"),
        ("real_in_one_line_buggy", "Theme2 A2 In One Line(句・文まるごと反復、保全済attempt)"),
        ("real_b1_fsp1_falsestart_partial_word", "Theme2 B1 FSP1 false start(語の途中で切れて即再開、保全済)"),
    ]
    results = {}
    for item_id, note in targets:
        m = manifest[item_id]
        t0 = time.time()
        r = repetition_qa.evaluate_repetition_qa(m["path"], m.get("canonical_text"), language="en")
        elapsed = round(time.time() - t0, 2)
        results[item_id] = {"note": note, "path": m["path"], "elapsed_seconds": elapsed,
                             "expected_label": "positive", "evidence": r}
        print(f"[POSITIVE] {item_id}: flagged={r['flagged']} "
              f"(A={r['method_a_ngram']['flagged']} "
              f"D={r['method_d_spectral_long_lag']['flagged']}/{r['method_d_spectral_long_lag']['best_run_length_seconds']}s "
              f"D'={r['method_d_prime_spectral_short_lag']['flagged']}/{r['method_d_prime_spectral_short_lag']['best_run_length_seconds']}s) "
              f"[{elapsed}s]")
    return results


def run_known_negatives(manifest):
    neg_en = [m for m in manifest.values()
              if m["source"] == "reused_production_pass" and m["language"] == "en"]
    neg_en = sorted(neg_en, key=lambda m: m["item_id"])[:10]
    results = {}
    for m in neg_en:
        t0 = time.time()
        r = repetition_qa.evaluate_repetition_qa(m["path"], m.get("canonical_text"), language="en")
        elapsed = round(time.time() - t0, 2)
        results[m["item_id"]] = {"path": m["path"], "elapsed_seconds": elapsed,
                                  "expected_label": "negative", "evidence": r}
        print(f"[NEGATIVE] {m['item_id']}: flagged={r['flagged']} "
              f"(A={r['method_a_ngram']['flagged']} "
              f"D={r['method_d_spectral_long_lag']['best_run_length_seconds']}s "
              f"D'={r['method_d_prime_spectral_short_lag']['best_run_length_seconds']}s) [{elapsed}s]")
    return results


def main():
    manifest = load_manifest()
    positives = run_known_positives(manifest)
    negatives = run_known_negatives(manifest)

    tp = sum(1 for v in positives.values() if v["evidence"]["flagged"])
    fp = sum(1 for v in negatives.values() if v["evidence"]["flagged"])
    summary = {
        "tp": f"{tp}/{len(positives)}", "fp": f"{fp}/{len(negatives)}",
        "positives": positives, "negatives": negatives,
    }
    out_path = f"{OUT_DIR}/known_positive_negative_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nTP={tp}/{len(positives)}  FP={fp}/{len(negatives)}")
    print(f"[known_positive_negative_runtime_evidence] -> {out_path}")


if __name__ == "__main__":
    main()
