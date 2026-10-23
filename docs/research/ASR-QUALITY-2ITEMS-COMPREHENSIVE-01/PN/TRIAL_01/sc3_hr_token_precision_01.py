# -*- coding: utf-8 -*-
"""SC-3 補強: HR群(audit和集合30群)の全segment・全tokenを総当たりし、表が証拠を付与する token の一覧(人手adjudication用)を出す。API 0。"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
tabs = {k: ret.EntityTable.from_dict(v) for k, v in json.load(open(os.path.join(HERE, "entity_tables_hr_01.json"), encoding="utf-8")).items()}
rows = [(i, r) for i, r, c in load_hr_rows() if not c]
granted = collections.defaultdict(set)
n_tok = 0
for i, r in rows:
    k, segs, how = group_key_and_segments(r)
    if segs is None:
        segs = [ret.Seg(text=r["canonical_text"])]
    tb = tabs[k]
    for s in segs:
        for w in ret.words(s.text):
            n_tok += 1
            gr, info = tb.grant_for_phrase(s.text, [w.fold])
            if gr:
                granted[w.fold].add(tuple(sorted(e["surface"] for e in info["entities"])))
res = {"tokens_scanned": n_tok, "granted_unique_tokens": len(granted), "granted": {t: sorted(map(list, v)) for t, v in sorted(granted.items())}}
json.dump(res, open(os.path.join(HERE, "sc3_hr_token_precision_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(granted), sorted(granted))
