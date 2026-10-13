# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01: Production state guard(読み取りのみ、sha256/行数を記録)。"""
import hashlib, json, os, sys, time

GUARDED = [
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/a2/audit/review_lock_state.json",
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/a2/audit/tts_generation_results.json",
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/b1b/audit/review_lock_state.json",
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/b1b/audit/tts_generation_results.json",
    "er006_output/master_audio_store_01/manifest.json",
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er011_output/attempt_history.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
]


def snapshot(root=".") -> dict:
    out = {}
    for rel in GUARDED:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            out[rel] = {"exists": False}
            continue
        h = hashlib.sha256()
        lines = 0
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
                lines += chunk.count(b"\n")
        out[rel] = {"exists": True, "sha256": h.hexdigest(), "lines": lines, "bytes": os.path.getsize(p)}
    return out


def diff(before: dict, after: dict) -> dict:
    return {k: (before[k] == after[k]) for k in before}


if __name__ == "__main__":
    json.dump({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": snapshot()}, sys.stdout, indent=1)
