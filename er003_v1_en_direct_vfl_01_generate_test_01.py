# ============================================================
# er003_v1_en_direct_vfl_01_generate_test_01.py
# NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01
# ============================================================
# run_deviation_check()の後方互換オプション引数拡張
# (prior_issues/include_related_fact_id/source_article_text)の単体テスト。
# 実API呼び出しは行わない(mock client使用)。既存呼び出し(引数省略)の
# prompt文言・schema・戻り値キー集合が一切変わらないことを最優先で確認する。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_v1_en_direct_vfl_01_generate_test_01 -v
# ============================================================
from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

import er003_v1_en_direct_vfl_01_generate as vfl01


def _fake_response(output_dict: dict, model: str = "gpt-5.6-luna", response_id: str = "resp_1"):
    return SimpleNamespace(
        output_text=json.dumps(output_dict),
        model=model,
        id=response_id,
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=50,
            input_tokens_details=SimpleNamespace(cached_tokens=10),
            output_tokens_details=SimpleNamespace(reasoning_tokens=5),
        ),
    )


class _FakeResponses:
    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._outputs.pop(0)


class _FakeClient:
    def __init__(self, outputs):
        self.responses = _FakeResponses(outputs)


NO_DEVIATION = {"deviations": []}


def _major_deviation(**overrides) -> dict:
    base = {
        "claim_in_article": "c", "issue": "i", "severity": "MAJOR",
        "changed_fact": True, "changed_scope": False, "changed_causality": False,
        "changed_certainty": False, "changed_number": False, "changed_actor": False,
        "changed_negation": False, "changed_comparison": False, "changed_time": False,
        "unsupported_new_claim": False, "explanation": "e",
    }
    base.update(overrides)
    return base


class RunDeviationCheckBackwardCompatTests(unittest.TestCase):
    def test_default_call_schema_and_prompt_unchanged(self):
        client = _FakeClient([_fake_response(NO_DEVIATION)])
        result = vfl01.run_deviation_check(client, "LEDGER TEXT", "ARTICLE TEXT")
        sent = client.responses.calls[0]
        self.assertEqual(sent["text"]["format"]["name"], vfl01.DEVIATION_JSON_SCHEMA["name"])
        self.assertNotIn("関連Fact ID", sent["input"][1]["content"])
        self.assertNotIn("逸脱の発生源", sent["input"][1]["content"])
        self.assertNotIn("前回指摘の解消確認", sent["input"][1]["content"])
        self.assertEqual(result["parsed"]["overall_status"], "LEDGER_COMPLIANT")
        self.assertNotIn("prior_issues_resolved", result["parsed"])
        self.assertNotIn("all_prior_issues_resolved", result["parsed"])
        self.assertIn("usage", result)
        self.assertIn("elapsed_seconds", result)

    def test_hook_aware_default_schema_unchanged(self):
        client = _FakeClient([_fake_response(NO_DEVIATION)])
        vfl01.run_deviation_check(client, "LEDGER", "ARTICLE", hook_aware=True)
        sent = client.responses.calls[0]
        self.assertEqual(sent["text"]["format"]["name"], vfl01.HOOK_AWARE_DEVIATION_JSON_SCHEMA["name"])


class IncludeRelatedFactIdTests(unittest.TestCase):
    def test_adds_prompt_instruction_and_schema_field(self):
        output = {"deviations": [_major_deviation(related_fact_id="F1")]}
        client = _FakeClient([_fake_response(output)])
        result = vfl01.run_deviation_check(client, "LEDGER", "ARTICLE", include_related_fact_id=True)
        sent = client.responses.calls[0]
        self.assertIn("関連Fact ID", sent["input"][1]["content"])
        schema_props = sent["text"]["format"]["schema"]["properties"]["deviations"]["items"]["properties"]
        self.assertIn("related_fact_id", schema_props)
        self.assertEqual(result["parsed"]["deviations"][0]["related_fact_id"], "F1")


class SourceArticleOriginTests(unittest.TestCase):
    def test_adds_origin_instruction_and_field(self):
        output = {"deviations": [_major_deviation(origin="ja_source")]}
        client = _FakeClient([_fake_response(output)])
        result = vfl01.run_deviation_check(client, "LEDGER", "ARTICLE",
                                            source_article_text="JA ORIGINAL TEXT")
        sent = client.responses.calls[0]
        self.assertIn("逸脱の発生源", sent["input"][1]["content"])
        self.assertIn("JA ORIGINAL TEXT", sent["input"][1]["content"])
        self.assertEqual(result["parsed"]["deviations"][0]["origin"], "ja_source")


class PriorIssuesTests(unittest.TestCase):
    def _make_prior(self):
        return [{"fact_id": "F1", "claim_in_article": "c1", "issue": "i1", "explanation": "e1"}]

    def test_all_resolved_true(self):
        output = {"deviations": [],
                  "prior_issues_resolved": [{"index": 0, "resolved": True, "explanation": "fixed"}]}
        client = _FakeClient([_fake_response(output)])
        result = vfl01.run_deviation_check(client, "LEDGER", "ARTICLE", prior_issues=self._make_prior())
        sent = client.responses.calls[0]
        self.assertIn("前回指摘の解消確認", sent["input"][1]["content"])
        self.assertTrue(result["parsed"]["all_prior_issues_resolved"])

    def test_partial_unresolved_false(self):
        output = {"deviations": [],
                  "prior_issues_resolved": [{"index": 0, "resolved": False, "explanation": "still there"}]}
        client = _FakeClient([_fake_response(output)])
        result = vfl01.run_deviation_check(client, "LEDGER", "ARTICLE", prior_issues=self._make_prior())
        self.assertFalse(result["parsed"]["all_prior_issues_resolved"])

    def test_missing_entries_treated_as_unresolved(self):
        output = {"deviations": [], "prior_issues_resolved": []}
        client = _FakeClient([_fake_response(output)])
        result = vfl01.run_deviation_check(client, "LEDGER", "ARTICLE", prior_issues=self._make_prior())
        self.assertFalse(result["parsed"]["all_prior_issues_resolved"])


class HookAwareWithExtensionsTests(unittest.TestCase):
    def test_hook_aware_plus_related_fact_id_schema_has_both_fields(self):
        client = _FakeClient([_fake_response(NO_DEVIATION)])
        vfl01.run_deviation_check(client, "LEDGER", "ARTICLE", hook_aware=True, include_related_fact_id=True)
        sent = client.responses.calls[0]
        props = sent["text"]["format"]["schema"]["properties"]["deviations"]["items"]["properties"]
        self.assertIn("treated_as_hook", props)
        self.assertIn("related_fact_id", props)


class DeviationAuditRecordTests(unittest.TestCase):
    def test_record_contains_expected_keys(self):
        check_result = {
            "prompt": "P", "raw_text": "R", "parsed": {"overall_status": "LEDGER_COMPLIANT"},
            "response_id": "resp_1", "model": "gpt-5.6-luna", "usage": {"input_tokens": 1},
            "elapsed_seconds": 0.5, "hook_aware": False,
        }
        record = vfl01.deviation_audit_record(check_result)
        for key in ("prompt", "raw_text", "parsed", "response_id", "model", "usage",
                    "elapsed_seconds", "hook_aware"):
            self.assertIn(key, record)


if __name__ == "__main__":
    unittest.main()
