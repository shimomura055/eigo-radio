# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_safety_control_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_28 Part1、Safety対照群の全量確認)
# ============================================================
# 目的: 委任_27で追加したStage2 body rubric(RUBRIC_R3_TRIPLE_PRIME_WITH_
# MISCONCEPTION_PRINCIPLE_V2、design書§4-18)を、Safety-critical claim全量
# (SAFETY_CRITICAL_SUB_IDS、hormuz-HF009除外後の9件、委任_28 Part0-2)+
# Safety12(er009 9フラグ、design書§7-1)の全量に対して対照測定する(委任_16
# の教訓: 共通rubricへの原則追記は無関係なclaimまで寛容化するprompt
# primingを起こした実例があるため、配線対象を全量で対照測定する)。
#
# 2系統の測定:
# (A) Safety-critical 9claim: 既存s2c.build_eval_groups()/build_claim_
#     records_for_groupをread-onlyで再利用し(新規fixture捏造なし)、
#     該当groupのみrubric=V2で再実行する(Stage2 bodyのみ、既存Stage1
#     出力[severity_final=BLOCKING]は変更しない)。
# (B) Safety12(er009 9フラグ): 全9フラグをStage2(rubric=V2)で直接判定する
#     (Hormuz要素Trial Aの「er009-changed_scope」と同一方式、LLM単独の
#     materiality判定をfloor非適用のまま検査する厳しめの対照)。さらに
#     このうち4フラグ(changed_actor/changed_number[floor対象]、
#     changed_scope/unsupported_new_claim[floor非対象])は、Stage1(V4A)
#     Trial harnessへ重大誤解原則を実配線した`flow_runner.stage1_fresh_
#     with_misconception_principle`からfresh実行し、Stage1自身の10種
#     フラグ分類(floorが参照する生データ)が原則追加によって緩まって
#     いないかを確認する(委任_28 Part0-1のStage1配線の効果測定、design書
#     委任文Part1参照)。
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 本委任専用のbudget state(他委任の既存証跡ファイルを汚染しない)。
# - claim_textは全て実データ(既存fixture)からの逐語引用であり、捏造
#   Ledger factは無い。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er009_ledger_deviation_recalibration_02_test as er009t
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_r3dprime_calibration_01 as r3d
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

# 注意(本委任中に実際に発生した事故の是正、委任_28): 当初
# `er052_open233_self_recovery_flow_runner_01.stage1_fresh_with_
# misconception_principle`を直接呼び出していたが、この関数は内部で
# `record_call`→`save_budget_state`を経由し、**呼び出し元のstate dictの
# 中身に関わらず、flow_runner側の固定`BUDGET_STATE_PATH`(rep15等、他
# 委任の既存証跡ファイル)へ書き込む**副作用を持つことが実行時に判明した
# (実際にrep15のbudget_state_c233ab_24_rep15.jsonを一時的に上書きする
# 事故が発生し、`git checkout`で直後に復元・確認済み、既存証跡への実害
# なし)。本ファイルは以後、flow_runner側のcost計上ヘルパーを経由せず、
# `trial.run_trial_deviation_check`を直接呼び出し、costは本ファイル専用の
# state/budget fileのみへ記録する(他モジュールの共有状態ファイルに触れない)。

OUT_DIR = "er052_output/open233_element_trial_safety_control_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ae.json"
TOTAL_BUDGET_JPY = 9.0  # 委任_28 Part1 Guardrail(委任文想定¥6、V3再測定分を含め実測超過時は報告)
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2

# 委任_28 Part1: Safety12(er009 9フラグ)のうちStage1 freshを行う4フラグ
# (floor対象2+非floor対象2、重大誤解原則の許容語彙[近似/一般化/数値丸め]
# と概念的に最も近いscope/numberを含めて選定)。
STAGE1_FRESH_FLAGS = ("changed_actor", "changed_number", "changed_scope", "unsupported_new_claim")

# 委任_28 Part1: n=1予備測定(V2)でSafety-critical 9claim中2件(A4-0/A5-1)が
# false downgradeしたため、最小修正1回(V3、上記stage2_calibration_01.py
# 参照)を適用した。以後の公式測定(n=2)はV3を使う(V2は予備測定のみに
# とどめ、上書きしない)。
BODY_RUBRIC = s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V3
BODY_RUBRIC_TAG = "V3"

# 予備測定(V2、n=1、partA/partB_stage2+stage1fresh4フラグ)で実際に支払い
# 済みの費用(¥2.7022)。当初`runner.stage1_fresh_with_misconception_
# principle`を誤って直接呼び出したため、そのうちstage1fresh分(4 call)の
# cost記録は本ファイル専用state fileではなく一時的に他delegationの共有
# state file(rep15)へ書き込まれ、事故発覚後に`git checkout`で同ファイルを
# 復元した(既存証跡への実害なし、詳細はimport直後のコメント参照)。この
# 復元操作により、該当4 callの詳細出力(json)自体も失われたため、本費用は
# 「既に実際にAPI課金が発生した既知のsunk cost」として別建てで記録し、
# 二重課金が発生しないよう本ファイル専用state(以下)はこの時点でリセット
# して再測定する。
SUNK_COST_PRELIMINARY_V2_RUN_JPY = 2.7022


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.4f}が委任_28 Part1 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


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


# ------------------------------------------------------------
# (A) Safety-critical 9claim: 既存groupsから該当groupのみ抽出
# ------------------------------------------------------------
def safety_critical_groups() -> list:
    groups = s2c.build_eval_groups()
    out = []
    for g in groups:
        sub_ids = {c["sub_id"] for c in g["claims"]}
        if sub_ids & r3d.SAFETY_CRITICAL_SUB_IDS:
            out.append(g)
    return out


def run_part_a(client, state, consecutive_errors, n_runs) -> dict:
    groups = safety_critical_groups()
    runs: dict = {}
    for run_idx in range(1, n_runs + 1):
        for group in groups:
            claims = s2c.build_claim_records_for_group(group)
            fixture = group["fixture"]
            label = f"partA_{BODY_RUBRIC_TAG}_{group['group_id']}_run{run_idx}"
            save_path = f"{OUT_DIR}/partA_{BODY_RUBRIC_TAG}/{group['group_id']}/run_{run_idx}.json"
            res = guarded_batch_call(
                state, consecutive_errors, label, save_path,
                client=client, verified_ledger_text=fixture["ledger_text"],
                source_article_text=fixture.get("source_article_text"),
                claims=claims, rubric_text=BODY_RUBRIC,
            )
            runs.setdefault(group["group_id"], []).append({"run": run_idx, "claims": claims, "result": res})

    per_claim_rows = []
    for group in groups:
        gid = group["group_id"]
        group_runs = runs.get(gid, [])
        for c in group["claims"]:
            sub_id = c["sub_id"]
            if sub_id not in r3d.SAFETY_CRITICAL_SUB_IDS:
                continue
            labels = []
            for run in group_runs:
                if "error" in run["result"]:
                    continue
                judgments = run["result"]["parsed"].get("judgments", [])
                claim_idx = [cc["sub_id"] for cc in run["claims"]].index(sub_id)
                match = next((j for j in judgments if j.get("claim_index") == claim_idx), None)
                if match is None:
                    continue
                labels.append({"materiality": match["materiality"], "basis": match.get("basis"),
                               "rewrite_hint": match.get("rewrite_hint")})
            observed = [lb["materiality"] for lb in labels]
            misdowngrade = [m for m in observed if m != "BLOCKING"]
            per_claim_rows.append({
                "sub_id": sub_id, "group_id": gid, "claim_text": c["claim_text"],
                "observed_labels": labels, "misdowngrade_count": len(misdowngrade),
            })
    return {"per_claim_rows": per_claim_rows,
             "misdowngrade_total": sum(r["misdowngrade_count"] for r in per_claim_rows)}


# ------------------------------------------------------------
# (B) Safety12(er009 9フラグ): Stage2 body直接判定(全9) + Stage1 fresh(4)
# ------------------------------------------------------------
def build_safety12_claims() -> list:
    claims = []
    for name, article_text in er009t.FIXTURES.items():
        local_context, fallback = s2p.build_local_context(article_text, article_text)
        claims.append({
            "flag": name, "claim_text": article_text, "origin": None, "related_fact_id": None,
            "local_context": local_context, "fallback_used": fallback,
            "stage1_fresh": name in STAGE1_FRESH_FLAGS,
        })
    return claims


def run_part_b_stage2(client, state, consecutive_errors, n_runs, claims) -> dict:
    batch_claims = [{"claim_text": c["claim_text"], "origin": c["origin"],
                      "related_fact_id": c["related_fact_id"], "local_context": c["local_context"],
                      "section_type": "body"} for c in claims]
    runs = []
    for run_idx in range(1, n_runs + 1):
        label = f"partB_stage2_{BODY_RUBRIC_TAG}_run{run_idx}"
        save_path = f"{OUT_DIR}/partB_stage2_{BODY_RUBRIC_TAG}/run_{run_idx}.json"
        res = guarded_batch_call(
            state, consecutive_errors, label, save_path,
            client=client, verified_ledger_text=er009t.LEDGER_TEXT, source_article_text=None,
            claims=batch_claims, rubric_text=BODY_RUBRIC,
        )
        runs.append(res)

    per_flag_rows = []
    for idx, c in enumerate(claims):
        labels = []
        for res in runs:
            if "error" in res:
                continue
            judgments = res["parsed"].get("judgments", [])
            match = next((j for j in judgments if j.get("claim_index") == idx), None)
            if match is not None:
                labels.append({"materiality": match["materiality"], "basis": match.get("basis")})
        observed = [lb["materiality"] for lb in labels]
        misdowngrade = [m for m in observed if m != "BLOCKING"]
        per_flag_rows.append({"flag": c["flag"], "observed_labels": labels,
                               "misdowngrade_count": len(misdowngrade)})
    return {"per_flag_rows": per_flag_rows,
             "misdowngrade_total": sum(r["misdowngrade_count"] for r in per_flag_rows)}


def stage1_fresh_misconception_local(client, state, consecutive_errors, label, fixture) -> dict:
    """`runner.stage1_fresh_with_misconception_principle`と同一の呼び出し
    (`trial.run_trial_deviation_check`+重大誤解原則override)だが、cost計上
    を本ファイル専用のstate/budget fileのみへ行う自己完結版(上記の事故是正
    コメント参照)。"""
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, fixture["ledger_text"], fixture["article_text"], s2p.MODEL, "V4A",
                include_related_fact_id=True, source_article_text=fixture.get("source_article_text"),
                developer_message_override=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    state["cumulative_calls"] += 1
    if result is not None:
        cost = round(s2p.official_cost_jpy(result["usage"]), 4)
        state["cumulative_jpy"] += cost
        state["history"].append({"label": label, "cost_jpy": cost, "usage": result["usage"]})
        consecutive_errors[0] = 0
        save_budget_state(state)
        return result["parsed"]
    state["cumulative_errors"] += 1
    consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")
    return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True,
            "_error": last_err}


def run_part_b_stage1_fresh(client, state, consecutive_errors, n_runs, claims) -> dict:
    rows = []
    for c in claims:
        if not c["stage1_fresh"]:
            continue
        fixture = {"ledger_text": er009t.LEDGER_TEXT, "article_text": c["claim_text"],
                   "source_article_text": None}
        run_records = []
        for run_idx in range(1, n_runs + 1):
            check_budget(state)
            label = f"partB_stage1fresh_{c['flag']}_run{run_idx}"
            parsed = stage1_fresh_misconception_local(client, state, consecutive_errors, label, fixture)
            devs = parsed.get("deviations", [])
            flag_true = any(d.get(c["flag"]) for d in devs)
            any_blocking = any(d.get("severity_final") == "BLOCKING" for d in devs)
            run_records.append({
                "run": run_idx, "overall_status": parsed.get("overall_status"),
                "n_deviations": len(devs), "expected_flag_true": flag_true,
                "any_blocking": any_blocking,
                "explanations": [d.get("explanation") for d in devs][:2],
            })
        recall_miss = [r for r in run_records if not (r["expected_flag_true"] and r["any_blocking"])]
        rows.append({"flag": c["flag"], "runs": run_records, "recall_miss_count": len(recall_miss)})
    return {"rows": rows, "recall_miss_total": sum(r["recall_miss_count"] for r in rows)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    parser.add_argument("--stage1_n_runs", type=int, default=N_RUNS)
    parser.add_argument("--skip_a", action="store_true")
    parser.add_argument("--skip_b_stage2", action="store_true")
    parser.add_argument("--skip_b_stage1", action="store_true")
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]

    stopped, stop_reason = False, None
    part_a = {"per_claim_rows": [], "misdowngrade_total": 0}
    part_b_stage2 = {"per_flag_rows": [], "misdowngrade_total": 0}
    part_b_stage1 = {"rows": [], "recall_miss_total": 0}
    safety12_claims = build_safety12_claims()

    try:
        if not args.skip_a:
            part_a = run_part_a(client, state, consecutive_errors, args.n_runs)
        if not args.skip_b_stage2:
            part_b_stage2 = run_part_b_stage2(client, state, consecutive_errors, args.n_runs, safety12_claims)
        if not args.skip_b_stage1:
            part_b_stage1 = run_part_b_stage1_fresh(
                client, state, consecutive_errors, args.stage1_n_runs, safety12_claims)
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "rubric_variant": BODY_RUBRIC_TAG,
        "cumulative_jpy_this_run": round(state["cumulative_jpy"], 4),
        "sunk_cost_preliminary_v2_run_jpy": SUNK_COST_PRELIMINARY_V2_RUN_JPY,
        "cumulative_jpy_total_including_sunk": round(state["cumulative_jpy"] + SUNK_COST_PRELIMINARY_V2_RUN_JPY, 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "part_a_safety_critical_9claim": {
            "misdowngrade_total": part_a["misdowngrade_total"],
            "n_claims": len(part_a["per_claim_rows"]),
        },
        "part_b_safety12_stage2": {
            "misdowngrade_total": part_b_stage2["misdowngrade_total"],
            "n_flags": len(part_b_stage2["per_flag_rows"]),
        },
        "part_b_safety12_stage1_fresh": {
            "recall_miss_total": part_b_stage1["recall_miss_total"],
            "n_flags_tested": len(part_b_stage1["rows"]),
        },
    }
    save_json(f"{OUT_DIR}/summary_safety_control.json", {
        "summary": summary, "part_a": part_a, "part_b_stage2": part_b_stage2,
        "part_b_stage1_fresh": part_b_stage1,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
