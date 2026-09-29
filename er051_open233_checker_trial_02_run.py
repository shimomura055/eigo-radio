# -*- coding: utf-8 -*-
# ============================================================
# er051_open233_checker_trial_02_run.py
# OPEN-233-CHECKER-REDESIGN-TRIAL-01 (Step2診断+Trial 2、委任_03)
# ============================================================
# 目的: (a) Step2診断(境界群5 fixture、V2/V3、原因分析専用、Safety未達
# variantでもStep2を実行してよいというFable判定(1)に基づく)と、
# (b) Trial 2(V4-A、Step1重大群12+changed_actor n=5+Step2境界群5+条件付き
# Step3非決定性群20)を実行するharness。
#
# 重要な設計制約(委任文より):
# - Production code(er003_v1_en_direct_vfl_01_generate.py、以下vfl01)は
#   一切変更しない。本ファイルはvfl01/er050/er051をimportのみで使用する。
# - Model Routing Contractは経由しない(er050/er051_...trial_01_run.pyと
#   同じ方式、model文字列を直接渡す)。
# - fixtureはer050_gpt6_checker_comparison_trial_01.py(g6)のstep1/2/3_
#   fixtures()をそのまま再利用する(新規fixture作成なし)。
# - V4-Aはer051_open233_checker_trial_variant_01.pyへ追加済み
#   (Prompt=V2差分ブロック+境界明確化ブロック、schema/post-hocはV2と同一)。
#
# Guardrail: 本委任(委任_03)単体¥50(累計¥400枠のうち、Trial 1委任_02
# ¥7.2882の残り¥392.7118の一部)。予算状態は本ファイル専用の
# budget_state_c233c.json(diag/Trial 2の両方のphaseで共有、Trial 1の
# budget_state.jsonとは別ファイル)で管理する。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial

BASE_DIR = "er051_output/open233_checker_trial_01"
OUT_DIRS = {
    "diag_step2": f"{BASE_DIR}/trial_01_step2_diag",
    "trial2_step1": f"{BASE_DIR}/trial_02/step1",
    "trial2_step1_changed_actor_n5": f"{BASE_DIR}/trial_02/step1_changed_actor_n5",
    "trial2_step2": f"{BASE_DIR}/trial_02/step2",
    "trial2_step3": f"{BASE_DIR}/trial_02/step3",
}
# 本委任(委任_03)専用の予算状態ファイル(diag/Trial 2の全phaseで共有し累計¥50を管理)。
BUDGET_STATE_PATH = f"{BASE_DIR}/trial_02/c233c_budget_state.json"

MODEL = "gpt-6-luna"

# 正式単価(GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Closeout C-2、$/1M tokens)
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50
USD_JPY = 156.88

TOTAL_BUDGET_JPY = 50.0  # 本委任(委任_03)単体のGuardrail(§1(5))

MAX_RETRIES_PER_CALL = 2  # 合計最大3 attempt
MAX_CONSECUTIVE_FIXTURE_ERRORS = 3


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


NOTES_CLASSIFICATION = {**trial.HORMUZ_NOTES_CLASSIFICATION, **trial.META_NOTES_CLASSIFICATION}


def ledger_text_for_variant(fixture: dict, variant: str) -> str:
    if variant == "V3":
        return trial.filter_ledger_notes_by_classification(fixture["ledger_text"], NOTES_CLASSIFICATION)
    return fixture["ledger_text"]


def save_run(out_dir: str, fixture_id: str, variant: str, attempt: int, result: dict | None,
             error: str | None, attempts_used: int) -> str:
    d = f"{out_dir}/{fixture_id}/{variant}"
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


def execute(phase: str, jobs: list) -> dict:
    """jobs: list of (fixture, variant, attempt_index)。累計(本委任¥50)を
    呼び出し前に確認し、超過見込みなら以降のjobをskipする(既実行分は保存済み)。
    API errorがMAX_CONSECUTIVE_FIXTURE_ERRORS連続したらTrial全体をabortする。"""
    out_dir = OUT_DIRS[phase]
    client = vfl01.get_client()
    state = load_budget_state()
    summary = {"phase": phase, "jobs": [], "stopped": False, "stop_reason": None}
    consecutive_errors = 0

    for fixture, variant, attempt in jobs:
        if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
            summary["stopped"] = True
            summary["stop_reason"] = f"累計¥{state['cumulative_jpy']:.3f}が本委任Guardrail¥{TOTAL_BUDGET_JPY}に到達"
            summary["jobs"].append({"fixture": fixture["id"], "variant": variant, "attempt": attempt,
                                     "skipped": True, "reason": summary["stop_reason"]})
            continue

        result, error, attempts_used = run_one_call(client, fixture, variant)
        state["cumulative_calls"] += 1
        if result is not None:
            cost = official_cost_jpy(result["usage"])
            state["cumulative_jpy"] += cost
            state["history"].append({
                "phase": phase, "fixture": fixture["id"], "variant": variant, "attempt": attempt,
                "usage": result["usage"], "cost_jpy": round(cost, 4), "elapsed_seconds": result["elapsed_seconds"],
                "attempts_used": attempts_used,
            })
            save_run(out_dir, fixture["id"], variant, attempt, result, None, attempts_used)
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
            save_run(out_dir, fixture["id"], variant, attempt, None, error, attempts_used)
            summary["jobs"].append({"fixture": fixture["id"], "variant": variant, "attempt": attempt,
                                     "error": error, "attempts_used": attempts_used})
            consecutive_errors += 1
        save_budget_state(state)

        if consecutive_errors >= MAX_CONSECUTIVE_FIXTURE_ERRORS:
            summary["stopped"] = True
            summary["stop_reason"] = f"API errorが{MAX_CONSECUTIVE_FIXTURE_ERRORS}fixture連続(STOP条件)"
            os.makedirs(out_dir, exist_ok=True)
            with open(f"{out_dir}/summary_{phase}.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            raise TrialAbort(summary["stop_reason"])

    summary["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    summary["cumulative_calls"] = state["cumulative_calls"]
    summary["cumulative_errors"] = state["cumulative_errors"]
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/summary_{phase}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def build_jobs_step2(variants: list) -> list:
    fixtures = g6.step2_fixtures()
    return [(fx, v, 1) for fx in fixtures for v in variants]


def build_jobs_step1(variant: str) -> list:
    fixtures = g6.step1_fixtures()
    return [(fx, variant, 1) for fx in fixtures]


def build_jobs_changed_actor_n5(variant: str) -> list:
    fixtures = g6.filter_fixtures_by_id(g6.step1_fixtures(), "er009_changed_actor")
    fx = fixtures[0]
    return [(fx, variant, attempt) for attempt in range(1, 6)]


def build_jobs_step3(variant: str) -> list:
    fixtures = g6.step3_fixtures()
    return [(fx, variant, attempt) for fx in fixtures for attempt in range(1, 6)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=list(OUT_DIRS.keys()))
    parser.add_argument("--variants", default="V2,V3",
                         help="diag_step2/trial2_step2: comma-separated. trial2_step1/"
                              "trial2_step1_changed_actor_n5/trial2_step3: single variant")
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

    if args.phase == "diag_step2":
        jobs = build_jobs_step2(variants)
    elif args.phase == "trial2_step1":
        assert len(variants) == 1
        jobs = build_jobs_step1(variants[0])
    elif args.phase == "trial2_step1_changed_actor_n5":
        assert len(variants) == 1
        jobs = build_jobs_changed_actor_n5(variants[0])
    elif args.phase == "trial2_step2":
        jobs = build_jobs_step2(variants)
    else:
        assert len(variants) == 1, "trial2_step3は最良variant1つのみ"
        jobs = build_jobs_step3(variants[0])

    summary = execute(args.phase, jobs)

    print(json.dumps({
        "phase": args.phase, "stopped": summary["stopped"], "stop_reason": summary["stop_reason"],
        "cumulative_jpy": summary["cumulative_jpy"], "cumulative_calls": summary["cumulative_calls"],
        "cumulative_errors": summary["cumulative_errors"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
