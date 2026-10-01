# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_meta_hook_02.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_30 Part1: Hook rubric V4で
# boundary-1-dramatizationのfalse block残存を是正できるかの最小修正1回
# 再測定 + Trial C期待2: 「users」claimをBLOCKING経路へ強制した場合の
# actor_rewrite_guard_ok実挙動の確認)
# ============================================================
# 目的:
# 1) 委任_29のV3実測(er052_output/open233_element_trial_meta_hook_01/
#    summary_meta_hook_trialb_v3.json)で、boundary-1-dramatization
#    ("The surprise came halfway through the call.")のみがn=2ともBLOCKING
#    のまま残存した(元Hook accept-1/accept-4は解消済み)。Fable判定
#    (design書§10の境界例定義に該当、許容が正解)に基づき追加したHook
#    rubric V4(`er052_open233_self_recovery_stage2_hook_01.
#    HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V4`)で、boundary-1(n=2)・
#    元Hook accept-1(n=2)・NG4群(n=2、委任文の要求n=1以上を満たす)を
#    1 batch×2 runで再測定する。
# 2) neg1 cycle2実データ(disclosure doc記載のMUSE-HC-012「社内テスト
#    誤読」claim)が、重大誤解原則配線後のStage1(V4A)では非検出
#    (`LEDGER_COMPLIANT`、委任_29 §27-5で既に確認済み)になったため、
#    「BLOCKING経路を強制した場合」のStage3 actor_rewrite_guard_ok実挙動
#    (委任文「期待2」)を、既存iter7実データの実際の過去BLOCKING判定
#    (`er052_output/open233_self_recovery_flow_runner_01_iter7/
#    instances_s1/neg1_meta_b3prod_a2.json`cycle[1]のstage2_results、
#    実データ・逐語、捏造なし)をそのまま`single_text_rewrite`へ投入して
#    1 run観測する。
#
# 重要な設計制約(既存er052_open233_element_trial_meta_hook_01.pyと同一
# 原則を踏襲):
# - `er052_open233_self_recovery_flow_runner_01`(以下runner)の
#   `record_call`/`save_budget_state`は、呼び出し元が渡すstate dictの
#   中身に関わらずrunner自身の固定`BUDGET_STATE_PATH`(他delegationの
#   既存証跡)へ書き込む副作用を持つため、`single_text_rewrite`呼び出し
#   箇所では`unittest.mock.patch.object(runner, "save_budget_state", ...)`
#   /`check_budget`で必ずこの副作用を遮断する。
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - claim_textは全て実データ逐語引用(既存iter7証跡から読み取り、捏造
#   Ledger factは無い)。
from __future__ import annotations

import json
import os
import time
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_element_trial_meta_hook_01 as mh1
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_stage2_hook_01 as s2h
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_element_trial_meta_hook_02"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ag_30.json"
TOTAL_BUDGET_JPY = 5.0  # 委任_30 Part1(Hook V4、≤¥4)+Trial C期待2(≤¥1)合算Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.4f}が委任_30 Part1+TrialC期待2 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def record(state: dict, consecutive_errors: list, label: str, cost: float, ok: bool) -> None:
    state["cumulative_calls"] += 1
    if ok:
        state["cumulative_jpy"] += cost
        state["history"].append({"label": label, "cost_jpy": cost})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")


# ------------------------------------------------------------
# Part1: Hook rubric V4のboundary-1/元Hook/NG4群 再測定
# ------------------------------------------------------------
V4_SUBSET_SUB_IDS = [
    "accept-1-original-hook", "boundary-1-dramatization",
    "ng-1-unconfirmed-person", "ng-2-unconfirmed-action",
    "ng-3-unconfirmed-number", "ng-4-fact-reversal",
]
N_RUNS_V4 = 2


def run_part1_hook_v4(client, state, consecutive_errors, meta_fixture) -> dict:
    subset = [c for c in mh1.HOOK_CLAIMS if c["sub_id"] in V4_SUBSET_SUB_IDS]
    assert len(subset) == len(V4_SUBSET_SUB_IDS), "subsetの抽出漏れ"
    batch_claims = [{"claim_text": c["claim_text"], "origin": "translation",
                      "related_fact_id": "MUSE-HC-006"} for c in subset]
    title_hook_text = f"{mh1.TITLE}\n\n{mh1.NEG1_ORIGINAL_HOOK}"

    hook_runs = []
    for run_idx in range(1, N_RUNS_V4 + 1):
        check_budget(state)
        label = f"partD_hookstage2_V4_run{run_idx}"
        save_path = f"{OUT_DIR}/trialD_hookstage2_V4/run_{run_idx}.json"
        last_err = None
        result = None
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                result = s2h.run_stage2_hook_batch(
                    client, meta_fixture["ledger_text"], meta_fixture.get("source_article_text"),
                    title_hook_text, batch_claims, model=s2p.MODEL,
                    hook_rubric_text=s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V4)
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        if result is not None:
            record(state, consecutive_errors, label, result["cost_jpy"], True)
            save_json(save_path, result)
            hook_runs.append(result)
        else:
            record(state, consecutive_errors, label, 0.0, False)
            save_json(save_path, {"error": last_err})

    rows = []
    for idx, c in enumerate(subset):
        labels = []
        for res in hook_runs:
            judgments = res["parsed"].get("judgments", [])
            match = next((j for j in judgments if j.get("claim_index") == idx), None)
            if match is not None:
                labels.append({"materiality": match["materiality"], "basis": match.get("basis")})
        observed = [lb["materiality"] for lb in labels]
        if c["group"] == "ng":
            false_pass_observed = [m for m in observed if m != "BLOCKING"]
            false_block_observed = []
        else:
            false_block_observed = [m for m in observed if m == "BLOCKING"]
            false_pass_observed = []
        rows.append({
            "sub_id": c["sub_id"], "group": c["group"], "claim_text": c["claim_text"],
            "hook_stage2_labels": labels,
            "false_block_count": len(false_block_observed),
            "false_pass_count": len(false_pass_observed),
        })
    return {
        "hook_stage2_rows": rows,
        "false_block_total": sum(r["false_block_count"] for r in rows),
        "false_pass_total": sum(r["false_pass_count"] for r in rows),
    }


# ------------------------------------------------------------
# Trial C期待2: 「users」claimをBLOCKING経路へ強制した場合のactor guard実挙動
# ------------------------------------------------------------
def load_real_blocking_dev_record() -> dict:
    """iter7実データ(既存証跡、読み取りのみ)から、neg1 cycle2で実際に
    BLOCKING判定だった「contract workers would make the calls」claimの
    stage2_results行をそのまま返す(dev/materiality/rewrite_kind/basis/
    rewrite_hint、全て実データ逐語、捏造なし)。"""
    with open(mh1.IT7_S1_PATH, encoding="utf-8") as f:
        d = json.load(f)
    cycle1 = d["cycles"][1]
    row = next(sr for sr in cycle1["stage2_results"]
               if "contract workers would make the calls" in sr["claim_text"])
    assert row["materiality"] == "BLOCKING", "実データの前提(BLOCKING)が崩れている"
    return row


def run_trial_c_expectation2(client, state, consecutive_errors, meta_fixture) -> dict:
    cycle2_article = mh1.load_neg1_cycle2_article()
    row = load_real_blocking_dev_record()
    claim_rec = {
        "claim_text": row["claim_text"], "rewrite_kind": row["rewrite_kind"],
        "dev": row["dev"], "materiality": "BLOCKING", "basis": row["basis"],
        "rewrite_hint": row.get("rewrite_hint", "") or "",
    }
    fixture_main = {"ledger_text": meta_fixture["ledger_text"], "article_text": cycle2_article,
                     "source_article_text": meta_fixture.get("source_article_text")}
    check_budget(state)
    call_log: list = []
    # 注意(委任_30、本関数固有の実装注意): `runner.single_text_rewrite`内部の
    # `simple_llm_call`は`runner.record_call`を直接呼び、渡した`state`dictを
    # その場でmutateする(`state["cumulative_jpy"] += cost`、save_budget_state
    # 呼び出しのみ下記でmockして無害化)。そのため呼び出し後に`record()`で
    # 二重計上してはならない(初回実装でこの二重計上バグが発生し、本注釈
    # 追加時に是正・再集計した)。
    with mock.patch.object(runner, "save_budget_state", lambda s: None), \
         mock.patch.object(runner, "check_budget", lambda s: None):
        stage3_result = runner.single_text_rewrite(
            client, state, consecutive_errors, call_log, "partD_actorguard_rewrite",
            fixture_main, "article_text", claim_rec)
    save_budget_state(state)
    save_json(f"{OUT_DIR}/trialD_actorguard.json", {
        "real_dev_record": row, "problem_kind_assigned": claim_rec.get("problem_kind"),
        "stage3_result": stage3_result, "call_log": call_log,
    })
    return {
        "problem_kind_assigned": claim_rec.get("problem_kind"),
        "method": stage3_result.get("method"), "guard_ok": stage3_result.get("guard_ok"),
        "updated_text_contains_users": "users" in (stage3_result.get("updated_text") or ""),
        "updated_text_contains_employees": "employees" in (stage3_result.get("updated_text") or ""),
        "target_sentence": stage3_result.get("target_sentence"),
        "after_fragment": stage3_result.get("after_fragment"),
    }


def main():
    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    meta_fixture = next(f for f in g6.step2_fixtures() if f["id"] == "Meta_run03_standard")

    stopped, stop_reason = False, None
    part1 = {}
    trial_c2 = {}
    try:
        part1 = run_part1_hook_v4(client, state, consecutive_errors, meta_fixture)
        trial_c2 = run_trial_c_expectation2(client, state, consecutive_errors, meta_fixture)
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "part1_false_block_total": part1.get("false_block_total"),
        "part1_false_pass_total": part1.get("false_pass_total"),
        "trial_c2": trial_c2,
    }
    save_json(f"{OUT_DIR}/summary_meta_hook_02.json", {
        "summary": summary, "part1": part1, "trial_c2": trial_c2,
    })
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
