# -*- coding: utf-8 -*-
"""run_e2e_06 / run_e2e_05 の記録からclip別evidenceを集計(API 0、read-only)。"""
import json, os, glob, collections, sys
B = "er026_output/family_z_production_e2e_01/melos"
OUT = "docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/run06_clip_evidence_01.json"

def seg_rows(run):
    rows = {}
    for lv in ("a2", "b1b"):
        d = json.load(open(f"{B}/{run}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
        for sid, s in d["segments"].items():
            aj = s.get("asr_judgement") or {}
            sec = aj.get("secondary") or {}
            rows[(lv, sid)] = {
                "status": s.get("status"), "state": aj.get("state"), "reason_code": aj.get("reason_code"),
                "primary_label": (aj.get("primary") or {}).get("label"),
                "warning_labels": aj.get("warning_labels") or (aj.get("primary") or {}).get("warning_labels"),
                "secondary_ran": bool(sec) and sec.get("text") is not None or bool(sec.get("ran")) if sec else False,
                "secondary_keys": sorted(sec.keys()) if sec else [],
                "tts_generations_used": s.get("tts_generations_used"),
                "n_attempts": len(s.get("attempts") or []),
                "slowdown_applied": s.get("slowdown_applied"),
                "post_slowdown_classification": s.get("post_slowdown_classification"),
                "post_slowdown_expected_text_source": s.get("post_slowdown_expected_text_source"),
                "audio_text_deviation": bool(s.get("audio_text_deviation")),
                "local_rewrite": bool(s.get("local_rewrite_recovery")),
                "model_ids": s.get("model_ids_measured"), "voice": s.get("voice"),
                "style_label": (s.get("style") or {}).get("instruction_label"),
                "asr_text_head": (s.get("asr_text") or "")[:160], "canonical_head": (s.get("canonical_text") or "")[:160],
            }
    return rows

def weight_records(run):
    out = []
    for p in glob.glob(f"{B}/{run}/*/narration/attempts/*.json") + glob.glob(f"{B}/{run}/*/narration/*.json"):
        txt = open(p, encoding="utf-8", errors="replace").read()
        if "azure_phrase_list_weight" in txt:
            try:
                d = json.loads(txt)
            except Exception:
                continue
            def walk(o, path=""):
                if isinstance(o, dict):
                    if "azure_phrase_list_weight" in o:
                        out.append({"file": os.path.basename(p), "step": o.get("step"), "weight": o["azure_phrase_list_weight"],
                                    "phrases": o.get("azure_phrase_list"), "cached": o.get("cached"), "classification": o.get("classification")})
                    for k, v in o.items(): walk(v, path + "/" + k)
                elif isinstance(o, list):
                    for v in o: walk(v, path)
            walk(d)
    return out

r6, r5 = seg_rows("run_e2e_06"), seg_rows("run_e2e_05")
agg = collections.Counter(); 
for (lv, sid), r in r6.items():
    agg[(lv, r["status"], r["state"], r["reason_code"])] += 1
diff = {f"{lv}/{sid}": {"05": {k: r5[(lv, sid)][k] for k in ("state", "reason_code", "primary_label", "n_attempts")}, "06": {k: r[k] for k in ("state", "reason_code", "primary_label", "n_attempts")}}
        for (lv, sid), r in r6.items() if (lv, sid) in r5 and (r["state"], r["reason_code"], r["n_attempts"]) != (r5[(lv, sid)]["state"], r5[(lv, sid)]["reason_code"], r5[(lv, sid)]["n_attempts"])}
res = {"clips_06": {f"{lv}/{sid}": r for (lv, sid), r in r6.items()},
       "aggregate_06": {"|".join(map(str, k)): v for k, v in sorted(agg.items(), key=str)},
       "weight_records_06": weight_records("run_e2e_06"), "weight_records_05": weight_records("run_e2e_05"),
       "diff_vs_05": diff,
       "n_clips_06": len(r6), "n_ok_06": sum(1 for r in r6.values() if r["status"] == "OK"),
       "lr_fired_06": [k for k, r in {f"{lv}/{sid}": r for (lv, sid), r in r6.items()}.items() if r["local_rewrite"]],
       "audio_text_deviation_06": [f"{lv}/{sid}" for (lv, sid), r in r6.items() if r["audio_text_deviation"]]}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(res["n_clips_06"], res["n_ok_06"], len(res["weight_records_06"]), len(res["weight_records_05"]), len(diff), res["lr_fired_06"], res["audio_text_deviation_06"])
print(json.dumps(res["aggregate_06"], ensure_ascii=False, indent=0))
