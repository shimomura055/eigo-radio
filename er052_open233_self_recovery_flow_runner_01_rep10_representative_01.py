# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep10_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_19: 委任_18の残課題4点の是正+
# 限定再試行rep10)
# ============================================================
# 目的: 委任文§2 Bで指定された7 instance(hormuz_run03_standard/
# neg3_hormuz_prodrunner_b1b/bgroup_B3[因果]/hormuz_run02_advanced
# [scope]/safety_A2A3/safety_A5/safety_er009_changed_number)を、委任_19の
# コード変更(A-1: full_recheck_required条件(f)新設+find_sentence_context
# locateバグ是正、A-2: escalate_to_paragraph)反映後にn=2で再実行する。
# Guardrail¥13(runner.TOTAL_BUDGET_JPY=13.0[委任_19でrunner本体へ設定
# 済み]、超過時TrialAbortで安全停止)。
#
# 設計制約(既存er052系rep7/rep8/rep9と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜6・rep7〜rep9の出力(OUT_DIR_ITER1〜6/OUT_DIR_REP7〜9)は
#   変更しない(本ファイルはrunner.OUT_DIR[=OUT_DIR_REP10、委任_19で
#   runner本体に新設]のみへ書く)。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - hormuz_run02_advancedのみstage1_mode="fresh"(既存instance定義どおり、
#   Stage1プロンプト自体は本委任で変更していない。stage1_cacheをsample1/
#   sample2間で共有するため、fresh call1回で足りる、二重課金なし)。
# - コストが高い順は事前に不明のため、委任文の記載順(優先順位が高い順と
#   解釈)どおりに実行し、Guardrail到達時はその時点までの結果を報告する
#   (rep9と同一の安全な打ち切り方針)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

REP10_INSTANCE_IDS = [
    "hormuz_run03_standard",       # (1) A-2 escalate_to_paragraph実測(cycle枯渇是正の効果測定)
    "neg3_hormuz_prodrunner_b1b",  # (2) A-3の両論併記対象(floor+LLM独立一致)
    "bgroup_B3",                   # (3) 因果("so")、Safety-critical回帰なしの再確認
    "hormuz_run02_advanced",       # (4) scope(HF-009系)、現行Production STOP実例
    "safety_er009_changed_number", # (5) ⑥不発の再確認(委任_18で既に0達成、regression確認)
    "safety_A2A3",                 # (6) 全文Recheck条件が残る側(safety_fixture)で新規BLOCKING継続捕捉
    "safety_A5",                   # (7) 同上
]

EXPECTED_RESULTS = {
    "hormuz_run03_standard": {
        "expect": "improved_or_same_no_regression",
        "detail": "A-2のescalate_to_paragraphにより、同一fact_id(HF-009)の"
                   "cycle枯渇が緩和されるか(段落単位で解消)を測定する。既知の"
                   "限界(見出し/one-line等の別セクションへの分散)がある場合は"
                   "STAGE4のままでも許容範囲(rep9からの悪化がなければ良い)。",
    },
    "neg3_hormuz_prodrunner_b1b": {
        "expect": "resolved_or_stage4_as_before",
        "detail": "floor+LLM独立一致のため解決策は実装していない(rep9と同様の"
                   "挙動を期待、悪化がないことのみ確認)。",
    },
    "bgroup_B3": {
        "expect": "resolved_with_minimal_ladder_no_safety_regression",
        "detail": "①単語水準でBLOCKING→解消、誤降格regressionなしを期待"
                   "(rep8/rep9と同様)。",
    },
    "hormuz_run02_advanced": {
        "expect": "resolved_or_acceptable_no_escalation",
        "detail": "現行Production STOP実例、V4A再判定でBLOCKING→Rewrite→PASSが"
                   "期待到達経路。",
    },
    "safety_er009_changed_number": {
        "expect": "resolved_no_full_article_fallback",
        "detail": "委任_18で達成した「⑥[6_full_article]を経由しない」を"
                   "維持することを期待(regression確認)。",
    },
    "safety_A2A3": {
        "expect": "full_recheck_required_true_safety_fixture",
        "detail": "safety_fixture条件(e)により全文Recheckが維持され、"
                   "disclosure §1-4-5で確認された新規BLOCKING検出能力が"
                   "引き続き機能することを期待。",
    },
    "safety_A5": {
        "expect": "full_recheck_required_true_safety_fixture",
        "detail": "safety_A2A3と同様。",
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
                "local_qa_fastpath_results": cycle.get("local_qa_fastpath_results"),
            })
    return out


def _extract_escalate_to_paragraph_evidence(result: dict) -> list:
    out = []
    for cycle in result.get("cycles", []):
        for rec in cycle.get("rewrite_records", []):
            if rec.get("ladder_level_used") == "4_paragraph":
                out.append({"cycle": cycle.get("cycle"), "claim_identity": rec.get("claim_identity")})
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
    for iid in REP10_INSTANCE_IDS:
        assert iid in all_instances, f"unknown instance_id: {iid}"

    stage1_cache: dict = {}
    sample_results: list = []
    stopped, stop_reason = False, None

    for sample_idx in (1, 2):
        subdir = f"instances_s{sample_idx}"
        results = []
        for iid in REP10_INSTANCE_IDS:
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
    for iid in REP10_INSTANCE_IDS:
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
                "escalate_to_paragraph_evidence": _extract_escalate_to_paragraph_evidence(r),
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
        "n_instances_planned": len(REP10_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "per_case": per_case,
    }
    runner.save_json(f"{runner.OUT_DIR}/summary_rep10.json", {
        "summary": summary,
        "instance_results_sample1": [
            {k: v for k, v in r.items() if k != "call_log"} for r in sample_results[0]
        ] if sample_results else [],
        "instance_results_sample2": (
            [{k: v for k, v in r.items() if k != "call_log"} for r in sample_results[1]]
            if len(sample_results) >= 2 else None
        ),
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str)[:4000])


if __name__ == "__main__":
    main()
