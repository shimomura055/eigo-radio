# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_62: 承認済み対策を全て有効にした少数実flow確認 rep23)
# ============================================================
# 目的(ユーザー決定[5回目]、2026-10-04、選択肢3の手順4): 単体確認PASS後の少数実flow確認。
#   6 instance x n=2 = 12 instance-run、全スイッチ有効:
#   HANDOFF_MODE=violation_span / VS_MATCH_EXT=True / VS_EXPLAIN_SPLIT=True(P-strict-closed) /
#   JA_MODE=english_only / Stage 2 rubric=V7b(BODY_RUBRIC_DEFAULT) / FLOOR_VERIFY_MODE=time_only。
#   他は既定(MAX_CYCLES=2、HARD_MAX_CYCLES=3、CHECKER_SPANS_MODE=legacy)。
# 設計制約: Production code(er003*〜er019*)は変更しない。runner本体(er052_open233_self_recovery_flow_runner_01.py)
#   のロジックも変更しない(モジュール変数のスイッチ設定とOUT_DIR/予算状態ファイルの切替のみ、rep22実行スクリプトと同方式)。
#   本ファイルはOUT_DIR_REP23のみへ書く。TTSなし。API keyは環境変数(.env)のみ。
# instance選定: design書§5-1の指定どおり(meta_run03_standard / hormuz_run03_standard /
#   neg3_hormuz_prodrunner_b1b / safety_A4 / safety_A2A3 / safety_er009_changed_number)。
# 集計(--stage agg)は..._rep23_agg_01.py(API呼び出しなし、記録済みinstance JSONのみ)。
from __future__ import annotations

import argparse
import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner

OUT_DIR_REP23 = "er052_output/open233_self_recovery_flow_runner_01_rep23"
BUDGET_STATE_REP23 = f"{OUT_DIR_REP23}/budget_state_c233ao_62_rep23.json"

# design書§5-1の順(実行順もこの順。n=2はsample単位で全instanceを回す=s1全部→s2全部)
INSTANCE_IDS = ["hormuz_run03_standard", "meta_run03_standard", "neg3_hormuz_prodrunner_b1b",
                "safety_A4", "safety_A2A3", "safety_er009_changed_number"]

# 比較基準(同instanceの直近の記録。rep22に無いinstanceは直近のrepを使う。集計に記録する)
BASELINES = {
    "meta_run03_standard": ("rep22", [f"er052_output/open233_self_recovery_flow_runner_01_rep22/instances_s{i}/meta_run03_standard.json" for i in (1, 2, 3, 4)]),
    "hormuz_run03_standard": ("rep16", [f"er052_output/open233_self_recovery_flow_runner_01_rep16/instances_s{i}/hormuz_run03_standard.json" for i in (1, 2)]),
    "neg3_hormuz_prodrunner_b1b": ("rep17", [f"er052_output/open233_self_recovery_flow_runner_01_rep17/instances_s{i}/neg3_hormuz_prodrunner_b1b.json" for i in (1, 2)]),
    "safety_A4": ("rep14", ["er052_output/open233_self_recovery_flow_runner_01_rep14/instances/safety_A4.json"]),
    "safety_A2A3": ("rep18", [f"er052_output/open233_self_recovery_flow_runner_01_rep18/instances_s{i}/safety_A2A3.json" for i in (1, 2)]),
    "safety_er009_changed_number": ("rep22", ["er052_output/open233_self_recovery_flow_runner_01_rep22/instances_safety_a/safety_er009_changed_number.json"]),
}


def apply_switches(budget_jpy: float) -> None:
    runner.OUT_DIR = OUT_DIR_REP23
    runner.BUDGET_STATE_PATH = BUDGET_STATE_REP23
    runner.TOTAL_BUDGET_JPY = budget_jpy
    runner.HANDOFF_MODE = runner.HANDOFF_MODE_VIOLATION_SPAN
    runner.VS_MATCH_EXT = True
    runner.VS_EXPLAIN_SPLIT = True
    runner.JA_MODE = runner.JA_MODE_ENGLISH_ONLY
    runner.FLOOR_VERIFY_MODE = runner.validate_floor_verify_mode(runner.FLOOR_VERIFY_MODE_TIME_ONLY)
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def immediate_stop_check(r: dict) -> list:
    """作業2の即時STOP条件(a)(b)(c)を1 instance-run完了後に確認(dはTrialAbort/例外で別途)。"""
    reasons = []
    # (a) 日本語本文・タイトルの変更(english_onlyではJA側処理が一切呼ばれない)
    for c in r.get("cycles", []):
        if c.get("ja_text_after_rewrite") is not None or "ja_text_after_rewrite" in c:
            reasons.append(f"a:ja_text_after_rewrite in cycle {c.get('cycle')}")
        for rr in c.get("rewrite_records", []):
            if str(rr.get("mechanism", "")).startswith("paired"):
                reasons.append(f"a:paired mechanism in cycle {c.get('cycle')}")
    for cl in r.get("call_log", []):
        if "ja_" in str(cl.get("label", "")):
            reasons.append(f"a:ja_ label {cl.get('label')}")
    # (b) floor_verifyで解放されたclaim(人間/Fableが確認するまで追加runを止める)
    for c in r.get("cycles", []):
        for sr in c.get("stage2_results", []):
            if (sr.get("floor_verify") or {}).get("released"):
                reasons.append(f"b:floor_verify released (cycle {c.get('cycle')}): {sr.get('claim_text')[:80]}")
    # (c) Safety-critical登録が合格系で残存
    rap = r.get("residual_at_pass") or {}
    for d in rap.get("defs", []):
        if d.get("pass_with_residual_unflagged"):
            reasons.append(f"c:pass_with_residual_unflagged {d.get('sub_id')}")
    return reasons


def run_main(instance_ids, n, budget_jpy):
    apply_switches(budget_jpy)
    os.makedirs(OUT_DIR_REP23, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"stopped": False, "stop_reason": None, "runs": []}
    for sample_idx in range(1, n + 1):
        subdir = f"instances_s{sample_idx}"
        for iid in instance_ids:
            path = f"{OUT_DIR_REP23}/{subdir}/{iid}.json"
            if os.path.exists(path):  # probeで実行済み(同一構成)を再利用
                print(f"[skip existing] {subdir}/{iid}")
                continue
            try:
                r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                        stage1_cache=stage1_cache, instances_subdir=subdir)
            except runner.TrialAbort as e:
                log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
                break
            reasons = immediate_stop_check(r)
            print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
                  f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}")
            log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                                "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"],
                                "stop_check": reasons})
            if reasons:
                log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
                break
        if log["stopped"]:
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR_REP23}/run_log_{'probe' if n == 1 and len(instance_ids) == 1 else 'main'}.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:6000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["probe", "main", "agg"])
    ap.add_argument("--instances", default=",".join(INSTANCE_IDS))
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=30.0)
    args = ap.parse_args()
    if args.stage == "agg":
        import er052_open233_self_recovery_flow_runner_01_rep23_agg_01 as agg
        agg.run_agg(OUT_DIR_REP23, INSTANCE_IDS, BASELINES)
        return
    ids = [s.strip() for s in args.instances.split(",") if s.strip()]
    run_main(ids, args.n, args.budget_jpy)


if __name__ == "__main__":
    main()
