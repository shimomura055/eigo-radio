# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep30a_limited_01.py
# OPEN-233-KPI-RECOVERY-REDESIGN-02 (委任_11作成・未実行。実行は委任_12): rep30a = 限定確認(rep30の前提確認)。
# 対象(3 run): meta_run03_advanced s1 / s2(rep29のHuman Review 2件=same_claim・violation_span_unverifiedの再確認)、safety_A4 s1(rep29の
# cycle_limit_exhausted_after_recheck=G/判定だけのcycleの再確認)。構成=rep30と同一(`rep30_full_01.apply_switches`)。
# 費用: `--budget-jpy`既定7(委任_11見積≈¥5、暴走防止Guardrail)。即時STOP: JA変更・例外2 instance以上・1 instance-run費用>JPY7・TrialAbort。
# 重大見逃し/STAGE4は止めずに完走し記録する(件数と原因を集計で特定)。Production codeは変更しない。出力はrep30a配下のみ。再実行しない(既存jsonはskip)。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep30_full_01 as full

OUT_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep30a"
BUDGET_STATE = f"{OUT_DIR}/budget_state_c233ay_12_rep30a.json"
PLAN = [(1, "meta_run03_advanced"), (2, "meta_run03_advanced"), (1, "safety_A4")]


def run_main(budget_jpy: float, reuse: bool, sibling: bool):
    applied = full.apply_switches(budget_jpy, False, reuse, sibling)
    runner.OUT_DIR = OUT_DIR
    runner.BUDGET_STATE_PATH = BUDGET_STATE
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    for sample_idx, iid in PLAN:
        subdir = f"instances_s{sample_idx}"
        if os.path.exists(f"{OUT_DIR}/{subdir}/{iid}.json"):
            print(f"[skip existing] {subdir}/{iid}")
            continue
        try:
            r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                    stage1_cache=stage1_cache, instances_subdir=subdir)
        except runner.TrialAbort as e:
            log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
            break
        except Exception as e:  # noqa: BLE001
            log["exceptions"].append({"sample": sample_idx, "instance_id": iid, "error": repr(e), "tb": traceback.format_exc()[-1500:]})
            print(f"[EXCEPTION] {subdir}/{iid}: {e!r}")
            if len({x['instance_id'] for x in log["exceptions"]}) >= 2:
                log.update(stopped=True, stop_reason="exceptions in >=2 instances")
                break
            continue
        reasons = full.stop_reasons(r)
        print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} cost=JPY{r['total_cost_jpy']} "
              f"cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
        log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                            "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"], "stop_check": reasons,
                            "stage4_allowlist": (r.get("stage4_allowlist") or {})})
        if reasons:
            log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2, default=str)[:6000])


def run_agg():
    import er052_open233_self_recovery_flow_runner_01_rep30_agg_01 as agg
    runs = []
    for s, iid in PLAN:
        p = f"{OUT_DIR}/instances_s{s}/{iid}.json"
        if os.path.exists(p):
            runs.append((s, iid, json.load(open(p, encoding="utf-8"))))
    m = agg.new_design_metrics(runs)
    out = {"runs": [(s, i, d["final_state"], d.get("stage4_reason"), d.get("total_cost_jpy")) for s, i, d in runs], "new_design": m,
           "cost_total_jpy": round(sum((d.get("total_cost_jpy") or 0) for _s, _i, d in runs), 4)}
    with open(f"{OUT_DIR}/summary_kpi_01.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:8000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--budget-jpy", type=float, default=7.0)
    ap.add_argument("--reuse", choices=["on", "off"], default="on")
    ap.add_argument("--sibling", choices=["on", "off"], default="on")
    args = ap.parse_args()
    if args.stage == "agg":
        run_agg()
        return
    run_main(args.budget_jpy, args.reuse == "on", args.sibling == "on")


if __name__ == "__main__":
    main()
