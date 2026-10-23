# -*- coding: utf-8 -*-
"""委任_07 Trial: 集計(DEV専用、API 0)。arm別PASS率、KP単位flip、Wilson CI、自己一致率。"""
import json, sys, math, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_judge_01 as jd
import er112_kp_gm_trial_02 as T
jd.configure_out(T.OUT)
RM = json.load(open(T.OUT / "row_map_02.json", encoding="utf-8"))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def verdicts(judges):
    caches = {j: jd.load_cache(j) for j in judges}
    out = {}   # (arm,key,rep) -> (kind, {judge: verdict}, row id)
    for rid_, refs in RM.items():
        vs = {j: caches[j].get(rid_) for j in judges}
        if any(v is None for v in vs.values()):
            continue
        kind = list(vs.values())[0]["kind"]
        for a, k, r in refs:
            out[(a, k, r)] = (kind, {j: v["verdict"] for j, v in vs.items()}, rid_)
    return out


def ok(kind, v):
    return jd.verdict_ok(kind, v)


def agg(V, arms_keys, judges, field=None, require="all"):
    n = g = 0
    for (a, k, r), (kind, vs, _) in V.items():
        if (a, k) not in arms_keys:
            continue
        n += 1
        f = [ok(kind, v) if field is None else (v[field] == jd.GOOD[field]) for v in vs.values()]
        g += 1 if (all(f) if require == "all" else f[0]) else 0
    return g, n


if __name__ == "__main__":
    judges = sys.argv[1].split(",") if len(sys.argv) > 1 else ["sonnet"]
    V = verdicts(judges)
    A = T.kpset()
    hard = {k for k, v in A.items() if v["tier"] == "hard"}
    arms = sorted({a for (a, k, r) in V})
    print("== arm x tier (Sonnet基準=%s): PASS / sense_ok / core / single / over_general (rep1のみ: E, Gは全rep)" % judges)
    for tier, keys in (("hard", hard), ("normal", set(A) - hard), ("all", set(A))):
        for a in arms:
            ks = {(a, k) for k in keys}
            sel = [(kk, v) for kk, v in V.items() if kk[0] == a and kk[1] in keys and kk[2] == 1]
            if not sel:
                continue
            kind = sel[0][1][0]
            n = len(sel)
            pas = sum(1 for _, (kd, vs, _) in sel if all(ok(kd, v) for v in vs.values()))
            fl = jd.FIELDS[kind]
            det = " ".join("%s=%d" % (f, sum(1 for _, (kd, vs, _) in sel if all(v[f] == jd.GOOD[f] for v in vs.values()))) for f in fl)
            lo, hi = wilson(pas, n)
            print(f"{tier:6s} {a:8s} n={n:3d} PASS={pas:3d} ({100*pas/n:3.0f}% CI {100*lo:.0f}-{100*hi:.0f}) | {det}")
