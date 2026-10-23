# -*- coding: utf-8 -*-
"""Bertie 必須要件(SC-4: Bertie 3/3)の再構築安定性: 『開いた窓』run_sf_prod_01 のStd+Adv TTS canonical和集合を replicate 0..4 で構築し、Bertie/Vera/Framton が usable(confirmed/declared)になる率。
併せて entry の根拠内訳(det/llm_b_agree/declared)を集計。"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
rows = {i: r for i, r, c in load_hr_rows()}
k, segs, how = group_key_and_segments(rows[118])
seed = json.load(open("er026_seeds/the_open_window/seed.json", encoding="utf-8"))
out = {"reps": []}
for rp in range(5):
    tb = ret.build_entity_table(segs, llm=cached_llm(rp), usage_log=USAGE_LOG, tag="bertie#%d" % rp)
    d = {e.surface: (e.grade, e.sources) for e in tb.entries}
    out["reps"].append({"rep": rp, "status": tb.status, "entries": {s: v[0] for s, v in d.items()}, "bertie_sources": d.get("Bertie", (None, None))[1], "usage": tb.meta["usage"]})
    print(rp, tb.status, {s: v[0] for s, v in d.items()}, d.get("Bertie", (None, None))[1])
out["bertie_usable_rate"] = sum(1 for r in out["reps"] if r["entries"].get("Bertie") in ("confirmed", "declared")) / 5
json.dump(out, open(os.path.join(HERE, "bertie_stability_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("Bertie usable rate", out["bertie_usable_rate"], "spend", ret.spend_so_far(USAGE_LOG))
