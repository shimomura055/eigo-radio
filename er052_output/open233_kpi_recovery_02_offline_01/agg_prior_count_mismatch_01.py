# -*- coding: utf-8 -*-
# 委任_07 作業1-3(¥0): Recheckの`all_prior_issues_resolved`件数一致バグの発生件数・偽の自己矛盾・再確認call費用の全ログ集計。
# 旧式: all_prior = (len(items)==n_prior) and all(resolved)。新式(index別集約): 全prior indexが揃い、各indexの全項目resolved。
import json, glob, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
def new_all(items, n_prior):
    g = collections.defaultdict(list)
    for it in items or []:
        g[it.get("index")].append(bool(it.get("resolved")))
    return n_prior > 0 and all(i in g and all(g[i]) for i in range(n_prior))
rows = []
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json")):
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    cl = d.get("call_log") or []
    for c in d.get("cycles") or []:
        items = c.get("recheck_prior_issues_resolved")
        if items is None: continue
        n = c.get("recheck_prior_issues_sent_count")
        uniq = len({it.get("index") for it in items})
        dup_idx = len(items) > uniq
        mism = (n is not None and len(items) != n)
        old = c.get("recheck_all_prior_issues_resolved")
        new = new_all(items, n) if n is not None else None
        allres = bool(items) and all(bool(it.get("resolved")) for it in items)
        cc = [x for x in cl if str(x.get("label", "")).endswith(f"_c{c.get('cycle')}_recheck_confirm")]
        rows.append({"run": run, "instance": d.get("instance_id"), "cycle": c.get("cycle"), "n_sent": n, "n_items": len(items), "n_unique_idx": uniq,
                     "dup_index": dup_idx, "count_mismatch": mism, "old_all_prior": old, "new_all_prior": new, "all_items_resolved": allres,
                     "overall": c.get("recheck_overall_status"), "confirm_called": c.get("recheck_confirm_overall_status") is not None,
                     "confirm_cost_jpy": round(sum(x.get("cost_jpy", 0) for x in cc), 4)})
json.dump(rows, open("er052_output/open233_kpi_recovery_02_offline_01/agg_prior_count_mismatch_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rechecks with prior_issues_resolved recorded:", len(rows), " with n_sent recorded:", sum(1 for r in rows if r["n_sent"] is not None))
mm = [r for r in rows if r["count_mismatch"] or r["dup_index"]]
print("count_mismatch or dup_index:", len(mm))
fs = [r for r in mm if r["all_items_resolved"] and r["old_all_prior"] is False]
print("  of which all items resolved but old all_prior=False (false self-contradiction):", len(fs))
fsc = [r for r in fs if r["overall"] == "LEDGER_COMPLIANT"]
print("  of which overall=LEDGER_COMPLIANT (=> triggers reverify call):", len(fsc), " with confirm_called:", sum(1 for r in fsc if r["confirm_called"]),
      " est cost JPY:", round(sum(r["confirm_cost_jpy"] for r in fsc if r["confirm_called"]), 2))
for r in mm: print(" ", r["run"], r["instance"], "c", r["cycle"], "sent", r["n_sent"], "items", r["n_items"], "uniq", r["n_unique_idx"], "allres", r["all_items_resolved"], "old", r["old_all_prior"], "new", r["new_all_prior"], r["overall"], "confirm", r["confirm_called"], r["confirm_cost_jpy"])
# self-contradiction (COMPLIANT & not all_prior) overall, to see how much the mechanism explains
sc = [r for r in rows if r["overall"] == "LEDGER_COMPLIANT" and r["old_all_prior"] is False]
print("ALL self-contradictory rechecks (COMPLIANT & all_prior False):", len(sc), " explained by count/dup mechanism w/ all items resolved:", sum(1 for r in sc if r["all_items_resolved"] and (r["count_mismatch"] or r["dup_index"])))
by = collections.Counter((r["instance"]) for r in sc); print("  by instance:", dict(by))
print("  by run:", dict(collections.Counter(r["run"] for r in sc)))
# fixed-formula differences (n_sent known)
diff = [r for r in rows if r["n_sent"] is not None and r["old_all_prior"] is not None and r["old_all_prior"] != r["new_all_prior"]]
print("old != new (n_sent known):", len(diff), "old False->new True:", sum(1 for r in diff if r["new_all_prior"]), "old True->new False:", sum(1 for r in diff if r["old_all_prior"] and not r["new_all_prior"]))
