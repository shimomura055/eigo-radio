# -*- coding: utf-8 -*-
"""OPEN-238 B2: 修正版precheck(DEVラッパinstall)で ai_control nb p2 rep2 のChecker経路を1回再生(Trial専用)。"""
import hashlib, json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "er052_output/open233_ledger_clarity_p_trial_01/tools"))
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_precheck_01 as precheck
import er052_open238_precheck_fix_dev_01 as fix
import run_checker_after_p01 as rc

E2E = "er052_output/open233_allfact_note_e2e_02"
RUN = f"{E2E}/runs/ai_control/nb/p2/rep2"
OUT = "er052_output/open238_precheck_fix_trial_01/replay/fixed"
BUDGET = 60.0

def main():
    if os.path.exists(f"{OUT}/runs"): raise SystemExit("既存出力あり")
    fix.install(runner, precheck)
    fix.reset_counters()
    applied = runner.apply_open233_approved_flow_switches()
    runner.assert_open233_approved_flow_switches()
    inst = rc.build_after_instance("", f"{E2E}/ledger/ai_control/research_ledger/verified_fact_ledger.txt",
                                   f"{RUN}/b1b/article.md", f"{RUN}/ja_writer/revision2.md")
    runner.OUT_DIR = OUT
    runner.BUDGET_STATE_PATH = f"{OUT}/budget_state_replay_fixed.json"
    runner.TOTAL_BUDGET_JPY = BUDGET
    dump = f"{OUT}/approved_switches_dump_replay.json"
    rc.save(dump, {"switches": applied})
    ref = "er052_output/open233_prod_e2e_02/approved_switches_dump_worker1.json"
    prov = {"switch_dump_sha256": rc.sha256_file(dump), "ref_dump_worker1_sha256": rc.sha256_file(ref),
            "switches_equal_ref": json.load(open(ref, encoding="utf-8")).get("switches") == applied,
            "fix_installed": fix._state["installed"], "model_id": applied.get("MODEL"),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    rc.save(f"{OUT}/replay_provenance.json", prov)
    if "--yes-run-paid" not in sys.argv:
        print("dry-run OK", prov); return
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    state = runner.load_budget_state(); start = state["cumulative_jpy"]
    res = runner.run_instance(client, state, [0], inst, enable_s1u=False, stage1_cache=None, instances_subdir="after_instances")
    res["run_cost_jpy"] = round(state["cumulative_jpy"] - start, 4)
    res["provenance"] = prov; res["fix_counters"] = dict(fix.counters)
    rc.save(f"{OUT}/runs/{inst['instance_id']}.json", res)
    print("[done]", res.get("final_state"), res["run_cost_jpy"], fix.counters)

main()
