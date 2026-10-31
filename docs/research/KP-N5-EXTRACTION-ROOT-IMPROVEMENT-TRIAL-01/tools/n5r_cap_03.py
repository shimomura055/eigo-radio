"""Trial専用(API 0・LLM呼出なし)。委任_03: 保存済みプール(ev02/rep_*.json)に対するcap感度の追加集計。
pick規則は n5r_lib_02 の既存関数(R0d/R1d/A10/RRF)をそのまま使用。A9は保存済みslate選定(cap7)+run_slate内の既存補充規則(R1d順)。
usage: python n5r_cap_03.py  -> ev03/cap_sensitivity_03.json"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
CAPS = [7, 8, 10, 12, 15]; ARMS = ["R0d", "R1d", "A9", "A10", "A13"]
HR = ["turn into an interrogation", "hear it out"]
fx = L.fixture()
MAIN = {"untidi_a2": "Std", "untidi_b1b": "Adv"}; HELD = ["surname_b1b", "moon_b1b", "melos_a2"]
def ov(a, b): return L.norm_key(a) == L.norm_key(b) or n5._contains(a, b) or n5._contains(b, a)
def inl(sp, lst): return any(ov(sp, x["span"]) for x in lst)
def pick(arm, rep, text, cap):
    J = rep["pools"]["E2"]["judged"]
    if arm == "R0d": return L.pick_R0d(J, text, cap)
    if arm == "R1d": return L.pick_R1d(J, text, cap)
    if arm == "A10": return L.pick_A10(J, text, cap)
    if arm == "A13":
        o = (rep.get("rr", {}).get("E2") or {}).get("order_spans")
        if o is None or "A13" not in rep["picks"]: return None
        return L.pick_RRF(J, text, o, 60, cap)
    if arm == "A9":
        if "A9" not in rep["picks"]: return None
        base = list(rep["picks"]["A9"])[:cap]; tl = text.lower()
        if len(base) < cap:   # run_slate内の既存補充規則(R1d順)
            for c in sorted([c for c in J if c["keep"]], key=lambda c: L._kd(c, tl, L._r1rank(c))):
                if len(base) >= cap: break
                if c not in base and not any(n5._contains(c["span"], x["span"]) or n5._contains(x["span"], c["span"]) for x in base): base.append(c)
        return base[:cap]
reps = {}
for f in sorted(glob.glob(f"{L.EV}/rep_*.json")):
    d = json.load(open(f, encoding="utf-8")); reps.setdefault(d["case"], []).append(d)
dictset = {c: L.e5_find(fx["cases"][c]["text"]) for c in HELD}
rows = []
for case, rl in reps.items():
    if case not in MAIN and case not in HELD: continue
    text = fx["cases"][case]["text"]
    for rep in rl:
        a0 = rep["picks"]["A0"]
        for arm in ARMS:
            for cap in CAPS:
                pk = pick(arm, rep, text, cap)
                if pk is None: continue
                h = L.hits([c["span"] for c in pk])
                r = {"case": case, "rep": rep["rep"], "arm": arm, "cap": cap, "n": len(pk), "pa": h["put_away"], "itw": h["in_the_way"],
                     "both": h["put_away"] and h["in_the_way"], "a0_kept": sum(1 for c in a0 if inl(c["span"], pk)), "n_a0": len(a0),
                     "diff": {d: sum(1 for c in pk if c["difficulty"] == d) for d in ("advanced", "upper_intermediate", "easy")},
                     "entrants": sum(1 for c in pk if not inl(c["span"], a0))}
                r["hr"] = {x: inl(x, pk) for x in HR if inl(x, a0)} if case in MAIN else {}
                if case in HELD:
                    cdict = [c for c in rep["pools"]["E2"]["judged"] if c["cls"] == "C" and c["keep"] and any(ov(c["span"], s) for s in dictset[case])]
                    r["dictC_in_pick"] = sum(1 for c in pk if any(c["span"] == d["span"] for d in cdict)); r["dictC_pool"] = len(cdict)
                    r["dictC_entrants"] = sum(1 for c in pk if any(c["span"] == d["span"] for d in cdict) and not inl(c["span"], a0))
                rows.append(r)
def agg(sel):
    n = len(sel)
    if not n: return None
    hrt = [v for r in sel for v in r["hr"].values()]
    D = {k: sum(r["diff"][k] for r in sel) / n for k in ("advanced", "upper_intermediate", "easy")}; tot = sum(D.values()) or 1
    o = {"reps": n, "both": sum(r["both"] for r in sel), "put_away": sum(r["pa"] for r in sel), "in_the_way": sum(r["itw"] for r in sel),
         "hr_kept": sum(hrt), "hr_total": len(hrt), "a0_kept_mean": round(sum(r["a0_kept"] for r in sel) / n, 2), "n_cand_mean": round(sum(r["n"] for r in sel) / n, 2),
         "diff_mean": {k: round(v, 2) for k, v in D.items()}, "easy_ratio": round(D["easy"] / tot, 3), "upper_ratio": round(D["upper_intermediate"] / tot, 3),
         "entrants_mean": round(sum(r["entrants"] for r in sel) / n, 2)}
    if "dictC_pool" in sel[0]:
        o["dictC_in_pick_mean"] = round(sum(r["dictC_in_pick"] for r in sel) / n, 2); o["dictC_pool_mean"] = round(sum(r["dictC_pool"] for r in sel) / n, 2)
        o["dictC_rate_of_pick"] = round(sum(r["dictC_in_pick"] for r in sel) / max(1, sum(r["n"] for r in sel)), 3)
        o["dictC_recall_proxy"] = round(sum(r["dictC_in_pick"] for r in sel) / max(1, sum(r["dictC_pool"] for r in sel)), 3)
        o["dictC_entrants_mean"] = round(sum(r["dictC_entrants"] for r in sel) / n, 2)
    return o
out = {"caps": CAPS, "arms": ARMS, "untidi": {}, "held_out": {}, "dict_headword_counts": {c: len(v) for c, v in dictset.items()}}
for arm in ARMS:
    for cap in CAPS:
        m = [r for r in rows if r["arm"] == arm and r["cap"] == cap and r["case"] in MAIN]
        out["untidi"][f"{arm}@{cap}"] = {"all": agg(m), "Std": agg([r for r in m if r["case"] == "untidi_a2"]), "Adv": agg([r for r in m if r["case"] == "untidi_b1b"])}
        h = [r for r in rows if r["arm"] == arm and r["cap"] == cap and r["case"] in HELD]
        out["held_out"][f"{arm}@{cap}"] = agg(h)
out["human_load"] = {str(cap): {"per_article_candidates": cap, "Std_plus_Adv": 2 * cap} for cap in CAPS}
json.dump(out, open(os.path.join(L.TD, "ev03", "cap_sensitivity_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(rows, open(os.path.join(L.TD, "ev03", "cap_sensitivity_03_rows.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("rows", len(rows))
for arm in ARMS:
    print(arm)
    for cap in CAPS:
        u = out["untidi"][f"{arm}@{cap}"]; a = u["all"]
        print(f" cap{cap}: both {a['both']}/{a['reps']} (Std {u['Std']['both']}/{u['Std']['reps']}, Adv {u['Adv']['both']}/{u['Adv']['reps']}) pa {a['put_away']} itw {a['in_the_way']} HR {a['hr_kept']}/{a['hr_total']} A0kept {a['a0_kept_mean']} easy {a['easy_ratio']} upper {a['upper_ratio']}")
