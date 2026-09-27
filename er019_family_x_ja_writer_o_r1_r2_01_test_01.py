# ============================================================
# er019_family_x_ja_writer_o_r1_r2_01_test_01.py
# NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01
# ============================================================
# er019_family_x_ja_writer_o_r1_r2_01.pyの単体テスト。実API呼び出しは
# 行わない(writer呼び出しはfake client、Fact Check
# [vfl01.run_deviation_check]はmock.patch.objectで直接差し替える)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_ja_writer_o_r1_r2_01_test_01 -v
# ============================================================
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

import er019_family_x_ja_writer_o_r1_r2_01 as jaw


def _fake_response(text: str, model: str = "gpt-5.6-luna", response_id: str = "resp_1"):
    return SimpleNamespace(output_text=text, model=model, id=response_id)


class _FakeResponses:
    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        item = self._outputs.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class _FakeClient:
    def __init__(self, outputs):
        self.responses = _FakeResponses(outputs)


def _check(status: str, major_devs: list | None = None,
           all_prior_issues_resolved: bool | None = None) -> dict:
    parsed = {"overall_status": status, "deviations": major_devs or []}
    if all_prior_issues_resolved is not None:
        parsed["all_prior_issues_resolved"] = all_prior_issues_resolved
    return {"parsed": parsed,
            "prompt": "P", "raw_text": "R", "model": "gpt-5.6-luna", "response_id": "chk_1",
            "usage": {}, "elapsed_seconds": 0.1, "hook_aware": False}


def _major(fact_id="F1"):
    return {"claim_in_article": "claim", "issue": "issue", "severity": "MAJOR",
            "explanation": "expl", "related_fact_id": fact_id}


class BackwardCompatNoLedgerTests(unittest.TestCase):
    def test_no_full_ledger_text_skips_fact_check_entirely(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check") as m_check:
            result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text")
        m_check.assert_not_called()
        self.assertEqual(len(client.responses.calls), 3)
        self.assertNotIn("fact_checks", result)
        self.assertEqual(result["final_text"], "R2 text")


class OriginalFactCheckTests(unittest.TestCase):
    def test_original_pass_no_must_fix(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check",
                                side_effect=[_check("LEDGER_COMPLIANT"), _check("LEDGER_COMPLIANT")]) as m_check:
            result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text",
                                                full_ledger_text="FULL LEDGER TEXT")
        self.assertEqual(m_check.call_count, 2)
        self.assertEqual(len(client.responses.calls), 3)
        self.assertFalse(result["fact_checks"]["original"]["must_fix_applied"])
        self.assertFalse(result["fact_checks"]["r2"]["must_fix_applied"])
        self.assertEqual(result["stages"]["original"]["text"], "Original text")

    def test_original_major_then_must_fix_then_pass(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("Original text FIXED", response_id="r_orig_mf"),
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check",
                                side_effect=[
                                    _check("LEDGER_DEVIATION", [_major()]),
                                    _check("LEDGER_COMPLIANT", all_prior_issues_resolved=True),
                                    _check("LEDGER_COMPLIANT"),
                                ]) as m_check:
            result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text",
                                                full_ledger_text="FULL LEDGER TEXT")
        self.assertEqual(m_check.call_count, 3)
        self.assertEqual(len(client.responses.calls), 4)
        self.assertTrue(result["fact_checks"]["original"]["must_fix_applied"])
        self.assertEqual(result["stages"]["original"]["text"], "Original text FIXED")
        self.assertEqual(result["stages"]["original"]["response_id"], "r_orig_mf")
        self.assertEqual(len(result["fact_checks"]["original"]["must_fix_used"]), 1)
        self.assertEqual(result["fact_checks"]["original"]["must_fix_used"][0]["fact_id"], "F1")
        # R1がmust-fix後のresponse_idから連鎖していること(previous_response_id)。
        r1_call = client.responses.calls[2]
        self.assertEqual(r1_call["previous_response_id"], "r_orig_mf")
        # retry checkにはprior_issues(前回のmust_fix内容)が渡されていること。
        retry_check_kwargs = m_check.call_args_list[1].kwargs
        self.assertEqual(len(retry_check_kwargs.get("prior_issues")), 1)

    def test_original_major_persists_raises_stop_error(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("Original text STILL BAD", response_id="r_orig_mf"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check",
                                side_effect=[
                                    _check("LEDGER_DEVIATION", [_major()]),
                                    _check("LEDGER_DEVIATION", [_major()]),
                                ]):
            with self.assertRaises(jaw.JAFactCheckStopError) as ctx:
                jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text",
                                           full_ledger_text="FULL LEDGER TEXT")
        self.assertEqual(ctx.exception.stage, "original")
        self.assertEqual(ctx.exception.rejected_text, "Original text STILL BAD")

    def test_original_overall_compliant_but_prior_issue_unresolved_still_stops(self):
        # NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01 要件3: overall_status
        # だけがLEDGER_COMPLIANTでも、prior_issues_resolvedが未解消ならSTOPする
        # (Checkerの自己申告overall_statusだけに頼らない安全側判定)。
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("Original text STILL BAD", response_id="r_orig_mf"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check",
                                side_effect=[
                                    _check("LEDGER_DEVIATION", [_major()]),
                                    _check("LEDGER_COMPLIANT", all_prior_issues_resolved=False),
                                ]):
            with self.assertRaises(jaw.JAFactCheckStopError) as ctx:
                jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text",
                                           full_ledger_text="FULL LEDGER TEXT")
        self.assertEqual(ctx.exception.stage, "original")
        self.assertEqual(len(ctx.exception.checks), 2)


class R2FactCheckTests(unittest.TestCase):
    def test_r2_major_then_must_fix_then_pass(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
            _fake_response("R2 text FIXED", response_id="r_r2_mf"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check",
                                side_effect=[
                                    _check("LEDGER_COMPLIANT"),  # original
                                    _check("LEDGER_DEVIATION", [_major()]),  # r2 attempt1
                                    _check("LEDGER_COMPLIANT", all_prior_issues_resolved=True),  # r2 attempt2
                                ]) as m_check:
            result = jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text",
                                                full_ledger_text="FULL LEDGER TEXT")
        self.assertEqual(m_check.call_count, 3)
        self.assertEqual(len(client.responses.calls), 4)
        self.assertTrue(result["fact_checks"]["r2"]["must_fix_applied"])
        self.assertEqual(result["stages"]["r2"]["text"], "R2 text FIXED")
        self.assertEqual(result["final_text"], "R2 text FIXED")
        # must-fix retryはR1からのrevisionとして連鎖する(previous_response_id=r1のid)。
        must_fix_call = client.responses.calls[3]
        self.assertEqual(must_fix_call["previous_response_id"], "r_r1")
        retry_check_kwargs = m_check.call_args_list[2].kwargs
        self.assertEqual(len(retry_check_kwargs.get("prior_issues")), 1)

    def test_r2_major_persists_raises_stop_error(self):
        client = _FakeClient([
            _fake_response("Original text", response_id="r_orig"),
            _fake_response("R1 text", response_id="r_r1"),
            _fake_response("R2 text", response_id="r_r2"),
            _fake_response("R2 text STILL BAD", response_id="r_r2_mf"),
        ])
        with mock.patch.object(jaw.vfl01, "run_deviation_check",
                                side_effect=[
                                    _check("LEDGER_COMPLIANT"),
                                    _check("LEDGER_DEVIATION", [_major()]),
                                    _check("LEDGER_DEVIATION", [_major()]),
                                ]):
            with self.assertRaises(jaw.JAFactCheckStopError) as ctx:
                jaw.run_ja_writer_o_r1_r2(client, "storyline", "brief text",
                                           full_ledger_text="FULL LEDGER TEXT")
        self.assertEqual(ctx.exception.stage, "r2")
        self.assertEqual(ctx.exception.rejected_text, "R2 text STILL BAD")


class BuildMustFixBlockTests(unittest.TestCase):
    def test_block_contains_fact_id_claim_issue_explanation_and_ledger(self):
        must_fix = [{"fact_id": "F1", "claim_in_article": "claim-X", "issue": "issue-X",
                     "explanation": "expl-X"}]
        block = jaw.build_must_fix_block(must_fix, "FULL LEDGER TEXT HERE")
        self.assertIn("F1", block)
        self.assertIn("claim-X", block)
        self.assertIn("issue-X", block)
        self.assertIn("expl-X", block)
        self.assertIn("FULL LEDGER TEXT HERE", block)


if __name__ == "__main__":
    unittest.main()
