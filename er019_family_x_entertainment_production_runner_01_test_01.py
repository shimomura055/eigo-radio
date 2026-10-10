# ============================================================
# er019_family_x_entertainment_production_runner_01_test_01.py
# RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2(2026-10-10)で全面更新
# ============================================================
# er019_family_x_entertainment_production_runner_01 の単体テスト(実API呼び出し0、費用0円)。
#   - run_ja_writer(): 新Writer W-1の呼出glue(入力は out_dir の注記済みB3 artifactのみ、予算ガード配線、記号QA STOP)
#   - 契約fail-closed: 注記なし/改変 -> 課金前STOP(client未呼出)
#   - load_reused_ja_text(): U-1/穴B(再利用分岐でも W-1来歴+注記契約sha一致を確認、違えばSTOP)
#   - run_post_en_risk_flag(): RF呼出glue(非Blocking、budget_checkフック、Queue保存、記事sha不変)
# (旧: JA Fact Check配線・audit保存・JAFactCheckStopErrorのtestは旧Fact Checker撤去に伴い削除)
#
# 実行方法:
#   .venv/Scripts/python.exe -m pytest er019_family_x_entertainment_production_runner_01_test_01.py -q
# ============================================================
from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_dev_b3_fixture_adapter_01 as adapter
import er053_review_queue_01 as rq
import er053_risk_flagger_production_01 as rf


def make_out(slug="meta"):
    d = tempfile.mkdtemp(prefix="c2_runner_")
    adapter.build_fixture(slug, d)
    return d


def write_w1_ja_writer(out_dir, text="これはW-1が書いた日本語記事です。\n", chain="W-1", annotated_sha=None, producer="trial_fixture"):
    """W-1が出力する ja_writer/{revision2.md, runtime_evidence.json} を模擬(最小)。"""
    if annotated_sha is None:
        annotated_sha = contract.validate_annotated_b3(out_dir).annotated_md_sha256
    d = os.path.join(out_dir, "ja_writer")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "revision2.md"), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    with open(os.path.join(d, "runtime_evidence.json"), "w", encoding="utf-8") as f:
        json.dump({"chain_method": chain, "annotated_md_sha256": annotated_sha,
                   "annotation_manifest_producer": producer}, f)
    return text


class _NeverClient:
    """API呼出が1回でも起きたら失敗する(課金前STOPの確認用)。"""
    def __init__(self):
        self.calls = 0
        self.responses = self

    def create(self, **kw):
        self.calls += 1
        raise AssertionError("API must not be called")


class RunJaWriterTests(unittest.TestCase):
    def setUp(self):
        self.out = make_out()

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_signature_has_no_legacy_brief_or_ledger_inputs(self):
        self.assertEqual(list(inspect.signature(runner.run_ja_writer).parameters), ["client", "out_dir", "budget_jpy"])

    def test_calls_w1_with_out_dir_only_and_budget_hook_uses_efam_assert_budget_ok(self):
        captured = {}

        def fake_w1(out_dir, client=None, budget_check=None):
            captured.update(out_dir=out_dir, client=client, budget_check=budget_check)
            return {"ja_text": "JA", "title": "T", "runtime_evidence": {"chain_method": "W-1"}}

        sentinel = object()
        with mock.patch.object(runner.w1, "run_w1_writer", side_effect=fake_w1), \
                mock.patch.object(runner.efam, "assert_budget_ok", return_value=1.0) as m_budget:
            r = runner.run_ja_writer(sentinel, self.out, 77.0)
            self.assertEqual(r["ja_text"], "JA")
            self.assertEqual(r["title"], "T")
            self.assertIs(captured["client"], sentinel)
            self.assertEqual(captured["out_dir"], self.out)
            captured["budget_check"]()          # フックを呼ぶと efam.assert_budget_ok(out_dir, 77.0, ...)
        args = m_budget.call_args.args
        self.assertEqual(args[0], self.out)
        self.assertEqual(args[1], 77.0)

    def test_budget_hook_exception_is_not_swallowed(self):
        def fake_w1(out_dir, client=None, budget_check=None):
            budget_check()
            return {}

        with mock.patch.object(runner.w1, "run_w1_writer", side_effect=fake_w1), \
                mock.patch.object(runner.efam, "assert_budget_ok", side_effect=RuntimeError("[BUDGET_GUARD] cap")):
            with self.assertRaises(RuntimeError) as cm:
                runner.run_ja_writer(object(), self.out, 1.0)
        self.assertIn("BUDGET_GUARD", str(cm.exception))

    def test_symbol_stop_becomes_runtime_error(self):
        exc = runner.w1.JASymbolCheckStopError("r2_symbol", "[STOP] JA_SYMBOL_CHECK_STOP: test", "rejected", [])
        with mock.patch.object(runner.w1, "run_w1_writer", side_effect=exc):
            with self.assertRaises(RuntimeError) as cm:
                runner.run_ja_writer(object(), self.out, 1.0)
        self.assertIn("JA_SYMBOL_CHECK_STOP", str(cm.exception))

    def test_no_legacy_stage_artifacts_are_written_by_runner(self):
        """旧: ja_writer/audit/deviation_checks, rejected_ja_*.md, fact_checks_summary はrunnerが書かない。"""
        src = inspect.getsource(runner)
        for token in ("deviation_checks", "fact_checks_summary", "rejected_ja_", "JAFactCheckStopError"):
            self.assertNotIn(token, src, token)


class ContractFailClosedTests(unittest.TestCase):
    """契約検証はWriter入口(課金前)。注記なし/改変 -> STOP、API呼出0(stub client未呼出)。"""

    def test_missing_annotation_stops_before_any_api_call(self):
        out = make_out()
        try:
            for f in ("selected_brief_annotated.md", "annotation.json", "annotation_manifest.json"):
                os.remove(os.path.join(out, "storyline_b3", f))
            c = _NeverClient()
            with self.assertRaises(contract.AnnotatedB3ContractViolation):
                runner.run_ja_writer(c, out, 150.0)
            self.assertEqual(c.calls, 0)
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_tampered_annotated_md_stops_before_any_api_call(self):
        out = make_out()
        try:
            p = os.path.join(out, "storyline_b3", "selected_brief_annotated.md")
            with open(p, "ab") as f:
                f.write("\n- 【事実99】改変された事実\n".encode("utf-8"))
            c = _NeverClient()
            with self.assertRaises(contract.AnnotatedB3ContractViolation):
                runner.run_ja_writer(c, out, 150.0)
            self.assertEqual(c.calls, 0)
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_unannotated_only_b3_stops(self):
        """注記なしの selected_brief.md だけがある(従来のProduction出力)場合はWriterを動かさずSTOP。"""
        out = tempfile.mkdtemp(prefix="c2_runner_unannot_")
        try:
            os.makedirs(os.path.join(out, "storyline_b3"))
            os.makedirs(os.path.join(out, "research_ledger"))
            with open(os.path.join(out, "storyline_b3", "selected_brief.md"), "w", encoding="utf-8") as f:
                f.write("# Selected Fact Brief\n\n## Storyline\nS\n\n## Selected Facts\n- fact one\n")
            c = _NeverClient()
            with self.assertRaises(contract.AnnotatedB3ContractViolation):
                runner.run_ja_writer(c, out, 150.0)
            self.assertEqual(c.calls, 0)
        finally:
            shutil.rmtree(out, ignore_errors=True)


class ReusedJaProvenanceTests(unittest.TestCase):
    """U-1 / 穴B: 再利用分岐でも chain_method=="W-1" かつ annotated_md_sha256 が契約と一致する場合のみ再利用。"""

    def setUp(self):
        self.out = make_out()

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_matching_w1_provenance_is_reused(self):
        text = write_w1_ja_writer(self.out)
        self.assertEqual(runner.load_reused_ja_text(self.out), text)

    def test_no_runtime_evidence_is_legacy_writer_stop(self):
        d = os.path.join(self.out, "ja_writer")
        os.makedirs(d)
        with open(os.path.join(d, "revision2.md"), "w", encoding="utf-8") as f:
            f.write("旧Writerの記事")
        with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
            runner.load_reused_ja_text(self.out)
        self.assertIn("U-1", str(cm.exception))

    def test_old_writer_chain_method_is_stop(self):
        write_w1_ja_writer(self.out, chain="previous_response_id")
        with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
            runner.load_reused_ja_text(self.out)
        self.assertIn("chain_method", str(cm.exception))

    def test_annotated_sha_mismatch_is_stop(self):
        write_w1_ja_writer(self.out, annotated_sha="0" * 64)
        with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
            runner.load_reused_ja_text(self.out)
        self.assertIn("PROVENANCE_MISMATCH", str(cm.exception))

    def test_contract_violation_blocks_reuse_too(self):
        write_w1_ja_writer(self.out)
        os.remove(os.path.join(self.out, "storyline_b3", "annotation_manifest.json"))
        with self.assertRaises(contract.AnnotatedB3ContractViolation):
            runner.load_reused_ja_text(self.out)


# ---------------------------------------------------------------- Risk Flagger glue
def write_articles(out_dir):
    for lv, text in (("b1b", "# Adv\n\nAdvanced sentence one. Advanced sentence two.\n"),
                     ("a2", "# Std\n\nStandard sentence one. Standard sentence two.\n")):
        os.makedirs(os.path.join(out_dir, lv), exist_ok=True)
        with open(os.path.join(out_dir, lv, "article.md"), "w", encoding="utf-8", newline="") as f:
            f.write(text)


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def fake_result(level, status="OK", n_issues=0):
    return {"status": status, "reason": None if status == "OK" else "x", "issues": [{}] * n_issues, "rf_run_id": "rfTEST",
            "article_level": level}


class RiskFlagGlueTests(unittest.TestCase):
    def setUp(self):
        self.out = make_out()
        write_articles(self.out)
        write_w1_ja_writer(self.out, producer="trial_fixture")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_passes_level_paths_producer_label_and_budget_hook(self):
        seen = {}

        def fake_rf(**kw):
            seen.update(kw)
            return fake_result(kw["article_level"])

        with mock.patch.object(runner.rf, "run_risk_flagger", side_effect=fake_rf), \
                mock.patch.object(runner.rq, "save_queue", return_value={"saved": True}) as m_save, \
                mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0) as m_budget:
            r = runner.run_post_en_risk_flag(self.out, "a2", 55.0, run_label="LBL")
            seen["budget_check"]()
        self.assertEqual(seen["article_path"], f"{self.out}/a2/article.md")
        self.assertEqual(seen["ledger_path"], f"{self.out}/research_ledger/verified_fact_ledger.txt")   # 完全台帳
        self.assertEqual(seen["article_level"], "a2")
        self.assertEqual(seen["article_id"], rq.derive_article_id(self.out))
        self.assertEqual(seen["producer"], "trial_fixture")
        self.assertEqual(seen["run_label"], "LBL")
        self.assertEqual(seen["out_dir"], self.out)
        self.assertNotIn("call_fn", seen)                  # 実API経路(default_call_fn)を使う
        self.assertEqual(m_budget.call_args.args[:2], (self.out, 55.0))   # budget_checkフック=efam.assert_budget_ok
        m_save.assert_called_once()
        self.assertEqual(r["status"], "OK")

    def test_rf_unavailable_and_partial_are_nonblocking(self):
        for st in ("RF_UNAVAILABLE", "PARTIAL"):
            with mock.patch.object(runner.rf, "run_risk_flagger", return_value=fake_result("b1b", st)), \
                    mock.patch.object(runner.rq, "save_queue", return_value={"saved": True}):
                r = runner.run_post_en_risk_flag(self.out, "b1b", 55.0)
            self.assertEqual(r["status"], st)

    def test_unexpected_rf_exception_is_nonblocking(self):
        with mock.patch.object(runner.rf, "run_risk_flagger", side_effect=ValueError("boom")):
            r = runner.run_post_en_risk_flag(self.out, "b1b", 55.0)
        self.assertEqual(r["status"], "RF_UNAVAILABLE")
        self.assertIn("ValueError", r["reason"])

    def test_queue_save_failure_is_nonblocking(self):
        with mock.patch.object(runner.rf, "run_risk_flagger", return_value=fake_result("b1b")), \
                mock.patch.object(runner.rq, "save_queue", return_value={"saved": False, "fallback": True, "error": "disk"}):
            r = runner.run_post_en_risk_flag(self.out, "b1b", 55.0)
        self.assertFalse(r["queue"]["saved"])

    def test_budget_stop_and_article_modified_propagate(self):
        with mock.patch.object(runner.rf, "run_risk_flagger", side_effect=runner.rf.BudgetCheckStop("RuntimeError: cap")):
            with self.assertRaises(runner.rf.BudgetCheckStop):
                runner.run_post_en_risk_flag(self.out, "b1b", 1.0)
        with mock.patch.object(runner.rf, "run_risk_flagger", side_effect=runner.rf.ArticleModifiedError("changed")):
            with self.assertRaises(runner.rf.ArticleModifiedError):
                runner.run_post_en_risk_flag(self.out, "b1b", 1.0)

    def test_article_modified_during_rf_or_queue_is_detected(self):
        p = f"{self.out}/b1b/article.md"

        def evil_rf(**kw):
            with open(p, "a", encoding="utf-8") as f:
                f.write("tampered")
            return fake_result("b1b")

        with mock.patch.object(runner.rf, "run_risk_flagger", side_effect=evil_rf), \
                mock.patch.object(runner.rq, "save_queue", return_value={"saved": True}):
            with self.assertRaises(runner.rf.ArticleModifiedError):
                runner.run_post_en_risk_flag(self.out, "b1b", 1.0)

    def test_real_rf_with_stub_api_keeps_article_sha_and_saves_queue(self):
        """実RF module(4条件逐次)をAPI stubで通し、記事sha不変・Queue保存・entry_point記録を確認。課金0。"""
        tmp_root = tempfile.mkdtemp(prefix="c2_queue_")
        calls = []

        def stub_call(model_key, model_id, system, user):
            calls.append((model_key, model_id))
            return ('{"flags":[]}', {"input_tokens": 10, "output_tokens": 5, "cached_tokens": 0}, "rid-%d" % len(calls), model_id)

        orig_save = rq.save_queue
        before = {lv: sha_file(f"{self.out}/{lv}/article.md") for lv in ("b1b", "a2")}
        try:
            with mock.patch.object(runner.rf, "default_call_fn", stub_call), \
                    mock.patch.object(runner.rq, "save_queue",
                                      side_effect=lambda res, out_dir=None: orig_save(res, out_dir=out_dir, root=tmp_root)), \
                    mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0), \
                    mock.patch.object(runner.rf.cl, "record"):
                r1 = runner.run_post_en_risk_flag(self.out, "b1b", 150.0, run_label="L")
                r2 = runner.run_post_en_risk_flag(self.out, "a2", 150.0, run_label="L")
            self.assertEqual({lv: sha_file(f"{self.out}/{lv}/article.md") for lv in ("b1b", "a2")}, before)
            self.assertEqual(len(calls), 8)                       # 2 Level x 4条件(逐次)
            self.assertEqual(r1["status"], "OK")
            self.assertEqual(r2["status"], "OK")
            idx = rq.read_index(tmp_root)
            self.assertEqual([e["article_level"] for e in idx], ["b1b", "a2"])
            self.assertTrue(all(e["producer"] == "trial_fixture" and e["run_label"] == "L" for e in idx))
            ep = json.load(open(os.path.join(self.out, "entry_point.json"), encoding="utf-8"))
            self.assertEqual(set(ep["risk_flagger"]), {"b1b", "a2"})
        finally:
            shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
