# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_safety_control_04.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_33: body rubric V6のpriming再測定)
# ============================================================
# 目的: 委任_33でbody rubric V6(RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_
# PRINCIPLE_V6、design書§4-25、B3[HF-007]/A2A3-0[HF-003]誤降格是正の許容/
# NG対比例示を追加)を導入したため、priming再測定の要件(委任_16の教訓:
# rubric文言の追加だけで無関係なclaimの判定にも寛容化/厳格化バイアスが
# 波及し得る)に従い、以下3系統をStage2のみ(Stage1/Stage3は実行しない)で
# n=1(委任文Guardrail¥13のうちPart A/C/Hook分の範囲内)で確認する。
#
# (A) Safety-critical 8claim(B3/A2A3-0を含む、r3d.SAFETY_CRITICAL_SUB_IDS):
#     既存er052_open233_element_trial_safety_control_02.pyのPart Aを
#     read-onlyで再利用(新規fixture捏造なし)。
# (C) Hormuz許容5/NG5(委任_27 Trial Aのclaim定義を再利用、sc02 Part C):
#     既存Stage1出力(claim_text自体が確定済みfixtureからの逐語引用)を
#     再利用し、Stage2のみ新規call。
# (Hook) neg1実Hook(accept-1-original-hook)・境界例(boundary-1-
#     dramatization)のHook専用Stage2(rubric本体は本委任で変更していない、
#     body V6が独立した別promptのHook rubricへ波及していないことの
#     非回帰確認)をn=1で再確認する。
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_element_trial_safety_control_02.py/
#   er052_open233_element_trial_meta_hook_01.py/
#   er052_open233_self_recovery_stage2_calibration_01.pyはread-onlyで
#   関数・定数を再利用するのみ、変更しない。
# - 本委任専用のbudget state(他委任の既存証跡ファイルを汚染しない、
#   sc02/mh1のモジュール変数を一時的に上書きし、本ファイル終了後の復元は
#   不要[単発実行専用スクリプトのため])。
from __future__ import annotations

import argparse
import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_element_trial_meta_hook_01 as mh1
import er052_open233_element_trial_safety_control_02 as sc02
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_hook_01 as s2h

OUT_DIR = "er052_output/open233_element_trial_safety_control_04"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233aj_33_partac.json"
TOTAL_BUDGET_JPY = 2.0  # 委任_33 rep18 Guardrail¥13のうち、Part A+C+Hookの小計分
N_RUNS = 1

RUBRIC_TAG = "V6"
RUBRIC_TEXT = s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V6

HOOK_CLAIMS_SUBSET = [c for c in mh1.HOOK_CLAIMS
                      if c["sub_id"] in ("accept-1-original-hook", "boundary-1-dramatization")]


def run_hook_check(client, state, consecutive_errors, meta_fixture) -> dict:
    batch_claims = [{"claim_text": c["claim_text"], "origin": "translation",
                      "related_fact_id": "MUSE-HC-006"} for c in HOOK_CLAIMS_SUBSET]
    title_hook_text = f"{mh1.TITLE}\n\n{mh1.NEG1_ORIGINAL_HOOK}"
    label = "hookcheck_v6regression_run1"
    save_path = f"{OUT_DIR}/hook_check/run_1.json"
    last_err = None
    result = None
    for _ in range(1 + sc02.MAX_RETRIES_PER_CALL):
        try:
            result = s2h.run_stage2_hook_batch(
                client, meta_fixture["ledger_text"], meta_fixture.get("source_article_text"),
                title_hook_text, batch_claims, model=s2c.s2p.MODEL,
                hook_rubric_text=runner.HOOK_RUBRIC_DEFAULT,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
    state["cumulative_calls"] += 1
    if result is not None:
        state["cumulative_jpy"] += result["cost_jpy"]
        state["history"].append({"label": label, "cost_jpy": result["cost_jpy"]})
        sc02.save_json(save_path, result)
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        sc02.save_json(save_path, {"error": last_err})
        consecutive_errors[0] += 1
    sc02.save_budget_state(state)
    if result is None:
        return {"error": last_err}
    judgments = result["parsed"].get("judgments", [])
    rows = []
    for idx, c in enumerate(HOOK_CLAIMS_SUBSET):
        match = next((j for j in judgments if j.get("claim_index") == idx), None)
        rows.append({"sub_id": c["sub_id"], "group": c["group"],
                      "materiality": match.get("materiality") if match else None})
    return {"rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    args = parser.parse_args()

    # sc02のbudget/guardrailグローバルを本委任専用のものへ一時的に差し替える
    # (他委任の既存証跡ファイルを汚染しない、委任_28の事故是正コメントと
    # 同一原則)。
    sc02.OUT_DIR = OUT_DIR
    sc02.BUDGET_STATE_PATH = BUDGET_STATE_PATH
    sc02.TOTAL_BUDGET_JPY = TOTAL_BUDGET_JPY

    client = vfl01.get_client()
    state = sc02.load_budget_state()
    consecutive_errors = [0]

    stopped, stop_reason = False, None
    part_a = {"per_claim_rows": [], "misdowngrade_total": 0}
    part_c = {}
    hook_check = {}
    try:
        part_a = sc02.run_part_a(client, state, consecutive_errors, args.n_runs, RUBRIC_TEXT, RUBRIC_TAG)
        part_c = sc02.run_part_c_hormuz(client, state, consecutive_errors, args.n_runs, RUBRIC_TEXT, RUBRIC_TAG)
        meta_fixture = next(f for f in s2c.g6.step2_fixtures() if f["id"] == "Meta_run03_standard")
        hook_check = run_hook_check(client, state, consecutive_errors, meta_fixture)
    except sc02.TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "rubric_variant": RUBRIC_TAG,
        "n_runs": args.n_runs,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "part_a_safety_critical_8claim": {
            "misdowngrade_total": part_a.get("misdowngrade_total"),
            "n_claims": len(part_a.get("per_claim_rows", [])),
            "per_claim_rows": part_a.get("per_claim_rows", []),
        },
        "part_c_hormuz_accept_ng": part_c,
        "hook_check_v6_regression": hook_check,
    }
    sc02.save_json(f"{OUT_DIR}/summary_safety_control_04_{RUBRIC_TAG}.json", {"summary": summary})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
