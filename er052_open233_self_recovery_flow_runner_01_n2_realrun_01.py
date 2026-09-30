# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_n2_realrun_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_11 作業D補完: 実run6 instanceの
# n=2実測、Opus L2 #2論点6推奨5「Stage1[V4A]はrun間でPASS/DEVIATIONが
# 反転する実例があるため、同一instance n=2以上でないとEscalation率のCI
# が意味を持たない」への対応)
# ============================================================
# 委任文§4「実run6 instance(hormuz run01/02/03_adv、run03_standard、
# meta run03_std/adv)はn=2で実行」のうち、stage1_mode="fresh"の3件
# (hormuz_run01_advanced/hormuz_run02_advanced/meta_run03_advanced)は
# 実行のたびに独立した新規V4A callが発生するため、本スクリプトで
# instance_idへ"_n2"を付与し2本目の独立標本として実行する
# (stage1_mode="reuse"の3件[hormuz_run03_advanced/run03_standard/
# meta_run03_standard]はStage1が固定artifact再利用のため、本スクリプト
# では対象外とする、既知の限界)。budget_state(累計¥・上限¥45)は
# 本体runner[er052_open233_self_recovery_flow_runner_01.py]と共有し、
# 二重に予算管理しない。
from __future__ import annotations

import json

import er052_open233_self_recovery_flow_runner_01 as runner
import er003_v1_en_direct_vfl_01_generate as vfl01

FRESH_REAL_RUN_IDS = {"hormuz_run01_advanced", "hormuz_run02_advanced", "meta_run03_advanced"}


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    results = []
    stopped, stop_reason = False, None

    for instance_id in sorted(FRESH_REAL_RUN_IDS):
        inst = dict(all_instances[instance_id])
        inst["instance_id"] = f"{instance_id}_n2"
        try:
            result = runner.run_instance(client, state, consecutive_errors, inst, enable_s1u=True)
            results.append(result)
        except runner.TrialAbort as e:
            stopped = True
            stop_reason = str(e)
            break

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed": len(results), "n_instances_planned": len(FRESH_REAL_RUN_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"], "cumulative_errors": state["cumulative_errors"],
        "results_summary": [
            {"instance_id": r["instance_id"], "final_state": r["final_state"],
             "stage4_reason": r["stage4_reason"], "total_cost_jpy": r["total_cost_jpy"],
             "s1u_screen_used": r.get("s1u_screen_used"), "s1u_additional_block": r.get("s1u_additional_block"),
             "s1u_additional_block_label": r.get("s1u_additional_block_label")}
            for r in results
        ],
    }
    with open(f"{runner.OUT_DIR}/summary_n2_realrun.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "instance_results": [
            {k: v for k, v in r.items() if k != "call_log"} for r in results
        ]}, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
