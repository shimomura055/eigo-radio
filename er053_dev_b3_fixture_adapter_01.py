# -*- coding: utf-8 -*-
"""er053_dev_b3_fixture_adapter_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。**DEV専用**(Production不参照)fixture adapter。

Trial(FACTLOCK-ASTRA-E2E-TRIAL-01)で実際に使われた成果物から、Production側の「注記済みB3 入力契約」
(er053_b3_annotation_contract_01)の契約ファイルを out_dir に組み立てる。¥0・API呼出0。

入力(Trialが実使用したもの。FROZEN表のb3_dirではない):
  er052_output/factlock_astra_e2e_trial_01/runs/<slug>/shared/{brief_original.md, ledger.txt, fact_selection_evidence_original.json}
  er052_output/factlock_astra_e2e_trial_01/annotation/final/<slug>/{selected_brief_factlock.md, annotation.json}
出力(out_dir):
  storyline_b3/selected_brief.md / selected_brief_annotated.md / annotation.json / annotation_manifest.json(producer="trial_fixture")
  storyline_b3/fact_selection_evidence.json(再利用分岐用。原B3のevidence)
  research_ledger/verified_fact_ledger.txt

Productionからimportされない(testで固定): どのProduction moduleもこのmoduleを参照しない。
manifest.producer="trial_fixture" は記録専用(Production検証は分岐しない)だが、G-C(最終L3)の受入条件は producer != "trial_fixture"。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL_ROOT = os.path.join(HERE, "er052_output", "factlock_astra_e2e_trial_01")
PRODUCER = "trial_fixture"
SCHEMA_VERSION = "b3_annotation_manifest_v1"
# Trial実使用のslug(annotation/final 9本)
SLUGS = ("byd_recall", "central_bank_mortgage", "hormuz", "meta", "openai_copyright",
         "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _read(p: str) -> bytes:
    with open(p, "rb") as f:
        return f.read()


def _write(p: str, b: bytes) -> None:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(b)


def fixture_paths(slug: str, trial_root: str = TRIAL_ROOT) -> dict:
    shared = os.path.join(trial_root, "runs", slug, "shared")
    final = os.path.join(trial_root, "annotation", "final", slug)
    return {"brief": os.path.join(shared, "brief_original.md"), "ledger": os.path.join(shared, "ledger.txt"),
            "evidence": os.path.join(shared, "fact_selection_evidence_original.json"),
            "annotated": os.path.join(final, "selected_brief_factlock.md"), "sidecar": os.path.join(final, "annotation.json")}


def build_fixture(slug: str, out_dir: str, trial_root: str = TRIAL_ROOT) -> dict:
    """Trial成果物 -> out_dir の契約ファイル。入力が無ければFileNotFoundError(黙って別物を作らない)。戻り値: 書いたパス・sha。"""
    src = fixture_paths(slug, trial_root)
    data = {k: _read(p) for k, p in src.items()}      # 生バイトのまま(sha整合のためCRLFも保存)
    sidecar = json.loads(data["sidecar"].decode("utf-8"))
    sdir = os.path.join(out_dir, "storyline_b3")
    _write(os.path.join(sdir, "selected_brief.md"), data["brief"])
    _write(os.path.join(sdir, "selected_brief_annotated.md"), data["annotated"])
    _write(os.path.join(sdir, "annotation.json"), data["sidecar"])
    _write(os.path.join(sdir, "fact_selection_evidence.json"), data["evidence"])
    _write(os.path.join(out_dir, "research_ledger", "verified_fact_ledger.txt"), data["ledger"])
    manifest = {
        "schema_version": SCHEMA_VERSION, "producer": PRODUCER,
        "source_selected_brief_sha256": _sha(data["brief"]), "ledger_sha256": _sha(data["ledger"]),
        "annotated_md_sha256": _sha(data["annotated"]), "sidecar_sha256": _sha(data["sidecar"]),
        "spec_sha256": sidecar["spec_sha256"],
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        # Trialでb3_annotation_check_01が検査済み(annotation/final/final_json_check.json)の自己申告に相当。fixtureなので全てPASS固定で記録のみ
        "checks": {"a_alignment": "PASS", "b_numbers": "PASS", "c_core_peripheral": "PASS", "d_tags": "PASS", "e_sidecar": "PASS"},
        "model_ids": [],
        "fixture": {"slug": slug, "note": "Trial成果物から組み立てた開発用fixture。B3注記自動化(Lane B)の出力ではない",
                    "source_files": {k: os.path.relpath(p, HERE).replace("\\", "/") for k, p in src.items()}},
    }
    _write(os.path.join(sdir, "annotation_manifest.json"), json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"slug": slug, "out_dir": out_dir, "manifest": manifest}
