# -*- coding: utf-8 -*-
"""FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_02: er053 derive_ranks の never-core kind(year/ordinal/name_embedded) role是正の回帰test。
結合概念(例: 同一Fact内の'2026年'と'2026年9月3日')がcoreでも、年/序数/名前埋込表記itemはperipheralになり、
produce_annotated_b3 の内部検査 c_core_peripheral が通る(API 0)。入力=ig_nobel_2026/run_nws_02のLedgerとB3 brief(委任_01でcommit済み)。"""
import os
import shutil
import tempfile
import unittest

import er053_b3_deterministic_producer_01 as prod

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "er019_output", "ig_nobel_2026", "run_nws_02")
NEVER_CORE = ("year", "ordinal", "name_embedded")


@unittest.skipUnless(os.path.isfile(os.path.join(SRC, "storyline_b3", "selected_brief.md")), "ig_nobel_2026 fixture missing")
class NeverCoreRoleTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "research_ledger"))
        os.makedirs(os.path.join(self.d, "storyline_b3"))
        shutil.copy(os.path.join(SRC, "research_ledger", "verified_fact_ledger.txt"), os.path.join(self.d, "research_ledger"))
        for f in ("selected_brief.md", "fact_selection_evidence.json"):
            shutil.copy(os.path.join(SRC, "storyline_b3", f), os.path.join(self.d, "storyline_b3"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_year_item_joined_with_core_date_is_peripheral_and_producer_passes(self):
        res = prod.produce_annotated_b3(self.d)          # 修正前は AnnotationProducerError(core '2026年' has never-core kind year)
        self.assertEqual(res["manifest"]["internal_checks"]["c_core_peripheral"]["status"], "PASS")

    def test_derive_ranks_never_core_kinds_are_peripheral(self):
        import json
        ledger = open(os.path.join(self.d, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
        ev = json.load(open(os.path.join(self.d, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
        der = prod.derive_ranks(ledger, ev["selected_fact_ids"], ev["selected_storyline"], with_story=True)
        bad = [it for it in der["items"] if it["role"] == "core" and it["kind"] in NEVER_CORE]
        self.assertEqual(bad, [])
        self.assertTrue(any(it["kind"] == "date_time" and it["role"] == "core" for it in der["items"]))     # 日付概念のcore自体は維持
        self.assertTrue(any(it["kind"] == "year" and it["role"] == "peripheral" for it in der["items"]))


if __name__ == "__main__":
    unittest.main()
