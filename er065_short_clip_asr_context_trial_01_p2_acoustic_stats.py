# -*- coding: utf-8 -*-
import json, sys, collections, random
import numpy as np
OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
rows = []; nclip = nskip = 0; wavs = set()
for l in open(OUT + "/acoustic_ss_probe_02b.jsonl", encoding="utf-8"):
    d = json.loads(l)
    if not d.get("rows"): nskip += 1; continue
    nclip += 1
    for r in d["rows"]:
        r = dict(r); r["wav"] = d["wav"]; rows.append(r); wavs.add(d["wav"])
def st(v):
    v = np.array(v, dtype=float); return {"n": len(v), "mean": round(v.mean()), "median": round(float(np.median(v))), "p10": round(float(np.percentile(v, 10))), "p90": round(float(np.percentile(v, 90))), "max": round(v.max())} if len(v) else {"n": 0}
def auc(pos, neg):
    if not len(pos) or not len(neg): return None
    pos, neg = np.array(pos), np.array(neg)
    return round(float(((pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])).mean()), 3)
out = {"n_clips_with_rows": nclip, "n_clips_no_rows": nskip, "n_boundaries": len(rows), "by_threshold": {}}
for th in ("0.3", "0.4", "0.5"):
    k = collections.defaultdict(list)
    for r in rows: k[r["kind"]].append(r["runs"][th])
    A_ = k["A_ss"]; B_ = k["B_single_initial_s"]; C_ = k["C_single_final_s"]
    # clipクラスタを考慮したAUC(クラスタbootstrap)
    byclip = collections.defaultdict(list)
    for r in rows: byclip[r["wav"]].append(r)
    wl = list(byclip); rng = random.Random(3); boots = []
    for _ in range(300):
        smp = [rng.choice(wl) for _ in wl]
        a = [r["runs"][th] for w in smp for r in byclip[w] if r["kind"] == "A_ss"]
        n = [r["runs"][th] for w in smp for r in byclip[w] if r["kind"] != "A_ss"]
        v = auc(a, n)
        if v is not None: boots.append(v)
    ths = {}
    for T in (100, 120, 140, 160, 180, 200):
        ths[T] = {"A_ge": round(float((np.array(A_) >= T).mean()), 3) if A_ else None, "single_ge": round(float((np.array(B_ + C_) >= T).mean()), 3) if B_ + C_ else None}
    out["by_threshold"][th] = {"A_ss": st(A_), "B_single_initial_s": st(B_), "C_single_final_s": st(C_),
                               "AUC_A_vs_single": auc(A_, B_ + C_), "AUC_A_vs_B": auc(A_, B_), "AUC_A_vs_C": auc(A_, C_),
                               "AUC_boot95": [round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)] if boots else None,
                               "threshold_table": ths}
sub = collections.defaultdict(list)
for r in rows:
    if r["kind"] == "A_ss": sub[f"{r['f']}+{r['i']}"].append(r["runs"]["0.4"])
out["A_by_phone_pair_th0.4"] = {k: st(v) for k, v in sub.items()}
# 同一clip内の差(話者・速度の影響を除く): clip内で A_ss と single が両方ある clip のペア差
diffs = []
for w, rs in byclip.items():
    a = [r["runs"]["0.4"] for r in rs if r["kind"] == "A_ss"]; n = [r["runs"]["0.4"] for r in rs if r["kind"] != "A_ss"]
    if a and n: diffs.append(float(np.mean(a) - np.mean(n)))
out["within_clip_diff_th0.4"] = {"n_clips": len(diffs), "mean_diff_ms": round(float(np.mean(diffs)), 1) if diffs else None, "frac_positive": round(float((np.array(diffs) > 0).mean()), 3) if diffs else None}
json.dump(out, open(OUT + "/acoustic_stats_02b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
