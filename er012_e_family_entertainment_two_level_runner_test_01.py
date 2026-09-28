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
import subprocess
import sys
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


@dataclass
class _FakeFaithfulTranslationResult:
    """FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1): adv_gen.
    FamilyXFaithfulTranslationResultのtitle/body形状に合わせたfake(旧
    _FakeWriterResultは.textのみでStandard側にのみ引き続き使う)。"""
    title: str
    body: str
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


# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1): 新記事構造(途中Heading
# 廃止、###×2は使わない)のfixture。段落境界3分割が成立するよう本文は
# 3段落以上にする。
ADVANCED_BODY = "Body paragraph one.\n\nBody paragraph two.\n\nBody paragraph three."
ADVANCED_TITLE = "Advanced Title"
ADVANCED_IN_ONE_LINE = "One closing sentence."
ADVANCED_TEXT = f"# {ADVANCED_TITLE}\n\n{ADVANCED_BODY}\n\n## In one line\n{ADVANCED_IN_ONE_LINE}"

STANDARD_TEXT = (
    "# Standard Title\n\nSimple body one.\n\nSimple body two.\n\nSimple body three.\n\n"
    "## In one line\nOne closing sentence."
)


def _fake_in_one_line(client, title, body, **kwargs):
    return {"text": ADVANCED_IN_ONE_LINE, "model": "gpt-5.6-luna", "response_id": "resp_iol",
            "usage": {}, "cost_usd": 0.0001, "cost_jpy": 0.016, "elapsed_seconds": 0.1}


def _deviation_result(status: str, deviations: list | None = None,
                       all_prior_issues_resolved: bool | None = None) -> dict:
    parsed = {"overall_status": status, "deviations": deviations or []}
    if all_prior_issues_resolved is not None:
        parsed["all_prior_issues_resolved"] = all_prior_issues_resolved
    return {"parsed": parsed}


def _major_deviation(origin: str = "translation", fact_id: str = "F1") -> dict:
    return {
        "claim_in_article": "claim X", "issue": "issue X", "severity": "MAJOR",
        "explanation": "expl X", "related_fact_id": fact_id, "origin": origin,
    }


class RunWriterStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.theme = {"theme_id": "testslug", "out_dir": os.path.join(self.tmp_dir, "out"),
                      "topic": "test topic", "ledger_path": "unused"}

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_writer_stage_success_no_deviation_retry(self):
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result) as m_std, \
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
        self.assertFalse(evidence["advanced"]["paragraph_retried"])
        self.assertFalse(evidence["standard"]["paragraph_retried"])
        self.assertTrue(os.path.exists(os.path.join(self.theme["out_dir"], "b1b", "article.md")))
        self.assertTrue(os.path.exists(os.path.join(self.theme["out_dir"], "a2", "article.md")))
        # OPEN-228: 新構造はheadingを持たない(旧h3見出しcontractへの復帰なし)。
        with open(os.path.join(self.theme["out_dir"], "b1b", "article.md"), encoding="utf-8") as f:
            b1b_article = f.read()
        self.assertNotIn("### ", b1b_article)

    def test_writer_stage_retries_once_on_major_deviation_then_passes(self):
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                side_effect=[
                                    _deviation_result("LEDGER_DEVIATION", deviations=[_major_deviation()]),
                                    _deviation_result("LEDGER_COMPLIANT", all_prior_issues_resolved=True),
                                    _deviation_result("LEDGER_COMPLIANT"),
                                ]) as m_dev, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)
        self.assertEqual(m_dev.call_count, 3)
        self.assertTrue(evidence["advanced"]["retried_for_deviation"])
        # 2回目(retry)呼び出しはmust_fix/prior_issuesを渡していること。
        self.assertEqual(m_adv.call_count, 2)
        retry_kwargs = m_adv.call_args_list[1].kwargs
        self.assertEqual(len(retry_kwargs.get("must_fix")), 1)
        self.assertEqual(retry_kwargs["must_fix"][0]["fact_id"], "F1")
        retry_check_kwargs = m_dev.call_args_list[1].kwargs
        self.assertEqual(len(retry_check_kwargs.get("prior_issues")), 1)

    def test_writer_stage_stops_on_persistent_major_deviation(self):
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result), \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_DEVIATION", deviations=[_major_deviation()])), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(RuntimeError):
                runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                         ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)

    def test_writer_stage_ja_recheck_required_stop_no_blind_retry(self):
        """NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01: English MAJORが
        origin=ja_source(JA R2由来)と判定された場合、Englishを盲目的に
        再生成せずJARecheckRequiredError(RuntimeErrorのサブクラス)でSTOPする
        こと(generate_family_x_faithful_translationは1回しか呼ばれない)。"""
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result(
                                    "LEDGER_DEVIATION", deviations=[_major_deviation(origin="ja_source")])), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(runner.JARecheckRequiredError):
                runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                         ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)
        self.assertEqual(m_adv.call_count, 1)

    def test_writer_stage_only_standard_reads_existing_advanced_file(self):
        b1b_dir = os.path.join(self.theme["out_dir"], "b1b")
        os.makedirs(b1b_dir, exist_ok=True)
        with open(os.path.join(b1b_dir, "article.md"), "w", encoding="utf-8") as f:
            f.write(ADVANCED_TEXT)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result) as m_std, \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_COMPLIANT")), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only="standard")
        m_std.assert_called_once_with(ADVANCED_TEXT, client=mock.ANY)
        self.assertIn("standard", evidence)
        self.assertNotIn("advanced", evidence)

    def test_writer_run_summary_json_merges_across_separate_only_calls(self):
        """NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01(Fable差し戻し1回目、
        Gate 3 #13): run_writer_stage(only="advanced")の後にrun_writer_stage(
        only="standard")を別呼び出しした場合でも、writer_run_summary.jsonへ
        両stageのevidenceキーが両方残ること(旧実装は後勝ち上書きでadvancedキーが
        消えていた)を検証する。"""
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        summary_path = os.path.join(self.theme["out_dir"], "writer_run_summary.json")

        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result), \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_COMPLIANT")), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                     ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only="advanced")

        with open(summary_path, encoding="utf-8") as f:
            summary_after_advanced = json.load(f)
        self.assertIn("advanced", summary_after_advanced)
        self.assertNotIn("standard", summary_after_advanced)

        with mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result("LEDGER_COMPLIANT")), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                     ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only="standard")

        with open(summary_path, encoding="utf-8") as f:
            summary_after_standard = json.load(f)
        self.assertIn("advanced", summary_after_standard,
                       "standard単独呼び出し後もadvancedキーが残らなければならない(マージ保存)")
        self.assertIn("standard", summary_after_standard)


class TtsModeCliTests(unittest.TestCase):
    """PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01: --tts-modeの既定は
    STANDARD(PM_GOVERNANCE.md 7-1)であり、BATCH指定時は--batch-reasonが
    必須であることを検証する(実API呼び出し・実TTS生成は行わない)。"""

    def test_default_tts_mode_is_standard(self):
        parser = runner.build_arg_parser()
        args = parser.parse_args([
            "--ja-article", "dummy.md", "--slug", "sewer", "--out-dir", "dummy_out",
        ])
        self.assertEqual(args.tts_mode, "STANDARD")
        self.assertIsNone(args.batch_reason)

    def test_explicit_batch_mode_with_reason_parses_ok(self):
        parser = runner.build_arg_parser()
        args = parser.parse_args([
            "--ja-article", "dummy.md", "--slug", "sewer", "--out-dir", "dummy_out",
            "--tts-mode", "BATCH", "--batch-reason", "PM_GOVERNANCE 7-2(1) Batch固有挙動の検証",
        ])
        self.assertEqual(args.tts_mode, "BATCH")
        self.assertEqual(args.batch_reason, "PM_GOVERNANCE 7-2(1) Batch固有挙動の検証")

    def test_invalid_tts_mode_value_rejected_by_argparse(self):
        parser = runner.build_arg_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([
                "--ja-article", "dummy.md", "--slug", "sewer", "--out-dir", "dummy_out",
                "--tts-mode", "SOMETHING_ELSE",
            ])

    def test_batch_mode_without_reason_errors_via_subprocess(self):
        script = os.path.join(os.path.dirname(runner.__file__),
                               "er012_e_family_entertainment_two_level_runner_01.py")
        result = subprocess.run(
            [sys.executable, script,
             "--ja-article", "dummy.md", "--slug", "sewer", "--out-dir", "dummy_out",
             "--tts-mode", "BATCH"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--batch-reason", result.stderr)


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
