# ============================================================
# er008_directional_fact_precheck_08_test.py
# ER-008-DIRECTIONAL-FACT-PRECHECK-08 Part H: Acceptance Tests
# ============================================================
from __future__ import annotations

import io
import json
import os
import unittest

import er008_directional_fact_precheck_08 as dfp


class CoreDirectionReversalTests(unittest.TestCase):
    """Part H項目1〜10。compare_direction()単体の直接比較(対象=主語が
    明確に一致した2文のペア)に対する判定を確認する。"""

    def test_1_more_fewer_reversal_fails(self):
        r = dfp.compare_direction("More people attended this year",
                                   "Fewer people attended this year")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_2_higher_lower_reversal_fails(self):
        r = dfp.compare_direction("Prices were higher than last year",
                                   "Prices were lower than last year")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_3_increase_decrease_reversal_fails(self):
        r = dfp.compare_direction("Sales increased by 10 percent",
                                   "Sales decreased by 10 percent")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_4_at_least_at_most_reversal_fails(self):
        r = dfp.compare_direction("at least one desk per employee",
                                   "at most one desk per employee")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_5_above_below_reversal_fails(self):
        r = dfp.compare_direction("The rate stayed above the threshold",
                                   "The rate stayed below the threshold")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_6_before_after_reversal_fails(self):
        r = dfp.compare_direction("The meeting happened before the announcement",
                                   "The meeting happened after the announcement")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_7_correct_synonym_passes(self):
        # increase(reference)とrise(candidate)は別カテゴリ表現だが、
        # 同じmagnitude軸のhigh方向であり、正しい同義表現として扱われる
        # べき(2軸統合設計の目的そのもの)。
        r = dfp.compare_direction("The share increased sharply",
                                   "The share rose sharply")
        self.assertEqual(r["verdict"], "MATCH")

    def test_8_ambiguous_direction_requires_review(self):
        r = dfp.compare_direction("Growth was reported this quarter",
                                   "The situation changed significantly")
        self.assertEqual(r["verdict"], "DIRECTION_REVIEW_REQUIRED")

    def test_9_no7_old_b1_point_two_fails(self):
        # Part G: 実際に発生したNo.7 B1 Point Twoの誤り。
        r = dfp.compare_direction("at least one desk per employee",
                                   "one desk per employee or fewer")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_9b_no7_old_b1_point_two_fails_full_sentence(self):
        ref = "at least one desk per employee, one desk or more"
        cand = ("A 2024 survey points in the other direction. The share of companies with "
                "one desk per employee or fewer fell from 56% in 2023 to 40% in 2024.")
        r = dfp.compare_direction(ref, cand)
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_10_no7_fixed_b1_point_two_passes(self):
        ref = "at least one desk per employee, one desk or more"
        cand = ("A 2024 survey points in the other direction. The share of companies with "
                "at least one desk per employee fell from 56% in 2023 to 40% in 2024.")
        r = dfp.compare_direction(ref, cand)
        self.assertEqual(r["verdict"], "MATCH")


class NotApplicableAndSymmetryTests(unittest.TestCase):
    def test_no_direction_words_not_applicable(self):
        r = dfp.compare_direction("The meeting was held in the main office",
                                   "The office hosted the meeting")
        self.assertEqual(r["verdict"], "NOT_APPLICABLE")

    def test_one_sided_direction_requires_review(self):
        r = dfp.compare_direction("Attendance increased this year",
                                   "People came to the event")
        self.assertEqual(r["verdict"], "DIRECTION_REVIEW_REQUIRED")

    def test_temporal_and_magnitude_do_not_cross_contaminate(self):
        # temporal(before/after)とmagnitude(more/fewer)は別軸であり、
        # 片方が一致していればもう片方の欠如だけでFAILにはしない。
        r = dfp.compare_direction("The event happened before the announcement, with more attendees",
                                   "The event happened before the announcement, with more attendees")
        self.assertEqual(r["verdict"], "MATCH")


class ThresholdVsTrendCategoryTests(unittest.TestCase):
    """trend(increase/decrease等)とthreshold(at least/at most等)を
    独立に評価すること、およびthresholdのみの衝突はcross-artifact層で
    FAILへ格上げしないことを確認する(実データ検証で判明した、比率と
    その逆数に近い量[例: デスク比率とデスク数]を混同するリスクへの
    対策)。"""

    def test_trend_and_threshold_conflict_independently_detected(self):
        # trendは一致(both increase-direction)だが、thresholdだけが逆
        r = dfp.compare_direction("The ratio increased to at most 1.0",
                                   "The ratio increased to at least 1.0")
        self.assertEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")
        cats = {c["category"] for c in r["conflicts"]}
        self.assertEqual(cats, {"threshold"})

    def test_downgrade_helper_demotes_threshold_only_conflict(self):
        raw = dfp.compare_direction("at least one item", "at most one item")
        self.assertEqual(raw["verdict"], "POTENTIAL_DIRECTION_REVERSAL")
        downgraded = dfp._downgrade_threshold_only_reversal(raw)
        self.assertEqual(downgraded["verdict"], "DIRECTION_REVIEW_REQUIRED")
        self.assertTrue(downgraded.get("downgraded_from_reversal"))

    def test_downgrade_helper_keeps_trend_conflict_as_fail(self):
        raw = dfp.compare_direction("Sales increased sharply", "Sales decreased sharply")
        downgraded = dfp._downgrade_threshold_only_reversal(raw)
        self.assertEqual(downgraded["verdict"], "POTENTIAL_DIRECTION_REVERSAL")


class No7RealDataRegressionTests(unittest.TestCase):
    """ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07で
    実際に発生したNo.7 F-008(CBRE desk ratio)を、実データ(VFL/Fact
    Ledger)を使って回帰確認する。**既知の限界(正直に記録)**: F-008は
    「比率」とその逆数に近い量(「従業員1人あたりのデスク数」)という、
    reciprocal(逆数)関係にある2つの主語を行き来するFactであり、
    本Precheckのrule-basedな表層語比較では、この種のFactを安全に
    FAILと判定できない(false negativeとなる)ことを、このテスト自体で
    明示的に記録する(検知漏れを隠さない)。"""

    OUT_DIR = "er006_output/pool_pilot_01/pool_n7_assigned_desks"

    def setUp(self):
        ledger_path = f"{self.OUT_DIR}/research/verified_fact_ledger.txt"
        if not os.path.exists(ledger_path):
            self.skipTest("No.7実データが存在しない環境のためスキップ")
        with io.open(ledger_path, encoding="utf-8") as f:
            ledger_text = f.read()
        self.ledger_line = next(
            l for l in ledger_text.splitlines() if "56" in l and "40" in l and "F-008" in l)

    def test_known_false_negative_old_wrong_script_not_flagged_as_fail(self):
        # 既知の限界: 誤りだった旧scriptは、cross-artifact層ではMATCH
        # またはWARN止まりになり、FAILへは至らない(reciprocal quantity
        # を機械的に解決できないため)。この挙動自体を回帰記録する。
        old_script = ("The share of companies with one desk per employee or fewer "
                       "fell from 56% in 2023 to 40% in 2024.")
        r = dfp._downgrade_threshold_only_reversal(dfp.compare_direction(self.ledger_line, old_script))
        self.assertNotEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL",
                             "既知の限界(reciprocal quantity)が変化した場合はこのテストを見直すこと")

    def test_fixed_script_not_hard_blocked(self):
        # 修正後(正しい)scriptが、thresholdのみの衝突でFAILへ誤爆
        # ブロックされないことを確認する(downgradeが機能している証跡)。
        new_script = ("The share of companies with at least one desk per employee "
                       "fell from 56% in 2023 to 40% in 2024.")
        r = dfp._downgrade_threshold_only_reversal(dfp.compare_direction(self.ledger_line, new_script))
        self.assertNotEqual(r["verdict"], "POTENTIAL_DIRECTION_REVERSAL")

    def test_vfl_internal_check_runs_without_error_on_real_data(self):
        vfl_path = f"{self.OUT_DIR}/research/stage_b3_vfl.json"
        with io.open(vfl_path, encoding="utf-8") as f:
            vfl_data = json.load(f)
        facts = vfl_data["parsed"]["facts"]
        f008 = next(f for f in facts if f["fact_id"] == "F-008")
        r = dfp.audit_vfl_fact_internal_consistency(f008)
        self.assertIn(r["verdict"], dfp.VALID_VERDICTS)

    def test_full_article_audit_no_unexpected_hard_fail(self):
        # 修正済みNo.7 B1記事全体を実行し、意図しないFAILが出ないことを
        # 確認する(false positive懸念の直接的な回帰guard)。
        article_path = f"{self.OUT_DIR}/b1b/article.md"
        vfl_path = f"{self.OUT_DIR}/research/stage_b3_vfl.json"
        with io.open(article_path, encoding="utf-8") as f:
            article_text = f.read()
        with io.open(f"{self.OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
            ledger_text = f.read()
        result = dfp.audit_article_directional_facts(article_text, ledger_text, vfl_path=vfl_path)
        self.assertNotEqual(result["overall_status"], "POTENTIAL_DIRECTION_REVERSAL",
                             f"修正済みNo.7 B1記事で予期しないFAILが発生: {result['results']}")


class GateFunctionTests(unittest.TestCase):
    def test_assert_raises_on_reversal(self):
        result = {"overall_status": "POTENTIAL_DIRECTION_REVERSAL",
                  "results": [{"verdict": "POTENTIAL_DIRECTION_REVERSAL", "reason": "x"}]}
        with self.assertRaises(dfp.DirectionalFactReversalError):
            dfp.assert_no_directional_reversal(result)

    def test_assert_does_not_raise_on_pass_or_warn(self):
        for status in ("PASS", "DIRECTION_REVIEW_REQUIRED"):
            with self.subTest(status=status):
                dfp.assert_no_directional_reversal({"overall_status": status, "results": []})


if __name__ == "__main__":
    unittest.main()
