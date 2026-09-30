# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_phase1_step3_stage1_compare_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ③、委任_07)
# ============================================================
# 目的: design書§9-1③(V0/V4-A/S1-D Stage1 variant比較)を実行するharness。
# (a) Safety群12 fixture: S1-Dのみ新規call(V0/V4-Aは既存er050_output/
#     er051_output/trial_02出力を再利用、0 call)。
# (b) er009_changed_actor: 既存n=5(V0/V4-A)に追加call(V0はvfl01.
#     run_deviation_check直接呼び出し、V4-Aはtrial.run_trial_deviation_check)
#     し各n=15化。S1-Dは新規n=15。
# (c) negative候補7記事: V4-A/S1-Dを新規実行(V0は既存deviations=[]記録を
#     再利用、0 call)。
# (d) B群5 fixture: S1-Dのみ新規call(V0/V4-Aは既存trial_02出力を再利用)。
# (e) hormuz_run03_standard/Meta_run03_standard: S1-Dのみ新規n=5×2
#     (V0/V4-Aは既存trial_03_stability_n20出力を再利用)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
# - Model Routing Contractは経由しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_s1d_trial_01 as s1d

OUT_DIR = "er052_output/open233_self_recovery_phase1_step3_stage1_compare_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233k.json"

MODEL = "gpt-6-luna"
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50
USD_JPY = 156.88

TOTAL_BUDGET_JPY = 35.0  # 委任_07 Guardrail(作業A+作業B共有)
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3


class TrialAbort(RuntimeError):
    pass


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def official_cost_jpy(usage: dict) -> float:
    it = usage.get("input_tokens") or 0
    ct = usage.get("cached_input_tokens") or 0
    ot = usage.get("output_tokens") or 0
    billable_in = max(it - ct, 0)
    cost_usd = billable_in / 1e6 * PRICE_IN + ct / 1e6 * PRICE_CACHED + ot / 1e6 * PRICE_OUT
    return cost_usd * USD_JPY


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_budget(state: dict) -> None:
    if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_07 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------
# 呼び出しラッパー(V0/V4A/S1D共通、budget/retry/error管理)
# ------------------------------------------------------------
def call_v0(client, fixture: dict) -> dict:
    kwargs = {"model": MODEL, "hook_aware": fixture.get("hook_aware", False)}
    if fixture.get("include_related_fact_id"):
        kwargs["include_related_fact_id"] = True
    if fixture.get("source_article_text") is not None:
        kwargs["source_article_text"] = fixture["source_article_text"]
    result = vfl01.run_deviation_check(client, fixture["ledger_text"], fixture["article_text"], **kwargs)
    return {
        "prompt_sha256": sha256_text(result["prompt"]), "model_returned": result["model"],
        "response_id": result["response_id"], "usage": result["usage"],
        "elapsed_seconds": result["elapsed_seconds"], "parsed": result["parsed"],
        "cost_jpy": round(official_cost_jpy(result["usage"]), 4),
    }


def call_v4a(client, fixture: dict) -> dict:
    result = trial.run_trial_deviation_check(
        client, fixture["ledger_text"], fixture["article_text"], MODEL, "V4A",
        include_related_fact_id=fixture.get("include_related_fact_id", False),
        source_article_text=fixture.get("source_article_text"),
    )
    return {
        "prompt_sha256": sha256_text(result["prompt"]), "model_returned": result["model"],
        "response_id": result["response_id"], "usage": result["usage"],
        "elapsed_seconds": result["elapsed_seconds"], "parsed": result["parsed"],
        "cost_jpy": round(official_cost_jpy(result["usage"]), 4),
    }


def call_s1d(client, fixture: dict) -> dict:
    result = s1d.run_s1d_check(
        client, fixture["ledger_text"], fixture["article_text"],
        source_article_text=fixture.get("source_article_text"),
    )
    return {
        "prompt_sha256": result["prompt_sha256"], "model_returned": result["model"],
        "response_id": result["response_id"], "usage": result["usage"],
        "elapsed_seconds": result["elapsed_seconds"], "parsed": result["parsed"],
        "cost_jpy": result["cost_jpy"],
    }


CALLERS = {"V0": call_v0, "V4A": call_v4a, "S1D": call_s1d}


def run_calls(client, state: dict, jobs: list, consecutive_errors: list) -> list:
    """jobs: list of (label, fixture, variant, attempt, save_path)。
    consecutive_errorsはmutableな1要素list(呼び出し元と共有、跨task集計用)。"""
    results = []
    for label, fixture, variant, attempt, save_path in jobs:
        check_budget(state)
        last_err = None
        result = None
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                result = CALLERS[variant](client, fixture)
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        state["cumulative_calls"] += 1
        if result is not None:
            state["cumulative_jpy"] += result["cost_jpy"]
            state["history"].append({
                "label": label, "fixture": fixture["id"], "variant": variant, "attempt": attempt,
                "cost_jpy": result["cost_jpy"], "usage": result["usage"],
            })
            save_json(save_path, {
                "label": label, "fixture_id": fixture["id"], "variant": variant, "attempt": attempt,
                **{k: v for k, v in result.items() if k != "parsed"}, "parsed": result["parsed"],
            })
            results.append({"label": label, "fixture_id": fixture["id"], "variant": variant,
                             "attempt": attempt, "parsed": result["parsed"], "cost_jpy": result["cost_jpy"]})
            consecutive_errors[0] = 0
        else:
            state["cumulative_errors"] += 1
            save_json(save_path, {"label": label, "fixture_id": fixture["id"], "variant": variant,
                                   "attempt": attempt, "error": last_err})
            results.append({"label": label, "fixture_id": fixture["id"], "variant": variant,
                             "attempt": attempt, "error": last_err})
            consecutive_errors[0] += 1
        save_budget_state(state)
        if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
            raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")
    return results


# ------------------------------------------------------------
# (a) Safety群12 fixture: S1-Dのみ
# ------------------------------------------------------------
def task_a_safety_group(client, state: dict, consecutive_errors: list) -> list:
    fixtures = g6.step1_fixtures()
    jobs = [("a_safety", fx, "S1D", 1, f"{OUT_DIR}/a_safety_group/{fx['id']}/S1D/run_1.json") for fx in fixtures]
    return run_calls(client, state, jobs, consecutive_errors)


# ------------------------------------------------------------
# (b) changed_actor n15: V0+10/V4A+10/S1D+15
# ------------------------------------------------------------
def task_b_changed_actor(client, state: dict, consecutive_errors: list) -> list:
    fixtures = g6.filter_fixtures_by_id(g6.step1_fixtures(), "er009_changed_actor")
    fx = fixtures[0]
    jobs = []
    for attempt in range(6, 16):  # 既存n=5に追加し n=15化(attempt 6..15)
        jobs.append(("b_changed_actor_v0_extra", fx, "V0", attempt,
                      f"{OUT_DIR}/b_changed_actor/V0_extra/run_{attempt}.json"))
    for attempt in range(6, 16):
        jobs.append(("b_changed_actor_v4a_extra", fx, "V4A", attempt,
                      f"{OUT_DIR}/b_changed_actor/V4A_extra/run_{attempt}.json"))
    for attempt in range(1, 16):
        jobs.append(("b_changed_actor_s1d", fx, "S1D", attempt,
                      f"{OUT_DIR}/b_changed_actor/S1D/run_{attempt}.json"))
    return run_calls(client, state, jobs, consecutive_errors)


# ------------------------------------------------------------
# (c) negative候補7記事: V4A+S1D新規(V0は既存deviations=[]記録流用)
# ------------------------------------------------------------
NEGATIVE_SOURCE_FILES = [
    ("neg1_meta_b3prod_a2", "er019_output/family_x_b3_production_wiring_01/run_01/a2/audit/"
     "deviation_checks/standard_attempt1.json"),
    ("neg2_meta_refresh_a2", "er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/"
     "deviation_checks/standard_attempt2.json"),
    ("neg3_hormuz_prodrunner_b1b", "er019_output/family_x_entertainment_production_runner_01/"
     "an3_t0_wiring_regression_01/hormuz/b1b/audit/deviation_checks/advanced_attempt2.json"),
    ("neg4_smallbag_div_a2", "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/"
     "audit/deviation_checks/standard_attempt1.json"),
    ("neg5_hormuz_div_a2", "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/audit/"
     "deviation_checks/standard_attempt1.json"),
    ("neg6_smallbag_div_b1b", "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/"
     "audit/deviation_checks/advanced_attempt1.json"),
    ("neg7_meta_prodrunner_b1b", "er019_output/family_x_entertainment_production_runner_01/"
     "an3_t0_wiring_regression_01/meta/b1b/audit/deviation_checks/advanced_attempt1.json"),
]


def load_negative_fixture(fixture_id: str, path: str) -> dict:
    return g6.load_audit_fixture(fixture_id, path, "negative候補出典(既存LEDGER_COMPLIANT記事、"
                                  "docs/pm/negative_claim_candidates_open233_01.md)")


def task_c_negative_candidates(client, state: dict, consecutive_errors: list) -> list:
    jobs = []
    for fixture_id, path in NEGATIVE_SOURCE_FILES:
        fx = load_negative_fixture(fixture_id, path)
        jobs.append(("c_negative_v4a", fx, "V4A", 1, f"{OUT_DIR}/c_negative/{fixture_id}/V4A/run_1.json"))
        jobs.append(("c_negative_s1d", fx, "S1D", 1, f"{OUT_DIR}/c_negative/{fixture_id}/S1D/run_1.json"))
    return run_calls(client, state, jobs, consecutive_errors)


# ------------------------------------------------------------
# (d) B群5 fixture: S1-Dのみ
# ------------------------------------------------------------
def task_d_b_group(client, state: dict, consecutive_errors: list) -> list:
    fixtures = g6.step2_fixtures()
    jobs = [("d_b_group", fx, "S1D", 1, f"{OUT_DIR}/d_b_group/{fx['id']}/S1D/run_1.json") for fx in fixtures]
    return run_calls(client, state, jobs, consecutive_errors)


# ------------------------------------------------------------
# (e) hormuz_run03_standard/Meta_run03_standard n5: S1-Dのみ
# ------------------------------------------------------------
def task_e_hormuz_meta_n5(client, state: dict, consecutive_errors: list) -> list:
    fixtures = g6.filter_fixtures_by_id(g6.step3_fixtures(), "hormuz_run03_standard")
    fixtures += g6.filter_fixtures_by_id(g6.step2_fixtures(), "Meta_run03_standard")
    jobs = []
    for fx in fixtures:
        for attempt in range(1, 6):
            jobs.append(("e_hormuz_meta_n5", fx, "S1D", attempt,
                          f"{OUT_DIR}/e_hormuz_meta_n5/{fx['id']}/S1D/run_{attempt}.json"))
    return run_calls(client, state, jobs, consecutive_errors)


TASKS = {
    "a": task_a_safety_group,
    "b": task_b_changed_actor,
    "c": task_c_negative_candidates,
    "d": task_d_b_group,
    "e": task_e_hormuz_meta_n5,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="a,b,c,d,e", help="comma-separated subset of a,b,c,d,e")
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    all_results = {}
    stopped = False
    stop_reason = None

    for t in [x.strip() for x in args.tasks.split(",") if x.strip()]:
        try:
            all_results[t] = TASKS[t](client, state, consecutive_errors)
        except TrialAbort as e:
            stopped = True
            stop_reason = str(e)
            all_results[t] = {"stopped": True, "reason": stop_reason}
            break

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "tasks_run": list(all_results.keys()),
    }
    save_json(f"{OUT_DIR}/summary_step3_stage1_compare.json", {"summary": summary, "results": all_results})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
