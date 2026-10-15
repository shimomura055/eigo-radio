"""check_delegation_prompt_qdc_warn_test_01.py

OF-D3-02(e) (PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01, 2026-10-15):
再委任・再計画を示す性質欄にQDC記録が無い場合のWARN(PASS/FAILは不変)の unit test。
実行: python -m pytest docs/pm/tools/check_delegation_prompt_qdc_warn_test_01.py -q
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_delegation_prompt as cdp  # noqa: E402

BASE = """## 管理ID
PM-TEST-01

## 性質/到達上限Status/禁止事項
{nature}

## 事前指定Read一覧
a.md:1-10
"""


class QdcWarnTest(unittest.TestCase):
    def test_redelegation_without_qdc_record_warns(self):
        r = cdp.run_check(BASE.format(nature="再委任(委任_02)。検証のみ。"))
        self.assertTrue(any("QDC記録" in w for w in r["warnings"]))
        self.assertFalse(any("QDC記録" in x for x in r["reasons"]))

    def test_redelegation_with_qdc_record_does_not_warn(self):
        r = cdp.run_check(BASE.format(nature="再委任(委任_02)。QDC記録: 試行1回、改善見込み中。"))
        self.assertFalse(any("QDC記録" in w for w in r["warnings"]))

    def test_first_delegation_does_not_warn(self):
        r = cdp.run_check(BASE.format(nature="Trial。初回委任。"))
        self.assertFalse(any("QDC記録" in w for w in r["warnings"]))


if __name__ == "__main__":
    unittest.main()
