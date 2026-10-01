# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep20_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_35: 委任_34で特定した追加原因(d)の
# 小修正[floorのfact_id単位broadcast廃止+same_fact_id_locations列挙の
# cycle1限定+iol_degenerate guard追加]と、frozen fixture再検証)
# ============================================================
# 目的:
# Part B(主体、n=2): rep19と同じfrozen fixture(iter8 cycle1のStage1原本、
#   `er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/
#   meta_run03_standard_iter8_cycle1_frozen.json`、再freezeしない)を
#   `stage1_mode=reuse`で固定入力とし、(d)是正後のコードでmeta_run03_standard
#   をn=2実行する。期待(委任文§2 B): Stage4到達0・false PASS 0・cycle≤2・
#   Rewriteは単数化等の最小単位のみ・見出し保持・JA/EN等価PASS・
#   費用<¥3/run。
# Part Safety対照A(full flow n=1×2): Safety12のうちchanged_number/
#   changed_actor fixture(`safety_er009_changed_number`/
#   `safety_er009_changed_actor`)を既定構成でfull flow実行し、floorが
#   引き続き違反文自体をBLOCKING維持する(is_broadcast無効化で安全装置が
#   弱まっていないこと)を確認する。
# Part Safety対照B(Stage2のみ n=1、≤¥1): SAFETY_CRITICAL_CLAIM_DEFSに
#   登録された6 instance(bgroup_B3/safety_A2A3/safety_A4/safety_A5/
#   meta_run03_standard/bgroup_B4、8claim)をStage1(reuse)+Stage2のみ
#   (Rewrite/Recheckサイクルは回さない、cycle=1相当の最小コスト)で実行し、
#   8claimが引き続きBLOCKINGであることを確認する。
#
# 設計制約(既存er052系rep7〜rep19と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜8・rep7〜19の出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜19)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_REP20、本委任でrunner
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
    "(d)是正(floorのfact_id単位broadcast廃止+same_fact_id_locations列挙の"
    "cycle1限定+iol_degenerate guard追加)後、rep19と同一のfrozen fixtureで"
    "Stage4到達0・false PASS 0・cycle<=2・Rewriteは最小単位のみ・見出し"
    "保持・JA/EN等価PASS・費用<¥3/runを期待(委任文§2 B)。"
)

SAFETY_CONTRAST_FULL_FLOW_INSTANCE_IDS = ["safety_er009_changed_number", "safety_er009_changed_actor"]


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
    """Safety12のうちchanged_number/changed_actor各1件をfull flow n=1で
    実行し、違反文自体がfloorでBLOCKING維持されることを確認する(既存
    safety instanceをそのまま使う、新規fixture捏造なし)。"""
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


def run_safety_contrast_b_stage2_only(client, state, consecutive_errors) -> dict:
    """SAFETY_CRITICAL_CLAIM_DEFS(6 instance・8claim)をStage1(reuse)+
    Stage2のみ(cycle=1相当、Rewrite/Recheckサイクルは回さない)で実行し、
    floor修正後も8claimが引き続きBLOCKINGであることを確認する(既存
    run_instance()のcycle=1前半[Stage1 reuse→precheck floor claims→
    llm_claims→run_stage2]と同じ組み立てを、Rewrite以降を省いて再利用する
    だけであり、新しい判定ロジックは作らない)。"""
    rows = []
    call_log: list = []
    for instance_id, defs in runner.SAFETY_CRITICAL_CLAIM_DEFS.items():
        inst = next(i for i in runner.build_target_instances() if i["instance_id"] == instance_id)
        fixture = inst["fixture"]
        stage1_parsed = runner.stage1_reuse(inst["stage1_source"])
        stage1_deviations = [d for d in stage1_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
        existing_fact_ids = {(d.get("related_fact_id") or "") for d in stage1_deviations}
        precheck_claims = runner.build_precheck_floor_claims(fixture, existing_fact_ids)
        llm_claims = [{"claim_text": d.get("claim_in_article", ""), "origin": d.get("origin"),
                       "related_fact_id": d.get("related_fact_id"), "dev": d, "detected_by": "stage1_llm"}
                      for d in stage1_deviations]
        stage2_results = []
        if llm_claims:
            stage2_results = runner.run_stage2(client, state, consecutive_errors, call_log,
                                                f"{instance_id}_safetyB_stage2", fixture, llm_claims)
        for pc in precheck_claims:
            stage2_results.append({**pc, "materiality": "BLOCKING", "llm_materiality": None,
                                    "basis": "precheck_floor", "floor_reason": "precheck_floor"})
        for d in defs:
            match = next((sr for sr in stage2_results
                          if (sr.get("related_fact_id") or "").strip() == d["related_fact_id"]
                          and d["text_substring"] in (sr.get("claim_text") or "")), None)
            rows.append({
                "instance_id": instance_id, "sub_id": d["sub_id"], "related_fact_id": d["related_fact_id"],
                "matched": match is not None,
                "materiality": match.get("materiality") if match else None,
                "llm_materiality": match.get("llm_materiality") if match else None,
                "floor_reason": match.get("floor_reason") if match else None,
                "still_blocking": bool(match) and match.get("materiality") == "BLOCKING",
            })
    cost_jpy = round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4)
    return {"rows": rows, "call_log": call_log, "cost_jpy": cost_jpy}


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    part_b = {"stopped": True, "stop_reason": "not_started"}
    safety_a = {"rows": []}
    safety_b = {"rows": [], "cost_jpy": 0.0}

    try:
        part_b = run_part_b(client, state, consecutive_errors)
        if not part_b.get("stopped"):
            safety_a = run_safety_contrast_a(client, state, consecutive_errors)
            safety_b = run_safety_contrast_b_stage2_only(client, state, consecutive_errors)
    except runner.TrialAbort as e:
        if "stop_reason" not in part_b or part_b.get("stop_reason") in (None, "not_started"):
            part_b["stopped"] = True
            part_b["stop_reason"] = str(e)

    safety_b_still_blocking_count = sum(1 for r in safety_b["rows"] if r["still_blocking"])
    safety_b_total = len(safety_b["rows"])

    summary = {
        "expected": EXPECTED_RESULT,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "part_b": {k: v for k, v in part_b.items() if k != "instance_results"},
        "safety_contrast_a_full_flow": safety_a,
        "safety_contrast_b_stage2_only": {
            "rows": safety_b["rows"], "cost_jpy": safety_b["cost_jpy"],
            "still_blocking_count": safety_b_still_blocking_count, "total": safety_b_total,
            "all_still_blocking": safety_b_still_blocking_count == safety_b_total and safety_b_total > 0,
        },
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep20.json", {
        "summary": summary, "part_b_instance_results": part_b.get("instance_results", []),
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str)[:12000])


if __name__ == "__main__":
    main()
