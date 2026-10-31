"""Trial専用(API 0)。ev02の全rep fileから、フェーズ別・アーム別の集計表(markdown)と費用・N7を作る。usage: python n5r_summary_02.py"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
PH = {"P1": [("untidi_b1b", 1, 5), ("untidi_a2", 1, 3)], "P3": [("untidi_b1b", 6, 9), ("untidi_a2", 4, 7)], "P3b": [("untidi_b1b", 10, 13), ("untidi_a2", 8, 11)],
      "held-out": [("surname_b1b", 1, 2), ("moon_b1b", 1, 2), ("melos_a2", 1, 2)]}
rows = {}
metas = []
for f in sorted(glob.glob(L.EV + "/rep_*.json")):
    r = json.load(open(f, encoding="utf-8"))
    metas += [dict(m, case=r["case"], rep=r["rep"]) for m in r["all_metas"]]
    ph = next(k for k, v in PH.items() for c, a, b in v if c == r["case"] and a <= r["rep"] <= b)
    for arm, pk in r["picks"].items():
        h = L.hits([c["span"] for c in pk])
        d = rows.setdefault((ph, arm), {"n": 0, "pa": 0, "itw": 0, "both": 0, "pool_both": 0})
        d["n"] += 1; d["pa"] += h["put_away"]; d["itw"] += h["in_the_way"]; d["both"] += h["put_away"] and h["in_the_way"]
        pool = {"A0": "A0", "A1": "E1", "A5": "E5", "A6p": "E6"}.get(arm, "E2")
        hp = L.hits([c["span"] for c in r["pools"][pool]["judged"]]); d["pool_both"] += hp["put_away"] and hp["in_the_way"]
out = ["| フェーズ | アーム | 反復 | プールに両表現(S1) | pick: put away | pick: in the way | **pick: 両表現同時(S3必要条件)** |", "|---|---|---|---|---|---|---|"]
for (ph, arm), d in sorted(rows.items(), key=lambda kv: (list(PH).index(kv[0][0]), kv[0][1])):
    if ph == "held-out": continue
    out.append(f"| {ph} | {arm} | {d['n']} | {d['pool_both']}/{d['n']} | {d['pa']}/{d['n']} | {d['itw']}/{d['n']} | **{d['both']}/{d['n']}** |")
tot = len(metas); bad = [m for m in metas if m.get("json_ok") is False or (m.get("attempt") or 1) > 1]
st = {}
for m in metas: st[m["stage"]] = st.get(m["stage"], 0) + 1
bs = {}
for m in bad: bs[m["label"]] = bs.get(m["label"], 0) + 1
out.append(""); out.append(f"N7(rep実行のLLM呼出): 総{tot}呼出、JSON途切れ/再試行{len(bad)}件({100*len(bad)/tot:.1f}%)、内訳{bs}、stage別呼出数{st}")
out.append(f"費用合計(全cost log glob合算): ¥{L.spent():.2f}")
open(L.EV + "/summary_all.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
