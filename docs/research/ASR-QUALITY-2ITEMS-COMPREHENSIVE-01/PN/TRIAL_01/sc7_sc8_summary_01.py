# -*- coding: utf-8 -*-
"""SC-7(費用・時間)/SC-8(横断: Z2作品+X19記事の分布・weak/dropped)/gold出現数/Bertie型件数。API 0(保存結果・usage_logの集計)。"""
import sys, os, json, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
res = {}
# ---- usage log
U = [json.loads(l) for l in open(USAGE_LOG, encoding="utf-8") if l.strip()]
res["usage"] = {"calls": len(U), "total_jpy": round(sum(u["jpy"] for u in U), 4), "mean_jpy": round(statistics.mean(u["jpy"] for u in U), 5),
                "max_jpy": max(u["jpy"] for u in U), "sec_mean": round(statistics.mean(u["sec"] for u in U), 2),
                "sec_p50": round(statistics.median(u["sec"] for u in U), 2),
                "sec_p95": round(sorted(u["sec"] for u in U)[int(len(U) * 0.95) - 1], 2), "sec_max": max(u["sec"] for u in U),
                "in_mean": round(statistics.mean(u["in"] for u in U)), "out_mean": round(statistics.mean(u["out"] for u in U))}
# ---- 記事(Std+Adv union=1 build)あたり: HR群(audit和集合) = 実運用単位に近い
hr = json.load(open(os.path.join(HERE, "entity_tables_hr_01.json"), encoding="utf-8"))
per = []
for k, v in hr.items():
    us = v["meta"].get("usage") or []
    if not us:
        continue
    per.append({"group": k, "calls": len(us), "jpy": round(sum(u["jpy"] for u in us), 5), "sec": round(sum(u["sec"] for u in us), 2), "n_segments": v["meta"]["n_segments"], "in": sum(u["in"] for u in us)})
audit_groups = [p for p in per if p["n_segments"] >= 10]
res["per_article_set_hr_groups"] = {"groups": len(per), "audit_groups_ge10seg": len(audit_groups),
    "jpy_mean": round(statistics.mean(p["jpy"] for p in per), 5), "jpy_max": max(p["jpy"] for p in per),
    "jpy_mean_audit": round(statistics.mean(p["jpy"] for p in audit_groups), 5) if audit_groups else None,
    "jpy_max_audit": max(p["jpy"] for p in audit_groups) if audit_groups else None,
    "sec_mean": round(statistics.mean(p["sec"] for p in per), 2), "sec_max": max(p["sec"] for p in per),
    "calls_mean": round(statistics.mean(p["calls"] for p in per), 2), "calls_max": max(p["calls"] for p in per)}
# ---- 横断: D3
d3 = json.load(open(os.path.join(HERE, "entity_tables_d3_01.json"), encoding="utf-8"))
cat = collections.defaultdict(collections.Counter)
weak, drop, blocked = [], collections.Counter(), []
for f, tb in d3.items():
    for e in tb["entries"]:
        usable = e["grade"] in ("confirmed", "declared") and bool(e["eligible"])
        cat[e["category"]]["usable" if usable else "not_usable"] += 1
        if not usable:
            weak.append({"file": f.split("/")[-4] + "/" + f.split("/")[-3], "surface": e["surface"], "category": e["category"], "grade": e["grade"], "notes": e["notes"]})
    for d in tb["meta"].get("dropped", []):
        drop[d["reason"]] += 1
    blocked += tb["meta"].get("blocked_general_person_place", [])
res["sc8_d3"] = {"tables": len(d3), "by_category": {k: dict(v) for k, v in cat.items()}, "dropped_reasons": dict(drop),
                 "blocked_general_person_place": len(blocked), "weak_examples": weak[:40], "status": dict(collections.Counter(t["status"] for t in d3.values()))}
# ---- gold occurrences
from synthetic_corpus_01 import P
import re
SPLIT = re.compile(r"(?<!Mrs\.)(?<!Mr\.)(?<!Dr\.)(?<!St\.)(?<![A-Z]\.)(?<=[.!?])\s+")
gold_d3 = json.load(open(os.path.join(HERE, "d3_gold_01.json"), encoding="utf-8"))["true_entities"]
occ_d3 = 0
for f in d3_files():
    for s in load_segments(f):
        ws = ret.words(s.text)
        for g in gold_d3:
            gw = [w.fold for w in ret.words(g)]
            occ_d3 += sum(1 for i in range(len(ws) - len(gw) + 1) if [w.fold for w in ws[i:i + len(gw)]] == gw)
occ_d4 = sum(len(o) for x in json.load(open(os.path.join(HERE, "sc2_sc3_detection_01_result.json"), encoding="utf-8"))["d4"] for o in [x["occurrences"]])
s2 = json.load(open(os.path.join(HERE, "sc2_sc3_detection_01_result.json"), encoding="utf-8"))
bertie = [x for x in s2["d4"] if x["category"] == "person" and x["rule_eligible"] and any(o["det_evidence"] is False for o in x["occurrences"])]
res["gold_occurrences"] = {"d3_occurrences": occ_d3, "d4_occurrences": occ_d4, "total": occ_d3 + occ_d4}
res["bertie_type_entities(person, CMU-in non-general, some occurrence w/o existing evidence)"] = {"n": len(bertie), "usable": sum(1 for x in bertie if x["usable"]),
    "all_needs_table_occ_granted": all(o["table_grant"] for x in bertie for o in x["occurrences"] if o["det_evidence"] is False)}
json.dump(res, open(os.path.join(HERE, "sc7_sc8_summary_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "sc8_d3"}, ensure_ascii=False, indent=1))
print(json.dumps({k: v for k, v in res["sc8_d3"].items() if k != "weak_examples"}, ensure_ascii=False))
