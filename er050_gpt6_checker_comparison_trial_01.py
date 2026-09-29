# -*- coding: utf-8 -*-
# ============================================================
# er050_gpt6_checker_comparison_trial_01.py
# GPT6-MODEL-COMPARISON-TRIAL-01 (Phase B, 委任_02)
# ============================================================
# 目的: 現行Ledger Deviation Checker(er003_v1_en_direct_vfl_01_generate.py::
# run_deviation_check)を、Prompt/Developer message/JSON schema/Validator/
# fixtureを完全固定したまま、model引数だけ差し替えて gpt-5.6-luna(現行
# baseline)と gpt-6-luna(主対象)を比較するTrial harness。
#
# 重要な設計制約(委任文より):
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
#   本スクリプトはvfl01をimportして`run_deviation_check()`をそのまま
#   呼び出すのみ(model引数のみ差し替え)。
# - Model Routing Contract(er006_model_routing_contract_01.py)は経由しない
#   (Trial harnessはContract非経由でmodel文字列を直接渡す)。
# - fixtureは既存の実データ(A/B群・Meta・ER-009-N1・Hormuz run_03)を
#   そのまま再利用する。新規fixtureの追加作成はしない。
# - A/B/Meta群のfixtureは、既存audit jsonに保存済みの`prompt`文字列を
#   DEVIATION_PROMPT_TEMPLATE / RELATED_FACT_ID_INSTRUCTION /
#   ORIGIN_INSTRUCTION_TEMPLATE から逆算するテンプレート逆展開方式で
#   verified_ledger_text/article_text/source_article_textを復元する
#   (この逆展開は「新規に作文」ではなく、既存の確定済みprompt文字列から
#   決定論的に元の入力を切り出すだけであり、harness側テストで
#   「復元した入力を再度テンプレートに通すと、保存済みpromptとbyte単位で
#   一致する」ことを検証している)。
#
# 費用Guardrail: 累計参考換算(USD_JPY=160、gpt-5.6-luna単価を「参考」として
# GPT-6側にも同一レートで換算)が--budget-jpyに到達したら、以降の呼び出しを
# 中止する(既に完了した分の結果は保存する)。GPT-6の実単価は未確認のため、
# token数を一次記録として必ず残す。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er009_ledger_deviation_recalibration_02_test as er009t

OUT_DIR = "er050_output/gpt6_checker_comparison_trial_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state.json"

# 参考換算レート(プロジェクト既存慣習、er006_pool_benches_luna_cost_compare.py等と同一値)。
USD_JPY = 160.0
REF_IN, REF_CACHED, REF_OUT = 0.20, 0.02, 1.20  # gpt-5.6-luna単価、$/1M tokens


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------------
# Phase A記録済みsha256(固定性の証明に使う、design書§4引用)
# ------------------------------------------------------------
PHASE_A_SHA256 = {
    "DEVIATION_PROMPT_TEMPLATE": "d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9",
    "DEVIATION_DEVELOPER_MESSAGE": "28d7efc6d289a246ddcf71da118ca175af86dd2001fe1ca4725a5c534c299b2b",
    "DEVIATION_JSON_SCHEMA": "bf6858126fc5888b43d84f06e0c9f6f550415516d2c9ca6ef6269f7229ed407f",
}


def verify_fixed_constants() -> dict:
    """Prompt/Developer message/JSON schemaがPhase A記録と一致するかを検証する。
    不一致ならRuntimeErrorでSTOPする(委任文の「fixtureのsha256を再検証(不一致なら
    STOP)」に対応、Prompt本体側の固定性検証)。"""
    schema_sha = sha256_text(json.dumps(vfl01.DEVIATION_JSON_SCHEMA, sort_keys=True))
    actual = {
        "DEVIATION_PROMPT_TEMPLATE": sha256_text(vfl01.DEVIATION_PROMPT_TEMPLATE),
        "DEVIATION_DEVELOPER_MESSAGE": sha256_text(vfl01.DEVIATION_DEVELOPER_MESSAGE),
        "DEVIATION_JSON_SCHEMA": schema_sha,
    }
    mismatches = {k: (v, PHASE_A_SHA256[k]) for k, v in actual.items() if v != PHASE_A_SHA256[k]}
    if mismatches:
        raise RuntimeError(f"固定性検証NG(Phase A記録と不一致、STOP): {mismatches}")
    return actual


# ------------------------------------------------------------
# audit json の prompt からledger_text/article_text/source_article_textを
# 逆展開する(テンプレート逆展開方式、§本ファイル冒頭コメント参照)
# ------------------------------------------------------------
def extract_inputs_from_prompt(prompt: str):
    tmpl = vfl01.DEVIATION_PROMPT_TEMPLATE
    prefix, rest = tmpl.split("{verified_ledger_text}", 1)
    mid, suffix = rest.split("{article_text}", 1)
    if not prompt.startswith(prefix):
        raise ValueError("prompt prefix mismatch(テンプレート逆展開失敗)")
    after_prefix = prompt[len(prefix):]
    idx_mid = after_prefix.index(mid)
    ledger_text = after_prefix[:idx_mid]
    after_mid = after_prefix[idx_mid + len(mid):]
    idx_suffix = after_mid.index(suffix)
    article_text = after_mid[:idx_suffix]
    remainder = after_mid[idx_suffix + len(suffix):]

    include_related_fact_id = "関連Fact ID" in remainder
    source_article_text = None
    if "逸脱の発生源" in remainder:
        origin_prefix, _ = vfl01.ORIGIN_INSTRUCTION_TEMPLATE.split("{source_article_text}", 1)
        idx_o = remainder.index(origin_prefix)
        after_o = remainder[idx_o + len(origin_prefix):]
        source_article_text = after_o
    return {
        "ledger_text": ledger_text,
        "article_text": article_text,
        "source_article_text": source_article_text,
        "include_related_fact_id": include_related_fact_id,
    }


def verify_reconstruction(prompt: str, extracted: dict) -> bool:
    """逆展開結果を再度テンプレートへ通し、保存済みpromptとbyte単位一致するか検証する。"""
    recon = vfl01.DEVIATION_PROMPT_TEMPLATE.format(
        verified_ledger_text=extracted["ledger_text"], article_text=extracted["article_text"]
    )
    if extracted["include_related_fact_id"]:
        recon += vfl01.RELATED_FACT_ID_INSTRUCTION
    if extracted["source_article_text"] is not None:
        recon += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=extracted["source_article_text"])
    return recon == prompt


def load_audit_fixture(fixture_id: str, path: str, gold_note: str) -> dict:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    prompt = d["prompt"]
    extracted = extract_inputs_from_prompt(prompt)
    if not verify_reconstruction(prompt, extracted):
        raise RuntimeError(f"fixture {fixture_id}: prompt再構成が保存済みpromptと不一致(STOP)")
    return {
        "id": fixture_id,
        "source_path": path,
        "source_sha256": sha256_file(path),
        "ledger_text": extracted["ledger_text"],
        "article_text": extracted["article_text"],
        "source_article_text": extracted["source_article_text"],
        "include_related_fact_id": extracted["include_related_fact_id"],
        "hook_aware": bool(d.get("hook_aware", False)),
        "gold_note": gold_note,
        "baseline_parsed": d.get("parsed"),
    }


# ------------------------------------------------------------
# Step1: 重大fixture群(ER-009-N1 9種 + A2/A3 + A4 + A5)
# ------------------------------------------------------------
def er009_fixtures() -> list:
    out = []
    for name, article_text in er009t.FIXTURES.items():
        out.append({
            "id": f"er009_{name}",
            "source_path": "er009_ledger_deviation_recalibration_02_test.py:FIXTURES",
            "source_sha256": None,
            "ledger_text": er009t.LEDGER_TEXT,
            "article_text": article_text,
            "source_article_text": None,
            "include_related_fact_id": False,
            "hook_aware": False,
            "gold_note": f"expected MAJOR with flag {name}=true",
            "expected_flag": name,
            "baseline_parsed": None,
        })
    return out


def step1_fixtures() -> list:
    fx = er009_fixtures()
    fx.append(load_audit_fixture(
        "A2A3",
        "er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_advanced/A3_deviation.json",
        "gold=LEDGER_DEVIATION(MAJORx3、origin=ja_source中心)。A2/A3は同一fileの1回実行"
        "(design書ではA2/A3の2項目表記だが実体は1 article/1 runのため本harnessでは"
        "1 fixtureとして扱う)。",
    ))
    fx.append(load_audit_fixture(
        "A4",
        "er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN2-T1_deviation.json",
        "gold=LEDGER_DEVIATION(MAJORx1、origin=translation、changed_scope)",
    ))
    # A5: design書記載パス(must_fix_retry_result.json)はretry後COMPLIANT結果であり
    # 再現可能なfixture inputを含まない(prompt keyなし)。本来のMAJOR検出は同一run内の
    # 事前段階ファイルer045_output/.../meta/deviation_check_trial.json(retry適用前、
    # fact_id=MUSE-HC-012、changed_fact=true、origin=translation)に記録されている
    # ため、こちらを実際のA5 fixture inputとして使う(design書のA-1と同種の
    # 「retry後ファイルは再現不可」という注記を踏襲した代替、fixtureの新規作成では
    # なく既存実データの中から再現可能な原本を採用しただけ)。
    fx.append(load_audit_fixture(
        "A5",
        "er045_output/family_x_no_heading_segmentation_trial_01/meta/deviation_check_trial.json",
        "gold=LEDGER_DEVIATION(MAJORx1、changed_fact、related_fact_id=MUSE-HC-012、"
        "'put back the feature'のrollback反転。design書記載パスmust_fix_retry_result.json"
        "はretry後COMPLIANT結果のため代替不可、本ファイルが検出時点の原本)",
    ))
    return fx


A1_NOTE = (
    "design書A-1(er019_output/family_x_b3_production_wiring_01/run_01/audit/"
    "fact_fidelity_fix_01_recheck_summary.json)は是正後recheckの結果(b1b/a2とも"
    "LEDGER_COMPLIANT)のみを保存しており、promptキーを持たずChecker再実行用の"
    "入力(検出漏れ発生時の元記事本文)を含まない。design書自身が「検出漏れ自体を"
    "再現したfixtureではない」と明記済みのため、本harnessではA-1を実行対象に含めず、"
    "既知の時制drift見逃し事例として参考記録のみ残す(新規fixtureの捏造はしない)。"
)


# ------------------------------------------------------------
# Step2: 境界・過剰品質群(B1-B4 + Meta run_03 Standard)
# ------------------------------------------------------------
def step2_fixtures() -> list:
    return [
        load_audit_fixture(
            "B1",
            "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/"
            "deviation_checks/ja_original_attempt1.json",
            "gold=LEDGER_DEVIATION(MAJORx1、origin無し[JA側]、changed_scope+unsupported_new_claim)",
        ),
        load_audit_fixture(
            "B2_hormuz",
            "er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/"
            "advanced_attempt1.json",
            "gold=LEDGER_DEVIATION(MAJORx1、origin=ja_source、changed_causality)",
        ),
        load_audit_fixture(
            "B3",
            "er037_output/family_xy_concreteness_control_trial_01/hormuz/task_b_cleanup/"
            "B1_deviation.json",
            "gold=LEDGER_DEVIATION(MAJORx1、origin=ja_source、changed_causality)",
        ),
        load_audit_fixture(
            "B4",
            "er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/"
            "advanced_attempt1.json",
            "gold=LEDGER_DEVIATION(MAJORx4、origin=ja_sourcex3+translationx1)",
        ),
        load_audit_fixture(
            "Meta_run03_standard",
            "er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/"
            "standard_attempt1.json",
            "gold=LEDGER_DEVIATION(MAJORx1、origin=translation、changed_fact+changed_certainty、"
            "related_fact_id=MUSE-HC-010)",
        ),
    ]


# ------------------------------------------------------------
# Step3: 非決定性群(Hormuz run_03、JA original/JA r2/Advanced/Standard)
# ------------------------------------------------------------
def step3_fixtures() -> list:
    return [
        load_audit_fixture(
            "hormuz_run03_ja_original",
            "er019_output/family_x_refresh_e2e_01/hormuz/run_03/ja_writer/audit/deviation_checks/"
            "ja_original_attempt1.json",
            "非決定性測定対象(JA original)",
        ),
        load_audit_fixture(
            "hormuz_run03_ja_r2",
            "er019_output/family_x_refresh_e2e_01/hormuz/run_03/ja_writer/audit/deviation_checks/"
            "ja_r2_attempt1.json",
            "非決定性測定対象(JA r2)",
        ),
        load_audit_fixture(
            "hormuz_run03_advanced",
            "er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/audit/deviation_checks/"
            "advanced_attempt1.json",
            "非決定性測定対象(Advanced、現行判定=LEDGER_COMPLIANT)。Advanced/Standard判定割れケース"
            "(design書§3-6)の片側",
        ),
        load_audit_fixture(
            "hormuz_run03_standard",
            "er019_output/family_x_refresh_e2e_01/hormuz/run_03/a2/audit/deviation_checks/"
            "standard_attempt1.json",
            "非決定性測定対象(Standard、現行判定=MAJORx1、related_fact_id=HF-009、changed_scope)。"
            "Advanced/Standard判定割れケース(design書§3-6)のもう片側",
        ),
    ]


# ------------------------------------------------------------
# 限定実行モード(委任_03): --fixture <id[,id2,...]> で特定fixtureのみに
# 絞り込む。step1/2の通常フル実行(既存run_1.json等)を上書きしないよう、
# main()側でstep_name(保存先ディレクトリ)をfixture絞り込み時のみ
# 別名(例: step1_er009_changed_actor_n5)へ変更する。
# ------------------------------------------------------------
def filter_fixtures_by_id(fixtures: list, fixture_ids_csv: str) -> list:
    want = [x.strip() for x in fixture_ids_csv.split(",") if x.strip()]
    by_id = {f["id"]: f for f in fixtures}
    missing = [w for w in want if w not in by_id]
    if missing:
        raise ValueError(f"指定fixture idが見つかりません: {missing}(存在するid: {sorted(by_id.keys())})")
    return [by_id[w] for w in want]


# ------------------------------------------------------------
# 費用Guardrail
# ------------------------------------------------------------
class BudgetExceeded(RuntimeError):
    pass


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_ref_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def usage_ref_cost_jpy(usage: dict) -> float:
    it = usage.get("input_tokens") or 0
    ct = usage.get("cached_input_tokens") or 0
    ot = usage.get("output_tokens") or 0
    billable_in = max(it - ct, 0)
    cost_usd = billable_in / 1e6 * REF_IN + ct / 1e6 * REF_CACHED + ot / 1e6 * REF_OUT
    return cost_usd * USD_JPY


# ------------------------------------------------------------
# 実行
# ------------------------------------------------------------
def run_fixture_once(client, fixture: dict, model: str) -> dict:
    kwargs = {"model": model, "hook_aware": fixture.get("hook_aware", False)}
    if fixture.get("include_related_fact_id"):
        kwargs["include_related_fact_id"] = True
    if fixture.get("source_article_text") is not None:
        kwargs["source_article_text"] = fixture["source_article_text"]
    result = vfl01.run_deviation_check(client, fixture["ledger_text"], fixture["article_text"], **kwargs)
    return result


def save_run(step: str, fixture_id: str, model: str, attempt: int, result: dict, error: str | None) -> str:
    d = f"{OUT_DIR}/{step}/{fixture_id}/{model}"
    os.makedirs(d, exist_ok=True)
    path = f"{d}/run_{attempt}.json"
    payload = {
        "fixture_id": fixture_id,
        "model": model,
        "attempt": attempt,
        "error": error,
    }
    if result is not None:
        payload.update({
            "prompt_sha256": sha256_text(result["prompt"]),
            "model_returned": result["model"],
            "response_id": result["response_id"],
            "usage": result["usage"],
            "elapsed_seconds": result["elapsed_seconds"],
            "raw_parsed": result["raw_parsed"],
            "parsed": result["parsed"],
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def execute_step(step_name: str, fixtures: list, models: list, budget_jpy: float, repeat: int = 1,
                  error_rate_stop: float = 0.20) -> dict:
    state = load_budget_state()
    summary = {"step": step_name, "models": models, "repeat": repeat, "fixtures": [], "stopped": False,
               "stop_reason": None}
    for fixture in fixtures:
        fx_summary = {"id": fixture["id"], "gold_note": fixture["gold_note"], "runs": {}}
        for model in models:
            fx_summary["runs"][model] = []
            for attempt in range(1, repeat + 1):
                if state["cumulative_ref_jpy"] >= budget_jpy:
                    summary["stopped"] = True
                    summary["stop_reason"] = (
                        f"累計参考換算¥{state['cumulative_ref_jpy']:.2f}が上限¥{budget_jpy}に到達"
                    )
                    fx_summary["runs"][model].append({"skipped": True, "reason": summary["stop_reason"]})
                    continue
                if state["cumulative_calls"] >= 5:
                    err_rate = state["cumulative_errors"] / state["cumulative_calls"]
                    if err_rate > error_rate_stop:
                        summary["stopped"] = True
                        summary["stop_reason"] = f"error率{err_rate:.1%}が{error_rate_stop:.0%}超過"
                        fx_summary["runs"][model].append({"skipped": True, "reason": summary["stop_reason"]})
                        continue
                try:
                    result = run_fixture_once(vfl01.get_client(), fixture, model)
                    ref_cost = usage_ref_cost_jpy(result["usage"])
                    state["cumulative_ref_jpy"] += ref_cost
                    state["cumulative_calls"] += 1
                    state["history"].append({
                        "step": step_name, "fixture": fixture["id"], "model": model, "attempt": attempt,
                        "usage": result["usage"], "ref_cost_jpy": round(ref_cost, 4),
                        "elapsed_seconds": result["elapsed_seconds"],
                    })
                    save_run(step_name, fixture["id"], model, attempt, result, None)
                    fx_summary["runs"][model].append({
                        "overall_status": result["parsed"]["overall_status"],
                        "deviations": result["parsed"]["deviations"],
                        "usage": result["usage"],
                        "ref_cost_jpy": round(ref_cost, 4),
                        "elapsed_seconds": result["elapsed_seconds"],
                    })
                except Exception as e:  # noqa: BLE001
                    state["cumulative_calls"] += 1
                    state["cumulative_errors"] += 1
                    save_run(step_name, fixture["id"], model, attempt, None, str(e))
                    fx_summary["runs"][model].append({"error": str(e)})
                save_budget_state(state)
        summary["fixtures"].append(fx_summary)
    summary["cumulative_ref_jpy"] = round(state["cumulative_ref_jpy"], 4)
    summary["cumulative_calls"] = state["cumulative_calls"]
    summary["cumulative_errors"] = state["cumulative_errors"]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/summary_{step_name}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", required=True, choices=["1", "2", "3"])
    parser.add_argument("--models", required=True, help="comma-separated model ids")
    parser.add_argument("--budget-jpy", type=float, default=300.0)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument(
        "--fixture", default=None,
        help="comma-separated fixture id(s) to run in isolation (e.g. er009_changed_actor). "
             "When given, output is saved under a distinct step-name directory "
             "(step{N}_{fixture_ids}_n{repeat}) so it never overwrites prior full-step results.",
    )
    args = parser.parse_args()

    verify_fixed_constants()
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    if args.step == "1":
        fixtures = step1_fixtures()
        default_repeat = 1
    elif args.step == "2":
        fixtures = step2_fixtures()
        default_repeat = 1
    else:
        fixtures = step3_fixtures()
        default_repeat = args.repeat

    step_name = f"step{args.step}"
    repeat = default_repeat
    if args.fixture:
        fixtures = filter_fixtures_by_id(fixtures, args.fixture)
        slug = "_".join(f["id"] for f in fixtures)
        step_name = f"step{args.step}_{slug}_n{args.repeat}"
        repeat = args.repeat

    summary = execute_step(step_name, fixtures, models, args.budget_jpy, repeat=repeat)

    print(json.dumps({
        "step": summary["step"], "stopped": summary["stopped"], "stop_reason": summary["stop_reason"],
        "cumulative_ref_jpy": summary["cumulative_ref_jpy"], "cumulative_calls": summary["cumulative_calls"],
        "cumulative_errors": summary["cumulative_errors"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
