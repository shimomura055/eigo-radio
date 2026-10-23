# -*- coding: utf-8 -*-
"""アブレーション(API 0): HR queue 88実イベント(Ledger全除外/現行Ledger)で、RET-2(証拠源)のみ / RET-2+RET-3 / 参考: 原本 の受理数・原因別。"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
tabs = {k: ret.EntityTable.from_dict(v) for k, v in json.load(open(os.path.join(HERE, "entity_tables_hr_01.json"), encoding="utf-8")).items()}
rows = [(i, r) for i, r, c in load_hr_rows() if not c]
out = {}
for lm in ("excl", "cur"):
    led = ledger_tokens(lm == "excl")
    c = collections.defaultdict(list)
    for i, r in rows:
        kw = inputs_for(r)
        if kw is None:
            continue
        k, segs, how = group_key_and_segments(r)
        tb = tabs[k]
        c["orig"].append(run_orig(kw, led).accept)
        c["RET2_only"].append(run_trial(kw, led, tb, ret3=False).accept)
        c["RET2+RET3"].append(run_trial(kw, led, tb, ret3=True).accept)
    out[lm] = {k: sum(v) for k, v in c.items()}
out["n_events"] = len(rows)
json.dump(out, open(os.path.join(HERE, "ablation_01_result.json"), "w", encoding="utf-8"), indent=1)
print(out)
