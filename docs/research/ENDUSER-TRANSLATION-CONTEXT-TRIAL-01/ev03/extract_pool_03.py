# ③(b) 母集団抽出(手順固定): 公開済みEnd Userページ(user_test/*/enduser/data/article.json)の ja_source==generated の全文を列挙する。
import json, glob, os, sys
rows = []
for f in sorted(glob.glob("user_test/*/enduser/data/article.json")):
    a = json.load(open(f, encoding="utf-8")); d = os.path.normpath(f).split(os.sep)[1]
    for lv, L in a["levels"].items():
        for p in L["parts"]:
            if p.get("ja_source") != "generated": continue
            ja = p["ja"]; k = 0
            for pi, pa in enumerate(p["paragraphs"]):
                # ja[pi]は段落内の文の訳の連結。ja_alignのオフセットで文ごとに切る
                grp = {g["sids"][0]: g["ja"] for g in p["ja_align"]}
                for s in pa:
                    _, b, e = grp[s["sid"]]
                    u = ja[pi].encode("utf-16-le")
                    rows.append({"dir": d, "family": a["family"], "level": lv, "part": p["key"], "kind": p["kind"], "sid": s["sid"], "para": pi,
                                 "en": s["text"], "ja": u[2*b:2*e].decode("utf-16-le")})
for i, r in enumerate(rows): r["n"] = i
json.dump(rows, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
import collections
print(len(rows), collections.Counter((r["family"], r["level"], r["kind"]) for r in rows))
