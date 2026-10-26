# -*- coding: utf-8 -*-
"""[事後・探索] 『複数take生成→停止計測で最良を選ぶ』選別方式の効果を、実測のmain rawサンプル分布からの復元抽出で見積もる(API 0)。
選別基準(仮): >=1000ms停止の個数が少ない→最長停止が短い の順。k take生成して最良を採用した場合の E[>=1s個数]・P(>=1s停止が残る)・E[最長ms]。
注意: (1)サンプルは同一takeのattemptを独立とみなす近似 (2)選別は新仕様(ユーザー判断)で、ここは見積りのみ (3)Voice×本文ごとの標本が小さいセルはプールして使う。"""
import json, random, sys

T = "docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01"
rows = json.load(open(f"{T}/measure/samples_measured.json", encoding="utf-8"))
rnd = random.Random(20261026)
out = {}


def sim(pool, k, n=20000):
    ge, anyl, mx = 0.0, 0, 0.0
    for _ in range(n):
        pick = min((rnd.choice(pool) for _ in range(k)), key=lambda r: (r["ge1000"], r["max_ms"]))
        ge += pick["ge1000"]
        anyl += 1 if pick["ge1000"] >= 1 else 0
        mx += pick["max_ms"]
    return {"E_ge1000": round(ge / n, 3), "P_has_ge1s": round(anyl / n, 3), "E_max_ms": round(mx / n)}


for lv in ("a2", "b1b"):
    for label, flt in (("V1(全本文)", lambda r: r["voice"] == 1), ("V2(全本文)", lambda r: r["voice"] == 2), ("V3(全本文)", lambda r: r["voice"] == 3)):
        pool = [r for r in rows if r["level"] == lv and r["kind"] == "main" and flt(r)]
        out[f"{lv}|{label}"] = {"n": len(pool), **{f"k{k}": sim(pool, k) for k in (1, 2, 3, 4)}}
json.dump(out, open(f"{T}/measure/selection_sim.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, "n=", v["n"], " ".join(f"k{i}: ge1s={v[f'k{i}']['E_ge1000']} P={v[f'k{i}']['P_has_ge1s']} max={v[f'k{i}']['E_max_ms']}" for i in (1, 2, 3, 4)))
