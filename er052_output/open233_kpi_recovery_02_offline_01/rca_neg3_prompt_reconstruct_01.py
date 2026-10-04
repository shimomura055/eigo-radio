# -*- coding: utf-8 -*-
# 委任_05 作業2: rep27 neg3_hormuz_prodrunner_b1b s1のRecheck/確認callのpromptを、記録済みの値(cycle本文・claim・Rewrite記録)と
# runnerの組み立て関数から決定論に再構築し、call_logのprompt_sha256との一致で正しさを検証する(API call 0、JPY0)。
import json, os, sys
sys.path.insert(0, os.getcwd())
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_stage2_production_01 as s2p  # noqa
import er003_v1_en_direct_vfl_01_generate as vfl01

runner.apply_kpi_trial_switches()
RUN = sys.argv[1] if len(sys.argv) > 1 else "er052_output/open233_self_recovery_flow_runner_01_rep27/instances_s1/neg3_hormuz_prodrunner_b1b.json"
d = json.load(open(RUN, encoding="utf-8"))
iid = d["instance_id"]
fx = {i["instance_id"]: i for i in runner.build_target_instances()}[iid]["fixture"]
c = d["cycles"][0]
en_after = c["en_text_after_rewrite"]
bl = [s for s in c["stage2_results"] if s["materiality"] == "BLOCKING"]
recs = c["rewrite_records"]
rec_by = {r["claim_identity"]: r for r in recs}
all_units = [u for r in recs for u in runner.collect_replaced_units(r, r["claim_identity"])]
prior_issues = []
for cl in bl:
    orig = cl.get("claim_span_text") or cl["claim_text"]
    txt, src = runner.resolve_prior_issue_text(orig, rec_by.get(runner.claim_identity(cl["dev"])), all_units, en_after, fx.get("source_article_text"))
    prior_issues.append({"fact_id": cl["dev"].get("related_fact_id", ""), "claim_in_article": txt,
                         "issue": cl["dev"].get("issue", ""), "explanation": cl["dev"].get("explanation", "")})
# 再構築
rf = dict(fx); rf["article_text"] = en_after
tmpl = runner.trial.build_trial_prompt_template("V4A")
base = tmpl.format(verified_ledger_text=fx["ledger_text"], article_text=en_after) + vfl01.RELATED_FACT_ID_INSTRUCTION
if fx.get("source_article_text") is not None:
    base += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fx["source_article_text"])
prior_instr = vfl01.build_prior_issues_instruction(prior_issues)
p_recheck = base + prior_instr
pairs = []
for r in recs:
    la = [a for a in (r["handoff"].get("level_attempts") or []) if a.get("result") == "success"]
    if la:
        pairs.append({"before": la[0]["before_after"][0]["before"], "after": la[0]["before_after"][0]["after"]})
p_confirm = base + prior_instr + runner.CITE_OR_RELEASE_INSTRUCTION + runner.build_before_after_instruction(pairs)
logs = {l["label"].rsplit("_", 1)[-1]: l for l in d["call_log"] if l["label"].endswith("recheck") or l["label"].endswith("recheck_confirm")}
out = {"prior_issues": prior_issues, "prior_issues_instruction": prior_instr, "pairs": pairs,
       "confirm_tail": runner.CITE_OR_RELEASE_INSTRUCTION + runner.build_before_after_instruction(pairs)}
for lab, p in (("recheck", p_recheck), ("confirm", p_confirm)):
    lg = [l for l in d["call_log"] if l["label"].endswith("_" + ("recheck" if lab == "recheck" else "recheck_confirm"))][0]
    sha = s2p.sha256_text(p)
    out[lab] = {"sha_reconstructed": sha, "sha_logged": lg["prompt_sha256"], "match": sha == lg["prompt_sha256"],
                "logged_status": lg.get("overall_status"), "logged_all_prior": lg.get("all_prior_issues_resolved")}
json.dump(out, open("er052_output/open233_kpi_recovery_02_offline_01/rca_neg3_prompt_reconstruct_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("recheck", "confirm")}, ensure_ascii=False, indent=1))
print("PRIOR_INSTRUCTION:\n" + prior_instr)
print("CONFIRM_TAIL:\n" + out["confirm_tail"])
