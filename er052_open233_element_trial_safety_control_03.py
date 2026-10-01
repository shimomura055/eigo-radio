# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_safety_control_03.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_31 Part1(b)、neg1の不要Rewrite
# 是正に伴うbody rubric V5のpriming再測定)
# ============================================================
# 目的: 委任_31 Part1(b)でbody rubric(RUBRIC_R3_TRIPLE_PRIME_WITH_
# MISCONCEPTION_PRINCIPLE_V5、新規「受け手側の驚き・反応は新規Factでは
# ない」の1段落追加)を導入した際、priming再測定の要件(委任_16の教訓:
# rubric文言の追加だけで無関係なclaimの判定にも寛容化バイアスが波及し
# 得る)に従い、Safety-critical 8claim(er052_open233_self_recovery_
# r3dprime_calibration_01.SAFETY_CRITICAL_SUB_IDS、B3を含む)が1件も
# 誤降格(非BLOCKING化)しないことをStage2のみ(Stage1/Stage3は実行しない、
# 既存er052_open233_element_trial_safety_control_02.pyのPart Aをread-only
# で再利用)で確認する。n=1(委任文Guardrail≤¥1.5の範囲内)。
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_element_trial_safety_control_02.py/
#   er052_open233_self_recovery_stage2_calibration_01.py/
#   er052_open233_self_recovery_r3dprime_calibration_01.pyはread-onlyで
#   関数・定数を再利用するのみ、変更しない。
# - 本委任専用のbudget state(他委任の既存証跡ファイルを汚染しない)。
from __future__ import annotations

import argparse
import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_element_trial_safety_control_02 as sc02
import er052_open233_self_recovery_stage2_calibration_01 as s2c

OUT_DIR = "er052_output/open233_element_trial_safety_control_03"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ah_31.json"
TOTAL_BUDGET_JPY = 1.5  # 委任_31 Part1(b)のGuardrail(priming再測定、Part Aのみ)
N_RUNS = 1

RUBRIC_VARIANTS = {"V5": s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V5}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    args = parser.parse_args()

    # 既存sc02のbudget/guardrailグローバルを本委任専用のものへ一時的に
    # 差し替える(他委任の既存証跡ファイルを汚染しない、委任_28の事故
    # 是正コメントと同一原則)。sc02.OUT_DIR/BUDGET_STATE_PATH/
    # TOTAL_BUDGET_JPYは本ファイル内でのみ上書きし、呼び出し終了後は
    # プロセス終了のため復元不要(本ファイルは単発実行専用スクリプト)。
    sc02.OUT_DIR = OUT_DIR
    sc02.BUDGET_STATE_PATH = BUDGET_STATE_PATH
    sc02.TOTAL_BUDGET_JPY = TOTAL_BUDGET_JPY

    rubric_tag = "V5"
    rubric_text = RUBRIC_VARIANTS[rubric_tag]

    client = vfl01.get_client()
    state = sc02.load_budget_state()
    consecutive_errors = [0]

    stopped, stop_reason = False, None
    part_a = {"per_claim_rows": [], "misdowngrade_total": 0}
    try:
        part_a = sc02.run_part_a(client, state, consecutive_errors, args.n_runs, rubric_text, rubric_tag)
    except sc02.TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "rubric_variant": rubric_tag,
        "n_runs": args.n_runs,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "part_a_safety_critical_8claim": {
            "misdowngrade_total": part_a["misdowngrade_total"],
            "n_claims": len(part_a["per_claim_rows"]),
            "per_claim_rows": part_a["per_claim_rows"],
        },
    }
    sc02.save_json(f"{OUT_DIR}/summary_safety_control_03_{rubric_tag}.json", {"summary": summary})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
