# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep24_full_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_63: 承認済み対策を全て有効にした29件横断 rep24、1回のみ)
# ============================================================
# rep23_limited_01を複製し、instance集合をiteration 7(委任_22)と同一(29 instance、9 instanceがn=2、20 instanceがn=1、
# 計38 instance-run)にした。スイッチはrep23と同一。runner本体のロジックは変更しない。Production codeは変更しない。
# 出力はOUT_DIR_REP24のみ。TTSなし。再実行・部分再実行・n増しはしない(既存jsonがあればskipするのみ)。
from __future__ import annotations

import argparse
import json
import os
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep23_limited_01 as rep23

OUT_DIR_REP24 = "er052_output/open233_self_recovery_flow_runner_01_rep24"
BUDGET_STATE_REP24 = f"{OUT_DIR_REP24}/budget_state_c233ap_63_rep24.json"
ITER7_DIR = "er052_output/open233_self_recovery_flow_runner_01_iter7"

# iteration 7 n=2 の9 instance(iter7 instances_s1/s2と同一)
N2_IDS = ["safety_A2A3", "bgroup_B3", "meta_run03_standard", "meta_run03_advanced", "hormuz_run03_standard",
          "hormuz_run03_advanced", "neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b"]
# iteration 7 n=1 の20 instance(iter7 instances/と同一)
N1_IDS = ["bgroup_B1", "bgroup_B2_hormuz", "bgroup_B4", "hormuz_run01_advanced", "hormuz_run02_advanced",
          "neg4_smallbag_div_a2", "neg5_hormuz_div_a2", "neg6_smallbag_div_b1b", "neg7_meta_prodrunner_b1b",
          "safety_A4", "safety_A5", "safety_er009_changed_actor", "safety_er009_changed_causality",
          "safety_er009_changed_certainty", "safety_er009_changed_comparison", "safety_er009_changed_negation",
          "safety_er009_changed_number", "safety_er009_changed_scope", "safety_er009_changed_time",
          "safety_er009_unsupported_new_claim"]
ALL_IDS = N2_IDS + N1_IDS
SAFETY_CRITICAL_5 = {"bgroup_B3": "B3", "bgroup_B4": "B4-a", "safety_A2A3": "A2A3-0", "safety_A4": "A4-0", "safety_A5": "A5-0"}


def apply_switches(budget_jpy: float) -> None:
    runner.OUT_DIR = OUT_DIR_REP24
    runner.BUDGET_STATE_PATH = BUDGET_STATE_REP24
    runner.TOTAL_BUDGET_JPY = budget_jpy
    runner.HANDOFF_MODE = runner.HANDOFF_MODE_VIOLATION_SPAN
    runner.VS_MATCH_EXT = True
    runner.VS_EXPLAIN_SPLIT = True
    runner.JA_MODE = runner.JA_MODE_ENGLISH_ONLY
    runner.FLOOR_VERIFY_MODE = runner.validate_floor_verify_mode(runner.FLOOR_VERIFY_MODE_TIME_ONLY)
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B


def run_main(budget_jpy):
    apply_switches(budget_jpy)
    os.makedirs(OUT_DIR_REP24, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    plan = [(1, iid) for iid in ALL_IDS] + [(2, iid) for iid in N2_IDS]
    for sample_idx, iid in plan:
        subdir = f"instances_s{sample_idx}"
        path = f"{OUT_DIR_REP24}/{subdir}/{iid}.json"
        if os.path.exists(path):
            print(f"[skip existing] {subdir}/{iid}")
            continue
        try:
            r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                    stage1_cache=stage1_cache, instances_subdir=subdir)
        except runner.TrialAbort as e:
            log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
            break
        except Exception as e:  # 例外は記録(再実行しない)。2 instance以上でSTOP
            log["exceptions"].append({"sample": sample_idx, "instance_id": iid, "error": repr(e), "tb": traceback.format_exc()[-1500:]})
            print(f"[EXCEPTION] {subdir}/{iid}: {e!r}")
            if len({x['instance_id'] for x in log["exceptions"]}) >= 2:
                log.update(stopped=True, stop_reason="exceptions in >=2 instances")
                break
            continue
        reasons = rep23.immediate_stop_check(r)
        print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
              f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
        log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                            "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"], "stop_check": reasons})
        if reasons:
            log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR_REP24}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:6000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--budget-jpy", type=float, default=70.0)
    args = ap.parse_args()
    if args.stage == "agg":
        import er052_open233_self_recovery_flow_runner_01_rep24_agg_01 as agg
        agg.run_agg()
        return
    run_main(args.budget_jpy)


if __name__ == "__main__":
    main()
