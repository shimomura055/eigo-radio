# -*- coding: utf-8 -*-
"""新arm出力の実読シート(API 0)。ユニークな(case, span, display_form, gloss)を列挙し、旧arm(D/E1L等)で既に同一項目に付いたラベルを参考表示する。
使い方: python kpg04_sheet.py --arms N1a,N1,N2 --cases HARD6 [--unlabeled]"""
import os, sys, json, argparse, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_stats as S
import kpg04_run as R

ap = argparse.ArgumentParser()
ap.add_argument("--arms", default="N1a,N1,N2"); ap.add_argument("--cases", default="ALL14"); ap.add_argument("--unlabeled", action="store_true")
a = ap.parse_args()
cases = {"ALL14": R.ALL14, "HELDOUT": R.HELDOUT, "HARD6": R.HARD6}.get(a.cases) or a.cases.split(",")
U = collections.OrderedDict()
for cid in cases:
    for arm in a.arms.split(","):
        its = S.items_of(arm, cid)
        if its is None:
            continue
        for it in its:
            k = (cid, S.nkey(it["source_span"]), S.nkey(it["display_form"]), (it["gloss_ja"] or "").strip())
            U.setdefault(k, dict(arms=[], rev=False, flags=set(), sent=it.get("source_sentence", ""), form=it["display_form"], span=it["source_span"], gloss=it["gloss_ja"]))
            U[k]["arms"].append(arm); U[k]["rev"] |= bool(it.get("reverted")); U[k]["flags"] |= set(it.get("flags") or [])
n = 0
for k, v in U.items():
    lab = S.NEW.get((v["arms"][0], k[0], k[2]))
    if a.unlabeled and all(S.NEW.get((arm, k[0], k[2])) for arm in v["arms"]):
        continue
    n += 1
    print(f"{k[0]} | {v['span']} => {v['form']} | {v['gloss']} | {','.join(sorted(set(v['arms'])))}{' R' if v['rev'] else ''}")
print("unique", n, "/", len(U))
