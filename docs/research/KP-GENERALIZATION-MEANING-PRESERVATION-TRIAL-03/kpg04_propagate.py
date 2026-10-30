# -*- coding: utf-8 -*-
"""N2で付けた実読ラベルを、同一ケース・同一表示形・同一訳のitemを持つ派生arm(N4/N4d/N5/N5d)へ複製する(API 0)。訳が異なるitemは複製せず『要実読』として列挙する。"""
import sys, json
sys.path.insert(0, ".")
import kpg04_stats as S, kpg04_run as R
from kpg04_label import add, judged
import argparse
ap = argparse.ArgumentParser(); ap.add_argument("--cases", default="ALL14"); ap.add_argument("--src", default="N2"); ap.add_argument("--dst", default="N4,N4d,N5,N5d")
a = ap.parse_args()
cases = {"ALL14": R.ALL14, "HELDOUT": R.HELDOUT}.get(a.cases) or a.cases.split(",")
todo = []
for cid in cases:
    src = S.items_of(a.src, cid)
    if src is None:
        continue
    smap = {S.nkey(i["display_form"]): i for i in src}
    for arm in a.dst.split(","):
        its = S.items_of(arm, cid)
        if its is None:
            continue
        judged([arm], [cid])
        for it in its:
            s = smap.get(S.nkey(it["display_form"]))
            lab = S.NEW.get((a.src, cid, S.nkey(it["display_form"])))
            if s and (s["gloss_ja"] or "").strip() == (it["gloss_ja"] or "").strip():
                if lab:
                    add([arm], cid, lab["display_form"], lab["code"], lab["level"], lab["reason"])
            else:
                todo.append((arm, cid, it["source_span"], it["display_form"], it["gloss_ja"], "R" if it.get("reverted") else ""))
for t in todo:
    print("要実読:", *t)
print("要実読", len(todo))
