# -*- coding: utf-8 -*-
"""委任_08: key開封後の詳細表(Sonnet参考値付き)。sonnet_reference_03_detail.md を出力。API 0。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_trial_03 as X

A = X.kpall()
res = X.load_res()
cache = X.judge_cache()


def lab(arm, k, rep):
    r = res.get((arm, k, rep))
    if not r or not r.get("gloss"):
        return "-", "(なし)"
    v = cache.get("S_" + X._jrid(k, r["sent"], r["gloss"]))
    return (v["verdict"]["v"] if v else "?"), r["gloss"]


L = ["# sonnet_reference_03_detail (key開封後。Sonnet参考値: P/T/F。最終判定はFable盲検)\n",
     "| tier/型 | key | G0 rep1 | G0 rep2 | G2 rep1 | G2 rep2 | G3 rep1 | G3 rep2 |", "|---|---|---|---|---|---|---|---|"]
for k in sorted(A, key=lambda k: (A[k]["tier"] != "hard", k)):
    cells = []
    for arm in X.ARMS:
        for rep in (1, 2):
            l, g = lab(arm, k, rep)
            cells.append("%s %s" % (l, g.replace("|", "/")))
    L.append("| %s/%s | %s | %s |" % (A[k]["tier"], A[k].get("type", "-"), A[k]["key"], " | ".join(cells)))
open(X.OUT / "sonnet_reference_03_detail.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
