# -*- coding: utf-8 -*-
import os, sys, json, collections, statistics as st
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_coffee_v5_pause_01_measure as M
BASE = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03")
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round4")
recs = []
for r in (1, 2, 3):
    d = os.path.join(BASE, f"round{r}")
    for l in open(os.path.join(d, f"generation_log_r{r}.jsonl"), encoding="utf-8"):
        x = json.loads(l)
        if x.get("status") == "OK": recs.append((d, x))
for l in open(os.path.join(ROOT, "er057_output/coffee_tts_style_h_speed_02/generation_log_02.jsonl"), encoding="utf-8"):
    x = json.loads(l)
    if x.get("status") == "OK" and x["job"].startswith("H0_"): recs.append((os.path.join(BASE, "round1"), x))
pos = {"std": collections.defaultdict(list), "adv": collections.defaultdict(list)}
per = []
for d, x in recs:
    M.OUT = d; a = M.analyze(x["final_wav"]); lv = x["level"]
    ps = a["sentence_end_pauses"]
    for k, q in enumerate(ps): pos[lv][k + 1].append(q["pause_ms"])
    per.append({"job": x["job"], "lv": lv, "n_b": len(ps), "p": [q["pause_ms"] for q in ps], "mean": sum(q["pause_ms"] for q in ps) / max(1, len(ps))})
res = {"n": {lv: len([p for p in per if p["lv"] == lv]) for lv in pos}, "pos_stats": {}}
for lv in pos:
    res["pos_stats"][lv] = {str(k): {"n": len(v), "mean": round(st.mean(v)), "median": round(st.median(v)), "max": max(v)} for k, v in sorted(pos[lv].items())}
# counterfactual (Std 11 boundaries): cap S05,S09 at median of other positions in same wav
cf = {}
for lv, ks in (("std", (5, 9)), ("adv", (5, 7))):
    nb = collections.Counter(len(p["p"]) for p in per if p["lv"] == lv); print(lv, nb); mode = nb.most_common(1)[0][0]; rows = [p for p in per if p["lv"] == lv and len(p["p"]) == mode]
    base_mean = [p["mean"] for p in rows]; cfm = []
    for p in rows:
        oth = [v for i, v in enumerate(p["p"], 1) if i not in ks]; cap = st.median(oth)
        cfm.append(sum((min(v, cap) if i in ks else v) for i, v in enumerate(p["p"], 1)) / len(p["p"]))
    cf[lv] = {"n_wav": len(rows), "mean_of_means": round(st.mean(base_mean)), "mean_if_capped": round(st.mean(cfm)), "frac_le_target_now": None}
    tgt = 498 if lv == "std" else 593
    cf[lv]["frac_le_target_now"] = round(sum(1 for v in base_mean if v <= tgt) / len(rows), 2)
    cf[lv]["frac_le_target_capped"] = round(sum(1 for v in cfm if v <= tgt) / len(rows), 2)
    cf[lv]["mean_without_S%d_S%d" % ks] = round(st.mean([st.mean([v for i, v in enumerate(p["p"], 1) if i not in ks]) for p in rows]))
res["counterfactual"] = cf
json.dump(res, open(os.path.join(OUT, "silence_posstats_r4.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
