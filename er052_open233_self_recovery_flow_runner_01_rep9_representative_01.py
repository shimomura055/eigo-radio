# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep9_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_18: 局所QA統合/全体Rewrite経路是正/
# 不要Rewrite4件の解決策/Escalation 2 run是正+代表ケース拡張Trial)
# ============================================================
# 目的: 委任文§3で指定された代表12 instance(neg1 Meta hook/bgroup_B3
# [丸め+因果]/hormuz_run03_standard[scope]/safety_er009_changed_actor・
# changed_number/neg2_meta_refresh_a2/meta_run03_advanced/
# neg3_hormuz_prodrunner_b1b/meta_run03_standard/
# safety_er009_unsupported_new_claim/safety_A2A3/safety_A5)を、委任_18の
# コード変更(2-1精緻化ロケータ+target_not_locatable+degenerate guard、
# 2-2 disclosure-gap downgrade、2-3(b) fact_id複数箇所cycle緩和、2-4局所QA
# fastpath)反映後にn=2で再実行する(29 instance全量の再実行は本委任
# スコープ外、Guardrail¥20内で確認する)。
#
# 重要な設計制約(既存er052系rep7/rep8と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜6・rep7・rep8の出力(OUT_DIR_ITER1〜6/OUT_DIR_REP7/
#   OUT_DIR_REP8)は変更しない(本ファイルはrunner.OUT_DIR[=OUT_DIR_REP9、
#   委任_18でrunner本体に新設]のみへ書く)。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - meta_run03_advanced以外の11 instanceはstage1_mode="reuse"(既存V4A
#   artifact再利用、¥0)。meta_run03_advancedのみstage1_mode="fresh"
#   (既存instance定義どおり、Stage1プロンプト自体は委任_18で変更して
#   いない。stage1_cacheをsample1/sample2間で共有するため、fresh call
#   1回[約¥0.3]で足りる、二重課金なし)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

REP9_INSTANCE_IDS = [
    "neg1_meta_b3prod_a2",              # (1) neg1 Meta hook
    "bgroup_B3",                        # (2)+(3) B3丸め+B3因果
    "hormuz_run03_standard",            # (4) Hormuz scope(HF-009 changed_scope)
    "safety_er009_changed_actor",       # (5) Safety changed_actor(floor維持)
    "safety_er009_changed_number",      # (5) Safety changed_number(⑥へ行かず解消を期待)
    "neg2_meta_refresh_a2",             # (6) neg2(disclosure-gap downgrade期待)
    "meta_run03_advanced",              # (7) meta_run03_advanced(disclosure-gap downgrade期待)
    "neg3_hormuz_prodrunner_b1b",       # (8) neg3(floor+LLM独立一致、解消策なし・確認のみ)
    "meta_run03_standard",              # (9) meta_run03_standard(Escalation 0を期待)
    "safety_er009_unsupported_new_claim",  # (10) タイトル空文字ガード
    "safety_A2A3",                      # (11) 全文Recheckが新規BLOCKINGを検出した実例1
    "safety_A5",                        # (11) 全文Recheckが新規BLOCKINGを検出した実例2
]

# 委任文§3の期待結果(事前固定、機械判定用)。
EXPECTED_RESULTS = {
    "neg1_meta_b3prod_a2": {
        "expect": "no_rewrite_or_quality_pass_no_escalation",
        "detail": "Hook専用StageでQUALITY/ACCEPTABLE、STAGE4_ESCALATIONに"
                   "至らないことを期待(委任_16/17ではcycle上限3回まで"
                   "Rewriteしても解消せずSTAGE4だった)",
    },
    "bgroup_B3": {
        "expect": "resolved_with_minimal_ladder",
        "detail": "body経路(既存R3''')でBLOCKING維持→①語で解消、"
                   "In one line語数+30%以内を期待",
    },
    "hormuz_run03_standard": {
        "expect": "resolved_minimal_scope_narrow",
        "detail": "narrow_scopeを最小変更で解消、A2語彙内を期待",
    },
    "safety_er009_changed_actor": {
        "expect": "blocking_then_resolved_no_full_article",
        "detail": "floor維持->解消、ladder_level_usedが6_full_articleに"
                   "ならないことを期待(2-1(a)のprecheck実文解決)",
    },
    "safety_er009_changed_number": {
        "expect": "blocking_then_resolved_no_full_article",
        "detail": "floor維持->解消、ladder_level_usedが6_full_articleに"
                   "ならないことを期待(2-1(a)のprecheck実文解決、"
                   "disclosure §1-1-2の根本原因是正)",
    },
    "neg2_meta_refresh_a2": {
        "expect": "no_rewrite_or_quality_downgrade",
        "detail": "disclosure_gap_negative_inference_downgradeでQUALITYへ"
                   "downgradeされRewriteなしを期待(2-2)",
    },
    "meta_run03_advanced": {
        "expect": "no_rewrite_or_quality_downgrade",
        "detail": "neg2と同一MUSE-HC-012パターン、同様にdowngradeを期待",
    },
    "neg3_hormuz_prodrunner_b1b": {
        "expect": "blocking_then_resolved_or_escalation",
        "detail": "disclosure §1-2-4で解決策なしと整理済み、floor維持の"
                   "まま従来どおりRewrite試行される想定(確認のみ、"
                   "解消策の実装なし)",
    },
    "meta_run03_standard": {
        "expect": "no_escalation",
        "detail": "sample1[J-1被フラグ文不変→次段]・sample2[fact_id複数"
                   "箇所→cycle緩和]の両方でSTAGE4_ESCALATIONに至らない"
                   "ことを期待(2-3(a)(b))",
    },
    "safety_er009_unsupported_new_claim": {
        "expect": "resolved_no_degenerate_title",
        "detail": "タイトルが空文字・極端短縮にならず解消することを期待"
                   "(2-1(c)、disclosure §1-1-3/§1-1-4のsample1型再発なし)",
    },
    "safety_A2A3": {
        "expect": "resolved_full_recheck_still_required",
        "detail": "Safety fixtureのためfull_recheck_required=Trueで局所QA "
                   "fastpathを使わず既存の全文Recheckが引き続き機能する"
                   "ことを期待(disclosure §1-4-5で新規BLOCKING検出実績あり)",
    },
    "safety_A5": {
        "expect": "resolved_full_recheck_still_required",
        "detail": "safety_A2A3と同様、Safety fixtureのため全文Recheckが"
                   "維持されることを期待",
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


def _extract_local_qa_fastpath_evidence(result: dict) -> list:
    out = []
    for cycle in result.get("cycles", []):
        if cycle.get("local_qa_fastpath_attempted") is not None:
            out.append({
                "cycle": cycle.get("cycle"),
                "full_recheck_required": cycle.get("full_recheck_required"),
                "full_recheck_required_reasons": cycle.get("full_recheck_required_reasons"),
                "local_qa_fastpath_attempted": cycle.get("local_qa_fastpath_attempted"),
                "local_qa_fastpath_success": cycle.get("local_qa_fastpath_success"),
            })
    return out


def _extract_disclosure_gap_evidence(result: dict) -> list:
    out = []
    for cycle in result.get("cycles", []):
        for sr in cycle.get("stage2_results", []):
            if sr.get("floor_reason") == "disclosure_gap_negative_inference_downgrade(委任_18 2-2)":
                out.append({"claim_text": sr.get("claim_text"), "llm_materiality": sr.get("llm_materiality"),
                             "materiality": sr.get("materiality")})
    return out


def _extract_hook_stage2_calls(result: dict) -> dict:
    hook_calls = [c for c in result.get("call_log", []) if c.get("stage2_variant") == "hook"]
    body_calls = [c for c in result.get("call_log", []) if c.get("stage2_variant") == "body"]
    local_qa_calls = [c for c in result.get("call_log", []) if c.get("recovery_stage") == "local_qa"]
    recheck_calls = [c for c in result.get("call_log", []) if c.get("recovery_stage") == "stage1_recheck"]
    return {
        "hook_call_count": len(hook_calls),
        "hook_total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in hook_calls), 4),
        "body_call_count": len(body_calls),
        "body_total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in body_calls), 4),
        "local_qa_call_count": len(local_qa_calls),
        "local_qa_total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in local_qa_calls), 4),
        "stage1_recheck_call_count": len(recheck_calls),
        "stage1_recheck_total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in recheck_calls), 4),
    }


def main():
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    for iid in REP9_INSTANCE_IDS:
        assert iid in all_instances, f"unknown instance_id: {iid}"

    stage1_cache: dict = {}
    sample_results: list = []  # [[sample1の12件], [sample2の12件]]
    stopped, stop_reason = False, None

    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        results = []
        for iid in REP9_INSTANCE_IDS:
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
    for iid in REP9_INSTANCE_IDS:
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
                "local_qa_fastpath_evidence": _extract_local_qa_fastpath_evidence(r),
                "disclosure_gap_downgrade_evidence": _extract_disclosure_gap_evidence(r),
                "call_breakdown": _extract_hook_stage2_calls(r),
                "stage2_materialities": [
                    {"claim_text": sr.get("claim_text"), "materiality": sr.get("materiality"),
                     "section_type": sr.get("section_type"), "stage2_route": sr.get("stage2_route"),
                     "floor_reason": sr.get("floor_reason")}
                    for cycle in r.get("cycles", []) for sr in cycle.get("stage2_results", [])
                ],
            }
        per_case.append(entry)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed_per_sample": [len(r) for r in sample_results],
        "n_instances_planned": len(REP9_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_case": per_case,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep9.json", {
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
