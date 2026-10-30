# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpg01_judge as J, kpg01_manual as M
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ["untidi_a2","untidi_b1b","ai_cha_a2","ai_cha_b1b","jwst_m_a2","jwst_m_b1b","meta_w_a2","meta_w_b1b","aiisland_b1b","surname_b1b","melos_a2","ignobel_a2","ignobel_b1b","tesla_b1b"]
GROUP = {"untidi_a2":"REQ","untidi_b1b":"REQ","ai_cha_a2":"REQ","ai_cha_b1b":"REQ","jwst_m_a2":"REQ","jwst_m_b1b":"REQ","meta_w_a2":"REQ","meta_w_b1b":"REQ","aiisland_b1b":"GEN","surname_b1b":"GEN","melos_a2":"GEN","ignobel_a2":"UNUSED","ignobel_b1b":"UNUSED","tesla_b1b":"UNUSED"}
def rows(cid):
    srcs = J.collect(cid)
    jp = os.path.join(J.JD, cid + ".json"); jm = {}
    if os.path.exists(jp):
        for m, rr in json.load(open(jp, encoding="utf-8"))["by_method"].items():
            for r in rr: jm[(m, r["disp"], r["span"])] = r["j"]
    out = {}
    for m in ("Before", "A_luna", "D_luna"):
        lst = []
        for r in srcs.get(m, []):
            ng = M.NG.get(cid, {}).get(m, {}).get(r["disp"])
            low = r["disp"] in M.LOW.get(cid, {}).get(m, [])
            j = jm.get((m, r["disp"], r["span"]))
            lst.append(dict(r, ok=ng is None, reason=ng, low=low, judge=j))
        out[m] = lst
    return out
def cost(cid, m):
    p = os.path.join(HERE, "kpg01_work", "results", f"{cid}__{m}.json")
    if not os.path.exists(p): return None
    r = json.load(open(p, encoding="utf-8")); return r["cost_jpy"], r["sec"]
if __name__ == "__main__":
    tot = {m: [0, 0, 0] for m in ("Before", "A_luna", "D_luna")}
    print("case | " + " | ".join(f"{m}(ok/n)" for m in ("Before","A_luna","D_luna")) + " | A¥ D¥ | judge-agree")
    agg = {}
    for cid in CASES:
        rs = rows(cid); line = [cid]
        for m in ("Before", "A_luna", "D_luna"):
            n = len(rs[m]); k = sum(1 for r in rs[m] if r["ok"])
            line.append(f"{k}/{n}" if n else "-")
            g = GROUP[cid]
            a = agg.setdefault((g, m), [0, 0, 0]); a[0] += k; a[1] += n; a[2] += 1 if n else 0
            if n: tot[m][0] += k; tot[m][1] += n; tot[m][2] += 1
        ca, cd = cost(cid, "A_luna"), cost(cid, "D_luna")
        agree = []
        for m in ("A_luna", "D_luna", "Before"):
            for r in rs[m]:
                if r["judge"]: agree.append(bool(r["judge"]["selectable"]) == r["ok"])
        print(" | ".join(line), "|", ca and ca[0], cd and cd[0], "|", f"{sum(agree)}/{len(agree)}" if agree else "-")
    print("TOTAL", {m: f"{v[0]}/{v[1]} in {v[2]} cases" for m, v in tot.items()})
    for k, v in sorted(agg.items()): print(k, f"{v[0]}/{v[1]}", "cases", v[2])
    # cost per case mean
    for m in ("A_luna", "D_luna"):
        cs = [cost(c, m)[0] for c in CASES if cost(c, m)]; ts = [cost(c, m)[1] for c in CASES if cost(c, m)]
        print(m, "mean ¥/case", round(sum(cs)/len(cs), 3), "mean sec", round(sum(ts)/len(ts), 1), "n", len(cs))
