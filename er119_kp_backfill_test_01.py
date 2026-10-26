# -*- coding: utf-8 -*-
"""KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02: Gate除外候補補完のtest(API 0、全LLM mock。TBFxx = TEST_PLAN_01の番号)。
実行: .venv\Scripts\python.exe -m unittest er119_kp_backfill_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import unittest

import er119_kp_backfill_golden_01 as g


class TestGoldenPureRefactorTBF24(unittest.TestCase):
    """R-6: _gate_chain抽出前(HEAD)に固定したgoldenと、抽出後の候補doc(Gate連鎖の全出力)が完全一致する。"""

    def test_candidate_docs_equal_pre_extraction_golden(self):
        for name in g.SCENARIOS:
            with self.subTest(name):
                with open(g.golden_path(name), encoding="utf-8") as f:
                    expected = json.load(f)
                self.assertEqual(g.strip_additive(g.run_scenario(name)), expected)


if __name__ == "__main__":
    unittest.main()
