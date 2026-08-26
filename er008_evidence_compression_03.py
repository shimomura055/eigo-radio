# ============================================================
# er008_evidence_compression_03.py
# ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03 Part B
# ============================================================
# No.7を対象に、Evidence Compression方針(spoken layerの固有名詞・数字を
# 減らす)を適用したcandidate scriptのみを生成する(script-only、TTS/ASR
# は実行しない)。Production Writerのopt-in経路(evidence_compression=True、
# 既定Falseで無変更)を使い、既存Baseline(article.md/parts.json)とは
# 完全に別ディレクトリへ出力する。

from __future__ import annotations

import json

import er008_n7_baseline_reset_01 as baseline

THEME_ID = baseline.THEME_ID
OUT_DIR = baseline.OUT_DIR
TOPIC_JA = baseline.TOPIC_JA
CANDIDATE_DIR = f"{OUT_DIR}/evidence_compression_candidate"


def run_candidate_writer() -> dict:
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"

    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_JA, ledger_path, CANDIDATE_DIR,
        blueprint=None, evidence_compression=True)
    print(f"[{THEME_ID}] Evidence Compression candidate Writer完了。")
    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return result


if __name__ == "__main__":
    import sys
    import er005_cost_logger as cl
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "writer":
        run_candidate_writer()
    else:
        print("usage: er008_evidence_compression_03.py writer")
