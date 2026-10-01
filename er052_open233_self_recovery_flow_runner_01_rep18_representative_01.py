# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep18_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_33: iter8未達3点のうちB3/A2A3-0の
# body rubric V6 full flow確認、2026-10-01)
# ============================================================
# 目的: 委任_32(広いTrial iteration8、REPORT§30-3C/design書§7-0-iter32)が
# full flow(Stage1→Stage2→Rewrite→Recheck)で新規検出したSafety-critical
# 誤降格2件(B3[HF-007]がn=2の両方でQUALITYへ誤降格、A2A3-0[HF-003]が
# n=2の1/2でQUALITYへ誤降格)に対し、body rubric V6(許容/NG対比例示の追加、
# design書§4-25)を既定へ反映した後、`bgroup_B3`(Stage1 fresh)・
# `safety_A2A3`(Stage1 reuse、既定のまま)・`meta_run03_standard`
# (Stage1 fresh)をfull flowで再実行し、誤降格が解消したかを確認する。
#
# 設計制約(既存er052系rep7〜rep17・iter8_01と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜8・rep7〜17の出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜17)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_REP18、本委任でrunner
#   本体に新設済み)のみへ書く。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - `bgroup_B3`/`meta_run03_standard`は`stage1_mode`を"fresh"へ明示的に
#   上書きする(既存reuse元fixtureは重大誤解原則配線前の出力であり、本委任の
#   確認目的には使えないため、iter8_01と同一方針)。`safety_A2A3`は
#   build_target_instances()既定のStage1 reuseのまま据え置く(委任文§2の
#   指定どおり)。
# - 3 instanceともsample1・sample2の2回実行する(stage1_cacheをsample間で
#   共有、Stage1 fresh instanceは二重課金しない)。
# - コストはrunner.TOTAL_BUDGET_JPY(本委任用に¥11へ再設定済み)で自己停止
#   する(Part A/C/Hookの別budget stateと合算してGuardrail¥13、委任文§2)。
#   予算が厳しいため実行順はB3→A2A3→metaの優先順(V6で実際に検証したい
#   claimを先に完走させる、meta_run03_standardは根本原因が別[§31参照]で
#   ありV6の影響を受けない見込みのため優先度を最後にする)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

REP18_INSTANCE_IDS = [
    "bgroup_B3",
    "safety_A2A3",
    "meta_run03_standard",
]

EXPECTED_RESULTS = {
    "bgroup_B3": "BLOCKING維持2/2(委任_32はQUALITYへ誤降格2/2)",
    "safety_A2A3": "BLOCKING維持2/2(委任_32はsample2のみQUALITYへ誤降格1/2)",
    "meta_run03_standard": "V6は本claimの根本原因(deterministic floor:"
                            "changed_numberの多箇所反復、§31参照)に無関係のため"
                            "非回帰(iter8と同程度のSTAGE4到達を許容)",
}


def _extract_stage2_materialities(result: dict) -> list:
    return [
        {"claim_text": sr.get("claim_text"), "related_fact_id": sr.get("related_fact_id"),
         "materiality": sr.get("materiality"), "llm_materiality": sr.get("llm_materiality"),
         "floor_reason": sr.get("floor_reason")}
        for cycle in result.get("cycles", []) for sr in cycle.get("stage2_results", [])
    ]


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    for iid in ("bgroup_B3", "meta_run03_standard"):
        all_instances[iid]["stage1_mode"] = "fresh"
        all_instances[iid]["stage1_source"] = None
    # safety_A2A3はbuild_target_instances()既定のreuseのまま(委任文§2)。

    stage1_cache: dict = {}
    sample_results: list = []
    stopped, stop_reason = False, None

    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        results = []
        for iid in REP18_INSTANCE_IDS:
            inst = all_instances[iid]
            try:
                result = runner.run_instance(client, state, consecutive_errors, inst,
                                              enable_s1u=False, stage1_cache=stage1_cache,
                                              instances_subdir=subdir)
                results.append(result)
            except runner.TrialAbort as e:
                stopped = True
                stop_reason = str(e)
                break
        sample_results.append(results)
        if stopped:
            break

    by_id_per_sample = [{r["instance_id"]: r for r in results} for results in sample_results]
    safety_critical_rows = runner.detect_safety_critical_misdowngrades(
        [r for results in sample_results for r in results])

    per_case = []
    for iid in REP18_INSTANCE_IDS:
        entry = {"instance_id": iid, "expected": EXPECTED_RESULTS[iid]}
        for si, by_id in enumerate(by_id_per_sample, start=1):
            r = by_id.get(iid)
            if r is None:
                entry[f"sample{si}"] = None
                continue
            entry[f"sample{si}"] = {
                "final_state": r["final_state"], "stage4_reason": r.get("stage4_reason"),
                "total_cost_jpy": r["total_cost_jpy"],
                "stage2_materialities": _extract_stage2_materialities(r),
            }
        per_case.append(entry)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed_per_sample": [len(r) for r in sample_results],
        "n_instances_planned": len(REP18_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_case": per_case,
        "safety_critical_misdowngrade_rows": safety_critical_rows,
        "safety_critical_misdowngrade_count_distinct": len({
            (row["instance_id"], row["sub_id"]) for row in safety_critical_rows
        }),
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep18.json", {
        "summary": summary,
        "instance_results_sample1": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample_results[0]
        ] if sample_results else [],
        "instance_results_sample2": (
            [{k: v for k, v in r.items() if k != "call_log"} for r in sample_results[1]]
            if len(sample_results) >= 2 else None
        ),
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str)[:8000])


if __name__ == "__main__":
    main()
