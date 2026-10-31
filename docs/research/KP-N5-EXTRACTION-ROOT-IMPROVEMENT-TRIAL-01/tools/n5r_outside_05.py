"""Trial専用(API 0)。委任_05: A案cap10に入らなかった(プールにある)候補・SEL非keep候補・Gate/pool脱落候補を、全repの出現頻度で一覧化する(N5外の表現の学習価値評価の材料)。
usage: python n5r_outside_05.py -> ev05/outside_05.json と標準出力"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
EV2 = os.path.join(L.TD, "ev02"); EV5 = os.path.join(L.TD, "ev05")
fx = L.fixture()
CASES = ["untidi_a2", "untidi_b1b", "melos_a2", "moon_b1b", "surname_b1b"]
res = {}
for case in CASES:
    text = fx["cases"][case]["text"]
    reps = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(f"{EV2}/rep_{case}_*.json"))]
    N = len(reps)
    agg = {}
    for r in reps:
        sel = [c["span"] for c in L.pick_A10(r["pools"]["E2"]["judged"], text, 10)]
        sel_k = {L.norm_key(s) for s in sel}
        seen = set()
        for c in r["pools"]["E2"]["judged"]:
            k = L.norm_key(c["span"])
            if k in seen:
                continue
            seen.add(k)
            d = agg.setdefault(k, {"span": c["span"], "n_pool": 0, "n_keep": 0, "n_in_cap10": 0, "labels": {}, "reason": c.get("chunk_reason_ja")})
            d["n_pool"] += 1
            d["n_keep"] += 1 if c["keep"] else 0
            d["n_in_cap10"] += 1 if (k in sel_k or any(n5._contains(c["span"], s) or n5._contains(s, c["span"]) for s in sel)) else 0
            lab = f"{c['cls']}/{c['chunk_type']}/{c['difficulty']}" + ("" if c["keep"] else "/nonkeep")
            d["labels"][lab] = d["labels"].get(lab, 0) + 1
    rows = sorted(agg.values(), key=lambda d: (-d["n_keep"], -d["n_pool"]))
    res[case] = {"n_reps": N, "rows": rows}
    print("====", case, "reps", N, "pool distinct", len(rows))
    for d in rows:
        if d["n_in_cap10"] < d["n_pool"] * 0.5:     # cap10にほとんど入らない
            print(f"  {d['span']!r:40} pool {d['n_pool']}/{N} keep {d['n_keep']} cap10 {d['n_in_cap10']}  {max(d['labels'], key=d['labels'].get)}  | {d['reason']}")
json.dump(res, open(f"{EV5}/outside_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
