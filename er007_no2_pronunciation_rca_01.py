# ============================================================
# er007_no2_pronunciation_rca_01.py
# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part B: No.2「やめにくくする」
# 発音問題のRCA。既存の本番生成関数をそのまま再利用し、同一canonical
# textで複数回生成して再現性を確認する(新規TTS instructionは作らない)。
# ============================================================
from __future__ import annotations

import json
import os
import sys

import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/evidence_density_ab_01/no2_pronunciation_rca_log.jsonl")

import er003_v1_n3_01_tts_generate as tts_gen

CANONICAL_TEXT = (
    "このニュースは、定期サービスをやめにくくする仕組みと、それを変えようとした"
    "ルールが裁判で取り消された流れを伝えています。次は、解約の負担を手続きの"
    "最初から最後まで見ていきます。そして、研究者が複雑な解約の流れをどう"
    "調べたのかを聞きます。"
)

OUT_DIR = "er006_output/pool_pilot_01/evidence_density_ab_01/no2_rca"


def run_attempt(n: int) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/comment_3_attempt{n}.wav"
    r = tts_gen.generate_a2_japanese_with_reading_safety(
        CANONICAL_TEXT, out_path, tts_gen.expected_substring_ja(CANONICAL_TEXT), max_attempts=1)
    asr_text = r.get("asr_text", "")
    has_kuku = "にくくする" in asr_text
    has_kuka = "にくかする" in asr_text
    result = {
        "attempt": n, "status": r.get("status"), "asr_text": asr_text,
        "has_kuku_correct": has_kuku, "has_kuka_error": has_kuka,
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    n_attempts = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    results = [run_attempt(i) for i in range(1, n_attempts + 1)]
    with open(f"{OUT_DIR}/rca_attempts_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("RCA_ATTEMPTS_DONE")
