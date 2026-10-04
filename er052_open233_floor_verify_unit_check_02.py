# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_floor_verify_unit_check_02.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_61): 選択肢3(追加確認による解放対象を時期`changed_time`のみに縮小、
# 2026-10-04ユーザー決定[5回目])の限定的な単体安全確認(flowは回さない)。委任_60の_01.pyは
# `comparison_time`モード廃止に伴い再実行不可(既存出力open233_floor_verify_unit_check_01は保存)。
# ============================================================
# 受入条件(ユーザー決定2026-10-04): 重大ラベルのケースを1件でも軽微以下へ解放(2回とも非BLOCKING)した
# ら測定を止めて報告する。解放期待(過剰判定)ケースの解放率は参考値(0でも不合格ではない=安全側)。
#
# 各ケースで、(1)対象判定(floor_verify_target)→(2)CONFIRMED(決定論の不一致確認)→(3)追加確認2回
# (run_floor_verify_call、claim 1件ごとに独立call、短絡なし=2回とも実行して分布を取る)を実行する。
# 想定シナリオは「Stage 2のLLM判定が非BLOCKING(QUALITY)なのに機械判定(floor)がBLOCKINGへ昇格した」
# 状況(=最も危険な場面)。Production code(er003〜er019)は変更しない。API keyは環境変数のみ。
from __future__ import annotations

import argparse
import csv
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_floor_verify_unit_check_02"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233aq_61.json"

# 各ケース: serious_expected=重大期待(どの版でも解放したらSTOP)/release_expected=解放期待(参考値)/
# exclusion_check=対象外確認(比較・主体フラグ。確認callなし=決定論BLOCKINGのまま)。
# version: C=決定論CONFIRMEDが発火する版(確認callなし) / N=抽出トークンを含まない版(確認callが実際に動く)。
def _c(case_id, category, expected, instance_id, fact_id, flags, claim, issue, source, version=""):
    return {"case_id": case_id, "category": category, "expected": expected, "instance_id": instance_id,
            "related_fact_id": fact_id, "flags": flags, "claim_text": claim, "issue": issue,
            "issue_source": source, "version": version}


CASES = [
    # --- 重大期待 ---
    _c("T1c_date_swap_July13", "serious_expected", "BLOCKING(日付の取り違え、CONFIRMED版)", "safety_A2A3", "HF-009",
       ["changed_time"], "On July 13, the plan was withdrawn and replaced with an investment deal.",
       "The claim dates the withdrawal to July 13, but HF-009 dates it to July 14.", "synthetic(委任_60 S3)", "C"),
    _c("T1n_order_withdrawn_before_proposed", "serious_expected", "BLOCKING(前後関係反転、非抽出版)", "safety_A2A3",
       "HF-003, HF-009", ["changed_time"], "The plan was withdrawn before the charge was ever proposed.",
       "The claim puts the withdrawal before the proposal, but the Ledger places the proposal on July 13 and the withdrawal on July 14; the order is reversed.",
       "synthetic", "N"),
    _c("T2c_K16_dated_return", "serious_expected", "BLOCKING(K16型+日付・期間、CONFIRMED版)",
       "neg3_hormuz_prodrunner_b1b", "HF-009", ["changed_time"],
       "The fee plan left the stage on July 15, but the events driving oil prices—and the prices themselves—returned within 3 days.",
       "The claim dates the events and gives a 3-day return, but the Ledger describes those events as continuing and dates the replacement to July 14.",
       "synthetic(K16型)", "C"),
    _c("T2n_K16_continuing_events_returned", "serious_expected",
       "BLOCKING(K16=継続中の出来事を一度消えて戻ったとする、非抽出版)", "neg3_hormuz_prodrunner_b1b", "HF-009",
       ["changed_time"],
       "The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.",
       "The one-line summary says the events driving prices returned, whereas the Ledger and the article’s earlier wording describe those events as continuing. This changes the timeline of the events; the price recovery itself is supported.",
       "recorded(iter8 neg3、委任_60 S2)", "N"),
    _c("T3c_safety12_year_2019", "serious_expected", "BLOCKING(Safety12 changed_time fixture、年の取り違え、CONFIRMED版)",
       "safety_er009_changed_time", "F-001", ["changed_time"],
       "In 2019, researchers published a study in the American Economic Journal: Applied Economics showing that higher suggested tip rates led New York City taxi passengers to leave more money.",
       "The Ledger cites the study as published in 2014, not 2019.", "synthetic(委任_60 S5)", "C"),
    _c("T3n_order_reversed_deal_first", "serious_expected", "BLOCKING(順序の反転、非抽出版)", "bgroup_B2_hormuz",
       "HF-002, HF-007", ["changed_time"],
       "The investment deal was announced first, and the 20% reimbursement fee was proposed only afterwards.",
       "The claim reverses the order: the Ledger says the 20% reimbursement was proposed first (July 13) and replaced by the investment deal afterwards (July 14).",
       "synthetic(HF系の順序反転)", "N"),
    _c("T4c_A5_0_put_back_dated", "serious_expected", "BLOCKING(A5-0=時期・経過の創作、CONFIRMED版)", "safety_A5",
       "MUSE-HC-012", ["changed_time"],
       "They put the feature back on September 30, so humans handled the calls again. They did not stop Muse itself.",
       "The claim invents a September 30 restoration, whereas the Ledger only says the feature was rolled back for now (through September 22).",
       "synthetic", "C"),
    _c("T4n_A5_0_put_back", "serious_expected", "BLOCKING(A5-0=時期・経過の創作、非抽出版)", "safety_A5", "MUSE-HC-012",
       ["changed_time"],
       "They also temporarily put back the feature in which humans handled the calls. They did not stop Muse itself.",
       "The article says the human-handled feature was temporarily put back (rolled back and then restored), whereas the Ledger only says the feature was rolled back for now; the claim invents a restoration in the timeline.",
       "synthetic(委任_60 S7)", "N"),
    _c("T5c_duration_3_days", "serious_expected", "BLOCKING(期間の付け替え、CONFIRMED版)", "bgroup_B2_hormuz",
       "HF-002, HF-007", ["changed_time"], "The Hormuz fee proposal was replaced about 3 days later.",
       "The claim says about 3 days later, but the Ledger gives about 24 hours 48 minutes between the proposal and the replacement.",
       "synthetic", "C"),
    _c("T5n_duration_long_time", "serious_expected", "BLOCKING(期間の付け替え、非抽出版)", "bgroup_B2_hormuz",
       "HF-002, HF-007", ["changed_time"], "The Hormuz fee proposal was replaced only after a long time.",
       "The claim says the replacement came after a long time, but the Ledger gives about 24 hours 48 minutes between the proposal and the replacement.",
       "synthetic", "N"),
    # --- 対象外確認(確認callなし) ---
    _c("X1_direction_reversal_out_of_scope", "exclusion_check",
       "BLOCKING(方向反転。changed_comparisonは対象外=決定論BLOCKINGのまま、委任_60 S1)", "safety_A2A3", "HF-009",
       ["changed_comparison"], "After the plan was withdrawn, oil prices fell.",
       "The claim says oil prices fell after the withdrawal, but HF-009 says the Brent gains narrowed only briefly and then recovered to a high level; the direction is reversed.",
       "synthetic(委任_60 S1)", "-"),
    _c("X2_actor_plus_time_out_of_scope", "exclusion_check",
       "BLOCKING(主体+時期。changed_actorが立つため対象外)", "safety_A2A3", "HF-003",
       ["changed_actor", "changed_time"],
       "The idea was that those carrying the cargo would repay the money the United States spends to keep the strait safe.",
       "The article identifies cargo carriers as the payers, although the Ledger says the proposal did not specify who would be liable to pay.",
       "recorded(iter6 K18、フラグ合成)", "-"),
    # --- 解放期待(参考値) ---
    _c("R1_B2_vanished_overnight", "release_expected", "QUALITY以下(B2、実run記録LLM=ACCEPTABLE、changed_timeのみ)",
       "bgroup_B2_hormuz", "HF-002, HF-007", ["changed_time"], "Trump’s proposed Hormuz fee vanished overnight.",
       "The claim says the fee vanished overnight, but the Ledger places the proposal on July 13 and the replacement on July 14, about 24 hours 48 minutes later.",
       "synthetic(委任_60 R2)", "N"),
    _c("R2_K15_during_that_period", "release_expected", "ACCEPTABLE(設計書K15=問題なし、changed_time)",
       "neg3_hormuz_prodrunner_b1b", "HF-009", ["changed_time"],
       "During that period, attacks between the United States and Iran, a sea blockade, and concerns about tanker safety continued.",
       "The claim places the attacks, blockade and tanker-safety concerns in a specific period, but the Ledger does not confirm that timeline.",
       "synthetic(設計書K15の文、issue文は合成)", "N"),
    _c("R3_K17_may_be_replaced", "release_expected", "QUALITY(設計書K17=軽微、changed_time)",
       "neg3_hormuz_prodrunner_b1b", "HF-009", ["changed_time"],
       "The fee plan may be replaced, but events continuing at the same time do not simply disappear backstage because of one announcement.",
       "The claim describes the timing of the continuing events relative to the announcement, but the Ledger does not confirm that timeline.",
       "synthetic(設計書K17の文、issue文は合成)", "N"),
]


def _load_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def _save_state(state: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _save(path: str, payload) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _fixtures() -> dict:
    return {i["instance_id"]: i["fixture"] for i in runner.build_target_instances()}


def run_trial(client, state, fixtures, case, trial_idx, raw_calls_out: list) -> dict:
    fx = fixtures[case["instance_id"]]
    local_context, _fb = s2p.build_local_context(fx["article_text"], case["claim_text"])
    dev = {"related_fact_id": case["related_fact_id"], "issue": case["issue"],
           **{f: True for f in case["flags"]}}

    def call_fn(claim_text, lc, fact_block, issue, flag_names, related_fact_id):
        try:
            res = runner.run_floor_verify_call(client, claim_text, lc, fact_block, issue, flag_names,
                                               related_fact_id)
        except Exception as e:  # noqa: BLE001
            state["cumulative_errors"] += 1
            _save_state(state)
            raise runner.FloorVerifyCallError(f"{type(e).__name__}: {e}") from e
        state["cumulative_calls"] += 1
        state["cumulative_jpy"] += res["cost_jpy"]
        state["history"].append({"case": case["case_id"], "trial": trial_idx, "cost_jpy": res["cost_jpy"]})
        _save_state(state)
        raw_calls_out.append({"parsed": res["parsed"], "prompt_sha256": res["prompt_sha256"],
                              "cost_jpy": res["cost_jpy"], "usage": res["usage"],
                              "response_id": res["response_id"], "model": res["model"]})
        return res

    fv = runner.floor_verify_evaluate(
        call_fn, fx["ledger_text"], case["claim_text"], local_context, dev, "QUALITY",
        "deterministic_floor:" + ",".join(case["flags"]), short_circuit=False)
    return fv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["probe", "main", "agg"], required=True)
    parser.add_argument("--suite", default="time_only", choices=["time_only"])
    parser.add_argument("--out-dir", default=OUT_DIR)
    parser.add_argument("--n-serious", type=int, default=5)
    parser.add_argument("--n-release", type=int, default=3)
    parser.add_argument("--budget-jpy", type=float, default=30.0)
    args = parser.parse_args()
    runner.FLOOR_VERIFY_MODE = runner.validate_floor_verify_mode(args.suite)
    if args.stage == "agg":
        return agg()
    client = vfl01.get_client()
    state = _load_state()
    fixtures = _fixtures()
    stopped, stop_reason = False, None
    if args.stage == "probe":
        case = next(c for c in CASES if c["case_id"].startswith("R1_"))
        raw: list = []
        t0 = time.time()
        # 単価確認: 1ケース×1回(確認callは1回だけ。floor_verify_evaluateは2回呼ぶため直接1回呼ぶ)
        fx = fixtures[case["instance_id"]]
        fb = runner.floor_verify_fact_block(fx["ledger_text"], case["related_fact_id"])
        lc, _ = s2p.build_local_context(fx["article_text"], case["claim_text"])
        res = runner.run_floor_verify_call(client, case["claim_text"], lc, fb, case["issue"], ["time"],
                                           case["related_fact_id"])
        state["cumulative_calls"] += 1
        state["cumulative_jpy"] += res["cost_jpy"]
        _save_state(state)
        _save(f"{OUT_DIR}/probe/probe_01.json", {"case": case["case_id"], "parsed": res["parsed"],
                                                 "cost_jpy": res["cost_jpy"], "usage": res["usage"],
                                                 "prompt_sha256": res["prompt_sha256"],
                                                 "elapsed_seconds": res["elapsed_seconds"]})
        print(json.dumps({"probe_cost_jpy_per_call": res["cost_jpy"], "parsed": res["parsed"],
                          "elapsed": round(time.time() - t0, 2)}, ensure_ascii=False, indent=2))
        return
    # main
    for case in CASES:
        if stopped:
            break
        n = (args.n_serious if case["category"] == "serious_expected"
             else args.n_release if case["category"] == "release_expected" else 1)
        for trial in range(1, n + 1):
            if state["cumulative_jpy"] >= args.budget_jpy:
                stopped, stop_reason = True, f"累計¥{state['cumulative_jpy']:.3f}がGuardrail¥{args.budget_jpy}に到達"
                break
            raw: list = []
            fv = run_trial(client, state, fixtures, case, trial, raw)
            _save(f"{OUT_DIR}/raw/{case['case_id']}/trial_{trial}.json", {"floor_verify": fv, "raw_calls": raw})
            # 以降の試行が、deterministic(CONFIRMED/対象外)で結果が同じなら繰り返さない
            if not fv["target"] or fv["confirmed"] or fv["blocking_fixed_reason"] == "fact_block_unavailable":
                break
            if case["category"] == "serious_expected" and fv["released"]:
                stopped = True
                stop_reason = (f"STOP: 重大期待ケース{case['case_id']}がtrial{trial}で解放された"
                               f"(2回とも非BLOCKING)。受入条件違反、測定を止めて報告する")
                break
    info = {"stage": "main", "n_serious": args.n_serious, "n_release": args.n_release, "stopped": stopped,
            "stop_reason": stop_reason, "cumulative_jpy": round(state["cumulative_jpy"], 4),
            "cumulative_calls": state["cumulative_calls"], "cumulative_errors": state["cumulative_errors"]}
    _save(f"{OUT_DIR}/stage_main_info.json", info)
    print(json.dumps(info, ensure_ascii=False, indent=2))


def agg() -> None:
    state = _load_state()
    info_path = f"{OUT_DIR}/stage_main_info.json"
    info = json.load(open(info_path, encoding="utf-8")) if os.path.exists(info_path) else {}
    rows, results = [], []
    for case in CASES:
        d = f"{OUT_DIR}/raw/{case['case_id']}"
        trials = []
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                trials.append(json.load(open(f"{d}/{fn}", encoding="utf-8")))
        if not trials:
            continue
        fvs = [t["floor_verify"] for t in trials]
        calls = [c for fv in fvs for c in fv["calls"]]
        dist: dict = {}
        for c in calls:
            k = c.get("materiality") or c.get("invalid_reason") or "unknown"
            dist[k] = dist.get(k, 0) + 1
        n_valid_cit = sum(1 for c in calls if c.get("citation_verbatim"))
        n_released = sum(1 for fv in fvs if fv["released"])
        fixed = {}
        for fv in fvs:
            if not fv["released"]:
                k = fv["blocking_fixed_reason"] or "unknown"
                fixed[k] = fixed.get(k, 0) + 1
        res = {"case_id": case["case_id"], "version": case["version"], "category": case["category"], "expected": case["expected"],
               "claim_text": case["claim_text"], "flags": case["flags"], "related_fact_id": case["related_fact_id"],
               "issue_source": case["issue_source"], "n_trials": len(fvs),
               "target": fvs[0]["target"], "target_reason": fvs[0]["target_reason"],
               "confirmed": fvs[0]["confirmed"], "confirmed_basis": fvs[0]["confirmed_basis"],
               "n_calls": len(calls), "call_label_distribution": dist,
               "n_citation_verbatim": n_valid_cit, "n_released": n_released,
               "blocking_fixed_by_reason": fixed,
               "cost_jpy": round(sum(fv["cost_jpy"] for fv in fvs), 4),
               "sample_citations": [c.get("ledger_citation") for c in calls[:3]],
               "sample_explanations": [c.get("explanation") for c in calls[:2]]}
        # 期待との一致: 重大期待/対象外は解放0が合格。解放期待は参考値。
        if case["category"] in ("serious_expected", "exclusion_check"):
            res["matches_expectation"] = (n_released == 0)
        else:
            res["matches_expectation"] = None
            res["release_rate_reference"] = f"{n_released}/{len(fvs)}"
        results.append(res)
        rows.append({"case_id": case["case_id"], "category": case["category"], "expected": case["expected"], "version": case["version"],
                     "n_trials": len(fvs), "target": res["target"], "confirmed": res["confirmed"],
                     "n_calls": res["n_calls"], "call_labels": json.dumps(dist, ensure_ascii=False),
                     "n_citation_verbatim": n_valid_cit, "n_released": n_released,
                     "blocking_fixed_by_reason": json.dumps(fixed, ensure_ascii=False),
                     "matches_expectation": res["matches_expectation"], "cost_jpy": res["cost_jpy"]})
    serious_released = sum(r["n_released"] for r in results if r["category"] in ("serious_expected", "exclusion_check"))
    out = {"stage_info": info, "cost_jpy_total": round(state["cumulative_jpy"], 4), "calls": state["cumulative_calls"],
           "errors": state["cumulative_errors"], "serious_or_exclusion_released_total": serious_released,
           "acceptance": "PASS(重大期待・対象外の解放0)" if serious_released == 0 and not info.get("stopped_for_serious") else "FAIL",
           "results": results}
    _save(f"{OUT_DIR}/results_01.json", out)
    with open(f"{OUT_DIR}/cases_01.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({"cost_jpy_total": out["cost_jpy_total"], "calls": out["calls"],
                      "serious_or_exclusion_released_total": serious_released, "acceptance": out["acceptance"],
                      "stopped": info.get("stopped"), "stop_reason": info.get("stop_reason"),
                      "cases": [{k: r[k] for k in ("case_id", "target", "confirmed", "n_trials", "n_calls",
                                                   "call_label_distribution", "n_released")} for r in results]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
