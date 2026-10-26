# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01: Adv不変保証用golden fixtureの凍結(実装前のHEAD bb578265cで実行)。
既存X Adv run(uk_train/part2_hr)とY Adv run(redelivery_fee/sns_age_limit)の parts.json に対し、er117の分割計画関数(plan_x_parts / plan_x_part)を
再実行した結果と、既存run保存済み audit/chunk_plan_b1b.json のchunk構成との一致を記録する。実装後は test がこのfixtureとバイト一致を確認する。API 0。"""
import hashlib, json, os, sys
sys.path.insert(0, os.environ.get("FREEZE_MODULE_DIR") or os.getcwd())   # 実装前HEADのer117を指す(git show HEAD:er117...)
import er117_chunk_tts_production_01 as ct

X_RUNS = {
    "x_uk_train_run_chunk_01": "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_chunk_01/b1b",
    "x_part2_hr_evidence_r1": "er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1/b1b",
}
Y_RUNS = {
    "y_redelivery_fee_run_01": "er121_output/family_y_production_01/redelivery_fee/run_01/b1b",
    "y_sns_age_limit_run_01": "er121_output/family_y_production_01/sns_age_limit/run_01/b1b",
}
Y_IDS = ("y_lead", "y_intro_1", "y_voice_1", "y_intro_2", "y_voice_2", "y_intro_3", "y_voice_3", "y_closing")


def sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


out = {"frozen_at_head": os.environ.get("FREEZE_HEAD", "?"), "planner_version": ct.CHUNK_PLANNER_VERSION,
       "extra_pause_seconds": ct.EXTRA_PAUSE_SECONDS, "x": {}, "y": {}}
for k, d in X_RUNS.items():
    parts = json.load(open(f"{d}/parts.json", encoding="utf-8"))
    plans = ct.plan_x_parts(parts)
    saved = json.load(open(f"{d}/audit/chunk_plan_b1b.json", encoding="utf-8"))["plans"]
    same_as_saved = all([(c["chunk_id"], c["text"]) for c in plans[p]["chunks"]] == [(c["chunk_id"], c["text"]) for c in saved[p]["chunks"]] for p in plans)
    out["x"][k] = {"dir": d, "input_parts": {n: parts[n] for n in ("part1", "part2", "part3")}, "plans": plans, "plans_sha256": sha(plans), "equals_saved_audit_plan": same_as_saved}
for k, d in Y_RUNS.items():
    parts = json.load(open(f"{d}/parts.json", encoding="utf-8"))
    plans = {sid: ct.plan_x_part(parts["segments"][sid], sid) for sid in Y_IDS}
    out["y"][k] = {"dir": d, "input_segments": {s: parts["segments"][s] for s in Y_IDS}, "plans": plans, "plans_sha256": sha(plans), "chunked_segments": [s for s, p in plans.items() if p["chunked"]]}
os.makedirs(os.path.dirname(__file__), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "adv_plans_golden_01.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
print(ct.__file__, {k: v["plans_sha256"][:12] for g in ("x", "y") for k, v in out[g].items()}, {k: v["equals_saved_audit_plan"] for k, v in out["x"].items()})
