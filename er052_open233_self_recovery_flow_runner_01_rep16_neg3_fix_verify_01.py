# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep16_neg3_fix_verify_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_30 Part3 FAIL是正の検証、≤¥2)
# ============================================================
# 目的: rep16(neg3_hormuz_prodrunner_b1b, sample1)がSTAGE4_ESCALATION
# (stage4_reason=ladder_exhausted_without_full_rewrite)になった根本原因
# (`paired_rewrite`で片側[今回はEN側]のみ対象文が特定できない場合に0 callで
# ⑥disabled経路へ落ちていたこと、本委任でPart3実測により特定)に対する
# 小修正1回(`er052_open233_self_recovery_flow_runner_01.paired_rewrite`へ
# `elif en_located != ja_located:`分岐を追加し、既存`single_text_rewrite`
# へ委譲する)が、実際に失敗していたclaim(fact:HF-003のJA再出現箇所)を
# 解決できるかを、**フルの29 call再実行ではなく**、既存rep16 sample1の
# instance json(`er052_output/open233_self_recovery_flow_runner_01_rep16/
# instances_s1/neg3_hormuz_prodrunner_b1b.json`)から実際に失敗した時点の
# 状態(cycle0 rewrite後のen/ja本文、cycle1で検出された実際のdev)をそのまま
# 再構成し、`paired_rewrite`単体を1回だけ実行して検証する(既存証跡は
# 読み取りのみ、新規APIコストは本検証の1〜2 callのみ)。
#
# 設計制約: Production code・既存iteration/rep証跡は一切変更しない。
# Model Routing Contractは経由しない。API keyは環境変数のみ。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp

OUT_DIR = runner.OUT_DIR  # rep16と同一ディレクトリ(既存instance jsonの横に保存)
INSTANCE_JSON = f"{OUT_DIR}/instances_s1/neg3_hormuz_prodrunner_b1b.json"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ag_30_neg3fix.json"
TOTAL_BUDGET_JPY = 2.0  # 委任文Part3 FAIL是正再実行Guardrail(≤¥2)


def main():
    with open(INSTANCE_JSON, encoding="utf-8") as f:
        inst_json = json.load(f)
    cycle0 = inst_json["cycles"][0]
    cycle1 = inst_json["cycles"][1]
    ja_claim_row = next(sr for sr in cycle1["stage2_results"] if "トランプ" in sr["claim_text"])

    fx = step3cmp.load_negative_fixture(
        "neg3_hormuz_prodrunner_b1b",
        "er019_output/family_x_entertainment_production_runner_01/"
        "an3_t0_wiring_regression_01/hormuz/b1b/audit/deviation_checks/advanced_attempt2.json",
    )
    fixture = {
        "ledger_text": fx["ledger_text"],
        "article_text": cycle0["en_text_after_rewrite"],
        "source_article_text": cycle0["ja_text_after_rewrite"],
    }
    claim_rec = {
        "claim_text": ja_claim_row["claim_text"], "rewrite_kind": ja_claim_row["rewrite_kind"],
        "dev": ja_claim_row["dev"], "materiality": "BLOCKING", "basis": ja_claim_row["basis"],
        "rewrite_hint": ja_claim_row.get("rewrite_hint", "") or "",
        "origin": ja_claim_row.get("origin"),
    }

    client = vfl01.get_client()
    state = runner.load_budget_state() if False else {
        "cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
    consecutive_errors = [0]
    call_log: list = []

    # 独自の小さいbudget guardで上限を守る(runner本体の固定BUDGET_STATE_
    # PATH/TOTAL_BUDGET_JPYは使わず、record_call/save_budget_stateの副作用
    # はこの検証専用stateのみへ閉じる)。
    import os
    from unittest import mock

    def local_save(_s):
        os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
        with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(_s, f, ensure_ascii=False, indent=2)

    def local_check(_s):
        if _s["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
            raise runner.TrialAbort(f"累計¥{_s['cumulative_jpy']:.4f}が本検証Guardrail¥{TOTAL_BUDGET_JPY}に到達")

    with mock.patch.object(runner, "save_budget_state", local_save), \
         mock.patch.object(runner, "check_budget", local_check):
        result = runner.paired_rewrite(
            client, state, consecutive_errors, call_log, "neg3fix_verify", fixture, claim_rec)
    local_save(state)

    summary = {
        "guard_ok": result.get("guard_ok"), "method": result.get("method"),
        "ladder_level_used": result.get("ladder_level_used"),
        "target_not_locatable": result.get("target_not_locatable"),
        "ja_claim_text": claim_rec["claim_text"],
        "en_before": fixture["article_text"], "en_after": result.get("updated_en_text"),
        "ja_before": fixture["source_article_text"], "ja_after": result.get("updated_ja_text"),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
    }
    with open(f"{OUT_DIR}/neg3_fail_fix_verification.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "call_log": call_log}, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
