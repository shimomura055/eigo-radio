# ============================================================
# er013_family_c_future_qa_test_03.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FINAL-TUNING-TRIAL-03
# ============================================================
# offline(¥0、API呼び出しなし)unit test。er013_family_c_future_writer_03
# /_qa_03の新規ロジック(枠内hedge密度スキャン・語数スキャン・編集Gate v3
# 統合)を検証する。既存er013_family_c_future_qa_test_02.py(24件)は
# 無変更で対象外(fcq2自体は本タスクで一切改変していない)。
# run_project_regression.py(pattern: er0*_test_*.py)から自動探索される。
# ============================================================
from __future__ import annotations

import os
import unittest

import er013_family_c_future_qa_03 as fcq3
import er013_family_c_future_writer_03 as fcw3

TRIAL02_A2_RAW_PATH = "er013_output/family_c_future_trial_02/a2/writer_raw_article.txt"
TRIAL02_B1_RAW_PATH = "er013_output/family_c_future_trial_02/b1/writer_raw_article.txt"


class HedgeDensityScanTest(unittest.TestCase):
    def test_zero_hedge_block_within_limit(self):
        blocks = [{"timeframe": "around 2035", "body": (
            "Picture a Tuesday evening in 2035. A small kitchen robot clears "
            "the table. It pauses. The child laughs and waves at it. The "
            "robot waits, then continues.")}]
        result = fcq3.compute_imagined_hedge_density(blocks)
        self.assertEqual(result["hedge_density"], 0.0)
        self.assertTrue(result["within_limit"])

    def test_high_hedge_block_exceeds_limit(self):
        blocks = [{"timeframe": "around 2035", "body": (
            "This might be a quiet evening. The robot could be cleaning. "
            "A person may feel relief. It might also feel strange. "
            "Perhaps the child would notice.")}]
        result = fcq3.compute_imagined_hedge_density(blocks)
        self.assertGreater(result["hedge_density"], fcq3.HEDGE_DENSITY_MAX_IN_MARKERS)
        self.assertFalse(result["within_limit"])

    def test_no_blocks_defaults_to_zero_density(self):
        result = fcq3.compute_imagined_hedge_density([])
        self.assertEqual(result["hedge_density"], 0.0)
        self.assertTrue(result["within_limit"])

    def test_multiple_blocks_are_pooled_not_averaged_per_block(self):
        blocks = [
            {"timeframe": "t1", "body": "The robot moves. It stops. It waits."},
            {"timeframe": "t2", "body": "This could be different. It might change again."},
        ]
        result = fcq3.compute_imagined_hedge_density(blocks)
        self.assertEqual(result["total_sentence_count"], 5)
        self.assertEqual(result["total_hedge_sentence_count"], 2)
        self.assertAlmostEqual(result["hedge_density"], 2 / 5)


class WordCountScanTest(unittest.TestCase):
    def test_within_range_passes(self):
        text = " ".join(["word"] * 500)
        result = fcq3.scan_word_count(text, 450, 600)
        self.assertTrue(result["within_range"])
        self.assertEqual(result["word_count"], 500)

    def test_over_range_fails(self):
        text = " ".join(["word"] * 1161)
        result = fcq3.scan_word_count(text, 450, 600)
        self.assertFalse(result["within_range"])

    def test_under_range_fails(self):
        text = " ".join(["word"] * 100)
        result = fcq3.scan_word_count(text, 450, 600)
        self.assertFalse(result["within_range"])


class EditorialGateV3IntegrationTest(unittest.TestCase):
    def test_clean_article_within_all_limits_passes(self):
        reader_text = (
            "## A Quiet Kitchen\n\n"
            "Picture a Tuesday evening when a small kitchen robot quietly clears "
            "the table while you help your daughter with her homework. " * 22
        )
        # 22回繰り返しで語数を目安範囲(450-600)へ寄せる(hedge語を含まない
        # 場面文のみで構成、統計値・研究語・製品名も含まない)。
        imagined_blocks = [{"timeframe": "t1", "body": reader_text}]
        result = fcq3.scan_editorial_gate_v3(
            reader_text, fact_blocks=[], banned_product_names=[],
            imagined_blocks=imagined_blocks, level="a2", word_count_range=(450, 600))
        self.assertEqual(result["overall_status"], "PASS", result["fail_reasons"])

    def test_high_hedge_density_fails_gate(self):
        reader_text = (
            "This might change everything. The robot could be helpful. "
            "A person may feel relief. It might also feel strange. "
            "Perhaps the family would notice a difference soon."
        )
        imagined_blocks = [{"timeframe": "t1", "body": reader_text}]
        result = fcq3.scan_editorial_gate_v3(
            reader_text, fact_blocks=[], banned_product_names=[],
            imagined_blocks=imagined_blocks, level="a2", word_count_range=(1, 1000))
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(any("imagined_hedge_density" in r for r in result["fail_reasons"]))

    def test_word_count_out_of_range_fails_gate(self):
        reader_text = "A calm robot scene with no numbers or research words at all. " * 30
        result = fcq3.scan_editorial_gate_v3(
            reader_text, fact_blocks=[], banned_product_names=[],
            imagined_blocks=[], level="a2", word_count_range=(450, 600))
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(any("word_count=" in r for r in result["fail_reasons"]))

    def test_v2_checks_still_enforced_unchanged(self):
        reader_text = (
            "In 2023, more than 2.1 million robots were sold, according to a survey. "
            "Many families bought a Roomba to help with chores."
        )
        result = fcq3.scan_editorial_gate_v3(
            reader_text, fact_blocks=[], banned_product_names=["Roomba"],
            imagined_blocks=[], level="a2", word_count_range=(1, 1000))
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(result["numeric_hits"])
        self.assertTrue(result["research_term_hits"])
        self.assertIn("Roomba", result["product_name_hits"])


class Trial02RegressionTest(unittest.TestCase):
    """Trial-02の実際の記事(枠内hedge密度は既に低いが、語数がA2目安の約
    2倍に達している実データ)を編集Gate v3へ入力し、語数超過でFAILになる
    ことを確認する(=新スキャン追加が実際にTrial-02の残課題を検出できる
    ことの回帰証跡)。"""

    def _route_and_scan(self, path: str, level: str, word_count_range: tuple) -> dict:
        if not os.path.exists(path):
            self.skipTest(f"Trial-02成果物が見つかりません: {path}")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        routed = fcq3.route_article_for_qa_v2(text)
        return fcq3.scan_editorial_gate_v3(
            routed["reader_text"], routed["fact_blocks"], banned_product_names=[],
            imagined_blocks=routed["imagined_blocks"], level=level,
            word_count_range=word_count_range), routed

    def test_trial02_a2_fails_on_word_count(self):
        result, routed = self._route_and_scan(
            TRIAL02_A2_RAW_PATH, "a2", fcw3.WORD_COUNT_TARGET_RANGE["a2"])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertFalse(result["word_count_result"]["within_range"])
        self.assertGreater(result["word_count_result"]["word_count"],
                            fcw3.WORD_COUNT_TARGET_RANGE["a2"][1])

    def test_trial02_a2_imagined_hedge_density_was_already_low(self):
        # 実データ確認: Trial-02 A2の[[IMAGINED]]枠内自体は、既にhedge密度が
        # 低かった(hedging過多は枠外に集中していたという発見の記録)。
        if not os.path.exists(TRIAL02_A2_RAW_PATH):
            self.skipTest("Trial-02成果物が見つかりません")
        with open(TRIAL02_A2_RAW_PATH, encoding="utf-8") as f:
            text = f.read()
        routed = fcq3.route_article_for_qa_v2(text)
        hedge_result = fcq3.compute_imagined_hedge_density(routed["imagined_blocks"])
        self.assertTrue(hedge_result["within_limit"])

    def test_trial02_b1_fails_on_word_count(self):
        result, routed = self._route_and_scan(
            TRIAL02_B1_RAW_PATH, "b1", fcw3.WORD_COUNT_TARGET_RANGE["b1"])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertFalse(result["word_count_result"]["within_range"])


class WriterV3PromptTest(unittest.TestCase):
    def test_prompt_retains_v2_ban_list_and_fact_limit(self):
        prompt = fcw3.build_family_c_writer_v3_prompt("home robots", "a2", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("study", prompt.lower())
        self.assertIn("研究", prompt)
        self.assertIn(str(fcw3.MAX_FACT_EXCEPTIONS), prompt)
        self.assertIn("[[META]]", prompt)
        self.assertIn("[[FACT:", prompt)
        self.assertIn("[[IMAGINED:", prompt)

    def test_prompt_instructs_no_hedging_inside_markers(self):
        prompt = fcw3.build_family_c_writer_v3_prompt("home robots", "a2", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("hedging語を使う", prompt)
        self.assertIn("現在形・断定調", prompt)

    def test_prompt_instructs_emotion_contrast_and_action_or_quote(self):
        prompt = fcw3.build_family_c_writer_v3_prompt("home robots", "a2", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("短い台詞", prompt)
        self.assertIn("対比", prompt)

    def test_prompt_contains_word_count_target(self):
        prompt_a2 = fcw3.build_family_c_writer_v3_prompt("home robots", "a2", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("450", prompt_a2)
        self.assertIn("600", prompt_a2)
        prompt_b1 = fcw3.build_family_c_writer_v3_prompt("home robots", "b1", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("500", prompt_b1)
        self.assertIn("700", prompt_b1)

    def test_prompt_prohibits_shortening_into_research_explanation(self):
        prompt = fcw3.build_family_c_writer_v3_prompt("home robots", "a2", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("研究解説的な", prompt)

    def test_prompt_appends_gate_feedback_when_provided(self):
        prompt = fcw3.build_family_c_writer_v3_prompt("home robots", "b1", "[WORLD_SCAFFOLD]\n...",
                                                        gate_feedback="word_count=1161")
        self.assertIn("word_count=1161", prompt)

    def test_invalid_level_raises(self):
        with self.assertRaises(ValueError):
            fcw3.build_family_c_writer_v3_prompt("home robots", "c1", "[WORLD_SCAFFOLD]\n...")


if __name__ == "__main__":
    unittest.main()
