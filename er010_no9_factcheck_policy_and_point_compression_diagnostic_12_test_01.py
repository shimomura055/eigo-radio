# ============================================================
# er010_no9_factcheck_policy_and_point_compression_diagnostic_12_test_01.py
# ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12
# ============================================================
# ユーザー正式Decision: Fact Checkerのverdict="REVIEW_REQUIRED"は原則
# non-blocking advisory(記事生成・QA工程は継続、status=OKの判定材料に
# しない)。verdict="FAIL"(信頼できる情報と明確に矛盾)は引き続き
# blocking。この2つの分岐を、実LLM呼び出しを行わず(mockのみ)、
# run_one_patternの制御フローで検証する。

import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_articles_generate as gen


ARTICLE_SIMPLE = """# A Screen Before Every Tip

Digital tip screens now appear at many checkouts. Researchers studied how this changes behavior.

### Why this pattern shows up

Researchers noticed a jump right around a key price point.

### A second angle

Some customers say the pressure feels different in person.

## In one line...

A small design choice can change what people pay.
"""


def _fake_writer_result(article_text):
    return {"status": "STRUCTURE_PASS", "raw_text": article_text, "attempts": [{"status": "STRUCTURE_PASS"}]}


def _fake_point_overlap_no_flag(*args, **kwargs):
    return {"status": "OK", "report": {
        "point_one": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1}},
        "point_two": {"before_overlap": {"flagged": False, "overlap_ratio": 0.1}},
    }}


def _compliant_deviation_result():
    return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []}}


def _fake_fact_checker_gates_for(verdict):
    return ({"verdict": verdict, "contradictions": [], "unsupported_specific_claims": [],
             "verified_claims_summary": [], "sources": [], "notes": "test"},
            "FACT_CHECK_COMPLETED", [], "fake-model", "fake-response-id", None, [])


class FactCheckerPolicyTests(unittest.TestCase):
    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er010_factcheck_policy_test_")
        self.addCleanup(shutil.rmtree, self.out_dir, ignore_errors=True)

    def _run_with_verdict(self, verdict, deviation_mock=None):
        writer_mock = mock.Mock(return_value=_fake_writer_result(ARTICLE_SIMPLE))
        deviation_mock = deviation_mock or mock.Mock(return_value=_compliant_deviation_result())
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen, "run_point_overlap_qa_and_regenerate", side_effect=_fake_point_overlap_no_flag), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates",
                                return_value=_fake_fact_checker_gates_for(verdict)), \
             mock.patch.object(gen.vfl01, "run_deviation_check", deviation_mock):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="tip screens", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=False)
        return result, deviation_mock

    def test_review_required_is_non_blocking_and_continues_to_ledger_check(self):
        result, deviation_mock = self._run_with_verdict("REVIEW_REQUIRED")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["fact_verdict"], "REVIEW_REQUIRED")
        deviation_mock.assert_called_once()

    def test_pass_is_non_blocking_as_before(self):
        result, deviation_mock = self._run_with_verdict("PASS")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["fact_verdict"], "PASS")
        deviation_mock.assert_called_once()

    def test_fail_is_blocking_and_skips_ledger_check(self):
        deviation_mock = mock.Mock(return_value=_compliant_deviation_result())
        result, deviation_mock = self._run_with_verdict("FAIL", deviation_mock=deviation_mock)
        self.assertEqual(result["status"], "NG_REVIEW_REQUIRED")
        self.assertEqual(result["fact_verdict"], "FAIL")
        deviation_mock.assert_not_called()

    def test_fail_result_preserves_article_text_and_fact_check_result(self):
        result, _ = self._run_with_verdict("FAIL")
        self.assertIsNotNone(result["article_text"])
        self.assertEqual(result["fact_check_result"]["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
