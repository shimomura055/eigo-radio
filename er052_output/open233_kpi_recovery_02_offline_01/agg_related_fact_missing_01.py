# -*- coding: utf-8 -*-
# 委任_08 rep29a後の¥0分析: BLOCKING claim(stage2_results)の related_fact_id 欠落率(AG1-strictのfail-closed頻度に直結。Opus#13「十分に答えられなかった点」)。
import json, glob, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
tot = miss = 0; by = collections.Counter(); rows = []
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json")):
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    for c in d.get("cycles") or []:
        for sr in c.get("stage2_results") or []:
            if sr.get("materiality") != "BLOCKING": continue
            tot += 1
            fid = (sr.get("related_fact_id") or "").strip()
            if not fid:
                miss += 1; by[(d.get("instance_id"))] += 1
                rows.append({"run": run, "instance": d.get("instance_id"), "cycle": c.get("cycle"), "claim": (sr.get("claim_text") or "")[:120]})
print("BLOCKING claims:", tot, " related_fact_id empty:", miss)
print("by instance:", dict(by))
print("runs:", dict(collections.Counter(r["run"] for r in rows)))
json.dump(rows, open("er052_output/open233_kpi_recovery_02_offline_01/agg_related_fact_missing_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
