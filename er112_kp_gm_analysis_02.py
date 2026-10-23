# -*- coding: utf-8 -*-
"""委任_07: 解析(API 0)。Judge一致/kappa、自己一致、KP単位flip(McNemar型)。"""
import json, sys, itertools, math, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_report_02 as R
import er112_kp_gm_judge_01 as jd
import er112_kp_gm_trial_02 as T


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa = sum(a) / n; pb = sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def judge_agreement():
    V = R.verdicts(["sonnet", "sol"])
    seen = {}
    for kk, (kind, vs, rid) in V.items():
        seen[rid] = (kind, vs)
    for kind in ("E3", "G"):
        rows = [vs for kd, vs in seen.values() if kd == kind]
        if not rows:
            continue
        print(f"-- {kind} 2系統Judge重複行 n={len(rows)}")
        for f in jd.FIELDS[kind]:
            a = [r["sonnet"][f] for r in rows]; b = [r["sol"][f] for r in rows]
            agree = sum(1 for x, y in zip(a, b) if x == y)
            k = kappa(a, b)
            print(f"   {f:12s} 一致 {agree}/{len(rows)} kappa={'n/a' if k is None else '%.2f' % k}  (悪側 sonnet={sum(1 for x in a if x!=jd.GOOD[f])} sol={sum(1 for x in b if x!=jd.GOOD[f])})")
        tot = [(jd.verdict_ok(kind, r["sonnet"]), jd.verdict_ok(kind, r["sol"])) for r in rows]
        k = kappa([int(x) for x, _ in tot], [int(y) for _, y in tot])
        print(f"   総合PASS 一致 {sum(1 for x,y in tot if x==y)}/{len(tot)} kappa={'n/a' if k is None else '%.2f'%k}")
    return seen


def self_agreement(V, arm, keys, reps=(1, 2, 3)):
    """同arm・同KPの3rep判定(総合PASS)が全て一致する割合。"""
    n = ag = 0
    for k in keys:
        vals = []
        for r in reps:
            x = V.get((arm, k, r))
            if x:
                vals.append(jd.verdict_ok(x[0], x[1]["sonnet"]))
        if len(vals) == len(reps):
            n += 1
            ag += 1 if len(set(vals)) == 1 else 0
    return ag, n


def flips(V, armA, armB, keys, rep=1):
    """KP単位: A->Bで 改善(NG->OK)/悪化(OK->NG)/不変。"""
    imp = wor = same = 0
    for k in keys:
        a = V.get((armA, k, rep)); b = V.get((armB, k, rep))
        if not a or not b:
            continue
        pa = jd.verdict_ok(a[0], a[1]["sonnet"]); pb = jd.verdict_ok(b[0], b[1]["sonnet"])
        if pa == pb:
            same += 1
        elif pb:
            imp += 1
        else:
            wor += 1
    return imp, wor, same


if __name__ == "__main__":
    judge_agreement()
    V = R.verdicts(["sonnet"])
    A = T.kpset()
    hard = [k for k, v in A.items() if v["tier"] == "hard"]
    normal = [k for k, v in A.items() if v["tier"] == "normal"]
    print("\n-- 自己一致(hard20、3rep、総合PASSが3回とも同じ)")
    for arm in ("E0@G0", "E1"):
        print("  ", arm, self_agreement(V, arm, hard))
    print("\n-- 3rep平均PASS率(hard20)")
    for arm in ("E0@G0", "E1"):
        v = [jd.verdict_ok(V[(arm, k, r)][0], V[(arm, k, r)][1]["sonnet"]) for k in hard for r in (1, 2, 3) if (arm, k, r) in V]
        print("  ", arm, sum(v), "/", len(v))
    print("\n-- KP単位flip(rep1。改善/悪化/不変)")
    for a, b, ks, nm in (("E0@G0", "E1", hard, "hard"), ("E0@G0", "E1c", hard, "hard"), ("E0@G0", "E4", hard, "hard"), ("E0@prod", "E1", normal, "normal"), ("E0@prod", "E1c", normal, "normal"),
                         ("E1", "E1c", hard + normal, "all"), ("E1", "E4", hard, "hard"), ("E0@G0", "E0@G2", hard, "hard(std6除く)"), ("E0@G0", "E0@G3", hard, "hard")):
        print(f"   {a:8s}->{b:8s} {nm:12s}", flips(V, a, b, ks))
