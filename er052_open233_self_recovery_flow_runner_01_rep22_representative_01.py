# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_42: 受け渡し修正[Checkerの違反範囲を
# そのままRewriteへ渡す、再推測の廃止]の限定Trial)
# ============================================================
# 目的(ユーザー指示§2、2026-10-02): 受け渡し修正後、限定Trialで次を確認する。
#   T1 2文取りこぼし型: meta_run03_standard、固定Stage 1(rep19のfrozen fixture、
#      rep20/rep21と同じ方式・再freezeしない)でn=4。
#   T2 離れた複数箇所型: rep20 sample2 cycle2の状態(記録されたcycle1後のEN本文+
#      JA原文+記録されたcycle2のStage 1/Stage 2出力)を固定入力にして、Stage 3以降
#      (Rewrite→品質/guard→(局所QA or 全文)Recheck)だけを実行する再現(n=2)。
#   T3 Safety対照: rep21と同じchanged_number fixture(`safety_er009_changed_number`)
#      をfull flow n=1(既存の決定論的floorが発火し、誤ってPASSしないこと)。
#
# 設計制約(既存er052系rep7〜rep21と同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - 既存iteration1〜8・rep7〜21の出力は変更しない。本ファイルはrunner.OUT_DIR
#   (=OUT_DIR_REP22、委任_42でrunner本体に新設)のみへ書く。rep19のfrozen fixture・
#   rep20の記録JSONは読み込むのみ。
# - TTSなし。Model Routing Contractは経由しない。API keyは環境変数(.env)のみ。
#
# T2の再現入力の組み方と限界(本Trialの報告にも記載):
# - 入力: rep20 sample2のcycle1記録`en_text_after_rewrite`(cycle1のRewrite後のEN本文)、
#   JA本文(cycle1でJAは変化していない=記録に`ja_text_after_rewrite`なし、fixtureの
#   `source_article_text`をそのまま使用)、cycle2の記録`stage2_results`のうちBLOCKINGの
#   1件(claim_text・origin=ja_source・dev・rewrite_hint・rewrite_kind・materiality等を
#   そのまま使う。Stage 1/Stage 2のLLMは再実行しない)。
# - 実行: `run_stage3_for_claim`(本番と同じ入口)→品質劣化v2/section_role→JAガード→
#   JA/EN等価チェック→`full_recheck_required`→(必要なら)局所QA→全文Recheck(EN+JA)
#   の判定までを、`run_instance`のcycle内ロジックと同じ関数・同じ順序で再現する。
# - 限界: (1)cycle2のStage 1/Stage 2の非決定性は再現しない(記録を固定入力にするため)。
#   (2)cycle3以降(未解消時の追加周回)は再現しない(1周だけ)。(3)`prior_blocking_records`
#   はcycle1のBLOCKING claim由来だが本再現ではcycle2のclaimに対する`repeat_fact_ids`を
#   空として扱う(cycle2のclaimのfact_id[MUSE-HC-012]はcycle1でBLOCKINGだったことが
#   なく、記録上も空と整合)。(4)2周目の入力本文は旧方式のRewrite結果であり、新方式の
#   1周目の結果ではない。
from __future__ import annotations

import argparse
import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

FROZEN_STAGE1_SOURCE = (
    "er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/"
    "meta_run03_standard_iter8_cycle1_frozen.json"
)
REP20_S2_RECORD = (
    "er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json"
)
REP20_S1_RECORD = (
    "er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s1/meta_run03_standard.json"
)
REP21_RECORDS = {
    1: "er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s1/meta_run03_standard.json",
    2: "er052_output/open233_self_recovery_flow_runner_01_rep21/instances_s2/meta_run03_standard.json",
}
SAFETY_CONTRAST_FULL_FLOW_INSTANCE_IDS = ["safety_er009_changed_number"]

EXPECTED_RESULT = (
    "(委任_42 受け渡し修正)後、T1(固定Stage1×n=4): 2文取りこぼし起因のStage 4が0、"
    "Rewrite対象=Checkerの範囲(縮小0)、水準①から開始、段落④・全文⑥を増やさない。"
    "T2(離れた2範囲): 2範囲とも対象になる(間の文は対象外)。T3(Safety対照): floor発火・false PASS 0。"
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


def _base_instance() -> dict:
    base = next(i for i in runner.build_target_instances() if i["instance_id"] == "meta_run03_standard")
    inst = dict(base)
    inst["stage1_mode"] = "reuse"
    inst["stage1_source"] = FROZEN_STAGE1_SOURCE
    return inst


def run_t1(client, state, consecutive_errors, n: int) -> dict:
    inst = _base_instance()
    sample_results: list = []
    stopped, stop_reason = False, None
    for sample_idx in range(1, n + 1):
        subdir = f"instances_s{sample_idx}"
        try:
            result = runner.run_instance(client, state, consecutive_errors, inst, enable_s1u=False,
                                         stage1_cache=None, instances_subdir=subdir)
            sample_results.append(result)
        except runner.TrialAbort as e:
            stopped, stop_reason = True, str(e)
            break
    per_sample = []
    for i, r in enumerate(sample_results, start=1):
        per_sample.append({
            "sample": i, "final_state": r["final_state"], "stage4_reason": r.get("stage4_reason"),
            "num_cycles": len(r.get("cycles", [])), "total_cost_jpy": r["total_cost_jpy"],
            "total_calls": r.get("total_calls"),
            "stage2_materialities": _extract_stage2_materialities(r),
        })
    return {"expected": EXPECTED_RESULT, "stopped": stopped, "stop_reason": stop_reason,
            "n_samples_completed": len(sample_results), "n_samples_planned": n,
            "per_sample": per_sample,
            "safety_critical_misdowngrade_rows": runner.detect_safety_critical_misdowngrades(sample_results)}


def run_t3(client, state, consecutive_errors) -> dict:
    rows = []
    for instance_id in SAFETY_CONTRAST_FULL_FLOW_INSTANCE_IDS:
        inst = next(i for i in runner.build_target_instances() if i["instance_id"] == instance_id)
        try:
            result = runner.run_instance(client, state, consecutive_errors, inst, enable_s1u=False,
                                         stage1_cache=None, instances_subdir="instances_safety_a")
            rows.append({"instance_id": instance_id, "final_state": result["final_state"],
                         "stage4_reason": result.get("stage4_reason"),
                         "total_cost_jpy": result["total_cost_jpy"], "total_calls": result.get("total_calls"),
                         "stage2_materialities": _extract_stage2_materialities(result)})
        except runner.TrialAbort as e:
            rows.append({"instance_id": instance_id, "aborted": True, "stop_reason": str(e)})
            break
    return {"rows": rows}


# ------------------------------------------------------------
# T2: rep20 sample2 cycle2の状態からStage 3以降だけを実行する再現
# ------------------------------------------------------------
def build_t2_inputs() -> dict:
    with open(REP20_S2_RECORD, encoding="utf-8") as f:
        rec = json.load(f)
    c1, c2 = rec["cycles"][0], rec["cycles"][1]
    blocking = [sr for sr in c2["stage2_results"] if sr.get("materiality") == "BLOCKING"]
    assert len(blocking) == 1, f"cycle2のBLOCKINGが1件でない: {len(blocking)}"
    inst = _base_instance()
    fixture = inst["fixture"]
    assert "ja_text_after_rewrite" not in c1  # cycle1でJA本文は変化していない
    return {"fixture": fixture, "en_text": c1["en_text_after_rewrite"],
            "ja_text": fixture["source_article_text"], "claim": blocking[0],
            "recorded_cycle2": {"final_state": rec["final_state"], "stage4_reason": rec["stage4_reason"],
                                "rewrite_records": c2.get("rewrite_records")}}


def run_t2_sample(client, state, consecutive_errors, sample_idx: int) -> dict:
    inp = build_t2_inputs()
    fixture, en_before, ja_before = inp["fixture"], inp["en_text"], inp["ja_text"]
    instance_id = "meta_run03_standard"
    call_log: list = []
    working_fixture = dict(fixture)
    working_fixture["article_text"] = en_before
    working_fixture["source_article_text"] = ja_before
    claim = dict(inp["claim"])
    runner.annotate_claim_span_identity(claim, en_before, ja_before)  # cycle開始時点の確定(周回同一判定用)
    blocking_claims = [claim]
    out = {"sample": sample_idx, "input": {"claim_text": claim["claim_text"], "origin": claim.get("origin"),
                                           "related_fact_id": claim.get("related_fact_id"),
                                           "materiality": claim.get("materiality"),
                                           "span_resolution_cycle_start": claim.get("span_resolution_cycle_start")},
           "recorded_cycle2_old_method": inp["recorded_cycle2"]}
    base_constraint = runner.level_constraint_text(runner.infer_article_level(instance_id))

    def stage3(extra, en_text, ja_text, suffix=""):
        c2 = dict(claim)
        c2["extra_constraint"] = extra
        r = runner.run_stage3_for_claim(client, state, consecutive_errors, call_log,
                                        f"{instance_id}_t2s{sample_idx}_c2{suffix}", working_fixture,
                                        en_text, ja_text, c2)
        rec = {"claim_identity": runner.claim_identity(claim["dev"]), "rewrite_kind": claim["rewrite_kind"],
               "mechanism": r["mechanism"], "method": r["method"], "guard_ok": r["guard_ok"],
               "ladder_level_used": r.get("ladder_level_used"), "section_type": claim.get("section_type"),
               "target_not_locatable": r.get("target_not_locatable", False),
               "ladder_exhausted_without_full_rewrite": r.get("ladder_exhausted_without_full_rewrite", False),
               "span_unverified": r.get("span_unverified", False), "handoff": r.get("handoff")}
        pairs = [{"before": r.get("before_fragment"), "after": r.get("after_fragment")}]
        return r["en_text"], (r["ja_text"] if r["ja_text"] is not None else ja_text), rec, pairs

    en_after, ja_after, rec, pairs = stage3(base_constraint, en_before, ja_before)
    records = [rec]
    out["stage3_first"] = rec
    if rec["target_not_locatable"]:
        out["final_state"], out["stage4_reason"] = "STAGE4_ESCALATION", (
            "violation_span_unverified" if rec["span_unverified"] else "target_not_locatable")
    elif rec["ladder_exhausted_without_full_rewrite"]:
        out["final_state"], out["stage4_reason"] = "STAGE4_ESCALATION", "ladder_exhausted_without_full_rewrite"
    else:
        qd = runner.measure_rewrite_quality_degradation_v2(en_before, en_after, changed_fragments=pairs)
        sr = runner.measure_section_role_violation(en_before, en_after)
        out["quality_degradation_v2"], out["section_role_violation"] = qd, sr
        regenerated = False
        if qd["needs_regeneration"] or sr["section_role_violated"]:
            regenerated = True
            combined = "; ".join(r for r in (qd["reasons"], sr["reasons"]) if r)
            emphasized = base_constraint + runner.REGENERATION_EMPHASIS_TEMPLATE.format(reasons=combined)
            en_after, ja_after, rec2, pairs = stage3(emphasized, en_before, ja_before, "_regen")
            records = [rec2]
            out["stage3_regen"] = rec2
            qd = runner.measure_rewrite_quality_degradation_v2(en_before, en_after, changed_fragments=pairs)
            sr = runner.measure_section_role_violation(en_before, en_after)
        out["regenerated"] = regenerated
        final_sr = sr
        ja_guard = runner.ja_fail_open_guard(ja_before, ja_after, blocking_claims) if ja_after != ja_before else \
            {"ok": True, "violations": [], "checked": False, "indeterminate": False}
        out["ja_fail_open_guard"] = ja_guard
        out["en_text_before"], out["en_text_after"] = en_before, en_after
        out["ja_text_changed"] = ja_after != ja_before
        if final_sr.get("title_degenerate") or final_sr.get("hook_degenerate") or final_sr.get("iol_degenerate"):
            out["final_state"], out["stage4_reason"] = "STAGE4_ESCALATION", "degenerate_rewrite_output"
        elif not records[0]["guard_ok"]:
            out["final_state"], out["stage4_reason"] = "STAGE4_ESCALATION", "ladder_exhausted_without_full_rewrite"
        else:
            eq_verdict = None
            if any(rr["mechanism"].startswith("paired") for rr in records):
                eq = runner.run_ja_en_equivalence_check(client, state, consecutive_errors, call_log,
                                                        f"{instance_id}_t2s{sample_idx}_c2_ja_en_equivalence",
                                                        ja_after, en_after)
                eq_verdict = eq.get("verdict")
                out["ja_en_equivalence_verdict"] = eq_verdict
                out["ja_en_equivalence_reason"] = {k: (eq.get("raw") or {}).get(k) for k in (
                    "notes", "meaning_changes", "important_omissions", "unsupported_additions",
                    "number_name_negation_issues")}
            req, reasons = runner.full_recheck_required(
                records, blocking_claims, instance_id, frozenset(),
                ja_guard_ok=ja_guard["ok"], ja_equivalence_verdict=eq_verdict)
            if not ja_guard["ok"]:
                req, reasons = True, reasons + ["ja_fail_open_guard_violation"]
            if ja_guard.get("indeterminate"):
                req, reasons = True, reasons + ["ja_fail_open_guard_indeterminate"]
            out["full_recheck_required"], out["full_recheck_required_reasons"] = req, reasons
            resolved_by_fastpath = False
            if not req:
                lq = runner.run_local_qa_fastpath(client, state, consecutive_errors, call_log,
                                                  f"{instance_id}_t2s{sample_idx}_c2", working_fixture,
                                                  en_after, blocking_claims, pairs)
                out["local_qa_fastpath_results"], out["local_qa_fastpath_success"] = lq["results"], lq["success"]
                resolved_by_fastpath = lq["success"]
            if resolved_by_fastpath:
                out["final_state"], out["stage4_reason"] = "RESOLVED_REWRITE", None
            else:
                prior_issues = [{"fact_id": claim["dev"].get("related_fact_id", ""),
                                 "claim_in_article": claim.get("claim_span_text") or claim["claim_text"],
                                 "issue": claim["dev"].get("issue", ""),
                                 "explanation": claim["dev"].get("explanation", "")}]
                rf = dict(working_fixture)
                rf["article_text"], rf["source_article_text"] = en_after, ja_after
                rc = runner.run_recheck(client, state, consecutive_errors, call_log,
                                        f"{instance_id}_t2s{sample_idx}_c2_recheck", rf, en_after, prior_issues)
                jrc = None
                if any(rr["mechanism"].startswith("paired") for rr in records):
                    jrc = runner.run_recheck(client, state, consecutive_errors, call_log,
                                             f"{instance_id}_t2s{sample_idx}_c2_ja_recheck", rf, ja_after,
                                             prior_issues)
                en_ok = (rc.get("overall_status") == "LEDGER_COMPLIANT" and rc.get("all_prior_issues_resolved"))
                ja_ok = True if jrc is None else (jrc.get("overall_status") == "LEDGER_COMPLIANT"
                                                  and jrc.get("all_prior_issues_resolved"))
                gating = runner.resolve_ja_ok_after_equivalence_gating(ja_ok, eq_verdict, ja_after)
                ja_ok = gating["ja_ok"]
                if ja_ok and not ja_guard["ok"]:
                    ja_ok = False
                out["recheck_en"] = {"overall_status": rc.get("overall_status"),
                                     "all_prior_issues_resolved": rc.get("all_prior_issues_resolved"),
                                     "deviations": [{"claim_in_article": d.get("claim_in_article"),
                                                     "severity": d.get("severity"),
                                                     "related_fact_id": d.get("related_fact_id"),
                                                     "issue": d.get("issue")} for d in rc.get("deviations", [])]}
                if jrc is not None:
                    out["recheck_ja"] = {"overall_status": jrc.get("overall_status"),
                                         "all_prior_issues_resolved": jrc.get("all_prior_issues_resolved"),
                                         "deviations": [{"claim_in_article": d.get("claim_in_article"),
                                                         "severity": d.get("severity"),
                                                         "related_fact_id": d.get("related_fact_id"),
                                                         "issue": d.get("issue")} for d in jrc.get("deviations", [])]}
                out["en_ok"], out["ja_ok"] = bool(en_ok), bool(ja_ok)
                if en_ok and ja_ok:
                    out["final_state"], out["stage4_reason"] = "RESOLVED_REWRITE", None
                else:
                    out["final_state"] = "UNRESOLVED_AFTER_ONE_CYCLE(次周回=cycle3はこの再現の範囲外)"
                    out["stage4_reason"] = None
    out["rewrite_records"] = records
    out["call_log"] = call_log
    out["total_cost_jpy"] = round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4)
    out["total_calls"] = len(call_log)
    runner.save_json(f"{runner.OUT_DIR}/instances_t2_s{sample_idx}/meta_run03_standard_cycle2_repro.json", out)
    return out


def run_t2(client, state, consecutive_errors, n: int) -> dict:
    results, stopped, stop_reason = [], False, None
    for i in range(1, n + 1):
        try:
            results.append(run_t2_sample(client, state, consecutive_errors, i))
        except runner.TrialAbort as e:
            stopped, stop_reason = True, str(e)
            break
    return {"stopped": stopped, "stop_reason": stop_reason, "n_planned": n,
            "samples": [{k: v for k, v in r.items() if k not in ("call_log", "en_text_before", "en_text_after",
                                                                "recorded_cycle2_old_method")}
                        for r in results]}


# ------------------------------------------------------------
# 集計(API呼び出しなし、記録済みinstance JSONのみ。成功条件1〜5・6の記録値ベース集計)
# ------------------------------------------------------------
def _load(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _records_of(inst_json: dict) -> list:
    """instance JSON(run_instance結果またはT2再現)から(cycle, rewrite_record)のlistを返す。"""
    if "cycles" in inst_json:
        return [(c["cycle"], rr) for c in inst_json["cycles"] for rr in c.get("rewrite_records", [])]
    return [(2, rr) for rr in inst_json.get("rewrite_records", [])]


def summarize_instance(inst_json: dict) -> dict:
    recs = _records_of(inst_json)
    levels: dict = {}
    for _cyc, rr in recs:
        lv = rr.get("ladder_level_used") or "none"
        levels[lv] = levels.get(lv, 0) + 1
    handoffs = [rr.get("handoff") for _c, rr in recs if rr.get("handoff")]
    l1_attempts = [a for h in handoffs for a in h.get("level_attempts", []) if a.get("level") == "1_word_connective"]
    all_attempt_levels = [a.get("level") for h in handoffs for a in h.get("level_attempts", [])]
    first_levels = [(h.get("level_attempts") or [{}])[0].get("level") for h in handoffs if h.get("level_attempts")]
    cycles = inst_json.get("cycles")
    return {
        "final_state": inst_json.get("final_state"), "stage4_reason": inst_json.get("stage4_reason"),
        "n_cycles": len(cycles) if cycles is not None else 1,
        "total_calls": inst_json.get("total_calls"), "total_cost_jpy": inst_json.get("total_cost_jpy"),
        "n_rewrite_records": len(recs), "ladder_level_used_counts": levels,
        "paragraph_level_4_successes": levels.get("4_paragraph", 0),
        "full_article_level_6_successes": levels.get("6_full_article", 0),
        "paragraph_level_4_attempted": sum(1 for lv in all_attempt_levels if lv == "4_paragraph"),
        "n_level1_attempts": len(l1_attempts),
        "n_level1_target_equals_confirmed_ranges": sum(1 for a in l1_attempts if a.get("target_equals_confirmed_ranges")),
        "n_level1_target_mismatch": sum(1 for a in l1_attempts if a.get("target_equals_confirmed_ranges") is False),
        "first_attempted_levels": first_levels,
        "n_span_unverified": sum(1 for _c, rr in recs if rr.get("span_unverified")),
        "n_ja_provisional_path": sum(1 for h in handoffs if h.get("ja_provisional_path")),
        "n_carry_forward_skipped": sum(1 for h in handoffs if h.get("skipped_covered_by_earlier_rewrite")),
        "n_paired_mechanism": sum(1 for _c, rr in recs if str(rr.get("mechanism", "")).startswith("paired")),
    }


def aggregate_rep22() -> dict:
    base = runner.OUT_DIR
    out: dict = {"rep22": {}, "old_method_same_fixed_input": {}}
    for i in range(1, 9):
        r = _load(f"{base}/instances_s{i}/meta_run03_standard.json")
        if r:
            out["rep22"][f"T1_s{i}"] = summarize_instance(r)
    for i in range(1, 5):
        r = _load(f"{base}/instances_t2_s{i}/meta_run03_standard_cycle2_repro.json")
        if r:
            out["rep22"][f"T2_s{i}"] = summarize_instance(r)
    r = _load(f"{base}/instances_safety_a/safety_er009_changed_number.json")
    if r:
        out["rep22"]["T3_safety_changed_number"] = summarize_instance(r)
    r = _load(f"{base}/instances_safety_a_run1_before_carry_forward_fix/safety_er009_changed_number.json")
    if r:
        out["rep22"]["T3_run1_before_carry_forward_fix"] = summarize_instance(r)
    for tag, path in (("rep20_s1", REP20_S1_RECORD), ("rep20_s2", REP20_S2_RECORD),
                      ("rep21_s1", REP21_RECORDS[1]), ("rep21_s2", REP21_RECORDS[2])):
        r = _load(path)
        if r:
            out["old_method_same_fixed_input"][tag] = summarize_instance(r)
    t1 = [v for k, v in out["rep22"].items() if k.startswith("T1_")]
    out["t1_totals"] = {
        "n": len(t1), "stage4_count": sum(1 for v in t1 if v["final_state"] == "STAGE4_ESCALATION"),
        "stage4_reasons": [v["stage4_reason"] for v in t1 if v["final_state"] == "STAGE4_ESCALATION"],
        "span_unverified_total": sum(v["n_span_unverified"] for v in t1),
        "level1_mismatch_total": sum(v["n_level1_target_mismatch"] for v in t1),
        "paragraph_level_4_successes_total": sum(v["paragraph_level_4_successes"] for v in t1),
        "full_article_level_6_total": sum(v["full_article_level_6_successes"] for v in t1),
        "cost_total_jpy": round(sum(v["total_cost_jpy"] or 0 for v in t1), 4),
    }
    allv = [v for k, v in out["rep22"].items() if not k.endswith("before_carry_forward_fix")]
    out["rep22_totals"] = {
        "level1_attempts": sum(v["n_level1_attempts"] for v in allv),
        "level1_target_equals_confirmed_ranges": sum(v["n_level1_target_equals_confirmed_ranges"] for v in allv),
        "level1_target_mismatch": sum(v["n_level1_target_mismatch"] for v in allv),
        "span_unverified_final_runs": sum(v["n_span_unverified"] for v in allv),
        "ja_provisional_path": sum(v["n_ja_provisional_path"] for v in allv),
        "carry_forward_skipped": sum(v["n_carry_forward_skipped"] for v in allv),
        "paragraph_level_4_successes": sum(v["paragraph_level_4_successes"] for v in allv),
        "full_article_level_6": sum(v["full_article_level_6_successes"] for v in allv),
        "cost_total_jpy_all_runs_incl_t3_run1": round(
            sum(v["total_cost_jpy"] or 0 for v in out["rep22"].values()), 4),
    }
    runner.save_json(f"{base}/analysis_rep22.json", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="t3,t1,t2", help="実行する部分(カンマ区切り、t1/t2/t3)")
    ap.add_argument("--t1-n", type=int, default=4)
    ap.add_argument("--t2-n", type=int, default=2)
    args = ap.parse_args()
    parts = [p.strip() for p in args.parts.split(",") if p.strip()]
    if parts == ["agg"]:  # API呼び出しなし。記録済みinstance JSONの集計だけ
        print(json.dumps(aggregate_rep22(), ensure_ascii=False, indent=2, default=str))
        return

    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    summary_path = f"{runner.OUT_DIR}/summary_rep22.json"
    summary = {"expected": EXPECTED_RESULT, "parts": {}}
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)
    try:
        for p in parts:
            if p == "t3":
                summary["parts"]["t3_safety_contrast"] = run_t3(client, state, consecutive_errors)
            elif p == "t1":
                summary["parts"]["t1_two_sentence_miss"] = run_t1(client, state, consecutive_errors, args.t1_n)
            elif p == "t2":
                summary["parts"]["t2_separated_ranges"] = run_t2(client, state, consecutive_errors, args.t2_n)
            else:
                raise SystemExit(f"unknown part {p}")
            summary["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
            summary["cumulative_calls"] = state["cumulative_calls"]
            summary["cumulative_errors"] = state["cumulative_errors"]
            runner.save_json(summary_path, summary)
    except runner.TrialAbort as e:
        summary["aborted"] = str(e)
    summary["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    summary["cumulative_calls"] = state["cumulative_calls"]
    summary["cumulative_errors"] = state["cumulative_errors"]
    runner.save_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str)[:12000])


if __name__ == "__main__":
    main()
