# -*- coding: utf-8 -*-
"""er053_dangling_reference_check_01 のtest(¥0)。実行: .venv/Scripts/python.exe -m pytest er053_dangling_reference_check_01_test_01.py -q"""
from __future__ import annotations

import os
import tempfile
import unittest

import er053_dangling_reference_check_01 as dg

NEW_C1_MODULES = ["er053_risk_flagger_production_01.py", "er053_review_queue_01.py", "er053_b3_annotation_contract_01.py",
                  "er053_en_sentence_splitter_01.py", "er053_family_x_factlock_ja_writer_01.py"]


class DanglingTests(unittest.TestCase):
    def test_count_in_text(self):
        t = "OPEN243_M1 and must_fix; MAJOR MAJOR; deviation check; local rewrite; JAFactCheckStopError"
        c = dg.count_in_text(t)
        self.assertEqual(c["OPEN243_M1"], 1)
        self.assertEqual(c["MAJOR"], 2)
        self.assertEqual(c["must_fix"], 1)
        self.assertEqual(c["Deviation Check (ci)"], 1)
        self.assertEqual(c["Local Rewrite (ci)"], 1)
        self.assertEqual(c["JAFactCheckStopError"], 1)

    def test_scan_deterministic_and_scope_complete(self):
        a, b = dg.scan(), dg.scan()
        self.assertEqual(a, b)
        self.assertFalse(any("_missing" in v for v in a["per_file"].values()))
        self.assertEqual(len(a["scope_files"]), 9)

    def test_new_c1_modules_have_zero_dangling_references(self):
        r = dg.scan()
        for f in NEW_C1_MODULES:
            self.assertEqual(r["per_file"][f], {}, f)

    def test_missing_file_reported(self):
        r = dg.scan(root=tempfile.mkdtemp(), files=["nope.py"])
        self.assertTrue(r["per_file"]["nope.py"]["_missing"])


if __name__ == "__main__":
    unittest.main()
