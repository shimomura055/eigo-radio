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


NORMAL_N = 3  # 委任_07: --normal-n 2 でNORMAL 6 instanceをn=2に縮小(SC+watchはn=3のまま)


def plan() -> list:
    """[(sample, instance_id)]。sample-major: sample1に全instance(hold-out含む)、sample2/3はn=3対象のみ。"""
    main_ids = SC_IDS + WATCH_IDS + NORMAL_IDS
    out = [(1, i) for i in main_ids + HOLDOUT_IDS]
    for s in range(2, N_MAIN + 1):
        out += [(s, i) for i in SC_IDS + WATCH_IDS + (NORMAL_IDS if s <= NORMAL_N else [])]
    return out


def plan_g_arm() -> list:
    """委任_11/12: (G)reasoning effort先行実験・r5-V fresh用。SC 6x3 + hold-out 9x1 + NORMAL 6x1 = 33 run(sample-major)。"""
    out = [(1, i) for i in SC_IDS + HOLDOUT_IDS + NORMAL_IDS]
    for smp in (2, 3):
        out += [(smp, i) for i in SC_IDS]
    return out


def plan_cap() -> list:
    """委任_13 Step 1b(r5-V検出能力テスト用): SC 6x3 + hold-out 9x1 = 27 run(NORMALなし)。"""
    out = [(1, i) for i in SC_IDS + HOLDOUT_IDS]
    for smp in (2, 3):
        out += [(smp, i) for i in SC_IDS]
    return out


PLANS = {"stageA": plan, "g_arm": plan_g_arm, "cap": plan_cap}

# ---- 委任_13 Step 1b: Trial専用・測定用。r5-Vの検出「能力」を測るため、gold単位を強制的に検証対象へ加える ----
# SC instance: Safety-critical定義(BLOCKING)に一致する単位を追加。hold-out(gold単位定義なし): 判定対象の全単位を追加。
# 量産経路・通常のTrial経路では使わない(既定=無効、--r5v-force-targets goldを付けたときだけ有効)。
CURRENT_IID = None


def force_gold_targets(units: list, targets: list) -> list:
    iid = CURRENT_IID
    ids = {u["id"] for u in targets}
    if iid in SC_IDS:
        defs = runner._safety_critical_defs(iid)
        for u in units:
            if u["type"] != "paragraph" and u.get("judged") and any(claim_matches_def(d, cov.unit_claim_text(u)) for d in defs):
                ids.add(u["id"])
    elif iid in HOLDOUT_IDS:
        ids |= {u["id"] for u in units if u["type"] != "paragraph" and u.get("judged")}
    return [u for u in units if u["id"] in ids]


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


# ---- 委任_11: 新スイッチ(既定=従来)と費用概算(r5-V・経路別effort。全て¥0・推測を含む) ----
# reasoning token(high時の平均)は段階A実測(委任_10 §1: r3 3,465 / r5 7,674)。effort別の倍率と帯は【推測】(未検証)。
REASON_HIGH_MEAN = {"r3": 3465, "r5": 7674}
EFFORT_FACTOR = {"high": 1.0, "medium": 0.5, "low": 0.25}
BAND = (0.6, 1.0, 1.5)  # low/mid/high帯(reasoningへの乗数)


def load_stored_r3(reuse_dir: str, sample: int, iid: str):
    p = f"{reuse_dir}/runs/s{sample}/{iid}.json"
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["audit"]["per_route"].get("r3")


def estimate_cost_v2(instances: dict, plan_rows: list, r5_mode: str, r3_eff: str, r5_eff: str, reuse_r3_dir: str | None,
                     r3_proxy_dir: str | None = None) -> dict:
    """r5_mode/effort/r3再利用を反映した費用概算。r5-Vの検証対象数は保存済みr3出力(`r3_proxy_dir`、同instance・同sample、
    無ければsample 1)のSUPPORTED単位+関係単位から数える(fresh時のr3結果の代理)。reuse_r3_dir指定時はr3 callを0とする。"""
    from er052_open233_self_recovery_stage2_production_01 import official_cost_jpy
    rows, tot = [], [0.0, 0.0, 0.0]
    src = reuse_r3_dir or r3_proxy_dir or OUT_DIR_A
    for smp, iid in plan_rows:
        fx = instances[iid]["fixture"]
        sp = cov.split_units(fx["article_text"], runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)
        blocks = cov.ledger_fact_blocks(fx["ledger_text"])
        nj, nf = len(sp["judged_ids"]), len(blocks)
        p3 = len(cov.build_r3_prompt(fx["ledger_text"], sp["units"], sp["judged_ids"]))
        r3st = load_stored_r3(src, smp, iid) or load_stored_r3(src, 1, iid)
        if r5_mode == "verify_supported":
            if r3st is None:  # 代理が無い場合は全単位を対象とする(上側見積)
                targets = [u for u in sp["units"] if u["type"] != "paragraph"]
            else:
                global CURRENT_IID
                CURRENT_IID = iid
                targets = cov.r5v_target_units(sp["units"], r3st.get("unit_status") or r3st.get("status") or {})
                targets = cov._r5v_force_hook(sp["units"], targets)
            p5 = len(cov.build_r5v_prompt(fx["ledger_text"], fx["article_text"], targets, list(blocks)))
            vis5 = nf * 35 + int(len(targets) * 0.8 * 90)
            n_targets = len(targets)
        else:
            p5 = len(cov.build_r5_prompt(fx["ledger_text"], sp["units"], list(blocks)))
            vis5 = nf * 35 + int(nj * 0.8 * 90)
            n_targets = nj
        est = []
        for k, b in enumerate(BAND):
            c3 = 0.0 if reuse_r3_dir else official_cost_jpy({
                "input_tokens": int(p3 * TOK_PER_CHAR), "output_tokens": int(REASON_HIGH_MEAN["r3"] * EFFORT_FACTOR[r3_eff] * b) + nj * 130})
            c5 = official_cost_jpy({"input_tokens": int(p5 * TOK_PER_CHAR),
                                    "output_tokens": int(REASON_HIGH_MEAN["r5"] * EFFORT_FACTOR[r5_eff] * b) + vis5})
            est.append(c3 + c5)
            tot[k] += c3 + c5
        rows.append({"sample": smp, "instance_id": iid, "n_judged": nj, "n_r5_targets": n_targets, "r3_proxy_missing": r3st is None,
                     "jpy_low_mid_high": [round(x, 3) for x in est]})
    return {"mode": {"r5_mode": r5_mode, "r3_reasoning": r3_eff, "r5_reasoning": r5_eff, "r3_reused_from": reuse_r3_dir},
            "assumptions": "reasoning=段階A実測平均(r3 3,465/r5 7,674)xeffort倍率(high1/medium0.5/low0.25, 未検証)x帯(0.6/1.0/1.5)。"
                           "入力=文字数x0.66、可視出力=r3 判定単位x130、r5 fact x35+対象単位x0.8x90。r5-Vの推論は同effortの5-lite同等と仮定(保守側)。",
            "n_runs": len(plan_rows), "total_jpy_low_mid_high": [round(x, 2) for x in tot], "rows": rows}


# ---- 有料実行(--stage main --yes-run-paid のときだけ) ----
def apply_switches(budget_jpy: float, out_dir: str | None = None, r5_mode: str = "full", r3_reasoning: str = "high",
                   r5_reasoning: str = "high", negation_mode: str = "legacy") -> dict:
    out_dir = out_dir or OUT_DIR_A  # call時のglobal参照(テストのpatch・既定=従来のOUT_DIR_A)
    runner.OUT_DIR = out_dir
    runner.BUDGET_STATE_PATH = BUDGET_STATE_A if out_dir == OUT_DIR_A else f"{out_dir}/budget_state_stage1_stageA_01.json"
    runner.TOTAL_BUDGET_JPY = budget_jpy
    runner.STAGE1_MODE = runner.STAGE1_MODE_COVERAGE_UNION
    runner.STAGE1_ROUTES = "both"  # 1 runで両経路を保存(集計で経路別/∪を分離)
    runner.STAGE1_R5_MODE = r5_mode
    runner.STAGE1_R3_REASONING = r3_reasoning
    runner.STAGE1_R5_REASONING = r5_reasoning
    runner.STAGE1_NEGATION_MODE = negation_mode
    assert runner.MODEL == "gpt-6-luna"
    return {"STAGE1_MODE": runner.STAGE1_MODE, "STAGE1_ROUTES": runner.STAGE1_ROUTES, "MODEL": runner.MODEL,
            "TOTAL_BUDGET_JPY": budget_jpy, "STAGE1_R5_MODE": r5_mode, "STAGE1_R3_REASONING": r3_reasoning,
            "STAGE1_R5_REASONING": r5_reasoning, "STAGE1_NEGATION_MODE": negation_mode}


WORST_RUN_RECORD_JPY = 3.0  # 委任_11: ユーザー基準「単発¥3超は報告」。超えた全runを記録(停止は従来のPER_RUN_COST_STOP_JPY=6)


def run_main(budget_jpy: float, out_dir: str | None = None, plan_name: str = "stageA", r5_mode: str = "full",
             r3_reasoning: str = "high", r5_reasoning: str = "high", negation_mode: str = "legacy",
             reuse_r3_dir: str | None = None) -> None:
    out_dir = out_dir or OUT_DIR_A
    applied = apply_switches(budget_jpy, out_dir, r5_mode, r3_reasoning, r5_reasoning, negation_mode)
    applied["REUSE_R3_DIR"] = reuse_r3_dir
    os.makedirs(out_dir, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    ce = [0]
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": [], "runs_over_3jpy": []}
    for sample, iid in PLANS[plan_name]():
        path = f"{out_dir}/runs/s{sample}/{iid}.json"
        if os.path.exists(path):
            print(f"[skip existing] s{sample}/{iid}")
            continue
        call_log: list = []
        global CURRENT_IID
        CURRENT_IID = iid
        try:
            pre = load_stored_r3(reuse_r3_dir, sample, iid) if reuse_r3_dir else None
            if reuse_r3_dir and pre is None:
                raise RuntimeError(f"stored r3 not found: s{sample}/{iid}")
            parsed = runner.stage1_coverage_fresh(client, state, ce, call_log, f"{iid}_s{sample}_stage1", insts[iid]["fixture"],
                                                  r3_precomputed=pre)
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
        runner.save_json(path, {"sample": sample, "instance_id": iid, "group": insts[iid]["group"], "switches": applied,
                                "api_failure": bool(parsed.get("_stage1_api_failure")),
                                "audit": parsed["stage1_coverage_audit"], "call_log": call_log, "total_cost_jpy": cost})
        print(f"[done] s{sample}/{iid} cands={parsed['stage1_coverage_audit']['n_union_candidates']} cost=JPY{cost} "
              f"cum=JPY{state['cumulative_jpy']:.3f}", flush=True)
        log["runs"].append({"sample": sample, "instance_id": iid, "cost": cost,
                            "n_union": parsed["stage1_coverage_audit"]["n_union_candidates"]})
        if cost > WORST_RUN_RECORD_JPY:  # ¥3超は全件記録(停止ではない)
            log["runs_over_3jpy"].append({"sample": sample, "instance_id": iid, "cost_jpy": cost})
        if cost > PER_RUN_COST_STOP_JPY:
            log.update(stopped=True, stop_reason=f"per-run cost>{PER_RUN_COST_STOP_JPY}: {cost}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    log["worst_run_jpy"] = max((r["cost"] for r in log["runs"]), default=None)
    runner.save_json(f"{out_dir}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:4000])


# ---- 集計(¥0、保存済みrun jsonのみ読む) ----
def claim_matches_def(d: dict, claim_text: str) -> bool:
    t = runner._norm_for_residual(claim_text)
    if runner._norm_for_residual(d["text_substring"]).lower() in t.lower():
        return True
    return bool(d.get("text_pattern") and re.search(d["text_pattern"], t, re.I))


def load_runs(out_dir: str | None = None) -> list:
    out_dir = out_dir or OUT_DIR_A
    out = []
    for p in sorted(os.listdir(f"{out_dir}/runs")) if os.path.isdir(f"{out_dir}/runs") else []:
        d = f"{out_dir}/runs/{p}"
        for f in sorted(os.listdir(d)):
            with open(f"{d}/{f}", encoding="utf-8") as fh:
                out.append(json.load(fh))
    return out


def route_cands(run: dict, route: str) -> list:
    if route == "union":
        return run["audit"]["union_candidates"]
    return (run["audit"]["per_route"].get(route) or {}).get("candidates", [])


def is_model_cand(c: dict) -> bool:
    """委任_13: M判定は`source_of`の定義(model_r3/model_r5=sub_reasonsが'model'または'unknown_unit_id')に合わせる。
    従来の`"model" in sub_reasons`は、モデルが単位IDを`[S2.1]`のように角括弧付きで返した(unit_id不明=orphan候補)検出をMから落としていた。"""
    return any(str(x).startswith("model_") for x in (c.get("sources") or [])) or "model" in (c.get("sub_reasons") or [])


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
            genuine = [any(claim_matches_def(d, c["claim_text"]) and is_model_cand(c)
                           for c in route_cands(r, "union")) for r in rs]
            m_idvalid = {k: [any(claim_matches_def(d, c["claim_text"]) and "model" in c["sub_reasons"]
                                 for c in route_cands(r, k)) for r in rs] for k in ("r3", "r5")}
            # 委任_11 M/D区分: 経路別のモデル判定(M)検出。Safety合否・effort採否はMだけで数える(決定論Dを入れない)。
            m_route = {k: [any(claim_matches_def(d, c["claim_text"]) and is_model_cand(c)
                               for c in route_cands(r, k)) for r in rs] for k in ("r3", "r5")}
            for a, b in zip(hit["r3"], hit["r5"]):
                corr[f"r3_{'hit' if a else 'miss'}_r5_{'hit' if b else 'miss'}"] += 1
            gold.append({"instance_id": iid, "sub_id": d["sub_id"], "n_runs": len(rs),
                         **{f"{k}_detected": f"{sum(v)}/{len(rs)}" for k, v in hit.items()},
                         "union_detected_by_model_judgement": f"{sum(genuine)}/{len(rs)}",
                         "r3_detected_M": f"{sum(m_route['r3'])}/{len(rs)}", "r5_detected_M": f"{sum(m_route['r5'])}/{len(rs)}",
                         "union_detected_M": f"{sum(genuine)}/{len(rs)}",
                         "r3_detected_M_idvalid_only": f"{sum(m_idvalid['r3'])}/{len(rs)}",
                         "r5_detected_M_idvalid_only": f"{sum(m_idvalid['r5'])}/{len(rs)}"})
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
    sc_m_ok = all(g["union_detected_M"].split("/")[0] == g["union_detected_M"].split("/")[1] == "3" for g in gold) if gold else False
    hold_m = {iid: [sum(1 for c in r["audit"]["union_candidates"] if is_model_cand(c)) for r in by_inst.get(iid, [])]
              for iid in HOLDOUT_IDS}
    hold_m_miss = [i for i, v in hold_m.items() if v and min(v) == 0]
    cost_runs = sorted(((r["total_cost_jpy"], r["sample"], r["instance_id"]) for r in runs), reverse=True)
    return {"n_runs": len(runs), "gold_sc": gold, "route_correlation_2x2_over_sc_runs": corr,
            "model_vs_deterministic": {
                "note": "Safety判定はM(model判定、sub_reasonsに'model')のみ。決定論(D)・coverage_gapのみの検出は別欄(Opus#17/Fable評価5)。",
                "sc_union_3of3_by_M_all": sc_m_ok, "holdout_model_judged_candidates_per_instance": hold_m,
                "holdout_missed_by_M": hold_m_miss,
                "n_union_candidates_deterministic_only": sum(r["audit"].get("n_deterministic_only_candidates", 0) for r in runs),
                "n_union_candidates_with_model": sum(r["audit"].get("n_model_candidates", 0) for r in runs)},
            "worst_runs": {"top3": [{"jpy": c, "sample": s, "instance_id": i} for c, s, i in cost_runs[:3]],
                           "runs_over_3jpy_all": [{"jpy": c, "sample": s, "instance_id": i} for c, s, i in cost_runs if c > 3.0]},
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
            "criteria_result": {"sc_union_3of3_all": sc_ok, "sc_union_3of3_by_M_all": sc_m_ok,
                                "holdout_new_miss_zero": not hold_miss and bool(hold),
                                "holdout_new_miss_zero_by_M": not hold_m_miss and bool(hold),
                                "missing_id_residual_le_5pct": (miss_after / n_j) <= CRITERIA["missing_id_residual_max"]}}


def run_agg(out_dir: str | None = None) -> None:
    out_dir = out_dir or OUT_DIR_A
    res = aggregate(load_runs(out_dir))
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/stageA_aggregate.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps(res, ensure_ascii=True, indent=2)[:6000])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["estimate", "main", "agg"], default="estimate")
    ap.add_argument("--budget-jpy", type=float, default=65.0)
    ap.add_argument("--yes-run-paid", action="store_true", help="有料API実行の明示確認(mainで必須)")
    ap.add_argument("--normal-n", type=int, default=3, help="NORMAL instanceのn(既定3、委任_07は2)")
    # 委任_11(全て既定=従来挙動。既定のままなら出力先・概算・実行とも従来と同一)
    ap.add_argument("--r5-mode", choices=list(cov.R5_MODES), default="full")
    ap.add_argument("--r3-reasoning", choices=list(cov.REASONING_EFFORTS), default="high")
    ap.add_argument("--r5-reasoning", choices=list(cov.REASONING_EFFORTS), default="high")
    ap.add_argument("--negation-mode", choices=list(cov.NEGATION_MODES), default="legacy")
    ap.add_argument("--plan", choices=list(PLANS), default="stageA", help="stageA(従来)/g_arm(SC 6x3+hold-out 9+NORMAL 6=33 run)")
    ap.add_argument("--out-dir", default=None, help="run/aggの出力先(既定は従来のOUT_DIR_A。新規置き場は作らず既存er052_output配下を指定)")
    ap.add_argument("--reuse-r3-from", default=None, help="保存済みr3出力(<dir>/runs/s*/<iid>.json)を再利用しr3を再実行しない(r5-V用)")
    ap.add_argument("--r5v-force-targets", choices=["gold"], default=None,
                    help="Trial専用・測定用(Step 1b): r5-Vの検出能力を測るためgold単位(SC=定義一致、hold-out=全判定単位)を強制的に検証対象へ加える")
    ap.add_argument("--estimate-out", default=None, help="estimateの出力json(未指定かつ従来設定ならOUT_DIR_A/cost_estimate.json)")
    args = ap.parse_args()
    global NORMAL_N
    NORMAL_N = args.normal_n
    if args.r5v_force_targets == "gold":
        cov.R5V_FORCE_TARGETS_FN = force_gold_targets
    if args.stage == "agg":
        run_agg(args.out_dir)
        return
    if args.r5_mode == "verify_supported" and args.stage == "main" and args.plan == "stageA" and not args.reuse_r3_from:
        pass  # r3を再実行する場合も可(fresh r3 -> r5-V)
    legacy_cfg = (args.r5_mode, args.r3_reasoning, args.r5_reasoning, args.reuse_r3_from, args.plan) == ("full", "high", "high", None, "stageA")
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    if legacy_cfg:
        est = estimate_cost(insts, plan())
    else:
        est = estimate_cost_v2(insts, PLANS[args.plan](), args.r5_mode, args.r3_reasoning, args.r5_reasoning, args.reuse_r3_from)
    print(json.dumps({"n_runs": est["n_runs"], "total_jpy_low_mid_high": est["total_jpy_low_mid_high"],
                      "budget_jpy": args.budget_jpy, "mode": est.get("mode")}, ensure_ascii=True))
    if args.stage == "estimate":
        out = args.estimate_out or (f"{OUT_DIR_A}/cost_estimate.json" if legacy_cfg else None)
        if out:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(est, f, ensure_ascii=False, indent=2)
        return
    if not args.yes_run_paid:
        raise SystemExit("--stage main は有料です。--yes-run-paid を付けて明示確認してください(未実行)。")
    run_main(args.budget_jpy, args.out_dir, args.plan, args.r5_mode, args.r3_reasoning, args.r5_reasoning,
             args.negation_mode, args.reuse_r3_from)


if __name__ == "__main__":
    main()
