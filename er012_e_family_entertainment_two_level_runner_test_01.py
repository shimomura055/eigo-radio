# ============================================================
# er012_e_family_entertainment_two_level_runner_test_01.py
# NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01
# ============================================================
# er012_e_family_entertainment_two_level_runner_01.pyの単体テスト。実API
# 呼び出しは行わない(mock使用)。downstream(scaffold/tts/assemble)は
# 既存Production関数をmockし、本runner側のglue logic(Ledger reuse、
# writer stage(段落3分割retry・M1(a)・S3-2観測記録)、budget guard、
# player row mapping、U-2 CLI封鎖)のみを検証する。
# RISK-FLAGGER-PRODUCTION-WIRING-01 C2(2026-10-10): 旧Fact Checker(各段の台帳照合・
# 指摘起点の再生成/STOP・JA差し戻し)は物理削除したため、そのtestは削除した
# (旧Checker不到達はer053_c2_old_checker_removal_test_01.pyで検証)。
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


class WebSearchCostGuardTests(unittest.TestCase):
    """OPEN-242: 予算ガード累計にweb_search tool課金を計上する。"""

    def _log(self, recs):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        path = os.path.join(d, "raw_usage_log.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r) + chr(10))
        return path

    def test_web_search_calls_added(self):
        base = {"provider": "openai", "model_id": "gpt-6-luna", "input_tokens": 0, "output_tokens": 0}
        j0, _ = runner.compute_cost_jpy_so_far(self._log([dict(base)]))
        j9, _ = runner.compute_cost_jpy_so_far(self._log([dict(base, web_search_call_count=9)]))
        self.assertEqual(j0, 0.0)
        self.assertAlmostEqual(j9, 9 * 10.0 / 1000 * runner.USD_JPY, places=6)

    def test_web_search_price_missing_fails_closed(self):
        path = self._log([{"provider": "openai", "model_id": "gpt-6-luna", "web_search_call_count": 1}])
        with mock.patch.object(runner, "PRICING_SNAPSHOT_PATH", self._pricing_without_ws()):
            with self.assertRaises(runner.PricingNotFoundError):
                runner.compute_cost_jpy_so_far(path)

    def _pricing_without_ws(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        p = os.path.join(d, "pricing.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"prices": [{"provider": "openai", "model": "gpt-6-luna", "meter": "input_tokens", "price": 1.0},
                                  {"provider": "openai", "model": "gpt-6-luna", "meter": "output_tokens", "price": 1.0}]}, f)
        return p


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


class RunWriterStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.theme = {"theme_id": "testslug", "out_dir": os.path.join(self.tmp_dir, "out"),
                      "topic": "test topic", "ledger_path": "unused"}

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _forbid_old_checker(self):
        def _boom(*a, **k):
            raise AssertionError("旧Checker(vfl01.run_deviation_check)が呼ばれた")
        return mock.patch.object(runner.vfl01, "run_deviation_check", side_effect=_boom)

    def test_writer_stage_success_no_old_checker_call(self):
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result) as m_std, \
             self._forbid_old_checker() as m_dev, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)

        self.assertEqual(m_adv.call_count, 1)
        self.assertEqual(m_std.call_count, 1)
        m_dev.assert_not_called()
        for lv in ("advanced", "standard"):
            for dead in ("deviation_overall_status", "retried_for_deviation", "must_fix_used"):
                self.assertNotIn(dead, evidence[lv])
        self.assertFalse(evidence["advanced"]["paragraph_retried"])
        self.assertFalse(evidence["standard"]["paragraph_retried"])
        for lv in ("b1b", "a2"):
            self.assertTrue(os.path.exists(os.path.join(self.theme["out_dir"], lv, "article.md")))
            self.assertFalse(os.path.exists(os.path.join(self.theme["out_dir"], lv, "audit", "deviation_check.json")))
            self.assertFalse(os.path.isdir(os.path.join(self.theme["out_dir"], lv, "audit", "deviation_checks")))
        # OPEN-228: 新構造はheadingを持たない(旧h3見出しcontractへの復帰なし)。
        with open(os.path.join(self.theme["out_dir"], "b1b", "article.md"), encoding="utf-8") as f:
            b1b_article = f.read()
        self.assertNotIn("### ", b1b_article)

    def test_m1a_in_one_line_always_gets_ja_text_and_ledger_advanced_only(self):
        """M1(a)無条件ON(環境変数なし): Advancedの「In one line」生成は常にja_text+ledger_textを渡す。Standardは呼ばない。"""
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        env = {k: v for k, v in os.environ.items() if not k.startswith("OPEN243")}
        with mock.patch.dict(os.environ, env, clear=True), \
             mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation", return_value=adv_result), \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line", side_effect=_fake_in_one_line) as m_iol, \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading", return_value=std_result), \
             self._forbid_old_checker(), mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            runner.run_writer_stage(client=object(), theme=self.theme, ja_text="JA-R2-TEXT",
                                     ledger_text="LEDGER-TEXT", budget_jpy=300.0, only=None)
        self.assertEqual(m_iol.call_count, 1)        # Advancedの初回のみ(Standardは呼ばない)
        kw = m_iol.call_args.kwargs
        self.assertEqual(kw.get("ja_text"), "JA-R2-TEXT")
        self.assertEqual(kw.get("ledger_text"), "LEDGER-TEXT")

    def test_paragraph_retry_technical_qa_still_works_and_uses_m1a(self):
        """技術QA維持: 3分割不能なら段落保持must-fixで1回だけ再生成(M1(a)の「In one line」も同じ関数で再生成)。"""
        few = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body="Only one paragraph.")
        ok = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation", side_effect=[few, ok]) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line", side_effect=_fake_in_one_line) as m_iol, \
             self._forbid_old_checker() as m_dev, mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            ev = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="JA", ledger_text="L",
                                          budget_jpy=300.0, only="advanced")
        self.assertEqual(m_adv.call_count, 2)
        self.assertEqual(m_adv.call_args_list[1].kwargs.get("must_fix"), runner._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        self.assertEqual(m_iol.call_count, 2)
        for c in m_iol.call_args_list:
            self.assertEqual(c.kwargs.get("ja_text"), "JA")
            self.assertEqual(c.kwargs.get("ledger_text"), "L")
        m_dev.assert_not_called()
        self.assertTrue(ev["advanced"]["paragraph_retried"])

    def test_paragraph_retry_persistent_stops(self):
        few = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body="Only one paragraph.")
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation", return_value=few) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line", side_effect=_fake_in_one_line), \
             self._forbid_old_checker(), mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(RuntimeError) as cm:
                runner.run_writer_stage(client=object(), theme=self.theme, ja_text="JA", ledger_text="L",
                                         budget_jpy=300.0, only="advanced")
        self.assertIn("[STOP]", str(cm.exception))
        self.assertEqual(m_adv.call_count, 2)        # 初回+段落retry1回のみ(上限不変)

    def test_budget_guard_still_called_per_stage(self):
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation", return_value=adv_result), \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line", side_effect=_fake_in_one_line), \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading", return_value=std_result), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0) as m_budget:
            runner.run_writer_stage(client=object(), theme=self.theme, ja_text="JA", ledger_text="L",
                                     budget_jpy=300.0, only=None)
        self.assertEqual(m_budget.call_count, 2)

    def test_standard_records_derived_from_advanced_sha256_observation_only(self):
        """S3-2: Standardの派生元Advanced英文のsha256を観測記録(判定・STOPには使わない)。"""
        b1b_dir = os.path.join(self.theme["out_dir"], "b1b")
        os.makedirs(b1b_dir, exist_ok=True)
        with open(os.path.join(b1b_dir, "article.md"), "w", encoding="utf-8") as f:
            f.write(ADVANCED_TEXT)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading", return_value=std_result), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            ev = runner.run_writer_stage(client=object(), theme=self.theme, ja_text="JA", ledger_text="L",
                                          budget_jpy=300.0, only="standard")
        expect = runner.sha256_text(ADVANCED_TEXT)
        self.assertEqual(ev["standard"]["derived_from_advanced_sha256"], expect)
        rec = json.load(open(os.path.join(self.theme["out_dir"], "a2", "audit", "derived_from_advanced_sha256.json"),
                             encoding="utf-8"))
        self.assertEqual(rec["derived_from_advanced_sha256"], expect)
        self.assertEqual(rec["standard_article_sha256"], runner.sha256_text(STANDARD_TEXT))

    def test_writer_stage_only_standard_reads_existing_advanced_file(self):
        b1b_dir = os.path.join(self.theme["out_dir"], "b1b")
        os.makedirs(b1b_dir, exist_ok=True)
        with open(os.path.join(b1b_dir, "article.md"), "w", encoding="utf-8") as f:
            f.write(ADVANCED_TEXT)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        with mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result) as m_std, \
             self._forbid_old_checker(), \
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
             self._forbid_old_checker(), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                     ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only="advanced")

        with open(summary_path, encoding="utf-8") as f:
            summary_after_advanced = json.load(f)
        self.assertIn("advanced", summary_after_advanced)
        self.assertNotIn("standard", summary_after_advanced)

        with mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result), \
             self._forbid_old_checker(), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            runner.run_writer_stage(client=object(), theme=self.theme, ja_text="日本語本文",
                                     ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only="standard")

        with open(summary_path, encoding="utf-8") as f:
            summary_after_standard = json.load(f)
        self.assertIn("advanced", summary_after_standard,
                       "standard単独呼び出し後もadvancedキーが残らなければならない(マージ保存)")
        self.assertIn("standard", summary_after_standard)


class U2StandaloneCliBlockTests(unittest.TestCase):
    """U-2(ユーザー確定2026-10-10): er012_e単体CLIのFamily X writer経路(--ja-article / --stage writer|all /
    --regenerate-stage)を封鎖。契約検証もRFも通らずb1b/a2を作れる経路を残さない。"""

    def _args(self, *extra):
        return runner.build_arg_parser().parse_args(["--slug", "s", "--out-dir", "dummy_out", *extra])

    def test_ja_article_blocked(self):
        with self.assertRaises(RuntimeError) as cm:
            runner.guard_standalone_cli(self._args("--ja-article", "x.md"))
        self.assertIn("U-2", str(cm.exception))
        self.assertIn("RISK-FLAGGER-PRODUCTION-WIRING-01", str(cm.exception))

    def test_stage_writer_all_and_regenerate_blocked(self):
        for extra in (("--stage", "writer"), ("--stage", "all"), ("--regenerate-stage", "advanced"),
                      ("--regenerate-stage", "standard")):
            with self.assertRaises(RuntimeError, msg=str(extra)):
                runner.guard_standalone_cli(self._args(*extra))

    def test_ledger_stage_not_blocked(self):
        runner.guard_standalone_cli(self._args("--stage", "ledger"))   # 例外なし

    def test_subprocess_blocked_before_any_output(self):
        out = os.path.join(tempfile.mkdtemp(), "should_not_exist")
        script = os.path.join(os.path.dirname(runner.__file__), "er012_e_family_entertainment_two_level_runner_01.py")
        res = subprocess.run([sys.executable, script, "--ja-article", "dummy.md", "--slug", "s", "--out-dir", out],
                             capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("U-2", res.stderr)
        self.assertFalse(os.path.exists(out), "封鎖はファイル出力(out_dir作成)より前に行う")

    def test_no_writer_entry_in_main_source(self):
        import inspect
        src = inspect.getsource(runner.main)
        self.assertNotIn("run_writer_stage", src)
        self.assertNotIn("load_text(args.ja_article)", src)


class TtsModeCliTests(unittest.TestCase):
    """PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01: --tts-modeの既定は
    STANDARD(PM_GOVERNANCE.md 7-1)であり、BATCH指定時は--batch-reasonが
    必須であることを検証する(実API呼び出し・実TTS生成は行わない)。"""

    def test_default_tts_mode_is_standard(self):
        parser = runner.build_arg_parser()
        args = parser.parse_args([
            "--slug", "sewer", "--out-dir", "dummy_out",
        ])
        self.assertEqual(args.tts_mode, "STANDARD")
        self.assertIsNone(args.batch_reason)

    def test_explicit_batch_mode_with_reason_parses_ok(self):
        parser = runner.build_arg_parser()
        args = parser.parse_args([
            "--slug", "sewer", "--out-dir", "dummy_out",
            "--tts-mode", "BATCH", "--batch-reason", "PM_GOVERNANCE 7-2(1) Batch固有挙動の検証",
        ])
        self.assertEqual(args.tts_mode, "BATCH")
        self.assertEqual(args.batch_reason, "PM_GOVERNANCE 7-2(1) Batch固有挙動の検証")

    def test_invalid_tts_mode_value_rejected_by_argparse(self):
        parser = runner.build_arg_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([
                "--slug", "sewer", "--out-dir", "dummy_out",
                "--tts-mode", "SOMETHING_ELSE",
            ])

    def test_batch_mode_without_reason_errors_via_subprocess(self):
        script = os.path.join(os.path.dirname(runner.__file__),
                               "er012_e_family_entertainment_two_level_runner_01.py")
        result = subprocess.run(
            [sys.executable, script,
             "--slug", "sewer", "--out-dir", "dummy_out",
             "--tts-mode", "BATCH"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--batch-reason", result.stderr)


class TtsStageJapaneseTitleInjectionTests(unittest.TestCase):
    def test_run_tts_stage_fails_fast_open_228_closure(self):
        """FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W5、Opus L2所見
        MAJOR-4是正、2026-09-29、OPEN-228封鎖): run_tts_stage()(旧###
        見出し2つ前提のlegacy経路)は、Family Xのscaffold/tts/assemble/
        playerが正式にer019_family_x_audio_production_runner_01.pyへ
        移行したことに伴いfail-fastするようになった(以前はtts_gen.
        run_theme()を実際に呼んでいたが、新構造[見出しなし]article.mdとは
        非互換のまま残置されていたため、運用トラップだった)。API呼び出しは
        一切発生しない(RuntimeErrorが即座に送出される)。"""
        theme = {"theme_id": "injected_slug_test"}
        with mock.patch.object(runner.tts_gen, "run_theme", return_value={"ok": True}) as m_run:
            with self.assertRaises(RuntimeError):
                runner.run_tts_stage(theme, "日本語タイトル")
        m_run.assert_not_called()

    def test_run_scaffold_stage_fails_fast_open_228_closure(self):
        with self.assertRaises(RuntimeError):
            runner.run_scaffold_stage(None, {"theme_id": "x"})

    def test_run_assemble_stage_fails_fast_open_228_closure(self):
        with self.assertRaises(RuntimeError):
            runner.run_assemble_stage({"theme_id": "x", "out_dir": "dummy"})

    def test_build_player_html_fails_fast_open_228_closure(self):
        with self.assertRaises(RuntimeError):
            runner.build_player_html({"theme_id": "x", "out_dir": "dummy"}, "日本語タイトル")


if __name__ == "__main__":
    unittest.main()
