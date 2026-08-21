# ============================================================
# er003_test_v1_n3_01_tts_generate.py
# ER-005-AUDIO-WASTE-REDUCTION-01: first_words()のハイフン複合語対策
# ============================================================
# A2 point_oneで実際に発生した偽陰性("parent-child"がASR側では
# "parent child"と書き起こされ、substring検証が常に不一致になる)への
# 回帰テスト。

import unittest

import er003_b1_p4c_audio as p4c
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts


class FirstWordsHyphenHandlingTests(unittest.TestCase):
    def test_hyphenated_compound_becomes_space_separated(self):
        # 実例: A2 point_one_body
        text = ("A closer parent-child relationship was linked with fewer "
                "behavior problems.")
        result = tts.first_words(text)
        self.assertEqual(result, "A closer parent child")

    def test_result_matches_asr_style_transcription(self):
        text = "A closer parent-child relationship was linked with fewer behavior problems."
        sub = tts.first_words(text)
        asr_text = ("A closer parent child relationship was linked with fewer "
                     "behavior problems, but closeness did not significantly "
                     "predict later screen time.")
        self.assertIn(sub.lower(), asr_text.lower())

    def test_non_hyphenated_text_unaffected(self):
        text = "The main result was clear in its direction."
        self.assertEqual(tts.first_words(text), "The main result was")

    def test_number_word_conversion_still_applied(self):
        # 既存の数字変換(two -> 2)が、ハイフン処理の追加後も維持されている
        text = "Two closer relationships were measured over time."
        self.assertEqual(tts.first_words(text), "2 closer relationships were")


class PointNotificationSurvivesStructuredSeparationTests(unittest.TestCase):
    """ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01 section 13: Structured
    Separation導入後も、ER-003-POINT-NOTIFICATION-01(Point番号ラベルを
    TTSへ送らない)の契約が壊れていないことを確認する回帰テスト。"""

    def test_clean_heading_output_still_passes_label_check_before_wrapping(self):
        raw_heading = 'Point Two: A pattern, not a final cause'
        cleaned = sc.clean_heading(raw_heading)
        self.assertEqual(cleaned, "A pattern, not a final cause")
        # ラベル検証は、Structured Separationで包む前のtextに対して行う
        sc.assert_no_point_number_label(cleaned, "point_two_heading")  # raises if it fails

    def test_final_tts_prompt_for_point_heading_contains_no_label_and_is_structured(self):
        raw_heading = 'Point One: "Behavior problems" is not one single picture'
        cleaned = sc.clean_heading(raw_heading)
        sc.assert_no_point_number_label(cleaned, "point_one_heading")
        prompt = p4c.build_tts_prompt(cleaned, "Some style instruction.\n\n")
        self.assertNotIn("Point One", prompt)
        self.assertNotIn("Point 1", prompt)
        self.assertIn("Behavior problems", prompt)
        self.assertIn("TEXT TO SPEAK", prompt)


if __name__ == "__main__":
    unittest.main()
