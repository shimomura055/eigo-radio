# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_safety_control_06.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_61: 判定原則文整合版body rubric V7bの再較正。委任_55の_05.pyをV7b用に
# 複製。出力先は`er052_output/open233_safety_control_04/`。_05.pyと出力`open233_safety_control_03`は不変)
# ============================================================
# 注意(命名): 委任文は`er052_open233_element_trial_safety_control_03.py`を指定したが、
# 同名ファイルは既に存在し(委任_29系の別スクリプト、commit済み)、上書きできないため、
# 本スクリプトは未使用の`_05`として作成した。出力先は委任文どおり
# `er052_output/open233_safety_control_03/`。
#
# 目的: ユーザー決定(2026-10-03、線引きの正式採用、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`
# 未達)に伴うbody rubric V7(`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7`、design書
# §4-26)を、Stage 2(body判定)単体に当てて再較正する。Stage 1/Stage 3は実行しない(新しい
# Checker呼び出しなし)。入力は既存の較正セット(`er052_open233_element_trial_safety_control_02.py`
# のPart A/B/C、および`build_target_instances()`の保存済みfixture)をそのまま使う。
#
#   (a) Safety-critical claim(更新後の定義、A5-1・Meta-1/2除外後の6件)=期待BLOCKING
#   (b) Safety12(er009の9フラグ)=期待BLOCKING
#   (c) Hormuz許容5/NG5=従来(V6、委任_33)と同じ
#   (d) 新しい例3件: 例1(Meta-1)=QUALITY、例2(They enjoyed...)=ACCEPTABLE、K19=QUALITY
#   (e) 再分類docで重大(見逃し0)とした種類: K16(neg3の時期)・K20(B4-a型の動機創作)=期待BLOCKING
#       (A2A3-0・B4-aは(a)と同一claimのため(a)の結果を参照し二重に実行しない)
#   (f) 負例(neg1_meta_b3prod_a2のK11/K12/K13、期待は非BLOCKING)
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録(各claimの入力はinputs.jsonに平文で保存)。
# - 既存sc02/s2c/runnerの関数・定数はread-onlyで再利用するのみ(sc02のOUT_DIR等のモジュール変数を
#   本スクリプト専用に一時的に差し替える。sc04と同じ方式)。
from __future__ import annotations

import argparse
import difflib
import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_element_trial_safety_control_02 as sc02
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_safety_control_04"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ar_61.json"
RUBRIC_TAG = "V7b"
RUBRIC_TEXT = s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
BASELINE_V6_SUMMARY = "er052_output/open233_element_trial_safety_control_04/summary_safety_control_04_V6.json"

# (d)(e)(f)の入力。claim文は再分類doc(`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`)の
# 「原文」(逐語)。related_fact_idは同docのinstance/fact表記。
# 各要素: (group_key, instance_id, [claim定義])
CUSTOM_GROUPS = [
    ("D1_meta", "meta_run03_standard", [
        {"part": "d", "sub_id": "d-ex1(K04/Meta-1)", "expected": "QUALITY", "related_fact_id": "MUSE-HC-010",
         "claim_text": "Also, some calls needed user information to continue."},
        {"part": "d", "sub_id": "d-ex2(K10)", "expected": "ACCEPTABLE", "related_fact_id": "MUSE-HC-012",
         "claim_text": "They enjoyed AI’s convenience, but a human was on the other end. They did not realize it."},
    ]),
    ("D2_a2a3", "safety_A2A3", [
        {"part": "d", "sub_id": "d-K19", "expected": "QUALITY", "related_fact_id": "HF-009",
         "claim_text": "Just after the charge plan disappeared, prices began to fall."},
    ]),
    ("E1_neg3", "neg3_hormuz_prodrunner_b1b", [
        {"part": "e", "sub_id": "e-K16", "expected": "BLOCKING", "related_fact_id": "HF-009",
         "claim_text": "The fee plan left the stage, but the events driving oil prices—and the prices "
                       "themselves—quickly returned."},
    ]),
    ("E2_a4", "safety_A4", [
        {"part": "e", "sub_id": "e-K20(B4-a型)", "expected": "BLOCKING", "related_fact_id": "MUSE-HC-006",
         "claim_text": "The idea was practical: when AI struggled, a person could help."},
    ]),
    ("F1_neg1", "neg1_meta_b3prod_a2", [
        {"part": "f", "sub_id": "f-K11", "expected": "NOT_BLOCKING", "related_fact_id": "MUSE-HC-012",
         "claim_text": "A Meta executive admitted the mistake. The test had begun without clearly telling users."},
        {"part": "f", "sub_id": "f-K12", "expected": "NOT_BLOCKING", "related_fact_id": "MUSE-HC-012",
         "claim_text": "A user might think the exchange was with AI, even though a person was involved."},
        {"part": "f", "sub_id": "f-K13", "expected": "NOT_BLOCKING", "related_fact_id": "MUSE-HC-012",
         "claim_text": "The test began without clearly telling users that contract workers would make the calls."},
    ]),
]


def use_local_dirs() -> None:
    sc02.OUT_DIR = OUT_DIR
    sc02.BUDGET_STATE_PATH = BUDGET_STATE_PATH


def write_rubric_diff() -> str:
    """変更前(V6)→変更後(V7)の原則文・rubric文の差分(逐語、unified diff)。¥0。"""
    path = f"{OUT_DIR}/rubric_diff.md"
    v6 = s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7.splitlines()
    v7 = s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B.splitlines()
    d1 = "\n".join(difflib.unified_diff(v6, v7, "body rubric V7 (旧、定数として残す)", "body rubric V7b (新)", lineterm=""))
    d2 = "\n".join(difflib.unified_diff(
        s2p.MATERIALITY_RUBRIC_V7.splitlines(), s2p.MATERIALITY_RUBRIC_V7B.splitlines(),
        "s2p.MATERIALITY_RUBRIC_V7 (旧、定数として残す)", "s2p.MATERIALITY_RUBRIC_V7B (新)", lineterm=""))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# rubric差分(委任_61、V7 -> V7b、逐語)\n\n"
                "## 1. body rubric: V7 -> V7b(`er052_open233_self_recovery_stage2_calibration_01.py`)\n\n"
                "V7は`RUBRIC_R3_TRIPLE_PRIME + MISCONCEPTION_PRINCIPLE_TEXT_V7`(= V6の原則文へ追記)。"
                "V4〜V6の原則文は削除・編集していない。\n\n```diff\n" + d1 + "\n```\n\n"
                "## 2. Stage 2 production既定rubric(`er052_open233_self_recovery_stage2_production_01.py`)\n\n"
                "`MATERIALITY_RUBRIC_V7`(旧、残す) -> `MATERIALITY_RUBRIC_V7B`(新、末尾の「迷えばBLOCKING」のみ置換、"
                "QUALITYの「動機の帰属」は不変。runnerのbody判定は上記1のV7を使う)。\n\n```diff\n" + d2 + "\n```\n\n"
                "## 3. 不変のもの\n\n"
                "`FLOOR_FLAGS`・precheck・主体置換ガード・`MAX_CYCLES`・Hook専用rubric(V3/V4)・"
                "`DISCLOSURE_GAP_NEGATION_RE`(否定形限定)は変更していない。\n")
    return path


def build_custom_inputs() -> dict:
    instances = {i["instance_id"]: i for i in runner.build_target_instances()}
    out = {}
    for key, iid, claims in CUSTOM_GROUPS:
        fx = instances[iid]["fixture"] if "fixture" in instances[iid] else instances[iid]
        recs = []
        for c in claims:
            lc, fb = s2p.build_local_context(fx["article_text"], c["claim_text"])
            recs.append({**c, "origin": "translation", "local_context": lc, "fallback_used": fb,
                         "section_type": "body"})
        out[key] = {"instance_id": iid, "fixture": fx, "claims": recs}
    return out


def run_custom_groups(client, state, ce, n_runs, keys, tag) -> dict:
    inputs = build_custom_inputs()
    rows = []
    save_inputs = {k: {"instance_id": v["instance_id"], "claims": v["claims"]} for k, v in inputs.items()
                   if k in keys}
    sc02.save_json(f"{OUT_DIR}/{tag}/inputs.json", save_inputs)
    for key in keys:
        g = inputs[key]
        runs = []
        for run_idx in range(1, n_runs + 1):
            label = f"{tag}_{RUBRIC_TAG}_{key}_run{run_idx}"
            save_path = f"{OUT_DIR}/{tag}/{key}/run_{run_idx}.json"
            res = sc02.guarded_batch_call(
                state, ce, label, save_path,
                client=client, verified_ledger_text=g["fixture"]["ledger_text"],
                source_article_text=g["fixture"].get("source_article_text"),
                claims=g["claims"], rubric_text=RUBRIC_TEXT,
            )
            runs.append(res)
        for idx, c in enumerate(g["claims"]):
            labels = []
            for res in runs:
                if "error" in res:
                    continue
                match = next((j for j in res["parsed"].get("judgments", []) if j.get("claim_index") == idx), None)
                if match is not None:
                    labels.append({"materiality": match["materiality"], "basis": match.get("basis"),
                                   "rewrite_hint": match.get("rewrite_hint")})
            obs = [lb["materiality"] for lb in labels]
            exp = c["expected"]
            if exp == "NOT_BLOCKING":
                ok = [m != "BLOCKING" for m in obs]
            else:
                ok = [m == exp for m in obs]
            rows.append({"group": key, "part": c["part"], "sub_id": c["sub_id"], "claim_text": c["claim_text"],
                         "related_fact_id": c["related_fact_id"], "expected": exp,
                         "observed_labels": labels, "n_observed": len(obs), "n_as_expected": sum(ok),
                         "n_not_blocking": sum(1 for m in obs if m != "BLOCKING"),
                         "n_blocking": sum(1 for m in obs if m == "BLOCKING")})
    return {"rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["probe", "main", "agg"], required=True)
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--budget-jpy", type=float, default=15.0)
    args = parser.parse_args()
    use_local_dirs()
    sc02.TOTAL_BUDGET_JPY = args.budget_jpy

    if args.stage == "agg":
        return agg()

    write_rubric_diff()
    client = vfl01.get_client()
    state = sc02.load_budget_state()
    ce = [0]
    stopped, reason = False, None
    try:
        if args.stage == "probe":
            res = run_custom_groups(client, state, ce, 1, ["D1_meta", "D2_a2a3"], "probe_d")
            sc02.save_json(f"{OUT_DIR}/probe_d/result.json", res)
        else:
            part_a = sc02.run_part_a(client, state, ce, args.n, RUBRIC_TEXT, RUBRIC_TAG)
            sc02.save_json(f"{OUT_DIR}/partA_result.json", part_a)
            part_b = sc02.run_part_b_stage2(client, state, ce, args.n, sc02.build_safety12_claims(),
                                            RUBRIC_TEXT, RUBRIC_TAG)
            sc02.save_json(f"{OUT_DIR}/partB_result.json", part_b)
            part_c = sc02.run_part_c_hormuz(client, state, ce, args.n, RUBRIC_TEXT, RUBRIC_TAG)
            sc02.save_json(f"{OUT_DIR}/partC_result.json", part_c)
            cust = run_custom_groups(client, state, ce, args.n, [k for k, _, _ in CUSTOM_GROUPS], "partDEF")
            sc02.save_json(f"{OUT_DIR}/partDEF_result.json", cust)
    except sc02.TrialAbort as e:
        stopped, reason = True, str(e)
    info = {"stage": args.stage, "n": args.n, "stopped": stopped, "stop_reason": reason,
            "cumulative_jpy": round(state["cumulative_jpy"], 4), "cumulative_calls": state["cumulative_calls"],
            "cumulative_errors": state["cumulative_errors"]}
    sc02.save_json(f"{OUT_DIR}/stage_{args.stage}_info.json", info)
    print(json.dumps(info, ensure_ascii=False, indent=2))


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def agg() -> None:
    part_a = _load(f"{OUT_DIR}/partA_result.json")
    part_b = _load(f"{OUT_DIR}/partB_result.json")
    part_c = _load(f"{OUT_DIR}/partC_result.json")
    cust = _load(f"{OUT_DIR}/partDEF_result.json")["rows"]
    state = _load(BUDGET_STATE_PATH)
    base = _load(BASELINE_V6_SUMMARY)["summary"]
    base_c = {r["sub_id"]: [l["materiality"] for l in r["observed_labels"]]
              for r in base["part_c_hormuz_accept_ng"]["per_claim_rows"]}
    c_rows = []
    c_same = True
    for r in part_c["per_claim_rows"]:
        obs = [l["materiality"] for l in r["observed_labels"]]
        b = base_c.get(r["sub_id"])
        # 従来(V6、n=1)と「期待に対する合否」が同じか(ラベル完全一致ではなく期待PASS/BLOCKの別で比較)
        def ok(ms, exp):
            return all((m != "BLOCKING") for m in ms) if exp == "PASS" else all(m == "BLOCKING" for m in ms)
        same = (b is not None) and ok(obs, r["expected"]) == ok(b, r["expected"])
        c_same = c_same and same
        c_rows.append({"sub_id": r["sub_id"], "expected": r["expected"], "v7": obs, "v6_baseline": b,
                       "same_verdict_as_v6": same})
    d_rows = [r for r in cust if r["part"] == "d"]
    e_rows = [r for r in cust if r["part"] == "e"]
    f_rows = [r for r in cust if r["part"] == "f"]
    criteria = {
        "a_safety_critical_misdowngrade_total": part_a["misdowngrade_total"],
        "a_n_claims": len(part_a["per_claim_rows"]),
        "b_safety12_misdowngrade_total": part_b["misdowngrade_total"],
        "b_n_flags": len(part_b["per_flag_rows"]),
        "c_accept_false_block_total": part_c["accept_false_block_total"],
        "c_ng_false_pass_total": part_c["ng_false_pass_total"],
        "c_all_same_verdict_as_v6": c_same,
        "d_all_as_expected_exact_label": all(r["n_as_expected"] == r["n_observed"] and r["n_observed"] > 0
                                              for r in d_rows),
        "e_misdowngrade_total": sum(r["n_not_blocking"] for r in e_rows),
        "f_false_block_total": sum(r["n_blocking"] for r in f_rows),
    }
    out = {
        "rubric": RUBRIC_TAG, "cost_jpy_total": round(state["cumulative_jpy"], 4),
        "calls": state["cumulative_calls"], "errors": state["cumulative_errors"],
        "criteria": criteria,
        "part_a_rows": part_a["per_claim_rows"], "part_b_rows": part_b["per_flag_rows"], "part_c_rows": c_rows,
        "part_d_rows": d_rows, "part_e_rows": e_rows, "part_f_rows": f_rows,
        "note_e": "A2A3-0・B4-aは(a)と同一claim(Part A、同じrubric・同じrun)のため(a)の結果を参照する。",
    }
    sc02.save_json(f"{OUT_DIR}/results_01.json", out)
    print(json.dumps({"cost_jpy_total": out["cost_jpy_total"], "calls": out["calls"], "criteria": criteria},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
