# ============================================================
# er019_family_x_entertainment_production_runner_01_test_01.py
# NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01
# ============================================================
# er019_family_x_entertainment_production_runner_01.run_ja_writer()の単体
# テスト(JA Fact Check配線、audit保存、STOP時のrejected_ja_*.md保存)。
# 実API呼び出しは行わない(jaw.run_ja_writer_o_r1_r2をmockし、本runner側の
# glue logic[audit保存/STOP時ファイル保存]のみを検証する)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_entertainment_production_runner_01_test_01 -v
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er019_family_x_ja_writer_o_r1_r2_01 as jaw


def _check(status: str = "LEDGER_COMPLIANT") -> dict:
    return {"parsed": {"overall_status": status, "deviations": []},
            "prompt": "P", "raw_text": "R", "model": "gpt-5.6-luna", "response_id": "chk_1",
            "usage": {}, "elapsed_seconds": 0.1, "hook_aware": False}


def _success_result() -> dict:
    return {
        "stages": {
            "original": {"text": "Original text", "response_id": "r_orig", "model": "gpt-5.6-luna"},
            "r1": {"text": "R1 text", "response_id": "r_r1", "model": "gpt-5.6-luna"},
            "r2": {"text": "R2 text", "response_id": "r_r2", "model": "gpt-5.6-luna"},
        },
        "final_text": "R2 text",
        "chain_method": "previous_response_id",
        "verbatim_shas": {},
        "title": "Title",
        "fact_checks": {
            "original": {"checks": [_check()], "must_fix_applied": False, "must_fix_used": [],
                         "final_status": "LEDGER_COMPLIANT"},
            "r2": {"checks": [_check()], "must_fix_applied": False, "must_fix_used": [],
                   "final_status": "LEDGER_COMPLIANT"},
        },
    }


class RunJaWriterTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_success_saves_audit_deviation_checks_and_summary(self):
        with mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2", return_value=_success_result()):
            result = runner.run_ja_writer(client=object(), storyline_line="storyline",
                                           selected_fact_brief_text="brief", out_dir=self.tmp_dir,
                                           full_ledger_text="FULL LEDGER")
        self.assertEqual(result["ja_text"], "R2 text")
        stage_dir = os.path.join(self.tmp_dir, "ja_writer")
        self.assertTrue(os.path.exists(os.path.join(stage_dir, "original.md")))
        self.assertTrue(os.path.exists(os.path.join(stage_dir, "revision2.md")))
        self.assertTrue(os.path.exists(
            os.path.join(stage_dir, "audit", "deviation_checks", "ja_original_attempt1.json")))
        self.assertTrue(os.path.exists(
            os.path.join(stage_dir, "audit", "deviation_checks", "ja_r2_attempt1.json")))
        with open(os.path.join(stage_dir, "runtime_evidence.json"), encoding="utf-8") as f:
            evidence = json.load(f)
        self.assertIn("fact_checks_summary", evidence)
        self.assertEqual(evidence["fact_checks_summary"]["original"]["final_status"], "LEDGER_COMPLIANT")

    def test_stop_error_saves_rejected_text_and_audit(self):
        stop_error = jaw.JAFactCheckStopError(
            stage="original", message="[STOP] JA_FACT_CHECK_STOP: test",
            rejected_text="REJECTED TEXT", checks=[_check("LEDGER_DEVIATION")],
            must_fix_used=[{"fact_id": "F1", "claim_in_article": "c", "issue": "i", "explanation": "e"}],
        )
        with mock.patch.object(runner.jaw, "run_ja_writer_o_r1_r2", side_effect=stop_error):
            with self.assertRaises(RuntimeError):
                runner.run_ja_writer(client=object(), storyline_line="storyline",
                                      selected_fact_brief_text="brief", out_dir=self.tmp_dir,
                                      full_ledger_text="FULL LEDGER")
        stage_dir = os.path.join(self.tmp_dir, "ja_writer")
        rejected_path = os.path.join(stage_dir, "audit", "rejected_ja_original.md")
        self.assertTrue(os.path.exists(rejected_path))
        with open(rejected_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "REJECTED TEXT")
        self.assertTrue(os.path.exists(
            os.path.join(stage_dir, "audit", "deviation_checks", "ja_original_attempt1.json")))
        self.assertTrue(os.path.exists(
            os.path.join(stage_dir, "audit", "rejected_ja_original_must_fix.json")))


if __name__ == "__main__":
    unittest.main()
