"""OPEN-482 (FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_03): 時刻の数詞語(ten thirty/two thirty/seven fifteen)を
合算(40/32/22)せず別token列(10 30 等)へ正規化する不具合是正のtest。数値差の検出力が弱まらないこと(合成負例)を含む。"""
import unittest

import er006_preprod_hardening_01_validation as val

CANON = "He waited. At ten thirty, a tall man in a long overcoat hurried towards Bob."


def _pass(canon, asr):
    return val.protected_check(val.tokenize(canon), val.tokenize(asr)).passed


class TimeNumeralTest(unittest.TestCase):
    def test_observed_c8_case_passes(self):
        r = val.classify_asr_match(CANON, CANON.replace("ten thirty", "10:30"), segment_id="full_story_part2_c8")
        self.assertTrue(r.should_pass, r)

    def test_time_words_split_not_summed(self):
        self.assertEqual(val._convert_cardinal_words("at ten thirty"), "at 10 30")
        self.assertEqual(val._convert_cardinal_words("at two thirty"), "at 2 30")
        self.assertEqual(val._convert_cardinal_words("at one thirty"), "at 1 30")
        self.assertEqual(val._convert_cardinal_words("at seven fifteen"), "at 7 15")
        self.assertEqual(val._convert_cardinal_words("at ten forty five"), "at 10 45")

    def test_positive_pairs(self):
        for c, a in [("at ten thirty", "at 10:30"), ("at ten thirty", "at ten-thirty"),
                     ("at two thirty", "at 2:30"), ("at one thirty", "at 1:30"), ("at seven fifteen", "at 7:15")]:
            self.assertTrue(_pass(c, a), (c, a))

    def test_synthetic_negatives_stay_ng(self):
        for c, a in [("at ten thirty", "at 10:13"), ("at ten thirty", "at ten"), ("at ten thirty", "at 10:30".replace("30", "15")),
                     ("at ten thirty", "at 40"), ("at ten thirty", "at forty"), ("at ten thirty", "at 30"),
                     ("at two thirty", "at 2:03"), ("at two thirty", "at 32"), ("at ten thirty", "at 11:30"),
                     ("at seven fifteen", "at 7:50")]:
            self.assertFalse(_pass(c, a), (c, a))

    def test_valid_compound_numbers_unchanged(self):
        self.assertEqual(val._convert_cardinal_words("twenty one"), "21")
        self.assertEqual(val._convert_cardinal_words("one hundred thirty"), "130")
        self.assertEqual(val._convert_cardinal_words("two hundred and five"), "205")
        self.assertEqual(val._convert_cardinal_words("three thousand two hundred forty five"), "3245")
        self.assertEqual(val._convert_cardinal_words("twenty twenty"), "40")  # 従来挙動を変えない(tens直後のtens)
        self.assertEqual(val._convert_cardinal_words("the right one"), "the right one")


if __name__ == "__main__":
    unittest.main()
