"""FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 委任_03: 実音声のf0(基本周波数)計測(API 0)。
自己相関法(numpy)。librosa非導入のため。voiced判定=正規化自己相関>=0.5かつRMS>=-40dBFS相対。
usage: f0_measure_01.py out.csv label=path [label=path ...]   (pathはwav。labelは"Voice:説明"形式)"""
import sys, csv, numpy as np, soundfile as sf
from scipy.signal import resample_poly

def f0_track(x, sr, fmin=60.0, fmax=400.0, frame=0.04, hop=0.01):
    if x.ndim > 1: x = x.mean(axis=1)
    if sr != 16000:
        from math import gcd
        g = gcd(sr, 16000); x = resample_poly(x, 16000 // g, sr // g); sr = 16000
    n, h = int(frame * sr), int(hop * sr)
    lo, hi = int(sr / fmax), int(sr / fmin)
    peak = np.max(np.abs(x)) + 1e-9
    out = []
    for i in range(0, len(x) - n - hi, h):
        f = x[i:i + n]
        rms = np.sqrt(np.mean(f ** 2))
        if rms < peak * 0.03: continue
        f = f - f.mean()
        w = np.hanning(n); fw = f * w
        ac = np.correlate(fw, fw, "full")[n - 1:]
        if ac[0] <= 0: continue
        ac = ac / ac[0]
        seg = ac[lo:hi]
        k = int(np.argmax(seg))
        if seg[k] >= 0.5:
            out.append(sr / (lo + k))
    return np.array(out)

def main():
    out = sys.argv[1]
    rows = []
    for a in sys.argv[2:]:
        label, path = a.split("=", 1)
        x, sr = sf.read(path)
        f0 = f0_track(x, sr)
        if len(f0) < 20:
            rows.append([label, path, len(f0), "", "", "", "", ""]); continue
        p = np.percentile(f0, [10, 25, 50, 75, 90])
        rows.append([label, path, len(f0)] + [round(float(v), 1) for v in p] + [round(float(np.mean(f0)), 1)])
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["label", "path", "voiced_frames", "p10", "p25", "median", "p75", "p90", "mean"])
        w.writerows(rows)
    for r in rows: print(r[0], r[2:], r[1].split("/")[-1])

if __name__ == "__main__":
    main()
