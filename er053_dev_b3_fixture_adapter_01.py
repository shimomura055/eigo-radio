# -*- coding: utf-8 -*-
"""er053_dev_b3_fixture_adapter_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1で追加、C4(2026-10-10)で producer 方式へ更新。**DEV専用**(Production不参照)。

C4の方針: 注記済みB3は本番producer(er053_b3_deterministic_producer_01、D-det v2+決定論assembler)が生成する。
本adapterは「既存テーマの research_ledger / storyline_b3(B3出力)を out_dir へ複製する」だけ(copy_inputs)。
注記artifact(selected_brief_annotated.md / annotation.json / annotation_manifest.json / writer_constraints.txt)は作らない。
旧 producer="trial_fixture"(Trial成果物からの注記組立)は廃止した。

入力(Trialが実使用したB3出力。FROZEN表のb3_dirではない):
  er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01/<slug>/shared/{brief_original.md, ledger.txt, fact_selection_evidence_original.json}
出力(out_dir):
  storyline_b3/selected_brief.md / storyline_b3/fact_selection_evidence.json(原B3のevidence) / research_ledger/verified_fact_ledger.txt

build_fixture(slug, out_dir) = copy_inputs + 本番producerの呼出(test・開発用確認runの入力準備の便宜。producerのコードはここに無い)。
Productionからimportされない(testで固定): どのProduction moduleもこのmoduleを参照しない。
"""
from __future__ import annotations

import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL_ROOT = os.path.join(HERE, "er052_output", "factlock_astra_e2e_trial_01")
SOURCE_SUBDIR = "g0_real_annotation_01"
# Trial実使用のslug(9本)
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
    shared = os.path.join(trial_root, SOURCE_SUBDIR, slug, "shared")
    return {"brief": os.path.join(shared, "brief_original.md"), "ledger": os.path.join(shared, "ledger.txt"),
            "evidence": os.path.join(shared, "fact_selection_evidence_original.json")}


def copy_inputs(slug: str, out_dir: str, trial_root: str = TRIAL_ROOT) -> dict:
    """既存テーマのB3出力(台帳・selected_brief.md・fact_selection_evidence.json)を out_dir へ複製するだけ。
    入力が無ければFileNotFoundError(黙って別物を作らない)。戻り値: 書いたパス・sha。"""
    src = fixture_paths(slug, trial_root)
    data = {k: _read(p) for k, p in src.items()}      # 生バイトのまま(sha整合のため)
    sdir = os.path.join(out_dir, "storyline_b3")
    _write(os.path.join(sdir, "selected_brief.md"), data["brief"])
    _write(os.path.join(sdir, "fact_selection_evidence.json"), data["evidence"])
    _write(os.path.join(out_dir, "research_ledger", "verified_fact_ledger.txt"), data["ledger"])
    return {"slug": slug, "out_dir": out_dir, "shas": {k: _sha(v) for k, v in data.items()},
            "source_files": {k: os.path.relpath(p, HERE).replace("\\", "/") for k, p in src.items()}}


def build_fixture(slug: str, out_dir: str, trial_root: str = TRIAL_ROOT) -> dict:
    """copy_inputs + 本番producer(er053_b3_deterministic_producer_01.produce_annotated_b3)。注記はproducerが生成する。"""
    import er053_b3_deterministic_producer_01 as producer
    r = copy_inputs(slug, out_dir, trial_root)
    r["producer_result"] = producer.produce_annotated_b3(out_dir)
    r["manifest"] = r["producer_result"]["manifest"]
    return r
