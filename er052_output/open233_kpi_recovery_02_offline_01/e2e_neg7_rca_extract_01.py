"""委任_22 RCA抽出(¥0・read-only): E2E 9 runとrep30同instanceのBLOCKING/Rewrite/cycle/Stage4を抽出する。"""
import json, glob, os, sys
E2E = r"C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01\runs\s1"
REP30 = r"C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_flow_runner_01_rep30\instances_s1"
OUT = os.path.dirname(os.path.abspath(__file__))

def load(p):
    return json.load(open(p, encoding="utf-8"))

def summarize(d):
    o = {"group": d.get("group"), "expected": d.get("expected_group_label"), "final_state": d.get("final_state"),
         "stage4_reason": d.get("stage4_reason"), "cost": d.get("total_cost_jpy"), "n_cycles": len(d.get("cycles", [])),
         "n_stage1_union": (d.get("stage1_coverage") or {}).get("n_union_candidates"), "cycles": []}
    for c in d.get("cycles", []):
        bl = []
        for s in c.get("stage2_results", []):
            if s.get("materiality") == "BLOCKING":
                dv = s.get("dev", {})
                so = s.get("second_opinion") or {}
                bl.append({"fact": s.get("related_fact_id"), "claim": s.get("claim_text", "")[:160],
                           "llm_materiality": s.get("llm_materiality"), "basis": s.get("basis"),
                           "floor": s.get("floor_reason"), "tier0_reason": (s.get("tier0") or {}).get("reason"),
                           "s1": [so.get("first_materiality"), so.get("second_materiality")] if so else None,
                           "issue": (dv.get("issue") or "")[:200]})
        rws = [{"id": r.get("claim_identity"), "method": r.get("method"), "lvl": r.get("ladder_level_used"),
                "guard": r.get("guard_ok"), "notloc": r.get("target_not_locatable"),
                "exhausted": r.get("ladder_exhausted_without_full_rewrite")} for r in c.get("rewrite_records", [])]
        rr = c.get("recheck_prior_issues_resolved") or []
        o["cycles"].append({"cycle": c.get("cycle"), "blocking_count": c.get("blocking_count"),
                            "non_blocking_count": c.get("non_blocking_count"), "n_rewrite": len(rws),
                            "blocking": bl, "rewrites": rws,
                            "recheck_unresolved": sum(1 for x in rr if not x.get("resolved")), "recheck_total": len(rr),
                            "merge_decision": (c.get("recheck_merge") or {}).get("decision"),
                            "full_recheck_reasons": c.get("full_recheck_required_reasons"),
                            "last_resort_delete_failed": c.get("last_resort_delete_failed")})
    return o

res = {"e2e": {}, "rep30": {}}
for p in sorted(glob.glob(os.path.join(E2E, "*.json"))):
    n = os.path.basename(p)[:-5]
    res["e2e"][n] = summarize(load(p))
    q = os.path.join(REP30, n + ".json")
    if os.path.exists(q):
        res["rep30"][n] = summarize(load(q))
json.dump(res, open(os.path.join(OUT, "e2e_neg7_rca_extract_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res["e2e"].items():
    r = res["rep30"].get(k)
    print(k, v["group"], v["final_state"], "cyc", v["n_cycles"], "BL", [c["blocking_count"] for c in v["cycles"]],
          "RW", [c["n_rewrite"] for c in v["cycles"]], "s1union", v["n_stage1_union"], "cost", v["cost"])
    if r:
        print("   rep30:", r["final_state"], "cyc", r["n_cycles"], "BL", [c["blocking_count"] for c in r["cycles"]],
              "RW", [c["n_rewrite"] for c in r["cycles"]], "s1union", r["n_stage1_union"])
