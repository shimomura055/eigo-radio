# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 異音再検知(無料ローカル、検知器er057_audio_anomaly_detect_trial_01・閾値不変)。usage: python ... adv|std"""
import os, sys, json
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_audio_anomaly_detect_trial_01 as D
V3D = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
OUT = os.path.join(ROOT, "er057_output", "coffee_final_v4")
FIXED = D.FIXED_ASSET_PARTS if hasattr(D, "FIXED_ASSET_PARTS") else ("Intro", "Notification 1", "Notification 2", "Notification 3", "Outro")
lv = sys.argv[1]
man = json.load(open(os.path.join(OUT, "assembly_manifest_v4_01.json"), encoding="utf-8"))["levels"][lv]
x, sr = sf.read(os.path.join(ROOT, man["wav"]), dtype="float64")
c, _ = D.analyze(D.mono(x), sr, "assembled", False)
for ch in range(x.shape[1]):
    for e in D.detect_clip(x[:, ch], sr, "assembled"):
        e["metrics"]["channel"] = ch; c.append(e)
rows = []
for e in c:
    part, tin = D.part_at(man["timeline"], e["t"])
    rows.append({"t_episode": round(e["t"], 3), "part": part, "t_in_part": round(tin, 3) if tin is not None else None, "symptom": e["symptom"],
                 "confidence": e["confidence"], "metrics": e["metrics"], "fixed_asset": part in FIXED})
old = json.load(open(os.path.join(V3D, f"anomaly_v3_{lv}.json"), encoding="utf-8"))
o = {"n_candidates": old["n_candidates"]}
res = {"detector": "er057_audio_anomaly_detect_trial_01(閾値・アルゴリズム不変)", "level": lv, "n_candidates": len(rows), "n_non_fixed": sum(1 for r in rows if not r["fixed_asset"]),
       "candidates": rows, "v3_n_candidates": o["n_candidates"],
       "medium_or_high_non_fixed": [r for r in rows if r["confidence"] in ("high", "medium") and not r["fixed_asset"]],
       "by_part_changed_parts": [r for r in rows if r["part"].startswith("Full Story") or r["part"].startswith("In One Line")]}
json.dump(res, open(os.path.join(OUT, f"anomaly_v4_{lv}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(lv, "n", len(rows), "non_fixed", res["n_non_fixed"], "v2", o["n_candidates"], "med/high non-fixed", len(res["medium_or_high_non_fixed"]))
for r in rows:
    if not r["fixed_asset"]: print(r["part"], r["t_in_part"], r["symptom"], r["confidence"])
