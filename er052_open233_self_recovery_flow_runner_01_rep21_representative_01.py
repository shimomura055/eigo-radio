# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep21_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_36: rep20 sample2の
# ladder_exhausted_without_full_rewrite根本原因是正[§6-18]後の
# frozen fixture再検証)
# ============================================================
# 目的:
# Part B(主体、n=2): rep19/rep20と同じfrozen fixture(iter8 cycle1の
#   Stage1原本、`er052_output/open233_self_recovery_flow_runner_01_rep19/
#   stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、
#   再freezeしない)を`stage1_mode=reuse`で固定入力とし、(§6-18)是正後の
#   コードでmeta_run03_standardをn=2実行する。期待(委任文§2 C): Stage4
#   到達0・cycle<=2・Rewriteは単語置換のみ・見出し保持・JA/EN等価PASS。
# Part Safety対照(full flow n=1): Safety12のうちchanged_number fixture
#   (`safety_er009_changed_number`)を既定構成でfull flow実行し、floorが
#   引き続き違反文自体をBLOCKING維持する(本委任の変更が安全装置を弱めて
#   いないこと)を確認する。
#
# 設計制約(既存er052系rep7〜rep20と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜8・rep7〜20の出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜20)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_REP21、本委任でrunner
#   本体に新設済み)のみへ書く。rep19のfrozen fixture自体は読み込むのみで
#   変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

FROZEN_STAGE1_SOURCE = (
    "er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/"
    "meta_run03_standard_iter8_cycle1_frozen.json"
)

EXPECTED_RESULT = (
    "(委任_36 §6-18是正: locate_multi_quote_span新設+locate_target/"
    "run_paired_local_rewriteのja_target決定への組み込み)後、rep19/rep20と"
    "同一のfrozen fixtureでStage4到達0・cycle<=2・Rewriteは単語置換のみ・"
    "見出し保持・JA/EN等価PASSを期待(委任文§2 C)。"
)

SAFETY_CONTRAST_FULL_FLOW_INSTANCE_IDS = ["safety_er009_changed_number"]


def _extract_stage2_materialities(result: dict) -> list:
    return [
        {"cycle": cycle.get("cycle"), "claim_text": sr.get("claim_text"),
         "related_fact_id": sr.get("related_fact_id"),
         "materiality": sr.get("materiality"), "llm_materiality": sr.get("llm_materiality"),
         "floor_reason": sr.get("floor_reason"),
         "detected_by_enumeration": sr.get("dev", {}).get("detected_by_enumeration", False)}
        for cycle in result.get("cycles", []) for sr in cycle.get("stage2_results", [])
    ]


def run_part_b(client, state, consecutive_errors) -> dict:
    base_instance = next(
        inst for inst in runner.build_target_instances() if inst["instance_id"] == "meta_run03_standard")
    inst = dict(base_instance)
    inst["stage1_mode"] = "reuse"
    inst["stage1_source"] = FROZEN_STAGE1_SOURCE

    sample_results: list = []
    stopped, stop_reason = False, None
    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        try:
            result = runner.run_instance(client, state, consecutive_errors, inst,
                                          enable_s1u=False, stage1_cache=None,
                                          instances_subdir=subdir)
            sample_results.append(result)
        except runner.TrialAbort as e:
            stopped = True
            stop_reason = str(e)
            break

    safety_critical_rows = runner.detect_safety_critical_misdowngrades(sample_results)
    per_sample = []
    for i, r in enumerate(sample_results, start=1):
        per_sample.append({
            "sample": i, "final_state": r["final_state"], "stage4_reason": r.get("stage4_reason"),
            "num_cycles": len(r.get("cycles", [])),
            "total_cost_jpy": r["total_cost_jpy"],
            "stage2_materialities": _extract_stage2_materialities(r),
        })
    return {
        "expected": EXPECTED_RESULT, "stopped": stopped, "stop_reason": stop_reason,
        "n_samples_completed": len(sample_results), "n_samples_planned": 2,
        "per_sample": per_sample, "safety_critical_misdowngrade_rows": safety_critical_rows,
        "instance_results": [{k: v for k, v in r.items() if k != "call_log"} for r in sample_results],
    }


def run_safety_contrast_a(client, state, consecutive_errors) -> dict:
    """Safety12のうちchanged_number fixture1件をfull flow n=1で実行し、
    違反文自体がfloorでBLOCKING維持されることを確認する(既存safety
    instanceをそのまま使う、新規fixture捏造なし)。"""
    rows = []
    for instance_id in SAFETY_CONTRAST_FULL_FLOW_INSTANCE_IDS:
        inst = next(i for i in runner.build_target_instances() if i["instance_id"] == instance_id)
        try:
            result = runner.run_instance(client, state, consecutive_errors, inst,
                                          enable_s1u=False, stage1_cache=None,
                                          instances_subdir="instances_safety_a")
            rows.append({
                "instance_id": instance_id, "final_state": result["final_state"],
                "stage4_reason": result.get("stage4_reason"),
                "total_cost_jpy": result["total_cost_jpy"],
                "stage2_materialities": _extract_stage2_materialities(result),
            })
        except runner.TrialAbort as e:
            rows.append({"instance_id": instance_id, "aborted": True, "stop_reason": str(e)})
            break
    return {"rows": rows}


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    part_b = {"stopped": True, "stop_reason": "not_started"}
    safety_a = {"rows": []}

    try:
        part_b = run_part_b(client, state, consecutive_errors)
        if not part_b.get("stopped"):
            safety_a = run_safety_contrast_a(client, state, consecutive_errors)
    except runner.TrialAbort as e:
        if "stop_reason" not in part_b or part_b.get("stop_reason") in (None, "not_started"):
            part_b["stopped"] = True
            part_b["stop_reason"] = str(e)

    summary = {
        "expected": EXPECTED_RESULT,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "part_b": {k: v for k, v in part_b.items() if k != "instance_results"},
        "safety_contrast_a_full_flow": safety_a,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep21.json", {
        "summary": summary, "part_b_instance_results": part_b.get("instance_results", []),
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str)[:12000])


if __name__ == "__main__":
    main()
