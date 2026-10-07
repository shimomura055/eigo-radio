import json, sys, os, importlib.util
sys.path.insert(0, ".")
import er052_open233_self_recovery_precheck_01 as new
spec = importlib.util.spec_from_file_location("old_pc", "er052_output/open238_precheck_fix_trial_01/runtime_evidence/tools/precheck_pre_wiring_HEAD_b1ed9b66.py")
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
D = "er052_output/open238_precheck_fix_trial_01/runtime_evidence"
r = json.load(open(f"{D}/run/runs/meta_run03_advanced.json", encoding="utf-8"))
led = open("er052_output/open233_allfact_note_e2e_02/ledger/ai_control/research_ledger/verified_fact_ledger.txt", encoding="utf-8").read()
TP = "set up by a third party"
def nm(fs): return [{k: f.get(k) for k in ("field","fact_id","foreign_values","article_evidence","kind")} for f in fs if f.get("kind")=="number_mismatch" or f.get("type")=="number_mismatch"]
out = {"final_state": r["final_state"], "n_cycles": len(r["cycles"]), "cost": r["run_cost_jpy"], "cycles": []}
for c in r["cycles"]:
    row = {"cycle": c["cycle"], "blocking": c["blocking_count"], "nb": c["non_blocking_count"],
           "rewrites": [{k: (v if not isinstance(v,str) or len(v)<300 else v[:300]) for k,v in rr.items() if k in ("fact_id","issue_id","before","after","action","sentence_before","sentence_after","rewrite_type")} for rr in c.get("rewrite_records",[])],
           "precheck_detected_stage2": [s.get("fact_id") or s.get("issue_id") for s in c["stage2_results"] if s.get("detected_by")=="precheck"],
           "rewrite_new_precheck_findings_count": c.get("rewrite_new_precheck_findings_count")}
    for tag in ("en_text_before_rewrite","en_text_after_rewrite"):
        t = c.get(tag)
        if not t: continue
        fn = new.run_precheck(led, t); fo = old.run_precheck(led, t)
        row[tag] = {"third_party_sentence_present": TP in t, "wired_precheck_total": len(fn), "wired_number_mismatch": nm(fn),
                    "pre_wiring_number_mismatch_count": len(nm(fo)), "pre_wiring_number_mismatch": nm(fo)}
    out["cycles"].append(row)
out["call_log_retry_fallback"] = sum(1 for x in r["call_log"] if any(k in json.dumps(x).lower() for k in ("retry","fallback")))
out["n_calls"] = len(r["call_log"])
out["errors_in_call_log"] = sum(1 for x in r["call_log"] if x.get("error"))
json.dump(out, open(f"{D}/precheck_findings_per_cycle.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:6000])
