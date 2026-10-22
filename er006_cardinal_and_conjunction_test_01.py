# -*- coding: utf-8 -*-
"""FAMILY-Z-VOICE-PRODUCTION-WIRING-01 委任_01: ASR Validatorの数値語列変換が接続詞"and"を巻き込む不具合の是正test(課金0)。
実例: 『開いた窓』Std a2 full_story_part1_c10 "Her husband and two young brothers ..." が、ASR転写=原文と完全一致なのに
canonical側(digit化後 "and 2")とASR側("and two"→"2"と変換され"and"消失)でtoken数が食い違いHuman Review Lockになった。"""
import unittest

import er006_preprod_hardening_01_validation as val

ASR = "Her husband and two young brothers went shooting three years ago today. They went outside through that very window."
CANON_DIGITS = '"Her husband and 2 young brothers went shooting 3 years ago today. They went outside through that very window."'


class CardinalAndTest(unittest.TestCase):
    def test_observed_case_passes(self):
        r = val.classify_asr_match(CANON_DIGITS, ASR, segment_id="full_story_part1_c10")
        self.assertTrue(r.should_pass, r)

    def test_and_before_number_word_is_kept(self):
        self.assertEqual(val._convert_cardinal_words("husband and two sons"), "husband and 2 sons")
        self.assertIn("and", val._convert_cardinal_words("ten and two").split())

    def test_hundred_and_compound_unchanged(self):
        self.assertEqual(val._convert_cardinal_words("one hundred and two"), "102")
        self.assertEqual(val._convert_cardinal_words("two hundred and fifty three"), "253")
        self.assertEqual(val._convert_cardinal_words("three thousand and five"), "3005")

    def test_existing_behaviour_kept(self):
        self.assertEqual(val._convert_cardinal_words("twenty one"), "21")
        self.assertEqual(val._convert_cardinal_words("the right one"), "the right one")
        self.assertEqual(val._convert_cardinal_words("and two"), "and 2")
        self.assertEqual(val._convert_cardinal_words("two and"), "2 and")

    def test_value_difference_still_detected(self):
        wrong = ASR.replace("two young", "three young")
        r = val.classify_asr_match(CANON_DIGITS, wrong, segment_id="full_story_part1_c10")
        self.assertFalse(r.should_pass)


if __name__ == "__main__":
    unittest.main()
