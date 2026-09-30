# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_r3dprime_calibration_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, iteration5、委任_13 作業C)
# ============================================================
# 目的: Opus L2レビュー#3(docs/pm/opus_l2_review_open233_self_recovery_03.md)
# 論点1・論点2の推奨に基づき、以下2点を反映したRUBRIC_R3_DOUBLE_PRIME
# (er052_open233_self_recovery_stage2_calibration_01.RUBRIC_R3_DOUBLE_PRIME)
# の単体較正Trialを実行する。
# 1. 較正セットの正解ラベル是正(論点1): A2A3-1(HF-006「原油高→ガソリン・
#    輸送費」)とA4-2(MUSE-HC-010 certainty強化)は、build_eval_groups()の
#    機械コピー由来ラベル(V4Aのseverity_finalをそのままBLOCKINGへコピー)
#    であり、NG(a)〜(e)に照らすとQUALITYが正しい(それぞれB1-b/B4-bと
#    実質同一のclaim)。本ファイルのCORRECT_LABEL_OVERRIDES_R3DPRIMEで
#    QUALITYへ上書きする(既存build_eval_groups()自体は変更しない、既存
#    r3_natural_calibration_01.pyのCORRECT_LABEL_OVERRIDES_R3と同一方式)。
# 2. 受入条件「Safety側誤降格0件」を、全group一律ではなく、名指しした
#    Safety-critical claim 10件(A2A3-0/A4-0/A4-1/A5-0/A5-1/Meta-1/Meta-2/
#    hormuz-HF009/B3/B4-a)の降格0件へ限定する(SAFETY_CRITICAL_SUB_IDS)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_self_recovery_stage2_calibration_01.py・
#   er052_open233_self_recovery_r3_natural_calibration_01.py(既存証跡含む)
#   は変更しない(RUBRIC_R3_DOUBLE_PRIME追加のみ、既存関数・既存出力は不変)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_r3dprime_calibration_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233q_c.json"
# 委任_13 作業C Guardrailは当初¥6(R3''単体較正、26 call実測¥4.267)。R3''
# 実測でB4-dが受入条件未達(2/2 BLOCKING、QUALITY化せず)だったため、委任文
# 「未達なら原因分類しR3'''を1回だけ」に従い追加較正(26 call、想定+¥4〜5)を
# 実施する。合計は¥6を超えるが、iteration5全体のGuardrail¥75(累計¥152.16→
# 上限¥400)には十分な余裕があり、超過は本委任のREPORTで明示的に報告する。
TOTAL_BUDGET_JPY = 11.0
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2

# 委任_13 論点1(是正1): 機械コピー由来ラベルの是正。
CORRECT_LABEL_OVERRIDES_R3DPRIME = {
    "B1-c": "QUALITY",   # 委任_12から継承(R3較正で確定済み)
    "B4-d": "QUALITY",   # 委任_12から継承(R3較正で確定済み)
    "A2A3-1": "QUALITY",  # 新規是正(委任_13、Opus L2 #3論点1)
    "A4-2": "QUALITY",   # 新規是正(委任_13、Opus L2 #3論点1)
}

# 委任_13 論点1(是正2): 「Safety側誤降格0件」を、名指しした10claimへ限定。
# A2A3-1/A4-2はQUALITYへ再ラベルされたため対象から除外する。
SAFETY_CRITICAL_SUB_IDS = frozenset({
    "A2A3-0", "A4-0", "A4-1", "A5-0", "A5-1", "Meta-1", "Meta-2",
    "hormuz-HF009", "B3", "B4-a",
})


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_13 作業C Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def resolved_correct_label(sub_id: str, original: str) -> str:
    return CORRECT_LABEL_OVERRIDES_R3DPRIME.get(sub_id, original)


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
    parser.add_argument("--rubric", choices=["r3dprime", "r3tripleprime"], default="r3dprime",
                         help="r3dprime=RUBRIC_R3_DOUBLE_PRIME(既定)、"
                              "r3tripleprime=RUBRIC_R3_TRIPLE_PRIME(B4-d是正版、"
                              "受入条件未達時の1回限り追加較正)")
    args = parser.parse_args()
    rubric_text = (
        s2c.RUBRIC_R3_TRIPLE_PRIME if args.rubric == "r3tripleprime" else s2c.RUBRIC_R3_DOUBLE_PRIME
    )
    variant_tag = "R3DPRIME" if args.rubric == "r3dprime" else "R3TRIPLEPRIME"

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    groups = s2c.build_eval_groups()

    stopped, stop_reason = False, None
    runs: dict = {}

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
                runs.setdefault(group["group_id"], []).append({"run": run_idx, "claims": claims, "result": res})
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    per_claim_rows = []
    for group in groups:
        gid = group["group_id"]
        group_runs = runs.get(gid, [])
        for c in group["claims"]:
            sub_id = c["sub_id"]
            correct_label = resolved_correct_label(sub_id, c["correct_label"])
            labels = []
            for run in group_runs:
                if "error" in run["result"]:
                    continue
                judgments = run["result"]["parsed"].get("judgments", [])
                claim_idx = [cc["sub_id"] for cc in run["claims"]].index(sub_id)
                match = next((j for j in judgments if j.get("claim_index") == claim_idx), None)
                if match is None:
                    continue
                labels.append({"materiality": match["materiality"], "basis": match["basis"],
                                "rewrite_hint_present": bool(match.get("rewrite_hint"))})
            per_claim_rows.append({
                "group_id": gid, "sub_id": sub_id, "correct_label": correct_label,
                "r3dprime_labels_by_run": labels,
            })

    safety_misdowngrade = []
    correct_matches = 0
    total_judged = 0
    accuracy_rows = []
    for row in per_claim_rows:
        must_stay_blocking = row["sub_id"] in SAFETY_CRITICAL_SUB_IDS
        labels = [r["materiality"] for r in row["r3dprime_labels_by_run"]]
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
            "observed_labels": labels, "is_safety_critical": must_stay_blocking,
        })

    # B4-d/B1-cが両run QUALITYで一致したかを明示的に確認する(委任_13受入条件)。
    def _row(sub_id):
        return next((r for r in per_claim_rows if r["sub_id"] == sub_id), None)

    b4d_row = _row("B4-d")
    b1c_row = _row("B1-c")
    b4d_labels = [r["materiality"] for r in (b4d_row["r3dprime_labels_by_run"] if b4d_row else [])]
    b1c_labels = [r["materiality"] for r in (b1c_row["r3dprime_labels_by_run"] if b1c_row else [])]

    summary = {
        "rubric_variant": variant_tag,
        "stopped": stopped, "stop_reason": stop_reason,
        "n_runs": args.n_runs,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "safety_critical_sub_ids": sorted(SAFETY_CRITICAL_SUB_IDS),
        "safety_misdowngrade_sub_ids": safety_misdowngrade,
        "safety_misdowngrade_count": len(safety_misdowngrade),
        "b4d_labels": b4d_labels, "b4d_quality_2of2": b4d_labels == ["QUALITY", "QUALITY"],
        "b1c_labels": b1c_labels, "b1c_quality_2of2": b1c_labels == ["QUALITY", "QUALITY"],
        "correct_label_accuracy": (
            round(correct_matches / total_judged, 4) if total_judged else None
        ),
        "correct_matches": correct_matches, "total_judged": total_judged,
        "adopt_r3dprime_recommended": (len(safety_misdowngrade) == 0),
    }
    save_json(f"{OUT_DIR}/summary_{variant_tag.lower()}_calibration.json", {
        "summary": summary, "per_claim_rows": per_claim_rows, "accuracy_rows": accuracy_rows,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
