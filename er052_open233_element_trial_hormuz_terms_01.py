# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_hormuz_terms_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_27 Part2、Hormuz要素Trial A)
# ============================================================
# 目的: ユーザー上位原則「重大誤解原則」(2026-10-01、design書§0)を追加した
# Stage2 body rubric(RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE、
# er052_open233_self_recovery_stage2_calibration_01.py)が、hormuz記事
# (HF-009)の用語一般化・数値丸めに対して許容側/BLOCK側を正しく分けるか、
# かつSafety-critical claim(B3因果・er009 changed_scope[別記事・別領域へ
# 拡張する真にBLOCKINGなscope違反])を誤降格させないかをn=2で実測する。
#
# 重要な設計制約(既存er052系Trialと同一原則):
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - 本委任専用のbudget state(他委任の既存証跡ファイルを汚染しない、
#   TestNoCrossModuleBudgetStateContaminationと同一原則)。
# - claim_textは全て実データ(hormuz_run03_standard実記事本文・neg3実文・
#   B3実fixture・er009 9フラグ実fixture)からの逐語引用、またはそれを
#   最小単位(名詞句のみ)で置換した構成である(捏造Ledger factは無い)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er009_ledger_deviation_recalibration_02_test as er009t
import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_element_trial_hormuz_terms_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ad.json"
TOTAL_BUDGET_JPY = 20.0  # 委任_27 Part2 Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2


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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.4f}が委任_27 Part2 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------
# claim構築(実データのみ、§1-2参照)
# ------------------------------------------------------------
def build_claims() -> tuple:
    """戻り値: (hormuz_fixture, claims)。claimsは各dictに
    group(accept/ng/safety)・sub_id・claim_text・expected(PASS=非
    BLOCKING期待/BLOCK=BLOCKING期待)・related_fact_id・origin・
    fixture(個別claimが参照するarticle_text/ledger_text)を持つ。"""
    hormuz = next(f for f in g6.step3_fixtures() if f["id"] == "hormuz_run03_standard")
    b3 = next(f for f in g6.step2_fixtures() if f["id"] == "B3")

    claims = []

    def add(group, sub_id, claim_text, expected, fixture, related_fact_id, origin="ja_source"):
        local_context, fallback = s2p.build_local_context(fixture["article_text"], claim_text)
        claims.append({
            "group": group, "sub_id": sub_id, "claim_text": claim_text, "expected": expected,
            "related_fact_id": related_fact_id, "origin": origin,
            "local_context": local_context, "fallback_used": fallback,
            "ledger_text": fixture["ledger_text"], "source_article_text": fixture.get("source_article_text"),
        })

    # ---- 許容群(期待PASS=非BLOCKING、§1) ----
    add("accept", "accept-1-oilprices-wholemarket",
        "Oil prices did not fall across the whole market after the plan was withdrawn.",
        "PASS", hormuz, "HF-009")
    add("accept", "accept-2-political-statements",
        "Political statements changed greatly. Oil prices moved briefly, then returned to a high level.",
        "PASS", hormuz, "HF-009")
    add("accept", "accept-3-in-one-line",
        "The fee plan vanished, but oil prices stayed high as tensions around the Strait of "
        "Hormuz continued.",
        "PASS", hormuz, "HF-009")
    add("accept", "accept-4-crude-prices-term",
        "Crude prices briefly lost some of their gains after the plan was withdrawn, then "
        "returned to a high level near their earlier level.",
        "PASS", hormuz, "HF-009")
    add("accept", "accept-5-rounding",
        "At the time of reporting, they were up about 3 percent, about 85 dollars a barrel.",
        "PASS", hormuz, "HF-009")

    # ---- NG対照群(期待BLOCK、§1) ----
    add("ng", "ng-1-gasoline-prices",
        "Gasoline prices did not fall across the whole market after the plan was withdrawn.",
        "BLOCK", hormuz, "HF-009")
    add("ng", "ng-2-world-energy-prices",
        "World energy prices did not fall after the plan was withdrawn, and stayed high across "
        "all energy markets.",
        "BLOCK", hormuz, "HF-009")
    add("ng", "ng-3-all-crude-benchmarks",
        "All crude benchmarks moved the same way after the plan was withdrawn, staying high "
        "across the board.",
        "BLOCK", hormuz, "HF-009")
    add("ng", "ng-4-direction-reversal",
        "Oil prices fell sharply across the whole market after the plan was withdrawn.",
        "BLOCK", hormuz, "HF-009")
    add("ng", "neg3-continued-to-returned",
        "The fee plan left the stage, but the events driving oil prices—and the prices "
        "themselves—quickly returned.",
        "BLOCK", hormuz, "HF-009")

    # ---- Safety対照群(期待BLOCK維持が必須、§1) ----
    # hormuz-HF009(旧Safety-critical、Brent→市場全体scope)は本委任の
    # 上位原則再ラベル(§1、design書§7-0)そのものの対象claimであり、
    # 「BLOCKING維持が必須」という対照には使えない(循環)。代わりに
    # B3(因果、別fact_id)+er009 changed_scope(別記事・別領域への
    # scope拡張、真にBLOCKINGな対照)を使う。
    add("safety", "B3-causality",
        "“Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on "
        "July 14, so the flashy 20% plan left the stage” links the continuing concerns "
        "causally to the plan’s withdrawal.",
        "BLOCK", b3, "HF-007")
    er009_fixture = {"article_text": er009t.FIXTURES["changed_scope"], "ledger_text": er009t.LEDGER_TEXT,
                      "source_article_text": None}
    add("safety", "er009-changed_scope",
        er009t.FIXTURES["changed_scope"],
        "BLOCK", er009_fixture, None, origin=None)

    return hormuz, claims


def run_batch(client, state, consecutive_errors, label, claims, rubric_text) -> dict:
    check_budget(state)
    # 全claimがhormuz(HF-009)+B3(HF-007)+er009(別ledger)の3ledgerに
    # またがるため、Verified Fact Ledger全文は3者を連結して渡す(各claimの
    # related_fact_idで対応するfactのみを参照させる、既存run_stage2_batch_
    # variantのprompt構造どおり)。
    hormuz_ledger = claims[0]["ledger_text"]
    b3_ledger = next(c["ledger_text"] for c in claims if c["sub_id"] == "B3-causality")
    er009_ledger = next(c["ledger_text"] for c in claims if c["sub_id"] == "er009-changed_scope")
    combined_ledger = "\n\n".join([hormuz_ledger, b3_ledger, er009_ledger])

    batch_claims = [{
        "claim_text": c["claim_text"], "origin": c["origin"], "related_fact_id": c["related_fact_id"],
        "local_context": c["local_context"], "section_type": "body",
    } for c in claims]

    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = s2c.run_stage2_batch_variant(
                client, combined_ledger, None, batch_claims, rubric_text, model=s2p.MODEL)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    state["cumulative_calls"] += 1
    if result is not None:
        state["cumulative_jpy"] += result["cost_jpy"]
        state["history"].append({"label": label, "cost_jpy": result["cost_jpy"], "usage": result["usage"]})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")
    if result is None:
        return {"error": last_err}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    parser.add_argument("--rubric", choices=["v1", "v2"], default="v1",
                         help="v1=初回rubric(RUBRIC_..._MISCONCEPTION_PRINCIPLE)、"
                              "v2=委任_27 Part2最小修正後(...MISCONCEPTION_PRINCIPLE_V2)")
    parser.add_argument("--label_prefix", default="hormuz_element_trial_a")
    args = parser.parse_args()

    rubric_text = (s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE if args.rubric == "v1"
                   else s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V2)

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    hormuz, claims = build_claims()

    runs = []
    stopped, stop_reason = False, None
    try:
        for run_idx in range(1, args.n_runs + 1):
            label = f"{args.label_prefix}_run{run_idx}"
            res = run_batch(client, state, consecutive_errors, label, claims, rubric_text)
            save_json(f"{OUT_DIR}/{args.label_prefix}_run_{run_idx}.json", {"label": label, **res})
            runs.append(res)
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    # 集計
    per_claim_rows = []
    for idx, c in enumerate(claims):
        labels = []
        for res in runs:
            if "error" in res:
                continue
            judgments = res["parsed"].get("judgments", [])
            match = next((j for j in judgments if j.get("claim_index") == idx), None)
            if match is not None:
                labels.append({"materiality": match["materiality"], "basis": match.get("basis"),
                               "rewrite_hint": match.get("rewrite_hint")})
        observed_materialities = [lb["materiality"] for lb in labels]
        if c["expected"] == "PASS":
            miscategorized = [m for m in observed_materialities if m == "BLOCKING"]
            false_block = len(miscategorized)
            false_pass = 0
        else:
            false_pass = sum(1 for m in observed_materialities if m != "BLOCKING")
            false_block = 0
        variance = len(set(observed_materialities)) > 1 if observed_materialities else False
        per_claim_rows.append({
            "group": c["group"], "sub_id": c["sub_id"], "claim_text": c["claim_text"],
            "expected": c["expected"], "observed_labels": labels,
            "false_pass_count": false_pass, "false_block_count": false_block,
            "variance_across_runs": variance,
        })

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "n_runs_requested": args.n_runs, "n_runs_completed": len(runs),
        "n_claims": len(claims),
        "accept_group_false_block_total": sum(r["false_block_count"] for r in per_claim_rows
                                               if r["group"] == "accept"),
        "ng_group_false_pass_total": sum(r["false_pass_count"] for r in per_claim_rows if r["group"] == "ng"),
        "safety_group_false_pass_total": sum(r["false_pass_count"] for r in per_claim_rows
                                              if r["group"] == "safety"),
    }
    save_json(f"{OUT_DIR}/summary_{args.label_prefix}.json", {
        "summary": summary, "per_claim_rows": per_claim_rows,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
