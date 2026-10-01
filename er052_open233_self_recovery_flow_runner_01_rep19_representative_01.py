# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep19_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_34: meta_run03_standardの人間確認を
# 「Stage1の揺れ」から切り離して検証。広いTrialは含めない)
# ============================================================
# 目的: iter8(委任_32)でmeta_run03_standardが2/2 Stage4になったcycle1の
# Stage1出力(fresh、同一事実の多箇所列挙を含む。s1/s2で完全同一内容、
# stage1_cache共有を実測で確認済み)をそのままreuse入力として固定し、
# 現行既定構成(body rubric V6・actorガード常時評価・局所QA・JA
# fail-open封鎖・escalate_to_paragraph OFF・⑥OFF)の流路が、このStage1
# 検出集合を人間確認なしに解消できるかを検証する。Stage1自体の揺れ
# (cycle1検出内容が run ごとに変わること)は本委任の責任範囲外。
#
# 設計制約(既存er052系rep7〜rep18と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜8・rep7〜18の出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜18)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_REP19、本委任でrunner
#   本体に新設済み)のみへ書く。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - meta_run03_standardの`stage1_mode`を"reuse"へ明示的に上書きし、
#   `stage1_source`をiter8 cycle1の原本2件(enumeration展開前、
#   `same_fact_id_locations`フィールドを保持)のみを抽出したfixture
#   (`stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`)へ
#   差し替える。article_text/ledger_textはbuild_target_instances()既定の
#   まま(g6.step2_fixtures()のMeta_run03_standard、iter8と同一であることを
#   事前に確認済み)。reuse経路のdeterministic_same_fact_id_location_
#   fallbackはフィールド既存時に上書きしない(委任_23 A-2(b)既存ガード)ため、
#   enumeration展開は既存expand_same_fact_id_locations経由でfresh instance
#   と同じ挙動になる。
# - iter8のs1/s2は同一のStage1原本だったため、本rep19ではiter8のsample
#   番号付け(s1/s2)を踏襲し、同一frozen fixtureから独立に2 run実行する。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

FROZEN_STAGE1_SOURCE = (
    f"{runner.OUT_DIR}/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json"
)

EXPECTED_RESULT = (
    "iter8のmeta_run03_standard cycle1 Stage1原本(MUSE-HC-012/MUSE-HC-011、"
    "各same_fact_id_locations付き)を固定入力として、現行既定構成で"
    "Stage4到達0・false PASS 0・JA/EN等価PASSを期待(委任文§2B)。"
)


def _extract_stage2_materialities(result: dict) -> list:
    return [
        {"cycle": cycle.get("cycle"), "claim_text": sr.get("claim_text"),
         "related_fact_id": sr.get("related_fact_id"),
         "materiality": sr.get("materiality"), "llm_materiality": sr.get("llm_materiality"),
         "floor_reason": sr.get("floor_reason"),
         "detected_by_enumeration": sr.get("dev", {}).get("detected_by_enumeration", False)}
        for cycle in result.get("cycles", []) for sr in cycle.get("stage2_results", [])
    ]


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

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

    summary = {
        "expected": EXPECTED_RESULT,
        "stopped": stopped, "stop_reason": stop_reason,
        "n_samples_completed": len(sample_results),
        "n_samples_planned": 2,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_sample": per_sample,
        "safety_critical_misdowngrade_rows": safety_critical_rows,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep19.json", {
        "summary": summary,
        "instance_results": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample_results
        ],
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str)[:8000])


if __name__ == "__main__":
    main()
