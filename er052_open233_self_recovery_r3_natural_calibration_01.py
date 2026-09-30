# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_r3_natural_calibration_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, iteration4、委任_12 作業B)
# ============================================================
# 目的: 委任_12ユーザー指示「許容線の再設計(自然な解釈はOK/事実の発明はNG)」
# に基づき新設したRUBRIC_R3_NATURAL_INTERPRETATION(er052_open233_self_
# recovery_stage2_calibration_01.RUBRIC_R3_NATURAL_INTERPRETATION)の単体較正
# Trialを実行する。既存build_eval_groups()(B1/B2/B3/B4/Meta_run03_standard/
# hormuz_run03_standard/negative4[neg1,neg2,neg3,neg5]/A2A3/A4/A5、委任_08で
# 確定した評価セット)を再利用し、n=2で新規call。
#
# 委任_12再ラベル(§7-0改訂、本ファイルのCORRECT_LABEL_OVERRIDES_R3で反映):
# - B1-c(市場動機の断定): BLOCKING(R2/旧) -> QUALITY(R3、自然な解釈として
#   通過が正解。ユーザー例「市場が海上リスクを重視したから価格が戻った」
#   程度はぎりぎり許容とのユーザー指示)。
# - B4-d(確実性強化、V4A run): BLOCKING(R2/旧、floor経由fail-closed)
#   -> QUALITY(R3。ユーザーNG5項目[actor/number/negation/comparison/time]
#   に確実性は含まれず、floorからも除外[§4-3改訂]したため)。
# - それ以外(B1-a/b、B2、B3、B4-a/b/c、Meta、hormuz HF-009、negative4、
#   A2A3/A4/A5)は§7-0既存ラベルを維持する(B3はLedger conditionsとの明示
#   矛盾、B4-aはメカニズム捏造、HF-009はscope重大変更のため、いずれも
#   「新しい具体的事実の発明」に該当しBLOCKINGを維持)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_self_recovery_stage2_calibration_01.py(委任_08の
#   summary_stage2_calibration.json含む既存証跡)は変更しない
#   (RUBRIC_R3_NATURAL_INTERPRETATION追加のみ、既存関数・既存出力は不変)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_r3_natural_calibration_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233p_b.json"
TOTAL_BUDGET_JPY = 8.0  # 委任_12 作業B Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2

# §7-0改訂(委任_12): 再ラベルされたsub_idのみ上書き。それ以外はbuild_eval_
# groups()のcorrect_labelをそのまま使う。
CORRECT_LABEL_OVERRIDES_R3 = {
    "B1-c": "QUALITY",
    "B4-d": "QUALITY",
}

# Safety側(誤降格ゼロが受入条件): B3/B4-a+A2A3/A4/A5+Meta+hormuz-HF009は
# 引き続きBLOCKING維持が正解(§7-0)。B1-cとB4-dはR3較正でQUALITY側へ
# 意図的に移動したためSafety側の対象から外す。
SAFETY_MUST_STAY_BLOCKING_SUB_IDS = {"B3", "B4-a"}  # +A2A3-*/A4-*/A5-*/Meta-*/hormuz-HF009(groupで判定)
SAFETY_GROUP_IDS_ALL_BLOCKING = {"A2A3", "A4", "A5", "Meta_run03_standard", "hormuz_run03_standard"}


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_12 作業B Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def resolved_correct_label(sub_id: str, original: str) -> str:
    return CORRECT_LABEL_OVERRIDES_R3.get(sub_id, original)


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
    parser.add_argument("--rubric", choices=["r3", "r3prime"], default="r3",
                         help="r3=RUBRIC_R3_NATURAL_INTERPRETATION(既定)、"
                              "r3prime=RUBRIC_R3_PRIME(Safety側誤降格是正版、"
                              "作業B受入条件未達時の1回限り再較正)")
    args = parser.parse_args()
    rubric_text = s2c.RUBRIC_R3_PRIME if args.rubric == "r3prime" else s2c.RUBRIC_R3_NATURAL_INTERPRETATION
    variant_tag = args.rubric.upper()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    groups = s2c.build_eval_groups()

    stopped, stop_reason = False, None
    r3_runs: dict = {}

    try:
        for run_idx in range(1, args.n_runs + 1):
            for group in groups:
                claims = s2c.build_claim_records_for_group(group)
                fixture = group["fixture"]
                label = f"{group['group_id']}_{variant_tag}_run{run_idx}"
                save_path = f"{OUT_DIR}/{variant_tag}/{group['group_id']}/run_{run_idx}.json"
                res = guarded_batch_call(
                    state, consecutive_errors, label, save_path,
                    client=client, verified_ledger_text=fixture["ledger_text"],
                    source_article_text=fixture.get("source_article_text"),
                    claims=claims, rubric_text=rubric_text,
                )
                r3_runs.setdefault(group["group_id"], []).append({"run": run_idx, "claims": claims, "result": res})
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    per_claim_rows = []
    for group in groups:
        gid = group["group_id"]
        runs = r3_runs.get(gid, [])
        for c in group["claims"]:
            sub_id = c["sub_id"]
            correct_label = resolved_correct_label(sub_id, c["correct_label"])
            r3_labels = []
            for run in runs:
                if "error" in run["result"]:
                    continue
                judgments = run["result"]["parsed"].get("judgments", [])
                claim_idx = [cc["sub_id"] for cc in run["claims"]].index(sub_id)
                match = next((j for j in judgments if j.get("claim_index") == claim_idx), None)
                if match is None:
                    continue
                r3_labels.append({"materiality": match["materiality"], "basis": match["basis"],
                                   "rewrite_hint_present": bool(match.get("rewrite_hint"))})
            per_claim_rows.append({
                "group_id": gid, "sub_id": sub_id, "correct_label": correct_label,
                "r3_labels_by_run": r3_labels,
            })

    safety_misdowngrade = []
    correct_matches = 0
    total_judged = 0
    accuracy_rows = []
    for row in per_claim_rows:
        must_stay_blocking = (
            row["sub_id"] in SAFETY_MUST_STAY_BLOCKING_SUB_IDS
            or row["group_id"] in SAFETY_GROUP_IDS_ALL_BLOCKING
        )
        labels = [r["materiality"] for r in row["r3_labels_by_run"]]
        if must_stay_blocking and any(lbl != "BLOCKING" for lbl in labels):
            safety_misdowngrade.append(row["sub_id"])
        correct_label = row["correct_label"]
        for lbl in labels:
            total_judged += 1
            is_correct = (
                lbl == correct_label
                or (correct_label == "NOT_BLOCKING(ACCEPTABLE/QUALITY)" and lbl in ("ACCEPTABLE", "QUALITY"))
            )
            if is_correct:
                correct_matches += 1
        accuracy_rows.append({
            "sub_id": row["sub_id"], "group_id": row["group_id"], "correct_label": correct_label,
            "observed_labels": labels,
        })

    summary = {
        "rubric_variant": variant_tag,
        "stopped": stopped, "stop_reason": stop_reason,
        "n_runs": args.n_runs,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "safety_misdowngrade_sub_ids": safety_misdowngrade,
        "safety_misdowngrade_count": len(safety_misdowngrade),
        "correct_label_accuracy": (
            round(correct_matches / total_judged, 4) if total_judged else None
        ),
        "correct_matches": correct_matches, "total_judged": total_judged,
        "adopt_r3_recommended": (len(safety_misdowngrade) == 0),
    }
    save_json(f"{OUT_DIR}/summary_{variant_tag.lower()}_natural_calibration.json", {
        "summary": summary, "per_claim_rows": per_claim_rows, "accuracy_rows": accuracy_rows,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
