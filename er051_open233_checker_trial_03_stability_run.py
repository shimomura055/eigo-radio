# -*- coding: utf-8 -*-
# ============================================================
# er051_open233_checker_trial_03_stability_run.py
# OPEN-233-CHECKER-REDESIGN-TRIAL-01 (Stability n=20実測、委任_04)
# ============================================================
# 目的: Opus L2レビュー#1論点4の推奨1(測定を先に増やす)に従い、
# hormuz_run03_standard と Meta_run03_standard の2 fixtureについて、
# V0(現行Production Prompt/schemaそのまま)とV4-A(既存実装済み)の
# 2variant x n=20で検出率(recall)を実測する。**設計変更・variant実装・
# gold/指標変更は一切行わない**(既存er051_open233_checker_trial_variant_01.py
# は無変更で流用のみ)。
#
# 重要な設計制約(委任文より、委任_02/_03と同一原則):
# - Production code(er003_v1_en_direct_vfl_01_generate.py、以下vfl01)は
#   一切変更しない。本ファイルはvfl01/er050/er051をimportのみで使用する。
# - Model Routing Contractは経由しない(既存Trialと同じ方式)。
# - fixtureはer050_gpt6_checker_comparison_trial_01.py(g6)のstep2/3_
#   fixtures()からfilter_fixtures_by_id()で該当2件のみを取り出す
#   (新規fixture作成なし)。
#
# Guardrail: 本委任(委任_04)作業B単体¥40(累計¥400枠のうち、Trial1
# ¥7.2882+委任_03¥14.8285=累計¥22.1167の残り¥377.8833の一部)。
# 予算状態は本ファイル専用のc233d_budget_state.jsonで管理する
# (委任_03のc233c_budget_state.jsonとは別ファイル)。
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
OUT_DIR = f"{BASE_DIR}/trial_03_stability_n20"
BUDGET_STATE_PATH = f"{OUT_DIR}/c233d_budget_state.json"

MODEL = "gpt-6-luna"

# 正式単価(GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Closeout C-2、$/1M tokens)
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50
USD_JPY = 156.88

TOTAL_BUDGET_JPY = 40.0  # 本委任(委任_04)作業B単体のGuardrail

MAX_RETRIES_PER_CALL = 2  # 合計最大3 attempt(既存harnessと同一原則)
MAX_CONSECUTIVE_FIXTURE_ERRORS = 3

TARGET_FIXTURE_IDS = ["hormuz_run03_standard", "Meta_run03_standard"]
VARIANTS = ["V0", "V4A"]
N_PER_CELL = 20


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


def load_target_fixtures() -> dict:
    """hormuz_run03_standardはstep3_fixtures()、Meta_run03_standardは
    step2_fixtures()にそれぞれ存在するため、両方から取り出してid->fixtureの
    辞書を作る。source_sha256をdesign書記載値と突合する(委任文の
    「既存sha256と一致することを確認」に対応)。"""
    all_fx = {f["id"]: f for f in g6.step2_fixtures() + g6.step3_fixtures()}
    expected_sha256 = {
        "hormuz_run03_standard": "88f5ef99a1592c80cfd56372e7db1faa7aebb36308446b6225c106c655af8e38",
        "Meta_run03_standard": "4016b8cb25a13dbc1809c0a147e7e992f64808ee0ff396189c0fa342a04e79a0",
    }
    out = {}
    for fid in TARGET_FIXTURE_IDS:
        fx = all_fx[fid]
        if fx["source_sha256"] != expected_sha256[fid]:
            raise RuntimeError(
                f"fixture {fid}: source_sha256不一致(実測={fx['source_sha256']}, "
                f"design書記載={expected_sha256[fid]})、STOP"
            )
        out[fid] = fx
    return out


def save_run(fixture_id: str, variant: str, attempt: int, result: dict | None,
             error: str | None, attempts_used: int) -> str:
    d = f"{OUT_DIR}/{fixture_id}/{variant}"
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
    last_err = None
    for attempt_i in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, fixture["ledger_text"], fixture["article_text"], MODEL, variant,
                include_related_fact_id=fixture.get("include_related_fact_id", False),
                source_article_text=fixture.get("source_article_text"),
            )
            return result, None, attempt_i + 1
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    return None, last_err, 1 + MAX_RETRIES_PER_CALL


def run_already_done(fixture_id: str, variant: str, attempt: int) -> bool:
    """既にsave_run()で保存済みかつerrorがNoneのrun_N.jsonがあればTrueを返す
    (システム都合[メモリ不足等]で中断した場合の再開用、委任_04追記。
    課金済みcallを再実行しないための安全策。APIの仕様・費用計算・出力形式は
    一切変更しない)。"""
    path = f"{OUT_DIR}/{fixture_id}/{variant}/run_{attempt}.json"
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("error") is None and "parsed" in d


def build_jobs(fixtures: dict, resume: bool = False) -> list:
    jobs = []
    for fid in TARGET_FIXTURE_IDS:
        for variant in VARIANTS:
            for attempt in range(1, N_PER_CELL + 1):
                if resume and run_already_done(fid, variant, attempt):
                    continue
                jobs.append((fixtures[fid], variant, attempt))
    return jobs


def execute(jobs: list) -> dict:
    client = vfl01.get_client()
    state = load_budget_state()
    summary = {"phase": "trial_03_stability_n20", "jobs": [], "stopped": False, "stop_reason": None}
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
                "fixture": fixture["id"], "variant": variant, "attempt": attempt,
                "usage": result["usage"], "cost_jpy": round(cost, 4), "elapsed_seconds": result["elapsed_seconds"],
                "attempts_used": attempts_used,
            })
            save_run(fixture["id"], variant, attempt, result, None, attempts_used)
            usage = result["usage"]
            summary["jobs"].append({
                "fixture": fixture["id"], "variant": variant, "attempt": attempt,
                "overall_status": result["parsed"]["overall_status"],
                "overall_action_trial": result["parsed"]["overall_action_trial"],
                "deviations": result["parsed"]["deviations"],
                "usage": usage, "reasoning_tokens": usage.get("reasoning_tokens"),
                "cost_jpy": round(cost, 4),
                "elapsed_seconds": result["elapsed_seconds"], "attempts_used": attempts_used,
            })
            consecutive_errors = 0
        else:
            state["cumulative_errors"] += 1
            save_run(fixture["id"], variant, attempt, None, error, attempts_used)
            summary["jobs"].append({"fixture": fixture["id"], "variant": variant, "attempt": attempt,
                                     "error": error, "attempts_used": attempts_used})
            consecutive_errors += 1
        save_budget_state(state)

        if consecutive_errors >= MAX_CONSECUTIVE_FIXTURE_ERRORS:
            summary["stopped"] = True
            summary["stop_reason"] = f"API errorが{MAX_CONSECUTIVE_FIXTURE_ERRORS}fixture連続(STOP条件)"
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(f"{OUT_DIR}/summary_trial_03_stability_n20.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            raise TrialAbort(summary["stop_reason"])

    summary["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    summary["cumulative_calls"] = state["cumulative_calls"]
    summary["cumulative_errors"] = state["cumulative_errors"]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/summary_trial_03_stability_n20.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="fixture読込・sha256検証のみ行いAPI呼び出しをしない")
    parser.add_argument("--resume", action="store_true",
                         help="既に成功保存済みのrun_N.jsonをスキップして残りのjobのみ実行する"
                              "(中断再開用、委任_04追記)")
    args = parser.parse_args()

    verify = {
        "DEVIATION_PROMPT_TEMPLATE": sha256_text(vfl01.DEVIATION_PROMPT_TEMPLATE),
        "DEVIATION_DEVELOPER_MESSAGE": sha256_text(vfl01.DEVIATION_DEVELOPER_MESSAGE),
        "DEVIATION_JSON_SCHEMA": sha256_text(json.dumps(vfl01.DEVIATION_JSON_SCHEMA, sort_keys=True)),
    }
    mismatches = {k: v for k, v in verify.items() if v != g6.PHASE_A_SHA256[k]}
    if mismatches:
        raise RuntimeError(f"固定性検証NG(Phase A記録と不一致、STOP): {mismatches}")

    fixtures = load_target_fixtures()

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "fixtures_verified": {fid: fx["source_sha256"] for fid, fx in fixtures.items()},
            "job_count": len(build_jobs(fixtures, args.resume)),
        }, ensure_ascii=False, indent=2))
        return

    jobs = build_jobs(fixtures, args.resume)
    summary = execute(jobs)

    print(json.dumps({
        "stopped": summary["stopped"], "stop_reason": summary["stop_reason"],
        "cumulative_jpy": summary["cumulative_jpy"], "cumulative_calls": summary["cumulative_calls"],
        "cumulative_errors": summary["cumulative_errors"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
