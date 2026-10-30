# -*- coding: utf-8 -*-
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpg01_stats as S1, kpg01_judge as J1, kpg01_manual as M1, kpg02_manual as M2
HERE = os.path.dirname(os.path.abspath(__file__))
RES2 = os.path.join(HERE, "kpg02_work", "results"); JD2 = os.path.join(HERE, "kpg02_work", "judge")
CASES = ["untidi_a2", "untidi_b1b", "ai_cha_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_a2", "meta_w_b1b"]
def load(cid, m="D2_luna"):
    p = os.path.join(RES2, f"{cid}__{m}.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
def d2rows(cid):
    r = load(cid)
    if not r: return None
    jp = os.path.join(JD2, f"{cid}__D2_luna.json"); jm = {}
    if os.path.exists(jp):
        for x in json.load(open(jp, encoding="utf-8"))["rows"]: jm[(x["track"], x["display_form"])] = x["j"]
    out = {"main": [], "alt": []}
    for t, key in (("main", "items"), ("alt", "alt_items")):
        for i in r[key]:
            ng = M2.NG.get(cid, {}).get(i["display_form"])
            out[t].append(dict(disp=i["display_form"], span=i["source_span"], gloss=i["gloss_ja"], ok=ng is None, reason=ng, low=i["display_form"] in M2.LOW.get(cid, []),
                               judge=jm.get((t, i["display_form"])), votes=i.get("sel_votes"), reverted=i.get("reverted"), guard=i.get("guard_restored"), track=t, sense=i.get("sense_note_ja")))
    return out
if __name__ == "__main__":
    tot = {"Before": [0, 0, 0], "A_luna": [0, 0, 0], "D_luna": [0, 0, 0], "D2": [0, 0, 0]}
    lv = {}
    jag = [0, 0]
    for cid in CASES:
        rs = S1.rows(cid); d2 = d2rows(cid)
        line = [cid]
        for m in ("Before", "A_luna", "D_luna"):
            n = len(rs[m]); k = sum(1 for r in rs[m] if r["ok"]); line.append(f"{k}/{n}")
            tot[m][0] += k; tot[m][1] += n; tot[m][2] += k >= 3
            lv.setdefault((m, cid.split("_")[-1]), [0, 0]); lv[(m, cid.split("_")[-1])][0] += k; lv[(m, cid.split("_")[-1])][1] += n
        n = len(d2["main"]); k = sum(1 for r in d2["main"] if r["ok"]); line.append(f"{k}/{n} (+alt {len(d2['alt'])})")
        tot["D2"][0] += k; tot["D2"][1] += n; tot["D2"][2] += k >= 3
        lv.setdefault(("D2", cid.split("_")[-1]), [0, 0]); lv[("D2", cid.split("_")[-1])][0] += k; lv[("D2", cid.split("_")[-1])][1] += n
        for r in d2["main"] + d2["alt"]:
            if r["judge"]:
                jag[1] += 1; jag[0] += bool(r["judge"]["selectable"]) == r["ok"]
        print(" | ".join(line))
    print("TOTAL ok/n, >=3cases:", {m: v for m, v in tot.items()})
    print("by level (a2=Std, b1b=Adv):", {f"{m}/{l}": f"{v[0]}/{v[1]}" for (m, l), v in sorted(lv.items())})
    print("gemini judge agreement with Sonnet (D' main+alt):", jag)
    # judge: gemini selectable counts
    gs = [0, 0]
    for cid in CASES:
        for r in d2rows(cid)["main"]:
            if r["judge"]: gs[1] += 1; gs[0] += bool(r["judge"]["selectable"])
    print("gemini selectable (main):", gs)
    # votes policy: items by sel_votes
    byv = {}
    for cid in CASES:
        for r in d2rows(cid)["main"]:
            v = r["votes"]; a = byv.setdefault(v, [0, 0]); a[0] += r["ok"]; a[1] += 1
    print("precision by sel_votes (2=both passes C-keep, 1=union only):", byv)
    # Before成功例の脱落
    drop = []
    for cid in CASES:
        rs = S1.rows(cid)
        d2f = " ".join(r["span"].lower() + "|" + r["disp"].lower() for r in d2rows(cid)["main"])
        for r in rs["Before"]:
            if r["ok"]:
                core = re.sub(r"^(the|a|an) ", "", r["span"].lower().strip())
                if core not in d2f and r["disp"].lower() not in d2f: drop.append((cid, r["disp"]))
    print("Before OK dropped in D':", drop, "of", sum(1 for cid in CASES for r in S1.rows(cid)["Before"] if r["ok"]))
    print("alt:", [(cid, r["disp"], r["ok"]) for cid in CASES for r in d2rows(cid)["alt"]])
    cost = [load(c)["cost_jpy"] for c in CASES]; sec = [load(c)["sec"] for c in CASES]
    print("D' cost/level mean", round(sum(cost) / len(cost), 3), "sec", round(sum(sec) / len(sec), 1))
