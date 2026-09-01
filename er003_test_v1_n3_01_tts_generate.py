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
import er006_preprod_hardening_01_validation as en_validator


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


class HyphenCompoundNumberWordsRegressionTests(unittest.TestCase):
    """ER-010-NO9-TTS-NUMBER-WORDS-BUGFIX-AND-AUDIO-RETRY-16: tts_safe_number_words_en()が
    `\\b`をハイフンでも単語境界とみなすため、"Forty-four"のようなハイフン複合数(20〜99台)の
    後半だけを独立数字語として誤変換し"Forty-4"のように壊していたbugへの回帰テスト。
    修正はハイフン複合数を個別にhardcodeせず、直前がハイフンの場合はマッチさせない
    汎用ルール(negative lookbehind)によるため、任意の複合数で成立することを確認する。"""

    def test_compound_numbers_survive_unchanged(self):
        compounds = [
            "twenty-one", "twenty-eight", "thirty-six", "forty-four",
            "fifty-nine", "sixty-six", "seventy-eight", "eighty-three", "ninety-nine",
        ]
        for word in compounds:
            with self.subTest(word=word):
                self.assertEqual(tts.tts_safe_number_words_en(word), word)

    def test_compound_numbers_with_percent_survive_unchanged(self):
        cases = [
            "Forty-four percent", "forty-four percent", "forty-four%",
            "Seventy-eight percent", "Thirty-six percent",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(tts.tts_safe_number_words_en(text), text)

    def test_plain_percent_forms_unaffected(self):
        # 複合数以外の数字表記(既にdigit)はそもそも対象外で変化しない
        for text in ["44 percent", "44%"]:
            with self.subTest(text=text):
                self.assertEqual(tts.tts_safe_number_words_en(text), text)

    def test_no9_point_two_sentence_fixtures_not_corrupted(self):
        # No.9 A2/B1 point_twoで実際に破損が発生していた文脈の再現
        sentences = [
            "Forty-four percent of respondents agreed with the statement.",
            "The share climbed to seventy-eight percent among younger workers.",
            "Only thirty-six percent said they felt confident about the plan.",
        ]
        for sentence in sentences:
            with self.subTest(sentence=sentence):
                result = tts.tts_safe_number_words_en(sentence)
                self.assertNotIn("forty-4", result.lower())
                self.assertNotIn("seventy-8", result.lower())
                self.assertNotIn("thirty-6", result.lower())
                self.assertEqual(result, sentence)

    def test_standalone_number_words_still_convert(self):
        # 既存の正しい単独数字変換(two〜twelve)は維持されている
        cases = {
            "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
            "seven": "7", "eight": "8", "nine": "9", "ten": "10",
            "eleven": "11", "twelve": "12",
        }
        for word, digit in cases.items():
            with self.subTest(word=word):
                self.assertEqual(tts.tts_safe_number_words_en(word), digit)

    def test_standalone_number_word_in_sentence_still_converts(self):
        text = "Two closer relationships were measured over time."
        self.assertEqual(
            tts.tts_safe_number_words_en(text),
            "2 closer relationships were measured over time.")

    def test_ordinals_decimals_currency_punctuation_unaffected(self):
        # 数字語変換の対象外である既存表記(序数・小数・通貨・句読点)への非回帰確認
        cases = [
            "The event happened on April twenty-eighth.",
            "The rate was 3.5 percent last year.",
            "The cost was $12.50 per item.",
            "\"Is this correct?\" she asked.",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(tts.tts_safe_number_words_en(text), text)


class ProductionValidatorIntegrationAfterHyphenFixTests(unittest.TestCase):
    """修正後のtts_safe_news_en()出力を、実Production ASR Validator
    (classify_asr_match)に通し、ASR側が数字表記で書き起こした場合に
    正しくMATCH側へ分類されることを確認する(No.9 A2/B1 point_two実例)。"""

    def test_forty_four_percent_matches_asr_digit_form(self):
        canonical = tts.tts_safe_news_en("Forty-four percent of respondents agreed.")
        asr_text = "44% of respondents agreed."
        result = en_validator.classify_asr_match(canonical, asr_text)
        self.assertIn(
            result.classification,
            ("EXACT_MATCH", "NORMALIZED_MATCH", "HIGH_SIMILARITY_SAFE"))

    def test_seventy_eight_percent_matches_asr_spoken_form(self):
        canonical = tts.tts_safe_news_en("The share climbed to seventy-eight percent.")
        asr_text = "The share climbed to 78 percent."
        result = en_validator.classify_asr_match(canonical, asr_text)
        self.assertIn(
            result.classification,
            ("EXACT_MATCH", "NORMALIZED_MATCH", "HIGH_SIMILARITY_SAFE"))

    def test_thirty_six_percent_matches_asr_digit_form(self):
        canonical = tts.tts_safe_news_en("Only thirty-six percent said they felt confident.")
        asr_text = "Only 36% said they felt confident."
        result = en_validator.classify_asr_match(canonical, asr_text)
        self.assertIn(
            result.classification,
            ("EXACT_MATCH", "NORMALIZED_MATCH", "HIGH_SIMILARITY_SAFE"))


if __name__ == "__main__":
    unittest.main()
