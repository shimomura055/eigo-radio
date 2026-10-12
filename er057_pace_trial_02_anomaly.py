# -*- coding: utf-8 -*-
"""委任_01(PACE-02) 異音検知(既存検知器 er057_audio_anomaly_detect_trial_01 無改変・閾値不変、無料ローカル)。基準F5 3Partも同条件で検知。"""
import os, sys, json, glob
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_audio_anomaly_detect_trial_01 as D
OUT = f"{ROOT}/er057_output/pace_trial_02"
F5 = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_final/segments"
files = {os.path.basename(p)[:-4]: p for p in sorted(glob.glob(f"{OUT}/attempts/PD*_adv_part*.wav"))}
for n in (1, 2, 3): files[f"F5_adv_part{n}"] = f"{F5}/adv_part{n}_f5.wav"
res = {}
for k, p in files.items():
    x, sr = sf.read(p, dtype="float64")
    c, _ = D.analyze(D.mono(x), sr, k, True)
    res[k] = [{**e, "t": round(float(e["t"]), 3), "metrics": {a: (round(b, 3) if isinstance(b, float) else b) for a, b in e["metrics"].items()}} for e in c]
    print(k, len(c), [(e["symptom"], e["confidence"], e["t"]) for e in res[k]], flush=True)
json.dump(res, open(f"{OUT}/anomaly_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
