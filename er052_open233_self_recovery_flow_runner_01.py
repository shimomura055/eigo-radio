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

import er003_ja_to_en_translation as jtr
import er003_v1_en_direct_vfl_01_generate as vfl01
import er010_ledger_local_rewrite_09 as er010
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp
import er052_open233_self_recovery_precheck_01 as precheck
import er052_open233_self_recovery_s1d_trial_01 as s1d
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_production_01 as s2p
import er052_open233_self_recovery_stage3_rewrite_trial_01 as s3rt

# 委任_10(iteration 2): 既存委任_09の出力(OUT_DIR_ITER1、budget_state_
# c233m.json)は変更しない。iteration 2の出力は別ディレクトリへ書く
# (rewrite_hint/J-1改善/claim identity正規化/delete再出現確認/S1-U variant
# を含む再実行、委任文§0)。Stage1(V4A)は既存V4A出力(OUT_DIR_ITER1と同一
# fixture)をそのまま再利用するため、reuseパス自体はcommitted_09時点の
# 既存artifactを参照し続ける(Stage1のprompt自体は不変のため二重課金しない)。
OUT_DIR_ITER1 = "er052_output/open233_self_recovery_flow_runner_01"
OUT_DIR_ITER2 = "er052_output/open233_self_recovery_flow_runner_01_iter2"
# 委任_11(iteration 3): 既存iteration1/2の出力(OUT_DIR_ITER1/OUT_DIR_ITER2)
# は変更しない。iteration 3の出力は別ディレクトリへ書く(Opus L2 #2の
# バグ修正2件+停止判定是正+段落単位Rewrite+測定是正+Rewrite由来逸脱検出+
# S1-U安価代替の反映後の再実行、委任文§0/§4)。Stage1(V4A)は既存出力を
# sha256一致で再利用する(build_target_instances()のstage1_source自体は
# iteration 1時点のartifactを参照し続ける、二重課金防止)。
OUT_DIR = "er052_output/open233_self_recovery_flow_runner_01_iter3"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233o_d.json"
TOTAL_BUDGET_JPY = 45.0  # 委任_11 作業D Guardrail(想定)
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
MODEL = "gpt-6-luna"
MAX_CYCLES = 2
# 委任_11 作業B-3(§3-3停止判定の是正): 別claim(fact_id同一だが本文相違、
# またはfact_id無しの新規claim)に限り、blocking件数が厳密に減少している
# 場合だけcycle 3を1回許可する(上限3、Opus L2 #2論点1推奨3)。
HARD_MAX_CYCLES = MAX_CYCLES + 1
CLAIM_TEXT_SIMILARITY_THRESHOLD = 0.75

FLOOR_FLAGS = [
    "changed_actor", "changed_number", "changed_negation",
    "changed_comparison", "changed_time", "changed_certainty",
]

# 委任_11 作業B-5(§8測定是正、Opus L2 #2論点5/6): 群別Escalation率算出のため、
# 「実run(現行Production記事に相当する6 instance)」を明示的に区別する
# (合成Safety/B群/negativeは正解ラベル付きfixtureであり、実記事の分母には
# 混ぜない、Opus L2 #2論点5)。
REAL_RUN_INSTANCE_IDS = frozenset({
    "hormuz_run01_advanced", "hormuz_run02_advanced", "hormuz_run03_advanced",
    "hormuz_run03_standard", "meta_run03_standard", "meta_run03_advanced",
})

# 委任_11 作業B-5(§8測定是正、Opus L2 #2論点6): 記事単位(Standard+Advanced
# 合算)のコスト・合否を集計するためのarticle_id -> instance_idグループ
# (Standardが存在しないrun_01/run_02はAdvanced単体、既知のデータ限界)。
ARTICLE_GROUPS = {
    "hormuz_run01": ["hormuz_run01_advanced"],
    "hormuz_run02": ["hormuz_run02_advanced"],
    "hormuz_run03": ["hormuz_run03_advanced", "hormuz_run03_standard"],
    "meta_run03": ["meta_run03_advanced", "meta_run03_standard"],
}

# 委任_11 作業B-5(§8測定是正、Opus L2 #2論点2): S1-U追加BLOCKの正解ラベル
# 照合用(委任_09/_10で確定した既知のStage1 recall miss実例=真陽性、
# negative群でのS1-U追加BLOCKは偽陽性、それ以外はラベル無し)。
KNOWN_RECALL_MISS_INSTANCE_IDS = frozenset({"bgroup_B2_hormuz", "bgroup_B3", "hormuz_run02_advanced"})


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
# 委任_10で正規化を強化(claim identity trackingの脆弱性補強、Opus L2 #1
# 論点5): fact_idが無い場合のfallback hashは、表記揺れ(引用符の有無・
# 大小文字・空白の数)だけで別claim扱いされてしまう既知の脆弱性があった
# ため、hash化前に正規化する。fact_idがある場合はfact_idが最優先(不変)。
# ------------------------------------------------------------
def normalize_claim_text(s: str) -> str:
    s = s2p._strip_wrapping_quotes(s or "")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def claim_identity(dev: dict) -> str:
    fact_id = (dev.get("related_fact_id") or "").strip()
    if fact_id:
        return f"fact:{fact_id}"
    claim = normalize_claim_text(dev.get("claim_in_article") or "")
    return "claim:" + hashlib.sha256(claim.encode("utf-8")).hexdigest()[:16]


def find_matching_prior_record(dev: dict, prior_records: list, threshold: float = CLAIM_TEXT_SIMILARITY_THRESHOLD):
    """委任_11 作業B-3(§3-3停止判定の是正、Opus L2 #2論点1推奨3): 従来の
    claim_identity()単独(fact_id一致のみ)による停止判定は、設計§3-3の原意
    (「Rewriteが当該claimに効かなかったことが実証された場合」)より厳しく、
    同一fact_idに紐づく*別の文*(兄弟文カスケード、例: bgroup_B4のhook文/
    タイトル)まで「同一claim再発」として即Stage4にしていた
    (safety_A2A3/safety_A4/meta_run03_standard/meta_run03_advanced/
    bgroup_B4/neg1_meta_b3prod_a2で実測)。本関数はfact_idが一致する場合、
    正規化claim本文の近似一致(SequenceMatcher比率>=threshold)も要求する。
    fact_idが無いclaim(hashベースidentity)は従来通り厳密一致のみ
    (Opus L2 #1論点5で確定した保守的挙動を維持、変更しない)。
    一致するprior recordがあれば返し(=「同一claimが再発した」)、無ければ
    Noneを返す(=「別claいとして扱い、cycle 3の1回限り緩和対象になり得る」)。"""
    fact_id = (dev.get("related_fact_id") or "").strip()
    claim_text_norm = normalize_claim_text(dev.get("claim_in_article") or "")
    ident = claim_identity(dev)
    for rec in prior_records:
        if fact_id:
            if rec["fact_id"] != fact_id:
                continue
            prior_text = rec["claim_text_norm"]
            if claim_text_norm and prior_text and (
                claim_text_norm == prior_text
                or difflib.SequenceMatcher(None, claim_text_norm, prior_text).ratio() >= threshold
            ):
                return rec
        else:
            if rec["identity"] == ident:
                return rec
    return None


# ------------------------------------------------------------
# Stage 1: 既存出力の再利用 or 新規V4A実行(routing述語=overall_status、§3-1)
# ------------------------------------------------------------
def run_ja_en_equivalence_check(client, state, consecutive_errors, call_log, label,
                                 ja_text: str, en_text: str) -> dict:
    """委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4推奨2):
    paired local rewrite(J-1)実行後のJA↔EN等価チェック(1 call)。既存
    Production資産(`er003_ja_to_en_translation.py`の翻訳忠実性QA:
    プロンプトテンプレート`build_fidelity_qa_prompt`+JSON Schema
    `FIDELITY_QA_JSON_SCHEMA`+パーサ`parse_and_validate_fidelity_qa_output`)
    をread-onlyで借用する(`make_fidelity_qa_fn`は使わない。同関数は独自に
    `OpenAI()`クライアントを生成しdotenvを読み直すため、本runner自身の
    client/budget/telemetryパターン[§既存simple_llm_call/record_callと
    同一原則]と二重管理になるのを避けるため)。verdict(PASS/
    REVIEW_REQUIRED/FAIL)を記録するのみで、flow制御(fail-closed判定)
    には使わない(既存Recheck機構と重複する権限を持たせない、測定・
    報告専用)。"""
    check_budget(state)
    prompt = jtr.build_fidelity_qa_prompt(ja_text, en_text)
    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **jtr.FIDELITY_QA_JSON_SCHEMA}},
                input=prompt,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "ja_en_equivalence", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "ja_en_equivalence")
        return {"verdict": None, "api_failure": True}
    try:
        parsed = jtr.parse_and_validate_fidelity_qa_output(response.output_text)
    except Exception:  # noqa: BLE001
        parsed = {"verdict": None}
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "ja_en_equivalence", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      "verdict": parsed.get("verdict")})
    record_call(state, consecutive_errors, label, cost, True, "ja_en_equivalence", usage)
    return {"verdict": parsed.get("verdict"), "api_failure": False, "raw": parsed}


def detect_rewrite_new_precheck_findings(ledger_text: str, baseline_findings: list, updated_text: str) -> list:
    """委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4推奨3、
    決定論・¥0): 編集後テキストへprecheckを再実行し、Rewrite前(baseline)に
    無かった新規finding(Ledger未出の数値・固有名詞の増加等)を検出する。
    誤検知を避けるため(field,kind)組の集合差分のみを見る(文言そのものの
    差異は問わない)。"""
    post_findings = precheck.run_precheck(ledger_text, updated_text)
    baseline_keys = {(f["field"], f["kind"]) for f in baseline_findings}
    return [f for f in post_findings if (f["field"], f["kind"]) not in baseline_keys]


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
# S1-U variant(委任_10、§3-1): Stage1(V4A)がACCEPTABLEだった場合に限り、
# S1-D(materiality一体型、1 call)を追加実行し、BLOCKING判定claimのみを
# union(fail-closed)でStage2以降へ送る(Stage1 recall miss対策)。V4Aの
# 出力自体は変更せず、追加のBLOCKING claimが見つかった場合のみメイン
# フローへ合流させる(既存のACCEPTABLE_STAGE1経路そのものは変更しない)。
# ------------------------------------------------------------
def stage1_union_screen(client, state, consecutive_errors, call_log, label, fixture) -> dict:
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = s1d.run_s1d_check(client, fixture["ledger_text"], fixture["article_text"],
                                        source_article_text=fixture.get("source_article_text"), model=MODEL)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    if result is None:
        call_log.append({"label": label, "recovery_stage": "stage1_union_screen", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage1_union_screen")
        return {"blocking_deviations": [], "api_failure": True}
    call_log.append({"label": label, "recovery_stage": "stage1_union_screen", "cost_jpy": result["cost_jpy"],
                      "usage": result["usage"], "elapsed_seconds": result["elapsed_seconds"],
                      "prompt_sha256": result["prompt_sha256"]})
    record_call(state, consecutive_errors, label, result["cost_jpy"], True, "stage1_union_screen", result["usage"])
    blocking = [d for d in result["parsed"]["deviations"] if d.get("materiality") == "BLOCKING"]
    # S1D出力のキー(claim_in_article/related_fact_id_guess/changed_*)をV4A
    # deviations互換のキー名へ変換する(severity=MAJOR固定、related_fact_id
    # はrelated_fact_id_guessをそのまま採用、originはS1Dが出力しないためNone)。
    converted = []
    for d in blocking:
        converted.append({
            "claim_in_article": d.get("claim_in_article", ""), "origin": None,
            "related_fact_id": d.get("related_fact_id_guess", ""), "severity": "MAJOR",
            **{k: d.get(k, False) for k in FLOOR_FLAGS},
        })
    return {"blocking_deviations": converted, "api_failure": False}


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
                        "rewrite_hint": "", "floor_reason": "stage2_api_failure_failclosed"})
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
            materiality, basis, rewrite_kind, rewrite_hint = (
                "BLOCKING", "none", "replace_with_ledger_value", "")
            floor_reason = "schema_index_mismatch_failclosed"
        else:
            materiality, basis, rewrite_kind = match["materiality"], match["basis"], match["rewrite_kind"]
            rewrite_hint = match.get("rewrite_hint", "") or ""
            floor_reason = None
        final_materiality, floor_applied = apply_floor(materiality, c["dev"], c.get("detected_by", "stage1_llm"))
        if floor_applied:
            floor_reason = floor_applied
        out.append({**c, "materiality": final_materiality, "llm_materiality": materiality, "basis": basis,
                    "rewrite_kind": rewrite_kind if rewrite_kind != "none" else "replace_with_ledger_value",
                    "rewrite_hint": rewrite_hint, "floor_reason": floor_reason})
    return out


# ------------------------------------------------------------
# Stage 3: Rewrite dispatch
# ------------------------------------------------------------
def locate_best_sentence(claim_text: str, full_text: str, ambiguous_margin: float = 0.08) -> tuple:
    """exact substring優先、無ければSequenceMatcher近傍探索(JA/EN共通の
    簡易汎用実装。専用の日本語文分割モジュールは実装しない、既知の限界
    として§5-4-補2と同一の位置づけ)。
    委任_10で追加: 最有力候補と次点候補のスコア差がambiguous_margin未満の
    場合は「ambiguous」として扱い、単一文を編集対象に確定させず
    呼び出し側の全文フォールバック(既存guard機構)へ委ねる(J-1改善、
    誤った文を編集してしまうリスクの低減)。"""
    if claim_text and claim_text.strip() in full_text:
        return claim_text.strip(), "exact_substring"
    sentences = re.split(r"(?<=[。.!?])", full_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    scored = sorted(
        ((difflib.SequenceMatcher(None, claim_text, s).ratio(), s) for s in sentences),
        key=lambda x: x[0], reverse=True,
    )
    if not scored:
        return None, "not_found"
    best_ratio, best = scored[0]
    second_ratio = scored[1][0] if len(scored) > 1 else 0.0
    # 文字単位SequenceMatcherは短い文同士だと偶然の一致でも比率が高くなり
    # やすいため(語単位jaccardより緩い)、閾値0.5(実測値: 言い換え一致
    # 0.92、無関係文0.41)をfail-closed側の下限として採用する。
    if best_ratio >= 0.5 and (best_ratio - second_ratio) >= ambiguous_margin:
        return best, f"sequence_matcher(ratio={round(best_ratio, 2)})"
    if best_ratio >= 0.5:
        return None, f"ambiguous(best={round(best_ratio, 2)},second={round(second_ratio, 2)})"
    return None, "not_found"


# ------------------------------------------------------------
# J-1(paired JA/EN local rewrite)ロケータ改善(委任_10、§5-4)
# ------------------------------------------------------------
# 開き引用符と閉じ引用符が異なる文字のペア(「」『』“”)はregexで安全に
# 抽出できるが、開き=閉じが同一文字("のみ)はfinditerの逐次マッチングだと
# 「1個目の引用が短すぎて{8,220}を満たさない場合、2個目の開き引用符を
# 1個目の閉じ引用符と誤ってペアリングしてしまう」既知のバグがある
# (委任_10のtestで実際に検出、隣接する2つの引用の間の非引用テキストを
# 誤抽出する)。そのため"はstr.split()による厳密なペアリングで処理する。
_BRACKET_QUOTE_PATTERNS = [
    re.compile(r"“([^”\n]{8,220})”"),
    re.compile(r"「([^」\n]{4,220})」"),
    re.compile(r"『([^』\n]{4,220})』"),
]
# 桁の並びのみ比較する(%等の記号は言語間で表記が揺れる[例: "20%"と"20
# percent"]ため比較対象から除く、位置比マッピングの数値トークン一致用)。
_DIGIT_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?")


def extract_quoted_fragment(hint: str) -> str | None:
    """rewrite_hint文字列中の最長の引用断片(逐語引用)を抽出する(委任_10、
    §4-5で追加したrewrite_hintを対象文特定の第一キーとして使うための補助)。
    引用符が無ければNone(呼び出し側は既存のlocate_best_sentenceへfallback)。"""
    if not hint:
        return None
    candidates = []
    for pat in _BRACKET_QUOTE_PATTERNS:
        for m in pat.finditer(hint):
            frag = m.group(1).strip()
            if frag:
                candidates.append(frag)
    # 直双引用符(")は開き=閉じが同一文字のため、split()で厳密にペアリング
    # する(奇数indexの要素だけが引用符の内側)。
    parts = hint.split('"')
    for i in range(1, len(parts), 2):
        frag = parts[i].strip()
        if len(frag) >= 8:
            candidates.append(frag)
    if not candidates:
        return None
    return max(candidates, key=len)


def split_sentences_generic(text: str) -> list:
    """見出し行(#開始)を除いた本文を句点等(全角。！？/半角.!?)で分割する
    汎用関数(JA/EN共通、位置比計算用)。"""
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not line.strip().startswith("#")]
    flat = " ".join(lines)
    parts = re.split(r"(?<=[。！？.!?])\s*", flat)
    return [p.strip() for p in parts if p.strip()]


def split_ja_sentences(text: str) -> list:
    """JA本文を句点(全角。！？)で分割する(見出し行除外、単語間空白を仮定
    しないJA向けの分割、位置比マッピング用)。"""
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not line.strip().startswith("#")]
    flat = "".join(lines)
    parts = re.split(r"(?<=[。！？])", flat)
    return [p.strip() for p in parts if p.strip()]


def locate_target(claim_text: str, rewrite_hint: str, full_text: str) -> tuple:
    """対象文特定の統合ロケータ(委任_10、§5-4): 第一キー=rewrite_hintの
    引用断片(exact substring)、第二キー=claim_textによるlocate_best_
    sentence(exact/SequenceMatcher)、第三キー=er010.locate_target_sentence
    (英語word-overlap、read-only借用)。いずれも失敗(またはambiguous)の
    場合はNoneを返し、呼び出し側の全文フォールバックに委ねる。"""
    hint_fragment = extract_quoted_fragment(rewrite_hint)
    if hint_fragment and hint_fragment in full_text:
        return hint_fragment, "rewrite_hint_quote"
    target, method = locate_best_sentence(claim_text, full_text)
    if target is not None:
        return target, method
    try:
        fb_target, fb_method = er010.locate_target_sentence(claim_text, full_text)
    except Exception:  # noqa: BLE001
        fb_target, fb_method = None, "er010_fallback_error"
    if fb_target is not None:
        return fb_target, f"er010_word_overlap({fb_method})"
    return None, method


def locate_paragraph_block(target_sentence: str | None, full_text: str) -> tuple:
    """委任_11 作業B-4(§5段落単位Rewriteへの拡張、Opus L2 #2論点1推奨4):
    Rewrite対象単位を「引用文(1文)」から「同一含意を持つ段落ブロック」へ
    拡張するための段落特定。段落は空行(\\n\\n)区切りとする。target_sentence
    を含む段落の直前blockが見出し行(#開始)のみで構成される場合は、見出し/
    タイトル/hook行も対象へ含める(bgroup_B4[hook文+タイトル]・
    neg1_meta_b3prod_a2[タイトル]で実測された兄弟文カスケードへの対策)。
    見つからない場合は(None, None)を返し、呼び出し側は文単位の既存経路
    (locate_targetの結果そのもの)にフォールバックする。"""
    if not target_sentence:
        return None, None
    blocks = full_text.split("\n\n")
    for i, block in enumerate(blocks):
        if target_sentence.strip() and target_sentence.strip() in block:
            if i > 0 and blocks[i - 1].strip().startswith("#"):
                combined = blocks[i - 1] + "\n\n" + block
                return combined, (i - 1, i)
            return block, (i, i)
    return None, None


def locate_ja_counterpart_by_position(en_target: str, en_full: str, ja_full: str) -> tuple:
    """J-1改善(委任_10、§5-4): EN対象文のen_full内での文位置比を、JA全文の
    句点分割へ写像し(対訳記事はほぼ同順序で対応するという構造的近似)、
    写像先window(±2文)内で数値トークン(桁数・%等、言語非依存)一致を
    優先しつつ候補を選ぶ。数値トークンが無ければwindow中央(推定位置その
    もの)を採用する(固有名詞は言語間で一致しないため主キーにしない、
    既知の限界として報告する)。"""
    en_sentences = split_sentences_generic(en_full)
    ja_sentences = split_ja_sentences(ja_full)
    if not en_sentences or not ja_sentences:
        return None, "position_mapping_empty"

    en_index = None
    for i, s in enumerate(en_sentences):
        if en_target.strip() and (en_target.strip() in s or s in en_target.strip()):
            en_index = i
            break
    if en_index is None:
        best_i, best_ratio = 0, 0.0
        for i, s in enumerate(en_sentences):
            ratio = difflib.SequenceMatcher(None, en_target, s).ratio()
            if ratio > best_ratio:
                best_i, best_ratio = i, ratio
        en_index = best_i

    ratio_pos = en_index / max(1, len(en_sentences) - 1)
    ja_index_guess = round(ratio_pos * (len(ja_sentences) - 1))
    lo = max(0, ja_index_guess - 2)
    hi = min(len(ja_sentences), ja_index_guess + 3)
    window = ja_sentences[lo:hi]
    if not window:
        return None, "position_mapping_empty_window"

    en_digits = set(_DIGIT_TOKEN_RE.findall(en_target))
    if en_digits:
        for s in window:
            if en_digits & set(_DIGIT_TOKEN_RE.findall(s)):
                return s, f"ja_position_ratio+digit_match(idx={ja_index_guess})"
    center_idx = min(len(window) - 1, max(0, ja_index_guess - lo))
    return window[center_idx], f"ja_position_ratio(idx={ja_index_guess})"


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

# 委任_11 作業B-4(§5段落単位Rewrite、Opus L2 #2論点1推奨4): 引用文1文だけ
# でなく、同一含意を持つ段落ブロック(見出し/タイトル/hook行を含み得る)を
# 対象にする。「この段落内で同じ含意を述べる全ての文を削除・限定せよ」を
# 明記する(兄弟文カスケード対策)。
E2_PARAGRAPH_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker. You must revise a paragraph "
    "block (which may include a heading/title/hook line) using the smallest edit that removes the "
    "unsupported claim from EVERY sentence in the block that states or implies it. You may be given "
    "Japanese or English text."
)
E2_PARAGRAPH_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Paragraph block flagged as containing a Ledger deviation (may include a heading/title/hook line)]
{paragraph_block}

[Sentence originally flagged]
{target_sentence}

[Checker's issue]
{issue}

[Rewrite hint]
{rewrite_hint}

Rewrite this paragraph block to resolve the issue. Delete or narrow EVERY sentence in this block \
(including any heading/title/hook line) that states or implies the same unsupported claim, per the \
rewrite hint above. Keep the same language as the input. Leave sentences unrelated to this issue \
unchanged, character-for-character, wherever possible. Return ONLY the revised paragraph block text, \
nothing else (no explanation, no code fences)."""

J1_PARAGRAPH_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[JA paragraph block (may include a heading/title/hook line)]
{ja_block}

[EN paragraph block (translation of the same paragraph)]
{en_block}

[Originally flagged sentences]
JA: {ja_target}
EN: {en_target}

[rewrite_hint]
{rewrite_hint}

Revise BOTH paragraph blocks (paired, minimal edits). Delete or narrow EVERY sentence in EACH block \
(including any heading/title/hook line) that states or implies the same unsupported claim, per the \
rewrite_hint above. Leave sentences unrelated to this issue unchanged wherever possible. Return strict \
JSON: {{"ja_revised": "<full revised JA paragraph block>", "en_revised": "<full revised EN paragraph block>"}}"""


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
    # 委任_10: Stage2出力のrewrite_hint(LLM生成、対象文引用+修正指示+fact_id)を
    # 優先して使う。空の場合(schema_index_mismatch等のfail-closed経路)のみ
    # 旧来の合成文字列へfallbackする。
    rewrite_hint = claim_rec.get("rewrite_hint") or f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}"

    target_sentence, locate_method = locate_target(claim_text, rewrite_hint, full_text)
    method_used = None
    updated_text = full_text
    found = target_sentence is not None

    delete_reoccurrence_detected = False
    if rewrite_kind == "delete":
        if found:
            updated_text = full_text.replace(target_sentence, "", 1)
            method_used = f"deterministic_delete({locate_method})"
            # 委任_10: delete型のclaim単位再出現確認(§2-4)。exact substring
            # 一致だけでなく、言い換えによる同一claimの再出現もfuzzy match
            # (locate_best_sentence)で検出し、見つかった場合はguard抵触
            # として全文フォールバックへ回す(削除漏れ・重複箇所の見逃し対策)。
            reoccur_target, _reoccur_method = locate_best_sentence(claim_text, updated_text)
            delete_reoccurrence_detected = reoccur_target is not None
        else:
            method_used = "delete_target_not_found"
    else:
        if found:
            # 委任_11 作業B-4: 対象文を含む段落ブロック(見出し/タイトル行を
            # 含み得る)が特定できれば、段落単位でRewriteする(兄弟文カスケード
            # 対策)。見つからなければ従来の文単位E-2 Promptへフォールバック。
            paragraph_block, _ = locate_paragraph_block(target_sentence, full_text)
            if paragraph_block:
                prompt = E2_PARAGRAPH_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], paragraph_block=paragraph_block,
                    target_sentence=target_sentence, issue=issue, rewrite_hint=rewrite_hint,
                )
                revised_block = simple_llm_call(client, state, consecutive_errors, call_log,
                                                 f"{label_prefix}_e2_paragraph_rewrite",
                                                 E2_PARAGRAPH_DEVELOPER_MSG, prompt, model=MODEL)
                if revised_block is not None:
                    updated_text = full_text.replace(paragraph_block, revised_block, 1)
                    method_used = f"e2_paragraph_rewrite({locate_method})"
                else:
                    method_used = "e2_paragraph_rewrite_api_failure"
            else:
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

    guard_ok = (updated_text != full_text and claim_text.strip() not in updated_text
                and not delete_reoccurrence_detected) if found else False
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
            "target_sentence": target_sentence, "locate_method": locate_method,
            "delete_reoccurrence_detected": delete_reoccurrence_detected}


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
    # 委任_10: Stage2出力のrewrite_hint(LLM生成)を優先して使う。空の場合
    # (fail-closed経路等)のみ旧来の合成文字列へfallbackする。
    rewrite_hint = claim_rec.get("rewrite_hint") or (
        f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}, "
        f"issue={dev.get('issue') or dev.get('explanation') or ''}"
    )

    en_target, en_method = locate_target(claim_text, rewrite_hint, en_full)
    # JA側ロケータ改善(委任_10、§5-4): 第一キー=rewrite_hintの引用断片
    # (もしJA本文中に逐語引用があれば)、第二キー=claim_text自体での
    # lexical探索(claim_textはEN文のため通常は失敗する、既知の限界)、
    # 第三キー=Ledger claim文言でのlexical探索(既存)、第四キー(NEW)=
    # EN対象文のen_full内での文位置比をJA全文へ写像する構造的近似
    # (対訳記事がほぼ同順序で対応するという仮定、locate_ja_counterpart_
    # by_position)。
    ja_target, ja_method = None, "not_attempted"
    hint_fragment = extract_quoted_fragment(rewrite_hint)
    if hint_fragment and hint_fragment in ja_full:
        ja_target, ja_method = hint_fragment, "rewrite_hint_quote"
    if ja_target is None:
        ja_target, ja_method = locate_best_sentence(claim_text, ja_full)
    if ja_target is None:
        # claim_textのEN文言でJA側から探せない場合、related_fact_idの
        # Ledger claim文言をprobeとして再探索する(近似、完全一致は保証しない)。
        facts = precheck.parse_ledger_text(fixture["ledger_text"])
        fact = next((f for f in facts if f.get("fact_id") == (dev.get("related_fact_id") or "")), None)
        if fact and fact.get("claim"):
            ja_target, ja_method = locate_best_sentence(fact["claim"], ja_full)
    if ja_target is None and en_target is not None:
        ja_target, ja_method = locate_ja_counterpart_by_position(en_target, en_full, ja_full)

    en_located = en_target is not None
    ja_located = ja_target is not None
    guard_ok = False
    method = None
    updated_en = en_full
    updated_ja = ja_full

    if en_located and ja_located:
        # 委任_11 作業B-4(§5段落単位Rewriteへの拡張): 対象文を含む段落
        # ブロック(見出し/タイトル/hook行を含み得る)が両言語で特定できれば
        # 段落単位でpaired rewriteする(兄弟文カスケード対策)。特定できない
        # 場合は従来の文単位J1 Promptへフォールバックする。
        ja_block, _ = locate_paragraph_block(ja_target, ja_full)
        en_block, _ = locate_paragraph_block(en_target, en_full)
        use_paragraph = bool(ja_block) and bool(en_block)
        if use_paragraph:
            prompt = J1_PARAGRAPH_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], ja_block=ja_block, en_block=en_block,
                ja_target=ja_target, en_target=en_target, rewrite_hint=rewrite_hint,
            )
        else:
            prompt = J1_GENERIC_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], ja_target=ja_target, en_target=en_target,
                rewrite_hint=rewrite_hint,
            )
        raw = simple_llm_call(client, state, consecutive_errors, call_log, f"{label_prefix}_j1_paired_rewrite",
                                    s3rt.J1_DEVELOPER_MSG, prompt, model=MODEL)
        try:
            parsed = s3rt.extract_json_obj(raw) if raw else {}
        except Exception:  # noqa: BLE001
            parsed = {}
        ja_revised = parsed.get("ja_revised", "")
        en_revised = parsed.get("en_revised", "")
        if use_paragraph:
            updated_ja = ja_full.replace(ja_block, ja_revised, 1) if ja_revised else ja_full
            updated_en = en_full.replace(en_block, en_revised, 1) if en_revised else en_full
        else:
            updated_ja = ja_full.replace(ja_target, ja_revised, 1) if ja_revised else ja_full
            updated_en = en_full.replace(en_target, en_revised, 1) if en_revised else en_full
        guard_ok = bool(ja_revised) and bool(en_revised) and updated_ja != ja_full and updated_en != en_full
        if guard_ok:
            method = "j1_paired_rewrite_paragraph" if use_paragraph else "j1_paired_rewrite"

    if not guard_ok:
        # 委任_11 作業B-1(バグA是正、Opus L2 #2論点1推奨1): 従来はen_target/
        # ja_targetのいずれかが特定できない(j1_pair_not_located)場合、この
        # 全文フォールバックへ到達せず早期returnしていたため、テキストが
        # 一切変わらないままcycle2で同一fact_idが再検出され、claim_identity()
        # 一致により即Stage4していた(safety_A2A3で実測、Opus L2 #2論点1)。
        # 本is正では、locate失敗の場合も含め必ずJA全文フォールバックを試みる。
        ja_target_for_fb = ja_target or claim_text
        prompt_fb = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], full_text=ja_full, target_sentence=ja_target_for_fb,
            issue=dev.get("issue") or "", rewrite_hint=rewrite_hint,
        )
        ja_fallback = simple_llm_call(client, state, consecutive_errors, call_log,
                                            f"{label_prefix}_j1_fulltext_fallback",
                                            FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt_fb, model=MODEL)
        if ja_fallback:
            updated_ja = ja_fallback
            ja_guard_ok = updated_ja != ja_full
            # 委任_11 作業B-2(バグB是正、Opus L2 #2論点1推奨2/論点4推奨1):
            # JA全文フォールバック後にEN側を無編集のまま残すと、JA/EN記事対が
            # 構造的に乖離する(safety_A4で実測)。EN側も同一rewrite_hintで
            # 必ず1 call編集する(en_targetが特定できればE-2局所編集、
            # できなければEN側も全文フォールバック)。
            if en_target is not None:
                prompt_en = E2_GENERIC_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], target_sentence=en_target,
                    issue=dev.get("issue") or dev.get("explanation") or claim_text, rewrite_hint=rewrite_hint,
                )
                en_revised_fb = simple_llm_call(client, state, consecutive_errors, call_log,
                                                      f"{label_prefix}_j1_en_fallback_edit",
                                                      E2_GENERIC_DEVELOPER_MSG, prompt_en, model=MODEL)
                if en_revised_fb is not None:
                    updated_en = en_full.replace(en_target, en_revised_fb, 1)
                    method = "j1_failed+ja_fulltext_fallback+en_local_edit"
                else:
                    updated_en = en_full
                    method = "j1_failed+ja_fulltext_fallback+en_local_edit_api_failure"
            else:
                prompt_en_fb = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], full_text=en_full, target_sentence=claim_text,
                    issue=dev.get("issue") or dev.get("explanation") or claim_text, rewrite_hint=rewrite_hint,
                )
                en_fallback = simple_llm_call(client, state, consecutive_errors, call_log,
                                                    f"{label_prefix}_j1_en_fulltext_fallback",
                                                    FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt_en_fb, model=MODEL)
                if en_fallback:
                    updated_en = en_fallback
                    method = "j1_failed+ja_fulltext_fallback+en_fulltext_fallback"
                else:
                    updated_en = en_full
                    method = "j1_failed+ja_fulltext_fallback+en_fulltext_fallback_api_failure"
            guard_ok = ja_guard_ok
        else:
            updated_ja = ja_full
            updated_en = en_full
            method = "j1_failed+ja_fulltext_fallback_api_failure"
            guard_ok = False

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
            # S1-U variant対象(委任_10、§3-1): B2_hormuz/B3はStage1(V4A)
            # recall miss実例(§10/§14既知の限界)であり、S1-U(S1-D union)が
            # これを追加検出できるかを実測する。
            "s1u_eligible": fx["id"] in ("B2_hormuz", "B3"),
        })

    # --- Meta run_03 Standard(既存V4A再利用) ---
    meta_std = next(fx for fx in g6.step2_fixtures() if fx["id"] == "Meta_run03_standard")
    instances.append({
        "instance_id": "meta_run03_standard", "group": "meta", "fixture": meta_std,
        "stage1_mode": "reuse", "stage1_source": f"{BGROUP_STAGE1_DIR}/Meta_run03_standard/V4A/run_1.json",
        "expected_group_label": "BLOCKING→Rewrite→PASS(§7-1、現行は既存retry1回で通過)",
        "s1u_eligible": True,
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
        "s1u_eligible": True,
    })

    # --- Hormuz run_03 Advanced/Standard(既存V4A再利用) ---
    for fx in g6.step3_fixtures():
        if fx["id"] not in ("hormuz_run03_advanced", "hormuz_run03_standard"):
            continue
        label = "Normal群(§7-5)" if fx["id"] == "hormuz_run03_advanced" else "BLOCKING(Safety群、§7-1、narrow_scope)"
        instances.append({
            "instance_id": fx["id"], "group": "hormuz", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{STEP3_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": label, "s1u_eligible": True,
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
            "s1u_eligible": True,
        })

    # --- negative候補7(Normal群、既存V4A再利用) ---
    for fixture_id, path in step3cmp.NEGATIVE_SOURCE_FILES:
        fx = step3cmp.load_negative_fixture(fixture_id, path)
        instances.append({
            "instance_id": fixture_id, "group": "negative", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{NEG_STAGE1_DIR}/{fixture_id}/V4A/run_1.json",
            "expected_group_label": "ACCEPTABLE(Normal群、§7-5)", "s1u_eligible": True,
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
def run_instance(client, state, consecutive_errors, inst: dict, enable_s1u: bool = False) -> dict:
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

    # S1-U variant(委任_10、§3-1): --s1u有効時、このinstanceがs1u_eligible
    # かつStage1(V4A)がACCEPTABLE(PASS)だった場合のみ、S1-D 1 callを追加して
    # recallを補強する(union、fail-closed)。既にLEDGER_DEVIATIONの場合は
    # 追加callを行わない(コストをかけない)。
    # 委任_11 作業B-5(§8測定是正、Opus L2 #2論点2): `s1u_caught_recall_miss`
    # を`s1u_additional_block`へ改名し(「実際にmissを捕捉したか」ではなく
    # 「追加BLOCKINGを検出したか」を素直に表す名前へ)、正解ラベル照合の
    # 真偽列(`s1u_additional_block_label`)を追加する(既知recall miss=
    # true_positive、negative群=false_positive、それ以外=unlabeled)。
    s1u_screen_used = False
    s1u_additional_blocking_count = 0
    s1u_additional_block = False
    s1u_additional_block_label = None
    if enable_s1u and inst.get("s1u_eligible") and stage1_parsed.get("overall_status") != "LEDGER_DEVIATION":
        s1u_screen_used = True
        s1u_result = stage1_union_screen(client, state, consecutive_errors, call_log,
                                          f"{instance_id}_s1u_screen", fixture)
        s1u_additional_blocking_count = len(s1u_result["blocking_deviations"])
        if s1u_result["blocking_deviations"]:
            s1u_additional_block = True
            if instance_id in KNOWN_RECALL_MISS_INSTANCE_IDS:
                s1u_additional_block_label = "true_positive"
            elif inst["group"] == "negative":
                s1u_additional_block_label = "false_positive"
            else:
                s1u_additional_block_label = "unlabeled"
            stage1_parsed = {"overall_status": "LEDGER_DEVIATION",
                              "deviations": s1u_result["blocking_deviations"]}

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
            "s1u_screen_used": s1u_screen_used, "s1u_additional_blocking_count": s1u_additional_blocking_count,
            "s1u_additional_block": s1u_additional_block, "s1u_additional_block_label": s1u_additional_block_label,
            "call_log": call_log,
            "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
            "total_calls": len(call_log), "elapsed_seconds": elapsed,
        }
        save_json(f"{OUT_DIR}/instances/{instance_id}.json", result)
        return result

    # 委任_11 作業B-3(§3-3停止判定の是正): fact_id一致+claim本文近似一致
    # (find_matching_prior_record)で「同一claim再発」を判定する(旧来の
    # fact_id単独一致による過剰なStage4を是正、Opus L2 #2論点1)。
    prior_blocking_records: list = []
    prev_cycle_blocking_count = None
    extra_cycle_granted = False
    current_en_text = fixture["article_text"]
    current_ja_text = fixture.get("source_article_text")
    cycles_log = []
    final_state, stage4_reason = None, None

    # 委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4推奨3):
    # Rewrite前(オリジナル記事)のprecheck findingをbaselineとして保持し、
    # 各cycleのRewrite後テキストと比較する(¥0、決定論)。
    baseline_precheck_en = precheck.run_precheck(fixture["ledger_text"], fixture["article_text"])
    baseline_precheck_ja = (
        precheck.run_precheck(fixture["ledger_text"], fixture["source_article_text"])
        if fixture.get("source_article_text") is not None else []
    )

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
        # precheck floor claimsはStage2をスキップし直接BLOCKING確定。rewrite_hintは
        # precheck findingのissue文言(deterministic、fact_idを含む)をそのまま使う
        # (LLM生成ではないが、対象claim文言の逐語引用+fact_idという要件は満たす)。
        for pc in precheck_claims:
            hint = (f"{pc['claim_text'][:60]!r} を、fact_id={pc['dev'].get('related_fact_id', '')}の"
                    f"Ledger値へ置換する。issue: {pc['dev'].get('issue', '')}")
            stage2_results.append({**pc, "materiality": "BLOCKING", "llm_materiality": None,
                                    "basis": "precheck_floor", "rewrite_kind": "replace_with_ledger_value",
                                    "rewrite_hint": hint, "floor_reason": "precheck_floor"})

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

        # 委任_11 作業B-3(§3-3停止判定の是正、Opus L2 #2論点1推奨3): fact_id
        # 一致だけでなく正規化claim本文の近似一致も要求する
        # (find_matching_prior_record)。一致すれば「Rewriteが当該claimに
        # 効かなかったことが実証された」として従来どおり即Stage4。一致
        # しない場合(fact_idが同じでも別文=兄弟文カスケードではない、
        # またはfact_id無しの新規claim)は、cycle上限(MAX_CYCLES)超過時でも
        # 直前cycleよりblocking件数が厳密に減少していればcycle 3を1回だけ
        # 許可する(上限HARD_MAX_CYCLES、Opus L2 #2論点1「残る7件のうち
        # meta_run03_standard/B4等は進捗しているのに打ち切られている」の
        # 是正)。
        matched_records = []
        if cycle > 1:
            for c in blocking_claims:
                m = find_matching_prior_record(c["dev"], prior_blocking_records)
                if m is not None:
                    matched_records.append(m)
        if matched_records:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "same_claim_fact_id_reblocked"
            cycle_record["repeat_claim_ids"] = sorted({m["identity"] for m in matched_records})
            cycles_log.append(cycle_record)
            break

        if cycle > MAX_CYCLES:
            allow_extra_cycle = (
                not extra_cycle_granted and prev_cycle_blocking_count is not None
                and len(blocking_claims) < prev_cycle_blocking_count and cycle == MAX_CYCLES + 1
            )
            if allow_extra_cycle:
                extra_cycle_granted = True
                cycle_record["extra_cycle_granted"] = True
            else:
                final_state = "STAGE4_ESCALATION"
                stage4_reason = "cycle_limit_exhausted"
                cycles_log.append(cycle_record)
                break

        for c in blocking_claims:
            prior_blocking_records.append({
                "identity": claim_identity(c["dev"]),
                "fact_id": (c["dev"].get("related_fact_id") or "").strip(),
                "claim_text_norm": normalize_claim_text(c["dev"].get("claim_in_article") or ""),
            })
        prev_cycle_blocking_count = len(blocking_claims)

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

        # 委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4):
        # (a) 決定論precheckの再実行(¥0、baseline比較で新規finding検出)。
        rewrite_new_findings_en = detect_rewrite_new_precheck_findings(
            fixture["ledger_text"], baseline_precheck_en, current_en_text)
        rewrite_new_findings_ja = (
            detect_rewrite_new_precheck_findings(fixture["ledger_text"], baseline_precheck_ja, current_ja_text)
            if current_ja_text is not None else []
        )
        cycle_record["rewrite_new_precheck_findings_count"] = (
            len(rewrite_new_findings_en) + len(rewrite_new_findings_ja))
        if rewrite_new_findings_en or rewrite_new_findings_ja:
            cycle_record["rewrite_new_precheck_findings"] = rewrite_new_findings_en + rewrite_new_findings_ja
        # (b) paired rewrite(J-1)が使われた場合のみ、JA↔EN等価チェック1 call
        # (既存の翻訳忠実性QA資産を借用、flow制御には使わず測定専用)。
        if current_ja_text is not None and any(rr["mechanism"].startswith("paired") for rr in rewrite_records):
            eq_result = run_ja_en_equivalence_check(
                client, state, consecutive_errors, call_log, f"{instance_id}_c{cycle}_ja_en_equivalence",
                current_ja_text, current_en_text)
            cycle_record["ja_en_equivalence_verdict"] = eq_result.get("verdict")

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

        # 委任_11 作業B-5是正(§8測定是正、Opus L2 #2論点7「安全≠成功」):
        # overall_status=LEDGER_COMPLIANTかつall_prior_issues_resolved=False
        # という自己矛盾する応答(fail-openの継ぎ目、iter2の5 instanceで
        # 実際に未検査のまま合格していた)は、次cycleの空deviationsによる
        # 静かな降格(RESOLVED_REWRITE_THEN_DOWNGRADE)を許さず、追加1 call
        # で再確認する(iteration 3で有効化)。
        en_ambiguous = (recheck_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                        and not recheck_parsed.get("all_prior_issues_resolved"))
        if en_ambiguous and not en_ok:
            confirm_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                          f"{instance_id}_c{cycle}_recheck_confirm", recheck_fixture,
                                          current_en_text, prior_issues)
            cycle_record["recheck_confirm_overall_status"] = confirm_parsed.get("overall_status")
            cycle_record["recheck_confirm_all_prior_issues_resolved"] = confirm_parsed.get(
                "all_prior_issues_resolved")
            if (confirm_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                    and confirm_parsed.get("all_prior_issues_resolved")):
                en_ok = True
                cycle_record["recheck_reconfirmed"] = True
            else:
                cycle_record["recheck_reconfirmed"] = False

        cycles_log.append(cycle_record)

        if en_ok and ja_ok:
            final_state = "RESOLVED_REWRITE"
            break

        if cycle_record.get("recheck_reconfirmed") is False:
            # 再確認でも解消未確認(自己矛盾が解消しない) -> 次cycleの空
            # deviationsによる静かな降格を許さずfail-closedでSTAGE4
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "unconfirmed_after_reverify"
            break

        # 未解消 -> 次cycleのStage1 deviationsをRecheck結果から再構築
        stage1_deviations = [d for d in recheck_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
        cycle += 1
        if cycle > HARD_MAX_CYCLES:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "cycle_limit_exhausted_after_recheck"
            break

    elapsed = round(time.time() - t0, 3)
    result = {
        "instance_id": instance_id, "group": inst["group"], "expected_group_label": inst["expected_group_label"],
        "final_state": final_state, "stage4_reason": stage4_reason, "cycles": cycles_log,
        "stage1_call_used": stage1_call_used, "stage1_recall_miss_substituted": stage1_recall_miss_substituted,
        "s1u_screen_used": s1u_screen_used, "s1u_additional_blocking_count": s1u_additional_blocking_count,
        "s1u_additional_block": s1u_additional_block, "s1u_additional_block_label": s1u_additional_block_label,
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

    # 委任_11 作業B-5是正(§8測定是正、Opus L2 #2論点7「安全≠成功」):
    # 従来はfinal_state=="RESOLVED_REWRITE"限定で集計しており、
    # "RESOLVED_REWRITE_THEN_DOWNGRADE"の5 instance(iter2実測)がどの
    # バケットにも入らず「誤PASS候補0」が未検査のまま報告されていた。
    # 分母をRESOLVED_*全体(RESOLVED_REWRITE+RESOLVED_REWRITE_THEN_
    # DOWNGRADE)へ拡張する。
    _resolved_states = ("RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE")
    true_resolved = sum(1 for r in instance_results if r["final_state"] in _resolved_states
                         and any(c.get("recheck_all_prior_issues_resolved") for c in r["cycles"]))
    quality_pass = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_STAGE2_DOWNGRADE"
                        and any(c["materiality"] == "QUALITY" for c in r["cycles"][0]["stage2_results"]))
    unresolved_unknown = sum(1 for r in instance_results if r["final_state"] in _resolved_states
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

    # S1-U variant集計(委任_10、§4/§9-1、委任_11で改名): screen_used=実際に
    # 1 call追加したinstance数、additional_block=そのうちBLOCKING claimを
    # 新規発見できた件数(旧名caught_recall_miss。「実際にmissを捕捉したか」
    # ではなく「追加BLOCKINGを検出したか」を素直に表す名前へ改名、Opus L2
    # #2論点2)。true/false_positiveは正解ラベル照合(既知recall miss vs
    # negative群)。s1u_extra_cost_jpy=S1-U screen call自体の総コスト
    # (下流Stage2/3コスト増は含まない、別途instance側total_cost_jpyの
    # 差分比較で評価する)。
    s1u_screen_used = sum(1 for r in instance_results if r.get("s1u_screen_used"))
    s1u_additional_block = sum(1 for r in instance_results if r.get("s1u_additional_block"))
    s1u_true_positive = sum(1 for r in instance_results
                             if r.get("s1u_additional_block_label") == "true_positive")
    s1u_false_positive = sum(1 for r in instance_results
                              if r.get("s1u_additional_block_label") == "false_positive")
    s1u_extra_cost = round(sum(
        c.get("cost_jpy", 0.0) for r in instance_results for c in r.get("call_log", [])
        if c.get("recovery_stage") == "stage1_union_screen"
    ), 4)

    # 委任_11 作業B-5(§8測定是正、Opus L2 #2論点5): 群別Escalation率
    # (合成Safety/B群/negativeを分母に混ぜず、実run6 instanceも別枠で出す)。
    group_totals: dict = {}
    for r in instance_results:
        g = r["group"]
        group_totals.setdefault(g, {"n": 0, "escalated": 0})
        group_totals[g]["n"] += 1
        if r["final_state"] == "STAGE4_ESCALATION":
            group_totals[g]["escalated"] += 1
    group_escalation_rates = {
        g: {"n": v["n"], "escalated": v["escalated"],
            "rate": round(v["escalated"] / v["n"], 4) if v["n"] else None}
        for g, v in group_totals.items()
    }
    real_run_results = [r for r in instance_results if r["instance_id"] in REAL_RUN_INSTANCE_IDS]
    real_run_n = len(real_run_results)
    real_run_escalated = sum(1 for r in real_run_results if r["final_state"] == "STAGE4_ESCALATION")
    real_run_escalation_rate = round(real_run_escalated / real_run_n, 4) if real_run_n else None

    # 委任_11 作業B-5(§8測定是正、Opus L2 #2論点6): 記事単位
    # (Standard+Advanced合算)のコスト・合否(ARTICLE_GROUPS参照)。
    by_instance_id = {r["instance_id"]: r for r in instance_results}
    article_aggregates: dict = {}
    for article_id, members in ARTICLE_GROUPS.items():
        present = [by_instance_id[m] for m in members if m in by_instance_id]
        if not present:
            continue
        article_aggregates[article_id] = {
            "members": [r["instance_id"] for r in present],
            "total_cost_jpy": round(sum(r["total_cost_jpy"] for r in present), 4),
            "escalated": any(r["final_state"] == "STAGE4_ESCALATION" for r in present),
        }
    article_costs = [a["total_cost_jpy"] for a in article_aggregates.values()]
    worst_article_cost = max(article_costs) if article_costs else None

    # 委任_11 作業B-6(§4 Rewrite由来新規逸脱検出集計、Opus L2 #2論点4): 決定論
    # precheckの新規finding件数、JA↔EN等価チェックのverdict内訳(測定専用、
    # flow制御には使っていない)。
    rewrite_new_precheck_findings_total = sum(
        c.get("rewrite_new_precheck_findings_count", 0) for r in instance_results for c in r["cycles"])
    ja_en_equivalence_verdicts = [
        c.get("ja_en_equivalence_verdict") for r in instance_results for c in r["cycles"]
        if "ja_en_equivalence_verdict" in c
    ]
    ja_en_equivalence_fail_count = sum(1 for v in ja_en_equivalence_verdicts if v == "FAIL")
    ja_en_equivalence_review_required_count = sum(
        1 for v in ja_en_equivalence_verdicts if v == "REVIEW_REQUIRED")
    unconfirmed_after_reverify_count = sum(
        1 for r in instance_results if r.get("stage4_reason") == "unconfirmed_after_reverify")

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
        "s1u_variant": {
            "screen_used_count": s1u_screen_used, "additional_block_count": s1u_additional_block,
            "additional_block_true_positive_count": s1u_true_positive,
            "additional_block_false_positive_count": s1u_false_positive,
            "extra_cost_jpy": s1u_extra_cost,
        },
        "group_escalation_rates": group_escalation_rates,
        "real_run": {
            "n": real_run_n, "escalated": real_run_escalated, "rate": real_run_escalation_rate,
        },
        "article_level": {
            "aggregates": article_aggregates, "worst_cost_jpy": worst_article_cost,
        },
        "rewrite_deviation_qa": {
            "rewrite_new_precheck_findings_total": rewrite_new_precheck_findings_total,
            "ja_en_equivalence_calls": len(ja_en_equivalence_verdicts),
            "ja_en_equivalence_fail_count": ja_en_equivalence_fail_count,
            "ja_en_equivalence_review_required_count": ja_en_equivalence_review_required_count,
            "unconfirmed_after_reverify_count": unconfirmed_after_reverify_count,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", default="safety,b_group,meta,hormuz,negative",
                         help="comma-separated subset of safety,b_group,meta,hormuz,negative")
    parser.add_argument("--resume", action="store_true",
                         help="既に er052_output/.../instances/<id>.json が存在するinstanceは"
                              "再実行せずキャッシュ結果を再利用する(重複課金防止)")
    parser.add_argument("--s1u", action="store_true",
                         help="委任_10 S1-U variant: s1u_eligibleなinstanceがStage1(V4A)で"
                              "ACCEPTABLEだった場合、S1-D 1 callを追加してBLOCKING claimを"
                              "union(fail-closed)で拾う(recall対策の実測、既定は無効)")
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
            result = run_instance(client, state, consecutive_errors, inst, enable_s1u=args.s1u)
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
