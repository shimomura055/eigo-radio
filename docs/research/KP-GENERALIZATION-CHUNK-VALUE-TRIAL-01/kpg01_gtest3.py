# -*- coding: utf-8 -*-
"""一般化段(G2+検証)の単体評価: 必須の一般化5例を選定なし(force_keep)で通す。"""
import json, os, sys
import kpg01_llm as L, kpg01_methods3 as M3
from kpg01_gtest import CASES, corpus, sent_of
HERE = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else "g3"
res = []
by_case = {}
for cid, span in CASES:
    by_case.setdefault(cid, []).append({"span": span, "sentence": sent_of(cid, span)})
for cid, cands in by_case.items():
    r = M3.run_D(corpus[cid], source="p7", cands_override=cands, force_keep=True, tag=f"gtest3_{tag}")
    cost = round(sum(s["cost_jpy"] for s in r["log"]["stages"]), 2)
    for it in r["items"]:
        print(f"{it['source_span']:32s} -> {it['display_form']:26s} | {it['gloss_ja']} | pre={it.get('display_form_pre_fix')} | verify={(it['verify'] or {}).get('verdict')}")
    for k in ("validator_dropped", "verify_dropped", "fix_rejected_by_validator", "assemble_failed"):
        if r["log"].get(k): print("  ", k, json.dumps(r["log"][k], ensure_ascii=False))
    print("  cost", cost)
    res.append({"case": cid, "items": r["items"], "log": r["log"], "cost": cost})
json.dump(res, open(os.path.join(HERE, "kpg01_work", f"gtest3_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
