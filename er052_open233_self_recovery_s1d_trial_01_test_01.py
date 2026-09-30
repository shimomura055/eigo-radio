# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_s1d_trial_01_test_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Phase 1 ③、委任_07)
# ============================================================
# ネットワーク呼び出しなし(¥0)。S1-D Prompt/schema構築ロジックの
# read-only regression testのみ。
from __future__ import annotations

import unittest

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_s1d_trial_01 as s1d


class TestS1DFlagParity(unittest.TestCase):
    def test_flag_keys_match_production(self):
        self.assertEqual(sorted(s1d.S1D_FLAG_KEYS), sorted(vfl01.DEVIATION_FLAG_KEYS))

    def test_schema_item_required_includes_all_flags(self):
        item_schema = s1d.S1D_JSON_SCHEMA["schema"]["properties"]["deviations"]["items"]
        required = set(item_schema["required"])
        for flag in vfl01.DEVIATION_FLAG_KEYS:
            self.assertIn(flag, required)
        self.assertIn("materiality", required)
        self.assertIn("basis", required)
        self.assertIn("rewrite_kind", required)
        self.assertNotIn("explanation", item_schema["properties"])
        self.assertNotIn("reasoning_summary", item_schema["properties"])

    def test_schema_strict_no_additional_properties(self):
        item_schema = s1d.S1D_JSON_SCHEMA["schema"]["properties"]["deviations"]["items"]
        self.assertFalse(item_schema["additionalProperties"])
        self.assertTrue(s1d.S1D_JSON_SCHEMA["strict"])


class TestBuildPrompt(unittest.TestCase):
    def test_build_prompt_contains_all_sections(self):
        prompt = s1d.build_s1d_prompt("LEDGER_TEXT_X", "ARTICLE_TEXT_Y", "SOURCE_JA_Z")
        self.assertIn("LEDGER_TEXT_X", prompt)
        self.assertIn("ARTICLE_TEXT_Y", prompt)
        self.assertIn("SOURCE_JA_Z", prompt)
        self.assertIn("changed_actor", prompt)
        self.assertIn("materiality", prompt.lower() if False else prompt)  # noqa: keep literal check below
        self.assertIn("BLOCKING", prompt)
        self.assertIn("rewrite_kind", prompt)

    def test_build_prompt_none_source(self):
        prompt = s1d.build_s1d_prompt("L", "A", None)
        self.assertIn("(なし)", prompt)

    def test_prompt_no_explanation_instruction_removed_field(self):
        prompt = s1d.build_s1d_prompt("L", "A", None)
        self.assertIn("explanationのような", prompt)


class TestOverallStatus(unittest.TestCase):
    def test_no_deviations_is_compliant(self):
        self.assertEqual(s1d.overall_status_from_deviations([]), "LEDGER_COMPLIANT")

    def test_all_acceptable_is_compliant(self):
        devs = [{"materiality": "ACCEPTABLE"}, {"materiality": "QUALITY"}]
        self.assertEqual(s1d.overall_status_from_deviations(devs), "LEDGER_COMPLIANT")

    def test_any_blocking_is_deviation(self):
        devs = [{"materiality": "ACCEPTABLE"}, {"materiality": "BLOCKING"}]
        self.assertEqual(s1d.overall_status_from_deviations(devs), "LEDGER_DEVIATION")


class TestCostFunction(unittest.TestCase):
    def test_official_cost_jpy_zero_usage(self):
        self.assertEqual(s1d.official_cost_jpy({}), 0.0)

    def test_official_cost_jpy_basic(self):
        usage = {"input_tokens": 1_000_000, "cached_input_tokens": 0, "output_tokens": 1_000_000}
        cost = s1d.official_cost_jpy(usage)
        expected_usd = 0.10 + 0.50
        self.assertAlmostEqual(cost, expected_usd * s1d.USD_JPY, places=3)


if __name__ == "__main__":
    unittest.main()
