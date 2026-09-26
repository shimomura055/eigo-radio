# ============================================================
# er021_en_asr_semantic_equivalence_trial_01_test_01.py
# EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01: unittest(API課金なし、Trial module
# 単体のオフライン検証)。
# ============================================================
from __future__ import annotations

import importlib.util
import unittest

import er021_en_asr_semantic_equivalence_trial_01 as sem
import er006_preprod_hardening_01_validation as val


class Tier1NumericEquivalenceTest(unittest.TestCase):
    def assertNumericMatch(self, canonical, asr):
        r = sem.classify_semantic_equivalence(canonical, asr)
        self.assertEqual(r["classification"], "NUMERIC_EQUIVALENCE_MATCH", r)
        self.assertTrue(r["should_pass"], r)
        self.assertEqual(r["sub_reason"], "numeric_only")

    def assertNotRescued(self, canonical, asr, **kwargs):
        r = sem.classify_semantic_equivalence(canonical, asr, **kwargs)
        self.assertFalse(r["should_pass"], r)
        self.assertNotEqual(r["classification"], "NUMERIC_EQUIVALENCE_MATCH")
        self.assertNotEqual(r["classification"], "SECONDARY_ASR_CORROBORATED_MATCH")

    def test_decimal_scale_currency_percent(self):
        self.assertNumericMatch(
            "The price rose to two point three million dollars, a fifteen percent increase from last year.",
            "The price rose to $2.3 million, a 15% increase from last year.")

    def test_billion_scale(self):
        self.assertNumericMatch("The company is now worth one point two billion dollars.",
                                 "The company is now worth $1.2 billion.")

    def test_year_pair_1999(self):
        self.assertNumericMatch("The policy was introduced in 1999.",
                                 "The policy was introduced in nineteen ninety-nine.")

    def test_year_pair_2026(self):
        self.assertNumericMatch("The forecast covers the period through 2026.",
                                 "The forecast covers the period through twenty twenty-six.")

    def test_year_thousand_and(self):
        self.assertNumericMatch("The building opened in 2006.",
                                 "The building opened in two thousand and six.")

    def test_time_pm(self):
        self.assertNumericMatch("The meeting starts at 3:30 pm.", "The meeting starts at three thirty pm.")

    def test_time_am_oh(self):
        self.assertNumericMatch("The train departs at 6:05 am.", "The train departs at six oh five am.")

    def test_fraction_half(self):
        self.assertNumericMatch("About one half of the group agreed.", "About 1/2 of the group agreed.")

    def test_fraction_two_thirds(self):
        self.assertNumericMatch("Two thirds of the students passed.", "2/3 of the students passed.")

    def test_roman_numeral_ww2(self):
        self.assertNumericMatch("The article discusses World War II history.",
                                 "The article discusses World War 2 history.")

    def test_roman_numeral_excludes_bare_I(self):
        # 安全策: 代名詞"I"と衝突するため、単独の"I"はローマ数字1として
        # 認識しない(閉じた集合はII〜Xに限定)。
        r = sem.classify_semantic_equivalence("I went to the store.", "I went to the store.")
        # 完全一致なのでこれ自体はEXACT_MATCH(baseline)になるはずで、
        # Tier1が変な値パースを行っていないことだけを確認する。
        self.assertNotEqual(r["classification"], "NUMERIC_EQUIVALENCE_MATCH")

    def test_no_dot_number(self):
        self.assertNumericMatch("Model No. 5 was recalled.", "Model number 5 was recalled.")

    def test_ampersand_and(self):
        self.assertNumericMatch("The report covers Q3 & Q4 results.", "The report covers Q3 and Q4 results.")

    def test_minus_dash(self):
        self.assertNumericMatch("The temperature dropped to minus five degrees.",
                                 "The temperature dropped to -5 degrees.")

    def test_comma_grouped_large_number(self):
        self.assertNumericMatch("The population is 2,300,000 people.",
                                 "The population is two million three hundred thousand people.")

    # ---- NEGATIVE(false accept 0が必須) ----
    def test_negative_million_value_differs(self):
        self.assertNotRescued("The price rose to $2.3 million.", "The price rose to $2.5 million.")

    def test_negative_fifteen_vs_fifty(self):
        self.assertNotRescued("There were fifteen participants.", "There were fifty participants.")

    def test_negative_percent_vs_percentage_points(self):
        self.assertNotRescued("Inflation rose by five percent.", "Inflation rose by five percentage points.")

    def test_negative_currency_presence(self):
        self.assertNotRescued("The device costs $100.", "The device costs 100.")

    def test_negative_million_vs_billion(self):
        self.assertNotRescued("The company is worth two point three million dollars.",
                               "The company is worth $2.3 billion.")

    def test_negative_minus_vs_plus(self):
        self.assertNotRescued("The adjustment was minus five points.", "The adjustment was plus five points.")

    def test_negative_about_20_vs_20(self):
        self.assertNotRescued("About 20 people attended.", "20 people attended.")

    def test_negative_currency_type_mismatch(self):
        self.assertNotRescued("The fee is fifty dollars.", "The fee is £50.")

    def test_negative_time_meridiem_mismatch(self):
        self.assertNotRescued("The meeting starts at 3:30 pm.", "The meeting starts at 3:30 am.")

    def test_negative_digit_by_digit_id_not_combined(self):
        self.assertNotRescued("The code is one two three.", "The code is 123.")

    def test_negative_seven_digit_id_spelled_not_combined(self):
        self.assertNotRescued("The reference number is 1234567.",
                               "The reference number is one two three four five six seven.")

    def test_negative_exponent_not_silently_dropped(self):
        # 既存fixtureで実測発見した回帰(上付き指数がtokenizerで消失し、
        # "10¹⁶"と"10"が誤って数値等価になっていた不具合の固定化)。
        self.assertNotRescued("roughly 10¹⁶ combinations", "roughly 10 combinations")


class Tier3CorroborationTest(unittest.TestCase):
    def test_plural_only_rescued_with_corroboration(self):
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        r = sem.classify_semantic_equivalence(canonical, asr, secondary_text=canonical)
        self.assertEqual(r["classification"], "SECONDARY_ASR_CORROBORATED_MATCH")
        self.assertTrue(r["should_pass"])
        self.assertEqual(r["sub_reason"], "plural_only")
        self.assertIn("secondary", r["corroborated_by"])

    def test_plural_only_not_rescued_without_corroboration(self):
        canonical = "The team is down one point."
        asr = "The team is down one points."
        r = sem.classify_semantic_equivalence(canonical, asr)
        self.assertFalse(r["should_pass"])
        self.assertEqual(r["sub_reason"], "plural_only")
        self.assertEqual(r["corroborated_by"], [])

    def test_entity_only_rescued_with_corroboration(self):
        canonical = "Ottoni and colleagues found similar results."
        asr = "Otani and colleagues found similar results."
        r = sem.classify_semantic_equivalence(canonical, asr, secondary_text=canonical)
        self.assertEqual(r["classification"], "SECONDARY_ASR_CORROBORATED_MATCH")
        self.assertTrue(r["should_pass"])
        self.assertEqual(r["sub_reason"], "entity_only")

    def test_entity_only_not_rescued_when_corroboration_contradicts(self):
        canonical = "Ottoni and colleagues found similar results."
        asr = "Otani and colleagues found similar results."
        r = sem.classify_semantic_equivalence(canonical, asr, secondary_text=asr)
        self.assertFalse(r["should_pass"])
        self.assertEqual(r["corroborated_by"], [])

    def test_homophone_only_is_not_in_tier3_rescue_scope(self):
        canonical = "Please wait for the results."
        asr = "Please weight for the results."
        r = sem.classify_semantic_equivalence(canonical, asr, secondary_text=canonical)
        self.assertFalse(r["should_pass"])
        self.assertNotEqual(r["classification"], "SECONDARY_ASR_CORROBORATED_MATCH")


class SubReasonObservabilityTest(unittest.TestCase):
    def test_protected_number(self):
        r = sem.classify_semantic_equivalence("The population is 2 million.", "The population is 3 million.")
        self.assertEqual(r["sub_reason"], "protected_number")
        self.assertIsNotNone(r["observability_record"])

    def test_protected_negation(self):
        r = sem.classify_semantic_equivalence("The vaccine is effective.", "The vaccine is not effective.")
        self.assertEqual(r["sub_reason"], "protected_negation")

    def test_content_word(self):
        r = sem.classify_semantic_equivalence("The team increased the budget.", "The team decreased the budget.")
        self.assertEqual(r["sub_reason"], "content_word")

    def test_none_when_already_passing(self):
        r = sem.classify_semantic_equivalence("Hello there.", "Hello there.")
        self.assertEqual(r["sub_reason"], "none")
        self.assertIsNone(r["observability_record"])


class Tier2OutOfScopeTest(unittest.TestCase):
    def test_wanna_not_rescued(self):
        r = sem.classify_semantic_equivalence("Do you want to join us?", "Do you wanna join us?")
        self.assertFalse(r["should_pass"])

    def test_dunno_not_rescued(self):
        r = sem.classify_semantic_equivalence("I don't know the answer.", "I dunno the answer.")
        self.assertFalse(r["should_pass"])


class ExistingFixtureRegressionTest(unittest.TestCase):
    """OPEN-123の既存Regression fixture(POSITIVE 29+AMBIGUOUS 2+NEGATIVE 28)
    に対して、本Trial moduleがfalse acceptを増やさないこと・POSITIVE fixture
    の受入条件(should_pass=Trueまたはshould_retry=False)を壊さないことを
    確認する(Production module自体は無変更)。"""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "_er006_fixtures_for_er021", "er006_preprod_hardening_01_validation_test.py")
        cls.fixmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.fixmod)

    def test_positive_fixtures_no_regression(self):
        for fx in self.fixmod.POSITIVE_FIXTURES:
            r = sem.classify_semantic_equivalence(fx["canonical"], fx["asr"])
            ok = r["should_pass"] or not r["should_retry"]
            self.assertTrue(ok, f"regression: {fx['name']} -> {r['classification']}")

    def test_negative_fixtures_no_false_accept(self):
        for fx in self.fixmod.NEGATIVE_FIXTURES:
            r = sem.classify_semantic_equivalence(fx["canonical"], fx["asr"])
            self.assertFalse(r["should_pass"], f"false accept: {fx['name']} -> {r['classification']}")


if __name__ == "__main__":
    unittest.main()
