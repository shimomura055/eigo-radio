# probe-03b: 同一KP(draw a line)・同一1文に、JA参考意味だけを変えて説明を各4回生成(H1の直接因果検証。費用<0.5円)
import sys, json, os, concurrent.futures as cf
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\tensh\eigo-radio\docs\research\FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01")
import kp_probe_03 as P
P.client = P.b1s.get_client()
kps, miss = P.load_kps()
out = {}
for key, variants in (("draw a line", ["(none)", "線を引く", "一線を引く", "境界線を引く", "区別をはっきりさせる"]),
                      ("Carry the Load", ["(none)", "荷物を運ぶ", "重い負担を引き受ける"])):
    kp = kps[key]
    def job(args):
        g, i = args
        if P.total() >= P.CAP: return (g, i, "SKIP")
        t, c, u, m = P.expl_call("E1" if g == "(none)" else "E0", kp, i, g if g != "(none)" else "x", None)
        P.log_cost(dict(kind="expl_3b", key=key, gloss=g, rep=i, usage=u, cost_jpy=round(c, 5)))
        return (g, i, t)
    with cf.ThreadPoolExecutor(6) as ex:
        res = list(ex.map(job, [(g, i) for g in variants for i in range(1, 5)]))
    out[key] = res
    print("##", key, "|", kp["sent"])
    for g in variants:
        print("  [gloss=%s]" % g)
        for (gg, i, t) in res:
            if gg == g: print("     ", t)
json.dump(out, open(r"C:\Users\tensh\eigo-radio\docs\research\FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01\kp_probe_03b_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cum", round(P.total(), 3))
