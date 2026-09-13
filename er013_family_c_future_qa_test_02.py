# ============================================================
# er013_family_c_future_qa_test_02.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02
# ============================================================
# offline(¥0、API呼び出しなし)unit test。er013_family_c_future_scaffold_02
# /_ledger_02/_writer_02/_qa_02の新規ロジックを検証する。特に、Trial-01の
# 実際の完成記事(er013_output/family_c_future_trial_01/{a2,b1}/
# reader_facing_article.txt)を編集Gateへ入力し、FAILになること
# (=回帰の検証。今回の設計変更が実際にTrial-01の問題を検出できることの
# 確認)を含む。run_project_regression.py(pattern: er0*_test_*.py)から
# 自動探索される。
# ============================================================
from __future__ import annotations

import os
import unittest

import er013_family_c_future_ledger_02 as fcl2
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_scaffold_02 as fcs
import er013_family_c_future_writer_02 as fcw2

TRIAL01_A2_PATH = "er013_output/family_c_future_trial_01/a2/reader_facing_article.txt"
TRIAL01_B1_PATH = "er013_output/family_c_future_trial_01/b1/reader_facing_article.txt"

SAMPLE_ARTICLE_V2 = """## When the Kitchen Learns to Wait

[[META]]
Chose a single deep scene at one future point because the theme is about a
single turning-point moment, not a multi-stage trend.
[[/META]]

Right now, most evenings in this house end the same way: dishes piling up
while everyone is too tired to deal with them.

[[FACT: WS-003]]
Right now, home robots can handle simple, repeated chores, but they still
struggle with anything messy or unexpected.
[[/FACT]]

[[IMAGINED: around 2035]]
Picture a Tuesday evening in 2035, when a small kitchen robot quietly clears
the table while you help your daughter with her homework. The robot pauses,
waiting for you to finish a sentence, then continues.
[[/IMAGINED]]

If robots like this became common, kitchens might feel calmer, but families
could also lose some of the small routines that bring them together.

## In One Line

A calmer kitchen might come at a quiet cost."""


class MetaBlockTest(unittest.TestCase):
    def test_extract_and_strip_meta(self):
        blocks = fcq2.extract_meta_blocks(SAMPLE_ARTICLE_V2)
        self.assertEqual(len(blocks), 1)
        self.assertIn("single turning-point moment", blocks[0]["body"])
        stripped = fcq2.strip_meta_blocks(SAMPLE_ARTICLE_V2)
        self.assertNotIn("[[META]]", stripped)
        self.assertNotIn("turning-point moment", stripped)


class FactBlockTest(unittest.TestCase):
    def test_extract_fact_blocks_and_balance(self):
        blocks = fcq2.extract_fact_blocks(SAMPLE_ARTICLE_V2)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["ref_id"], "WS-003")
        self.assertIn("struggle with anything messy", blocks[0]["body"])
        check = fcq2.validate_fact_markers_balanced(SAMPLE_ARTICLE_V2)
        self.assertTrue(check["balanced"])

    def test_strip_fact_markers_keeps_body(self):
        stripped = fcq2.strip_fact_markers_keep_body(SAMPLE_ARTICLE_V2)
        self.assertNotIn("[[FACT:", stripped)
        self.assertNotIn("[[/FACT]]", stripped)
        self.assertIn("struggle with anything messy", stripped)

    def test_fact_marker_not_inside_imagined_in_sample(self):
        imagined_blocks = fcq_v1_extract(SAMPLE_ARTICLE_V2)
        issues = fcq2.check_fact_markers_inside_imagined(imagined_blocks)
        self.assertEqual(issues, [])


def fcq_v1_extract(text: str) -> list:
    import er013_family_c_future_qa_01 as fcq_v1
    return fcq_v1.extract_imagined_blocks(fcq2.strip_meta_blocks(text))


class RouteArticleV2Test(unittest.TestCase):
    def test_route_produces_clean_reader_text_and_layer1_text(self):
        routed = fcq2.route_article_for_qa_v2(SAMPLE_ARTICLE_V2)
        self.assertTrue(routed["marker_check_imagined"]["balanced"])
        self.assertTrue(routed["marker_check_fact"]["balanced"])
        self.assertEqual(len(routed["fact_blocks"]), 1)
        self.assertEqual(len(routed["meta_blocks"]), 1)
        # 読者向け本文にはどのマーカーも残らない
        for tag in ("[[META]]", "[[FACT:", "[[IMAGINED:"):
            self.assertNotIn(tag, routed["reader_text"])
        self.assertIn("Picture a Tuesday evening", routed["reader_text"])
        self.assertIn("struggle with anything messy", routed["reader_text"])
        # Layer1向けテキストには想像パッセージが漏れない
        self.assertNotIn("Picture a Tuesday evening", routed["layer1_text_for_fact_check"])
        self.assertNotIn("[[META]]", routed["layer1_text_for_fact_check"])
        # FACT例外の文はLayer1向けテキストにも残る(Fact Checker A'の対象)
        self.assertIn("struggle with anything messy", routed["layer1_text_for_fact_check"])


class ScaffoldTest(unittest.TestCase):
    def test_validate_scaffold_no_leakage_detects_digit_and_product(self):
        parsed = {
            "scaffold_items": [
                {"scaffold_id": "WS-001", "category": "capability_now",
                 "statement": "Home robots can already clean floors in 2023."},
                {"scaffold_id": "WS-002", "category": "limitation_now",
                 "statement": "A Roomba still cannot climb stairs."},
                {"scaffold_id": "WS-003", "category": "change_direction",
                 "statement": "Robots are slowly able to handle more varied chores."},
            ],
            "product_names_mentioned": ["Roomba"],
        }
        issues = fcs.validate_scaffold_no_leakage(parsed)
        types = {i["type"] for i in issues}
        self.assertIn("digit_in_scaffold_statement", types)
        self.assertIn("product_name_in_scaffold_statement", types)
        clean_ids = {i["scaffold_id"] for i in issues}
        self.assertNotIn("WS-003", clean_ids)

    def test_validate_scaffold_grounding_detects_unknown_fact_id(self):
        parsed = {"scaffold_items": [
            {"scaffold_id": "WS-001", "category": "capability_now", "statement": "x", "based_on": ["HR-999"]},
        ]}
        issues = fcs.validate_scaffold_grounding(["HR-001", "HR-002"], parsed)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["type"], "scaffold_based_on_unknown_fact_id")

    def test_build_world_scaffold_text_excludes_based_on_and_product_names(self):
        parsed = {
            "scaffold_items": [
                {"scaffold_id": "WS-001", "category": "capability_now",
                 "statement": "Robots can clean floors regularly.", "based_on": ["HR-001"]},
            ],
            "product_names_mentioned": ["Roomba"],
        }
        text = fcs.build_world_scaffold_text_for_writer(parsed)
        self.assertIn("Robots can clean floors regularly.", text)
        self.assertNotIn("HR-001", text)
        self.assertNotIn("Roomba", text)


class Layer23V2Test(unittest.TestCase):
    def test_grounding_validation_accepts_scaffold_and_assumption_ids(self):
        parsed = {
            "future_assumptions": [{"assumption_id": "FA-001", "assumption": "x", "based_on": ["WS-001"]}],
            "imagined_futures": [{"scene_id": "IF-001", "timeframe": "around 2035",
                                   "scene_summary": "x", "grounded_in": ["FA-001", "WS-002"]}],
        }
        issues = fcl2.validate_layer23_v2_grounding(["WS-001", "WS-002"], parsed)
        self.assertEqual(issues, [])

    def test_grounding_validation_detects_unknown_ref(self):
        parsed = {
            "future_assumptions": [{"assumption_id": "FA-001", "assumption": "x", "based_on": ["WS-999"]}],
            "imagined_futures": [],
        }
        issues = fcl2.validate_layer23_v2_grounding(["WS-001"], parsed)
        self.assertEqual(len(issues), 1)

    def test_assemble_world_package_text_excludes_layer1_raw(self):
        world_scaffold_text = "[WORLD_SCAFFOLD]\nscaffold_id: WS-001\ncategory: capability_now\nstatement: Robots can clean floors.\n"
        parsed = {
            "structure_rationale": "single scene chosen for focus",
            "future_assumptions": [{"assumption_id": "FA-001", "assumption": "If this continues, homes change.",
                                     "based_on": ["WS-001"]}],
            "imagined_futures": [{"scene_id": "IF-001", "timeframe": "around 2035",
                                   "scene_summary": "a calmer kitchen", "grounded_in": ["FA-001"]}],
        }
        text = fcl2.assemble_world_package_text(world_scaffold_text, parsed)
        self.assertIn("WS-001", text)
        self.assertIn("FA-001", text)
        self.assertIn("IF-001", text)
        self.assertIn("single scene chosen for focus", text)
        self.assertNotIn("[VERIFIED]", text)  # Layer1生テキストのタグは含まれない


class WriterV2PromptTest(unittest.TestCase):
    def test_prompt_contains_ban_list_and_fact_limit(self):
        prompt = fcw2.build_family_c_writer_v2_prompt("home robots", "a2", "[WORLD_SCAFFOLD]\n...")
        self.assertIn("study", prompt.lower())
        self.assertIn("研究", prompt)
        self.assertIn(str(fcw2.MAX_FACT_EXCEPTIONS), prompt)
        self.assertIn("[[META]]", prompt)
        self.assertIn("[[FACT:", prompt)
        self.assertIn("[[IMAGINED:", prompt)

    def test_prompt_appends_gate_feedback_when_provided(self):
        prompt = fcw2.build_family_c_writer_v2_prompt("home robots", "b1", "[WORLD_SCAFFOLD]\n...",
                                                        gate_feedback="numeric_hits=3")
        self.assertIn("numeric_hits=3", prompt)

    def test_invalid_level_raises(self):
        with self.assertRaises(ValueError):
            fcw2.build_family_c_writer_v2_prompt("home robots", "c1", "[WORLD_SCAFFOLD]\n...")


class EditorialGateDeterministicScanTest(unittest.TestCase):
    def test_clean_scene_first_article_passes(self):
        reader_text = (
            "## A Quiet Kitchen\n\n"
            "Picture a Tuesday evening when a small kitchen robot quietly clears the "
            "table while you help your daughter with her homework.\n\n"
            "If robots like this became common, kitchens might feel calmer, but "
            "families could also lose some of the small routines that bring them "
            "together.\n\n"
            "A calmer kitchen might come at a quiet cost."
        )
        result = fcq2.scan_editorial_gate(reader_text, fact_blocks=[], banned_product_names=["Roomba"])
        self.assertEqual(result["overall_status"], "PASS")
        self.assertEqual(result["numeric_hits"], [])
        self.assertEqual(result["research_term_hits"], [])

    def test_allows_future_timeframe_year_but_not_statistics(self):
        reader_text = "Picture a home around 2035, when the robot quietly clears the table."
        result = fcq2.scan_editorial_gate(reader_text, fact_blocks=[], banned_product_names=[])
        self.assertEqual(result["numeric_hits"], [])
        self.assertEqual(result["overall_status"], "PASS")

    def test_allows_future_year_followed_by_sentence_final_period(self):
        # 回帰テスト: "around 2035."のように年の直後に文末ピリオドが続く場合、
        # 数字トークン抽出が誤ってピリオドを含めて統計値と誤判定しないこと
        # (実Trial-02実行中に発見・修正した不具合)。
        reader_text = "Picture a weekday morning around 2035. A small home robot moves quietly."
        result = fcq2.scan_editorial_gate(reader_text, fact_blocks=[], banned_product_names=[])
        self.assertEqual(result["numeric_hits"], [])
        self.assertEqual(result["overall_status"], "PASS")

    def test_allows_future_year_followed_by_comma(self):
        reader_text = "In 2035, a robot quietly clears the table while a child does homework."
        result = fcq2.scan_editorial_gate(reader_text, fact_blocks=[], banned_product_names=[])
        self.assertEqual(result["numeric_hits"], [])
        self.assertEqual(result["overall_status"], "PASS")

    def test_detects_statistic_and_research_term_and_product_name(self):
        reader_text = (
            "In 2023, more than 2.1 million robots were sold, according to a survey. "
            "Many families bought a Roomba to help with chores."
        )
        result = fcq2.scan_editorial_gate(reader_text, fact_blocks=[], banned_product_names=["Roomba"])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(result["numeric_hits"])
        self.assertTrue(result["research_term_hits"])
        self.assertIn("Roomba", result["product_name_hits"])

    def test_fact_exception_over_limit_fails(self):
        reader_text = "A calm scene with no numbers or research words at all."
        fact_blocks = [{"ref_id": "WS-001"}, {"ref_id": "WS-002"}, {"ref_id": "WS-003"}]
        result = fcq2.scan_editorial_gate(reader_text, fact_blocks=fact_blocks, banned_product_names=[])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertFalse(result["fact_exception_within_limit"])

    def test_opening_paragraph_extraction_skips_heading(self):
        reader_text = "## Heading Only\n\nThe first real paragraph starts here.\n\nSecond paragraph."
        opening = fcq2.get_opening_paragraph(reader_text)
        self.assertEqual(opening, "The first real paragraph starts here.")


class Trial01RegressionTest(unittest.TestCase):
    """Trial-01の実際の完成記事(冒頭から統計値が並ぶ/study found型表現/
    製品名列挙が残存)を、今回新設した編集Gateへ入力し、FAILになることを
    確認する(=回帰の検証。設計変更が実データの問題を検出できることの
    証跡)。"""

    def _run_gate_on_file(self, path: str) -> dict:
        if not os.path.exists(path):
            self.skipTest(f"Trial-01成果物が見つかりません: {path}")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        banned_products = ["Roomba", "iRobot", "CLOiD", "LG CLOiD", "YouGov", "Mobile ALOHA"]
        return fcq2.scan_editorial_gate(text, fact_blocks=[], banned_product_names=banned_products)

    def test_trial01_a2_fails_editorial_gate(self):
        result = self._run_gate_on_file(TRIAL01_A2_PATH)
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(result["numeric_hits"], "Trial-01 A2には統計値が残っているはず")

    def test_trial01_b1_fails_editorial_gate(self):
        result = self._run_gate_on_file(TRIAL01_B1_PATH)
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(result["numeric_hits"], "Trial-01 B1には統計値が残っているはず")
        self.assertTrue(result["research_term_hits"], "Trial-01 B1には研究語(survey/study等)が残っているはず")

    def test_trial01_a2_opening_paragraph_is_not_scene_first(self):
        if not os.path.exists(TRIAL01_A2_PATH):
            self.skipTest("Trial-01成果物が見つかりません")
        with open(TRIAL01_A2_PATH, encoding="utf-8") as f:
            text = f.read()
        opening = fcq2.get_opening_paragraph(text)
        # Trial-01 A2の冒頭段落は場面描写ではなく、未来を巡る一般論の宣言文
        self.assertNotIn("Picture", opening)


if __name__ == "__main__":
    unittest.main()
