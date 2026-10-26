# -*- coding: utf-8 -*-
"""3回目(従来方式)のTTS promptが、従来Dialogue Styleの現行builder出力とバイト一致(sha256)することの検証。read-only(API 0)。"""
import hashlib, json, sys
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a

D = "docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01"
M = "er026_output/family_z_production_e2e_01/melos"
CASES = [("E-2", "run_fzcw_e2_a2_01", "a2", "RUNTIME_EVIDENCE_E-2_run_fzcw_e2_a2_01.json", -1),
         ("E-2", "run_fzcw_e2_b1b_01", "b1b", "RUNTIME_EVIDENCE_E-2_run_fzcw_e2_b1b_01.json", -1),
         ("E-3", "run_fzcw_e3_a2_01", "a2", "RUNTIME_EVIDENCE_E-3_run_fzcw_e3_a2_01_resume.json", -1),
         ("E-4", "run_fzcw_e4_a2_01", "a2", "RUNTIME_EVIDENCE_E-4_run_fzcw_e4_a2_01.json", -1),
         ("E-4", "run_fzcw_e4_b1b_01", "b1b", "RUNTIME_EVIDENCE_E-4_run_fzcw_e4_b1b_01.json", -1)]
out = []
for case, run, lv, ef, idx in CASES:
    e = json.load(open(f"{D}/{ef}", encoding="utf-8"))
    r = json.load(open(f"{M}/{run}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
    seg = r["segments"]["full_story_part1_c2"]
    legacy = p4c.build_tts_prompt(seg["text"], p9a.ENGLISH_STYLE_PREFIX)
    req = e["tts_requests"][idx]
    ctx_reqs = [x for x in e["tts_requests"] if x["has_context"]]
    out.append({"case": case, "run": run, "level": lv, "attempt3_prompt_sha256": req["prompt_sha256"], "legacy_builder_sha256": hashlib.sha256(legacy.encode()).hexdigest(),
                "byte_identical_to_legacy_builder": req["prompt_sha256"] == hashlib.sha256(legacy.encode()).hexdigest(), "attempt3_has_context_marker": req["has_context"],
                "ctx_requests_in_this_process": len(ctx_reqs), "dialogue_tts_final": seg.get("dialogue_tts")})
json.dump(out, open(f"{D}/legacy_prompt_check_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in out:
    print(o["case"], o["run"], "identical=", o["byte_identical_to_legacy_builder"], "ctx_marker=", o["attempt3_has_context_marker"])
