# -*- coding: utf-8 -*-
"""FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_02: ドット区切りバージョン表記(26.10.10以上)で
抽出器(SURF_RE)と注記器(find_all)が矛盾し ANNOTATION_PRODUCER_FAILED となる不具合の回帰test。API 0。
実行: .venv/Scripts/python.exe -m pytest er053_b3_deterministic_producer_dotted_version_test_01.py -q
"""
from __future__ import annotations

import os
import unittest

import er053_b3_deterministic_producer_01 as prod

HERE = os.path.dirname(os.path.abspath(__file__))
BYUS_RUN = os.path.join(HERE, "er019_output", "manga_ai_chat_byus", "run_byus_01")


class DottedVersionTests(unittest.TestCase):
    def test_version_with_suffix_is_single_surface(self):
        self.assertEqual(prod.extract_surfaces("アプリバージョン26.10.10以上が必要"), ["26.10.10以上"])

    def test_dotted_sequences_longest_match(self):
        self.assertEqual(prod.extract_surfaces("バージョン1.2.3が公開"), ["1.2.3"])
        self.assertEqual(prod.extract_surfaces("5.5%増"), ["5.5%"])          # 既存挙動維持(小数)
        self.assertEqual(prod.extract_surfaces("3.14ドル"), ["3.14ドル"])

    def test_find_all_same_unit_as_extractor(self):
        text = "アプリバージョン26.10.10以上が必要"
        for s in prod.extract_surfaces(text):
            self.assertTrue(prod.find_all(prod.nfkc(text), prod.nfkc(s)), s)

    def test_find_all_partial_match_still_rejected(self):   # 既存規則(5.5の中の5を除く)の維持
        self.assertEqual(prod.find_all("5.5%", "5%"), [])
        self.assertEqual(prod.find_all("26.10.10以上", "10以上"), [])
        self.assertEqual(prod.find_all("26.10.10以上", "26.10"), [])
        self.assertEqual(prod.find_all("26.10.10以上", "26.10.10以上"), [0])

    def test_value_of_dotted_does_not_crash(self):
        self.assertEqual(prod.dec("26.10.10"), "26.10.10")

    @unittest.skipUnless(os.path.isdir(BYUS_RUN), "run_byus_01 not present")
    def test_byus_run_produces_all_checks_pass(self):
        import shutil
        import tempfile
        d = tempfile.mkdtemp(prefix="dotv_")
        os.makedirs(os.path.join(d, "research_ledger")); os.makedirs(os.path.join(d, "storyline_b3"))
        shutil.copy(os.path.join(BYUS_RUN, "research_ledger", "verified_fact_ledger.txt"), os.path.join(d, "research_ledger"))
        for f in ("selected_brief.md", "fact_selection_evidence.json"):
            shutil.copy(os.path.join(BYUS_RUN, "storyline_b3", f), os.path.join(d, "storyline_b3"))
        r = prod.produce_annotated_b3(d)
        self.assertTrue(all(v == "PASS" for v in r["manifest"]["checks"].values()), r["manifest"]["checks"])


if __name__ == "__main__":
    unittest.main()
