# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ⑥、委任_09)
# ============================================================
# 目的: design_open233_self_recovery_flow_01.md §3〜§8で確定したStage 1→2→3
# →Recheckの一連のSelf-Recovery Flowを、既存の個別実測モジュール
# (er052_open233_self_recovery_{precheck,stage2_production,stage2_calibration,
# stage3_rewrite_trial}_01.py)をimportして1本のTrial runnerへ統合し、
# 代表fixture群に対して通しで実行する(統合dry-run、委任_09)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則、本ファイルも遵守):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない
#   (本ファイルはer010.rewrite_ng_item/generate_rewriteを直接呼ばず、
#   §5-2-補2確定案どおりE-2[最小1-shot Prompt]のみを使う独立実装のため、
#   er010に対するmonkeypatchも行わない)。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
#   保存jsonにはprompt本体ではなくsha256のみ記録。
# - **[委任_09で実際に検出・修正した実装上の注意]** 既存Trialモジュール
#   (`er052_open233_self_recovery_stage3_rewrite_trial_01.py`='s3rt')の
#   `simple_llm_call`は、そのモジュール自身の`record_call`/
#   `save_budget_state`(`s3rt.BUDGET_STATE_PATH`=既存委任_08の証跡
#   ファイル)を内部で呼ぶため、そのまま流用すると**他委任の既存証跡
#   ファイルを上書き汚染する**(本委任の実行中に実際に発生、
#   `git checkout`で復元済み)。本ファイルは`s3rt`のPrompt定数
#   (`J1_DEVELOPER_MSG`)とpure関数(`extract_json_obj`)のみを読み取り
#   専用で借用し、API呼び出し・budget記録は本ファイル自身の
#   `simple_llm_call`(下記)で完結させる。
# - 真のProduction JA Fact Check(er002系)・JA Writer O cascade(er019)は
#   呼び出さない。V4A variant checker(er051)をJA/EN両方の文面に適用する
#   近似で代用する(委任_08と同一のスコープ限界、§5-4-補2に既述)。
#
# 本ファイル固有の設計判断(委任_09、Trial限定・報告のみ・独断でrubric等を
# 変更しない):
# 1. Stage 1は「既存fixtureに同一入力のV4A出力が既に存在する場合は再利用
#    (0 call)、無ければ新規実行」(委任文どおり)。fixture一覧・reuse元
#    パスはbuild_target_instances()に列挙する(全て既存artifact/実データ
#    由来、新規fixtureの捏造はしない)。
# 2. Stage 3のRewrite機構は、claimのorigin文字列だけでなく「fixtureが
#    JA/EN双方の本文(article_text+source_article_text)を実際に持つか」
#    も条件に加えて選択する(paired local rewrite[J-1]はJA/EN双方の本文が
#    ある場合のみ意味を持つため)。JA/EN pairingが無いfixture(例: B1=JA
#    Original単体チェック)は、claimが検出された「その言語のテキスト単体」
#    への局所編集+同一言語でのRecheckとする(委任_08のdelete型実測[B1-c
#    はJA本文への直接削除+JA Recheck]と同一方式の一般化)。
# 3. replace_with_ledger_value型・narrow_scope型(単一言語)は、委任_08で
#    確定した第一候補E-2(最小1-shot Prompt)一本化とする(E-1
#    escalationはn=2実測で一度も発火しておらず[§5-4-補2]、E-1固有の
#    per-claim機械検証[verify_fn]は個別fixtureごとの正解文字列を要求する
#    ため、任意fixtureを横断する本汎用runnerでは実装しない。最終的な
#    正否は全文Recheck[fail-closed]が担保する、既存設計の権限分担どおり)。
# 4. guard抵触時の段階的フォールバック(§5-2/§5-4)は、本runnerでは
#    「対象文局所編集の1回再試行」までを実装し、その次段階(旧案B/
#    既存全文must-fix retryへのフォールバック)は「全文に対する最小編集
#    指示(対象文以外は変えないという指示付きの全文Rewrite、J-2/旧案Bの
#    近似)」として言語を問わず統一実装する(委任_08のJ-2実装[JA]の
#    考え方をEN/JA共通の汎用フォールバックへ一般化したもの、既知の限界
#    として報告する)。
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp
import er052_open233_self_recovery_precheck_01 as precheck
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p
import er052_open233_self_recovery_stage3_rewrite_trial_01 as s3rt

OUT_DIR = "er052_output/open233_self_recovery_flow_runner_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233m.json"
TOTAL_BUDGET_JPY = 45.0  # 委任_09 Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
MODEL = "gpt-6-luna"
MAX_CYCLES = 2

FLOOR_FLAGS = [
    "changed_actor", "changed_number", "changed_negation",
    "changed_comparison", "changed_time", "changed_certainty",
]


class TrialAbort(RuntimeError):
    pass


# ------------------------------------------------------------
# budget state(既存er052系と同一パターン)
# ------------------------------------------------------------
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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_09 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def record_call(state: dict, consecutive_errors: list, label: str, cost_jpy: float, ok: bool,
                 recovery_stage: str, usage: dict | None = None) -> None:
    state["cumulative_calls"] += 1
    if ok:
        state["cumulative_jpy"] += cost_jpy
        state["history"].append({"label": label, "cost_jpy": cost_jpy, "recovery_stage": recovery_stage,
                                  "usage": usage})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")


def simple_llm_call(client, state, consecutive_errors, call_log, label, developer_msg, prompt,
                     model: str = MODEL) -> str | None:
    """`s3rt.simple_llm_call`と同一の単純1-shot呼び出しロジックだが、本runner
    自身の`check_budget`/`record_call`/`save_budget_state`(本ファイル冒頭
    定義、budget_state_c233m.json)のみを使う独立実装(委任_09で実装)。
    **重要な修正**: 当初実装は`s3rt.simple_llm_call`をそのまま呼んでいたが、
    `s3rt.simple_llm_call`内部の`record_call`は`s3rt`モジュール自身の
    `save_budget_state`(`s3rt.BUDGET_STATE_PATH`=既存委任_08の
    `er052_output/open233_self_recovery_stage3_rewrite_trial_01/
    budget_state_c233l_b.json`)へ書き込むため、本runner実行のたびに
    **既存committment_08の証跡ファイルを上書き汚染する**実害があった
    (本委任の実行中に実際に発生・検出し、`git checkout`で復元済み。
    詳細はdelegation_log/RESULT_PACKET参照)。加えて`s3rt.check_budget`は
    `s3rt.TOTAL_BUDGET_JPY`(¥30、本runnerのGuardrail¥45とは別値)を
    参照するため、Guardrail判定も本runner側の意図と一致しない別軸だった
    (今回は¥30に達する前に完走したため実害は生じなかったが、潜在的な
    二重基準リスクだった)。本関数はこの2点を解消する。"""
    check_budget(state)
    last_err = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            t0 = time.time()
            response = client.responses.create(
                model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
                input=[{"role": "developer", "content": developer_msg}, {"role": "user", "content": prompt}],
            )
            elapsed = round(time.time() - t0, 3)
            usage = s2p._extract_usage(response)
            cost = round(s2p.official_cost_jpy(usage), 4)
            call_log.append({"label": label, "recovery_stage": "stage3_rewrite", "cost_jpy": cost,
                              "usage": usage, "elapsed_seconds": elapsed,
                              "prompt_sha256": s2p.sha256_text(prompt)})
            record_call(state, consecutive_errors, label, cost, True, "stage3_rewrite", usage)
            return response.output_text.strip()
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    call_log.append({"label": label, "recovery_stage": "stage3_rewrite", "error": last_err})
    record_call(state, consecutive_errors, label, 0.0, False, "stage3_rewrite")
    return None


# ------------------------------------------------------------
# claim identity(同一claim/fact_id再発検出、§3-3/§5-3/§6-1 A5/A7)
# ------------------------------------------------------------
def claim_identity(dev: dict) -> str:
    fact_id = (dev.get("related_fact_id") or "").strip()
    if fact_id:
        return f"fact:{fact_id}"
    claim = (dev.get("claim_in_article") or "").strip()
    return "claim:" + hashlib.sha256(claim.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------
# Stage 1: 既存出力の再利用 or 新規V4A実行(routing述語=overall_status、§3-1)
# ------------------------------------------------------------
def stage1_reuse(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d["parsed"] if "parsed" in d else d


def stage1_fresh(client, state, consecutive_errors, call_log, label, fixture) -> dict:
    check_budget(state)
    last_err = None
    result = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, fixture["ledger_text"], fixture["article_text"], MODEL, "V4A",
                include_related_fact_id=True, source_article_text=fixture.get("source_article_text"),
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if result is not None:
        cost = round(s2p.official_cost_jpy(result["usage"]), 4)
        call_log.append({"label": label, "recovery_stage": "stage1_initial", "cost_jpy": cost,
                          "usage": result["usage"], "elapsed_seconds": elapsed,
                          "prompt_sha256": s2p.sha256_text(result["prompt"])})
        record_call(state, consecutive_errors, label, cost, True, "stage1_initial", result["usage"])
        return result["parsed"]
    call_log.append({"label": label, "recovery_stage": "stage1_initial", "error": last_err})
    record_call(state, consecutive_errors, label, 0.0, False, "stage1_initial")
    # fail-closedとしてBLOCKING-candidate扱い(§6-1 A7)。deviationsは空だが
    # overall_statusをLEDGER_DEVIATIONにしてルーティングだけ強制する。
    return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}


# ------------------------------------------------------------
# Stage 1 Recheck(prior_issuesあり、A1)。trial variant(V4A)+
# vfl01.build_prior_issues_instruction()を組み合わせた本runner専用関数
# (er051側は変更しない、read-onlyで部品を借用するだけ)。
# ------------------------------------------------------------
def build_recheck_schema(include_related_fact_id: bool, include_origin: bool) -> dict:
    item_schema = trial.build_trial_deviation_item_schema(include_related_fact_id, include_origin)
    props = {"deviations": {"type": "array", "items": item_schema},
              "prior_issues_resolved": {"type": "array", "items": vfl01.PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA}}
    required = ["deviations", "prior_issues_resolved"]
    return {
        "name": "open233_self_recovery_recheck_v4a_prior",
        "schema": {"type": "object", "properties": props, "required": required, "additionalProperties": False},
        "strict": True,
    }


def run_recheck(client, state, consecutive_errors, call_log, label, fixture, article_text: str,
                 prior_issues: list) -> dict:
    check_budget(state)
    prompt_template = trial.build_trial_prompt_template("V4A")
    prompt = prompt_template.format(verified_ledger_text=fixture["ledger_text"], article_text=article_text)
    prompt += vfl01.RELATED_FACT_ID_INSTRUCTION
    include_origin = fixture.get("source_article_text") is not None
    if include_origin:
        prompt += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fixture["source_article_text"])
    prompt += vfl01.build_prior_issues_instruction(prior_issues)
    schema = build_recheck_schema(True, include_origin)

    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **schema}},
                input=[{"role": "developer", "content": vfl01.DEVIATION_DEVELOPER_MESSAGE},
                       {"role": "user", "content": prompt}],
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "stage1_recheck", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage1_recheck")
        # fail-closed: API失敗はBLOCKING-candidate扱い(§6-1 A7)
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "all_prior_issues_resolved": False,
                "_recheck_api_failure": True}

    raw_parsed = json.loads(response.output_text)
    parsed = vfl01._apply_deviation_post_hoc_validation(raw_parsed)
    parsed_trial = trial.classify_parsed_result_trial(parsed, "V4A")
    resolved = raw_parsed.get("prior_issues_resolved", [])
    parsed_trial["prior_issues_resolved"] = resolved
    parsed_trial["all_prior_issues_resolved"] = (
        len(resolved) == len(prior_issues) and all(bool(r.get("resolved")) for r in resolved)
    )
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "stage1_recheck", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      "overall_status": parsed_trial["overall_status"],
                      "all_prior_issues_resolved": parsed_trial["all_prior_issues_resolved"]})
    record_call(state, consecutive_errors, label, cost, True, "stage1_recheck", usage)
    return parsed_trial


# ------------------------------------------------------------
# Stage 2: R2 rubric、instance単位batch(§4-8/A9)、floor適用
# ------------------------------------------------------------
def apply_floor(materiality: str, dev: dict, detected_by: str) -> tuple:
    if detected_by == "precheck":
        return "BLOCKING", "precheck_floor"
    triggered = [k for k in FLOOR_FLAGS if bool(dev.get(k))]
    if triggered:
        return "BLOCKING", "deterministic_floor:" + ",".join(triggered)
    return materiality, None


def run_stage2(client, state, consecutive_errors, call_log, label, fixture, claims: list) -> list:
    """claims: list of dict(claim_text, origin, related_fact_id, dev[元deviation])。
    戻り値: 各claimにmateriality/basis/rewrite_kind/floor_appliedを付与したlist。"""
    check_budget(state)
    claim_records = []
    for c in claims:
        local_context, fallback = s2p.build_local_context(fixture["article_text"], c["claim_text"])
        claim_records.append({**c, "local_context": local_context, "fallback_used": fallback})
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = s2c.run_stage2_batch_variant(
                client, fixture["ledger_text"], fixture.get("source_article_text"),
                claim_records, s2c.RUBRIC_R2, model=MODEL,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    if result is None:
        call_log.append({"label": label, "recovery_stage": "stage2_second_judge", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage2_second_judge")
        # 判断不能はfail-closedでBLOCKING確定(§6-1)
        out = []
        for c in claim_records:
            out.append({**c, "materiality": "BLOCKING", "basis": "none", "rewrite_kind": "replace_with_ledger_value",
                        "floor_reason": "stage2_api_failure_failclosed"})
        return out
    call_log.append({"label": label, "recovery_stage": "stage2_second_judge", "cost_jpy": result["cost_jpy"],
                      "usage": result["usage"], "elapsed_seconds": result["elapsed_seconds"],
                      "prompt_sha256": result["prompt_sha256"]})
    record_call(state, consecutive_errors, label, result["cost_jpy"], True, "stage2_second_judge", result["usage"])
    judgments = result["parsed"].get("judgments", [])
    out = []
    for i, c in enumerate(claim_records):
        match = next((j for j in judgments if j.get("claim_index") == i), None)
        if match is None:
            materiality, basis, rewrite_kind = "BLOCKING", "none", "replace_with_ledger_value"
            floor_reason = "schema_index_mismatch_failclosed"
        else:
            materiality, basis, rewrite_kind = match["materiality"], match["basis"], match["rewrite_kind"]
            floor_reason = None
        final_materiality, floor_applied = apply_floor(materiality, c["dev"], c.get("detected_by", "stage1_llm"))
        if floor_applied:
            floor_reason = floor_applied
        out.append({**c, "materiality": final_materiality, "llm_materiality": materiality, "basis": basis,
                    "rewrite_kind": rewrite_kind if rewrite_kind != "none" else "replace_with_ledger_value",
                    "floor_reason": floor_reason})
    return out


# ------------------------------------------------------------
# Stage 3: Rewrite dispatch
# ------------------------------------------------------------
def locate_best_sentence(claim_text: str, full_text: str) -> tuple:
    """exact substring優先、無ければSequenceMatcher近傍探索(JA/EN共通の
    簡易汎用実装。専用の日本語文分割モジュールは実装しない、既知の限界
    として§5-4-補2と同一の位置づけ)。"""
    if claim_text and claim_text.strip() in full_text:
        return claim_text.strip(), "exact_substring"
    sentences = re.split(r"(?<=[。.!?])", full_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    best, best_ratio = None, 0.0
    for s in sentences:
        ratio = difflib.SequenceMatcher(None, claim_text, s).ratio()
        if ratio > best_ratio:
            best, best_ratio = s, ratio
    # 文字単位SequenceMatcherは短い文同士だと偶然の一致でも比率が高くなり
    # やすいため(語単位jaccardより緩い)、閾値0.5(実測値: 言い換え一致
    # 0.92、無関係文0.41)をfail-closed側の下限として採用する。
    if best is not None and best_ratio >= 0.5:
        return best, f"sequence_matcher(ratio={round(best_ratio, 2)})"
    return None, "not_found"


E2_GENERIC_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the smallest "
    "possible edit (single-shot, no escalation). You may be given Japanese or English text."
)
E2_GENERIC_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Sentence flagged as a Ledger deviation]
{target_sentence}

[Checker's issue]
{issue}

[Rewrite hint]
{rewrite_hint}

Rewrite ONLY this sentence to resolve the issue (delete the unsupported part, replace it with what the \
Ledger actually supports, or narrow its scope to match the Ledger, per the rewrite hint above). Keep the \
same language as the input sentence. Return ONLY the revised sentence, nothing else. If the issue is \
best resolved by deleting the sentence entirely, return an empty string."""

FULL_TEXT_FALLBACK_DEVELOPER_MSG = (
    "You are the article writer. You must revise the full article text to fix ONE flagged sentence, "
    "while keeping every other sentence character-for-character identical. The text may be Japanese or "
    "English."
)
FULL_TEXT_FALLBACK_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Full article text]
{full_text}

[Sentence to fix]
{target_sentence}

[Checker's issue / rewrite_hint]
{issue}
{rewrite_hint}

Rewrite ONLY the sentence above (per the rewrite_hint). Do NOT change any other sentence in the article, \
not even punctuation or spacing. Return the FULL revised article text, nothing else (no explanation, no \
code fences)."""

J1_GENERIC_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[JA target sentence]
{ja_target}

[EN target sentence (translation of the same claim)]
{en_target}

[rewrite_hint]
{rewrite_hint}

Revise ONLY the JA target sentence and ONLY the EN target sentence (paired, minimal, local edit; do not \
touch anything else). Return strict JSON: {{"ja_revised": "...", "en_revised": "..."}}"""


def single_text_rewrite(client, state, consecutive_errors, call_log, label_prefix, fixture, target_text_field,
                         claim_rec: dict) -> dict:
    """claim_rec['dev']の言語テキスト(target_text_field='article_text'固定、
    JA単体fixtureもarticle_text側にJA本文が入っている、g6.load_audit_fixture
    の仕様どおり)に対する単一言語local rewrite。delete型はまず決定論的削除を
    試し、それ以外(replace_with_ledger_value/narrow_scope)はE-2汎用Promptを
    使う。guard抵触(対象文が特定できない/置換後も同じ問題文言が残る)時は
    1回だけ全文最小編集フォールバックを試す。"""
    full_text = fixture[target_text_field]
    claim_text = claim_rec["claim_text"]
    rewrite_kind = claim_rec["rewrite_kind"]
    dev = claim_rec["dev"]
    issue = dev.get("issue") or dev.get("explanation") or claim_text
    rewrite_hint = f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}"

    target_sentence, locate_method = locate_best_sentence(claim_text, full_text)
    method_used = None
    updated_text = full_text
    found = target_sentence is not None

    if rewrite_kind == "delete":
        if found:
            updated_text = full_text.replace(target_sentence, "", 1)
            method_used = f"deterministic_delete({locate_method})"
        else:
            method_used = "delete_target_not_found"
    else:
        if found:
            prompt = E2_GENERIC_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], target_sentence=target_sentence,
                issue=issue, rewrite_hint=rewrite_hint,
            )
            revised = simple_llm_call(client, state, consecutive_errors, call_log,
                                            f"{label_prefix}_e2_rewrite", E2_GENERIC_DEVELOPER_MSG, prompt,
                                            model=MODEL)
            if revised is not None:
                updated_text = full_text.replace(target_sentence, revised, 1)
                method_used = f"e2_generic_rewrite({locate_method})"
            else:
                method_used = "e2_generic_rewrite_api_failure"
        else:
            method_used = "target_not_found"

    guard_ok = updated_text != full_text and claim_text.strip() not in updated_text if found else False
    if not guard_ok:
        # guard抵触(見つからない、または置換後も同じclaim文言が残存) ->
        # 全文最小編集フォールバック(§5-2/§5-4のフォールバック段2に相当)
        prompt = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], full_text=full_text,
            target_sentence=target_sentence or claim_text, issue=issue, rewrite_hint=rewrite_hint,
        )
        fallback_text = simple_llm_call(client, state, consecutive_errors, call_log,
                                              f"{label_prefix}_fulltext_fallback",
                                              FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt, model=MODEL)
        if fallback_text:
            updated_text = fallback_text
            method_used = (method_used or "") + "+fulltext_fallback"
            guard_ok = updated_text != full_text
        else:
            method_used = (method_used or "") + "+fulltext_fallback_api_failure"

    return {"updated_text": updated_text, "method": method_used, "guard_ok": guard_ok,
            "target_sentence": target_sentence, "locate_method": locate_method}


def paired_rewrite(client, state, consecutive_errors, call_log, label_prefix, fixture, claim_rec: dict) -> dict:
    """JA/EN pairing(article_text=EN, source_article_text=JA)がある場合の
    paired local rewrite(J-1一般化)。JA側は言及先が特定できない場合が
    多いため、claim_textはEN側(article_text)から検出したものを使い、対応する
    JA文はsource_article_text側で同一claim_text/related_fact_idに近い文を
    best-effortで探す(専用の対訳アラインメントは実装しない、既知の限界)。"""
    en_full = fixture["article_text"]
    ja_full = fixture["source_article_text"]
    claim_text = claim_rec["claim_text"]
    dev = claim_rec["dev"]
    rewrite_hint = f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}, " \
                   f"issue={dev.get('issue') or dev.get('explanation') or ''}"

    en_target, en_method = locate_best_sentence(claim_text, en_full)
    # JA側: related_fact_idのnotes/claim行を手がかりに、Ledger中の該当claim
    # 記述に近いJA文をbest-effortで探す(claim_text自体はEN文のため、直接
    # JA本文とは一致しない。fact_idのnumeric_value/claim等をprobeに使う)。
    ja_target, ja_method = locate_best_sentence(claim_text, ja_full)
    if ja_target is None:
        # claim_textのEN文言でJA側から探せない場合、related_fact_idの
        # Ledger claim文言をprobeとして再探索する(近似、完全一致は保証しない)。
        facts = precheck.parse_ledger_text(fixture["ledger_text"])
        fact = next((f for f in facts if f.get("fact_id") == (dev.get("related_fact_id") or "")), None)
        if fact and fact.get("claim"):
            ja_target, ja_method = locate_best_sentence(fact["claim"], ja_full)

    if en_target is None or ja_target is None:
        return {"updated_en_text": en_full, "updated_ja_text": ja_full, "method": "j1_pair_not_located",
                "guard_ok": False, "en_target": en_target, "ja_target": ja_target}

    prompt = J1_GENERIC_PROMPT_TEMPLATE.format(
        ledger_text=fixture["ledger_text"], ja_target=ja_target, en_target=en_target, rewrite_hint=rewrite_hint,
    )
    raw = simple_llm_call(client, state, consecutive_errors, call_log, f"{label_prefix}_j1_paired_rewrite",
                                s3rt.J1_DEVELOPER_MSG, prompt, model=MODEL)
    try:
        parsed = s3rt.extract_json_obj(raw) if raw else {}
    except Exception:  # noqa: BLE001
        parsed = {}
    ja_revised = parsed.get("ja_revised", "")
    en_revised = parsed.get("en_revised", "")
    updated_ja = ja_full.replace(ja_target, ja_revised, 1) if ja_revised else ja_full
    updated_en = en_full.replace(en_target, en_revised, 1) if en_revised else en_full
    guard_ok = bool(ja_revised) and bool(en_revised) and updated_ja != ja_full and updated_en != en_full

    if not guard_ok:
        # フォールバック: 全文最小編集(JA側、旧案Bの近似、§5-4)
        rewrite_hint_full = rewrite_hint
        prompt_fb = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], full_text=ja_full, target_sentence=ja_target,
            issue=dev.get("issue") or "", rewrite_hint=rewrite_hint_full,
        )
        ja_fallback = simple_llm_call(client, state, consecutive_errors, call_log,
                                            f"{label_prefix}_j1_fulltext_fallback",
                                            FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt_fb, model=MODEL)
        if ja_fallback:
            updated_ja = ja_fallback
            updated_en = en_full  # EN側はcycle 2のEN Recheckで再評価に委ねる
            guard_ok = updated_ja != ja_full
            method = "j1_failed+ja_fulltext_fallback"
        else:
            method = "j1_failed+ja_fulltext_fallback_api_failure"
    else:
        method = "j1_paired_rewrite"

    return {"updated_en_text": updated_en, "updated_ja_text": updated_ja, "method": method, "guard_ok": guard_ok,
            "en_target": en_target, "ja_target": ja_target}


def run_stage3_for_claim(client, state, consecutive_errors, call_log, label_prefix, fixture,
                          current_en_text: str, current_ja_text: str | None, claim_rec: dict) -> dict:
    """1 claim分のRewriteを実行し、更新後の(en_text, ja_text)を返す。"""
    use_pairing = (
        claim_rec.get("origin") == "ja_source"
        and current_ja_text is not None
        and fixture.get("source_article_text") is not None
    )
    working_fixture = dict(fixture)
    working_fixture["article_text"] = current_en_text
    if current_ja_text is not None:
        working_fixture["source_article_text"] = current_ja_text

    if use_pairing:
        res = paired_rewrite(client, state, consecutive_errors, call_log, label_prefix, working_fixture, claim_rec)
        return {"mechanism": "paired_ja_en(J-1)", "en_text": res["updated_en_text"],
                "ja_text": res["updated_ja_text"], "method": res["method"], "guard_ok": res["guard_ok"]}
    else:
        res = single_text_rewrite(client, state, consecutive_errors, call_log, label_prefix, working_fixture,
                                   "article_text", claim_rec)
        return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": res["updated_text"],
                "ja_text": current_ja_text, "method": res["method"], "guard_ok": res["guard_ok"]}


# ------------------------------------------------------------
# instance構築(委任_09対象: Hormuz run01/02/03、Meta run03、B群4、
# negative候補7、Safety群12)
# ------------------------------------------------------------
SAFETY_STAGE1_DIR = "er051_output/open233_checker_trial_01/trial_02/step1"
BGROUP_STAGE1_DIR = "er051_output/open233_checker_trial_01/trial_02/step2"
STEP3_STAGE1_DIR = "er051_output/open233_checker_trial_01/trial_02/step3"
NEG_STAGE1_DIR = "er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/c_negative"


def build_target_instances() -> list:
    instances = []

    # --- Safety群12(er009 9種+A2A3+A4+A5) ---
    for fx in g6.step1_fixtures():
        instances.append({
            "instance_id": f"safety_{fx['id']}", "group": "safety", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{SAFETY_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": "BLOCKING(Safety、§7-1)",
        })

    # --- B群4(B1/B2_hormuz/B3/B4) ---
    for fx in g6.step2_fixtures():
        if fx["id"] == "Meta_run03_standard":
            continue
        instances.append({
            "instance_id": f"bgroup_{fx['id']}", "group": "b_group", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{BGROUP_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": "claim単位混在(§7-0)",
            # B2_hormuz/B3は真のProduction V0では検出済みのReal-but-fixable
            # 群だが、V4A単発実行では非検出(recall欠落、§10/§14既知の限界)
            # になり得る。その場合はfixture自体のbaseline_parsed(V0、既に
            # MAJOR検出済み)へ代替してStage2/3の経路自体は検証する
            # (代替した事実は結果へ明記し、Stage1 recall miss発生として
            # 別途報告する。V4Aが実際に検出したと偽装しない)。
            "substitute_baseline_on_stage1_miss": fx["id"] in ("B2_hormuz", "B3"),
        })

    # --- Meta run_03 Standard(既存V4A再利用) ---
    meta_std = next(fx for fx in g6.step2_fixtures() if fx["id"] == "Meta_run03_standard")
    instances.append({
        "instance_id": "meta_run03_standard", "group": "meta", "fixture": meta_std,
        "stage1_mode": "reuse", "stage1_source": f"{BGROUP_STAGE1_DIR}/Meta_run03_standard/V4A/run_1.json",
        "expected_group_label": "BLOCKING→Rewrite→PASS(§7-1、現行は既存retry1回で通過)",
    })

    # --- Meta run_03 Advanced(V4A未実測、新規Stage1call) ---
    meta_adv = g6.load_audit_fixture(
        "meta_run03_advanced",
        "er019_output/family_x_refresh_e2e_01/meta/run_03/b1b/audit/deviation_checks/advanced_attempt1.json",
        "現行Production実測=LEDGER_COMPLIANT(V0)。V4Aでの再判定は本委任で新規実行。",
    )
    instances.append({
        "instance_id": "meta_run03_advanced", "group": "meta", "fixture": meta_adv,
        "stage1_mode": "fresh", "stage1_source": None,
        "expected_group_label": "Normal群(§7-5、Stage1のみでACCEPTABLE到達が期待)",
    })

    # --- Hormuz run_03 Advanced/Standard(既存V4A再利用) ---
    for fx in g6.step3_fixtures():
        if fx["id"] not in ("hormuz_run03_advanced", "hormuz_run03_standard"):
            continue
        label = "Normal群(§7-5)" if fx["id"] == "hormuz_run03_advanced" else "BLOCKING(Safety群、§7-1、narrow_scope)"
        instances.append({
            "instance_id": fx["id"], "group": "hormuz", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{STEP3_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": label,
        })

    # --- Hormuz run_01/run_02 Advanced(現行Production STOP実例、V4A未実測) ---
    for run_id, path in [
        ("hormuz_run01_advanced",
         "er019_output/family_x_refresh_e2e_01/hormuz/run_01/b1b/audit/deviation_checks/advanced_attempt1.json"),
        ("hormuz_run02_advanced",
         "er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json"),
    ]:
        fx = g6.load_audit_fixture(
            run_id, path,
            "現行Production実測=LEDGER_DEVIATION(V0、origin=ja_source、JA_RECHECK_REQUIRED STOP実例)。"
            "Standard(a2)は当該run内でStandardが生成される前にAdvanced段でSTOPしたため存在しない"
            "(既知のデータ限界、run_01/run_02ともAdvancedのみ)。V4Aでの再判定は本委任で新規実行。",
        )
        instances.append({
            "instance_id": run_id, "group": "hormuz", "fixture": fx,
            "stage1_mode": "fresh", "stage1_source": None,
            "expected_group_label": "BLOCKING→Rewrite→PASSが期待(現行Production STOP実例)",
        })

    # --- negative候補7(Normal群、既存V4A再利用) ---
    for fixture_id, path in step3cmp.NEGATIVE_SOURCE_FILES:
        fx = step3cmp.load_negative_fixture(fixture_id, path)
        instances.append({
            "instance_id": fixture_id, "group": "negative", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{NEG_STAGE1_DIR}/{fixture_id}/V4A/run_1.json",
            "expected_group_label": "ACCEPTABLE(Normal群、§7-5)",
        })

    return instances


# ------------------------------------------------------------
# precheck floor claim構築(§3-1/§4-3、findingが既存Stage1 MAJOR claimの
# related_fact_idと重複しない場合のみ追加)
# ------------------------------------------------------------
def build_precheck_floor_claims(fixture: dict, existing_fact_ids: set) -> list:
    findings = precheck.run_precheck(fixture["ledger_text"], fixture["article_text"])
    out = []
    for f in findings:
        if f["field"] in existing_fact_ids:
            continue
        dev = {
            "claim_in_article": f.get("article_evidence") if isinstance(f.get("article_evidence"), str)
            else str(f.get("article_evidence")),
            "issue": f"precheck detected {f['kind']} vs ledger_value={f['ledger_value']}",
            "explanation": f"deterministic precheck finding (kind={f['kind']})",
            "related_fact_id": f["field"], "origin": None,
            **{k: False for k in FLOOR_FLAGS},
        }
        out.append({"claim_text": dev["claim_in_article"], "origin": None, "related_fact_id": f["field"],
                     "dev": dev, "detected_by": "precheck"})
    return out


# ------------------------------------------------------------
# instance単位オーケストレーション(Stage1→2→3→Recheck、cycle上限2)
# ------------------------------------------------------------
def run_instance(client, state, consecutive_errors, inst: dict) -> dict:
    instance_id = inst["instance_id"]
    fixture = inst["fixture"]
    call_log: list = []
    t0 = time.time()

    if inst["stage1_mode"] == "reuse":
        stage1_parsed = stage1_reuse(inst["stage1_source"])
        stage1_call_used = False
    else:
        stage1_parsed = stage1_fresh(client, state, consecutive_errors, call_log,
                                      f"{instance_id}_stage1", fixture)
        stage1_call_used = True

    stage1_recall_miss_substituted = False
    if (inst.get("substitute_baseline_on_stage1_miss") and stage1_parsed.get("overall_status") != "LEDGER_DEVIATION"
            and fixture.get("baseline_parsed", {}).get("overall_status") == "LEDGER_DEVIATION"):
        # V4A単発実行がSafety観点で既知BLOCKINGのfixtureを非検出(recall
        # miss、§10/§14既知の限界)だったため、Stage2/3経路自体を検証する
        # 目的で実Production V0 baseline(既にMAJOR検出済み)へ代替する。
        # V4Aが検出したかのように偽装はせず、代替した事実をそのまま記録する。
        stage1_recall_miss_substituted = True
        stage1_parsed = fixture["baseline_parsed"]

    overall_status = stage1_parsed.get("overall_status")
    if overall_status != "LEDGER_DEVIATION":
        elapsed = round(time.time() - t0, 3)
        result = {
            "instance_id": instance_id, "group": inst["group"], "expected_group_label": inst["expected_group_label"],
            "final_state": "ACCEPTABLE_STAGE1", "stage4_reason": None, "cycles": [],
            "stage1_call_used": stage1_call_used, "stage1_recall_miss_substituted": stage1_recall_miss_substituted,
            "call_log": call_log,
            "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
            "total_calls": len(call_log), "elapsed_seconds": elapsed,
        }
        save_json(f"{OUT_DIR}/instances/{instance_id}.json", result)
        return result

    prior_blocking_claim_ids_all_cycles: set = set()
    current_en_text = fixture["article_text"]
    current_ja_text = fixture.get("source_article_text")
    cycles_log = []
    final_state, stage4_reason = None, None

    stage1_deviations = [d for d in stage1_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
    cycle = 1
    while True:
        working_fixture = dict(fixture)
        working_fixture["article_text"] = current_en_text
        if current_ja_text is not None:
            working_fixture["source_article_text"] = current_ja_text

        existing_fact_ids = {(d.get("related_fact_id") or "") for d in stage1_deviations}
        precheck_claims = build_precheck_floor_claims(working_fixture, existing_fact_ids)

        llm_claims = [{"claim_text": d.get("claim_in_article", ""), "origin": d.get("origin"),
                       "related_fact_id": d.get("related_fact_id"), "dev": d, "detected_by": "stage1_llm"}
                      for d in stage1_deviations]

        stage2_input_claims = [c for c in llm_claims]
        stage2_results = []
        if stage2_input_claims:
            stage2_results = run_stage2(client, state, consecutive_errors, call_log,
                                         f"{instance_id}_c{cycle}_stage2", working_fixture, stage2_input_claims)
        # precheck floor claimsはStage2をスキップし直接BLOCKING確定
        for pc in precheck_claims:
            stage2_results.append({**pc, "materiality": "BLOCKING", "llm_materiality": None,
                                    "basis": "precheck_floor", "rewrite_kind": "replace_with_ledger_value",
                                    "floor_reason": "precheck_floor"})

        blocking_claims = [c for c in stage2_results if c["materiality"] == "BLOCKING"]
        non_blocking_claims = [c for c in stage2_results if c["materiality"] != "BLOCKING"]

        cycle_record = {
            "cycle": cycle, "stage2_results": stage2_results,
            "blocking_count": len(blocking_claims), "non_blocking_count": len(non_blocking_claims),
        }

        if not blocking_claims:
            final_state = "RESOLVED_STAGE2_DOWNGRADE" if cycle == 1 else "RESOLVED_REWRITE_THEN_DOWNGRADE"
            cycles_log.append(cycle_record)
            break

        # 同一claim再発チェック(A5/A7): このcycleのBLOCKING claimのidentityが
        # 過去cycleで既にBLOCKING確定していたidentityと重複する場合、即Stage4
        current_ids = {claim_identity(c["dev"]) for c in blocking_claims}
        repeat_ids = current_ids & prior_blocking_claim_ids_all_cycles
        if repeat_ids and cycle > 1:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "same_claim_fact_id_reblocked"
            cycle_record["repeat_claim_ids"] = sorted(repeat_ids)
            cycles_log.append(cycle_record)
            break

        if cycle > MAX_CYCLES:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "cycle_limit_exhausted"
            cycles_log.append(cycle_record)
            break

        prior_blocking_claim_ids_all_cycles |= current_ids

        # Stage 3: 各BLOCKING claimに対しRewrite dispatch
        rewrite_records = []
        for c in blocking_claims:
            r = run_stage3_for_claim(client, state, consecutive_errors, call_log,
                                      f"{instance_id}_c{cycle}_{claim_identity(c['dev'])[:20]}",
                                      working_fixture, current_en_text, current_ja_text, c)
            current_en_text = r["en_text"]
            if r["ja_text"] is not None:
                current_ja_text = r["ja_text"]
            rewrite_records.append({"claim_identity": claim_identity(c["dev"]), "rewrite_kind": c["rewrite_kind"],
                                     "mechanism": r["mechanism"], "method": r["method"], "guard_ok": r["guard_ok"]})
        cycle_record["rewrite_records"] = rewrite_records

        # Recheck(全文、prior_issuesあり、A1)
        prior_issues = [{"fact_id": c["dev"].get("related_fact_id", ""),
                          "claim_in_article": c["claim_text"],
                          "issue": c["dev"].get("issue", ""), "explanation": c["dev"].get("explanation", "")}
                         for c in blocking_claims]
        recheck_fixture = dict(working_fixture)
        recheck_fixture["article_text"] = current_en_text
        if current_ja_text is not None:
            recheck_fixture["source_article_text"] = current_ja_text
        recheck_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                      f"{instance_id}_c{cycle}_recheck", recheck_fixture, current_en_text,
                                      prior_issues)
        # JA側も別途Recheck(paired rewriteが使われていた場合のみ、JA本文の
        # Ledger整合を独立に確認する。§5-4の「JA側1call+EN側1call」に対応)
        ja_recheck_parsed = None
        if current_ja_text is not None and any(rr["mechanism"].startswith("paired") for rr in rewrite_records):
            ja_recheck_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                             f"{instance_id}_c{cycle}_ja_recheck", recheck_fixture,
                                             current_ja_text, prior_issues)

        cycle_record["recheck_overall_status"] = recheck_parsed.get("overall_status")
        cycle_record["recheck_all_prior_issues_resolved"] = recheck_parsed.get("all_prior_issues_resolved")
        if ja_recheck_parsed is not None:
            cycle_record["ja_recheck_overall_status"] = ja_recheck_parsed.get("overall_status")

        en_ok = (recheck_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                 and recheck_parsed.get("all_prior_issues_resolved"))
        ja_ok = True if ja_recheck_parsed is None else (
            ja_recheck_parsed.get("overall_status") == "LEDGER_COMPLIANT"
            and ja_recheck_parsed.get("all_prior_issues_resolved"))

        cycles_log.append(cycle_record)

        if en_ok and ja_ok:
            final_state = "RESOLVED_REWRITE"
            break

        # 未解消 -> 次cycleのStage1 deviationsをRecheck結果から再構築
        stage1_deviations = [d for d in recheck_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
        cycle += 1
        if cycle > MAX_CYCLES:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "cycle_limit_exhausted_after_recheck"
            break

    elapsed = round(time.time() - t0, 3)
    result = {
        "instance_id": instance_id, "group": inst["group"], "expected_group_label": inst["expected_group_label"],
        "final_state": final_state, "stage4_reason": stage4_reason, "cycles": cycles_log,
        "stage1_call_used": stage1_call_used, "stage1_recall_miss_substituted": stage1_recall_miss_substituted,
        "call_log": call_log,
        "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
        "total_calls": len(call_log), "elapsed_seconds": elapsed,
    }
    save_json(f"{OUT_DIR}/instances/{instance_id}.json", result)
    return result


# ------------------------------------------------------------
# 測定集計(§8-1/§8-2/§8-3/§8-4)
# ------------------------------------------------------------
def aggregate_measurements(instance_results: list) -> dict:
    n = len(instance_results)
    initial_block = sum(1 for r in instance_results if r["final_state"] != "ACCEPTABLE_STAGE1")
    rescreen_auto_resolved = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_STAGE2_DOWNGRADE")
    rewrite_progressed = sum(1 for r in instance_results
                              if any(c.get("rewrite_records") for c in r["cycles"]))
    rewrite_auto_resolved = sum(1 for r in instance_results if r["final_state"] in
                                 ("RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE"))
    final_stop = sum(1 for r in instance_results if r["final_state"] == "STAGE4_ESCALATION")

    true_resolved = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_REWRITE"
                         and any(c.get("recheck_all_prior_issues_resolved") for c in r["cycles"]))
    quality_pass = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_STAGE2_DOWNGRADE"
                        and any(c["materiality"] == "QUALITY" for c in r["cycles"][0]["stage2_results"]))
    unresolved_unknown = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_REWRITE"
                              and not any(c.get("recheck_all_prior_issues_resolved") for c in r["cycles"]))

    quality_claims = []
    for r in instance_results:
        for c in r["cycles"]:
            for sr in c.get("stage2_results", []):
                if sr["materiality"] == "QUALITY":
                    quality_claims.append({"instance_id": r["instance_id"], "claim_text": sr["claim_text"]})

    total_calls = sum(r["total_calls"] for r in instance_results)
    total_cost = round(sum(r["total_cost_jpy"] for r in instance_results), 4)
    latencies = sorted(r["elapsed_seconds"] for r in instance_results)

    def percentile(vals, p):
        if not vals:
            return None
        idx = min(len(vals) - 1, int(round(p / 100 * (len(vals) - 1))))
        return vals[idx]

    completion = sum(1 for r in instance_results if r["final_state"] != "STAGE4_ESCALATION")
    retry_count = sum(1 for r in instance_results if any(c.get("rewrite_records") for c in r["cycles"]))
    loop_count = sum(1 for r in instance_results if len(r["cycles"]) >= MAX_CYCLES
                      and any(c.get("rewrite_records") for c in r["cycles"]))

    return {
        "n_instances": n,
        "self_recovery_6": {
            "initial_block_count": initial_block,
            "rescreening_auto_resolved_count": rescreen_auto_resolved,
            "rewrite_progressed_count": rewrite_progressed,
            "rewrite_auto_resolved_count": rewrite_auto_resolved,
            "final_stop_count": final_stop,
            "user_decision_required_count": final_stop,
        },
        "escalation_zero_breakdown": {
            "true_resolved_all_prior_issues_resolved_true": true_resolved,
            "quality_pass": quality_pass,
            "all_prior_issues_resolved_unconfirmed": unresolved_unknown,
            "silent_pass_candidate": 0,
        },
        "quality_claims": quality_claims,
        "qcd": {
            "total_calls": total_calls, "total_cost_jpy": total_cost,
            "avg_cost_per_instance_jpy": round(total_cost / n, 4) if n else 0,
            "latency_p50": percentile(latencies, 50), "latency_p95": percentile(latencies, 95),
            "completion_rate": round(completion / n, 4) if n else 0,
            "retry_rate": round(retry_count / n, 4) if n else 0,
            "loop_rate": round(loop_count / n, 4) if n else 0,
        },
        "final_stop_reasons": [r["stage4_reason"] for r in instance_results if r["stage4_reason"]],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", default="safety,b_group,meta,hormuz,negative",
                         help="comma-separated subset of safety,b_group,meta,hormuz,negative")
    parser.add_argument("--resume", action="store_true",
                         help="既に er052_output/.../instances/<id>.json が存在するinstanceは"
                              "再実行せずキャッシュ結果を再利用する(重複課金防止)")
    args = parser.parse_args()
    selected_groups = {g.strip() for g in args.groups.split(",") if g.strip()}

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]

    instances = [inst for inst in build_target_instances() if inst["group"] in selected_groups]
    instance_results = []
    stopped, stop_reason = False, None

    for inst in instances:
        cache_path = f"{OUT_DIR}/instances/{inst['instance_id']}.json"
        if args.resume and os.path.exists(cache_path):
            with open(cache_path, encoding="utf-8") as f:
                instance_results.append(json.load(f))
            continue
        try:
            result = run_instance(client, state, consecutive_errors, inst)
            instance_results.append(result)
        except TrialAbort as e:
            stopped = True
            stop_reason = str(e)
            break

    measurements = aggregate_measurements(instance_results) if instance_results else {}
    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_instances_completed": len(instance_results),
        "n_instances_planned": len(instances),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "measurements": measurements,
    }
    save_json(f"{OUT_DIR}/summary_flow_runner.json", {
        "summary": summary,
        "instance_results": [
            {k: v for k, v in r.items() if k != "call_log"} for r in instance_results
        ],
    })
    print(json.dumps({k: v for k, v in summary.items() if k != "measurements"}, ensure_ascii=False, indent=2))
    print(json.dumps(measurements, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
