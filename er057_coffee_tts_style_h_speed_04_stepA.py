# -*- coding: utf-8 -*-
"""TRIAL-04 Step A: 長無音位置の集計(API呼出なし、費用0)。Round1-3の測定条件と同一(-40dBFS/50ms)。"""
import os, sys, json, re, collections
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_coffee_v5_pause_01_measure as M
BASE = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03")
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round4"); os.makedirs(OUT, exist_ok=True)
recs = []
for r in (1, 2, 3):
    M.OUT = os.path.join(BASE, f"round{r}")
    for l in open(os.path.join(M.OUT, f"generation_log_r{r}.jsonl"), encoding="utf-8"):
        x = json.loads(l)
        if x.get("status") == "OK": recs.append((r, x))
# H0
H0 = [json.loads(l) for l in open(os.path.join(ROOT, "er057_output/coffee_tts_style_h_speed_02/generation_log_02.jsonl"), encoding="utf-8")]
H0 = [x for x in H0 if x.get("status") == "OK" and x["job"].startswith("H0_")]
def sents(job):
    return M.ref_sents(job)
agg = collections.defaultdict(lambda: {"ge800": 0, "r500_800": 0})
n_wav = collections.Counter(); rows = []
def proc(src, rec, outdir):
    M.OUT = outdir
    p = rec["final_wav"]; lv = rec["level"]; job = f"{lv}_part1"
    x, sr = M.load(p); runs, dur = M.silent_runs(x, sr); w = M.words_of(p)
    ends, nref, ratio = M.ref_end_to_asr(job, w)
    ss = sents(job)
    # boundary k: after ref sentence k (1-based)
    bidx = {}
    for k, i in enumerate(ends):
        if i is not None: bidx[k] = i
    n_wav[lv] += 1
    for c, b in runs:
        d = b - c
        if not (c > 0.005 and b < dur - 0.011) or d < 0.5: continue
        cat = "ge800" if d >= 0.8 else "r500_800"
        hit = None
        for k, i in bidx.items():
            if i + 1 < len(w) and c >= w[i]["e"] - 0.25 and c <= w[i + 1]["s"] + 0.25: hit = k
        if hit is not None:
            prev = ss[hit].split()[-1]; nxt = ss[hit + 1].split()[0]
            key = (lv, "S%02d" % (hit + 1), f"{prev} -> {nxt}", "sentence_end")
        else:
            prev = [q for q in w if q["e"] <= c + 0.15]; nx = [q for q in w if q["s"] >= b - 0.15]
            key = (lv, "mid", f"{prev[-1]['w'] if prev else None} -> {nx[0]['w'] if nx else None}", "mid_sentence")
        agg[key][cat] += 1
        rows.append({"src": src, "level": lv, "t": round(c, 2), "ms": round(d * 1000), "cat": cat, "pos": key[1], "pair": key[2], "kind": key[3]})
for r, x in recs: proc(x["job"], x, os.path.join(BASE, f"round{r}"))
for x in H0: proc(x["job"], x, os.path.join(BASE, "round1"))
json.dump({"n_wav": dict(n_wav), "rows": rows}, open(os.path.join(OUT, "silence_rows_r4.json"), "w"), ensure_ascii=False)
print(dict(n_wav), len(rows))
for lv in ("std", "adv"):
    tot800 = sum(v["ge800"] for k, v in agg.items() if k[0] == lv); tot5 = sum(v["r500_800"] for k, v in agg.items() if k[0] == lv)
    print(lv, "tot>=800", tot800, "tot500-800", tot5)
    for k, v in sorted(((k, v) for k, v in agg.items() if k[0] == lv), key=lambda kv: -(kv[1]["ge800"] * 100 + kv[1]["r500_800"]))[:12]:
        print("  ", k[1:], v)
json.dump({"%s|%s|%s|%s" % k: v for k, v in agg.items()}, open(os.path.join(OUT, "silence_agg_r4.json"), "w"), ensure_ascii=False, indent=1)
