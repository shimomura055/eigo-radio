# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_neg3_stage2_n3_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_19 A-3)
# ============================================================
# 目的: neg3_hormuz_prodrunner_b1bのBLOCKING claim
# 「The fee plan left the stage, but the events driving oil prices—and
# the prices themselves—quickly returned.」(related_fact_id=HF-009)に
# ついて、Stage2のみをn=3で再現性測定する(既存Stage1出力[V4A run_1.json、
# `er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/
# c_negative/neg3_hormuz_prodrunner_b1b/V4A/run_1.json`]を再利用、Stage1
# API callは発生しない)。委任文§2 A-3(i): BLOCKING/QUALITYのブレ幅を
# 実測する。Guardrail≤¥0.5(本ファイル独自の予算管理、runner.OUT_DIR/
# runner.TOTAL_BUDGET_JPY[=rep10用]は一切変更しない)。
#
# 設計制約:
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - runner.run_stage2をそのまま呼ぶ(Stage2 promptは変更しない)。
# - 出力は新規ディレクトリのみへ書く。既存rep7/rep8/rep9出力は無変更。
# - 【既知の注意点、実行時に発覚・git checkoutで復旧済み】runner.record_call/
#   save_budget_state()はモジュール変数runner.BUDGET_STATE_PATH(実行時の
#   runner.OUT_DIR依存)へ無条件に書き込む。本ファイルはローカルのstate辞書
#   (cumulative_jpy等)を独自管理しているが、run_stage2内部のrecord_call呼び
#   出しはこのグローバルパスへも書き込んでしまうため、実行タイミングにより
#   既存rep9のbudget_state_c233v_18.jsonを上書きするリスクがある(実際に
#   発生し、git checkoutで復旧した)。再実行する場合は事前に
#   runner.OUT_DIR/runner.BUDGET_STATE_PATHを本ファイル専用の値へ明示的に
#   上書きしてから呼ぶこと。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp

OUT_PATH = "er052_output/open233_self_recovery_neg3_stage2_n3_01/summary_neg3_n3.json"
GUARDRAIL_JPY = 0.5

# rep9実測(instances_s1/neg3_hormuz_prodrunner_b1b.json cycle1
# stage2_results[0]["dev"])と一致する、Stage1 V4A run_1.jsonのdeviation
# そのもの(claim_in_article/issue/各changed_*フラグ/related_fact_id等)。
NEG3_CLAIM_TEXT = ("The fee plan left the stage, but the events driving oil "
                    "prices—and the prices themselves—quickly returned.")
NEG3_DEV = {
    "claim_in_article": NEG3_CLAIM_TEXT,
    "issue": ("The sentence describes the events as having quickly returned and as driving oil "
              "prices, whereas HF-009 reports that relevant attacks, blockade and tanker-safety "
              "concerns continued during the price movement. It changes continued events into "
              "returning events and asserts a causal role not established by the Ledger."),
    "severity": "MAJOR",
    "changed_fact": True, "changed_scope": False, "changed_causality": True,
    "changed_certainty": False, "changed_number": False, "changed_actor": False,
    "changed_negation": False, "changed_comparison": False, "changed_time": True,
    "unsupported_new_claim": True,
    "explanation": ("The timing changes from concerns that continued to events that returned, and "
                    "the sentence adds an unsupported causal link between those events and oil "
                    "prices."),
    "related_fact_id": "HF-009", "origin": "translation",
}


def main():
    client = vfl01.get_client()
    state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
    consecutive_errors = [0]

    src_path = dict(step3cmp.NEGATIVE_SOURCE_FILES)["neg3_hormuz_prodrunner_b1b"]
    fx = step3cmp.load_negative_fixture("neg3_hormuz_prodrunner_b1b", src_path)
    fixture = {"article_text": fx["article_text"], "ledger_text": fx["ledger_text"]}
    if fx.get("source_article_text") is not None:
        fixture["source_article_text"] = fx["source_article_text"]

    claims = [{"claim_text": NEG3_CLAIM_TEXT, "origin": "translation",
               "related_fact_id": "HF-009", "dev": dict(NEG3_DEV)}]

    runs = []
    call_log_all = []
    for i in range(1, 4):
        if state["cumulative_jpy"] >= GUARDRAIL_JPY:
            runs.append({"run": i, "skipped": True, "reason": f"guardrail_reached(¥{GUARDRAIL_JPY})"})
            continue
        call_log = []
        results = runner.run_stage2(client, state, consecutive_errors, call_log,
                                     f"neg3_n3_run{i}", fixture, claims)
        call_log_all.extend(call_log)
        cost = round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4)
        r0 = results[0]
        runs.append({
            "run": i, "materiality": r0.get("materiality"), "llm_materiality": r0.get("llm_materiality"),
            "basis": r0.get("basis"), "floor_reason": r0.get("floor_reason"),
            "rewrite_kind": r0.get("rewrite_kind"), "cost_jpy": cost,
            "cumulative_jpy_after": round(state["cumulative_jpy"], 4),
        })

    materialities = [r["materiality"] for r in runs if "materiality" in r]
    summary = {
        "instance_id": "neg3_hormuz_prodrunner_b1b", "fact_id": "HF-009",
        "claim_text": NEG3_CLAIM_TEXT, "n_completed": len(materialities),
        "materialities": materialities,
        "blocking_count": materialities.count("BLOCKING"),
        "quality_or_acceptable_count": sum(1 for m in materialities if m != "BLOCKING"),
        "runs": runs, "total_cost_jpy": round(state["cumulative_jpy"], 4),
        "guardrail_jpy": GUARDRAIL_JPY, "call_log": call_log_all,
    }
    runner.save_json(OUT_PATH, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "call_log"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
