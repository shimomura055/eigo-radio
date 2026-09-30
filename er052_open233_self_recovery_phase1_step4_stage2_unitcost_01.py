# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_phase1_step4_stage2_unitcost_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ④、委任_07)
# ============================================================
# 目的: design書§9-1④(Stage2実単価・per-claim vs batch・prompt caching)を
# 実行するharness。B4(4 claim)/B1(2 claim)を対象に、per-claim call・
# instance batch callを同一入力で実行し、判定一致率・単価・latencyを比較
# する。あわせて同一Ledger prefixに対する連続2 callでprompt cachingの
# 受理可否・削減率を実測する。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
# - Model Routing Contractは経由しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01"
BUDGET_STATE_PATH = "er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/budget_state_c233k.json"
TOTAL_BUDGET_JPY = 35.0  # 委任_07 Guardrail(作業A+作業B共有、同一状態ファイルで管理)
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3

# B4/B1のBLOCKING確定claim(既存V4A run_1.json、trial_02/step2出力より抽出、
# 新規APIコール無し・既存jsonのread-onlyロード)
V4A_STEP2_DIR = "er051_output/open233_checker_trial_01/trial_02/step2"


class TrialAbort(RuntimeError):
    pass


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


def load_v4a_blocking_claims(fixture_id: str) -> list:
    path = f"{V4A_STEP2_DIR}/{fixture_id}/V4A/run_1.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    devs = d["parsed"]["deviations"]
    return [dv for dv in devs if dv.get("severity_final") == "BLOCKING"]


def get_fixture(fixture_id: str) -> dict:
    fixtures = g6.step2_fixtures()
    by_id = {f["id"]: f for f in fixtures}
    return by_id[fixture_id]


def build_claim_records(fixture: dict, blocking_devs: list) -> list:
    out = []
    for dv in blocking_devs:
        claim_text = dv.get("claim_in_article", "")
        local_context, fallback = s2p.build_local_context(fixture["article_text"], claim_text)
        out.append({
            "claim_text": claim_text, "origin": dv.get("origin"),
            "related_fact_id": dv.get("related_fact_id"), "local_context": local_context,
            "fallback_used": fallback,
        })
    return out


def guarded_call(state: dict, consecutive_errors: list, label: str, fn, save_path: str, **kwargs) -> dict:
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = fn(**kwargs)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    state["cumulative_calls"] += 1
    if result is not None:
        state["cumulative_jpy"] += result["cost_jpy"]
        state["history"].append({"label": label, "cost_jpy": result["cost_jpy"], "usage": result["usage"]})
        save_json(save_path, {"label": label, **result})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        save_json(save_path, {"label": label, "error": last_err})
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")
    return result if result is not None else {"error": last_err}


def run_per_claim_vs_batch(client, state: dict, consecutive_errors: list) -> dict:
    out = {}
    for fixture_id in ["B4", "B1"]:
        fixture = get_fixture(fixture_id)
        blocking = load_v4a_blocking_claims(fixture_id)
        claims = build_claim_records(fixture, blocking)
        per_claim_results = []
        for i, c in enumerate(claims):
            res = guarded_call(
                state, consecutive_errors, f"{fixture_id}_per_claim_{i}", s2p.run_stage2_per_claim,
                f"{OUT_DIR}/per_claim_vs_batch/{fixture_id}/per_claim_{i}.json",
                client=client, verified_ledger_text=fixture["ledger_text"],
                source_article_text=fixture.get("source_article_text"),
                claim_text=c["claim_text"], origin=c["origin"], related_fact_id=c["related_fact_id"],
                local_context=c["local_context"],
            )
            per_claim_results.append(res)
        batch_res = guarded_call(
            state, consecutive_errors, f"{fixture_id}_batch", s2p.run_stage2_batch,
            f"{OUT_DIR}/per_claim_vs_batch/{fixture_id}/batch.json",
            client=client, verified_ledger_text=fixture["ledger_text"],
            source_article_text=fixture.get("source_article_text"), claims=claims,
        )
        out[fixture_id] = {
            "n_claims": len(claims), "per_claim": per_claim_results, "batch": batch_res,
            "claims_meta": claims,
        }
    return out


def run_caching_test(client, state: dict, consecutive_errors: list) -> dict:
    out = {}
    for fixture_id in ["B4", "B1"]:
        fixture = get_fixture(fixture_id)
        blocking = load_v4a_blocking_claims(fixture_id)
        claims = build_claim_records(fixture, blocking)
        c0 = claims[0]
        call1 = guarded_call(
            state, consecutive_errors, f"{fixture_id}_cache_call1", s2p.run_stage2_per_claim,
            f"{OUT_DIR}/prompt_caching/{fixture_id}/call1.json",
            client=client, verified_ledger_text=fixture["ledger_text"],
            source_article_text=fixture.get("source_article_text"),
            claim_text=c0["claim_text"], origin=c0["origin"], related_fact_id=c0["related_fact_id"],
            local_context=c0["local_context"],
        )
        call2 = guarded_call(
            state, consecutive_errors, f"{fixture_id}_cache_call2", s2p.run_stage2_per_claim,
            f"{OUT_DIR}/prompt_caching/{fixture_id}/call2.json",
            client=client, verified_ledger_text=fixture["ledger_text"],
            source_article_text=fixture.get("source_article_text"),
            claim_text=c0["claim_text"], origin=c0["origin"], related_fact_id=c0["related_fact_id"],
            local_context=c0["local_context"],
        )
        out[fixture_id] = {"call1": call1, "call2": call2}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="unitcost,caching", help="comma-separated: unitcost,caching")
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    results = {}
    stopped = False
    stop_reason = None

    tasks = [x.strip() for x in args.tasks.split(",") if x.strip()]
    try:
        if "unitcost" in tasks:
            results["unitcost"] = run_per_claim_vs_batch(client, state, consecutive_errors)
        if "caching" in tasks:
            results["caching"] = run_caching_test(client, state, consecutive_errors)
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
    }
    save_json(f"{OUT_DIR}/summary_step4_stage2_unitcost.json", {"summary": summary, "results": results})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
