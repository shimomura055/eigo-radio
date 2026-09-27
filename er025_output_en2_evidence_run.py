# ============================================================
# er025_output_en2_evidence_run.py (runtime evidence script, not Production)
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 (Phase 2)
# ============================================================
# EN-2 evidence: 略語(頭字語読みか単語読みか曖昧なもの、"OPEC" = 単語読み
# "OH-peck"であり、O-P-E-Cの文字読みではない)を含む短文fixture。
#
# 残課題(REPORTに明記): 記事レベルでのextract_proper_nouns()自動発火は
# 本Phaseでは未配線(Family X production runner側の変更が必要だが、
# 並走Agent[Stage 3c]との衝突回避のため本Phaseでは対象外、詳細REPORT
# 「残課題」節)。本evidenceでは、既存(無改変)のextract_proper_nouns()/
# research_pronunciations()を直接呼び出してLedgerへ事前投入することで、
# 「記事レベル抽出が将来配線された場合に何が起きるか」を、新設した
# pre_tts cache-hit注入経路(resolve_and_augment_en_style_prefix)側の
# 検証に限定して確認する。
from __future__ import annotations

import json
import os
import time

os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

from dotenv import load_dotenv
load_dotenv()

import er005_cost_logger as cl
import er006_pronunciation_ledger_01 as ledger
import er006_pronunciation_research_01 as en_research
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er025_output/pronunciation_resolution_phase2_evidence_01"
os.makedirs(OUT_DIR, exist_ok=True)
cl.install(f"{OUT_DIR}/raw_usage_log_en2.jsonl")

TEXT = "OPEC announced new production targets at its meeting today."


def main():
    pre_existing = ledger.get_hint_for_text(TEXT, min_confidence="low")
    seeded = None
    if not pre_existing:
        entities = [{"surface": "OPEC", "entity_type": "organization",
                     "risk_reason": "頭字語読み(O-P-E-C)か単語読み(OH-peck)か曖昧"}]
        research_result = en_research.research_pronunciations(entities)
        if research_result.get("status") == "OK":
            ids = ledger.upsert_research_result(
                entities, research_result["items"], sources=research_result.get("citations", []))
            seeded = {"research_status": research_result.get("status"), "ids": ids,
                      "items": research_result.get("items")}
        else:
            seeded = {"research_status": research_result.get("status"), "error": research_result}

    out_path = f"{OUT_DIR}/en2_run1.wav"
    t0 = time.time()
    r1 = repro01.generate_narration_snippet_verified_strict(TEXT, "en", out_path, "OPEC announced")
    elapsed1 = round(time.time() - t0, 2)

    summary = {
        "text": TEXT,
        "pre_existing_ledger_hint": pre_existing,
        "seeded_via_existing_research_pipeline": seeded,
        "run1": {
            "status": r1.get("status"), "elapsed_seconds": elapsed1,
            "en_pronunciation_resolver_info": r1.get("en_pronunciation_resolver_info"),
            "asr_verified": r1.get("asr_verified"), "asr_text": r1.get("asr_text"),
            "audio_classification": r1.get("audio_classification"),
        },
    }
    with open(f"{OUT_DIR}/en2_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({
        "status": r1.get("status"), "hints_applied": (r1.get("en_pronunciation_resolver_info") or {}).get("hints_applied"),
        "asr_verified": r1.get("asr_verified"),
    }, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
