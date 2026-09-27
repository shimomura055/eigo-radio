# ============================================================
# er025_output_ja2_evidence_run.py (runtime evidence script, not Production)
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 (Phase 2)
# ============================================================
# JA-2 evidence: 合成fixture(辞書未登録の実在企業名"Figma"を含む日本語文、
# Muse以外)で、検出->web lookup発火->confidence判定->自動使用->TTS成功->
# Ledger保存->2回目実行でcache hit・追加lookup0回、の6項目を確認する。
from __future__ import annotations

import json
import os
import time

os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er003_v1_n3_01_tts_generate as ttsgen
import er005_cost_logger as cl
import er006_pronunciation_ledger_01 as ledger
import er025_entity_pronunciation_resolver_core_01 as core

OUT_DIR = "er025_output/pronunciation_resolution_phase2_evidence_01"
os.makedirs(OUT_DIR, exist_ok=True)
cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

TEXT = "多くのデザイナーがFigmaを使ってプロトタイプを作成しています。"
EXPECTED_SUBSTRING = "多くのデザイナー"


def main():
    core.reset_run_caches()
    # 事前状態確認(未登録であること)
    pre_existing = ledger.get_ja_reading_entry("figma")

    out_path_1 = f"{OUT_DIR}/ja2_run1.wav"
    t0 = time.time()
    r1 = ttsgen.generate_a2_japanese_with_reading_safety(TEXT, out_path_1, EXPECTED_SUBSTRING)
    elapsed1 = round(time.time() - t0, 2)

    resolver_info_1 = r1.get("ja_pronunciation_resolver_info", {})

    # 2回目実行(同一プロセス内、run cacheでweb lookup再発火なしを確認)
    out_path_2 = f"{OUT_DIR}/ja2_run2.wav"
    t1 = time.time()
    r2 = ttsgen.generate_a2_japanese_with_reading_safety(TEXT, out_path_2, EXPECTED_SUBSTRING)
    elapsed2 = round(time.time() - t1, 2)
    resolver_info_2 = r2.get("ja_pronunciation_resolver_info", {})

    stored_after = ledger.get_ja_reading_entry("figma")

    summary = {
        "text": TEXT,
        "pre_existing_ledger_entry": pre_existing,
        "run1": {
            "status": r1.get("status"), "elapsed_seconds": elapsed1,
            "resolver_info": resolver_info_1,
            "asr_verified": r1.get("asr_verified"), "asr_text": r1.get("asr_text"),
            "reason": r1.get("reason"),
        },
        "run2": {
            "status": r2.get("status"), "elapsed_seconds": elapsed2,
            "resolver_info": resolver_info_2,
            "asr_verified": r2.get("asr_verified"), "asr_text": r2.get("asr_text"),
            "reason": r2.get("reason"),
        },
        "stored_ledger_entry_after": stored_after,
        "cache_hit_confirmed_run2": resolver_info_2.get("web_lookup_called") is False,
    }
    with open(f"{OUT_DIR}/ja2_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({
        "run1_status": r1.get("status"), "run1_web_lookup_called": resolver_info_1.get("web_lookup_called"),
        "run2_status": r2.get("status"), "run2_web_lookup_called": resolver_info_2.get("web_lookup_called"),
        "resolved_run1": resolver_info_1.get("resolved"),
    }, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
