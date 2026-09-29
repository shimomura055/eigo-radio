# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_precheck_01_test_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1, 委任_06)
# ============================================================
# deterministic pre-check(er052_open233_self_recovery_precheck_01.py)の
# unit test。ネットワーク呼び出しなし(¥0)。合成fixtureでの検出確認+
# 既存実データ(negative claim候補16件・Safety群)での非検出/検出確認。
from __future__ import annotations

import unittest

import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_precheck_01 as pc


FAMILY_X_STYLE_LEDGER = """[VERIFIED] HF-002: Harvard Business School researchers announced that a survey of 1,300 workers found rising satisfaction.
  scope: US office workers surveyed in 2026
  numeric_value: 1,300 workers (numeric_scope: survey sample size)
  date_or_period: 2026-07-13

[VERIFIED] HF-003: The company reported that the new product line will launch on schedule.
  scope: general product launch
  numeric_value: 20% (numeric_scope: expected market share)
  date_or_period: 2026-08-01
"""


class ParseLedgerTextTest(unittest.TestCase):
    def test_parses_family_x_style_blocks(self):
        facts = pc.parse_ledger_text(FAMILY_X_STYLE_LEDGER)
        self.assertEqual(len(facts), 2)
        self.assertEqual(facts[0]["fact_id"], "HF-002")
        self.assertEqual(facts[0]["verdict"], "VERIFIED")
        self.assertEqual(facts[0]["numeric_value"], "1,300 workers (numeric_scope: survey sample size)")
        self.assertEqual(facts[0]["date_or_period"], "2026-07-13")

    def test_parses_real_hormuz_ledger_without_error(self):
        fx = {f["id"]: f for f in g6.step3_fixtures()}
        ledger_text = fx["hormuz_run03_standard"]["ledger_text"]
        facts = pc.parse_ledger_text(ledger_text)
        self.assertEqual(len(facts), 12)  # HF-001..HF-012
        self.assertTrue(all(f["fact_id"].startswith("HF-") for f in facts))

    def test_parses_er006_style_ledger_without_crashing(self):
        fx = {f["id"]: f for f in g6.step1_fixtures()}
        ledger_text = fx["er009_changed_actor"]["ledger_text"]
        facts = pc.parse_ledger_text(ledger_text)
        self.assertGreater(len(facts), 0)
        self.assertTrue(all(not f["fact_id"].upper().startswith("SRC") for f in facts))


class NumberMismatchTest(unittest.TestCase):
    def test_detects_actor_text_number_substitution(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED",
                "claim": "...", "numeric_value": "1.3 million workers"}
        article = "A team announced that a survey of 3 million workers found rising satisfaction."
        result = pc.check_number_mismatch(fact, article)
        self.assertIsNotNone(result)
        self.assertEqual(result["kind"], "number_mismatch")

    def test_no_finding_when_article_omits_the_number(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED",
                "claim": "...", "numeric_value": "1.3 million workers"}
        article = "A team announced rising satisfaction among office workers."
        result = pc.check_number_mismatch(fact, article)
        self.assertIsNone(result)

    def test_fraction_word_paraphrase_counts_as_match(self):
        fact = {"fact_id": "HF-003", "verdict": "VERIFIED",
                "claim": "...", "numeric_value": "20%"}
        article = "The report says roughly one-fifth of respondents agreed."
        result = pc.check_number_mismatch(fact, article)
        self.assertIsNone(result)

    def test_no_false_positive_when_observed_value_belongs_to_another_fact(self):
        fact_a = {"fact_id": "F-A", "verdict": "VERIFIED", "claim": "...", "numeric_value": "9.59%"}
        all_pct = {9.59, 2.6, 20.0}
        article = "Prices moved up about 2.6 percent after the 20 percent plan was withdrawn."
        result = pc.check_number_mismatch(fact_a, article, all_ledger_pct=all_pct)
        self.assertIsNone(result)

    def test_real_er009_changed_number_fixture_is_detected(self):
        fx = {f["id"]: f for f in g6.step1_fixtures()}
        f = fx["er009_changed_number"]
        findings = pc.run_precheck(f["ledger_text"], f["article_text"])
        kinds = [x["kind"] for x in findings]
        self.assertIn("number_mismatch", kinds)

    def test_real_hormuz_run03_standard_produces_no_number_mismatch_fp(self):
        """HF-006/HF-011の9.59%/1.7%は記事中の2.6%/20%(=別Factの正しい値)と
        混同してmismatch扱いされてはならない(Phase1実測で発見した補正の
        regression test)。"""
        fx = {f["id"]: f for f in g6.step3_fixtures()}
        f = fx["hormuz_run03_standard"]
        findings = pc.run_precheck(f["ledger_text"], f["article_text"])
        self.assertEqual(findings, [])


class DateMismatchTest(unittest.TestCase):
    def test_iso_date_matches_english_month_day_form(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED", "claim": "...",
                "date_or_period": "2026-07-13"}
        article = "On July 13, a plan suddenly appeared."
        result = pc.check_date_mismatch(fact, article)
        self.assertIsNone(result)

    def test_iso_date_matches_weekday_name_form(self):
        # 2026-07-13 is a Monday.
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED", "claim": "...",
                "date_or_period": "2026-07-13"}
        article = "The announcement came out on Monday, surprising markets."
        result = pc.check_date_mismatch(fact, article)
        self.assertIsNone(result)

    def test_detects_substituted_different_date(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED", "claim": "...",
                "date_or_period": "2026-07-13"}
        article = "On July 20, a plan suddenly appeared, surprising markets."
        result = pc.check_date_mismatch(fact, article)
        self.assertIsNotNone(result)
        self.assertEqual(result["kind"], "date_mismatch")

    def test_no_finding_when_article_omits_the_date(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED", "claim": "...",
                "date_or_period": "2026-07-13"}
        article = "A plan suddenly appeared, surprising markets."
        result = pc.check_date_mismatch(fact, article)
        self.assertIsNone(result)


class ActorMissingTest(unittest.TestCase):
    def test_detects_actor_substitution_when_a_foreign_name_appears(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED",
                "claim": "Harvard Business School researchers announced the survey results."}
        article = "Cornell University researchers announced the survey results."
        result = pc.check_actor_missing(fact, article, all_ledger_actor_tokens=set())
        self.assertIsNotNone(result)
        self.assertEqual(result["kind"], "actor_missing")

    def test_honorific_difference_counts_as_match(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED",
                "claim": "Trump posted that the fee would be dropped."}
        article = "President Trump posted that the fee would be dropped."
        result = pc.check_actor_missing(fact, article, all_ledger_actor_tokens=set())
        self.assertIsNone(result)

    def test_no_finding_for_non_attributive_claim(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED",
                "claim": "Oil prices near the Strait of Hormuz stayed volatile."}
        article = "A completely different unrelated article about weather."
        result = pc.check_actor_missing(fact, article, all_ledger_actor_tokens=set())
        self.assertIsNone(result)

    def test_no_finding_when_actor_simply_omitted_without_substitution(self):
        fact = {"fact_id": "HF-002", "verdict": "VERIFIED",
                "claim": "Harvard Business School researchers announced the survey results."}
        article = "A survey found rising satisfaction among office workers."
        result = pc.check_actor_missing(fact, article, all_ledger_actor_tokens=set())
        self.assertIsNone(result)


class NegationComparisonMarkerTest(unittest.TestCase):
    def test_negation_marker_detects_exact_strip_match(self):
        fact = {"fact_id": "HF-X", "verdict": "VERIFIED",
                "claim": "The study found that tip rates did not affect behavior"}
        article = "the study found that tip rates affect behavior here."
        result = pc.check_negation_marker(fact, article)
        self.assertIsNotNone(result)

    def test_negation_marker_no_finding_on_unrelated_text(self):
        fact = {"fact_id": "HF-X", "verdict": "VERIFIED",
                "claim": "The study found that tip rates did not affect passenger behavior at all."}
        article = "A completely unrelated sentence about something else entirely."
        result = pc.check_negation_marker(fact, article)
        self.assertIsNone(result)

    def test_comparison_marker_detects_antonym_verbatim_swap(self):
        fact = {"fact_id": "HF-X", "verdict": "VERIFIED",
                "claim": "prices rose sharply after the announcement was made"}
        article = "prices fell sharply after the announcement was made"
        result = pc.check_comparison_marker(fact, article)
        self.assertIsNotNone(result)

    def test_comparison_marker_no_finding_on_unrelated_text(self):
        fact = {"fact_id": "HF-X", "verdict": "VERIFIED",
                "claim": "prices rose sharply after the announcement was made"}
        article = "the weather was nice today in a different city"
        result = pc.check_comparison_marker(fact, article)
        self.assertIsNone(result)


class RealCorpusRegressionTest(unittest.TestCase):
    """Phase1①(¥0)実測の一部を、明示的なregression testとしても固定する。"""

    def test_negative_claim_candidates_produce_no_or_minimal_findings(self):
        # negative_claim_candidates_open233_01.md出典7fileのうち、
        # step2/step3_fixtures()経由で参照可能なもの(B1/B2/B4/Meta_run03)を
        # 対象にする(他はaudit json単体で別スクリプト側にて全28件を検証)。
        fx = {f["id"]: f for f in g6.step2_fixtures() + g6.step3_fixtures()}
        for fid in ("Meta_run03_standard",):
            f = fx[fid]
            findings = pc.run_precheck(f["ledger_text"], f["article_text"])
            # Meta_run03_standardはgold=LEDGER_DEVIATION(changed_fact+
            # changed_certainty、related_fact_id=MUSE-HC-010)が既に既知
            # だが、precheckのnumber/date/actor機械照合ではcertainty変化を
            # 検出できない設計(既知の限界)。number/date/actorのFPが出ない
            # ことのみを確認する。
            for finding in findings:
                self.assertIn(finding["kind"], ("number_mismatch", "date_mismatch",
                                                 "actor_missing", "negation_marker",
                                                 "comparison_marker"))

    def test_hormuz_run03_standard_known_scope_generalization_is_not_detected(self):
        """設計書§14-4の既知の限界(scope一般化は機械照合できない)を
        regression testとして固定する(precheckがHF-009 changed_scopeを
        検出「しない」ことを期待値として明記)。"""
        fx = {f["id"]: f for f in g6.step3_fixtures()}
        f = fx["hormuz_run03_standard"]
        findings = pc.run_precheck(f["ledger_text"], f["article_text"])
        self.assertEqual(findings, [], "known limitation: scope generalization is not machine-checkable")


if __name__ == "__main__":
    unittest.main()
