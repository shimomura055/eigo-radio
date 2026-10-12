# -*- coding: utf-8 -*-
"""V5 style適用evidence集計(無料・読み取りのみ): attempts JSONのinstruction_text sha、style_profile記録、raw_usage_logのmodel_id、費用。"""
import json, glob, hashlib, os, sys
sys.path.insert(0, os.getcwd())
import er019_family_x_style_profile_01 as sp
O = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01"
H = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
out = {"run_dir": O, "levels": {}}
for lv, names, exp in (("a2", ["preview", "comment_1", "comment_2", "comment_3", "comment_4"], sp.R2_SHA256),
                       ("b1b", [f"kp{i}_explanation_en" for i in range(1, 6)], sp.P3_SHA256)):
    rows = []
    for n in names:
        for f in sorted(glob.glob(f"{O}/{lv}/narration/attempts/{n}_attempt*.json")):
            d = json.load(open(f, encoding="utf-8"))
            ins = d.get("instruction_text") or ""
            rows.append({"clip": n, "attempt": d.get("loop_attempt_index"), "model": d.get("model"), "voice": d.get("voice"), "tts_backend": d.get("tts_backend"),
                         "exec_mode": d.get("tts_execution_mode"), "instruction_sha256": H(ins), "instruction_len": len(ins), "equals_expected_style": H(ins) == exp,
                         "instruction_startswith_expected": None, "verified": d.get("verified"), "audio_classification": d.get("audio_classification"), "asr_text": d.get("asr_text")})
    out["levels"][lv] = {"expected_sha256": exp, "attempts": rows}
res = {}
for lv in ("a2", "b1b"):
    p = f"{O}/{lv}/audit/tts_generation_results.json"
    if os.path.exists(p):
        res[lv] = json.load(open(p, encoding="utf-8"))
if "a2" in res:
    segs = {k: v for k, v in res["a2"]["segments"].items() if k in ("preview", "comment_1", "comment_2", "comment_3", "comment_4")}
    out["a2_results"] = {k: {"status": v.get("status"), "fallback_used": v.get("fallback_used"), "style_profile": v.get("style_profile"), "model": v.get("model"),
                              "asr_verified": v.get("asr_verified"), "audio_classification": v.get("audio_classification"), "asr_text": v.get("asr_text"),
                              "canonical_text": v.get("canonical_text"), "wav_sha256": hashlib.sha256(open(f"{O}/a2/narration/{k}.wav", "rb").read()).hexdigest()} for k, v in segs.items()}
    gate = sp.m3_assembly_gate("coffee_final_v5", "a2", {"segments": segs})
    out["a2_m3_gate_support_ja_only"] = {"blocked": [b for b in gate["blocked"] if not b["segment"].startswith(("full_story", "topic", "in_one"))]}
    out["a2_m3_gate_support_ja_only"]["note"] = "full_story_*はv4音声流用のためruntime生成なし(SKIPPED_NOT_SELECTED)。SUPPORT_JA 5件のみ判定"
if "b1b" in res and res["b1b"].get("key_phrases"):
    kps = res["b1b"]["key_phrases"]
    out["b1b_results"] = {k: {"status": (v.get("explanation") or {}).get("status"), "style_profile": (v.get("explanation") or {}).get("style_profile")} for k, v in kps.items()}
# cost
tot = {}
for l in open(f"{O}/raw_usage_log.jsonl", encoding="utf-8"):
    r = json.loads(l)
    tot.setdefault(r.get("provider"), 0)
    tot[r["provider"]] += 1
out["raw_usage_log_calls_by_provider"] = tot
models = {}
for l in open(f"{O}/raw_usage_log.jsonl", encoding="utf-8"):
    r = json.loads(l); models[(r.get("provider"), r.get("model_id"))] = models.get((r.get("provider"), r.get("model_id")), 0) + 1
out["models"] = {f"{k[0]}|{k[1]}": v for k, v in models.items()}
json.dump(out, open("er057_output/coffee_final_v5/style_application_evidence_v5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for lv, d in out["levels"].items():
    for r in d["attempts"]:
        print(lv, r["clip"], "att", r["attempt"], r["model"], r["voice"], r["exec_mode"], "style_ok" if r["equals_expected_style"] else "STYLE_DIFF", r["audio_classification"], "verified=", r["verified"])
print(json.dumps(out.get("a2_m3_gate_support_ja_only"), ensure_ascii=False))
print(out["models"])
