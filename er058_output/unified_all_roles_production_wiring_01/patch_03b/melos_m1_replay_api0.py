"""API 0: er077 evidence_01/clip_results.json の保存Primary転写(36件)を、新adapter(evaluate_attempt_with_cascade_detail)で再判定する。
Secondary(Azure)は呼ばれても外部へ出ないよう、保存済みprimary転写と同一文字列を返すmockにする(独立証拠なし=受理に使えない設定)。"""
import json
import sys
sys.path.insert(0, ".")
import er006_secondary_asr_01 as sec

sec.semantic_equivalence.append_telemetry_log = lambda *a, **k: None
clips = json.load(open("er077_output/m1_oov_multi_pronunciation_01/evidence_01/clip_results.json", encoding="utf-8"))
rows = []
for c in clips:
    sec._reset_m1_freeze_cache()
    stored_az = None
    for st in c.get("steps") or []:
        if st.get("step") == "secondary_1":
            stored_az = st.get("text"); break
    if stored_az is None:
        for st in c.get("steps") or []:
            if st.get("step") in ("tier3_corroboration_secondary", "non_latin_secondary", "connected_speech_equivalence_secondary"):
                stored_az = st.get("text"); break
    sec.get_full_text_via_azure_stt_with_phrase_list = (lambda t: (lambda *a, **k: (t, None) if t else (None, "no_stored_secondary")))(stored_az)
    r = sec.evaluate_attempt_with_cascade_detail(
        c["text"], c["primary_asr"], [], "no_such.wav", cascade_enabled=True, segment_id=c.get("segment_id"))
    aj = r["asr_judgement"]
    rows.append({"id": c["id"], "canonical": c["text"], "primary_asr": c["primary_asr"],
                 "stored_verified": c["verified"], "stored_final_status": c["final_status"],
                 "new_verified": r["verified"], "new_final_status": r["final_status"], "new_state": aj["state"],
                 "new_reason": aj["reason_code"], "new_m1": bool(r.get("m1_multi_candidate")),
                 "azure_calls": aj["adapter"]["azure_real_calls"]})
agree = sum(1 for x in rows if bool(x["stored_verified"]) == bool(x["new_verified"]))
m1_stored = sum(1 for x in rows if x["stored_final_status"] == "M1_MULTI_CANDIDATE_ACCEPT")
m1_new = sum(1 for x in rows if x["new_m1"])
diff = [x for x in rows if bool(x["stored_verified"]) != bool(x["new_verified"])]
melos = [x for x in rows if x["canonical"].startswith("Melos said")]
print(json.dumps({"clips": len(rows), "verified_agree_with_stored": agree, "m1_accept_stored": m1_stored, "m1_accept_new": m1_new,
                  "melos_said_clips": len(melos), "melos_said_verified_new": sum(1 for x in melos if x["new_verified"]),
                  "melos_said_verified_stored": sum(1 for x in melos if x["stored_verified"]),
                  "disagreements": diff}, ensure_ascii=False, indent=1))
json.dump(rows, open("er058_output/unified_all_roles_production_wiring_01/patch_03b/melos_m1_replay_api0.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
