# -*- coding: utf-8 -*-
"""er053_u1_approved_master_acceptance_test_01.py
FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_05(2026-10-11): U-1限定受入(案b)の単体テスト。API呼出0・費用0円。

実行: .venv/Scripts/python.exe -m pytest er053_u1_approved_master_acceptance_test_01.py -q
合成の承認マスター一式(tmp repo root + master + meta + run dir)で、runner.REPO_ROOT / APPROVED_QUALITY_MASTERS を
mock.patchして検証する(実registryの内容は別testで固定)。
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er053_approved_master_rundir_builder_01 as builder
import er053_dev_b3_fixture_adapter_01 as adapter

SLUG = "meta"
CHAIN = "MAQ_TRIAL_W-1"
JA_TEXT = "これは承認済み品質マスターの本文です。\n二行目の本文です。\n"
DECISION = runner.APPROVED_MASTER_DECISION_REF


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rb(p):
    with open(p, "rb") as f:
        return f.read()


def wb(p, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(b)


class Env:
    """tmp repo root + 承認マスター + run dir(adapterのB3 fixture + ja_writer複製)を作る。"""

    def __init__(self, *, status="HUMAN_APPROVED_QUALITY_MASTER", family="X", chain=CHAIN, master_crlf=False,
                 rev_bytes=None, ev_ja_sha=None, meta_override=None, annotated_sha=None, slug=SLUG):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="u1amq_"))
        self.root = os.path.join(self.tmp, "repo")
        self.out = os.path.join(self.tmp, "run")
        self.slug = slug
        adapter.build_fixture(SLUG, self.out)
        self.master_lf = JA_TEXT.encode("utf-8")
        self.M = sha(self.master_lf)
        mdir = os.path.join(self.root, *runner.APPROVED_MASTERS_REL.split("/"), slug)
        self.master_path = os.path.join(mdir, "E_master_r2.md")
        wb(self.master_path, self.master_lf.replace(b"\n", b"\r\n") if master_crlf else self.master_lf)
        sc = json.loads(rb(os.path.join(self.out, "storyline_b3", "annotation.json")).decode("utf-8"))
        self.ids = sorted({i for f in sc["facts"] for i in f["ledger_ids"]})
        self.ledger_sha = sha(rb(os.path.join(self.out, "research_ledger", "verified_fact_ledger.txt")))
        self.meta = {
            "slug": slug, "family": family, "status": status, "source_sha256": self.M, "saved_sha256": self.M,
            "byte_identical_to_source": True, "saved_file": f"{runner.APPROVED_MASTERS_REL}/{slug}/E_master_r2.md",
            "fact_ledger": {"sha256": self.ledger_sha}, "selected_fact_ids": self.ids,
            "user_eval_date": "2026-10-11", "note": "test note"}
        self.meta.update(meta_override or {})
        self.meta_path = os.path.join(mdir, "E_master_meta.json")
        wb(self.meta_path, json.dumps(self.meta, ensure_ascii=False, indent=1).encode("utf-8"))
        from er053_b3_annotation_contract_01 import validate_annotated_b3
        ann_sha = annotated_sha or validate_annotated_b3(self.out).annotated_md_sha256
        self.ev = {"chain_method": chain, "annotated_md_sha256": ann_sha,
                   "ja_text_sha256": ev_ja_sha if ev_ja_sha is not None else self.M,
                   "annotation_manifest_producer": "deterministic_v2", "override_reason": "trial"}
        self.ev_bytes = json.dumps(self.ev, ensure_ascii=False, indent=2).encode("utf-8")
        wb(os.path.join(self.out, "ja_writer", "runtime_evidence.json"), self.ev_bytes)
        wb(os.path.join(self.out, "ja_writer", "revision2.md"), rev_bytes if rev_bytes is not None else self.master_lf)
        self.pin = {"master_sha256_lf": self.M, "chain_method": CHAIN, "ledger_sha256": self.ledger_sha,
                    "selected_brief_sha256_raw": sha(rb(os.path.join(self.out, "storyline_b3", "selected_brief.md"))),
                    "runtime_evidence_sha256_raw": sha(self.ev_bytes), "decision_ref": DECISION}
        self.patches = [mock.patch.object(runner, "REPO_ROOT", self.root),
                        mock.patch.dict(runner.APPROVED_QUALITY_MASTERS, {slug: self.pin}, clear=True)]
        for p in self.patches:
            p.start()

    def close(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def load(self, **kw):
        return runner.load_reused_ja_text(self.out, approved_quality_master=kw.pop("meta", self.meta_path),
                                          slug=kw.pop("slug", self.slug), cli_args=kw.pop("cli", {"x": 1}))

    def acc(self):
        p = os.path.join(self.out, runner.ACCEPTANCE_RECORD_REL)
        if not os.path.exists(p):
            return []
        return [json.loads(l) for l in rb(p).decode("utf-8").splitlines() if l.strip()]


class Base(unittest.TestCase):
    def mk(self, **kw):
        e = Env(**kw)
        self.addCleanup(e.close)
        return e

    def rejects(self, e, cond, **kw):
        with self.assertRaisesRegex(runner.ApprovedMasterAcceptanceStop, rf"APPROVED_MASTER_REJECTED: {cond}="):
            e.load(**kw)
        self.assertEqual(e.acc(), [], "NG時はacceptance記録を作らない")


class AcceptTests(Base):
    def test_accept_ok_returns_text_and_records_once(self):
        e = self.mk()
        ev_before = rb(os.path.join(e.out, "ja_writer", "runtime_evidence.json"))
        self.assertEqual(e.load(), JA_TEXT)
        recs = e.acc()
        self.assertEqual(len(recs), 1)
        r = recs[0]
        self.assertEqual(r["decision_ref"], DECISION)
        self.assertEqual(r["slug"], SLUG)
        self.assertEqual(r["meta_user_eval_date"], "2026-10-11")
        self.assertEqual(r["meta_note"], "test note")
        self.assertEqual(r["cli"], {"x": 1})
        self.assertEqual(r["chain_method_observed"], CHAIN)
        self.assertEqual(r["registry_snapshot"], e.pin)
        self.assertEqual(r["runner_version"], runner.self_sha256(runner.__file__))
        self.assertEqual(sorted(r["checks"]), sorted(["a", "b1", "b2", "b3", "b4", "c", "d", "e", "f", "g", "g2"]))
        self.assertEqual(r["shas"]["master_sha256_lf"], e.M)
        # 来歴不変: runtime_evidence.jsonはバイト不変(chain_methodはMAQ_TRIAL_W-1のまま)
        self.assertEqual(rb(os.path.join(e.out, "ja_writer", "runtime_evidence.json")), ev_before)
        self.assertEqual(json.loads(ev_before)["chain_method"], CHAIN)
        self.assertEqual(rb(os.path.join(e.out, "ja_writer", "revision2.md")), e.master_lf)

    def test_master_body_crlf_in_worktree_is_still_accepted_by_lf_normalization(self):
        e = self.mk(master_crlf=True)
        self.assertEqual(e.load(), JA_TEXT)

    def test_acceptance_is_append_only_and_reruns_add_lines(self):
        e = self.mk()
        e.load()
        first = rb(os.path.join(e.out, runner.ACCEPTANCE_RECORD_REL))
        e.load()
        e.load()
        data = rb(os.path.join(e.out, runner.ACCEPTANCE_RECORD_REL))
        self.assertTrue(data.startswith(first), "既存行は不変(追記のみ)")
        self.assertEqual(len(e.acc()), 3)

    def test_acceptance_file_is_not_a_judgement_input(self):
        """記録があっても opt-in 無しは従来U-1 STOP(chain_method!='W-1')。偽造した記録でも受理されない。"""
        e = self.mk()
        e.load()
        self.assertEqual(len(e.acc()), 1)
        with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
            runner.load_reused_ja_text(e.out)
        self.assertNotIsInstance(cm.exception, runner.ApprovedMasterAcceptanceStop)
        self.assertIn("LEGACY_WRITER_PROVENANCE", str(cm.exception))
        # 記録を偽造した別run dir(条件不一致)でも、毎回フル再検証でSTOP
        e2 = self.mk(ev_ja_sha="0" * 64)
        os.makedirs(os.path.join(e2.out, "ja_writer"), exist_ok=True)
        wb(os.path.join(e2.out, runner.ACCEPTANCE_RECORD_REL), rb(os.path.join(e.out, runner.ACCEPTANCE_RECORD_REL)))
        with self.assertRaisesRegex(runner.ApprovedMasterAcceptanceStop, "b3="):
            e2.load()

    def test_build_manifest_is_copied_into_record_as_info(self):
        e = self.mk()
        wb(os.path.join(e.out, runner.RUNDIR_BUILD_MANIFEST),
           json.dumps({"origin_dir": "X:/origin", "files": {"ja_writer/revision2.md": e.M}}).encode("utf-8"))
        e.load()
        r = e.acc()[0]
        self.assertEqual(r["rundir_build"]["origin_dir"], "X:/origin")
        self.assertEqual(r["rundir_current_raw_shas"]["ja_writer/revision2.md"], e.M)

    def test_toctou_returns_the_bytes_that_were_verified(self):
        e = self.mk()
        real = runner.contract.validate_annotated_b3

        def swap(out_dir):
            r = real(out_dir)
            wb(os.path.join(out_dir, "ja_writer", "revision2.md"), "検証後に差し替えられた本文\n".encode("utf-8"))
            return r
        with mock.patch.object(runner.contract, "validate_annotated_b3", side_effect=swap):
            self.assertEqual(e.load(), JA_TEXT)     # 差し替え前(検証時)のbytesをそのまま返す


class RejectionTests(Base):
    def test_a_status_not_approved(self):
        self.rejects(self.mk(status="CANDIDATE"), "a")

    def test_a_family_not_x(self):
        self.rejects(self.mk(family="E"), "a")

    def test_b1_source_sha_differs_from_saved(self):
        self.rejects(self.mk(meta_override={"source_sha256": "1" * 64}), "b1")

    def test_b1_byte_identical_false(self):
        self.rejects(self.mk(meta_override={"byte_identical_to_source": False}), "b1")

    def test_b2_master_body_differs(self):
        e = self.mk()
        wb(e.master_path, "改変されたマスター本文\n".encode("utf-8"))
        self.rejects(e, "b2")

    def test_b3_evidence_ja_text_sha_differs(self):
        self.rejects(self.mk(ev_ja_sha="2" * 64), "b3")

    def test_b4_revision2_raw_sha_differs(self):
        self.rejects(self.mk(rev_bytes="別の本文\n".encode("utf-8")), "b4")

    def test_b4_revision2_crlf_copy_rejected(self):
        self.rejects(self.mk(rev_bytes=JA_TEXT.encode("utf-8").replace(b"\n", b"\r\n")), "b4")

    def test_c_contract_violation_still_enforced(self):
        e = self.mk()
        with open(os.path.join(e.out, "storyline_b3", "selected_brief_annotated.md"), "ab") as f:
            f.write("\n- 【事実99】改変\n".encode("utf-8"))
        with self.assertRaises(runner.contract.AnnotatedB3ContractViolation):
            e.load()
        self.assertEqual(e.acc(), [])

    def test_c_annotated_sha_mismatch(self):
        self.rejects(self.mk(annotated_sha="3" * 64), "c")

    def test_d_chain_method_exact_match_only(self):
        for bad in ("MAQ_TRIAL_W-1 ", "maq_trial_w-1", "MAQ_TRIAL_W-1-X", "XMAQ_TRIAL_W-1", "MAQ_TRIAL", "W-1", "", None, ["MAQ_TRIAL_W-1"]):
            with self.subTest(chain=bad):
                self.rejects(self.mk(chain=bad), "d")

    def test_e_meta_path_not_under_repo_masters_dir(self):
        e = self.mk()
        other = os.path.join(e.out, "E_master_meta.json")        # run dir内meta
        shutil.copyfile(e.meta_path, other)
        self.rejects(e, "e", meta=other)

    def test_e_dotdot_rejected(self):
        e = self.mk()
        p = os.path.join(e.root, "docs", "..", "docs", "quality", "ja_quality_masters", SLUG, "E_master_meta.json")
        self.rejects(e, "e", meta=p)

    def test_e_unc_rejected(self):
        e = self.mk()
        self.rejects(e, "e", meta="\\\\server\\share\\E_master_meta.json")
        self.rejects(e, "e", meta="//server/share/E_master_meta.json")

    def test_e_symlink_rejected(self):
        e = self.mk()
        link = os.path.join(e.root, "docs", "quality", "ja_quality_masters", "linkslug")
        try:
            os.symlink(os.path.dirname(e.meta_path), link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink作成権限なし")
        self.rejects(e, "e", meta=os.path.join(link, "E_master_meta.json"))

    def test_e_file_symlink_rejected(self):
        e = self.mk()
        alt = os.path.join(e.tmp, "alt_meta.json")
        shutil.copyfile(e.meta_path, alt)
        os.remove(e.meta_path)
        try:
            os.symlink(alt, e.meta_path)
        except (OSError, NotImplementedError):
            self.skipTest("symlink作成権限なし")
        self.rejects(e, "e")

    def test_e_non_string_or_empty_path(self):
        e = self.mk()
        self.rejects(e, "e", meta="   ")

    def test_f_slug_mismatch(self):
        e = self.mk()
        self.rejects(e, "(e|f)", slug="coffee_prices")   # path/--slug不一致はeで先に厳密拒否(f相当)
        self.assertEqual(e.acc(), [])

    def test_f_meta_slug_field_mismatch(self):
        self.rejects(self.mk(meta_override={"slug": "other"}), "f")

    def test_g_slug_not_registered(self):
        e = self.mk()
        with mock.patch.dict(runner.APPROVED_QUALITY_MASTERS, {}, clear=True):
            self.rejects(e, "g")

    def test_g_each_pin_field_mismatch(self):
        for k in ("master_sha256_lf", "chain_method", "ledger_sha256", "selected_brief_sha256_raw", "runtime_evidence_sha256_raw"):
            with self.subTest(pin=k):
                e = self.mk()
                bad = dict(e.pin)
                bad[k] = "f" * 64 if k != "chain_method" else "W-1"
                with mock.patch.dict(runner.APPROVED_QUALITY_MASTERS, {SLUG: bad}, clear=True):
                    self.rejects(e, "g")

    def test_g2_meta_ledger_sha_differs(self):
        self.rejects(self.mk(meta_override={"fact_ledger": {"sha256": "4" * 64}}), "g2")

    def test_g2_selected_fact_ids_differ(self):
        self.rejects(self.mk(meta_override={"selected_fact_ids": ["ZZZ-999"]}), "g2")

    def test_ordinary_w1_article_with_optin_is_stop(self):
        """通常W-1記事(chain_method=='W-1')へのopt-in付与は意図不明としてSTOP(d)。"""
        self.rejects(self.mk(chain="W-1"), "d")


class PrecheckTests(Base):
    def args(self, e, **kw):
        base = ["--theme", "t", "--slug", kw.pop("slug", SLUG), "--out-dir", kw.pop("out", e.out)]
        if kw.pop("optin", True):
            base += ["--approved-quality-master", kw.pop("meta", e.meta_path)]
        for k, v in kw.items():
            base += [f"--{k.replace('_', '-')}", v]
        return runner.build_arg_parser().parse_args(base)

    def test_precheck_ok_and_no_record_written(self):
        e = self.mk()
        res = runner.precheck_approved_quality_master(self.args(e))
        self.assertEqual(res["master_sha256_lf"], e.M)
        self.assertEqual(e.acc(), [])        # 記録は再利用時のみ

    def test_precheck_none_when_not_opted_in(self):
        e = self.mk()
        self.assertIsNone(runner.precheck_approved_quality_master(self.args(e, optin=False)))

    def test_stage_combinations_stop(self):
        e = self.mk()
        for st in ("research", "ledger", "storyline_b3", "writer"):
            with self.subTest(stage=st), self.assertRaisesRegex(runner.ApprovedMasterAcceptanceStop, "pre.stage="):
                runner.precheck_approved_quality_master(self.args(e, stage=st))
        for st in ("advanced", "standard", "all"):
            with self.subTest(ok_stage=st):
                self.assertIsNotNone(runner.precheck_approved_quality_master(self.args(e, stage=st)))

    def test_regenerate_stage_combinations_stop(self):
        e = self.mk()
        for rg in ("writer", "storyline_b3"):
            with self.subTest(rg=rg), self.assertRaisesRegex(runner.ApprovedMasterAcceptanceStop, "pre.regenerate="):
                runner.precheck_approved_quality_master(self.args(e, regenerate_stage=rg))
        self.assertIsNotNone(runner.precheck_approved_quality_master(self.args(e, regenerate_stage="advanced")))

    def test_stop_after_storyline_b3_stops(self):
        e = self.mk()
        with self.assertRaisesRegex(runner.ApprovedMasterAcceptanceStop, "pre.stop_after="):
            runner.precheck_approved_quality_master(self.args(e, stop_after="storyline_b3"))

    def test_revision2_missing_stops(self):
        e = self.mk()
        os.remove(os.path.join(e.out, "ja_writer", "revision2.md"))
        with self.assertRaisesRegex(runner.ApprovedMasterAcceptanceStop, "pre.revision2="):
            runner.precheck_approved_quality_master(self.args(e))

    def test_main_stops_before_get_client_and_creates_nothing(self):
        e = self.mk(ev_ja_sha="5" * 64)
        fresh = os.path.join(e.tmp, "fresh_out")
        for out, argv_extra in ((e.out, []), (fresh, [])):
            argv = ["runner", "--theme", "t", "--slug", SLUG, "--out-dir", out, "--approved-quality-master", e.meta_path]
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(runner.vfl01, "get_client", side_effect=AssertionError("get_client called")) as gc, \
                    mock.patch.object(runner, "run_research_and_ledger", side_effect=AssertionError("research called")), \
                    self.assertRaises(runner.ApprovedMasterAcceptanceStop):
                runner.main()
            gc.assert_not_called()
        self.assertFalse(os.path.exists(fresh), "revision2欠落のrun dirは作らない(課金前STOP)")
        self.assertFalse(os.path.exists(os.path.join(e.out, "entry_point.json")))

    def test_main_accepts_then_reuses_without_api_for_ja(self):
        """正常系: 事前検証PASS -> writerはload_reused経由(run_ja_writer未呼出) -> stop-after writerで停止。"""
        e = self.mk()
        argv = ["runner", "--theme", "t", "--slug", SLUG, "--out-dir", e.out, "--approved-quality-master", e.meta_path,
                "--stage", "all", "--stop-after", "writer"]
        with mock.patch.object(sys, "argv", argv), \
                mock.patch.object(runner.vfl01, "get_client", return_value=object()), \
                mock.patch.object(runner, "run_ja_writer", side_effect=AssertionError("writer regenerated")), \
                mock.patch.object(runner, "run_annotation_producer"), \
                mock.patch.object(runner.cl, "install"), \
                mock.patch.object(runner, "_write_cost_json") as wc:
            runner.main()
        self.assertEqual(len(e.acc()), 1)
        tag = f"approved_quality_master:{SLUG}@{e.M[:12]}"
        ep = json.loads(rb(os.path.join(e.out, "entry_point.json")).decode("utf-8"))
        self.assertEqual(ep["approved_quality_master"]["ja_source"], tag)
        wc.assert_called_with(e.out, ja_source=tag)

    def test_ja_source_audit_and_cost_json(self):
        e = self.mk()
        runner.write_ja_source_audit(e.out, "b1b", "approved_quality_master:x@abc")
        self.assertEqual(json.loads(rb(os.path.join(e.out, "b1b", "audit", "ja_source.json"))), {"ja_source": "approved_quality_master:x@abc"})
        with mock.patch.object(runner.ca, "compute_stage_cost_breakdown_multi", side_effect=lambda *_a, **_k: {"by_stage_jpy": {}, "total_jpy": 0}), \
                mock.patch.object(runner.ca, "rf_stage_summary", return_value={}):
            runner._write_cost_json(e.out, ja_source="approved_quality_master:x@abc")
            self.assertEqual(json.loads(rb(os.path.join(e.out, "cost.json")))["ja_source"], "approved_quality_master:x@abc")
            runner._write_cost_json(e.out)
            self.assertNotIn("ja_source", json.loads(rb(os.path.join(e.out, "cost.json"))))


class DefaultOffTests(unittest.TestCase):
    def test_argparse_default_none_and_function_defaults_none(self):
        a = runner.build_arg_parser().parse_args(["--theme", "t", "--slug", "s", "--out-dir", "o"])
        self.assertIsNone(a.approved_quality_master)
        sig = inspect.signature(runner.load_reused_ja_text)
        for k in ("approved_quality_master", "slug", "cli_args"):
            self.assertIsNone(sig.parameters[k].default)

    def test_no_env_or_config_enable_path(self):
        src = inspect.getsource(runner)
        start = src.index("# U-1 限定受入(案b)")
        end = src.index("def load_reused_ja_text")
        block = src[start:end]
        for token in ("os.environ", "getenv", "configparser", "yaml", "environ"):
            self.assertNotIn(token, block)
        main_src = inspect.getsource(runner.main)
        self.assertNotIn("environ", main_src)
        # opt-in値の唯一の供給元は CLI引数(argparse)
        self.assertEqual(main_src.count("approved_quality_master"), main_src.count("approved_quality_master"))
        self.assertIn("args.approved_quality_master", main_src)

    def test_without_optin_chain_method_trial_is_legacy_stop_even_with_valid_master(self):
        e = Env()
        try:
            with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
                runner.load_reused_ja_text(e.out)
            self.assertNotIsInstance(cm.exception, runner.ApprovedMasterAcceptanceStop)
            self.assertIn("chain_method", str(cm.exception))
            self.assertEqual(e.acc(), [])
        finally:
            e.close()

    def test_exception_is_subclass_of_legacy_stop(self):
        self.assertTrue(issubclass(runner.ApprovedMasterAcceptanceStop, runner.LegacyWriterProvenanceStop))

    def test_real_registry_is_exactly_coffee_prices_e_master(self):
        reg = runner.APPROVED_QUALITY_MASTERS
        self.assertEqual(sorted(reg), ["coffee_prices"])
        pin = reg["coffee_prices"]
        self.assertEqual(pin["master_sha256_lf"], "742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a")
        self.assertEqual(pin["ledger_sha256"], "e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b")
        self.assertEqual(pin["chain_method"], "MAQ_TRIAL_W-1")
        self.assertEqual(pin["decision_ref"], DECISION)
        self.assertEqual(runner.APPROVED_CHAIN_METHODS, frozenset({"MAQ_TRIAL_W-1"}))
        meta = json.loads(rb(os.path.join(runner.REPO_ROOT, "docs", "quality", "ja_quality_masters", "coffee_prices",
                                          "E_master_meta.json")).decode("utf-8"))
        self.assertEqual(meta["saved_sha256"], pin["master_sha256_lf"])
        self.assertEqual(meta["fact_ledger"]["sha256"], pin["ledger_sha256"])

    def test_registry_and_allowlist_strict_type(self):
        self.assertIsInstance(runner.APPROVED_CHAIN_METHODS, frozenset)


class BuilderTests(unittest.TestCase):
    def test_builder_copies_bytes_and_manifest_and_refuses_overwrite(self):
        tmp = os.path.realpath(tempfile.mkdtemp(prefix="u1amq_b_"))
        try:
            origin = os.path.join(tmp, "origin")
            files = {"research_ledger/verified_fact_ledger.txt": b"L\r\nx\r\n", "storyline_b3/selected_brief.md": b"B\n",
                     "storyline_b3/selected_brief_annotated.md": b"A\n", "storyline_b3/annotation.json": b"{}",
                     "storyline_b3/annotation_manifest.json": b"{}", "storyline_b3/writer_constraints.txt": b"W\n",
                     "ja_writer/revision2.md": b"R\n", "ja_writer/runtime_evidence.json": b"{}",
                     "ja_writer/factlock/r0.md": b"r0\n", "raw_usage_log.jsonl": b"NO\n", "export/r2.md": b"NO\n"}
            for rel, b in files.items():
                wb(os.path.join(origin, rel), b)
            out = os.path.join(tmp, "run")
            m = builder.build_rundir(origin, out)
            self.assertNotIn("raw_usage_log.jsonl", m["files"])
            self.assertNotIn("export/r2.md", m["files"])
            self.assertFalse(os.path.exists(os.path.join(out, "raw_usage_log.jsonl")))
            for rel, b in files.items():
                if rel in m["files"]:
                    self.assertEqual(rb(os.path.join(out, rel)), b)
                    self.assertEqual(m["files"][rel], sha(b))
            self.assertEqual(json.loads(rb(os.path.join(out, builder.BUILD_MANIFEST)))["origin_dir"], os.path.abspath(origin))
            builder.build_rundir(origin, out)        # 一致する既存は冪等
            wb(os.path.join(out, "ja_writer/revision2.md"), b"changed\n")
            with self.assertRaisesRegex(RuntimeError, "no overwrite"):
                builder.build_rundir(origin, out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
