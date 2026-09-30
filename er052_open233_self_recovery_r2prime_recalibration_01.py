# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_r2prime_recalibration_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, iteration 2、委任_10)
# ============================================================
# 目的: 委任_10 作業B。negative群7出典のうちV4Aが過剰BLOCKした4記事の
# 実claim(委任_09 統合dry-runの実測instance jsonから抽出した実際の
# claim_text、placeholderではない)+B1-a/b+B4-b/c(通すべき側)と、
# B1-c/B3/B4-a/B4-d+A2A3/A4/A5(止めるべき側、Safety群)を対象に、
# RUBRIC_R2'(段階的手順+例示追加、er052_open233_self_recovery_stage2_
# calibration_01.RUBRIC_R2_PRIME)をn=2で実測し、既存RUBRIC_R2実測
# (委任_08/_09、B1/B3/B4/A2A3/A4/A5は既存summary_stage2_calibration.json、
# neg1/2/3/5は委任_09統合dry-run実測)と比較する。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_self_recovery_stage2_calibration_01.py(委任_08の
#   summary_stage2_calibration.json含む既存証跡)は変更しない
#   (RUBRIC_R2_PRIMEの追加のみ、既存関数・既存出力は不変)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_r2prime_recalibration_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233n_b.json"
TOTAL_BUDGET_JPY = 8.0  # 委任_10 作業B Guardrail(想定)
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2

SAFETY_SIDE_GROUP_IDS = {"B1", "B3", "B4", "A2A3", "A4", "A5"}
SAFETY_MUST_STAY_BLOCKING_SUB_IDS = {"B1-c", "B3", "B4-a", "B4-d"}  # +A2A3-*/A4-*/A5-*(全件BLOCKING)
PRODUCTIVITY_SUB_IDS = {"B1-a", "B1-b", "B4-b", "B4-c"}

NEG_INSTANCE_PATHS = {
    "neg1_meta_b3prod_a2": "er052_output/open233_self_recovery_flow_runner_01/instances/"
                            "neg1_meta_b3prod_a2.json",
    "neg2_meta_refresh_a2": "er052_output/open233_self_recovery_flow_runner_01/instances/"
                             "neg2_meta_refresh_a2.json",
    "neg3_hormuz_prodrunner_b1b": "er052_output/open233_self_recovery_flow_runner_01/instances/"
                                   "neg3_hormuz_prodrunner_b1b.json",
    "neg5_hormuz_div_a2": "er052_output/open233_self_recovery_flow_runner_01/instances/"
                           "neg5_hormuz_div_a2.json",
}


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_10 作業B Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------
# 実claim抽出(委任_09統合dry-run instance jsonのcycle[0].stage2_resultsより、
# placeholderではない実際にV4Aが検出したclaim_text/related_fact_id/originを
# そのまま使う)。
# ------------------------------------------------------------
def build_negative_real_claim_groups() -> list:
    groups = []
    for fixture_id, path in NEG_INSTANCE_PATHS.items():
        with open(path, encoding="utf-8") as f:
            inst = json.load(f)
        cycle0 = inst["cycles"][0]
        real_claims = [sr for sr in cycle0["stage2_results"] if sr.get("detected_by") == "stage1_llm"]
        src_id, src_path = next(t for t in step3cmp.NEGATIVE_SOURCE_FILES if t[0] == fixture_id)
        fixture = step3cmp.load_negative_fixture(src_id, src_path)
        claims = []
        for i, sr in enumerate(real_claims):
            claims.append({
                "sub_id": f"{fixture_id}-{i}", "claim_text": sr["claim_text"],
                "correct_label": "NOT_BLOCKING(ACCEPTABLE/QUALITY)",
                "origin": sr.get("origin"), "related_fact_id": sr.get("related_fact_id"),
                "unsupported_new_claim": True,
                "r2_baseline_label": sr["materiality"],  # 委任_09実測(RUBRIC_R2、real claim)
            })
        groups.append({"group_id": fixture_id, "fixture": fixture, "claims": claims})
    return groups


def build_eval_groups_iter2() -> list:
    base_groups = {g["group_id"]: g for g in s2c.build_eval_groups()}
    groups = [base_groups[gid] for gid in ("B1", "B3", "B4", "A2A3", "A4", "A5")]
    groups += build_negative_real_claim_groups()
    return groups


def build_claim_records_for_group(group: dict) -> list:
    fixture = group["fixture"]
    out = []
    for c in group["claims"]:
        local_context, fallback = s2p.build_local_context(fixture["article_text"], c["claim_text"])
        out.append({**c, "local_context": local_context, "fallback_used": fallback})
    return out


def guarded_batch_call(state: dict, consecutive_errors: list, label: str, save_path: str, **kwargs) -> dict:
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = s2c.run_stage2_batch_variant(**kwargs)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    groups = build_eval_groups_iter2()

    stopped, stop_reason = False, None
    r2p_runs = {}

    try:
        for run_idx in range(1, args.n_runs + 1):
            for group in groups:
                claims = build_claim_records_for_group(group)
                fixture = group["fixture"]
                label = f"{group['group_id']}_R2PRIME_run{run_idx}"
                save_path = f"{OUT_DIR}/R2PRIME/{group['group_id']}/run_{run_idx}.json"
                res = guarded_batch_call(
                    state, consecutive_errors, label, save_path,
                    client=client, verified_ledger_text=fixture["ledger_text"],
                    source_article_text=fixture.get("source_article_text"),
                    claims=claims, rubric_text=s2c.RUBRIC_R2_PRIME,
                )
                r2p_runs.setdefault(group["group_id"], []).append({
                    "run": run_idx, "claims": claims, "result": res,
                })
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    per_claim_rows = []
    for group in groups:
        gid = group["group_id"]
        runs = r2p_runs.get(gid, [])
        for c in group["claims"]:
            sub_id = c["sub_id"]
            r2p_labels = []
            for run in runs:
                if "error" in run["result"]:
                    continue
                judgments = run["result"]["parsed"].get("judgments", [])
                claim_idx = [cc["sub_id"] for cc in run["claims"]].index(sub_id)
                match = next((j for j in judgments if j.get("claim_index") == claim_idx), None)
                if match is None:
                    continue
                r2p_labels.append({"materiality": match["materiality"], "basis": match["basis"],
                                    "rewrite_hint_present": bool(match.get("rewrite_hint"))})
            per_claim_rows.append({
                "group_id": gid, "sub_id": sub_id, "correct_label": c["correct_label"],
                "r2_baseline_label": c.get("r2_baseline_label"),
                "r2prime_labels_by_run": r2p_labels,
            })

    safety_misdowngrade = []
    productivity_improved = []
    productivity_unchanged_or_worse = []
    for row in per_claim_rows:
        must_stay_blocking = (row["sub_id"] in SAFETY_MUST_STAY_BLOCKING_SUB_IDS
                               or row["group_id"] in ("A2A3", "A4", "A5"))
        labels = [r["materiality"] for r in row["r2prime_labels_by_run"]]
        if must_stay_blocking:
            if any(lbl != "BLOCKING" for lbl in labels):
                safety_misdowngrade.append(row["sub_id"])
        else:
            # productivity側: correct_labelがBLOCKINGでないもの
            baseline = row.get("r2_baseline_label")
            non_blocking_now = sum(1 for lbl in labels if lbl != "BLOCKING")
            if baseline == "BLOCKING" and non_blocking_now > 0:
                productivity_improved.append(row["sub_id"])
            elif row["sub_id"] in {"B1-a", "B1-b"} and non_blocking_now == 0:
                productivity_unchanged_or_worse.append(row["sub_id"])
            elif row["sub_id"] in {"B4-b", "B4-c"} and non_blocking_now == 0:
                productivity_unchanged_or_worse.append(row["sub_id"])
            elif row["group_id"].startswith("neg") and non_blocking_now == 0:
                productivity_unchanged_or_worse.append(row["sub_id"])

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_runs": args.n_runs,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "safety_misdowngrade_sub_ids": safety_misdowngrade,
        "safety_misdowngrade_count": len(safety_misdowngrade),
        "productivity_improved_sub_ids": productivity_improved,
        "productivity_unchanged_or_worse_sub_ids": productivity_unchanged_or_worse,
        "adopt_r2prime_recommended": (len(safety_misdowngrade) == 0 and len(productivity_improved) > 0),
    }
    save_json(f"{OUT_DIR}/summary_r2prime_recalibration.json", {
        "summary": summary, "per_claim_rows": per_claim_rows,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
