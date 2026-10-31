# B1(a): 事前登録の既知の文脈依存項目を A 3回・M(最終候補) 3回生成した成功率。make=ブラインドシート作成、score=採点集計。
import json, os, random, re, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = [("family_z_melos_kphr_evidence_r3", "std_13-s010"), ("family_z_melos_kphr_evidence_r3", "std_13-s019"), ("family_z_melos_kphr_evidence_r3", "std_13-s020"),
         ("family_z_melos_kphr_evidence_r3", "adv_12-s038"), ("family_x_untidiness_family_resource_01", "adv_19-s044")]
FINAL = "EV"
SRC = {  # label -> list of (dir, file tag)
 "A": [("ev05_dev", "A"), ("ev05_dev", "Ap"), ("ev07_b1a", "A_x1")],
 "M": [("ev05_dev", FINAL), ("ev07_b1a", FINAL + "_x1"), ("ev07_b1a", FINAL + "_x2")]}
SRC_HELD = {"A": [("ev06_heldout", "A"), ("ev06_heldout", "Ap"), ("ev07_b1a", "A_x1")], "M": [("ev06_heldout", FINAL), ("ev07_b1a", FINAL + "_x1"), ("ev07_b1a", FINAL + "_x2")]}
def load(dirn, tag):
    out = {}
    p = os.path.join(D, dirn, f"parts_{tag}.jsonl")
    if not os.path.exists(p):
        return out
    for ln in open(p, encoding="utf-8"):
        r = json.loads(ln)
        for sid, ja in r["ja"].items():
            out[r["slug"] + "|" + sid] = ja
    return out
sets = json.load(open(os.path.join(D, "ev05_common", "eval_sets_03.json"), encoding="utf-8"))
en = {e["slug"] + "|" + s["sid"]: s["en"] for sp in sets.values() for e in sp for s in e["sentences"]}
def gen(item):
    slug, sid = item
    src = SRC_HELD if "untidiness" in slug else SRC
    got = {}
    for k, lst in src.items():
        got[k] = [load(d, t).get(slug + "|" + sid, "MISSING") for d, t in lst]
    return got
mode = sys.argv[1]
if mode == "make":
    rng = random.Random(20261031); sheet = []; key = {}
    for n, it in enumerate(ITEMS, 1):
        g = gen(it); vs = {}
        for k, lst in g.items():
            for i, t in enumerate(lst):
                if t is not None and t != "MISSING":
                    vs.setdefault(t, []).append(f"{k}#{i+1}")
                else:
                    vs.setdefault("(None)" if t is None else "MISSING", []).append(f"{k}#{i+1}")
        texts = [t for t in vs if t not in ("(None)", "MISSING")]
        rng.shuffle(texts)
        letters = "ABCDEFGHIJKLMNOP"[:len(texts)]
        sheet.append({"row": n, "en": en[it[0] + "|" + it[1]], "variants": dict(zip(letters, texts))})
        key[str(n)] = {"item": list(it), "map": {L: vs[t] for L, t in zip(letters, texts)}, "none": vs.get("(None)", []), "missing": vs.get("MISSING", [])}
    json.dump(sheet, open(os.path.join(D, "ev07_b1a", "b1a_sheet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(key, open(os.path.join(D, "ev07_b1a", "b1a_key.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    for r in sheet:
        print(f"#{r['row']} EN: {r['en']}")
        for L, t in r["variants"].items():
            print(f"  {L}: {t}")
elif mode == "score":
    key = json.load(open(os.path.join(D, "ev07_b1a", "b1a_key.json"), encoding="utf-8"))
    gr = {}
    for ln in open(sys.argv[2], encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        t = ln.split(); gr[t[0]] = {m.group(1): int(m.group(2)) for x in t[1:] for m in [re.match(r"([A-Z])([0-3])", x)] if m}
    tot = {"A": [0, 0], "M": [0, 0]}
    for row, k in key.items():
        res = {"A": [], "M": []}
        for L, labs in k["map"].items():
            g = gr[row].get(L, 0)
            for lab in labs:
                res[lab[0]].append((lab, g == 0))
        for lab in k["none"]:
            res[lab[0]].append((lab, False))
        line = {kk: f"{sum(1 for _, ok in v if ok)}/{len(v)}" for kk, v in res.items()}
        print(k["item"][1], line, "missing:", k["missing"])
        for kk in res:
            tot[kk][0] += sum(1 for _, ok in res[kk] if ok); tot[kk][1] += len(res[kk])
    ra = tot["A"][0] / tot["A"][1]; rm = tot["M"][0] / tot["M"][1]
    print("A success", tot["A"], round(ra, 3), "M success", tot["M"], round(rm, 3), "diff(pt)", round((rm - ra) * 100, 1), "B1a_pass(>= +15pt):", (rm - ra) * 100 >= 15)
