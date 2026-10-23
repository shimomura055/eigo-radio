# -*- coding: utf-8 -*-
"""D3(保存X記事19+Z脚本2+『開いた窓』実TTS segment)に対し 実体表を構築(gpt-6-luna、call A + 必要時 call B)。結果を entity_tables_d3_01.json に保存。"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
out = {}
llm = cached_llm(0)
t0 = time.time()
for f in d3_files():
    segs = load_segments(f)
    t1 = time.time()
    tb = ret.build_entity_table(segs, llm=llm, usage_log=USAGE_LOG, tag=f)
    out[f] = {**tb.to_dict(), "sec": round(time.time() - t1, 2), "n_segs": len(segs)}
    print(f, tb.status, len(tb.entries), [(e.surface, e.category, e.grade) for e in tb.entries][:30])
json.dump(out, open(os.path.join(HERE, "entity_tables_d3_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total sec", round(time.time() - t0, 1), "spend", ret.spend_so_far(USAGE_LOG))
