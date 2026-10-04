# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep29a_affected_01.py
# OPEN-233-KPI-RECOVERY-REDESIGN-02 (委任_08 作業4: rep29a = 影響instance限定確認。Step 6(rep29)の前提確認、n=2、1回のみ[問題時のみ同instanceを1回再実行])
# ============================================================
# 対象: safety_er009_changed_scope / safety_er009_unsupported_new_claim / meta_run03_advanced × n=2(計6 run)。
# 構成: rep29と同一(`runner.apply_kpi_trial_switches()`=AG1-strict・構造要素の対渡し・N1′・因果floor known6・S1・L6・prior_issues現行本文・
#       NORMAL群OFF・P+Q/U-2(1)・VS_MATCH_EXT・english_only・V7b・time_only。N3′はOFF)。件数一致の3穴修正はrunner既定で常時有効。
# 即時STOP: JA変更・例外2 instance以上・1 instance-run費用>JPY7。重大見逃し・STAGE4は止めずに完走し記録。Production codeは変更しない。TTSなし。
from __future__ import annotations

import argparse
import collections
import json
import os
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep23_limited_01 as rep23

OUT_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep29a"
BUDGET_STATE = f"{OUT_DIR}/budget_state_c233aw_08_rep29a.json"
IDS = ["safety_er009_changed_scope", "safety_er009_unsupported_new_claim", "meta_run03_advanced"]


def apply_switches(budget_jpy: float) -> dict:
    runner.OUT_DIR = OUT_DIR
    runner.BUDGET_STATE_PATH = BUDGET_STATE
    runner.TOTAL_BUDGET_JPY = budget_jpy
    applied = runner.apply_kpi_trial_switches()
    assert runner.ACTOR_GUARD_MODE == "ag1_strict" and runner.STRUCTURAL_PAIRS_TO_RECHECK is True
    assert runner.STRUCTURAL_ELEMENT_REWRITE is True and runner.RECHECK_MERGE_UNRESOLVED is True
    assert runner.RECHECK_BEFORE_AFTER_PAIRS is False
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
    return applied


def stop_reasons(r: dict) -> list:
    out = [x for x in rep23.immediate_stop_check(r) if x.startswith("a:")]
    if (r.get("total_cost_jpy") or 0) > 7.0:
        out.append(f"cost>7: {r.get('total_cost_jpy')}")
    return out


def run_main(n: int, budget_jpy: float):
    applied = apply_switches(budget_jpy)
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    plan = [(k, iid) for k in range(1, n + 1) for iid in IDS]
    for sample_idx, iid in plan:
        subdir = f"instances_s{sample_idx}"
        path = f"{OUT_DIR}/{subdir}/{iid}.json"
        if os.path.exists(path):
            print(f"[skip existing] {subdir}/{iid}")
            continue
        try:
            r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                    stage1_cache=stage1_cache, instances_subdir=subdir)
        except runner.TrialAbort as e:
            log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
            break
        except Exception as e:  # 例外は記録(再実行しない)。2 instance以上でSTOP
            log["exceptions"].append({"sample": sample_idx, "instance_id": iid, "error": repr(e), "tb": traceback.format_exc()[-1500:]})
            print(f"[EXCEPTION] {subdir}/{iid}: {e!r}")
            if len({x['instance_id'] for x in log["exceptions"]}) >= 2:
                log.update(stopped=True, stop_reason="exceptions in >=2 instances")
                break
            continue
        reasons = stop_reasons(r)
        print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
              f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
        log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                            "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"], "stop_check": reasons})
        if reasons:
            log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:4000])


def _load(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def run_agg():
    rows, ag_rows, st_rows, sc_rows = [], [], [], []
    for s in (1, 2, 3):
        for iid in IDS:
            d = _load(f"{OUT_DIR}/instances_s{s}/{iid}.json")
            if not d:
                continue
            cyc = d.get("cycles", [])
            rap = d.get("residual_at_pass") or {}
            rechecks = sum(1 for c in cyc if c.get("recheck_overall_status") is not None)
            selfc = sum(1 for c in cyc if c.get("recheck_overall_status") == "LEDGER_COMPLIANT" and c.get("recheck_all_prior_issues_resolved") is False)
            confirms = sum(1 for c in cyc if c.get("recheck_confirm_overall_status") is not None)
            rows.append({"sample": s, "instance_id": iid, "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"),
                         "cycles": len(cyc), "cost": d.get("total_cost_jpy"),
                         "ja_changed": any("ja_text_after_rewrite" in c for c in cyc),
                         "rechecks": rechecks, "self_contradictions": selfc, "reverify_calls": confirms,
                         "residual_defs": [(x.get("sub_id"), x.get("remains_in_final_en"), x.get("remains_in_final_en_pattern"),
                                            x.get("pass_with_residual_unflagged"), x.get("pass_with_residual_unflagged_pattern"))
                                           for x in rap.get("defs", [])]})
            for c in cyc:
                for rr in c.get("rewrite_records", []):
                    h = rr.get("handoff") or {}
                    for a in h.get("level_attempts") or []:
                        for dec in a.get("actor_guard_decision") or []:
                            for pc in dec.get("new_classes") or []:
                                ag_rows.append({"sample": s, "iid": iid, "cycle": c["cycle"], "level": a.get("level"), "result": a.get("result"),
                                                "class": pc.get("class"), "new_words": pc.get("new_words"), "ok": pc.get("ok"), "basis": pc.get("basis"),
                                                "related_fact_hits": pc.get("related_fact_hits"), "ledger_hits": pc.get("ledger_hits"),
                                                "issue_named": pc.get("issue_named"), "before": (a.get("targets") or [None])[0],
                                                "after": (a.get("revised") or [None])[0]})
                    if h.get("structural_element_rewrite"):
                        st_rows.append({"sample": s, "iid": iid, "cycle": c["cycle"], "reasons": h["structural_element_rewrite"].get("reasons"),
                                        "level_used": h.get("level_used"), "pair": h.get("structural_pair"),
                                        "attempts": [(a.get("level"), a.get("result")) for a in h.get("level_attempts") or []],
                                        "recheck_structural_pairs_n": c.get("recheck_structural_pairs_n"),
                                        "final_state": d.get("final_state"), "claim_identity": rr.get("claim_identity")})
            inst_list = [d]
            for x in runner.detect_safety_critical_misdowngrades(inst_list):
                sc_rows.append({"sample": s, "iid": iid, "kind": "old", **{k: x.get(k) for k in ("sub_id", "cycle_index", "materiality", "claim_text")}})
            for x in runner.detect_safety_critical_misdowngrades(inst_list, use_pattern=True):
                sc_rows.append({"sample": s, "iid": iid, "kind": "pattern", **{k: x.get(k) for k in ("sub_id", "cycle_index", "materiality", "claim_text")}})
    K = {"n_runs": len(rows), "runs": rows,
         "stage4": [(r["sample"], r["instance_id"], r["stage4_reason"]) for r in rows if r["final_state"] == "STAGE4_ESCALATION"],
         "cost_total_jpy": round(sum(r["cost"] or 0 for r in rows), 4), "cost_worst_run_jpy": max([r["cost"] or 0 for r in rows], default=None),
         "ja_changed_runs": sum(1 for r in rows if r["ja_changed"]),
         "self_contradictions": sum(r["self_contradictions"] for r in rows), "reverify_calls": sum(r["reverify_calls"] for r in rows),
         "actor_guard_decisions": {"n": len(ag_rows), "allowed": sum(1 for r in ag_rows if r["ok"]), "rejected": sum(1 for r in ag_rows if not r["ok"]),
                                   "by_basis": dict(collections.Counter(str(r["basis"]) for r in ag_rows)), "rows": ag_rows},
         "structural_rewrite": st_rows, "safety_critical_rows_old_and_pattern": sc_rows,
         "pass_with_residual_unflagged_old": [(r["sample"], r["instance_id"], x[0]) for r in rows for x in r["residual_defs"] if x[3]],
         "pass_with_residual_unflagged_pattern": [(r["sample"], r["instance_id"], x[0]) for r in rows for x in r["residual_defs"] if x[4]]}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/summary_kpi_01.json", "w", encoding="utf-8") as f:
        json.dump(K, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(K, ensure_ascii=False, indent=1, default=str)[:12000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=8.0)
    ap.add_argument("--instances", default=None, help="委任_09: カンマ区切りで対象instanceを限定(既定=3 instance)")
    ap.add_argument("--out-subdir", default=None, help="委任_09: 出力先をrep29a配下のサブdirへ(例: rerun_01)。予算stateもサブdir内")
    args = ap.parse_args()
    global OUT_DIR, BUDGET_STATE, IDS
    if args.out_subdir:
        OUT_DIR = f"{OUT_DIR}/{args.out_subdir}"
        BUDGET_STATE = f"{OUT_DIR}/budget_state_c233aw_09_rep29a_{args.out_subdir}.json"
    if args.instances:
        IDS = [x for x in args.instances.split(",") if x]
    if args.stage == "agg":
        run_agg()
        return
    run_main(args.n, args.budget_jpy)


if __name__ == "__main__":
    main()
