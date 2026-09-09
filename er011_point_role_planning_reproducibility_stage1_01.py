# ============================================================
# er011_point_role_planning_reproducibility_stage1_01.py
# FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01 作業2-(e)
# ============================================================
# 目的: Opusレビュー観点4「Trial-07のRole収束はFocus Moduleの因果経路が
# 存在しない(Role PlanningはFocus Moduleを受け取らない)」を踏まえ、
# 同一入力(Household Ledger/topic、Focus Moduleなし)でPoint Role
# Planningだけを追加抽選し(Writer呼び出しなし)、role分布の
# サンプリングばらつきを測る。Trial-07 baseline(N=3)/discovery_focus
# (N=3)のrole分布差が抽選ばらつきの範囲内かを判定するための補助データ。
#
# **読み取り専用検証タスクの一部として許可された極小LLM呼び出し
# (Fable委任: FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01の(e)の
# み)**。Production/Prompt/SSOT編集なし、Writer呼び出しなし、
# Git操作なし。run_point_role_planning()自体は無変更・無改変で
# そのままimportして呼ぶ(Production関数の再定義・monkeypatchなし)。
#
# 費用上限: ¥15(超過見込み時は途中で打ち切りrunを記録する)。
# 冒頭でcl.install()を有効化し、全API callのusageを記録する。
# ============================================================
from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_point_role_value_planning_01 as point_planning
import er006_model_routing_contract_01 as routing

OUT_DIR = "er011_output/point_role_planning_reproducibility_stage1_01"
N_RUNS = 10
BUDGET_JPY = 15.0

# Luna pricing (公式、er009_n1_point_overlap_cost_closeout_09.pyと同一値)
LUNA_INPUT = 0.20   # USD per 1M tokens
LUNA_CACHED_INPUT = 0.02  # USD per 1M tokens
LUNA_OUTPUT = 1.20  # USD per 1M tokens
USD_TO_JPY = 160.0


def cost_jpy(input_tokens, cached_input_tokens, output_tokens) -> float:
    non_cached_input = max((input_tokens or 0) - (cached_input_tokens or 0), 0)
    usd = (non_cached_input / 1_000_000) * LUNA_INPUT
    usd += ((cached_input_tokens or 0) / 1_000_000) * LUNA_CACHED_INPUT
    usd += ((output_tokens or 0) / 1_000_000) * LUNA_OUTPUT
    return round(usd * USD_TO_JPY, 4)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    household_theme = next(t for t in prod_gen.THEMES if t["theme_id"] == "household")
    topic = household_theme["topic"]
    verified_ledger_text = load_text(household_theme["ledger_path"])

    client = vfl01.get_client()
    writer_model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    reasoning_effort = prod_gen.REASONING_EFFORT

    results = []
    cumulative_jpy = 0.0
    for i in range(N_RUNS):
        existing_path = f"{OUT_DIR}/run{i}_full.json"
        if os.path.exists(existing_path):
            print(f"[stage1-e] run{i}: 既存結果を再利用(API再呼び出しなし)")
            with open(existing_path, encoding="utf-8") as f:
                role_plan_result = json.load(f)
            parsed = role_plan_result["parsed"]
            results.append({
                "run": i,
                "point_one_role": parsed["point_one"]["role"],
                "point_two_role": parsed["point_two"]["role"],
                "response_id": role_plan_result.get("response_id"),
                "model": role_plan_result.get("model"),
                "cost_jpy_estimate": None,
                "note": "reused_from_previous_partial_run",
            })
            continue
        if cumulative_jpy >= BUDGET_JPY:
            print(f"[stage1-e] budget cap JPY{BUDGET_JPY} reached, stopping before run{i} "
                  f"(cumulative JPY{cumulative_jpy:.2f})")
            break
        with cl.logging_context("point_role_planning_reproducibility_stage1", f"run{i}"):
            t0 = time.time()
            role_plan_result = point_planning.run_point_role_planning(
                client, topic, verified_ledger_text, model=writer_model,
                reasoning_effort=reasoning_effort)
            elapsed = time.time() - t0
        parsed = role_plan_result["parsed"]
        run_record = {
            "run": i,
            "point_one_role": parsed["point_one"]["role"],
            "point_two_role": parsed["point_two"]["role"],
            "elapsed_seconds": round(elapsed, 2),
            "response_id": role_plan_result.get("response_id"),
            "model": role_plan_result.get("model"),
        }
        results.append(run_record)
        with open(f"{OUT_DIR}/run{i}_full.json", "w", encoding="utf-8") as f:
            json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)

        # 直近callのusageから概算費用を加算(raw_usage_log.jsonlの最終行を読む)
        with open(f"{OUT_DIR}/raw_usage_log.jsonl", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        last = json.loads(lines[-1])
        run_cost = cost_jpy(last.get("input_tokens"), last.get("cached_input_tokens"),
                             last.get("output_tokens"))
        run_record["cost_jpy_estimate"] = run_cost
        cumulative_jpy += run_cost
        print(f"[stage1-e] run{i}: P1_role={parsed['point_one']['role'][:60]!r} "
              f"P2_role={parsed['point_two']['role'][:60]!r} cost=JPY{run_cost:.3f} "
              f"cumulative=JPY{cumulative_jpy:.2f}")

    with open(f"{OUT_DIR}/results.json", "w", encoding="utf-8") as f:
        json.dump({
            "management_id": "FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01",
            "work_item": "(e) Point Role Planning reproducibility (N=10, Household Ledger/topic, "
                         "no Focus Module, no Writer call)",
            "n_runs_completed": len(results),
            "n_runs_requested": N_RUNS,
            "budget_jpy": BUDGET_JPY,
            "cumulative_cost_jpy_estimate": round(cumulative_jpy, 2),
            "topic": topic,
            "ledger_path": household_theme["ledger_path"],
            "model": writer_model,
            "reasoning_effort": reasoning_effort,
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"[stage1-e] done. {len(results)}/{N_RUNS} runs, estimated cumulative cost JPY{cumulative_jpy:.2f}")


if __name__ == "__main__":
    main()
