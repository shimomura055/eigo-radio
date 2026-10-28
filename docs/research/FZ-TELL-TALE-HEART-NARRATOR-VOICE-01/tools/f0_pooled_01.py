"""委任_03: 声ごとのf0をクリップ横断でpoolして中央値・p10/p90を出す(単一clipの揺れ・オクターブ誤検出の影響を減らす)。
usage: f0_pooled_01.py out.csv group=glob [group=glob ...]"""
import sys, glob, csv, numpy as np, soundfile as sf
sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
from f0_measure_01 import f0_track
rows = []
for a in sys.argv[2:]:
    g, pat = a.split("=", 1)
    files = sorted(glob.glob(pat))
    allf = []; per = []
    for f in files:
        x, sr = sf.read(f); t = f0_track(x, sr)
        if len(t) >= 20:
            allf.append(t); per.append(float(np.median(t)))
    if not allf: rows.append([g, 0]); continue
    p = np.concatenate(allf)
    rows.append([g, len(per), len(p)] + [round(float(v), 1) for v in np.percentile(p, [10, 25, 50, 75, 90])] +
                [round(min(per), 1), round(max(per), 1)])
with open(sys.argv[1], "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["group", "n_files", "voiced_frames", "p10", "p25", "median", "p75", "p90", "min_file_median", "max_file_median"]); w.writerows(rows)
for r in rows: print(r)
