# -*- coding: utf-8 -*-
import json, glob, os, hashlib
B="er052_output/open233_allfact_note_e2e_02"
fr=json.load(open(f"{B}/ledger/FREEZE.json",encoding="utf-8"))
runs=[]; tot={"phase1":0.0,"phase2_en":0.0,"checker":0.0}
for slug in ["meta","hormuz","space_weapons","sewer","ai_control"]:
  for rep in (1,2):
    R=f"{B}/runs/{slug}/nb/p2/rep{rep}"
    def J(p):
        return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else None
    p1=J(f"{R}/nb_provenance_phase1.json"); p2=J(f"{R}/nb_provenance_phase2.json"); bt=J(f"{R}/brief_transfer_check.json")
    cost=J(f"{R}/cost.json") or {}
    cr=glob.glob(f"{R}/checker/runs/*.json"); c=J(cr[0]) if cr else None
    ck={}
    if c:
        cy=c["cycles"]
        ck={"final_state":c["final_state"],"n_cycles":len(cy),"rewrite_used":any(x.get("rewrite_records") for x in cy),
            "final_blocking_count":cy[-1].get("blocking_count"),"residual_defs":len(c["residual_at_pass"]["defs"]),
            "pass_family":c["residual_at_pass"]["final_state_is_pass_family"],"checker_cost_jpy":c["total_cost_jpy"],
            "switches_equal_e2e02":c["provenance"]["switches_equal_e2e02"],"result_json":cr[0]}
        tot["checker"]+=c["total_cost_jpy"]
    stages=(cost.get("by_stage_jpy") or {})
    p1c=sum(v for k,v in stages.items() if k!="advanced"); enc=stages.get("advanced",0.0)
    tot["phase1"]+=p1c; tot["phase2_en"]+=enc
    stop1=f"{R}_stop1"
    runs.append({"slug":slug,"rep":rep,"out_dir":R,
      "command":f"OPEN233_RUNS_ROOT={B}/runs OPEN233_B3_VARIANT=nb OPEN233_NOTE_PREFIX='注意:' python er052_open233_polysemy_nb_dev_01.py --phase phase1|phase2 --slug {slug} --theme er052_output/open233_polysemy_trial_02/ledgers/{slug}/topic.txt --ledger-txt {B}/ledger/{slug}/research_ledger/verified_fact_ledger.txt --out-dir {R} --budget-jpy 8(p1)/15(p2) --yes-run-paid (via {B}/tools/launch.sh)",
      "env":{"OPEN233_B3_VARIANT":"nb","OPEN233_NOTE_PREFIX":"注意:"},
      "ledger_p2_sha256":fr["themes"][slug]["p2_sha256"],"transfer_block_sha256":(p1 or {}).get("transfer_block_sha256"),
      "brief_transfer_check":{k:bt[k] for k in ("selected_facts","both_reached","existing_only","poly_only","ALL_PASS")} if bt else None,
      "phase1_state":(p1 or {}).get("exit_reason"),"phase2_state":(p2 or {}).get("exit_reason"),"checker_exit_code":(p2 or {}).get("checker_exit_code"),
      "stop_reason":None,"rerun":os.path.exists(stop1),"stop_attempt_dir":stop1 if os.path.exists(stop1) else None,
      "artifacts":{"selected_brief":f"{R}/storyline_b3/selected_brief.md","ja_original":f"{R}/ja_writer/original.md","ja_r1":f"{R}/ja_writer/revision1.md","ja_r2":f"{R}/ja_writer/revision2.md","en_article":f"{R}/b1b/article.md"},
      "checker":ck,"cost_jpy":{"phase1":round(p1c,4),"phase2_en":round(enc,4),"checker":ck.get("checker_cost_jpy",0)}})
    if os.path.exists(stop1):
        runs[-1]["stop_reason"]="JA_FACT_CHECK_STOP: JA R2 Fact Check LEDGER_DEVIATION(must-fix Rewrite後もMAJOR)。同一枠で1回再実行済み"
tot["total"]=round(sum(tot.values()),4)
stopcost=0.0
for sc in glob.glob(f"{B}/runs/*/nb/p2/rep*_stop1/cost.json"):
    stopcost+=json.load(open(sc,encoding="utf-8")).get("total_jpy",0.0)
json.dump({"runs":runs,"totals_jpy":tot,"stop_attempt_cost_jpy":round(stopcost,4),"n_runs":len(runs)},open(f"{B}/runs/manifest.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
json.dump({"cap_jpy":300,"stop_threshold_jpy":250,"phaseA_meta_rep1_included_in_phase1":True,"totals_jpy":tot,"stop_attempt_cost_jpy":round(stopcost,4),"grand_total_jpy":round(tot["total"]+stopcost,4),"per_run":[{"run":f"{r['slug']}_rep{r['rep']}","cost":r["cost_jpy"]} for r in runs]},open(f"{B}/cost.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
for r in runs:
    print(r["slug"],r["rep"],r["phase1_state"],r["phase2_state"],r["brief_transfer_check"],r["rerun"],r["checker"].get("final_state"),r["checker"].get("n_cycles"),r["checker"].get("rewrite_used"),r["checker"].get("final_blocking_count"),r["checker"].get("residual_defs"),r["cost_jpy"])
print(tot,stopcost)
