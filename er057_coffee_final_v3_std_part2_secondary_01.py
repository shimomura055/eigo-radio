# -*- coding: utf-8 -*-
"""委任_02: Std Part2の3候補に、Production承認済みSecondary cascade(er006_secondary_asr_01.evaluate_attempt_with_cascade_detail)をTrial隔離で適用。
Primary ASR文は委任_01のgeneration_logの記録を再利用(Primary再呼出なし)。ledger書込/human_review_queue/telemetryは書かない。"""
import os, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
B.patch_validator_telemetry()
import er006_secondary_asr_01 as sec
sec._resolve_unresolved_entity_for_review = lambda span: None   # Production ledger(upsert)へ書かない
OUT = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
import er005_cost_logger as cl
cl.init_logger(os.path.join(OUT, "cost_log_std_part2_secondary_01.jsonl"))  # Trial専用(Production cost logへ書かない)
recs = [json.loads(l) for l in open(os.path.join(OUT, "generation_log_v3_01.jsonl"), encoding="utf-8") if l.strip()]
recs = [r for r in recs if r.get("job") == "std_part2" and r.get("asr_text")]
import soundfile as sf
res = []
for r in recs:
    wav = os.path.join(ROOT, r["wav"])
    detail = sec.evaluate_attempt_with_cascade_detail(r["tts_input_text"], r["asr_text"], [], wav, language="en-US", ledger_phrases=None,
        cascade_enabled=True, enable_connected_speech_equivalence_layer=True, segment_id="full_story_part2")
    dur = sf.info(wav).duration
    az = sum(1 for s in detail["steps"] if s.get("provider") == "azure")
    cost = az * dur * (0.0003 / 1.0) * 160 / 1.0  # Azure概算 $0.00028/秒相当
    cls = detail["classification"]
    out = {"attempt": r["attempt"], "wav": r["wav"], "wav_sha256": r["wav_sha256"], "duration_s": round(dur, 2), "verified": detail["verified"],
           "final_status": detail["final_status"], "cascade_invoked": detail["cascade_invoked"], "human_review_required": detail["human_review_required"],
           "steps": [{k: v for k, v in s.items() if k in ("step", "provider", "text", "classification", "layer_judgment", "sub_reason")} for s in detail["steps"]],
           "semantic_equivalence_info": getattr(cls, "semantic_equivalence_info", None), "connected_speech_info": getattr(cls, "connected_speech_info", None) and
           {k: v for k, v in getattr(cls, "connected_speech_info").items() if k not in ("secondary_asr_text", "local_asr_text")},
           "azure_calls": az, "azure_cost_jpy_est": round(cost, 2)}
    res.append(out)
    print(r["attempt"], detail["verified"], detail["final_status"], az, round(cost, 2), flush=True)
json.dump({"results": res, "validator_telemetry_redirected": B._sem_telemetry}, open(os.path.join(OUT, "std_part2_secondary_cascade_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
