# -*- coding: utf-8 -*-
"""SC-9 安定性: 同一textを3回構築(replicate 0,1,2。cacheのkeyにreplicateを含めるため再callされる)し、confirmed(usable)entry集合の Jaccard、
および『3回の和集合でも非固有名詞へ証拠付与0』を測る。D3(entry数の多い10本)+D4合成16段落+『開いた窓』。"""
import sys, os, json, re, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
from synthetic_corpus_01 import P
SPLIT = re.compile(r"(?<!Mrs\.)(?<!Mr\.)(?<!Dr\.)(?<!St\.)(?<![A-Z]\.)(?<=[.!?])\s+")
d3 = json.load(open(os.path.join(HERE, "entity_tables_d3_01.json"), encoding="utf-8"))
top = sorted(d3, key=lambda f: -sum(1 for e in d3[f]["entries"] if e["grade"] in ("confirmed", "declared") and e["eligible"]))[:10]
jobs = [(f, load_segments(f)) for f in top] + [("synthetic:" + p["id"], [ret.Seg(s) for s in SPLIT.split(p["text"].strip()) if s]) for p in P]
gold_d3 = json.load(open(os.path.join(HERE, "d3_gold_01.json"), encoding="utf-8"))
gold_d3_set = {tuple(w.fold for w in ret.words(s)) for s in gold_d3["true_entities"]}
reps = [0, 1, 2]
out = []
nongold = []
for name, segs in jobs:
    sets = []
    tabs = []
    for rp in reps:
        tb = ret.build_entity_table(segs, llm=cached_llm(rp), usage_log=USAGE_LOG, tag="%s#rep%d" % (name, rp))
        tabs.append(tb)
        sets.append({tuple(e.words) for e in tb.usable_entries()})
    jac = []
    for a, b in itertools.combinations(sets, 2):
        u = a | b
        jac.append(1.0 if not u else len(a & b) / len(u))
    # 運用上の意味を持つ「証拠を付与されるtoken集合」(usable entryのeligible/initial token)のJaccard
    tsets = [{t for e in tb.usable_entries() for t in (list(e.eligible) + list(e.initials))} for tb in tabs]
    tjac = []
    for a, b in itertools.combinations(tsets, 2):
        u = a | b
        tjac.append(1.0 if not u else len(a & b) / len(u))
    union = set().union(*sets)
    # 和集合の非固有名詞付与: 合成はgold(paragraph)で、D3はd3 goldで判定
    if name.startswith("synthetic:"):
        para = next(p for p in P if p["id"] == name.split(":")[1])
        g = {w.fold for gg in para["gold"] for w in ret.words(gg["surface"])}
        bad = [u for u in union if not (set(u) & g)]
    else:
        bad = [u for u in union if u not in gold_d3_set]
    out.append({"text": name, "n_confirmed_per_rep": [len(s) for s in sets], "jaccard_pairs": [round(j, 3) for j in jac], "jaccard_min": round(min(jac), 3), "token_jaccard_pairs": [round(j, 3) for j in tjac], "token_jaccard_min": round(min(tjac), 3),
                "token_union_size": len(set().union(*tsets)),
                "union_size": len(union), "union_non_proper": [" ".join(b) for b in bad], "statuses": [t.status for t in tabs]})
    print(name, [len(s) for s in sets], round(min(jac), 3), bad)
res = {"texts": len(out), "mean_min_jaccard": round(sum(o["jaccard_min"] for o in out) / len(out), 4), "min_jaccard": min(o["jaccard_min"] for o in out),
       "texts_below_0.90": [o["text"] for o in out if o["jaccard_min"] < 0.90],
       "token_level": {"mean_min_jaccard": round(sum(o["token_jaccard_min"] for o in out) / len(out), 4), "min_jaccard": min(o["token_jaccard_min"] for o in out),
                       "texts_below_0.90": [o["text"] for o in out if o["token_jaccard_min"] < 0.90]},
       "union_non_proper_total": sum(len(o["union_non_proper"]) for o in out), "detail": out}
json.dump(res, open(os.path.join(HERE, "sc9_stability_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("mean_min_jaccard", res["mean_min_jaccard"], "min", res["min_jaccard"], "below", res["texts_below_0.90"], "union_non_proper", res["union_non_proper_total"], "spend", ret.spend_so_far(USAGE_LOG))
