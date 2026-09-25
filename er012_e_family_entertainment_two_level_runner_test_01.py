# ============================================================
# er012_e_family_entertainment_two_level_runner_test_01.py
# NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01
# ============================================================
# er012_e_family_entertainment_two_level_runner_01.pyの単体テスト。実API
# 呼び出しは行わない(mock使用)。downstream(scaffold/tts/assemble)は
# 既存Production関数をmockし、本runner側のglue logic(Ledger reuse、
# writer stage deviation retry、budget guard、player row mapping)のみを
# 検証する。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er012_e_family_entertainment_two_level_runner_test_01 -v
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from dataclasses import dataclass, field
from unittest import mock

import er012_e_family_entertainment_two_level_runner_01 as runner


class ExtractTitleTests(unittest.TestCase):
    def test_extract_title_from_markdown_heading(self):
        self.assertEqual(runner._extract_title("# My Title\n\nBody here."), "My Title")

    def test_extract_title_missing_returns_empty(self):
        self.assertEqual(runner._extract_title("No heading here.\nJust text."), "")


class BudgetGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_assert_budget_ok_under_cap(self):
        with mock.patch.object(runner, "compute_cost_jpy_so_far", return_value=(10.0, {"openai": 10.0})):
            jpy = runner.assert_budget_ok(self.tmp_dir, 300.0, "note")
        self.assertEqual(jpy, 10.0)

    def test_assert_budget_ok_over_cap_raises(self):
        with mock.patch.object(runner, "compute_cost_jpy_so_far", return_value=(301.0, {"openai": 301.0})):
            with self.assertRaises(RuntimeError):
                runner.assert_budget_ok(self.tmp_dir, 300.0, "note")


class LedgerReuseTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_reuses_existing_ledger_file_without_new_build(self):
        reuse_src = os.path.join(self.tmp_dir, "existing_ledger.txt")
        with open(reuse_src, "w", encoding="utf-8") as f:
            f.write("[VERIFIED] FACT-001: something true.")
        out_dir = os.path.join(self.tmp_dir, "out")
        os.makedirs(out_dir, exist_ok=True)

        with mock.patch.object(runner, "build_ledger_for_topic") as mock_build:
            text = runner.load_or_build_ledger(client=None, out_dir=out_dir, topic="dummy topic",
                                                reuse_ledger_file=reuse_src)
        mock_build.assert_not_called()
        self.assertIn("FACT-001", text)
        self.assertTrue(os.path.exists(os.path.join(out_dir, "ledger", "verified_fact_ledger.txt")))

    def test_builds_new_ledger_when_no_reuse_file(self):
        out_dir = os.path.join(self.tmp_dir, "out2")
        os.makedirs(out_dir, exist_ok=True)
        with mock.patch.object(runner, "build_ledger_for_topic", return_value="[VERIFIED] X: y.") as mock_build:
            text = runner.load_or_build_ledger(client=object(), out_dir=out_dir, topic="dummy topic",
                                                reuse_ledger_file=None)
        mock_build.assert_called_once()
        self.assertEqual(text, "[VERIFIED] X: y.")

    def test_reuses_already_generated_ledger_in_out_dir(self):
        out_dir = os.path.join(self.tmp_dir, "out3")
        ledger_dir = os.path.join(out_dir, "ledger")
        os.makedirs(ledger_dir, exist_ok=True)
        with open(os.path.join(ledger_dir, "verified_fact_ledger.txt"), "w", encoding="utf-8") as f:
            f.write("[VERIFIED] ALREADY: built.")
        with mock.patch.object(runner, "build_ledger_for_topic") as mock_build:
            text = runner.load_or_build_ledger(client=None, out_dir=out_dir, topic="dummy",
                                                reuse_ledger_file=None)
        mock_build.assert_not_called()
        self.assertIn("ALREADY", text)


@dataclass
class _FakeWriterResult:
    text: str
    model_id_actual: str = "gpt-5.6-luna"
    model_id_requested: str = "gpt-5.6-luna"
    response_id: str = "resp_1"
    usage: dict = field(default_factory=dict)
    cost_usd: float = 0.001
    cost_jpy: float = 0.16
    attempts: int = 1
    retried: bool = False
    fallback_detected: bool = False
    structure_status: str = "STRUCTURE_PASS"
    elapsed_seconds: float = 1.0
    checks: dict = field(default_factory=dict)


ADVANCED_TEXT = (
    "# Advanced Title\n\nBody paragraph one.\n\nBody paragraph two.\n\n"
    "### First point\nFirst point body.\n\n### Second point\nSecond point body.\n\n"
    "## In one line\nOne closing sentence."
)
STANDARD_TEXT = (
    "# Standard Title\n\nSimple body one.\n\nSimple body two.\n\n"
    "### First point\nFirst point body.\n\n### Second point\nSecond point body.\n\n"
    "## In one line\nOne closing sentence."
)


def _deviation_result(status: str) -> dict:
    return {"parsed": {"overall_status": status}}


class RunWriterStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.theme = {"theme_id": "testslug", "out_dir": os.path.join(self.tmp_dir, "out"),
                      "topic": "test topic", "ledger_path": "unused"}

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_writer_stage_success_no_deviation_retry(self):
        adv_result = _FakeWriterResult(text=ADVANCED_TEXT)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_advanced_adaptation", return_value=adv_result) as m_adv, \
             mock.patch.object(runner.std_gen, "generate_standard_a2", return_value=std_result) as m_std, \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_COMPLIANT")) as m_dev, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)

        self.assertEqual(m_adv.call_count, 1)
        self.assertEqual(m_std.call_count, 1)
        self.assertEqual(m_dev.call_count, 2)  # advanced + standard, no retry
        self.assertEqual(evidence["advanced"]["deviation_overall_status"], "LEDGER_COMPLIANT")
        self.assertEqual(evidence["standard"]["deviation_overall_status"], "LEDGER_COMPLIANT")
        self.assertTrue(os.path.exists(os.path.join(self.theme["out_dir"], "b1b", "article.md")))
        self.assertTrue(os.path.exists(os.path.join(self.theme["out_dir"], "a2", "article.md")))

    def test_writer_stage_retries_once_on_major_deviation_then_passes(self):
        adv_result = _FakeWriterResult(text=ADVANCED_TEXT)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_advanced_adaptation", return_value=adv_result), \
             mock.patch.object(runner.std_gen, "generate_standard_a2", return_value=std_result), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                side_effect=[_deviation_result("LEDGER_DEVIATION"), _deviation_result("LEDGER_COMPLIANT"),
                                             _deviation_result("LEDGER_COMPLIANT")]) as m_dev, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)
        self.assertEqual(m_dev.call_count, 3)
        self.assertTrue(evidence["advanced"]["retried_for_deviation"])

    def test_writer_stage_stops_on_persistent_major_deviation(self):
        adv_result = _FakeWriterResult(text=ADVANCED_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_advanced_adaptation", return_value=adv_result), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_DEVIATION")), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(RuntimeError):
                runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                         ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)

    def test_writer_stage_only_standard_reads_existing_advanced_file(self):
        b1b_dir = os.path.join(self.theme["out_dir"], "b1b")
        os.makedirs(b1b_dir, exist_ok=True)
        with open(os.path.join(b1b_dir, "article.md"), "w", encoding="utf-8") as f:
            f.write(ADVANCED_TEXT)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.std_gen, "generate_standard_a2", return_value=std_result) as m_std, \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_COMPLIANT")), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only="standard")
        m_std.assert_called_once_with(ADVANCED_TEXT, client=mock.ANY)
        self.assertIn("standard", evidence)
        self.assertNotIn("advanced", evidence)


class TtsStageJapaneseTitleInjectionTests(unittest.TestCase):
    def test_run_tts_stage_registers_japanese_title_and_calls_run_theme(self):
        theme = {"theme_id": "injected_slug_test"}
        with mock.patch.object(runner.tts_gen, "run_theme", return_value={"ok": True}) as m_run:
            result = runner.run_tts_stage(theme, "日本語タイトル")
        self.assertEqual(runner.tts_gen.JAPANESE_TITLES["injected_slug_test"], "日本語タイトル")
        m_run.assert_called_once_with(theme)
        self.assertEqual(result, {"ok": True})


if __name__ == "__main__":
    unittest.main()
