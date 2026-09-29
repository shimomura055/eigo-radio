# ============================================================
# er019_family_x_ja_recheck_retry_01_test_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W6)
# ============================================================
# ja_source MAJOR(JARecheckRequiredError)発生時の暫定対応「案B」
# (English Deviation CheckがJA R2由来[origin=ja_source]MAJORを検出した
# 場合、その具体的な指摘をJA Writer O[er019_family_x_ja_writer_o_r1_r2_01.
# run_ja_writer_o_r1_r2]のOriginal段へmust-fixとして差し戻し、
# Original→R1→R2→Fact Checkの全体で1回だけJAを再生成し、Advanced/
# Standardを再実行、なおMAJORならSTOPする)の単体テスト。実装本体は
# er012_e_family_entertainment_two_level_runner_01.run_writer_stage()
# (薄いwrapper、_run_writer_stage_once()を包む)。実API呼び出しは一切
# 行わない(mock使用、費用¥0)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_ja_recheck_retry_01_test_01 -v
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from dataclasses import dataclass, field
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er012_e_family_entertainment_two_level_runner_01 as runner
import er019_family_x_ja_writer_o_r1_r2_01 as jaw


# ------------------------------------------------------------
# fixtures(er012_e_family_entertainment_two_level_runner_test_01.pyと
# 同型、本テストファイル単体で完結させるためあえて重複させる)
# ------------------------------------------------------------
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


ADVANCED_BODY = "Body paragraph one.\n\nBody paragraph two.\n\nBody paragraph three."
ADVANCED_TITLE = "Advanced Title"
ADVANCED_IN_ONE_LINE = "One closing sentence."

# recheck後(2回目)の生成結果は別内容にして、redoが実際に別呼び出しである
# ことを検証しやすくする。
ADVANCED_BODY_2 = "Fixed paragraph one.\n\nFixed paragraph two.\n\nFixed paragraph three."
ADVANCED_TITLE_2 = "Advanced Title Fixed"

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


def _ja_writer_success_result(final_text: str = "JA final text (recheck済み)") -> dict:
    return {
        "stages": {
            "original": {"text": "Original recheck text", "response_id": "r_orig2", "model": "gpt-5.6-luna"},
            "r1": {"text": "R1 recheck text", "response_id": "r_r1_2", "model": "gpt-5.6-luna"},
            "r2": {"text": final_text, "response_id": "r_r2_2", "model": "gpt-5.6-luna"},
        },
        "final_text": final_text,
        "chain_method": "previous_response_id",
        "verbatim_shas": jaw.verbatim_shas(),
        "title": "JA Title",
        "fact_checks": {
            "original": {"checks": [], "must_fix_applied": True, "must_fix_used": [],
                         "final_status": "LEDGER_COMPLIANT"},
            "r2": {"checks": [], "must_fix_applied": False, "must_fix_used": [],
                   "final_status": "LEDGER_COMPLIANT"},
        },
    }


class JaRecheckRetryTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.out_dir = os.path.join(self.tmp_dir, "out")
        self.theme = {"theme_id": "testslug", "out_dir": self.out_dir,
                      "topic": "test topic", "ledger_path": "unused"}
        os.makedirs(os.path.join(self.out_dir, "ja_writer"), exist_ok=True)
        for fname, content in (("original.md", "OLD ORIGINAL"), ("revision1.md", "OLD R1"),
                                ("revision2.md", "OLD R2 (pre-recheck)")):
            with open(os.path.join(self.out_dir, "ja_writer", fname), "w", encoding="utf-8") as f:
                f.write(content)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_ja_source_major_then_regenerate_once_then_completes(self):
        """1. ja_source MAJOR -> 2. JA must-fix差し戻し・1回だけ再生成 ->
        3〜5. 再Fact Check・再英訳・再Deviation Check -> COMPLIANTで完走。"""
        adv_result_1 = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        adv_result_2 = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE_2, body=ADVANCED_BODY_2)
        std_result = _FakeWriterResult(text=STANDARD_TEXT)
        ja_recheck_result = _ja_writer_success_result()

        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                side_effect=[adv_result_1, adv_result_2]) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                return_value=std_result) as m_std, \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                side_effect=[
                                    _deviation_result("LEDGER_DEVIATION",
                                                       deviations=[_major_deviation(origin="ja_source")]),
                                    _deviation_result("LEDGER_COMPLIANT"),
                                    _deviation_result("LEDGER_COMPLIANT"),
                                ]) as m_dev, \
             mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2",
                                return_value=ja_recheck_result) as m_jaw, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(
                client=object(), theme=self.theme, ja_text="日本語本文(旧)",
                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None,
                storyline_line="storyline", selected_fact_brief_text="brief")

        # JA Writer Oは1回だけ呼ばれる(無限retry禁止の直接証拠)。
        m_jaw.assert_called_once()
        call_kwargs = m_jaw.call_args.kwargs
        self.assertEqual(call_kwargs["original_must_fix"][0]["fact_id"], "F1")
        self.assertEqual(call_kwargs["full_ledger_text"], "[VERIFIED] X: y.")

        self.assertTrue(evidence["ja_recheck_used"])
        self.assertEqual(evidence["ja_recheck_attempts"], 1)
        self.assertEqual(evidence["advanced"]["deviation_overall_status"], "LEDGER_COMPLIANT")
        self.assertEqual(evidence["standard"]["deviation_overall_status"], "LEDGER_COMPLIANT")
        self.assertEqual(m_adv.call_count, 2)  # 1回目(MAJOR検知) + recheck後の再英訳
        self.assertEqual(m_std.call_count, 1)  # recheck後のみ(1回目はAdvancedでSTOPし未到達)

        with open(os.path.join(self.out_dir, "ja_writer", "revision2.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), ja_recheck_result["final_text"])

        audit_path = os.path.join(self.out_dir, "ja_writer", "audit", "ja_recheck_attempt1.json")
        self.assertTrue(os.path.exists(audit_path))
        with open(audit_path, encoding="utf-8") as f:
            audit = json.load(f)
        self.assertEqual(audit["outcome"], "REGENERATED")
        self.assertEqual(audit["trigger_stage"], "advanced")
        self.assertEqual(len(audit["major_deviations_ja_sourced"]), 1)
        self.assertIn("original.md", audit["pre_recheck_sha256"])

        result_path = os.path.join(self.out_dir, "ja_writer", "audit", "ja_recheck_attempt1_result.json")
        with open(result_path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["outcome"], "RESOLVED")

        with open(os.path.join(self.out_dir, "writer_run_summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        self.assertTrue(summary["ja_recheck_used"])
        self.assertEqual(summary["ja_recheck_attempts"], 1)

    def test_ja_source_major_persists_after_recheck_then_stops_no_second_regeneration(self):
        """再実行後もMAJOR -> STOP。JA Writer Oは1回しか呼ばれない
        (2回目のJA再生成が呼ばれない=無限retry禁止の証明)。"""
        adv_result_1 = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        adv_result_2 = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE_2, body=ADVANCED_BODY_2)
        ja_recheck_result = _ja_writer_success_result()

        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                side_effect=[adv_result_1, adv_result_2]) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                side_effect=[
                                    _deviation_result("LEDGER_DEVIATION",
                                                       deviations=[_major_deviation(origin="ja_source")]),
                                    _deviation_result("LEDGER_DEVIATION",
                                                       deviations=[_major_deviation(origin="ja_source",
                                                                                    fact_id="F2")]),
                                ]) as m_dev, \
             mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2",
                                return_value=ja_recheck_result) as m_jaw, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(runner.JARecheckRequiredError) as ctx:
                runner.run_writer_stage(
                    client=object(), theme=self.theme, ja_text="日本語本文(旧)",
                    ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None,
                    storyline_line="storyline", selected_fact_brief_text="brief")

        m_jaw.assert_called_once()  # 2回目のJA再生成が呼ばれていないことの直接証拠
        self.assertIn("ja_recheck_attempts=1", str(ctx.exception))
        result_path = os.path.join(self.out_dir, "ja_writer", "audit", "ja_recheck_attempt1_result.json")
        with open(result_path, encoding="utf-8") as f:
            result_audit = json.load(f)
        self.assertEqual(result_audit["outcome"], "STILL_MAJOR_AFTER_RECHECK")

    def test_standard_stage_ja_source_major_shares_same_one_time_budget(self):
        """Standard段でja_source MAJORが発生した場合も、同じ1回枠を消費して
        Advanced/Standardを再実行する(Advanced/Standard合計でJA再生成は
        1回)。"""
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        std_result_1 = _FakeWriterResult(text=STANDARD_TEXT)
        std_result_2 = _FakeWriterResult(text=STANDARD_TEXT)
        ja_recheck_result = _ja_writer_success_result()

        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result) as m_adv, \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.std_gen, "generate_family_x_standard_a2_no_heading",
                                side_effect=[std_result_1, std_result_2]) as m_std, \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                side_effect=[
                                    _deviation_result("LEDGER_COMPLIANT"),
                                    _deviation_result("LEDGER_DEVIATION",
                                                       deviations=[_major_deviation(origin="ja_source")]),
                                    _deviation_result("LEDGER_COMPLIANT"),
                                    _deviation_result("LEDGER_COMPLIANT"),
                                ]) as m_dev, \
             mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2",
                                return_value=ja_recheck_result) as m_jaw, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(
                client=object(), theme=self.theme, ja_text="日本語本文(旧)",
                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None,
                storyline_line="storyline", selected_fact_brief_text="brief")

        m_jaw.assert_called_once()
        self.assertTrue(evidence["ja_recheck_used"])
        audit_path = os.path.join(self.out_dir, "ja_writer", "audit", "ja_recheck_attempt1.json")
        with open(audit_path, encoding="utf-8") as f:
            audit = json.load(f)
        self.assertEqual(audit["trigger_stage"], "standard")
        self.assertEqual(m_std.call_count, 2)

    def test_translation_origin_major_retry_unchanged_no_ja_recheck(self):
        """既存のtranslation由来MAJOR must-fix retry(1回)は不変で、JA
        Writer Oは一切呼ばれない(storyline_line等を渡していても無関係)。"""
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
                                    _deviation_result("LEDGER_DEVIATION",
                                                       deviations=[_major_deviation(origin="translation")]),
                                    _deviation_result("LEDGER_COMPLIANT", all_prior_issues_resolved=True),
                                    _deviation_result("LEDGER_COMPLIANT"),
                                ]), \
             mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2") as m_jaw, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            evidence = runner.run_writer_stage(
                client=object(), theme=self.theme, ja_text="日本語本文",
                ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None,
                storyline_line="storyline", selected_fact_brief_text="brief")
        m_jaw.assert_not_called()
        self.assertEqual(m_adv.call_count, 2)  # 既存の1回だけmust-fix retry(不変)
        self.assertFalse(evidence["ja_recheck_used"])
        self.assertEqual(evidence["ja_recheck_attempts"], 0)

    def test_ja_fact_check_stop_propagates_as_runtime_error(self):
        """JA再生成中のFact Check(JAFactCheckStopError)はそのままSTOPし、
        rejected本文とaudit記録を保存する(JAFactCheckStopErrorをそのまま
        伝播させず、RuntimeErrorへ変換してSTOPする既存方針と同型)。"""
        stop_error = jaw.JAFactCheckStopError(
            stage="r2", message="[STOP] JA_FACT_CHECK_STOP: test",
            rejected_text="REJECTED JA R2 TEXT", checks=[],
            must_fix_used=[{"fact_id": "F1", "claim_in_article": "c", "issue": "i", "explanation": "e"}],
        )
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result), \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result(
                                    "LEDGER_DEVIATION", deviations=[_major_deviation(origin="ja_source")])), \
             mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2", side_effect=stop_error) as m_jaw, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(RuntimeError) as ctx:
                runner.run_writer_stage(
                    client=object(), theme=self.theme, ja_text="日本語本文",
                    ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None,
                    storyline_line="storyline", selected_fact_brief_text="brief")
        self.assertNotIsInstance(ctx.exception, runner.JARecheckRequiredError)
        m_jaw.assert_called_once()
        rejected_path = os.path.join(self.out_dir, "ja_writer", "audit", "ja_recheck_rejected_r2.md")
        with open(rejected_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "REJECTED JA R2 TEXT")
        audit_path = os.path.join(self.out_dir, "ja_writer", "audit", "ja_recheck_attempt1.json")
        with open(audit_path, encoding="utf-8") as f:
            audit = json.load(f)
        self.assertEqual(audit["outcome"], "JA_FACT_CHECK_STOP")

    def test_no_ja_recheck_when_storyline_not_provided_backward_compat(self):
        """storyline_line/selected_fact_brief_textが渡されない場合(既定
        None)は、従来通りJARecheckRequiredErrorがそのまま伝播する(案B
        無効・後方互換、既存呼び出し元への影響なし)。"""
        adv_result = _FakeFaithfulTranslationResult(title=ADVANCED_TITLE, body=ADVANCED_BODY)
        with mock.patch.object(runner.adv_gen, "generate_family_x_faithful_translation",
                                return_value=adv_result), \
             mock.patch.object(runner.adv_gen, "generate_family_x_in_one_line",
                                side_effect=_fake_in_one_line), \
             mock.patch.object(runner.vfl01, "run_deviation_check",
                                return_value=_deviation_result(
                                    "LEDGER_DEVIATION", deviations=[_major_deviation(origin="ja_source")])), \
             mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2") as m_jaw, \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0):
            with self.assertRaises(runner.JARecheckRequiredError):
                runner.run_writer_stage(
                    client=object(), theme=self.theme, ja_text="日本語本文",
                    ledger_text="[VERIFIED] X: y.", budget_jpy=300.0, only=None)
        m_jaw.assert_not_called()


# ------------------------------------------------------------
# Checker Prompt本体・severity判定基準の不変性(sha256による証明)。
# ハッシュ値は本委任(W6)着手前に独立算出した既知値(er003_v1_en_direct_
# vfl_01_generate.pyは本委任で一切編集していない)。
# ------------------------------------------------------------
EXPECTED_DEVIATION_PROMPT_TEMPLATE_SHA256 = (
    "d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9")
EXPECTED_HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE_SHA256 = (
    "5fa3ab187dc3d89e76caf6ad753c9e65f73b23aa2286e6225c28fdd910441286")
EXPECTED_DEVIATION_FLAG_KEYS = [
    "changed_fact", "changed_scope", "changed_causality", "changed_certainty",
    "changed_number", "changed_actor", "changed_negation", "changed_comparison",
    "changed_time", "unsupported_new_claim",
]


class CheckerPromptSeverityUnchangedTests(unittest.TestCase):
    def test_deviation_prompt_template_sha256_unchanged(self):
        actual = hashlib.sha256(vfl01.DEVIATION_PROMPT_TEMPLATE.encode("utf-8")).hexdigest()
        self.assertEqual(actual, EXPECTED_DEVIATION_PROMPT_TEMPLATE_SHA256)

    def test_hook_aware_deviation_prompt_template_sha256_unchanged(self):
        actual = hashlib.sha256(vfl01.HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE.encode("utf-8")).hexdigest()
        self.assertEqual(actual, EXPECTED_HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE_SHA256)

    def test_deviation_flag_keys_unchanged(self):
        self.assertEqual(vfl01.DEVIATION_FLAG_KEYS, EXPECTED_DEVIATION_FLAG_KEYS)


if __name__ == "__main__":
    unittest.main()
