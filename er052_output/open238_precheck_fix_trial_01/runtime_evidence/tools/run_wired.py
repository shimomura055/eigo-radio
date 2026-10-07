# -*- coding: utf-8 -*-
"""OPEN-238 配線後 runtime evidence: 未パッチのProduction関数(runner.run_instance、承認スイッチ既定)でai_control nb p2 rep2を1 run。
fix.install()は使わない(DEV patch無し)。出力はTrial専用dir。"""
import hashlib, json, os, sys, time, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "er052_output/open233_ledger_clarity_p_trial_01/tools"))
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_precheck_01 as precheck
import run_checker_after_p01 as rc
assert "er052_open238_precheck_fix_dev_01" not in sys.modules, "DEV patch module imported"

E2E = "er052_output/open233_allfact_note_e2e_02"
RUN = f"{E2E}/runs/ai_control/nb/p2/rep2"
OUT = "er052_output/open238_precheck_fix_trial_01/runtime_evidence/run"
BUDGET = 20.0
sha = rc.sha256_file

def main():
    if os.path.exists(f"{OUT}/runs"): raise SystemExit("既存出力あり")
    applied = runner.apply_open233_approved_flow_switches()
    runner.assert_open233_approved_flow_switches()
    inst = rc.build_after_instance("", f"{E2E}/ledger/ai_control/research_ledger/verified_fact_ledger.txt",
                                   f"{RUN}/b1b/article.md", f"{RUN}/ja_writer/revision2.md")
    runner.OUT_DIR = OUT
    runner.BUDGET_STATE_PATH = f"{OUT}/budget_state.json"
    runner.TOTAL_BUDGET_JPY = BUDGET
    ev = "er052_output/open238_precheck_fix_trial_01/runtime_evidence"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "diff", "--stat", "--", "er052_open233_self_recovery_precheck_01.py", "er052_open233_self_recovery_flow_runner_01.py"], text=True)
    rc.save(f"{ev}/approved_switches_dump.json", {"switches": applied})
    ref = "er052_output/open233_prod_e2e_02/approved_switches_dump_worker1.json"
    prov = {"git_head": head, "wired_files_dirty_vs_head": dirty.strip() or "clean",
            "precheck_sha256": sha("er052_open233_self_recovery_precheck_01.py"),
            "runner_sha256": sha("er052_open233_self_recovery_flow_runner_01.py"),
            "dev_patch_module_loaded": "er052_open238_precheck_fix_dev_01" in sys.modules,
            "entry": "runner.run_instance (Production function, unpatched, same as E2E_02 wrapper)",
            "switches_equal_ref_e2e02": json.load(open(ref, encoding="utf-8")).get("switches") == applied,
            "PRECHECK_MODE": applied.get("PRECHECK_MODE"), "FLOOR_MODE": applied.get("FLOOR_MODE"),
            "model_id": applied.get("MODEL"), "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    rc.save(f"{ev}/provenance.json", prov)
    if "--yes-run-paid" not in sys.argv:
        print("dry-run OK", json.dumps(prov, ensure_ascii=False, indent=1)); return
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    state = runner.load_budget_state(); start = state["cumulative_jpy"]
    res = runner.run_instance(client, state, [0], inst, enable_s1u=False, stage1_cache=None, instances_subdir="after_instances")
    res["run_cost_jpy"] = round(state["cumulative_jpy"] - start, 4)
    res["provenance"] = prov
    rc.save(f"{OUT}/runs/{inst['instance_id']}.json", res)
    rc.save(f"{ev}/cost.json", {"total_jpy": res["run_cost_jpy"], "calls": res.get("total_calls"), "limit_jpy": 20})
    print("[done]", res.get("final_state"), res["run_cost_jpy"])
main()
