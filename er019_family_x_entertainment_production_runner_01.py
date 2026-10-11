# ============================================================
# er019_family_x_entertainment_production_runner_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01
# ============================================================
# 目的: Family X/Entertainment系統の正式Production入口(新entry point)。
# ユーザー確定事項(2026-09-26)の正式フローを実装する:
#   Research -> Full Fact Ledger -> AIが中心Storylineを1つ決定
#   -> B3 4テストを全Factへ適用 -> Selected Fact Brief -> Writer
#   -> Original->R1->R2 -> Advanced -> Standard
#
# RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2(2026-10-10)での変更:
#   - Writer = 新Writer W-1(er053_family_x_factlock_ja_writer_01: Fact Lock R0->R1/R2、E案: B3/R0/R1/R2=gpt-6.1-sol)。
#     入口は注記済みB3の契約検証(er053_b3_annotation_contract_01、V1-V10、課金前fail-closed)のみ。
#     注記なしB3をWriterへ渡す経路・switchは存在しない。再利用分岐(ja_writer/revision2.md)でも
#     W-1来歴(chain_method=="W-1" かつ annotated_md_sha256が契約と一致)を確認し、違えばSTOP(U-1)。
#   - 旧Fact Checker(各段の台帳照合・指摘起点の再生成/STOP・JA差し戻し)は物理削除(案P)。
#   - Advanced英訳完了直後にAdvanced RF、Standard生成完了直後にStandard RF(Risk Flagger、非Blocking、
#     4条件逐次、er053_review_queue_01へLevel明示で保存)。RF呼出は cl.logging_context ブロックの外。
# 既存Production primitiveの再利用(Research/Ledger/Advanced/Standardは従来どおりefam primitive):
#   - Research/Ledger: er012_e_family_entertainment_two_level_runner_01.
#     run_researcher_for_topic/run_verification_for_topic
#   - Advanced/Standard/段落retry: 同runnerのrun_writer_stage()
#
# **Mandatory STOP(構造的)**: 本runnerはscaffold/tts/assemble/player関連の
# 関数を一切importしない。Standard生成までで必ず停止する
# (--stop-after既定"standard"、それ以降のstage自体がコード上存在しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py \
#       --theme "<Research用topic文字列>" --slug <slug> --out-dir <dir> \
#       [--source-note "<由来メモ>"] [--budget-jpy 150] \
#       [--stage research|ledger|storyline_b3|writer|advanced|standard|all] \
#       [--regenerate-stage storyline_b3|writer|advanced|standard] \
#       [--stop-after storyline_b3|writer|advanced|standard(既定)]
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as annot
import er053_cost_aggregate_01 as ca
import er053_family_x_factlock_ja_writer_01 as w1
import er053_review_queue_01 as rq
import er053_risk_flagger_production_01 as rf

MANAGEMENT_ID = "NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01"
RUNNER_TAG = "NEWS_FAMILY_X_B3_PRODUCTION_RUNNER_01"

STAGE_ORDER = ["research_ledger", "storyline_b3", "writer", "advanced", "standard"]
# CLI --stage/--stop-after 語彙("research"/"ledger"はどちらもresearch_ledger
# stageへ写像する。既存primitive[run_researcher_for_topic単独では検証まで
# 到達しないためLedgerとして未確定]がResearcherとVerificationを1組として
# 構築する設計であり、分割再実行はサポートしない、既存er012runnerと同じ
# 制約)。
STAGE_ALIASES = {
    "research": "research_ledger",
    "ledger": "research_ledger",
    "research_ledger": "research_ledger",
    "storyline_b3": "storyline_b3",
    "writer": "writer",
    "advanced": "advanced",
    "standard": "standard",
    "all": "all",
}


# ------------------------------------------------------------
# 共通ヘルパー(efamのものをそのまま再利用、独自実装しない)
# ------------------------------------------------------------
load_json = efam.load_json
save_json = efam.save_json
load_text = efam.load_text
save_text = efam.save_text
sha256_text = efam.sha256_text
sha256_file = efam.sha256_file


def self_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------------
# Stage 1: Research -> Full Fact Ledger(既存efam primitiveをそのまま呼ぶ、
# stage別costタグ付けのため保存ロジックのみここで踏襲する)
# ------------------------------------------------------------
def run_research_and_ledger(client, topic: str, ledger_dir: str) -> dict:
    if os.path.exists(f"{ledger_dir}/verified_fact_ledger.txt"):
        print(f"[B3-RUNNER][research_ledger] 既存Ledgerを再利用(既生成済み): {ledger_dir}")
        return {
            "ledger_text": load_text(f"{ledger_dir}/verified_fact_ledger.txt"),
            "reused": True,
        }

    os.makedirs(f"{ledger_dir}/audit", exist_ok=True)
    print(f"[B3-RUNNER][research] Researcher呼び出し開始(topic={topic[:60]!r}...)...")
    with cl.logging_context(RUNNER_TAG, "research"):
        research = efam.run_researcher_for_topic(client, topic)
    print(f"[B3-RUNNER][research] facts={len(research['parsed']['facts'])} "
          f"web_search_calls={research['search_usage']['web_search_call_count']}")
    save_json(f"{ledger_dir}/fact_ledger_draft.json", research["parsed"])
    save_json(f"{ledger_dir}/audit/researcher_full_record.json",
              {k: v for k, v in research.items() if k != "parsed"})

    print("[B3-RUNNER][ledger] Verification呼び出し開始...")
    with cl.logging_context(RUNNER_TAG, "ledger"):
        verification = efam.run_verification_for_topic(client, topic, research["parsed"])
    save_json(f"{ledger_dir}/fact_ledger_verification.json", verification["parsed"])
    save_json(f"{ledger_dir}/audit/verification_full_record.json",
              {k: v for k, v in verification.items() if k != "parsed"})

    ledger_text, verdict_counts, kept_facts = vfl01.build_verified_ledger_text(
        research["parsed"], verification["parsed"])
    save_text(f"{ledger_dir}/verified_fact_ledger.txt", ledger_text)
    save_json(f"{ledger_dir}/verdict_counts.json", verdict_counts)
    print(f"[B3-RUNNER][ledger] Ledger確定。verdict_counts={verdict_counts} "
          f"kept_facts={len(kept_facts)}")

    runtime_evidence = {
        "research": {
            "model_id_actual": research["model"], "response_id": research["response_id"],
            "web_search_call_count": research["search_usage"]["web_search_call_count"],
        },
        "ledger_verification": {
            "model_id_actual": verification["model"], "response_id": verification["response_id"],
        },
        "verdict_counts": verdict_counts, "kept_facts_count": len(kept_facts),
        "reused": False,
    }
    save_json(f"{ledger_dir}/runtime_evidence.json", runtime_evidence)
    return {"ledger_text": ledger_text, "reused": False, "runtime_evidence": runtime_evidence}


# ------------------------------------------------------------
# Stage 2: AI Storyline決定 + B3 4テスト(LLM 1 call)
# ------------------------------------------------------------
def run_storyline_b3(client, topic: str, ledger_text: str, out_dir: str) -> dict:
    stage_dir = f"{out_dir}/storyline_b3"
    os.makedirs(stage_dir, exist_ok=True)
    # FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01(2026-10-11、E案): B3はroutingキー
    # FAMILY_X_STORYLINE_B3(gpt-6.1-sol)。API call前にrequire_model、返却model不一致はSTOP(従来のvfl01.MODEL
    # 暗黙参照=Lunaは廃止)。effortは従来どおりvfl01.REASONING_EFFORT(high、不変)。
    b3_model = routing.require_model("FAMILY_X_STORYLINE_B3", routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"])
    selection = b3.run_storyline_b3_selection(
        client, topic, ledger_text, model=b3_model, effort=vfl01.REASONING_EFFORT)
    if not str(selection.get("model") or "").startswith(b3_model):
        raise RuntimeError(f"[STOP] B3段の返却modelが{b3_model}で始まらない: {selection.get('model')!r}")

    ledger_fact_ids = selection["ledger_fact_ids"]
    full_ledger_record = b3.build_full_ledger_record(topic, ledger_text, ledger_fact_ids)
    save_json(f"{stage_dir}/full_ledger.json", full_ledger_record)

    brief_md = b3.build_selected_brief_markdown(selection)
    save_text(f"{stage_dir}/selected_brief.md", brief_md)

    fact_selection_evidence = {
        "selected_storyline": selection["parsed"]["selected_storyline"],
        "full_ledger_fact_ids": ledger_fact_ids,
        "fact_tests": selection["parsed"]["fact_tests"],
        "selected_fact_ids": selection["parsed"]["selected_fact_ids"],
        "selected_fact_brief_text": selection["parsed"]["selected_fact_brief"],
        "recheck_note": selection["parsed"]["recheck_note"],
        "soft_warnings": selection["soft_warnings"],
    }
    save_json(f"{stage_dir}/fact_selection_evidence.json", fact_selection_evidence)

    runtime_evidence = {
        "model_id_actual": selection["model"], "response_id": selection["response_id"],
        "latency_seconds": selection["latency_seconds"], "attempts": selection["attempts"],
        "retried": selection["retried"], "prompt_shas": selection["prompt_shas"],
        "attempts_log": selection["attempts_log"],
    }
    save_json(f"{stage_dir}/runtime_evidence.json", runtime_evidence)
    return {
        "selected_storyline": selection["parsed"]["selected_storyline"],
        "selected_fact_brief_text": selection["parsed"]["selected_fact_brief"],
        "selected_brief_markdown": brief_md,
        "fact_selection_evidence": fact_selection_evidence,
        "runtime_evidence": runtime_evidence,
    }


# ------------------------------------------------------------
# Stage 3: JA Writer = 新Writer W-1(注記済みB3契約検証 -> R0[Fact Lock] -> R1/R2、全段gpt-6.1-sol)
# ------------------------------------------------------------
class LegacyWriterProvenanceStop(RuntimeError):
    """U-1: W-1来歴のない(または契約と不一致の)JA記事を通常Production経路で再利用しようとした場合のSTOP。"""


def run_annotation_producer(out_dir: str) -> dict:
    """C4: 正式 annotated B3 producer(D-det v2 + 決定論assembler、LLM call 0)。storyline_b3 の確定直後に必ず呼ぶ
    (初回/--regenerate-stage storyline_b3/resume/既存B3再利用のすべての分岐。決定論・冪等)。
    注記なしB3へのfallbackは無い: 失敗は AnnotationProducerError(課金前STOP、技術QA)で伝播し、Writerへ進まない。
    出力は契約検証(contract.validate_annotated_b3、W-1入口T-19)の対象。runtime evidenceは storyline_b3/audit/annotation_producer_evidence.json。"""
    result = annot.produce_annotated_b3(out_dir)
    save_json(f"{out_dir}/storyline_b3/audit/annotation_producer_evidence.json", {
        "producer": result["producer"], "rule_version": result["rule_version"], "rules_sha256": result["rules_sha256"],
        "rules_sha_table": annot.rules_sha_table(), "input_shas": result["input_shas"],
        "annotated_md_sha256": result["annotated_md_sha256"], "writer_constraints_sha256": result["writer_constraints_sha256"],
        "n_facts": result["n_facts"], "llm_calls": 0,
        "internal_checks": {k: v["status"] for k, v in result["manifest"]["internal_checks"].items()},
        "producer_module_sha256": self_sha256(annot.__file__)})
    print(f"[B3-RUNNER][annotation] producer={result['producer']} rules_sha={result['rules_sha256'][:12]} "
          f"facts={result['n_facts']} annotated_sha={result['annotated_md_sha256'][:12]}(LLM 0 call)")
    return result


def run_ja_writer(client, out_dir: str, budget_jpy: float) -> dict:
    """W-1を実行する。入力は out_dir/storyline_b3 の注記済みB3 artifact(契約検証V1-V10、課金前fail-closed)
    のみで、注記済みmdを parse_brief_md した結果がR0 Promptの素材になる。
    (旧Production呼出のように fact_selection_evidence.json['selected_fact_brief_text'] を渡す経路は無い。)
    予算ガードとして efam.assert_budget_ok をR0前・R1前・R1/R2間・R2再実行前後に呼ぶ。"""
    try:
        result = w1.run_w1_writer(
            out_dir, client=client,
            budget_check=lambda: efam.assert_budget_ok(out_dir, budget_jpy, "w1 writer"))
    except w1.JASymbolCheckStopError as exc:
        # JA_SYMBOL_CHECK_STOP(技術QA、記号Validator): rejected本文はW-1側がja_writer/auditへ保存済み。
        raise RuntimeError(str(exc)) from exc
    return {"ja_text": result["ja_text"], "title": result["title"], "runtime_evidence": result["runtime_evidence"]}


# ------------------------------------------------------------
# U-1 限定受入(案b): 承認済み品質マスター受入(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_05、2026-10-11)
# ユーザー正式決定①(案b、APPROVED_FOR_PRODUCTION)+Opus条件Aレビュー(GO with required fixes)に基づく。
# 設計: er053_output/coffee_new_tone_e2e_01/U1_APPROVED_MASTER_ACCEPTANCE_DESIGN_01.md
# 既定(未指定)=従来のU-1と完全同一。明示opt-in `--approved-quality-master <meta>` のときだけ、
# chain_method=="MAQ_TRIAL_W-1" の「人間承認済み品質マスター」の無改変複製を、下記a〜g全件一致で受理する。
# 環境変数・設定ファイル・既定ONでの有効化経路は無い。受理記録(acceptance.jsonl)は判定の入力にしない(毎回フル再検証)。
# ------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
APPROVED_MASTERS_REL = "docs/quality/ja_quality_masters"
APPROVED_MASTER_STATUS = "HUMAN_APPROVED_QUALITY_MASTER"
APPROVED_CHAIN_METHODS = frozenset({"MAQ_TRIAL_W-1"})      # 完全一致のみ(startswith/部分一致/正規表現/大小無視は禁止)
APPROVED_MASTER_DECISION_REF = "FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 ユーザー決定①(案b)2026-10-11"
ACCEPTANCE_RECORD_REL = "ja_writer/approved_master_acceptance.jsonl"
RUNDIR_BUILD_MANIFEST = "approved_master_rundir_build.json"
# pinned registry(g、Opus A1-2): 登録の追加=コードcommit+レビュー+ユーザー承認が必要。値の算出手順は設計書「8節」。
APPROVED_QUALITY_MASTERS = {
    "coffee_prices": {
        "master_sha256_lf": "742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a",
        "chain_method": "MAQ_TRIAL_W-1",
        "ledger_sha256": "e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b",
        "selected_brief_sha256_raw": "5acded774f71033ffba90ca7cb29577d3aca1094458e9f7be9adcd757c5d729b",
        "runtime_evidence_sha256_raw": "241c0401a8c74a416e75c31c7f3ae3303ada607ffead8b0057a3ec4b9edabeae",
        "decision_ref": APPROVED_MASTER_DECISION_REF,
    },
}


class ApprovedMasterAcceptanceStop(LegacyWriterProvenanceStop):
    """案b(承認済み品質マスター受入)の受理条件不一致。LegacyWriterProvenanceStopのサブクラス(既存assertRaisesと整合)。
    メッセージ先頭に条件ID(a/b1/b2/b3/b4/c/d/e/f/g/g2/pre.*)を付ける。課金前・fail-closed。"""


def _amq_stop(cond: str, detail: str):
    raise ApprovedMasterAcceptanceStop(f"[STOP] U-1 APPROVED_MASTER_REJECTED: {cond}={detail}")


def _raw_sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _read_bytes_once(path: str, cond: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as exc:
        _amq_stop(cond, f"unreadable {os.path.basename(path)} ({type(exc).__name__})")


def resolve_approved_master_meta(meta_path, slug) -> str:
    """e: metaパスを repo root 配下 docs/quality/ja_quality_masters/<slug>/E_master_meta.json のみに限定(厳密一致)。
    UNC・`..`・symlink/junction(realpath前後で変化)・別repo・run dir内は拒否。戻り値=検証済み絶対パス。"""
    if (not isinstance(meta_path, str) or not meta_path.strip()
            or not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9_]+", slug)):
        _amq_stop("e", f"invalid meta path/slug ({meta_path!r}, {slug!r})")
    if meta_path.startswith("\\\\") or meta_path.startswith("//"):
        _amq_stop("e", f"UNC path rejected: {meta_path!r}")
    if ".." in re.split(r"[\\/]", meta_path):
        _amq_stop("e", f"'..' in path rejected: {meta_path!r}")
    absp = os.path.abspath(meta_path)
    real = os.path.realpath(absp)
    if os.path.normcase(real) != os.path.normcase(absp) or os.path.islink(absp):
        _amq_stop("e", f"symlink/junction/alias rejected (realpath differs): {meta_path!r}")
    root_real = os.path.realpath(REPO_ROOT)
    expected = os.path.join(root_real, *APPROVED_MASTERS_REL.split("/"), slug, "E_master_meta.json")
    try:
        inside = os.path.commonpath([os.path.normcase(real), os.path.normcase(root_real)]) == os.path.normcase(root_real)
    except ValueError:
        inside = False
    if not inside or os.path.normcase(real) != os.path.normcase(expected):
        _amq_stop("e", f"meta path must be exactly <repo>/{APPROVED_MASTERS_REL}/{slug}/E_master_meta.json (got {real!r})")
    return real


def verify_approved_quality_master(out_dir: str, meta_path, slug) -> dict:
    """案bの受理条件a〜gを全件検証する(API呼出0・書込なし。contractが違反時にcontract_violation.jsonを書く従来挙動を除く)。
    revision2.md / runtime_evidence.json は1回だけbytesで読み、そのbytesでsha/CR検査し、同じbytesをdecodeして返す(TOCTOU対策)。
    不一致は ApprovedMasterAcceptanceStop(条件ID付き)。戻り値=受理記録用の判定結果(ja_textを含む)。"""
    real_meta = resolve_approved_master_meta(meta_path, slug)                                    # e
    meta_raw = _read_bytes_once(real_meta, "e")
    try:
        meta = json.loads(meta_raw.decode("utf-8"))
        if not isinstance(meta, dict):
            raise ValueError("not an object")
    except ValueError as exc:
        _amq_stop("e", f"meta unreadable/invalid json: {exc}")
    if meta.get("status") != APPROVED_MASTER_STATUS or meta.get("family") != "X":                  # a
        _amq_stop("a", f"status={meta.get('status')!r} family={meta.get('family')!r} "
                       f"(need {APPROVED_MASTER_STATUS!r} / 'X')")
    path_slug = os.path.basename(os.path.dirname(real_meta))
    if meta.get("slug") != slug or path_slug != slug:                                              # f
        _amq_stop("f", f"meta.slug={meta.get('slug')!r} path slug={path_slug!r} --slug={slug!r}")
    master_sha = meta.get("saved_sha256")
    if (not isinstance(master_sha, str) or meta.get("source_sha256") != master_sha
            or meta.get("byte_identical_to_source") is not True):                                  # b1
        _amq_stop("b1", f"source_sha256={meta.get('source_sha256')!r} saved_sha256={master_sha!r} "
                        f"byte_identical_to_source={meta.get('byte_identical_to_source')!r}")
    expected_saved = f"{APPROVED_MASTERS_REL}/{slug}/E_master_r2.md"
    master_path = os.path.join(os.path.dirname(real_meta), "E_master_r2.md")
    if meta.get("saved_file") != expected_saved:
        _amq_stop("b2", f"meta.saved_file={meta.get('saved_file')!r} != {expected_saved!r}")
    master_raw = _read_bytes_once(master_path, "b2")
    master_lf_sha = _raw_sha(master_raw.replace(b"\r\n", b"\n"))
    if master_lf_sha != master_sha:                                                                # b2(CRLF正規化後)
        _amq_stop("b2", f"master body LF-normalized sha {master_lf_sha} != meta {master_sha}")
    ev_raw = _read_bytes_once(f"{out_dir}/ja_writer/runtime_evidence.json", "b3")                  # 1回だけ読む
    rev_raw = _read_bytes_once(f"{out_dir}/ja_writer/revision2.md", "b4")                          # 1回だけ読む
    try:
        ev = json.loads(ev_raw.decode("utf-8"))
        if not isinstance(ev, dict):
            raise ValueError("not an object")
    except ValueError as exc:
        _amq_stop("b3", f"runtime_evidence.json unreadable/invalid: {exc}")
    if ev.get("ja_text_sha256") != master_sha:                                                     # b3
        _amq_stop("b3", f"evidence.ja_text_sha256={ev.get('ja_text_sha256')!r} != {master_sha}")
    if b"\r" in rev_raw:                                                                           # b4(CR混入=LF原本複製でない)
        _amq_stop("b4", "revision2.md contains CR (CRLF-converted copy rejected)")
    rev_sha = _raw_sha(rev_raw)
    if rev_sha != master_sha:
        _amq_stop("b4", f"revision2.md raw sha {rev_sha} != {master_sha}")
    try:
        ja_text = rev_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        _amq_stop("b4", f"revision2.md not utf-8: {exc}")
    chain = ev.get("chain_method")
    if not isinstance(chain, str) or chain not in APPROVED_CHAIN_METHODS:                          # d(完全一致の集合照合)
        _amq_stop("d", f"chain_method={chain!r} not in allowlist {sorted(APPROVED_CHAIN_METHODS)} (exact match only)")
    pin = APPROVED_QUALITY_MASTERS.get(slug)                                                       # g(pinned registry)
    if pin is None:
        _amq_stop("g", f"slug {slug!r} is not registered in APPROVED_QUALITY_MASTERS")
    ledger_raw = _read_bytes_once(f"{out_dir}/research_ledger/verified_fact_ledger.txt", "g")
    brief_raw = _read_bytes_once(f"{out_dir}/storyline_b3/selected_brief.md", "g")
    actual = {"master_sha256_lf": master_lf_sha, "chain_method": chain, "ledger_sha256": _raw_sha(ledger_raw),
              "selected_brief_sha256_raw": _raw_sha(brief_raw), "runtime_evidence_sha256_raw": _raw_sha(ev_raw)}
    for k, got in actual.items():
        if pin.get(k) != got:
            _amq_stop("g", f"registry.{k}={pin.get(k)!r} != actual {got!r}")
    fl = meta.get("fact_ledger") if isinstance(meta.get("fact_ledger"), dict) else {}              # g2(meta<->sidecar<->ledger)
    if fl.get("sha256") != actual["ledger_sha256"]:
        _amq_stop("g2", f"meta.fact_ledger.sha256={fl.get('sha256')!r} != run dir ledger {actual['ledger_sha256']}")
    sidecar_raw = _read_bytes_once(f"{out_dir}/storyline_b3/annotation.json", "g2")
    try:
        sc = json.loads(sidecar_raw.decode("utf-8"))
        sidecar_ids = sorted({i for fct in sc["facts"] for i in fct["ledger_ids"]})
    except (ValueError, KeyError, TypeError) as exc:
        _amq_stop("g2", f"annotation.json sidecar unreadable: {type(exc).__name__}: {exc}")
    if not isinstance(meta.get("selected_fact_ids"), list) or sorted(meta["selected_fact_ids"]) != sidecar_ids:
        _amq_stop("g2", f"meta.selected_fact_ids={meta.get('selected_fact_ids')!r} != sidecar ledger_ids {sidecar_ids}")
    annotated = contract.validate_annotated_b3(out_dir)                                            # c(従来どおり必ず実行: V1〜V10)
    if ev.get("annotated_md_sha256") != annotated.annotated_md_sha256:
        _amq_stop("c", f"PROVENANCE_MISMATCH evidence.annotated_md_sha256={ev.get('annotated_md_sha256')} "
                       f"!= contract {annotated.annotated_md_sha256}")
    return {"ja_text": ja_text, "slug": slug, "meta": meta, "meta_path_real": real_meta, "meta_sha256_raw": _raw_sha(meta_raw),
            "master_sha256_lf": master_lf_sha, "master_body_raw_sha256_worktree": _raw_sha(master_raw),
            "evidence_ja_text_sha256": ev.get("ja_text_sha256"), "revision2_raw_sha256": rev_sha,
            "chain_method_observed": chain, "annotated_md_sha256": annotated.annotated_md_sha256,
            "actual_pinned": actual, "registry_snapshot": dict(pin),
            "checks": {k: "PASS" for k in ("a", "b1", "b2", "b3", "b4", "c", "d", "e", "f", "g", "g2")}}


def precheck_approved_quality_master(args):
    """課金前の事前検証(Opus A1-1): main の引数解析直後(get_client・Research・B3実行より前)に呼ぶ。
    opt-in未指定(None)なら何もせずNone(従来動作)。併用NGの組合せ・revision2.md欠落・受理条件不一致はSTOP。"""
    meta_path = getattr(args, "approved_quality_master", None)
    if meta_path is None:
        return None
    if getattr(args, "stage", "all") in ("research", "ledger", "storyline_b3", "writer"):
        _amq_stop("pre.stage", f"--approved-quality-master cannot be combined with --stage {args.stage} (JA writer reuse path only)")
    if getattr(args, "regenerate_stage", None) in ("writer", "storyline_b3"):
        _amq_stop("pre.regenerate", f"cannot be combined with --regenerate-stage {args.regenerate_stage}")
    if getattr(args, "stop_after", "standard") == "storyline_b3":
        _amq_stop("pre.stop_after", "cannot be combined with --stop-after storyline_b3 (opt-in would be silently ignored)")
    if not os.path.isfile(f"{args.out_dir}/ja_writer/revision2.md"):
        _amq_stop("pre.revision2", "ja_writer/revision2.md is missing in the run dir "
                                   "(the Writer would regenerate; opt-in is reuse only)")
    res = verify_approved_quality_master(args.out_dir, meta_path, args.slug)
    print(f"[B3-RUNNER][U-1] APPROVED_QUALITY_MASTER precheck OK: slug={res['slug']} "
          f"master_sha={res['master_sha256_lf'][:12]} chain_method={res['chain_method_observed']!r}"
          "(課金前。受理記録は再利用時にacceptance.jsonlへ追記)")
    return res


def approved_ja_source_tag(res: dict) -> str:
    return f"approved_quality_master:{res['slug']}@{res['master_sha256_lf'][:12]}"


def write_ja_source_audit(out_dir: str, level: str, tag: str) -> None:
    """b1b/a2 の audit に ja_source を1行(1ファイル)残す(新規ファイルのみ、既存audit構造は変更しない)。記録専用。"""
    os.makedirs(f"{out_dir}/{level}/audit", exist_ok=True)
    save_json(f"{out_dir}/{level}/audit/ja_source.json", {"ja_source": tag})


def _runner_git_head():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10)
        return (r.stdout.strip() or None) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def append_approved_master_acceptance_record(out_dir: str, res: dict, cli: dict) -> dict:
    """受理記録を ja_writer/approved_master_acceptance.jsonl へ追記のみ(1実行1行、既存行・runtime_evidence.jsonは不変)。
    判定の入力には使わない(記録専用)。複製元dir・複製ファイルshaは builder が書いた approved_master_rundir_build.json を
    情報として転記し、現在の生shaも併記する(不一致でもここでは判定しない)。"""
    build = None
    bpath = f"{out_dir}/{RUNDIR_BUILD_MANIFEST}"
    if os.path.isfile(bpath):
        try:
            with open(bpath, "rb") as f:
                build = json.loads(f.read().decode("utf-8"))
        except ValueError:
            build = {"unreadable": True}
    current = {}
    if isinstance(build, dict) and isinstance(build.get("files"), dict):
        for rel in build["files"]:
            p = f"{out_dir}/{rel}"
            current[rel] = _raw_sha(open(p, "rb").read()) if os.path.isfile(p) else None
    meta = res["meta"]
    try:
        meta_rel = os.path.relpath(res["meta_path_real"], os.path.realpath(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        meta_rel = res["meta_path_real"]
    record = {
        "schema_version": 1, "accepted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "decision_ref": APPROVED_MASTER_DECISION_REF, "runner": "er019_family_x_entertainment_production_runner_01.py",
        "runner_version": self_sha256(__file__), "runner_git_head": _runner_git_head(),
        "meta_path": meta_rel, "meta_sha256_raw": res["meta_sha256_raw"], "slug": res["slug"],
        "shas": {"master_sha256_lf": res["master_sha256_lf"],
                 "master_body_raw_sha256_worktree": res["master_body_raw_sha256_worktree"],
                 "evidence_ja_text_sha256": res["evidence_ja_text_sha256"], "revision2_raw_sha256": res["revision2_raw_sha256"],
                 "annotated_md_sha256": res["annotated_md_sha256"], **res["actual_pinned"]},
        "chain_method_observed": res["chain_method_observed"], "chain_method_allowlist": sorted(APPROVED_CHAIN_METHODS),
        "checks": res["checks"], "registry_snapshot": res["registry_snapshot"],
        "meta_user_eval_date": meta.get("user_eval_date"), "meta_note": meta.get("note"),
        "cli": cli, "rundir_build": build, "rundir_current_raw_shas": current,
    }
    os.makedirs(f"{out_dir}/ja_writer", exist_ok=True)
    with open(f"{out_dir}/{ACCEPTANCE_RECORD_REL}", "ab") as f:      # 追記のみ
        f.write((json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    return record


def load_reused_ja_text(out_dir: str, approved_quality_master=None, slug=None, cli_args=None) -> str:
    """JA記事(ja_writer/revision2.md)の再利用(U-1/穴B): runtime_evidence.json の chain_method=="W-1" かつ
    annotated_md_sha256 が現在の注記済みB3契約(validate_annotated_b3)と一致する場合のみ再利用する。
    来歴なし(旧Writer記事)・不一致(注記がstale/差し替え)はSTOP(旧記事の再生成は旧経路の worktree で行う)。
    案b(2026-10-11): approved_quality_master(metaパス)を明示したときだけ、承認済み品質マスターの無改変複製を
    受理条件a〜g全件一致で受理(verify_approved_quality_master)し、受理記録をacceptance.jsonlへ追記する。既定None=従来動作。"""
    if approved_quality_master is not None:
        res = verify_approved_quality_master(out_dir, approved_quality_master, slug)   # 毎回フル再検証(記録は入力にしない)
        append_approved_master_acceptance_record(out_dir, res, dict(cli_args or {}))
        print(f"[B3-RUNNER][U-1] APPROVED_QUALITY_MASTER accepted: slug={res['slug']} master_sha={res['master_sha256_lf'][:12]} "
              f"chain_method={res['chain_method_observed']!r} decision_ref={APPROVED_MASTER_DECISION_REF}")
        return res["ja_text"]
    ev_path = f"{out_dir}/ja_writer/runtime_evidence.json"
    if not os.path.exists(ev_path):
        raise LegacyWriterProvenanceStop(
            "[STOP] U-1 LEGACY_WRITER_PROVENANCE: ja_writer/runtime_evidence.json がありません"
            "(W-1来歴なしの旧Writer記事)。通常のProduction経路では再利用・再生成できません。"
            "旧記事の再生成はC2適用前のcommitのworktreeで行ってください。")
    ev = load_json(ev_path)
    if ev.get("chain_method") != w1.CHAIN_METHOD:
        raise LegacyWriterProvenanceStop(
            f"[STOP] U-1 LEGACY_WRITER_PROVENANCE: chain_method={ev.get('chain_method')!r} は "
            f"{w1.CHAIN_METHOD!r}(新Writer W-1)ではありません。")
    annotated = contract.validate_annotated_b3(out_dir)   # 契約違反はAnnotatedB3ContractViolation(STOP)
    if ev.get("annotated_md_sha256") != annotated.annotated_md_sha256:
        raise LegacyWriterProvenanceStop(
            "[STOP] U-1 PROVENANCE_MISMATCH: ja_writer/runtime_evidence.json の annotated_md_sha256 が"
            "現在の注記済みB3(契約検証済み)と一致しません。JA記事は別の注記版から生成されたものです。"
            "B3を再生成した場合は、続けて `--regenerate-stage writer` を実行してJA記事を新しい注記版から作り直してください"
            "(下流の自動再生成は行いません=安全側)。"
            f"(evidence={ev.get('annotated_md_sha256')}, contract={annotated.annotated_md_sha256})")
    return load_text(f"{out_dir}/ja_writer/revision2.md")


# ------------------------------------------------------------
# Post-EN Risk Flagger(非Blocking)+ Review Queue保存
# 呼出は cl.logging_context ブロックの外(RF moduleが条件ごとに自前でstage tagのcontextを張る)。
# ------------------------------------------------------------
LEVEL_DIR = {"b1b": "b1b", "a2": "a2"}      # article_level -> out_dir配下のdir(b1b=Advanced, a2=Standard)


def _annotation_producer(out_dir: str):
    """記録専用(分岐に使わない): W-1 evidenceに残った注記manifestのproducer。"""
    try:
        return load_json(f"{out_dir}/ja_writer/runtime_evidence.json").get("annotation_manifest_producer")
    except (OSError, ValueError):
        return None


def run_post_en_risk_flag(out_dir: str, level: str, budget_jpy: float, run_label: str | None = None) -> dict:
    """完成した英語記事(level: b1b=Advanced / a2=Standard)に対し、完全台帳でRF 4条件を逐次実行し、
    Review Queueへ保存する。**非Blocking**: RF_UNAVAILABLE/PARTIAL/Queue保存失敗でも例外にせず次工程へ進む。
    例外として伝播するのは (1)予算超過STOP(rf.BudgetCheckStop: 既存安全装置を回避しない)
    (2)記事sha変化(rf.ArticleModifiedError: RFは記事を書き換えない契約の違反)のみ。"""
    assert level in LEVEL_DIR, level
    article_path = f"{out_dir}/{LEVEL_DIR[level]}/article.md"
    ledger_path = f"{out_dir}/research_ledger/verified_fact_ledger.txt"
    article_id = rq.derive_article_id(out_dir)
    sha_before = hashlib.sha256(open(article_path, "rb").read()).hexdigest()
    print(f"[B3-RUNNER][risk_flag/{level}] Risk Flagger開始(非Blocking、4条件逐次)...")
    try:
        result = rf.run_risk_flagger(
            article_path=article_path, ledger_path=ledger_path, article_id=article_id, article_level=level,
            out_dir=out_dir, producer=_annotation_producer(out_dir), run_label=run_label,
            budget_check=lambda: efam.assert_budget_ok(out_dir, budget_jpy, f"risk_flag {level}"))
    except (rf.BudgetCheckStop, rf.ArticleModifiedError):
        raise
    except Exception as exc:  # noqa: BLE001 - 非Blocking: 想定外もRF_UNAVAILABLEとして可視化し次工程へ進む
        print(f"[WARN][RF] {level}: 想定外の例外 {type(exc).__name__}: {str(exc)[:200]}"
              "(非Blocking: 次工程へ進みます)")
        return {"status": "RF_UNAVAILABLE", "reason": f"runner_wrapper_exception: {type(exc).__name__}",
                "queue": None}
    saved = rq.save_queue(result, out_dir=out_dir)
    sha_after = hashlib.sha256(open(article_path, "rb").read()).hexdigest()
    if sha_after != sha_before:
        raise rf.ArticleModifiedError(f"article sha changed across RF+Queue: {sha_before} -> {sha_after}")
    print(f"[B3-RUNNER][risk_flag/{level}] status={result['status']} issues={len(result['issues'])} "
          f"queue_saved={saved.get('saved')}")
    return {"status": result["status"], "reason": result.get("reason"), "queue": saved,
            "issue_count": len(result["issues"]), "rf_run_id": result["rf_run_id"]}


# ------------------------------------------------------------
# コスト集計(stage別、web_search_call費用も含める。
# efam.compute_cost_jpy_so_far()はtoken費用のみでweb_search_call費用を
# 含まないため[既存の既知の粒度差、Production budget guardは
# efam.assert_budget_ok経由でそのまま流用し変更しない]、本runnerの
# cost.json用に別途web_search_call費用込みで集計する)。
# ------------------------------------------------------------
def compute_stage_cost_breakdown(cost_log_path: str) -> dict:
    if not os.path.exists(cost_log_path):
        return {"by_stage": {}, "total_jpy": 0.0}
    price = efam._load_pricing()
    by_stage = {}
    total_usd = 0.0
    with open(cost_log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            stage = rec.get("stage") or "UNTAGGED"
            usd = 0.0
            if provider == "openai" and model:
                in_tok = rec.get("input_tokens") or 0
                out_tok = rec.get("output_tokens") or 0
                # 単価未登録は efam._load_pricing() の price() が
                # PricingNotFoundError(fail-closed)を送出する(WIRING-01 Phase 1, M1)
                usd += in_tok * price("openai", model, "input_tokens") / 1e6
                usd += out_tok * price("openai", model, "output_tokens") / 1e6
                usd += efam.web_search_call_usd(rec, price)
            total_usd += usd
            by_stage[stage] = by_stage.get(stage, 0.0) + usd
    usd_jpy = efam.USD_JPY
    return {
        "by_stage_jpy": {k: round(v * usd_jpy, 3) for k, v in by_stage.items()},
        "total_jpy": round(total_usd * usd_jpy, 3),
    }


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", required=True,
                         help="Research用topic文字列(記事テーマの説明)。")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--source-note", default="",
                         help="由来メモ(evidenceとして記録のみ、Research promptには使わない)。")
    parser.add_argument("--run-label", default="",
                         help="実行ラベル(記録専用の自由文字列。制御には一切影響しない。Review Queueへ記録される)。")
    parser.add_argument("--budget-jpy", type=float, default=150.0)
    parser.add_argument("--stage", default="all",
                         choices=("research", "ledger", "storyline_b3", "writer",
                                  "advanced", "standard", "all"))
    parser.add_argument("--regenerate-stage", default=None,
                         choices=("storyline_b3", "writer", "advanced", "standard"))
    parser.add_argument("--stop-after", default="standard",
                         choices=("storyline_b3", "writer", "advanced", "standard"))
    parser.add_argument("--approved-quality-master", default=None,
                         help="案b(U-1限定受入): 人間承認済み品質マスターのmetaパス(<repo>/docs/quality/ja_quality_masters/<slug>/E_master_meta.json)。"
                              "指定時のみ、無改変複製のJA記事(chain_method=MAQ_TRIAL_W-1)を受理条件a〜g全件一致で再利用する。"
                              "未指定=従来のU-1(既定)。--stage research/ledger/storyline_b3/writer・--regenerate-stage writer/storyline_b3と併用不可。")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    # 案b: 課金前の事前検証(get_client・Research・B3実行より前、受理条件a〜g全件+併用NG+revision2.md存在)。未指定ならNone。
    approved_res = precheck_approved_quality_master(args)
    ja_source_tag = approved_ja_source_tag(approved_res) if approved_res else None

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    cl.install(f"{out_dir}/raw_usage_log.jsonl")

    save_json(f"{out_dir}/entry_point.json", {
        "runner": "er019_family_x_entertainment_production_runner_01.py",
        "management_id": MANAGEMENT_ID,
        "runner_sha256": self_sha256(__file__),
        "b3_module_sha256": self_sha256(b3.__file__),
        "ja_writer_module_sha256": self_sha256(w1.__file__),
        "annotation_contract_module_sha256": self_sha256(contract.__file__),
        "annotation_producer_module_sha256": self_sha256(annot.__file__),
        "risk_flagger_module_sha256": self_sha256(rf.__file__),
        "review_queue_module_sha256": self_sha256(rq.__file__),
        "args": vars(args),
        **({"approved_quality_master": {"meta_path": approved_res["meta_path_real"], "meta_sha256_raw": approved_res["meta_sha256_raw"],
                                         "slug": approved_res["slug"], "master_sha256_lf": approved_res["master_sha256_lf"],
                                         "ja_source": ja_source_tag}} if approved_res else {}),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    theme = {"theme_id": args.slug, "topic": args.theme, "out_dir": out_dir,
              "ledger_path": f"{out_dir}/research_ledger/verified_fact_ledger.txt"}

    client = vfl01.get_client()
    stage = STAGE_ALIASES[args.stage]

    ledger_dir = f"{out_dir}/research_ledger"
    ledger_result = run_research_and_ledger(client, args.theme, ledger_dir)
    ledger_text = ledger_result["ledger_text"]
    efam.assert_budget_ok(out_dir, args.budget_jpy, "after research_ledger")
    if stage == "research_ledger":
        print("[B3-RUNNER] stage=research/ledger 完了。--stage storyline_b3以降は未実行。")
        _write_cost_json(out_dir, ja_source=ja_source_tag)
        return

    storyline_dir = f"{out_dir}/storyline_b3"
    need_storyline = (stage in ("storyline_b3", "writer", "advanced", "standard", "all")
                       or args.regenerate_stage == "storyline_b3")
    if need_storyline:
        if (os.path.exists(f"{storyline_dir}/selected_brief.md")
                and args.regenerate_stage != "storyline_b3"
                and stage != "storyline_b3"):
            print(f"[B3-RUNNER][storyline_b3] 既存Selected Fact Briefを再利用: {storyline_dir}")
            storyline_result = None     # Writerの入力は注記済みB3 artifact(契約検証)であり、本結果は渡さない
        else:
            storyline_result = run_storyline_b3(client, args.theme, ledger_text, out_dir)
            efam.assert_budget_ok(out_dir, args.budget_jpy, "after storyline_b3")
        run_annotation_producer(out_dir)    # C4: 初回・regeneration・resume・再利用のすべてで storyline_b3 確定直後(Writer/契約検証の前)に呼ぶ
        if stage == "storyline_b3" or args.stop_after == "storyline_b3":
            print("[B3-RUNNER] stage=storyline_b3で停止(--stop-after storyline_b3)。")
            _write_cost_json(out_dir, ja_source=ja_source_tag)
            return
    else:
        storyline_result = None

    ja_writer_dir = f"{out_dir}/ja_writer"
    need_writer = stage in ("writer", "advanced", "standard", "all") or args.regenerate_stage == "writer"
    if need_writer:
        if (os.path.exists(f"{ja_writer_dir}/revision2.md")
                and args.regenerate_stage != "writer" and stage != "writer"):
            print(f"[B3-RUNNER][writer] 既存JA記事(R2)の再利用を検討: {ja_writer_dir}/revision2.md"
                  "(W-1来歴+注記契約sha一致を確認、U-1)")
            ja_text = load_reused_ja_text(out_dir, approved_quality_master=args.approved_quality_master,
                                          slug=args.slug, cli_args=vars(args))
        else:
            writer_result = run_ja_writer(client, out_dir, args.budget_jpy)
            ja_text = writer_result["ja_text"]
            efam.assert_budget_ok(out_dir, args.budget_jpy, "after ja_writer")
        if stage == "writer" or args.stop_after == "writer":
            print("[B3-RUNNER] stage=writerで停止(--stop-after writer)。")
            _write_cost_json(out_dir, ja_source=ja_source_tag)
            return
    else:
        ja_text = ""

    # Advanced英訳(M1(a)入り「In one line」、段落3分割retryは技術QA) -> Advanced RF(非Blocking)。
    # RFはcl.logging_contextブロックの外で呼ぶ。Standard生成の入力はb1b/article.md(RFは記事を変更しない)。
    if stage in ("advanced", "all") or args.regenerate_stage == "advanced":
        with cl.logging_context(RUNNER_TAG, "advanced"):
            efam.run_writer_stage(client, theme, ja_text, ledger_text, args.budget_jpy, only="advanced")
        efam.assert_budget_ok(out_dir, args.budget_jpy, "after advanced")
        if ja_source_tag:
            write_ja_source_audit(out_dir, "b1b", ja_source_tag)
        run_post_en_risk_flag(out_dir, "b1b", args.budget_jpy, run_label=args.run_label or None)
        efam.assert_budget_ok(out_dir, args.budget_jpy, "after risk_flag b1b")
        if stage == "advanced" or args.stop_after == "advanced":
            print("[B3-RUNNER] stage=advancedで停止(--stop-after advanced、Mandatory STOP)。")
            _write_cost_json(out_dir, ja_source=ja_source_tag)
            return

    # Standard Level調整(入力=Advanced英文) -> Standard RF(完成Standard英文 x 完全台帳、非Blocking)
    if stage in ("standard", "all") or args.regenerate_stage == "standard":
        with cl.logging_context(RUNNER_TAG, "standard"):
            efam.run_writer_stage(client, theme, ja_text, ledger_text, args.budget_jpy, only="standard")
        efam.assert_budget_ok(out_dir, args.budget_jpy, "after standard")
        if ja_source_tag:
            write_ja_source_audit(out_dir, "a2", ja_source_tag)
        run_post_en_risk_flag(out_dir, "a2", args.budget_jpy, run_label=args.run_label or None)
        efam.assert_budget_ok(out_dir, args.budget_jpy, "after risk_flag a2")

    print("[B3-RUNNER] Standardまで完了。Mandatory STOP(ユーザー確認前に後工程[scaffold/tts/"
          "assemble/player]へは進みません。本runnerにはそれらのstage自体が実装されていません)。")
    _write_cost_json(out_dir, ja_source=ja_source_tag)


def _write_cost_json(out_dir: str, ja_source=None) -> None:
    # C3-3: 非OpenAI(Gemini RF)対応のstage集計へ切替(er053_cost_aggregate_01)。式は旧関数と同じ
    # (openai+gemini、fail-closed)。旧`compute_stage_cost_breakdown`は他経路(Trial等)用に残置。
    # by_stage_jpy/total_jpyの形式は旧cost.jsonと互換、by_provider_jpyとRF Level別内訳を追加。
    breakdown = ca.compute_stage_cost_breakdown_multi(f"{out_dir}/raw_usage_log.jsonl")
    breakdown["risk_flag_by_level_model_condition_jpy"] = ca.rf_stage_summary(breakdown["by_stage_jpy"])
    if ja_source:     # 案b: 記録のみ(分岐に使わない)
        breakdown["ja_source"] = ja_source
    save_json(f"{out_dir}/cost.json", breakdown)
    print(f"[B3-RUNNER][cost] {breakdown}")


if __name__ == "__main__":
    main()
