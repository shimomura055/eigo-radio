# -*- coding: utf-8 -*-
# ============================================================
# er051_open233_checker_trial_01_run.py
# OPEN-233-CHECKER-REDESIGN-TRIAL-01 (Trial 1実行、委任_02)
# ============================================================
# 目的: er051_open233_checker_trial_variant_01.py(Family X限定Trial
# variant V2/V3、Production非接続)を使い、実際にAPI呼び出しを行って
# Trial 1(Step1重大群+changed_actor n=5/Step2境界群/Step3非決定性群)を
# 実行するharness。
#
# 重要な設計制約(委任文より):
# - Production code(er003_v1_en_direct_vfl_01_generate.py、以下vfl01)は
#   一切変更しない。本ファイルはvfl01/er051をimportのみで使用する。
# - Model Routing Contractは経由しない(Trial harnessはContract非経由で
#   model文字列を直接渡す、er050と同じ方式)。
# - fixtureはer050_gpt6_checker_comparison_trial_01.py(以下g6)の
#   step1_fixtures()/step2_fixtures()/step3_fixtures()をそのまま再利用する
#   (新規fixture作成はしない)。
# - V0/V1は既存er050_output/のデータ再利用(0 call、本ファイルでは呼ばない)。
#   本ファイルが新規に呼び出すのはV2/V3のみ。
#
# 費用: gpt-6-luna正式単価(Input $0.10/Cached $0.01/Output $0.50 per 1M、
# GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Closeout C-2)× 実測usage ×
# ¥156.88/USD(Frankfurter API、2026-09-28付、同REPORT記載値)。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial

OUT_DIR = "er051_output/open233_checker_trial_01/trial_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state.json"

MODEL = "gpt-6-luna"

# 正式単価(GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Closeout C-2、$/1M tokens)
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50
USD_JPY = 156.88

STEP_BUDGET_JPY = {"step1": 8.0, "step2": 6.0, "step3": 12.0}
TOTAL_BUDGET_JPY = 50.0

NOTES_CLASSIFICATION = {**trial.HORMUZ_NOTES_CLASSIFICATION, **trial.META_NOTES_CLASSIFICATION}

MAX_RETRIES_PER_CALL = 2  # 合計最大3 attempt
MAX_CONSECUTIVE_FIXTURE_ERRORS = 3


class TrialAbort(RuntimeError):
    pass


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
    return {
        "cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0,
        "by_step_jpy": {}, "history": [],
    }


def save_budget_state(state: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def ledger_text_for_variant(fixture: dict, variant: str) -> str:
    if variant == "V3":
        return trial.filter_ledger_notes_by_classification(fixture["ledger_text"], NOTES_CLASSIFICATION)
    return fixture["ledger_text"]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def save_run(step_name: str, fixture_id: str, variant: str, attempt: int, result: dict | None,
             error: str | None, attempts_used: int) -> str:
    d = f"{OUT_DIR}/{step_name}/{fixture_id}/{variant}"
    os.makedirs(d, exist_ok=True)
    path = f"{d}/run_{attempt}.json"
    payload = {
        "fixture_id": fixture_id, "variant": variant, "model": MODEL, "attempt": attempt,
        "attempts_used": attempts_used, "error": error,
    }
    if result is not None:
        payload.update({
            "prompt_sha256": sha256_text(result["prompt"]),
            "model_returned": result["model"],
            "response_id": result["response_id"],
            "usage": result["usage"],
            "elapsed_seconds": result["elapsed_seconds"],
            "raw_parsed": result["raw_parsed"],
            "parsed": result["parsed"],
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def run_one_call(client, fixture: dict, variant: str) -> tuple[dict | None, str | None, int]:
    ledger_text = ledger_text_for_variant(fixture, variant)
    last_err = None
    for attempt_i in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, ledger_text, fixture["article_text"], MODEL, variant,
                include_related_fact_id=fixture.get("include_related_fact_id", False),
                source_article_text=fixture.get("source_article_text"),
            )
            return result, None, attempt_i + 1
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    return None, last_err, 1 + MAX_RETRIES_PER_CALL


def execute(step_name: str, jobs: list, budget_note: str) -> dict:
    """jobs: list of (fixture, variant, attempt_index)。budget_note: step別上限のkey
    ("step1"/"step2"/"step3")。呼び出し前に累計(全体¥50/当該step上限)を確認し、
    超過見込みならそのjob以降をskipする(既実行分は保存済み)。API errorが
    MAX_CONSECUTIVE_FIXTURE_ERRORS連続したらTrial全体をabortする(呼び出し元で捕捉)。"""
    client = vfl01.get_client()
    state = load_budget_state()
    state["by_step_jpy"].setdefault(budget_note, 0.0)
    summary = {"step": step_name, "budget_key": budget_note, "jobs": [], "stopped": False, "stop_reason": None}
    consecutive_errors = 0

    for fixture, variant, attempt in jobs:
        step_spent = state["by_step_jpy"][budget_note]
        if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
            summary["stopped"] = True
            summary["stop_reason"] = f"累計¥{state['cumulative_jpy']:.3f}が総枠¥{TOTAL_BUDGET_JPY}に到達"
            summary["jobs"].append({"fixture": fixture["id"], "variant": variant, "attempt": attempt,
                                     "skipped": True, "reason": summary["stop_reason"]})
            continue
        if step_spent >= STEP_BUDGET_JPY[budget_note]:
            summary["stopped"] = True
            summary["stop_reason"] = f"{budget_note}累計¥{step_spent:.3f}が上限¥{STEP_BUDGET_JPY[budget_note]}に到達"
            summary["jobs"].append({"fixture": fixture["id"], "variant": variant, "attempt": attempt,
                                     "skipped": True, "reason": summary["stop_reason"]})
            continue

        result, error, attempts_used = run_one_call(client, fixture, variant)
        state["cumulative_calls"] += 1
        if result is not None:
            cost = official_cost_jpy(result["usage"])
            state["cumulative_jpy"] += cost
            state["by_step_jpy"][budget_note] += cost
            state["history"].append({
                "step": step_name, "fixture": fixture["id"], "variant": variant, "attempt": attempt,
                "usage": result["usage"], "cost_jpy": round(cost, 4), "elapsed_seconds": result["elapsed_seconds"],
                "attempts_used": attempts_used,
            })
            save_run(step_name, fixture["id"], variant, attempt, result, None, attempts_used)
            summary["jobs"].append({
                "fixture": fixture["id"], "variant": variant, "attempt": attempt,
                "overall_status": result["parsed"]["overall_status"],
                "overall_action_trial": result["parsed"]["overall_action_trial"],
                "deviations": result["parsed"]["deviations"],
                "usage": result["usage"], "cost_jpy": round(cost, 4),
                "elapsed_seconds": result["elapsed_seconds"], "attempts_used": attempts_used,
            })
            consecutive_errors = 0
        else:
            state["cumulative_errors"] += 1
            save_run(step_name, fixture["id"], variant, attempt, None, error, attempts_used)
            summary["jobs"].append({"fixture": fixture["id"], "variant": variant, "attempt": attempt,
                                     "error": error, "attempts_used": attempts_used})
            consecutive_errors += 1
        save_budget_state(state)

        if consecutive_errors >= MAX_CONSECUTIVE_FIXTURE_ERRORS:
            summary["stopped"] = True
            summary["stop_reason"] = f"API errorが{MAX_CONSECUTIVE_FIXTURE_ERRORS}fixture連続(STOP条件)"
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(f"{OUT_DIR}/summary_{step_name}.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            raise TrialAbort(summary["stop_reason"])

    summary["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    summary["cumulative_calls"] = state["cumulative_calls"]
    summary["cumulative_errors"] = state["cumulative_errors"]
    summary["by_step_jpy"] = {k: round(v, 4) for k, v in state["by_step_jpy"].items()}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/summary_{step_name}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def build_jobs_step1(variants: list) -> list:
    fixtures = g6.step1_fixtures()
    jobs = [(fx, v, 1) for fx in fixtures for v in variants]
    return jobs


def build_jobs_changed_actor_n5(variants: list) -> list:
    fixtures = g6.filter_fixtures_by_id(g6.step1_fixtures(), "er009_changed_actor")
    fx = fixtures[0]
    jobs = [(fx, v, attempt) for v in variants for attempt in range(1, 6)]
    return jobs


def build_jobs_step2(variants: list) -> list:
    fixtures = g6.step2_fixtures()
    jobs = [(fx, v, 1) for fx in fixtures for v in variants]
    return jobs


def build_jobs_step3(variant: str) -> list:
    fixtures = g6.step3_fixtures()
    jobs = [(fx, variant, attempt) for fx in fixtures for attempt in range(1, 6)]
    return jobs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True,
                         choices=["step1", "step1_changed_actor_n5", "step2", "step3"])
    parser.add_argument("--variants", default="V2,V3", help="comma-separated (V2,V3) or single variant for step3")
    args = parser.parse_args()

    verify = {
        "DEVIATION_PROMPT_TEMPLATE": sha256_text(vfl01.DEVIATION_PROMPT_TEMPLATE),
        "DEVIATION_DEVELOPER_MESSAGE": sha256_text(vfl01.DEVIATION_DEVELOPER_MESSAGE),
        "DEVIATION_JSON_SCHEMA": sha256_text(json.dumps(vfl01.DEVIATION_JSON_SCHEMA, sort_keys=True)),
    }
    mismatches = {k: v for k, v in verify.items() if v != g6.PHASE_A_SHA256[k]}
    if mismatches:
        raise RuntimeError(f"固定性検証NG(Phase A記録と不一致、STOP): {mismatches}")

    variants = [v.strip() for v in args.variants.split(",") if v.strip()]

    if args.phase == "step1":
        jobs = build_jobs_step1(variants)
        summary = execute("step1", jobs, "step1")
    elif args.phase == "step1_changed_actor_n5":
        jobs = build_jobs_changed_actor_n5(variants)
        summary = execute("step1_changed_actor_n5", jobs, "step1")
    elif args.phase == "step2":
        jobs = build_jobs_step2(variants)
        summary = execute("step2", jobs, "step2")
    else:
        assert len(variants) == 1, "step3は最良variant1つのみ"
        jobs = build_jobs_step3(variants[0])
        summary = execute("step3", jobs, "step3")

    print(json.dumps({
        "phase": args.phase, "stopped": summary["stopped"], "stop_reason": summary["stop_reason"],
        "cumulative_jpy": summary["cumulative_jpy"], "cumulative_calls": summary["cumulative_calls"],
        "cumulative_errors": summary["cumulative_errors"], "by_step_jpy": summary["by_step_jpy"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
