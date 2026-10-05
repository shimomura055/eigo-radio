# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_stage1_stageA_01.py
# OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_06 作業5: 段階A(有料)スクリプト。**作成のみ・未実行**(実行は別委任でFable/ユーザー判断後)。
# Stage 1(coverage_union、`STAGE1_ROUTES=both`)だけをfresh実行し、1 runで3'-R・5-lite両経路の出力を保存する(集計で経路別/∪を分離)。
# Stage 2以降は実行しない(段階A=Stage 1の検出力・非決定性・欠落ID・費用の測定。E2Eは後続段階)。
# 対象: 正式SC 6 instance + B2_hormuz(監視) + 負例/NORMAL 6 をn=3、er009合成9種をhold-out n=1。実行順はsample-major(途中停止でもnが揃う)。
# 事前固定の採用基準(結果を見て変えない): (1)正式SC 6件が全てunion 3/3 (2)hold-out新規見逃し0(=union候補0のinstanceが無い)
#   (3)欠落ID残存率<=5%(再実行後)。基準はそのまま機械判定して出力するだけで、Production採用・Stage 1置換の判断ではない。
# 使い方: --stage estimate(¥0、費用概算) / --stage main --yes-run-paid(有料、既定予算JPY65) / --stage agg(¥0、保存済みrunの集計)
# Trial専用。Production未配線・`APPROVED_FOR_PRODUCTION`ではない。再実行・n増しはしない(既存run jsonがあればskip)。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov

OUT_DIR_A = "er052_output/open233_stage1_stageA_01"
BUDGET_STATE_A = f"{OUT_DIR_A}/budget_state_stage1_stageA_01.json"
SC_IDS = ["bgroup_B3", "safety_A2A3", "safety_A4", "safety_A5", "bgroup_B4", "neg5_hormuz_div_a2"]
WATCH_IDS = ["bgroup_B2_hormuz"]
NORMAL_IDS = ["neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b", "neg4_smallbag_div_a2",
              "neg6_smallbag_div_b1b", "neg7_meta_prodrunner_b1b"]
HOLDOUT_IDS = ["safety_er009_changed_number", "safety_er009_changed_actor", "safety_er009_changed_scope",
               "safety_er009_changed_causality", "safety_er009_changed_certainty", "safety_er009_changed_negation",
               "safety_er009_changed_comparison", "safety_er009_changed_time", "safety_er009_unsupported_new_claim"]
N_MAIN, N_HOLDOUT = 3, 1
PER_RUN_COST_STOP_JPY = 6.0
CRITERIA = {"sc_union_detect_per_instance": "3/3", "holdout_new_miss_max": 0, "missing_id_residual_max": 0.05}


def plan() -> list:
    """[(sample, instance_id)]。sample-major: sample1に全instance(hold-out含む)、sample2/3はn=3対象のみ。"""
    main_ids = SC_IDS + WATCH_IDS + NORMAL_IDS
    out = [(1, i) for i in main_ids + HOLDOUT_IDS]
    for s in range(2, N_MAIN + 1):
        out += [(s, i) for i in main_ids]
    return out


# ---- 費用概算(¥0): 入力トークン=prompt文字数x0.66(rep30のV4A Stage 1実測 6,719token/10,188字から較正)、出力=推論+可視出力の仮定 ----
TOK_PER_CHAR = 0.66
# (推論token low/mid/high, 可視出力: R3=判定単位x130token、R5=fact x35 + 単位x0.8x90)
REASON = {"r3": (3000, 6000, 10000), "r5": (3000, 5000, 8000)}


def estimate_cost(instances: dict, plan_rows: list) -> dict:
    from er052_open233_self_recovery_stage2_production_01 import official_cost_jpy
    rows, tot = {}, [0.0, 0.0, 0.0]
    cache = {}
    for _, iid in plan_rows:
        if iid not in cache:
            fx = instances[iid]["fixture"]
            sp = cov.split_units(fx["article_text"], runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)
            blocks = cov.ledger_fact_blocks(fx["ledger_text"])
            p3 = len(cov.build_r3_prompt(fx["ledger_text"], sp["units"], sp["judged_ids"]))
            p5 = len(cov.build_r5_prompt(fx["ledger_text"], sp["units"], list(blocks)))
            nj, nf = len(sp["judged_ids"]), len(blocks)
            est = []
            for k in range(3):
                c3 = official_cost_jpy({"input_tokens": int(p3 * TOK_PER_CHAR), "output_tokens": REASON["r3"][k] + nj * 130})
                c5 = official_cost_jpy({"input_tokens": int(p5 * TOK_PER_CHAR),
                                        "output_tokens": REASON["r5"][k] + nf * 35 + int(nj * 0.8 * 90)})
                est.append(c3 + c5)
            cache[iid] = est
        for k in range(3):
            tot[k] += cache[iid][k]
    return {"per_instance_run_jpy_low_mid_high": {k: [round(x, 3) for x in v] for k, v in cache.items()},
            "n_runs": len(plan_rows), "total_jpy_low_mid_high": [round(x, 2) for x in tot]}


# ---- 有料実行(--stage main --yes-run-paid のときだけ) ----
def apply_switches(budget_jpy: float) -> dict:
    runner.OUT_DIR = OUT_DIR_A
    runner.BUDGET_STATE_PATH = BUDGET_STATE_A
    runner.TOTAL_BUDGET_JPY = budget_jpy
    runner.STAGE1_MODE = runner.STAGE1_MODE_COVERAGE_UNION
    runner.STAGE1_ROUTES = "both"  # 1 runで両経路を保存(集計で経路別/∪を分離)
    assert runner.MODEL == "gpt-6-luna"
    return {"STAGE1_MODE": runner.STAGE1_MODE, "STAGE1_ROUTES": runner.STAGE1_ROUTES, "MODEL": runner.MODEL,
            "TOTAL_BUDGET_JPY": budget_jpy}


def run_main(budget_jpy: float) -> None:
    applied = apply_switches(budget_jpy)
    os.makedirs(OUT_DIR_A, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    ce = [0]
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    for sample, iid in plan():
        path = f"{OUT_DIR_A}/runs/s{sample}/{iid}.json"
        if os.path.exists(path):
            print(f"[skip existing] s{sample}/{iid}")
            continue
        call_log: list = []
        try:
            parsed = runner.stage1_coverage_fresh(client, state, ce, call_log, f"{iid}_s{sample}_stage1", insts[iid]["fixture"])
        except runner.TrialAbort as e:
            log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
            break
        except Exception as e:  # 例外は記録(再実行しない)。2 instance以上でSTOP
            log["exceptions"].append({"sample": sample, "instance_id": iid, "error": repr(e), "tb": traceback.format_exc()[-1500:]})
            if len({x["instance_id"] for x in log["exceptions"]}) >= 2:
                log.update(stopped=True, stop_reason="exceptions in >=2 instances")
                break
            continue
        cost = round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4)
        runner.save_json(path, {"sample": sample, "instance_id": iid, "group": insts[iid]["group"],
                                "api_failure": bool(parsed.get("_stage1_api_failure")),
                                "audit": parsed["stage1_coverage_audit"], "call_log": call_log, "total_cost_jpy": cost})
        print(f"[done] s{sample}/{iid} cands={parsed['stage1_coverage_audit']['n_union_candidates']} cost=JPY{cost} "
              f"cum=JPY{state['cumulative_jpy']:.3f}", flush=True)
        log["runs"].append({"sample": sample, "instance_id": iid, "cost": cost,
                            "n_union": parsed["stage1_coverage_audit"]["n_union_candidates"]})
        if cost > PER_RUN_COST_STOP_JPY:
            log.update(stopped=True, stop_reason=f"per-run cost>{PER_RUN_COST_STOP_JPY}: {cost}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR_A}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:4000])


# ---- 集計(¥0、保存済みrun jsonのみ読む) ----
def claim_matches_def(d: dict, claim_text: str) -> bool:
    t = runner._norm_for_residual(claim_text)
    if runner._norm_for_residual(d["text_substring"]).lower() in t.lower():
        return True
    return bool(d.get("text_pattern") and re.search(d["text_pattern"], t, re.I))


def load_runs() -> list:
    out = []
    for p in sorted(os.listdir(f"{OUT_DIR_A}/runs")) if os.path.isdir(f"{OUT_DIR_A}/runs") else []:
        d = f"{OUT_DIR_A}/runs/{p}"
        for f in sorted(os.listdir(d)):
            with open(f"{d}/{f}", encoding="utf-8") as fh:
                out.append(json.load(fh))
    return out


def route_cands(run: dict, route: str) -> list:
    if route == "union":
        return run["audit"]["union_candidates"]
    return (run["audit"]["per_route"].get(route) or {}).get("candidates", [])


def aggregate(runs: list) -> dict:
    by_inst: dict = {}
    for r in runs:
        by_inst.setdefault(r["instance_id"], []).append(r)
    gold = []
    corr = {"r3_hit_r5_hit": 0, "r3_hit_r5_miss": 0, "r3_miss_r5_hit": 0, "r3_miss_r5_miss": 0}
    for iid in SC_IDS:
        for d in runner._safety_critical_defs(iid):
            rs = by_inst.get(iid, [])
            hit = {k: [any(claim_matches_def(d, c["claim_text"]) for c in route_cands(r, k)) for r in rs]
                   for k in ("r3", "r5", "union")}
            genuine = [any(claim_matches_def(d, c["claim_text"]) and "model" in c["sub_reasons"]
                           for c in route_cands(r, "union")) for r in rs]
            for a, b in zip(hit["r3"], hit["r5"]):
                corr[f"r3_{'hit' if a else 'miss'}_r5_{'hit' if b else 'miss'}"] += 1
            gold.append({"instance_id": iid, "sub_id": d["sub_id"], "n_runs": len(rs),
                         **{f"{k}_detected": f"{sum(v)}/{len(rs)}" for k, v in hit.items()},
                         "union_detected_by_model_judgement": f"{sum(genuine)}/{len(rs)}"})
    hold = {iid: [r["audit"]["n_union_candidates"] for r in by_inst.get(iid, [])] for iid in HOLDOUT_IDS}
    hold_miss = [i for i, v in hold.items() if v and min(v) == 0]
    def mean_cands(ids, k):
        v = [len(route_cands(r, k)) if k != "union" else r["audit"]["n_union_candidates"]
             for i in ids for r in by_inst.get(i, [])]
        return round(sum(v) / len(v), 2) if v else None
    r3runs = [r for r in runs if "r3" in r["audit"]["per_route"]]
    n_j = sum(r["audit"]["n_judged_units"] for r in r3runs) or 1
    miss_first = sum(len(r["audit"]["per_route"]["r3"].get("missing_first") or []) for r in r3runs)
    miss_after = sum(len(r["audit"]["per_route"]["r3"].get("missing_after_rerun") or []) for r in r3runs)
    ret_by = {}
    for r in r3runs:
        for s in r["audit"]["per_route"]["r3"].get("unit_status", {}).values():
            m = re.match(r"SUPPORTED->CANDIDATE\((.*)\)", s)
            for reason in (m.group(1).split(",") if m else []):
                ret_by[reason] = ret_by.get(reason, 0) + 1
    calls = [c for r in runs for k in r["audit"]["per_route"].values() for c in k["calls"] if c.get("cost_jpy")]
    total = round(sum(r["total_cost_jpy"] for r in runs), 4)
    sc_ok = all(g["union_detected"].split("/")[0] == g["union_detected"].split("/")[1] == "3" for g in gold) if gold else False
    return {"n_runs": len(runs), "gold_sc": gold, "route_correlation_2x2_over_sc_runs": corr,
            "holdout_union_candidates_per_instance": hold, "holdout_missed_instances": hold_miss,
            "normal_mean_candidates_per_article": {k: mean_cands(NORMAL_IDS, k) for k in ("r3", "r5", "union")},
            "watch_B2_hormuz_mean_union": mean_cands(WATCH_IDS, "union"),
            "missing_id_rate_first": round(miss_first / n_j, 4), "missing_id_rate_after_rerun": round(miss_after / n_j, 4),
            "runs_with_rerun": sum(1 for r in r3runs if r["audit"]["per_route"]["r3"].get("rerun_used")),
            "returned_by_deterministic_check_by_reason": ret_by,
            "api_failure_runs": sum(1 for r in runs if r.get("api_failure")),
            "cost": {"n_calls": len(calls), "mean_jpy_per_call": round(sum(c["cost_jpy"] for c in calls) / len(calls), 4) if calls else None,
                     "mean_jpy_per_run": round(total / len(runs), 4) if runs else None, "total_jpy": total},
            "criteria_prefixed": CRITERIA,
            "criteria_result": {"sc_union_3of3_all": sc_ok, "holdout_new_miss_zero": not hold_miss and bool(hold),
                                "missing_id_residual_le_5pct": (miss_after / n_j) <= CRITERIA["missing_id_residual_max"]}}


def run_agg() -> None:
    res = aggregate(load_runs())
    os.makedirs(OUT_DIR_A, exist_ok=True)
    with open(f"{OUT_DIR_A}/stageA_aggregate.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps(res, ensure_ascii=True, indent=2)[:6000])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["estimate", "main", "agg"], default="estimate")
    ap.add_argument("--budget-jpy", type=float, default=65.0)
    ap.add_argument("--yes-run-paid", action="store_true", help="有料API実行の明示確認(mainで必須)")
    args = ap.parse_args()
    if args.stage == "agg":
        run_agg()
        return
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    est = estimate_cost(insts, plan())
    print(json.dumps({"n_runs": est["n_runs"], "total_jpy_low_mid_high": est["total_jpy_low_mid_high"],
                      "budget_jpy": args.budget_jpy}, ensure_ascii=True))
    if args.stage == "estimate":
        os.makedirs(OUT_DIR_A, exist_ok=True)
        with open(f"{OUT_DIR_A}/cost_estimate.json", "w", encoding="utf-8") as f:
            json.dump(est, f, ensure_ascii=False, indent=2)
        return
    if not args.yes_run_paid:
        raise SystemExit("--stage main は有料です。--yes-run-paid を付けて明示確認してください(未実行)。")
    run_main(args.budget_jpy)


if __name__ == "__main__":
    main()
