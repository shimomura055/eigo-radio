import json, shutil
P = "er026_output/family_z_production_e2e_01/melos/run_e2e_02/a2/audit/tts_generation_results.json"
D = "er026_output/family_z_production_e2e_01/melos/evidence_14"
shutil.copyfile(P, f"{D}/pre_slowdown_backup/tts_generation_results_a2_before_update.json")
t = json.load(open(P, encoding="utf-8")); e = t["segments"]["full_story_part1_c5"]
r = json.load(open(f"{D}/slowdown_result_c5.json", encoding="utf-8"))
si = r["slowdown_info"]
e["sha256"] = r["_post_slowdown_sha256"]; e["duration_seconds"] = round(si["dst_duration_seconds"], 3)
e["slowdown_applied"] = True; e["slowdown_info"] = si
e["slowdown_ratio"] = round(si["dst_duration_seconds"] / si["src_duration_seconds"], 4)
e["original_path"] = r.get("original_path")
for k in ("post_slowdown_asr_text", "post_slowdown_classification", "post_slowdown_final_classification", "post_slowdown_cascade"):
    e[k] = r.get(k)
e["post_slowdown_status_honest"] = "STOPPED (減速後再検証 ASR_VALIDATION_UNCERTAIN: Mella/Mallow said, Tier3不成立)。HR個別承認(canonical sha一致)により採用。新規自動PASS規則は不使用"
e["z_adoption"] = "human_review_adopted"
e["pre_slowdown_attempt4_sha256"] = r["_pre_slowdown_sha256"]
json.dump(t, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(e["sha256"][:12], e["slowdown_ratio"], e["status"])
