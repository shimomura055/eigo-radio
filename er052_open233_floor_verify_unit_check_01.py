# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_floor_verify_unit_check_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_60): 案1(比較・方向・時期の機械判定の追加確認による解放)の
# 限定的な単体安全確認(flowは回さない)。
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

OUT_DIR = "er052_output/open233_floor_verify_unit_check_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ap_60.json"

# 各ケース: (case_id, category, expected, instance_id, claim_text, flags(dev), related_fact_id, issue, note)
# category: release_expected(解放期待=過剰判定。解放率は参考値)/serious_expected(重大期待。解放したらSTOP)/
#           exclusion_check(主体・数値の対象外確認。確認callなし=決定論BLOCKINGのまま)
# issue_source: recorded=過去の実run記録の逐語 / synthetic=合成(本スクリプトで作成)
CASES = [
    {"case_id": "R1_K19", "category": "release_expected", "expected": "QUALITY(ユーザー決定2026-10-03、解放期待)",
     "instance_id": "safety_A2A3", "related_fact_id": "HF-009", "flags": ["changed_comparison"],
     "claim_text": "Just after the charge plan disappeared, prices began to fall.",
     "issue": "記事は価格そのものが下落し始めたと述べていますが、Ledgerが確認しているのは、撤回発表後にBrent先物の上げ幅が一時縮小し、その後、発表前に近い高水準へ戻ったことです。",
     "issue_source": "recorded(iter6 safety_A2A3)"},
    {"case_id": "R2_B2_vanished_overnight", "category": "release_expected",
     "expected": "QUALITY以下(過剰判定、解放期待。B2の実run記録はLLM=ACCEPTABLE、changed_timeのみ)",
     "instance_id": "bgroup_B2_hormuz", "related_fact_id": "HF-002, HF-007", "flags": ["changed_time"],
     "claim_text": "Trump’s proposed Hormuz fee vanished overnight.",
     "issue": "The claim says the fee vanished overnight, but the Ledger places the proposal on July 13 and the replacement on July 14, about 24 hours 48 minutes later.",
     "issue_source": "synthetic(実run記録のdevにissue無し)"},
    {"case_id": "R3_B4_Names_plans", "category": "release_expected",
     "expected": "ACCEPTABLE〜QUALITY(設計書B4-b、解放期待)",
     "instance_id": "bgroup_B4", "related_fact_id": "MUSE-HC-010", "flags": ["changed_comparison"],
     "claim_text": "Names, plans, and private matters are easier to share when you know who is hearing them.",
     "issue": "原文は、機械に話すと思う場合と人が聞いていると知る場合とで安心感が異なり、相手が誰かは重要だとしている。記事はそこから、相手を知っていると個人的な情報をより話しやすいという方向性のある比較を加えているが、Ledgerはその比較を確認していない。",
     "issue_source": "recorded(iter6 bgroup_B4)"},
    {"case_id": "S1_direction_reversal", "category": "serious_expected", "expected": "BLOCKING(方向反転、解放したらSTOP)",
     "instance_id": "safety_A2A3", "related_fact_id": "HF-009", "flags": ["changed_comparison"],
     "claim_text": "After the plan was withdrawn, oil prices fell.",
     "issue": "The claim says oil prices fell after the withdrawal, but HF-009 says the Brent gains narrowed only briefly and then recovered to a high level; the direction is reversed.",
     "issue_source": "synthetic"},
    {"case_id": "S2_K16_continuing_events_returned", "category": "serious_expected",
     "expected": "BLOCKING(継続中の出来事を一度消えて戻ったとする。解放したらSTOP)",
     "instance_id": "neg3_hormuz_prodrunner_b1b", "related_fact_id": "HF-009", "flags": ["changed_time"],
     "claim_text": "The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.",
     "issue": "The one-line summary says the events driving prices returned, whereas the Ledger and the article’s earlier wording describe those events as continuing. This changes the timeline of the events; the price recovery itself is supported.",
     "issue_source": "recorded(iter8 neg3)"},
    {"case_id": "S3_date_swap_July13", "category": "serious_expected", "expected": "BLOCKING(日付の取り違え。CONFIRMEDで確認callなしが期待)",
     "instance_id": "safety_A2A3", "related_fact_id": "HF-009", "flags": ["changed_time"],
     "claim_text": "On July 13, the plan was withdrawn and replaced with an investment deal.",
     "issue": "The claim dates the withdrawal to July 13, but HF-009 dates it to July 14.",
     "issue_source": "synthetic"},
    {"case_id": "S4_number_swap_excluded", "category": "exclusion_check",
     "expected": "BLOCKING(数値の付け替え。changed_numberが立つため対象外=決定論BLOCKINGのまま)",
     "instance_id": "safety_A2A3", "related_fact_id": "HF-003", "flags": ["changed_number", "changed_comparison"],
     "claim_text": "Oil prices rose 20% after the plan was withdrawn.",
     "issue": "The 20% in the Ledger is the proposed reimbursement rate, not a price increase.",
     "issue_source": "synthetic"},
    {"case_id": "S5_safety12_time_2019", "category": "serious_expected",
     "expected": "BLOCKING(Safety12のchanged_time fixture。CONFIRMEDが期待)",
     "instance_id": "safety_er009_changed_time", "related_fact_id": "F-001", "flags": ["changed_time"],
     "claim_text": "In 2019, researchers published a study in the American Economic Journal: Applied Economics showing that higher suggested tip rates led New York City taxi passengers to leave more money.",
     "issue": "The Ledger cites the study as published in 2014, not 2019.",
     "issue_source": "synthetic(related_fact_idは本scriptで付与=F-001)"},
    {"case_id": "S6_safety12_comparison_lower", "category": "serious_expected",
     "expected": "BLOCKING(Safety12のchanged_comparison fixture。方向反転、解放したらSTOP)",
     "instance_id": "safety_er009_changed_comparison", "related_fact_id": "F-004", "flags": ["changed_comparison"],
     "claim_text": "Passengers who saw LOWER suggested tip rates left more money than those who saw higher suggested rates, according to the New York City taxi study.",
     "issue": "The Ledger says passengers who saw HIGHER suggested rates left more money; the claim reverses the comparison.",
     "issue_source": "synthetic(related_fact_idは本scriptで付与=F-004)"},
    {"case_id": "S7_A5_0_put_back", "category": "serious_expected",
     "expected": "BLOCKING(A5-0=時期・経過の創作。解放したらSTOP)",
     "instance_id": "safety_A5", "related_fact_id": "MUSE-HC-012", "flags": ["changed_time"],
     "claim_text": "They also temporarily put back the feature in which humans handled the calls. They did not stop Muse itself.",
     "issue": "The article says the human-handled feature was temporarily put back (rolled back and then restored), whereas the Ledger only says the feature was rolled back for now; the claim invents a restoration in the timeline.",
     "issue_source": "synthetic(記録のdevはchanged_factのみ。時期の創作として合成)"},
    {"case_id": "S8_K18_A2A3_0_actor_excluded", "category": "exclusion_check",
     "expected": "BLOCKING(K18=A2A3-0は主体=対象外確認。決定論BLOCKINGのまま)",
     "instance_id": "safety_A2A3", "related_fact_id": "HF-003", "flags": ["changed_actor", "changed_comparison"],
     "claim_text": "The idea was that those carrying the cargo would repay the money the United States spends to keep the strait safe.",
     "issue": "The article identifies cargo carriers as the payers, although the Ledger says the proposal did not specify who would be liable to pay.",
     "issue_source": "recorded(iter6 safety_A2A3、フラグは主体を付けて合成)"},
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
    parser.add_argument("--n-serious", type=int, default=5)
    parser.add_argument("--n-release", type=int, default=3)
    parser.add_argument("--budget-jpy", type=float, default=30.0)
    args = parser.parse_args()
    runner.FLOOR_VERIFY_MODE = runner.FLOOR_VERIFY_MODE_COMPARISON_TIME
    if args.stage == "agg":
        return agg()
    client = vfl01.get_client()
    state = _load_state()
    fixtures = _fixtures()
    stopped, stop_reason = False, None
    if args.stage == "probe":
        case = CASES[0]
        raw: list = []
        t0 = time.time()
        # 単価確認: 1ケース×1回(確認callは1回だけ。floor_verify_evaluateは2回呼ぶため直接1回呼ぶ)
        fx = fixtures[case["instance_id"]]
        fb = runner.floor_verify_fact_block(fx["ledger_text"], case["related_fact_id"])
        lc, _ = s2p.build_local_context(fx["article_text"], case["claim_text"])
        res = runner.run_floor_verify_call(client, case["claim_text"], lc, fb, case["issue"], ["comparison"],
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
        res = {"case_id": case["case_id"], "category": case["category"], "expected": case["expected"],
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
        rows.append({"case_id": case["case_id"], "category": case["category"], "expected": case["expected"],
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
