# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep17_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_31 Part2: rep16の残3点の是正後の
# neg1/neg3再確認)
# ============================================================
# 目的: 委任_31 Part1で反映した3点の是正((a)主体置換ガードを
# problem_kindに関係なく常に評価、(b)Hookセクション境界拡張[締め文を
# 条件付きで含める]+body rubric V5)を使って、`neg1_meta_b3prod_a2`/
# `neg3_hormuz_prodrunner_b1b`の2 instanceをn=2・Stage1 fresh(既存reuse
# fixtureのstage1_modeを本委任限定で明示的に上書き)で再実行する。
#
# 設計制約(既存er052系rep7〜rep16と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜7・rep7〜16の出力(OUT_DIR_ITER1〜7/OUT_DIR_REP7〜16)は
#   変更しない。本ファイルはrunner.OUT_DIR(=OUT_DIR_REP17、本委任でrunner
#   本体に新設済み)のみへ書く。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 2 instanceとも`stage1_mode`を"fresh"へ明示的に上書きする(reuse元の
#   既存Stage1出力は本委任の是正[actor guard/Hook境界/body rubric V5]前の
#   ものであり、本委任の確認目的には使えないため)。stage1_cacheはsample1/
#   sample2間で共有する(既存rep方式と同一、二重課金防止)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

REP17_INSTANCE_IDS = [
    "neg1_meta_b3prod_a2",
    "neg3_hormuz_prodrunner_b1b",
]

EXPECTED_RESULTS = {
    "neg1_meta_b3prod_a2": {
        "expect": "no_rewrite_hook_closing_line_and_users_claim_both",
        "detail": "Hook claim(“Ring, ring...It was a person.”)・Hook締め文"
                   "(“Meta had run a test that caused exactly this surprise.”、"
                   "委任_31 Part1(b)でHook境界へ編入)・users claim(重大誤解"
                   "原則配線後はLEDGER_COMPLIANT、Stage1非検出)の3者とも、"
                   "実記事のcycle1からRewriteなしで完結することを期待。",
    },
    "neg3_hormuz_prodrunner_b1b": {
        "expect": "resolved_with_one_word_or_phrase_edit_no_stage4",
        "detail": "委任_30で是正したpaired_rewrite片側locate委譲により、"
                   "Stage4到達0・1語/短い句の編集水準のみで解消することを"
                   "期待(単体検証で確認済みのguard_ok=Trueがフルフロー内でも"
                   "再現することを確認)。",
    },
}


def _extract_ladder_levels(result: dict) -> list:
    levels = []
    for cycle in result.get("cycles", []):
        for rec in cycle.get("rewrite_records", []):
            levels.append(rec.get("ladder_level_used"))
    return levels


def _extract_hook_stage2_calls(result: dict) -> dict:
    hook_calls = [c for c in result.get("call_log", []) if c.get("stage2_variant") == "hook"]
    body_calls = [c for c in result.get("call_log", []) if c.get("stage2_variant") == "body"]
    local_qa_calls = [c for c in result.get("call_log", []) if c.get("recovery_stage") == "local_qa"]
    recheck_calls = [c for c in result.get("call_log", []) if c.get("recovery_stage") == "stage1_recheck"]
    return {
        "hook_call_count": len(hook_calls),
        "body_call_count": len(body_calls),
        "local_qa_call_count": len(local_qa_calls),
        "stage1_recheck_call_count": len(recheck_calls),
    }


def _extract_stage2_materialities(result: dict) -> list:
    return [
        {"claim_text": sr.get("claim_text"), "materiality": sr.get("materiality"),
         "section_type": sr.get("section_type"), "stage2_route": sr.get("stage2_route"),
         "floor_reason": sr.get("floor_reason")}
        for cycle in result.get("cycles", []) for sr in cycle.get("stage2_results", [])
    ]


def _extract_before_after(result: dict) -> list:
    out = []
    for cycle in result.get("cycles", []):
        before = cycle.get("en_text_before_rewrite")
        after = cycle.get("en_text_after_rewrite")
        ja_before = cycle.get("ja_text_before_rewrite")
        ja_after = cycle.get("ja_text_after_rewrite")
        if before is not None or after is not None or ja_before is not None:
            out.append({
                "cycle": cycle.get("cycle"),
                "en_text_before_rewrite": before, "en_text_after_rewrite": after,
                "ja_text_before_rewrite": ja_before, "ja_text_after_rewrite": ja_after,
            })
    return out


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    for iid in REP17_INSTANCE_IDS:
        assert iid in all_instances, f"unknown instance_id: {iid}"
        all_instances[iid]["stage1_mode"] = "fresh"
        all_instances[iid]["stage1_source"] = None

    stage1_cache: dict = {}
    sample_results: list = []
    stopped, stop_reason = False, None

    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        results = []
        for iid in REP17_INSTANCE_IDS:
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
    for iid in REP17_INSTANCE_IDS:
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
                "call_breakdown": _extract_hook_stage2_calls(r),
                "stage2_materialities": _extract_stage2_materialities(r),
                "before_after_by_cycle": _extract_before_after(r),
            }
        per_case.append(entry)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed_per_sample": [len(r) for r in sample_results],
        "n_instances_planned": len(REP17_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_case": per_case,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep17.json", {
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
