# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_s1u_alt_compare_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, 委任_11 作業C)
# ============================================================
# 目的: 委任_11 作業C(Opus L2 #2論点2推奨1/2)。iteration 2でS1-U
# (S1-D reasoning effort=high、union screen)を適用した7 instanceに対し、
# より安価な代替2案を実測比較する。
#   (a) 2×V4A union: 既存Stage1(V4A)出力(reuse、¥0)を1本目の標本とし、
#       新規1 callのV4A再実行を2本目の標本として、BLOCKING(severity=MAJOR)
#       claimをunion(fail-closedのOR)する。
#   (b) S1-D reasoning effort=medium / low: 既存S1-D Trial実装
#       (er052_open233_self_recovery_s1d_trial_01.py)のPrompt/Schema/
#       コスト計算関数を read-only で借用し、reasoning effortだけを
#       medium/lowへ変えた新規1 callを、7 instance × 2 effort = 14回実行する。
#
# 受入条件(委任文§3): 既知3 miss(B2_hormuz/B3/hormuz_run02_advanced)を
# 全て捕捉し、かつ本スクリプトの対象に含まれるnegative instance
# (neg4/neg6/neg7、iteration2でS1-U適用済みの3件。委任文の「negative 7件」
# 全体ではなく、本比較の対象7 instanceに含まれる範囲でのみ判定する制約を
# 明記する)で追加BLOCK ≤1件。
#
# 設計制約(既存er052系Trialと同一原則): Production code(er003/er009/
# er010/er012/er019)は一切変更しない。Model Routing Contractは経由しない。
# API keyは環境変数のみ。保存jsonにはprompt本体ではなくprompt_sha256のみ
# 記録する。本スクリプト自身のbudget_state/record_call/save_budget_state
# で完結させ(既存委任_09で検出した他委任証跡汚染バグの再発防止と同一
# パターン)、er052_open233_self_recovery_s1d_trial_01.py側のbudget機構
# には一切触れない(同モジュールからはPrompt/Schema/コスト計算関数の
# 読み取りのみ)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_s1d_trial_01 as s1d

OUT_DIR = "er052_output/open233_self_recovery_s1u_alt_compare_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233o_c.json"
TOTAL_BUDGET_JPY = 5.0  # 委任_11 作業C Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
MODEL = "gpt-6-luna"

# 委任_11作業C対象7 instance(iteration2でs1u_screen_used=Trueだった全件、
# er052_output/open233_self_recovery_flow_runner_01_iter2/instances/*.json
# から機械確認済み)。
TARGET_INSTANCE_IDS = [
    "bgroup_B2_hormuz", "bgroup_B3", "hormuz_run02_advanced", "hormuz_run03_advanced",
    "neg4_smallbag_div_a2", "neg6_smallbag_div_b1b", "neg7_meta_prodrunner_b1b",
]
KNOWN_RECALL_MISS_IDS = {"bgroup_B2_hormuz", "bgroup_B3", "hormuz_run02_advanced"}
NEGATIVE_IDS = {"neg4_smallbag_div_a2", "neg6_smallbag_div_b1b", "neg7_meta_prodrunner_b1b"}


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_11作業C Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def record_call(state: dict, consecutive_errors: list, label: str, cost_jpy: float, ok: bool) -> None:
    state["cumulative_calls"] += 1
    if ok:
        state["cumulative_jpy"] += cost_jpy
        state["history"].append({"label": label, "cost_jpy": cost_jpy})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def run_v4a_fresh(client, state, consecutive_errors, label, fixture) -> dict:
    check_budget(state)
    t0 = time.time()
    result = trial.run_trial_deviation_check(
        client, fixture["ledger_text"], fixture["article_text"], MODEL, "V4A",
        include_related_fact_id=True, source_article_text=fixture.get("source_article_text"),
    )
    elapsed = round(time.time() - t0, 3)
    cost = round(s1d.official_cost_jpy(result["usage"]), 4)
    record_call(state, consecutive_errors, label, cost, True)
    blocking = [d for d in result["parsed"].get("deviations", []) if d.get("severity") == "MAJOR"]
    return {"label": label, "cost_jpy": cost, "usage": result["usage"], "elapsed_seconds": elapsed,
            "prompt_sha256": s1d.sha256_text(result["prompt"]), "blocking_count": len(blocking),
            "blocking_deviations": blocking}


def run_s1d_with_effort(client, state, consecutive_errors, label, fixture, effort: str) -> dict:
    """`er052_open233_self_recovery_s1d_trial_01.py`のPrompt/Schema/コスト
    計算関数(read-only借用)を使い、reasoning effortだけを可変にした
    新規1 call(同モジュールの`run_s1d_check`は`vfl01.REASONING_EFFORT`
    ="high"固定のため、本比較専用にeffort引数を追加した薄いラッパー)。"""
    check_budget(state)
    prompt = s1d.build_s1d_prompt(fixture["ledger_text"], fixture["article_text"],
                                   fixture.get("source_article_text"))
    t0 = time.time()
    response = client.responses.create(
        model=MODEL, reasoning={"effort": effort},
        text={"format": {"type": "json_schema", **s1d.S1D_JSON_SCHEMA}},
        input=[{"role": "developer", "content": s1d.S1D_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    deviations = parsed.get("deviations", [])
    blocking = [d for d in deviations if d.get("materiality") == "BLOCKING"]
    usage_obj = getattr(response, "usage", None)
    input_tokens = getattr(usage_obj, "input_tokens", None) if usage_obj else None
    output_tokens = getattr(usage_obj, "output_tokens", None) if usage_obj else None
    cached_tokens = None
    reasoning_tokens = None
    if usage_obj is not None:
        in_details = getattr(usage_obj, "input_tokens_details", None)
        if in_details is not None:
            cached_tokens = getattr(in_details, "cached_tokens", None)
        out_details = getattr(usage_obj, "output_tokens_details", None)
        if out_details is not None:
            reasoning_tokens = getattr(out_details, "reasoning_tokens", None)
    usage = {"input_tokens": input_tokens, "cached_input_tokens": cached_tokens,
              "output_tokens": output_tokens, "reasoning_tokens": reasoning_tokens}
    cost = round(s1d.official_cost_jpy(usage), 4)
    record_call(state, consecutive_errors, label, cost, True)
    return {"label": label, "effort": effort, "cost_jpy": cost, "usage": usage, "elapsed_seconds": elapsed,
            "prompt_sha256": s1d.sha256_text(prompt), "blocking_count": len(blocking),
            "blocking_deviations": blocking}


def label_for(instance_id: str, blocking_found: bool) -> str | None:
    if not blocking_found:
        return None
    if instance_id in KNOWN_RECALL_MISS_IDS:
        return "true_positive"
    if instance_id in NEGATIVE_IDS:
        return "false_positive"
    return "unlabeled"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]

    all_instances = {inst["instance_id"]: inst for inst in runner.build_target_instances()}
    results = []
    stopped, stop_reason = False, None

    for instance_id in TARGET_INSTANCE_IDS:
        cache_path = f"{OUT_DIR}/instances/{instance_id}.json"
        if args.resume and os.path.exists(cache_path):
            with open(cache_path, encoding="utf-8") as f:
                results.append(json.load(f))
            continue
        inst = all_instances[instance_id]
        fixture = inst["fixture"]
        try:
            # (a) 2×V4A union: 1本目=既存Stage1出力(reuse、¥0)。stage1_mode=
            # "fresh"のinstance(hormuz_run02_advanced)は、iteration 2で
            # s1u_screen_used=Trueだった時点で「その時のfresh V4A run自体は
            # ACCEPTABLE(=MAJOR blocking 0件)だったからこそS1-Uが発火した」
            # ことが既に確定しているため(stage1_union_screenの発火条件が
            # overall_status!=LEDGER_DEVIATION)、新規に呼び直さずblocking 0件
            # として扱う(二重課金回避、事実と矛盾しない)。
            if inst["stage1_mode"] == "reuse":
                existing_stage1 = runner.stage1_reuse(inst["stage1_source"])
                sample1_blocking = [d for d in existing_stage1.get("deviations", []) if d.get("severity") == "MAJOR"]
                sample1_source = "reuse"
            else:
                sample1_blocking = []
                sample1_source = "fresh_prior_run_was_acceptable(iter2で確定済み、再課金なし)"
            v4a_run2 = run_v4a_fresh(client, state, consecutive_errors, f"{instance_id}_v4a_run2", fixture)
            union_blocking_count = len(sample1_blocking) + v4a_run2["blocking_count"]
            v4a_union_found = union_blocking_count > 0

            s1d_medium = run_s1d_with_effort(client, state, consecutive_errors,
                                              f"{instance_id}_s1d_medium", fixture, "medium")
            s1d_low = run_s1d_with_effort(client, state, consecutive_errors,
                                           f"{instance_id}_s1d_low", fixture, "low")

            result = {
                "instance_id": instance_id, "group": inst["group"],
                "known_recall_miss": instance_id in KNOWN_RECALL_MISS_IDS,
                "negative": instance_id in NEGATIVE_IDS,
                "v4a_union": {
                    "sample1_source": sample1_source,
                    "sample1_blocking_count": len(sample1_blocking),
                    "sample2_cost_jpy": v4a_run2["cost_jpy"],
                    "sample2_blocking_count": v4a_run2["blocking_count"],
                    "union_blocking_count": union_blocking_count,
                    "found": v4a_union_found,
                    "label": label_for(instance_id, v4a_union_found),
                },
                "s1d_medium": {"cost_jpy": s1d_medium["cost_jpy"], "found": s1d_medium["blocking_count"] > 0,
                                "blocking_count": s1d_medium["blocking_count"],
                                "label": label_for(instance_id, s1d_medium["blocking_count"] > 0)},
                "s1d_low": {"cost_jpy": s1d_low["cost_jpy"], "found": s1d_low["blocking_count"] > 0,
                             "blocking_count": s1d_low["blocking_count"],
                             "label": label_for(instance_id, s1d_low["blocking_count"] > 0)},
            }
            results.append(result)
            save_json(cache_path, result)
        except TrialAbort as e:
            stopped = True
            stop_reason = str(e)
            break

    def _accept(variant_key: str) -> dict:
        tp = sum(1 for r in results if r.get(variant_key, {}).get("label") == "true_positive")
        fp = sum(1 for r in results if r.get(variant_key, {}).get("label") == "false_positive")
        known_miss_caught = sum(
            1 for r in results if r["known_recall_miss"] and r.get(variant_key, {}).get("found"))
        return {"true_positive_count": tp, "false_positive_count": fp,
                "known_recall_miss_caught": known_miss_caught,
                "known_recall_miss_total": sum(1 for r in results if r["known_recall_miss"]),
                "meets_acceptance": (
                    known_miss_caught == sum(1 for r in results if r["known_recall_miss"]) and fp <= 1)}

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed": len(results), "n_instances_planned": len(TARGET_INSTANCE_IDS),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"], "cumulative_errors": state["cumulative_errors"],
        "acceptance": {
            "v4a_union": _accept("v4a_union"),
            "s1d_medium": _accept("s1d_medium"),
            "s1d_low": _accept("s1d_low"),
        },
    }
    save_json(f"{OUT_DIR}/summary_s1u_alt_compare.json", {"summary": summary, "results": results})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
