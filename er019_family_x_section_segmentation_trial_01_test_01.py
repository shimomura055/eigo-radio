# ============================================================
# er019_family_x_section_segmentation_trial_01_test_01.py
# NEWS-FAMILY-X-SECTION-SEGMENTATION-TRIAL-01
# ============================================================
# er019_family_x_section_segmentation_trial_01.pyの決定論的ロジック
# (ブロック分割/方式Aの移動/fact_tokens_check相当/文単位diff)の単体
# テスト。実API呼び出しは一切行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_section_segmentation_trial_01_test_01 -v
# ============================================================
from __future__ import annotations

import json
import unittest

import er019_family_x_section_segmentation_trial_01 as seg


class SplitBlocksRoundTripTests(unittest.TestCase):
    def test_split_and_join_is_lossless(self):
        text = "# Title\n\nPara one. Sentence two.\n\n### Heading\n\nPara three."
        blocks = seg.split_blocks(text)
        self.assertEqual("\n\n".join(blocks), text)

    def test_real_input_articles_round_trip(self):
        for path in seg.LEVEL_ARTICLE_PATHS.values():
            text = seg.load_text(path).strip()
            blocks = seg.split_blocks(text)
            self.assertEqual("\n\n".join(blocks), text, msg=f"round-trip mismatch: {path}")


class MoveParagraphAfterHeadingTests(unittest.TestCase):
    def test_swaps_only_the_targeted_paragraph_and_heading(self):
        blocks = ["# Title", "Para A.", "Para B.", "Para C to move.", "### Heading", "Para D."]
        new_blocks, record = seg.move_paragraph_after_heading(blocks, "### Heading", "Para C to move.")
        self.assertEqual(new_blocks, ["# Title", "Para A.", "Para B.", "### Heading", "Para C to move.", "Para D."])
        self.assertEqual(record["moved_paragraph"], "Para C to move.")

    def test_raises_when_preceding_paragraph_does_not_match_expected(self):
        blocks = ["# Title", "Para A.", "### Heading", "Para B."]
        with self.assertRaises(ValueError):
            seg.move_paragraph_after_heading(blocks, "### Heading", "Not the actual paragraph.")

    def test_real_advanced_article_moves_expected_ng_paragraph(self):
        text = seg.load_text(seg.LEVEL_ARTICLE_PATHS["b1b"]).strip()
        blocks = seg.split_blocks(text)
        expected = seg.BEFORE_BOUNDARY_JUDGMENT["b1b"][1]["preceding_paragraph"]
        old_idx = blocks.index(seg.TARGET_HEADING)
        new_blocks, record = seg.move_paragraph_after_heading(blocks, seg.TARGET_HEADING, expected)
        new_idx = new_blocks.index(seg.TARGET_HEADING)
        self.assertEqual(new_blocks[new_idx + 1], expected)
        self.assertNotEqual(blocks[old_idx - 1], new_blocks[new_idx - 1])


class FactTokensCheckTests(unittest.TestCase):
    def test_identical_texts_match(self):
        text = 'Prada showed 3 bags. She said "hello" today.'
        result = seg.fact_tokens_check(text, text)
        self.assertTrue(result["overall_fact_tokens_match"])

    def test_reordered_but_identical_content_still_matches(self):
        before = "Sentence one about Prada. Sentence two with 44%."
        after = "Sentence two with 44%. Sentence one about Prada."
        result = seg.fact_tokens_check(before, after)
        self.assertTrue(result["numbers_match"])
        self.assertTrue(result["proper_noun_words_match"])

    def test_detects_changed_number(self):
        before = "Sales rose 44% this year."
        after = "Sales rose 45% this year."
        result = seg.fact_tokens_check(before, after)
        self.assertFalse(result["numbers_match"])
        self.assertFalse(result["overall_fact_tokens_match"])

    def test_detects_new_proper_noun(self):
        before = "Prada showed bags."
        after = "Prada and Loewe showed bags."
        result = seg.fact_tokens_check(before, after)
        self.assertFalse(result["proper_noun_words_match"])

    def test_heading_without_terminal_punctuation_does_not_leak_into_next_paragraph(self):
        """見出し(文末記号なし)が次の段落の先頭文へ連結され、段落の並び順を
        変えただけでproper_noun判定が変わってしまう回帰を防ぐ(実データで
        発見したバグの再現テスト)。"""
        before = "Para A ends here.\n\nYet this stays. Vogue also covered bags.\n\n### Heading\n\nVogue featured Prada."
        after = "Para A ends here.\n\n### Heading\n\nYet this stays. Vogue also covered bags.\n\nVogue featured Prada."
        result = seg.fact_tokens_check(before, after)
        self.assertTrue(result["proper_noun_words_match"])
        self.assertTrue(result["overall_fact_tokens_match"])

    def test_real_advanced_article_before_after_fact_tokens_match(self):
        before_text = seg.load_text(seg.LEVEL_ARTICLE_PATHS["b1b"]).strip()
        before_blocks = seg.split_blocks(before_text)
        expected = seg.BEFORE_BOUNDARY_JUDGMENT["b1b"][1]["preceding_paragraph"]
        after_blocks, _ = seg.move_paragraph_after_heading(before_blocks, seg.TARGET_HEADING, expected)
        after_text = "\n\n".join(after_blocks)
        result = seg.fact_tokens_check(before_text, after_text)
        self.assertTrue(result["overall_fact_tokens_match"], msg=json.dumps(result, indent=2))


class SentenceLevelDiffTests(unittest.TestCase):
    def test_pure_move_is_classified_move_only(self):
        before = "Para A.\n\nPara B to move.\n\n### Heading\n\nPara C."
        after = "Para A.\n\n### Heading\n\nPara B to move.\n\nPara C."
        diff = seg.sentence_level_diff(before, after)
        self.assertTrue(diff["multiset_equal"])
        self.assertEqual(diff["classification"], "MOVE_ONLY_NO_ADD_NO_REMOVE")

    def test_wording_change_is_not_classified_move_only(self):
        before = "Para A.\n\n### Heading\n\nPara B."
        after = "Para A.\n\n### Heading\n\nPara B changed."
        diff = seg.sentence_level_diff(before, after)
        self.assertEqual(diff["classification"], "CONTENT_CHANGED_NEEDS_REVIEW")

    def test_real_articles_produce_move_only_classification_both_levels(self):
        for level, path in seg.LEVEL_ARTICLE_PATHS.items():
            before_text = seg.load_text(path).strip()
            before_blocks = seg.split_blocks(before_text)
            expected = seg.BEFORE_BOUNDARY_JUDGMENT[level][1]["preceding_paragraph"]
            after_blocks, _ = seg.move_paragraph_after_heading(before_blocks, seg.TARGET_HEADING, expected)
            after_text = "\n\n".join(after_blocks)
            diff = seg.sentence_level_diff(before_text, after_text)
            self.assertEqual(diff["classification"], "MOVE_ONLY_NO_ADD_NO_REMOVE", msg=level)
            self.assertEqual(seg.word_count(before_text), seg.word_count(after_text), msg=level)


class ReassessBoundariesAfterTests(unittest.TestCase):
    def test_moved_paragraph_now_directly_after_heading_for_both_levels(self):
        for level, path in seg.LEVEL_ARTICLE_PATHS.items():
            before_text = seg.load_text(path).strip()
            before_blocks = seg.split_blocks(before_text)
            expected = seg.BEFORE_BOUNDARY_JUDGMENT[level][1]["preceding_paragraph"]
            after_blocks, _ = seg.move_paragraph_after_heading(before_blocks, seg.TARGET_HEADING, expected)
            boundary = seg.reassess_boundaries_after(after_blocks)
            self.assertTrue(boundary["moved_paragraph_now_directly_after_heading"], msg=level)
            self.assertTrue(boundary["先取りは消えたか"], msg=level)


if __name__ == "__main__":
    unittest.main()
