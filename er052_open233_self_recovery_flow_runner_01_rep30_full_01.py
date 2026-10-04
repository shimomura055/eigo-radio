# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep30_full_01.py
# OPEN-233-KPI-RECOVERY-REDESIGN-02 (委任_11作成・未実行。実行は委任_12以降、限定確認[rep30a]の後): rep30 = rep29と同じ29 instance・38 instance-run、
# KPI構成(`apply_kpi_trial_switches`)+Opus#14後のFable評価採用設計の新スイッチ(STAGE4_ALLOWLIST/LADDER_LOCATION_CARRY/REWRITE_REVERT_GUARD/
# SPAN_FALLBACK_CHAIN/JUDGE_ONLY_CYCLE_AFTER_CAP/LAST_RESORT_DELETE/MATERIALITY_BLOCKING_PIN=既定ON)。
# 既定OFFの2スイッチ(STAGE2_VERDICT_REUSE_NONBLOCKING/STAGE2_SIBLING_LOCATIONS_CYCLE1)は、事前固定条件の¥0 replay結果でON/OFFを決める
# (委任_11の結果: `--reuse`/`--sibling`の既定へ反映。replay_verdict_reuse_01/agg_sibling_locations_cycle1_01)。
# 即時STOP: JA変更(a)・例外2 instance以上・1 instance-run費用>JPY7・TrialAbort。重大見逃し/STAGE4は止めずに完走し記録する。
# Production codeは変更しない。出力はOUT_DIR_REP30のみ。再実行・n増しはしない(既存jsonがあればskip)。TTSなし。集計(--stage agg)はrep30_agg_01(API呼び出しなし)。
# 予算: `--budget-jpy`既定28(委任_11見積: rep29実績+新経路[T=Recheck1回、判定だけのcycle=Stage2+S1、兄弟列挙=Stage2 token増]の余裕、暴走防止Guardrail)。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep23_limited_01 as rep23

OUT_DIR_REP30 = "er052_output/open233_self_recovery_flow_runner_01_rep30"
BUDGET_STATE_REP30 = f"{OUT_DIR_REP30}/budget_state_c233ay_11_rep30.json"
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
SAFETY_CRITICAL_6 = {**SAFETY_CRITICAL_5, "neg5_hormuz_div_a2": "B3-same@neg5"}
REP24_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep24"
REP27_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep27"
REP28_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep28"
REP29_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep29"


def apply_switches(budget_jpy: float, n3: bool, reuse: bool = True, sibling: bool = True) -> dict:
    runner.OUT_DIR = OUT_DIR_REP30
    runner.BUDGET_STATE_PATH = BUDGET_STATE_REP30
    runner.TOTAL_BUDGET_JPY = budget_jpy
    applied = runner.apply_kpi_trial_switches()
    runner.RECHECK_BEFORE_AFTER_PAIRS = n3
    runner.STAGE2_VERDICT_REUSE_NONBLOCKING = reuse
    runner.STAGE2_SIBLING_LOCATIONS_CYCLE1 = sibling
    assert runner.RECHECK_MERGE_UNRESOLVED is True
    assert runner.ACTOR_GUARD_MODE == "ag1_strict" and runner.STRUCTURAL_PAIRS_TO_RECHECK is True and runner.STRUCTURAL_ELEMENT_REWRITE is True
    assert runner.RECHECK_BEFORE_AFTER_PAIRS is False  # N3′はOFF(委任_06 A/Bで不採用)
    assert runner.STAGE2_DOWNGRADE_VERIFY is False and runner.TIER0_G_L_ENABLED is False
    assert runner.CAUSAL_FLOOR is True and runner.CAUSAL_FLOOR_VOCAB == "known6" and runner.STAGE2_SECOND_OPINION is True
    assert runner.STAGE2_NORMAL_TWO_OF_TWO is False and runner.VS_SENTENCE_RESTORE is True
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    for k_ in ("STAGE4_ALLOWLIST", "LADDER_LOCATION_CARRY", "REWRITE_REVERT_GUARD", "SPAN_FALLBACK_CHAIN",
               "JUDGE_ONLY_CYCLE_AFTER_CAP", "LAST_RESORT_DELETE", "MATERIALITY_BLOCKING_PIN"):
        assert getattr(runner, k_) is True, k_
    assert runner.STAGE2_VERDICT_REUSE_NONBLOCKING is reuse and runner.STAGE2_SIBLING_LOCATIONS_CYCLE1 is sibling
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
    return {**applied, "RECHECK_BEFORE_AFTER_PAIRS": n3, "STAGE2_VERDICT_REUSE_NONBLOCKING": reuse,
            "STAGE2_SIBLING_LOCATIONS_CYCLE1": sibling}


def stop_reasons(r: dict) -> list:
    """委任_04の即時STOP条件のみ(JA変更、1 instance-run費用>JPY7)。見逃し・STAGE4・floor_verify解放は止めない。"""
    out = [x for x in rep23.immediate_stop_check(r) if x.startswith("a:")]
    if (r.get("total_cost_jpy") or 0) > 7.0:
        out.append(f"cost>7: {r.get('total_cost_jpy')}")
    return out


def run_main(budget_jpy, n3, reuse=True, sibling=True):
    applied = apply_switches(budget_jpy, n3, reuse, sibling)
    os.makedirs(OUT_DIR_REP30, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    plan = [(1, iid) for iid in ALL_IDS] + [(2, iid) for iid in N2_IDS]
    for sample_idx, iid in plan:
        subdir = f"instances_s{sample_idx}"
        path = f"{OUT_DIR_REP30}/{subdir}/{iid}.json"
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
        reasons = stop_reasons(r)
        print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
              f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
        log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                            "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"], "stop_check": reasons})
        if reasons:
            log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR_REP30}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:6000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--budget-jpy", type=float, default=28.0)
    ap.add_argument("--n3", choices=["on", "off"], default="off", help="RECHECK_BEFORE_AFTER_PAIRS(N3′)。A/B(委任_06 作業4)の結果で決める")
    ap.add_argument("--reuse", choices=["on", "off"], default="on",
                    help="STAGE2_VERDICT_REUSE_NONBLOCKING。委任_11 replay: 抑制8件・ラベル重大0・flip0=事前固定条件を満たす→既定on")
    ap.add_argument("--sibling", choices=["on", "off"], default="on",
                    help="STAGE2_SIBLING_LOCATIONS_CYCLE1。委任_11集計①=1/5=20%%>0=事前固定条件を満たす→既定on(NORMAL群の不要Rewriteがrep29の5/14から増えたら不採用候補)")
    args = ap.parse_args()
    if args.stage == "agg":
        import er052_open233_self_recovery_flow_runner_01_rep30_agg_01 as agg
        agg.run_agg()
        return
    run_main(args.budget_jpy, args.n3 == "on", args.reuse == "on", args.sibling == "on")


if __name__ == "__main__":
    main()
