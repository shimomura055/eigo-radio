"""ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02 H(F-1): TTS入力の数字化後の『十の位の語 + 1桁数字』(`thirty 5`)を合成数(35)として読む固定test。API 0。
対象: er006 `_convert_cardinal_words`/`normalize_numeric`(分類層)と er021 `_consume_number_word_run`(Tier1 atom化=最終ANDゲートも同じ)。"""
from __future__ import annotations

import unittest

import er006_preprod_hardening_01_validation as val
import er021_en_asr_semantic_equivalence_production_01 as t1
import er021_time_numeral_test_01 as base


def _nums(text):
    return [x["value"] for x in t1._tier1_atoms(text) if x["kind"] == "number"]


class ComposeTensDigit(unittest.TestCase):
    def test_er006_normalize(self):
        cases = {
            "thirty 5 people": "35 people", "twenty 1 days": "21 days", "forty 2 cats": "42 cats",
            "one hundred thirty 5": "135", "At 10 thirty 5": "at 10 35", "At 12 forty 5": "at 12 45",
        }
        for src, exp in cases.items():
            with self.subTest(src=src):
                self.assertEqual(val.normalize_numeric(src), exp)

    def test_er006_not_composed(self):
        # 2桁数字・0・十の位でない語・trailing and・桁区切りは合成しない(従来どおり)
        self.assertEqual(val.normalize_numeric("thirty 55 people"), "30 55 people")
        self.assertEqual(val.normalize_numeric("thirty 0 people"), "30 0 people")
        self.assertEqual(val.normalize_numeric("ten 5 people"), "10 5 people")
        self.assertEqual(val.normalize_numeric("thirty and 5 people"), "30 and 5 people")

    def test_er021_atoms(self):
        self.assertEqual(_nums("thirty 5 people"), [35])
        self.assertEqual(_nums("one hundred thirty 5"), [135])
        self.assertEqual(_nums("thirty 55 people"), [30, 55])
        self.assertEqual(_nums("ten 5 people"), [10, 5])
        self.assertEqual(_nums("thirty five people"), [35])   # 従来どおり

    def test_judge_cases(self):
        cases = [
            ("thirty 5 people", "35 people", True), ("There were thirty 5 people", "There were 35 people", True),
            ("thirty 5 people", "thirty five people", True), ("thirty 5 people", "36 people", False),
            ("thirty 5 people", "30 5 people", False),                       # PIN: 合成数として読むため30 5とは別値
            ("thirty 5 percent", "35%", True), ("one hundred thirty 5 dollars", "$135", True),
            ("At 10 thirty 5", "At 10:35", True), ("At 12 forty 5", "At 12:45", True),   # TEST_MATRIX #72/73(F-1由来の残存だったもの)
            ("At 10 thirty 5", "At 10 35", True), ("At 10 thirty 5", "At 10:30 5", False), ("At 10 thirty 5", "At 1035", False),
        ]
        for c, x, exp in cases:
            with self.subTest(canon=c, asr=x):
                self.assertEqual(base.final_pass(c, x), exp)


if __name__ == "__main__":
    unittest.main()
