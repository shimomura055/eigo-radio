# -*- coding: utf-8 -*-
"""PACE-02 ピッチ/エネルギー簡易統計(無料、機械指標。聴感評価ではない)。F5基準と各候補Part1-3連結で比較。"""
import json, glob, os, numpy as np, soundfile as sf
from scipy.signal import resample_poly, fftconvolve
ROOT = "C:/Users/tensh/eigo-radio"; OUT = f"{ROOT}/er057_output/pace_trial_02"
F5 = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_final/segments"
def track(y, sr=16000, fl=640, hop=160):
    f0, rms = [], []
    lo, hi = int(sr/400), int(sr/75)
    for i in range(0, len(y) - fl, hop):
        fr = y[i:i+fl]; r = float(np.sqrt(np.mean(fr**2))); rms.append(r); fr = fr - fr.mean()
        ac = fftconvolve(fr, fr[::-1])[fl-1:]
        if ac[0] <= 0: f0.append(np.nan); continue
        ac = ac / ac[0]; k = lo + int(np.argmax(ac[lo:hi]))
        f0.append(sr / k if ac[k] > 0.5 and r > 0.01 else np.nan)
    return np.array(f0), np.array(rms)
def stats(paths):
    f0s, rms = [], []
    for p in paths:
        x, sr = sf.read(p, dtype="float32"); x = x.mean(axis=1) if x.ndim > 1 else x
        y = resample_poly(x, 16000, sr) if sr != 16000 else x
        f, r = track(y); f0s.append(f[~np.isnan(f)]); rms.append(r)
    f = np.concatenate(f0s); r = np.concatenate(rms); act = r > 0.02 * r.max()
    st = 12 * np.log2(f / np.median(f)); db = 20*np.log10(r[act]+1e-9)
    return {"f0_median_hz": round(float(np.median(f)), 1), "f0_range_st_p10_p90": round(float(np.percentile(st, 90) - np.percentile(st, 10)), 2),
            "f0_std_st": round(float(np.std(st)), 2), "voiced_ratio": round(float(len(f) / act.sum()), 3),
            "rms_dyn_db_p10_p90": round(float(np.percentile(db, 90) - np.percentile(db, 10)), 2)}
res = {"F5": stats([f"{F5}/adv_part{n}_f5.wav" for n in (1, 2, 3)])}
for c in [f"PD{i}" for i in range(1, 9)]:
    res[c] = stats([f"{OUT}/attempts/{c}_adv_part{n}.wav" for n in (1, 2, 3)]); print(c, res[c], flush=True)
print("F5", res["F5"])
json.dump(res, open(f"{OUT}/prosody_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
