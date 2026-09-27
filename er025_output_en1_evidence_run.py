# ============================================================
# er025_output_en1_evidence_run.py (runtime evidence script, not Production)
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 (Phase 2)
# ============================================================
# EN-1 evidence: 既存Ledger low-confidence実例(toteme/kallmeyer、
# cascade_unresolved_entity、既存er014 tiny_bags trial由来の実文)を含む
# 既存segment textで、pre_tts配線後にresolverが発火し、confidenceが
# 改善/注入が行われ、ASR照合PASSすることを確認する。
#
# Family X small_bagはStage 3c完了未確認(docs/pm/RESULT_PACKET_FXA4.md
# 未生成)のため、既存er014 Trial(tiny_bags a2 support、user_test_news_
# light_01)由来の実文で代替する(委任文の代替指示どおり)。
from __future__ import annotations

import json
import os
import time

os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

from dotenv import load_dotenv
load_dotenv()

import er005_cost_logger as cl
import er006_pronunciation_ledger_01 as ledger
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er025_output/pronunciation_resolution_phase2_evidence_01"
os.makedirs(OUT_DIR, exist_ok=True)
cl.install(f"{OUT_DIR}/raw_usage_log_en1.jsonl")

# 実データ(er014_output/user_test_news_light_01/tiny_bags/a2/audit/
# a2_support_generation.json由来の実文の一部)。
TEXT = ("At the same time, very large bags appeared at Celine, Altuzarra, "
        "Toteme, Stella McCartney, and Kallmeyer.")


def main():
    before_toteme = ledger.lookup(ledger.LedgerKey(surface="toteme", entity_type="cascade_unresolved_entity"))
    before_kallmeyer = ledger.lookup(ledger.LedgerKey(surface="kallmeyer", entity_type="cascade_unresolved_entity"))

    out_path = f"{OUT_DIR}/en1_run1.wav"
    t0 = time.time()
    r1 = repro01.generate_narration_snippet_verified_strict(TEXT, "en", out_path, "very large bags",
                                                             max_extra_chars=30)
    elapsed1 = round(time.time() - t0, 2)

    after_toteme = ledger.lookup(ledger.LedgerKey(surface="toteme", entity_type="cascade_unresolved_entity"))
    after_kallmeyer = ledger.lookup(ledger.LedgerKey(surface="kallmeyer", entity_type="cascade_unresolved_entity"))

    summary = {
        "text": TEXT,
        "before": {"toteme": before_toteme, "kallmeyer": before_kallmeyer},
        "after": {"toteme": after_toteme, "kallmeyer": after_kallmeyer},
        "run1": {
            "status": r1.get("status"), "elapsed_seconds": elapsed1,
            "en_pronunciation_resolver_info": r1.get("en_pronunciation_resolver_info"),
            "asr_verified": r1.get("asr_verified"), "asr_text": r1.get("asr_text"),
            "audio_classification": r1.get("audio_classification"),
        },
    }
    with open(f"{OUT_DIR}/en1_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({
        "status": r1.get("status"),
        "before_toteme_confidence": (before_toteme or {}).get("confidence"),
        "after_toteme_confidence": (after_toteme or {}).get("confidence"),
        "before_kallmeyer_confidence": (before_kallmeyer or {}).get("confidence"),
        "after_kallmeyer_confidence": (after_kallmeyer or {}).get("confidence"),
        "hints_applied": (r1.get("en_pronunciation_resolver_info") or {}).get("hints_applied"),
        "asr_verified": r1.get("asr_verified"),
    }, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
