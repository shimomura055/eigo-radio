"""OPEN-482 第2層 (FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_04): 最終ゲートvalue_guardの時刻atom不整合の是正test。
原稿側『10 thirty』(TTS入力の数字化後: 2数値atom)と、ASR側『10:30』(1つのtime atom)は同一値として扱う。値が違えば従来どおり非EQUAL。"""
import unittest

import er078_asr_value_guard_01 as vg

OK_KINDS = (vg.EQUAL, vg.NO_VALUES, vg.AMBIGUOUS)


def _kind(src, hyp):
    return vg.value_guard(src, hyp, "en").kind


class ClockAtomTest(unittest.TestCase):
    def test_observed_c8_case_equal(self):
        self.assertEqual(_kind("At 10 thirty, a tall man in a long overcoat", "At 10:30, a tall man in a long overcoat"), vg.EQUAL)

    def test_positive_pairs(self):
        for s, h in [("At 10 thirty", "At 10:30"), ("At 10:30", "At 10 thirty"), ("At 2 thirty", "At 2:30"),
                     ("At 1 thirty", "At 1:30"), ("At 7 fifteen sharp", "At 7:15 sharp")]:
            self.assertEqual(_kind(s, h), vg.EQUAL, (s, h))

    def test_synthetic_negatives_stay_non_equal(self):
        for s, h in [("At 10 thirty", "At 10:13"), ("At 10 thirty", "At 10:15"), ("At 10 thirty", "At 10:03"),
                     ("At 10 thirty", "At 11:30"), ("At 10 thirty", "At 10"), ("At 10 thirty", "At 40"),
                     ("At 10 thirty", "At 30"), ("At 10 thirty", "At 10:30 pm"), ("At 10 thirty pm", "At 10:30 am"),
                     ("At 2 thirty", "At 2:03"), ("At 2 thirty", "At 2:13"), ("At 2 thirty", "At 32"),
                     ("At 7 fifteen", "At 7:50"), ("At 12 thirty", "At 12:03"), ("At 1:30", "At 13:00"),
                     ("At 25 thirty", "At 25:30"), ("At 10 apples and 30 pears", "At 10:30"),
                     ("At 10 percent 30", "At 10:30"), ("At $10 30", "At 10:30"), ("At 10 sixty", "At 10:60"),
                     ("At 3 forty", "At 3:04"), ("At 9 ten", "At 9:01")]:
            self.assertNotIn(_kind(s, h), OK_KINDS, (s, h))

    def test_existing_behaviour_unchanged(self):
        self.assertEqual(_kind("There are 10 people", "There are 10 people"), vg.EQUAL)
        self.assertEqual(_kind("There are 10 people", "There are 30 people"), vg.DIFF)


if __name__ == "__main__":
    unittest.main()
