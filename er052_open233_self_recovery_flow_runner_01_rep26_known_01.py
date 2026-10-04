# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep26_known_01.py
# OPEN-233-KPI-RECOVERY-REDESIGN-02 (委任_02 作業5: Step 5 既知caseの限定確認 rep26、n=2固定)
# ============================================================
# rep25_affected_01を複製し、(1)instance集合を既知case 4件(bgroup_B3 / safety_A2A3 / neg5_hormuz_div_a2[B3同一文] /
# neg3_hormuz_prodrunner_b1b[不要Rewriteの監視])へ、(2)スイッチを`runner.apply_kpi_trial_switches()`(KPI確認構成:
# HANDOFF_MODE=violation_span・VS_MATCH_EXT・VS_EXPLAIN_SPLIT[Q/U-2(1)含む]・VS_SENTENCE_RESTORE[L6]・JA_MODE=english_only・
# FLOOR_VERIFY_MODE=time_only・STAGE2_NORMAL_TWO_OF_TWO=OFF・**STAGE2_DOWNGRADE_VERIFY=ON**)へ変更した。runner本体は変更しない。
# 【委任_04で更新・実行】確認役(STAGE2_DOWNGRADE_VERIFY)は不採用でOFF。KPI_TRIAL_SWITCHES=Tier 0因果floor(known6+issue_actor)+
# Tier 1' S1第2意見+Tier 2 hint+L6+prior_issues現行本文化+NORMAL群2-of-2 OFF+Q/U-2(1)+VS_MATCH_EXT+english_only+V7b+time_only floor_verify。
# Production codeは変更しない。出力はOUT_DIR_REP26のみ。
# 即時STOP: 日本語変更・floor_verify解放・Safety-critical残存・STAGE4(Human Review)・例外・TrialAbort。再実行・n増しはしない。
# 集計(--stage agg)は本ファイル内(API呼び出しなし、記録済みinstance JSONのみ)。
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep23_limited_01 as rep23

OUT_DIR_REP26 = "er052_output/open233_self_recovery_flow_runner_01_rep26"
BUDGET_STATE_REP26 = f"{OUT_DIR_REP26}/budget_state_c233au_02_rep26.json"
REP24_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep24"
REP25_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep25"
INSTANCE_IDS = ["bgroup_B3", "safety_A2A3", "neg5_hormuz_div_a2", "neg3_hormuz_prodrunner_b1b"]
# 旧定義(委任_01まで)のSafety-critical sub_id。新定義(登録済み+自動導出)は`runner.safety_critical_dual_summary`。
SAFETY_CRITICAL_IDS = {"bgroup_B3": "B3", "safety_A2A3": "A2A3-0", "neg5_hormuz_div_a2": "B3-same@neg5"}


def apply_switches(budget_jpy: float) -> dict:
    runner.OUT_DIR = OUT_DIR_REP26
    runner.BUDGET_STATE_PATH = BUDGET_STATE_REP26
    runner.TOTAL_BUDGET_JPY = budget_jpy
    applied = runner.apply_kpi_trial_switches()
    assert runner.STAGE2_DOWNGRADE_VERIFY is False and runner.TIER0_G_L_ENABLED is False
    assert runner.CAUSAL_FLOOR is True and runner.CAUSAL_FLOOR_VOCAB == "known6" and runner.STAGE2_SECOND_OPINION is True
    assert runner.STAGE2_NORMAL_TWO_OF_TWO is False and runner.VS_SENTENCE_RESTORE is True
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
    return applied


def stop_check(r: dict) -> list:
    reasons = list(rep23.immediate_stop_check(r))
    if r.get("final_state") == "STAGE4_ESCALATION":
        reasons.append(f"STAGE4(Human Review): {r.get('stage4_reason')}")
    return reasons


def run_main(n, budget_jpy):
    applied = apply_switches(budget_jpy)
    os.makedirs(OUT_DIR_REP26, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    for sample_idx in range(1, n + 1):
        subdir = f"instances_s{sample_idx}"
        for iid in INSTANCE_IDS:
            path = f"{OUT_DIR_REP26}/{subdir}/{iid}.json"
            if os.path.exists(path):
                print(f"[skip existing] {subdir}/{iid}")
                continue
            try:
                r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                        stage1_cache=stage1_cache, instances_subdir=subdir)
            except runner.TrialAbort as e:
                log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
                break
            except Exception as e:  # 例外は即STOP(再実行しない)
                log["exceptions"].append({"sample": sample_idx, "instance_id": iid, "error": repr(e),
                                          "tb": traceback.format_exc()[-1500:]})
                log.update(stopped=True, stop_reason=f"exception: {e!r}")
                print(f"[EXCEPTION] {subdir}/{iid}: {e!r}")
                break
            reasons = stop_check(r)
            print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
                  f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
            log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                                "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"], "stop_check": reasons})
            if reasons:
                log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
                break
        if log["stopped"]:
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR_REP26}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:6000])


# ---------------------------------------------------------------- 集計(API呼び出しなし)
def _load(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _stage2_rows(d):
    for c in d.get("cycles", []):
        for sr in c.get("stage2_results", []):
            yield c.get("cycle"), sr


def _baseline_costs(dirpath, iid):
    costs = []
    for f in glob.glob(f"{dirpath}/instances_s*/{iid}.json"):
        d = _load(f)
        if d:
            costs.append(d.get("total_cost_jpy") or 0.0)
    return costs


def run_agg():
    runs = []
    for s in (1, 2):
        for iid in INSTANCE_IDS:
            d = _load(f"{OUT_DIR_REP26}/instances_s{s}/{iid}.json")
            if d:
                runs.append((s, iid, d))
    S = {"n_runs": len(runs), "instances": INSTANCE_IDS, "per_run": []}
    for s, iid, d in runs:
        cycles = d.get("cycles", [])
        rap = d.get("residual_at_pass") or {}
        dv_rows = [(cy, sr) for cy, sr in _stage2_rows(d) if sr.get("downgrade_verify")]
        dv_target = [(cy, sr) for cy, sr in dv_rows if sr["downgrade_verify"]["target"]]
        dv_blocked = [(cy, sr) for cy, sr in dv_target if sr["downgrade_verify"]["blocking"]]
        # 解除不可claimのRewrite解消: 当該instanceがpass系の最終状態で終わったか、cycle数
        resolved = d.get("final_state") in runner.PASS_FINAL_STATES
        ja_changed = any("ja_text_after_rewrite" in c for c in cycles)
        ja_calls = [cl.get("label") for cl in d.get("call_log", []) if "ja_" in str(cl.get("label", ""))]
        dvs = runner.downgrade_verify_summarize(sr for _cy, sr in _stage2_rows(d))
        S["per_run"].append({
            "sample": s, "instance_id": iid, "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"),
            "is_stage4": d.get("final_state") == "STAGE4_ESCALATION", "cost_jpy": d.get("total_cost_jpy"),
            "n_cycles": len(cycles), "n_rewrite_records": sum(len(c.get("rewrite_records") or []) for c in cycles),
            "downgrade_verify": dvs,
            "dv_blocked_claims": [{"cycle": cy, "reason": sr["downgrade_verify"]["blocking_reason"],
                                   "hint_source": sr["downgrade_verify"]["hint_source"],
                                   "claim": (sr.get("claim_text") or "")[:140]} for cy, sr in dv_blocked],
            "dv_released_claims": [{"cycle": cy, "claim": (sr.get("claim_text") or "")[:140],
                                    "citation": ((sr["downgrade_verify"].get("call") or {}).get("ledger_citation") or "")[:120],
                                    "citation_verbatim": (sr["downgrade_verify"].get("call") or {}).get("citation_verbatim")}
                                   for cy, sr in dv_target if sr["downgrade_verify"]["released"]],
            "unblocked_by_rewrite_final_pass": bool(dv_blocked) and resolved,
            "section_type_mismatch": [{"cycle": cy, "section_type": sr.get("section_type"),
                                       "observed": sr.get("section_type_observed")} for cy, sr in _stage2_rows(d)
                                      if sr.get("section_type_observed") != sr.get("section_type")],
            "residual_at_pass": {"final_state_is_pass_family": rap.get("final_state_is_pass_family"), "defs": rap.get("defs")},
            "pass_with_residual_unflagged": [x.get("sub_id") for x in rap.get("defs", []) if x.get("pass_with_residual_unflagged")],
            "ja_changed": ja_changed, "ja_labelled_calls": ja_calls, "switches": d.get("switches"),
            "unresolved_reasons": [(rr.get("handoff") or {}).get("span_unverified_reason")
                                   for c in cycles for rr in (c.get("rewrite_records") or [])
                                   if (rr.get("handoff") or {}).get("span_unverified")],
        })
    inst_runs = [d for _s, _i, d in runs]
    S["downgrade_verify_total"] = runner.downgrade_verify_summarize(sr for d in inst_runs for _cy, sr in _stage2_rows(d))
    S["sentence_restore_summary"] = runner.sentence_restore_summarize(inst_runs)
    S["tier0"] = runner.tier0_summarize(inst_runs)
    S["s1_second_opinion"] = runner.s1_summarize(inst_runs)
    S["stage4_count"] = sum(1 for m in S["per_run"] if m["is_stage4"])
    S["stage4_by_reason"] = dict(collections.Counter(m["stage4_reason"] for m in S["per_run"] if m["is_stage4"]))
    S["cost_total_jpy"] = round(sum(m["cost_jpy"] or 0 for m in S["per_run"]), 4)
    S["ja_changed_total"] = sum(1 for m in S["per_run"] if m["ja_changed"])
    S["pass_with_residual_unflagged_total"] = sum(len(m["pass_with_residual_unflagged"]) for m in S["per_run"])
    S["safety_critical_dual"] = runner.safety_critical_dual_summary(inst_runs)
    S["safety_critical_registered_rows"] = runner.detect_safety_critical_misdowngrades(inst_runs)
    # 費用: rep24・rep25の同instance比(1記事あたり、実測)
    cmp_rows = []
    for iid in INSTANCE_IDS:
        mine = [m["cost_jpy"] or 0.0 for m in S["per_run"] if m["instance_id"] == iid]
        b24 = _baseline_costs(REP24_DIR, iid)
        b25 = _baseline_costs(REP25_DIR, iid)
        mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None
        cmp_rows.append({"instance_id": iid, "rep26_mean": mean(mine), "rep26_n": len(mine), "rep24_mean": mean(b24),
                         "rep24_n": len(b24), "rep25_mean": mean(b25), "rep25_n": len(b25),
                         "diff_vs_rep24": (round(mean(mine) - mean(b24), 4) if mine and b24 else None),
                         "diff_vs_rep25": (round(mean(mine) - mean(b25), 4) if mine and b25 else None)})
    S["cost_vs_baselines"] = cmp_rows
    d24 = [r["diff_vs_rep24"] for r in cmp_rows if r["diff_vs_rep24"] is not None]
    S["cost_diff_per_article_vs_rep24_mean_of_instances"] = round(sum(d24) / len(d24), 4) if d24 else None
    # 不要Rewrite(neg3=不要、neg5=B3同一文なので必要)
    S["unnecessary_rewrite_neg3_runs"] = sum(1 for m in S["per_run"] if m["instance_id"].startswith("neg3") and m["n_rewrite_records"] > 0)
    os.makedirs(OUT_DIR_REP26, exist_ok=True)
    with open(f"{OUT_DIR_REP26}/summary_01.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    md = ["# summary_01.md (rep26、委任_04)", "",
          f"n instance-run={S['n_runs']} cost=JPY{S['cost_total_jpy']}",
          f"STAGE4={S['stage4_count']} {S['stage4_by_reason']} / pass_with_residual_unflagged={S['pass_with_residual_unflagged_total']} / "
          f"ja_changed={S['ja_changed_total']}",
          f"Tier0: {json.dumps(S['tier0'], ensure_ascii=False)}",
          f"S1: {json.dumps(S['s1_second_opinion'], ensure_ascii=False)}",
          f"Safety-critical旧/新: {json.dumps({k: v for k, v in S['safety_critical_dual'].items() if k != 'new_definition_detail'}, ensure_ascii=False)}",
          f"L6集計: {json.dumps(S['sentence_restore_summary'], ensure_ascii=False)}",
          f"費用vs rep24/rep25: {json.dumps(S['cost_vs_baselines'], ensure_ascii=False)}", "", "## per run", ""]
    for m in S["per_run"]:
        md.append(f"- s{m['sample']} {m['instance_id']}: {m['final_state']} s4={m['stage4_reason']} JPY{m['cost_jpy']} cycles={m['n_cycles']} "
                  f"rewrite_records={m['n_rewrite_records']} dv={json.dumps(m['downgrade_verify'], ensure_ascii=False)}")
        for b in m["dv_blocked_claims"]:
            md.append(f"  - BLOCKED(c{b['cycle']}) {b['reason']} hint={b['hint_source']}: {b['claim']}")
        for b in m["dv_released_claims"]:
            md.append(f"  - RELEASED(c{b['cycle']}) verbatim={b['citation_verbatim']}: {b['claim']} | cite: {b['citation']}")
    with open(f"{OUT_DIR_REP26}/summary_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({k: S[k] for k in ("n_runs", "stage4_count", "stage4_by_reason", "cost_total_jpy", "pass_with_residual_unflagged_total",
                                         "ja_changed_total", "tier0", "s1_second_opinion", "sentence_restore_summary",
                                         "cost_diff_per_article_vs_rep24_mean_of_instances", "unnecessary_rewrite_neg3_runs")},
                     ensure_ascii=True, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=8.0)
    args = ap.parse_args()
    if args.stage == "agg":
        run_agg()
        return
    if args.n != 2:
        raise SystemExit("n=2固定(委任_02)")
    run_main(args.n, args.budget_jpy)


if __name__ == "__main__":
    main()
