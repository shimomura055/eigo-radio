# -*- coding: utf-8 -*-
import json, os, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpg01_judge as J
CASES = sys.argv[1:]
for cid in CASES:
    jp = os.path.join(J.JD, cid + ".json")
    srcs = J.collect(cid)
    jm = {}
    if os.path.exists(jp):
        for m, rows in json.load(open(jp, encoding="utf-8"))["by_method"].items():
            for r in rows: jm[(m, r["disp"], r["span"])] = r["j"]
    print("###", cid)
    for m in ("Before", "A_luna", "D_luna"):
        for r in srcs.get(m, []):
            j = jm.get((m, r["disp"], r["span"])) or {}
            print(f"  {m:7s}| {r['disp']:30s} | {r['gloss']:26s} | <- {r['span']:34s}| {j.get('code','-')}{'*' if j.get('selectable') else ''}")
