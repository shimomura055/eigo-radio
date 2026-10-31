# -*- coding: utf-8 -*-
"""JA-GLOSS-NUANCE-01: Trial出力(out/*.json)と保存済み本番出力(inputs/*_stored_meta.json)をitem単位で並べる。
サブコマンド: table(arm開示の比較表) / blind(A/B順を乱数で伏せた判定シートとmapping) / checks(既存検査・2訳語・token集計)"""
import json, os, re, sys, glob, random, collections
D = sys.argv[2] if len(sys.argv) > 2 else "."
def items_of_prompt(tag):
    t = open(f"{D}/inputs/{tag}.txt", encoding="utf-8").read()
    i = t.find("【対象項目】"); j = t.find("【記事本文(参考)】")
    return {it["rank"]: it for it in json.loads(t[i + len("【対象項目】"):j])}
def stored(tag):
    d = json.load(open(f"{D}/inputs/{tag}_stored_meta.json", encoding="utf-8"))
    return {int(k): v[-1]["proposed_gloss"] for k, v in d["item_log"].items()}
def runs(tag):
    out = collections.OrderedDict()
    for p in sorted(glob.glob(f"{D}/out/{tag}__*.json")):
        r = json.load(open(p, encoding="utf-8"))
        arm, rep = r["job"]["arm"], r["job"]["rep"]
        resp = json.loads(r["output_text"])
        out[(arm, rep)] = {"items": {it["rank"]: it for it in resp["items"]}, "usage": r["usage"], "cost": r["cost_jpy"]}
    return out
TAGS = os.environ.get("JAG_TAGS", "untidiness,moon,jwst,aichat,meta").split(",")
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "table":
        for tag in TAGS:
            P, S, R = items_of_prompt(tag), stored(tag), runs(tag)
            print(f"== {tag}")
            for rk, it in P.items():
                cells = [f"Ast={S.get(rk)}"]
                for (arm, rep), v in R.items():
                    g = v["items"].get(rk, {}).get("japanese_gloss")
                    cells.append(f"{arm}{rep}={g}")
                print(f"  {rk:>2} {it['key_phrase']} | " + " | ".join(cells))
    elif cmd == "checks":
        tot = collections.defaultdict(lambda: {"n": 0, "multi": 0, "viol": 0, "out": 0, "calls": 0, "len": 0})
        for tag in TAGS:
            for (arm, rep), v in runs(tag).items():
                t = tot[arm]; t["calls"] += 1; t["out"] += v["usage"]["output_tokens"]
                for rk, it in v["items"].items():
                    g = it["japanese_gloss"]; t["n"] += 1; t["len"] += len(g)
                    if re.search("[、,]", g): t["multi"] += 1; print("MULTI", arm, tag, rk, g)
                    if re.search("[()（）]|…|[0-9]", g) or not g.strip() or it["naive_ja_conveys"] not in ("yes", "partly", "no"): t["viol"] += 1; print("VIOL", arm, tag, rk, g)
        for a, t in tot.items(): print(a, t, "mean_out_tokens", round(t["out"] / t["calls"]), "mean_len", round(t["len"] / t["n"], 2))

def norm(g):
    return re.sub(r"[〜～~\s]", "", g or "")
def pairs_blind(armX, repX, armY, repY, seed, label):
    """armX/repX と armY/repY が異なるitemだけを、順序を乱数で伏せて列挙。mappingは別file。"""
    rnd = random.Random(seed); rows = []; mapping = {}
    for tag in TAGS:
        P, R = items_of_prompt(tag), runs(tag)
        X, Y = R.get((armX, repX)), R.get((armY, repY))
        if not X or not Y: continue
        for rk, it in P.items():
            gx = X["items"][rk]["japanese_gloss"]; gy = Y["items"][rk]["japanese_gloss"]
            if norm(gx) == norm(gy): continue
            flip = rnd.random() < 0.5
            first, second = (gy, gx) if flip else (gx, gy)
            key = f"{label}-{tag}-{rk}"
            rows.append({"id": key, "key_phrase": it["key_phrase"], "source_sentence": it["source_sentence"][:110], "P": first, "Q": second})
            mapping[key] = {"P": (armY, repY) if flip else (armX, repX), "Q": (armX, repX) if flip else (armY, repY)}
    return rows, mapping
if __name__ == "__main__" and sys.argv[1] == "blind":
    out = sys.argv[3]
    rows1, m1 = pairs_blind("A", 1, "B3", 1, 20261031, "AB3")
    rows2, m2 = pairs_blind("A", 1, "A", 2, 20261032, "AA")
    json.dump(rows1 + rows2, open(f"{out}/blind_sheet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({**m1, **m2}, open(f"{out}/blind_mapping.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(rows1), "A-vs-B3 differing;", len(rows2), "A1-vs-A2 differing")

if __name__ == "__main__" and sys.argv[1] == "blind2":
    out = sys.argv[3]
    rows, m = pairs_blind("A", 2, "B3", 2, 20261033, "AB3r2")
    # untidiness はA/B3とも rep2 が存在。他4記事は A r2 / B3 r2 が存在
    json.dump(rows, open(f"{out}/blind_sheet2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(m, open(f"{out}/blind_mapping2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(rows), "A2-vs-B3r2 differing")

if __name__ == "__main__" and sys.argv[1] == "blindho":
    out = sys.argv[3]
    rows, m = pairs_blind("A", 1, "B3", 1, 20261034, "HO")
    json.dump(rows, open(f"{out}/blind_sheet_ho.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(m, open(f"{out}/blind_mapping_ho.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n_all = sum(len(items_of_prompt(t)) for t in TAGS)
    print(len(rows), "differing of", n_all)
