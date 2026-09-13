# ============================================================
# er013_family_c_future_qa_test_01.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01
# ============================================================
# offline(¥0、API呼び出しなし)unit test。Family C(Future)の
# Layerルーティング(マーカー抽出・Layer1限定テキスト生成・マーカー除去・
# 現在事実紛れ込み検出のheuristic)、Ledgerの3層組み立て・grounding検証、
# Writer Promptの構築を検証する。run_project_regression.py(pattern:
# er0*_test_*.py)から自動探索される。
# ============================================================
from __future__ import annotations

import unittest

import er013_family_c_future_ledger_01 as fcl
import er013_family_c_future_qa_01 as fcq
import er013_family_c_future_writer_01 as fcw

SAMPLE_ARTICLE = """## When the Robot Learns Your Kitchen

Right now, many families already juggle dinner, dishes, and homework at once.

[[IMAGINED: around 2035]]
Picture a Tuesday evening in 2035, when a small kitchen robot quietly clears
the table while you help your daughter with her homework. The robot pauses,
waiting for you to finish a sentence, then continues.
[[/IMAGINED]]

If robots like this became common, kitchens might feel calmer, but families
could also lose some of the small routines that bring them together.

[[IMAGINED: a decade later]]
Now imagine a home where the robot has already replaced every chore, and
today it also decides what the family eats.
[[/IMAGINED]]

## In One Line

A calmer kitchen might come at a quiet cost."""


class ExtractImaginedBlocksTest(unittest.TestCase):
    def test_extracts_two_blocks_in_order(self):
        blocks = fcq.extract_imagined_blocks(SAMPLE_ARTICLE)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]["timeframe"], "around 2035")
        self.assertIn("Picture a Tuesday evening", blocks[0]["body"])
        self.assertEqual(blocks[1]["timeframe"], "a decade later")
        self.assertIn("Now imagine a home", blocks[1]["body"])

    def test_no_blocks_returns_empty_list(self):
        self.assertEqual(fcq.extract_imagined_blocks("no markers here"), [])
        self.assertEqual(fcq.extract_imagined_blocks(""), [])


class MarkerBalanceTest(unittest.TestCase):
    def test_balanced_markers(self):
        result = fcq.validate_markers_balanced(SAMPLE_ARTICLE)
        self.assertTrue(result["balanced"])
        self.assertEqual(result["open_count"], 2)
        self.assertEqual(result["close_count"], 2)
        self.assertEqual(result["matched_blocks"], 2)

    def test_unbalanced_markers_detected(self):
        broken = SAMPLE_ARTICLE.replace(fcq.IMAGINED_CLOSE, "", 1)  # 終了マーカーを1つ欠落させる
        result = fcq.validate_markers_balanced(broken)
        self.assertFalse(result["balanced"])
        self.assertEqual(result["open_count"], 2)
        self.assertEqual(result["close_count"], 1)


class ReaderTextTest(unittest.TestCase):
    def test_strip_markers_keeps_body_removes_tags(self):
        reader_text = fcq.strip_markers_for_reader(SAMPLE_ARTICLE)
        self.assertNotIn("[[IMAGINED:", reader_text)
        self.assertNotIn("[[/IMAGINED]]", reader_text)
        self.assertIn("Picture a Tuesday evening in 2035", reader_text)
        self.assertIn("Now imagine a home", reader_text)


class Layer1PlaceholderTest(unittest.TestCase):
    def test_imagined_content_is_not_leaked_to_fact_check_text(self):
        layer1_text = fcq.build_layer1_placeholder_text(SAMPLE_ARTICLE)
        self.assertNotIn("Picture a Tuesday evening", layer1_text)
        self.assertNotIn("Now imagine a home", layer1_text)
        self.assertNotIn("[[IMAGINED:", layer1_text)
        self.assertEqual(layer1_text.count(fcq.DEFAULT_LAYER1_PLACEHOLDER), 2)
        # 枠外の現在事実文はそのまま残る(Layer1は厳格Fact Checkの対象のため)
        self.assertIn("Right now, many families already juggle", layer1_text)
        self.assertIn("In One Line", layer1_text)

    def test_custom_placeholder(self):
        text = fcq.build_layer1_placeholder_text(SAMPLE_ARTICLE, placeholder="[REMOVED]")
        self.assertEqual(text.count("[REMOVED]"), 2)


class PresentTenseLeakageTest(unittest.TestCase):
    def test_detects_already_today_present_claim(self):
        body = ("Now imagine a home where the robot has already replaced every chore, and "
                "today it also decides what the family eats.")
        hits = fcq.detect_present_tense_leakage(body)
        self.assertTrue(hits, "「already」+現在時制の紛れ込みを検出できていない")

    def test_no_false_positive_on_pure_future_scene(self):
        body = "Picture a quiet kitchen where a small robot might one day fold the laundry."
        hits = fcq.detect_present_tense_leakage(body)
        self.assertEqual(hits, [])


class UnhedgedFutureClaimTest(unittest.TestCase):
    def test_detects_will_without_hedge_nearby(self):
        text = "Robots will completely replace every home chore within five years."
        hits = fcq.detect_unhedged_future_claims(text)
        self.assertTrue(hits)

    def test_no_flag_when_hedged(self):
        text = "If this trend continues, robots might eventually take on more chores."
        hits = fcq.detect_unhedged_future_claims(text)
        self.assertEqual(hits, [])


class RouteArticleForQaTest(unittest.TestCase):
    def test_route_produces_consistent_outputs(self):
        routed = fcq.route_article_for_qa(SAMPLE_ARTICLE)
        self.assertTrue(routed["marker_check"]["balanced"])
        self.assertEqual(len(routed["imagined_blocks"]), 2)
        self.assertNotIn("[[IMAGINED:", routed["reader_text"])
        self.assertNotIn("Picture a Tuesday evening", routed["layer1_text_for_fact_check"])
        self.assertEqual(len(routed["present_tense_leakage_heuristic"]), 1)  # 2番目のblockのみ検知想定


class FutureFramingQaPromptTest(unittest.TestCase):
    def test_prompt_contains_all_five_items_and_blocks(self):
        blocks = fcq.extract_imagined_blocks(SAMPLE_ARTICLE)
        prompt = fcq.build_future_framing_qa_prompt(
            topic="Home robots and housework",
            layer1_reference_text="[PRESENT_FACT]\n[VERIFIED] F001: sample fact\n",
            imagined_blocks=blocks,
            layer1_body_excerpt="Right now, many families already juggle dinner, dishes, and homework at once.",
        )
        for keyword in ("framing_violations", "fabricated_present_facts", "unlabeled_assumptions",
                        "discovery_style_leakage", "future_stated_as_fact_outside_scenes"):
            self.assertIn(keyword, prompt)
        self.assertIn("Picture a Tuesday evening", prompt)
        self.assertIn("Now imagine a home", prompt)


class LedgerLayer1Test(unittest.TestCase):
    def test_build_layer1_ledger_text_wraps_unchanged_body(self):
        original = "[VERIFIED] F001: sample claim\n  source: example\n"
        wrapped = fcl.build_layer1_ledger_text(original)
        self.assertTrue(wrapped.startswith(fcl.PRESENT_FACT_TAG))
        self.assertIn("[VERIFIED] F001: sample claim", wrapped)

    def test_extract_present_fact_ids(self):
        text = "[VERIFIED] F001: claim a\n[VERIFIED] F002: claim b\nnot a fact line\n"
        ids = fcl.extract_present_fact_ids(text)
        self.assertEqual(ids, ["F001", "F002"])


class LedgerGroundingValidationTest(unittest.TestCase):
    def test_valid_grounding_produces_no_issues(self):
        present_fact_ids = ["F001", "F002"]
        layer23 = {
            "future_assumptions": [
                {"assumption_id": "A1", "assumption": "if adoption grows", "based_on": ["F001"]},
            ],
            "imagined_futures": [
                {"scene_id": "S1", "timeframe": "around 2035", "scene_summary": "...",
                 "grounded_in": ["A1", "F002"]},
            ],
        }
        issues = fcl.validate_layer23_grounding(present_fact_ids, layer23)
        self.assertEqual(issues, [])

    def test_unknown_reference_is_flagged(self):
        present_fact_ids = ["F001"]
        layer23 = {
            "future_assumptions": [
                {"assumption_id": "A1", "assumption": "...", "based_on": ["F999"]},
            ],
            "imagined_futures": [
                {"scene_id": "S1", "timeframe": "...", "scene_summary": "...", "grounded_in": ["A999"]},
            ],
        }
        issues = fcl.validate_layer23_grounding(present_fact_ids, layer23)
        types = {i["type"] for i in issues}
        self.assertIn("assumption_based_on_unknown_fact_id", types)
        self.assertIn("scene_grounded_in_unknown_id", types)

    def test_no_specific_basis_sentinel_is_allowed(self):
        issues = fcl.validate_layer23_grounding(["F001"], {
            "future_assumptions": [
                {"assumption_id": "A1", "assumption": "...", "based_on": [fcl.NO_SPECIFIC_BASIS]},
            ],
            "imagined_futures": [],
        })
        self.assertEqual(issues, [])


class AssembleThreeLayerLedgerTest(unittest.TestCase):
    def test_assembles_all_three_tags_in_order(self):
        layer1_text = fcl.build_layer1_ledger_text("[VERIFIED] F001: sample claim\n")
        layer23 = {
            "future_assumptions": [
                {"assumption_id": "A1", "assumption": "if adoption grows", "based_on": ["F001"]},
            ],
            "imagined_futures": [
                {"scene_id": "S1", "timeframe": "around 2035", "scene_summary": "a calmer kitchen",
                 "grounded_in": ["A1"]},
            ],
        }
        assembled = fcl.assemble_three_layer_ledger_text(layer1_text, layer23)
        idx_present = assembled.index(fcl.PRESENT_FACT_TAG)
        idx_assumption = assembled.index(fcl.FUTURE_ASSUMPTION_TAG)
        idx_imagined = assembled.index(fcl.IMAGINED_FUTURE_TAG)
        self.assertTrue(idx_present < idx_assumption < idx_imagined)
        self.assertIn("F001: sample claim", assembled)
        self.assertIn("assumption_id: A1", assembled)
        self.assertIn("scene_id: S1", assembled)


class WriterPromptTest(unittest.TestCase):
    def test_build_prompt_contains_marker_template_and_ledger(self):
        prompt = fcw.build_family_c_writer_prompt(
            topic="Home robots and housework", level="a2",
            three_layer_ledger_text="[PRESENT_FACT]\n[VERIFIED] F001: sample\n")
        self.assertIn("[[IMAGINED:", prompt)
        self.assertIn(fcw.IMAGINED_CLOSE, prompt)
        self.assertIn("[VERIFIED] F001: sample", prompt)
        self.assertIn("A2レベル", prompt)

    def test_build_prompt_b1_level_guidance(self):
        prompt = fcw.build_family_c_writer_prompt(
            topic="Home robots and housework", level="b1",
            three_layer_ledger_text="[PRESENT_FACT]\n")
        self.assertIn("B1レベル", prompt)

    def test_unknown_level_raises(self):
        with self.assertRaises(ValueError):
            fcw.build_family_c_writer_prompt(topic="x", level="c1", three_layer_ledger_text="")


if __name__ == "__main__":
    unittest.main()
