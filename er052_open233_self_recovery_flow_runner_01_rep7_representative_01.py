# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep7_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_16 作業C: 代表5ケースTrial)
# ============================================================
# 目的: 委任文§3-Cで指定された代表5 instance(neg1_meta_b3prod_a2/
# bgroup_B3/hormuz_run03_standard/safety_er009_changed_actor/
# safety_er009_changed_number)のみをn=2で実行する(29 instance全量の
# 再実行は本委任スコープ外、Guardrail¥15内で安価に確認する)。
#
# 重要な設計制約(既存er052系と同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜6の出力(OUT_DIR_ITER1〜5/OUT_DIR_ITER6)は変更しない
#   (本ファイルはrunner.OUT_DIR[= OUT_DIR_REP7、委任_16でrunner本体に
#   新設]のみへ書く)。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 5 instance全てがstage1_mode="reuse"(既存V4A artifact再利用、¥0)で
#   あることを実行前に確認済み(Stage1コストは発生しない)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

REP7_INSTANCE_IDS = [
    "neg1_meta_b3prod_a2",       # ケース1: Meta Hook(item2、Hook-aware)
    "bgroup_B3",                 # ケース2+3: B3丸め+B3因果(item1・item4、J-1ラダー)
    "hormuz_run03_standard",     # ケース4: Hormuz scope(HF-009 changed_scope)
    "safety_er009_changed_actor",  # ケース5a: 既知Safety重大(actor floor)
    "safety_er009_changed_number",  # ケース5b: 既知Safety重大(number floor)
]

# 委任文§3-Cの期待結果(事前固定、機械判定用)。
EXPECTED_RESULTS = {
    "neg1_meta_b3prod_a2": {
        "expect": "no_rewrite_or_quality_pass",
        "detail": "Rewriteなしで通過(QUALITY/ACCEPTABLE)を期待",
    },
    "bgroup_B3": {
        "expect": "resolved_with_minimal_ladder",
        "detail": "so->whileの①②で解消、In one line語数+30%以内、背景Fact追加なしを期待",
    },
    "hormuz_run03_standard": {
        "expect": "resolved_minimal_scope_narrow",
        "detail": "narrow_scopeを最小変更で解消、A2語彙内を期待",
    },
    "safety_er009_changed_actor": {
        "expect": "blocking_then_resolved",
        "detail": "BLOCKING維持->①〜③で解消、Recheck all_prior_issues_resolved=Trueを期待",
    },
    "safety_er009_changed_number": {
        "expect": "blocking_then_resolved",
        "detail": "BLOCKING維持->①〜③で解消、Recheck all_prior_issues_resolved=Trueを期待",
    },
}


def _extract_ladder_levels(result: dict) -> list:
    levels = []
    for cycle in result.get("cycles", []):
        for rec in cycle.get("rewrite_records", []):
            levels.append(rec.get("ladder_level_used"))
    return levels


def _extract_section_role_violations(result: dict) -> list:
    out = []
    for cycle in result.get("cycles", []):
        srv = cycle.get("section_role_violation")
        if srv and srv.get("section_role_violated"):
            out.append(srv)
    return out


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    for iid in REP7_INSTANCE_IDS:
        assert iid in all_instances, f"unknown instance_id: {iid}"
        assert all_instances[iid]["stage1_mode"] == "reuse", (
            f"{iid} is not stage1_mode=reuse; aborting to avoid unplanned Stage1 spend")

    stage1_cache: dict = {}
    sample_results: list = []  # [[sample1の5件], [sample2の5件]]
    stopped, stop_reason = False, None

    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        results = []
        for iid in REP7_INSTANCE_IDS:
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
    per_case = []
    for iid in REP7_INSTANCE_IDS:
        entry = {"instance_id": iid, "expected": EXPECTED_RESULTS[iid]}
        for si, by_id in enumerate(by_id_per_sample, start=1):
            r = by_id.get(iid)
            if r is None:
                entry[f"sample{si}"] = None
                continue
            entry[f"sample{si}"] = {
                "final_state": r["final_state"], "stage4_reason": r.get("stage4_reason"),
                "total_cost_jpy": r["total_cost_jpy"],
                "ladder_levels_used": _extract_ladder_levels(r),
                "section_role_violations": _extract_section_role_violations(r),
                "stage2_materialities": [
                    {"claim_text": sr.get("claim_text"), "materiality": sr.get("materiality"),
                     "section_type": sr.get("section_type"), "floor_reason": sr.get("floor_reason")}
                    for cycle in r.get("cycles", []) for sr in cycle.get("stage2_results", [])
                ],
            }
        per_case.append(entry)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed_per_sample": [len(r) for r in sample_results],
        "n_instances_planned": len(REP7_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_case": per_case,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep7.json", {
        "summary": summary,
        "instance_results_sample1": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample_results[0]
        ] if sample_results else [],
        "instance_results_sample2": (
            [{k: v for k, v in r.items() if k != "call_log"} for r in sample_results[1]]
            if len(sample_results) >= 2 else None
        ),
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
