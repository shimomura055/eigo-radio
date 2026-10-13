# -*- coding: utf-8 -*-
"""state guard: 保護対象ファイルのsha256/行数を記録(begin/end)し不変を確認。python ... --phase begin|end --out <json>"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er069_attribution_clip_split_trial_01_lib as L

TARGETS = [
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/review_lock_state.json",
    "er026_output/family_z_production_e2e_01/melos/run_e2e_02/tts_generation_results.json",
    "er006_output/master_audio_store_01/manifest.json",
    "er011_output/attempt_history.jsonl",
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
]


def snap():
    return {t: {"exists": os.path.exists(t), "sha256": L.sha256_file(t), "lines": L.line_count(t)} for t in TARGETS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["begin", "end"], required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(a.out)) if os.path.exists(a.out) else {}
    d[a.phase] = snap()
    if "begin" in d and "end" in d:
        d["unchanged"] = d["begin"] == d["end"]
        d["changed_files"] = [t for t in TARGETS if d["begin"][t] != d["end"][t]]
    json.dump(d, open(a.out, "w"), indent=1)
    print(a.phase, "unchanged=", d.get("unchanged"), d.get("changed_files"))


if __name__ == "__main__":
    main()
