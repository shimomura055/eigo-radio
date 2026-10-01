# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_safety_control_02.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_29 Part1、Safety対照群の安定化)
# ============================================================
# 目的: 委任_28のSTOP判定(A5-1がさらにACCEPTABLEへ悪化、新規にMeta-1/
# Meta-2がQUALITYへfalse downgrade)に対し、委任_29委任文§1のFableラベル
# 判定を反映した上で、Stage2 body rubric(RUBRIC_R3_TRIPLE_PRIME_WITH_
# MISCONCEPTION_PRINCIPLE_V4、er052_open233_self_recovery_stage2_
# calibration_01.py)を以下3系統で再測定する。
#
# (A) Safety-critical 8claim(A5-1除外後、r3d.SAFETY_CRITICAL_SUB_IDS):
#     既存s2c.build_eval_groups()/build_claim_records_for_groupを
#     read-onlyで再利用(新規fixture捏造なし)。
# (B) Safety12(er009 9フラグ): Stage2 body rubricで直接判定する(Stage1
#     fresh配線自体は委任_28で既に安定確認済みのため本委任では再測定しない、
#     スコープはStage2 body rubricの安定化のみ)。
# (C) Hormuz許容5/NG5(委任_27 Trial Aのclaim定義を再利用、
#     er052_open233_element_trial_hormuz_terms_01.build_claims): 既存
#     Stage1出力(claim_text自体が確定済みfixtureからの逐語引用)を再利用し、
#     Stage2のみ新規call(「既存Stage1出力再利用でStage2のみ」という
#     委任文の指定どおり)。Safety対照2件(B3因果/er009 changed_scope)は
#     (A)(B)と重複するため本ファイルでは除外する(コスト重複回避)。
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 本委任専用のbudget state(他委任の既存証跡ファイルを汚染しない、
#   委任_28 Part1の事故是正コメントと同一原則)。
# - claim_textは全て実データ(既存fixture)からの逐語引用であり、捏造
#   Ledger factは無い。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er009_ledger_deviation_recalibration_02_test as er009t
import er052_open233_element_trial_hormuz_terms_01 as hz
import er052_open233_self_recovery_r3dprime_calibration_01 as r3d
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_element_trial_safety_control_02"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233af.json"
TOTAL_BUDGET_JPY = 9.5  # 委任_29 Part1 Guardrail¥10のうち、余裕を残して¥9.5で自己停止する
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2

RUBRIC_VARIANTS = {
    "V4": s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V4,
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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.4f}が委任_29 Part1 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


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
# (A) Safety-critical 8claim(A5-1除外後)
# ------------------------------------------------------------
def safety_critical_groups() -> list:
    groups = s2c.build_eval_groups()
    out = []
    for g in groups:
        sub_ids = {c["sub_id"] for c in g["claims"]}
        if sub_ids & r3d.SAFETY_CRITICAL_SUB_IDS:
            out.append(g)
    return out


def run_part_a(client, state, consecutive_errors, n_runs, rubric_text, rubric_tag) -> dict:
    groups = safety_critical_groups()
    runs: dict = {}
    for run_idx in range(1, n_runs + 1):
        for group in groups:
            claims = s2c.build_claim_records_for_group(group)
            fixture = group["fixture"]
            label = f"partA_{rubric_tag}_{group['group_id']}_run{run_idx}"
            save_path = f"{OUT_DIR}/partA_{rubric_tag}/{group['group_id']}/run_{run_idx}.json"
            res = guarded_batch_call(
                state, consecutive_errors, label, save_path,
                client=client, verified_ledger_text=fixture["ledger_text"],
                source_article_text=fixture.get("source_article_text"),
                claims=claims, rubric_text=rubric_text,
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
# (B) Safety12(er009 9フラグ): Stage2 body直接判定
# ------------------------------------------------------------
def build_safety12_claims() -> list:
    claims = []
    for name, article_text in er009t.FIXTURES.items():
        local_context, fallback = s2p.build_local_context(article_text, article_text)
        claims.append({
            "flag": name, "claim_text": article_text, "origin": None, "related_fact_id": None,
            "local_context": local_context, "fallback_used": fallback,
        })
    return claims


def run_part_b_stage2(client, state, consecutive_errors, n_runs, claims, rubric_text, rubric_tag) -> dict:
    batch_claims = [{"claim_text": c["claim_text"], "origin": c["origin"],
                      "related_fact_id": c["related_fact_id"], "local_context": c["local_context"],
                      "section_type": "body"} for c in claims]
    runs = []
    for run_idx in range(1, n_runs + 1):
        label = f"partB_stage2_{rubric_tag}_run{run_idx}"
        save_path = f"{OUT_DIR}/partB_stage2_{rubric_tag}/run_{run_idx}.json"
        res = guarded_batch_call(
            state, consecutive_errors, label, save_path,
            client=client, verified_ledger_text=er009t.LEDGER_TEXT, source_article_text=None,
            claims=batch_claims, rubric_text=rubric_text,
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


# ------------------------------------------------------------
# (C) Hormuz許容5/NG5(既存Trial Aのclaim定義を再利用、Stage2のみ)
# ------------------------------------------------------------
def hormuz_accept_ng_claims() -> list:
    _, claims = hz.build_claims()
    return [c for c in claims if c["group"] in ("accept", "ng")]


def run_part_c_hormuz(client, state, consecutive_errors, n_runs, rubric_text, rubric_tag) -> dict:
    claims = hormuz_accept_ng_claims()
    hormuz_ledger = claims[0]["ledger_text"]
    batch_claims = [{"claim_text": c["claim_text"], "origin": c["origin"],
                      "related_fact_id": c["related_fact_id"], "local_context": c["local_context"],
                      "section_type": "body"} for c in claims]
    runs = []
    for run_idx in range(1, n_runs + 1):
        label = f"partC_hormuz_{rubric_tag}_run{run_idx}"
        save_path = f"{OUT_DIR}/partC_hormuz_{rubric_tag}/run_{run_idx}.json"
        res = guarded_batch_call(
            state, consecutive_errors, label, save_path,
            client=client, verified_ledger_text=hormuz_ledger, source_article_text=None,
            claims=batch_claims, rubric_text=rubric_text,
        )
        runs.append(res)

    per_claim_rows = []
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
        if c["expected"] == "PASS":
            false_block = sum(1 for m in observed if m == "BLOCKING")
            false_pass = 0
        else:
            false_pass = sum(1 for m in observed if m != "BLOCKING")
            false_block = 0
        per_claim_rows.append({
            "group": c["group"], "sub_id": c["sub_id"], "claim_text": c["claim_text"],
            "expected": c["expected"], "observed_labels": labels,
            "false_pass_count": false_pass, "false_block_count": false_block,
        })
    return {
        "per_claim_rows": per_claim_rows,
        "accept_false_block_total": sum(r["false_block_count"] for r in per_claim_rows if r["group"] == "accept"),
        "ng_false_pass_total": sum(r["false_pass_count"] for r in per_claim_rows if r["group"] == "ng"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    parser.add_argument("--rubric", choices=sorted(RUBRIC_VARIANTS), default="V4")
    parser.add_argument("--skip_a", action="store_true")
    parser.add_argument("--skip_b", action="store_true")
    parser.add_argument("--skip_c", action="store_true")
    args = parser.parse_args()

    rubric_tag = args.rubric
    rubric_text = RUBRIC_VARIANTS[rubric_tag]

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]

    stopped, stop_reason = False, None
    part_a = {"per_claim_rows": [], "misdowngrade_total": 0}
    part_b = {"per_flag_rows": [], "misdowngrade_total": 0}
    part_c = {"per_claim_rows": [], "accept_false_block_total": 0, "ng_false_pass_total": 0}

    try:
        if not args.skip_a:
            part_a = run_part_a(client, state, consecutive_errors, args.n_runs, rubric_text, rubric_tag)
        if not args.skip_b:
            part_b = run_part_b_stage2(client, state, consecutive_errors, args.n_runs,
                                        build_safety12_claims(), rubric_text, rubric_tag)
        if not args.skip_c:
            part_c = run_part_c_hormuz(client, state, consecutive_errors, args.n_runs, rubric_text, rubric_tag)
    except TrialAbort as e:
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
        },
        "part_b_safety12_stage2": {
            "misdowngrade_total": part_b["misdowngrade_total"],
            "n_flags": len(part_b["per_flag_rows"]),
        },
        "part_c_hormuz_accept_ng": {
            "accept_false_block_total": part_c["accept_false_block_total"],
            "ng_false_pass_total": part_c["ng_false_pass_total"],
            "n_claims": len(part_c["per_claim_rows"]),
        },
    }
    save_json(f"{OUT_DIR}/summary_safety_control_02_{rubric_tag}.json", {
        "summary": summary, "part_a": part_a, "part_b_stage2": part_b, "part_c_hormuz": part_c,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
