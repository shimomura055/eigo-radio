# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_iter8_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_32: 広いTrial iteration8=重大誤解
# 原則・要素Trial修正の横断安定性確認、2026-10-01、ユーザー承認済み)
# ============================================================
# 目的: 委任_27〜31で反映した重大誤解原則配線(Stage1 V4-A+原則/Stage2 V5/
# Hook V4)・actorガード常時評価・Hook境界拡張の既定構成が、29 instance全量
# (うち9 instanceはn=2、20 instanceはn=1)で横断的に安定して機能するかを
# 確認する(新しい改善案を探すTrialではない)。
#
# 設計制約(既存er052系rep7〜rep17と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜7・rep7〜17の出力(OUT_DIR_ITER1〜7/OUT_DIR_REP7〜17)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_ITER8、本委任でrunner
#   本体に新設済み)のみへ書く。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - Stage1はSafety 12 fixture(`safety_*`)を除く27 instanceで"fresh"へ
#   明示的に上書きする(既存reuse元fixtureは重大誤解原則配線前の出力であり
#   本委任の確認目的には使えないため)。Safety 12 fixtureは
#   build_target_instances()既定のreuseのまま据え置く(Safety-critical
#   adversarial単一claim改変[changed_number等]はfloor/既存safeguardにより
#   principleの有無に関わらずBLOCKING固定が期待される既知ground-truthで
#   あり、Stage1再実行はこの既定構成の確認目的に対して情報を追加しない
#   [原則が効くのはnuanceのある境界判断であって明白な改変の検出可否では
#   ない]。Stage2[body V5/Hook V4、principle-aware]は全instance共通で
#   通常どおり実行されるため、Safety対照群へのRegression確認はStage2以降で
#   担保する)。
# - 9 instance(neg1/neg2/neg3/meta_run03_advanced/meta_run03_standard/
#   hormuz_run03_standard/hormuz_run03_advanced/bgroup_B3/safety_A2A3)は
#   sample1・sample2の2回実行する(stage1_cacheをsample間で共有、Stage1
#   fresh instanceは二重課金しない)。残り20 instanceはsample1のみ。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

N2_INSTANCE_IDS = [
    "neg1_meta_b3prod_a2",
    "neg2_meta_refresh_a2",
    "neg3_hormuz_prodrunner_b1b",
    "meta_run03_advanced",
    "meta_run03_standard",
    "hormuz_run03_standard",
    "hormuz_run03_advanced",
    "bgroup_B3",
    "safety_A2A3",
]


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    instances = runner.build_target_instances()
    assert len(instances) == 29, f"expected 29 instances, got {len(instances)}"
    n2_set = set(N2_INSTANCE_IDS)
    assert n2_set.issubset({inst["instance_id"] for inst in instances})

    for inst in instances:
        if not inst["instance_id"].startswith("safety_"):
            inst["stage1_mode"] = "fresh"
            inst["stage1_source"] = None
        # safety_* instanceはbuild_target_instances()既定のreuseのまま
        # (理由は本ファイル冒頭コメント・REPORT参照)。

    stage1_cache: dict = {}
    stopped, stop_reason = False, None

    sample1_results: list = []
    for inst in instances:
        try:
            result = runner.run_instance(client, state, consecutive_errors, inst, enable_s1u=False,
                                          stage1_cache=stage1_cache, instances_subdir="instances_s1")
            sample1_results.append(result)
        except runner.TrialAbort as e:
            stopped = True
            stop_reason = str(e)
            break

    sample2_results: list = []
    if not stopped:
        n2_instances = [inst for inst in instances if inst["instance_id"] in n2_set]
        for inst in n2_instances:
            try:
                result = runner.run_instance(client, state, consecutive_errors, inst, enable_s1u=False,
                                              stage1_cache=stage1_cache, instances_subdir="instances_s2")
                sample2_results.append(result)
            except runner.TrialAbort as e:
                stopped = True
                stop_reason = str(e)
                break

    measurements = runner.aggregate_measurements(sample1_results) if sample1_results else {}

    sample1_by_id = {r["instance_id"]: r for r in sample1_results}
    sample1_n2_subset = [sample1_by_id[iid] for iid in N2_INSTANCE_IDS if iid in sample1_by_id]

    n2_combined = None
    if (not stopped) and len(sample2_results) == len(N2_INSTANCE_IDS) and len(sample1_n2_subset) == len(N2_INSTANCE_IDS):
        n2_combined = runner.combine_n2_measures([sample1_n2_subset, sample2_results])

    cost_breakdown_5way = runner.compute_cost_breakdown_5way(sample1_results) if sample1_results else {}

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_planned_sample1": len(instances),
        "n_instances_completed_sample1": len(sample1_results),
        "n2_instance_ids_planned": N2_INSTANCE_IDS,
        "n_instances_completed_sample2": len(sample2_results),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "measurements": measurements,
        "cost_breakdown_5way_sample1": cost_breakdown_5way,
        "n2_combined": n2_combined,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_iter8.json", {
        "summary": summary,
        "instance_results_sample1": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample1_results
        ],
        "instance_results_sample2": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample2_results
        ],
    })
    print(json.dumps({k: v for k, v in summary.items() if k not in ("measurements", "n2_combined")},
                      ensure_ascii=True, indent=2))
    print(json.dumps(measurements, ensure_ascii=True, indent=2)[:6000])
    if n2_combined:
        print(json.dumps(n2_combined, ensure_ascii=True, indent=2)[:6000])


if __name__ == "__main__":
    main()
