# -*- coding: utf-8 -*-
# 委任_07 作業2 ¥0 replay(決定論、LLM callなし=simple_llm_callをmock):
#  (1) rep28 safety_er009_unsupported_new_claim s1の記録(fixture本文・claim・rewrite_kind=delete)で、構造要素判定がtitleになり、
#      STRUCTURAL_ELEMENT_REWRITE=ONでは0_deleteが選ばれず書き換えへ回る(OFFでは旧挙動のdeleteで本文が空)。
#  (2) neg3 rep28 s1/s2のRecheck応答(prior 1件に対し同index 2項目)で、旧式=False、新式(aggregate_prior_issues_resolved)=True。
import json, os, sys
from unittest import mock
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner
out = {}
ins = {i["instance_id"]: i for i in runner.build_target_instances()}
fx = ins["safety_er009_unsupported_new_claim"]["fixture"]
d = json.load(open("er052_output/open233_self_recovery_flow_runner_01_rep28/instances_s1/safety_er009_unsupported_new_claim.json", encoding="utf-8"))
c = d["cycles"][-1]
cl = [s for s in c["stage2_results"] if s["materiality"] == "BLOCKING"][0]
claim_rec = {"claim_text": cl["claim_text"], "rewrite_kind": cl["rewrite_kind"], "materiality": cl["materiality"], "basis": cl["basis"],
             "rewrite_hint": cl.get("rewrite_hint") or "", "dev": cl["dev"]}
state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
def run(on, llm_reply):
    calls = []
    def llm(client, st, errs, log, label, dev_msg, prompt, model=None):
        calls.append(label); return llm_reply
    with mock.patch.object(runner, "STRUCTURAL_ELEMENT_REWRITE", on), mock.patch.object(runner, "simple_llm_call", side_effect=llm):
        r = runner.rewrite_ranges_ladder(None, dict(state), [0], [], "replay", fx, "article_text", dict(claim_rec))
    return r, calls
r_off, calls_off = run(False, "")
r_on, calls_on = run(True, json.dumps({"revised_ranges": ["Passengers shown higher suggested tip rates tipped more."]}))
sr_off = runner.measure_section_role_violation(fx["article_text"], r_off["updated_text"])
sr_on = runner.measure_section_role_violation(fx["article_text"], r_on["updated_text"])
out["unsupported_new_claim_s1"] = {
    "recorded_rewrite_kind": cl["rewrite_kind"], "recorded_section_type": cl["section_type"],
    "OFF": {"ladder_level_used": r_off["ladder_level_used"], "updated_text": r_off["updated_text"], "llm_calls": calls_off,
            "title_degenerate": sr_off["title_degenerate"], "hook_degenerate": sr_off["hook_degenerate"]},
    "ON": {"ladder_level_used": r_on["ladder_level_used"], "updated_text": r_on["updated_text"], "llm_calls": calls_on,
           "structural": r_on["handoff"].get("structural_element_rewrite"),
           "levels": [(a["level"], a["result"]) for a in r_on["handoff"]["level_attempts"]],
           "title_degenerate": sr_on["title_degenerate"], "hook_degenerate": sr_on["hook_degenerate"]},
}
neg = []
for s in ("s1", "s2"):
    dd = json.load(open(f"er052_output/open233_self_recovery_flow_runner_01_rep28/instances_{s}/neg3_hormuz_prodrunner_b1b.json", encoding="utf-8"))
    cc = dd["cycles"][0]
    items, n = cc["recheck_prior_issues_resolved"], cc["recheck_prior_issues_sent_count"]
    ok, by = runner.aggregate_prior_issues_resolved(["x"] * n, items)
    neg.append({"sample": s, "prior_sent": n, "items": [(i["index"], i["resolved"]) for i in items], "recorded_old_all_prior": cc["recheck_all_prior_issues_resolved"],
                "new_all_prior": ok, "by_index": by, "confirm_called_in_record": cc.get("recheck_confirm_overall_status") is not None})
out["neg3_rep28"] = neg
json.dump(out, open("er052_output/open233_kpi_recovery_02_offline_01/replay_title_delete_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
