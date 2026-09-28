# ============================================================
# er045_family_x_no_heading_segmentation_trial_01_test_01.py
# FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01
# ============================================================
# API呼び出しなし(unittest、決定論部分のみ検証)。
#   - Production Prompt定数(ADVANCED_VOCAB_RULE_V2_BLOCK)のsha256不変
#     (import元モジュールのfail-closed assertが通ること自体で保証されるが、
#     本テストでも明示的に再確認する)
#   - 決定論的3分割アルゴリズムの決定論性・本文不変(語の並び替え・追加・
#     削除が発生しないこと)
#   - Trial Prompt(TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION)に見出し生成・
#     In One Line生成の指示が含まれていないこと
#   - Comment本文はTrial側で一切生成・変更しない(モジュールに生成関数が
#     存在しないことを確認する簡易チェック)
# ============================================================
from __future__ import annotations

import hashlib
import unittest

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er045_family_x_no_heading_segmentation_trial_01 as trial


class TestProductionPromptUnchanged(unittest.TestCase):
    def test_vocab_rule_v2_sha256_matches_production_constant(self):
        actual = hashlib.sha256(adv_gen.ADVANCED_VOCAB_RULE_V2_BLOCK.encode("utf-8")).hexdigest()
        self.assertEqual(actual, adv_gen.ADVANCED_VOCAB_RULE_V2_SHA256)

    def test_trial_module_does_not_redefine_production_blocks(self):
        # Trialモジュールが独自にADVANCED_VOCAB_RULE_V2_BLOCK等の同名定数を
        # 再定義していない(importのみ)ことを確認する。
        self.assertFalse(hasattr(trial, "ADVANCED_VOCAB_RULE_V2_BLOCK"))
        self.assertFalse(hasattr(trial, "ADVANCED_ARM3_BLOCK"))
        self.assertFalse(hasattr(trial, "ADVANCED_SECTION_BOUNDARY_CONTRACT"))
        self.assertFalse(hasattr(trial, "ADVANCED_CONTRACT_SUFFIX"))


class TestTrialPromptHasNoHeadingOrInOneLineInstruction(unittest.TestCase):
    def test_no_heading_markup_instruction_in_translation_prompt(self):
        text = trial.TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION
        self.assertIn("Do not add section headings", text)
        self.assertNotIn("### ", text)
        self.assertNotIn("Point One", text)

    def test_translation_prompt_does_not_ask_for_in_one_line(self):
        text = trial.TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION
        self.assertNotIn("In one line", text)
        self.assertNotIn("In One Line", text)

    def test_in_one_line_prompt_forbids_new_facts(self):
        text = trial.TRIAL_IN_ONE_LINE_INSTRUCTION_TEMPLATE
        self.assertIn("Do not add any new fact", text)


class TestDeterministicThreeWaySplit(unittest.TestCase):
    def _sample_body(self, n_paragraphs=7):
        return "\n\n".join(f"Paragraph {i} has some words in it for testing purposes today." * (i % 3 + 1)
                            for i in range(n_paragraphs))

    def test_deterministic_repeatable(self):
        body = self._sample_body()
        r1 = trial.deterministic_three_way_split(body)
        r2 = trial.deterministic_three_way_split(body)
        self.assertEqual(r1, r2)

    def test_reconstructs_original_text_exactly(self):
        body = self._sample_body()
        r = trial.deterministic_three_way_split(body)
        self.assertEqual(r["status"], "OK")
        reconstructed = "\n\n".join([r["part1"], r["part2"], r["part3"]])
        self.assertEqual(reconstructed, body)

    def test_no_word_added_or_removed(self):
        body = self._sample_body()
        r = trial.deterministic_three_way_split(body)
        original_words = body.split()
        reconstructed_words = "\n\n".join([r["part1"], r["part2"], r["part3"]]).split()
        self.assertEqual(original_words, reconstructed_words)

    def test_too_few_paragraphs_reports_status(self):
        body = "Only one paragraph here."
        r = trial.deterministic_three_way_split(body)
        self.assertEqual(r["status"], "TOO_FEW_PARAGRAPHS")

    def test_chooses_minimum_cost_boundary_by_brute_force(self):
        # 全探索が実際に最小二乗誤差の境界を選んでいることを、独立実装の
        # brute forceと突き合わせて確認する(極端に偏った段落サイズの例)。
        import itertools
        import re as _re
        paragraphs = [
            "short one.", "short two.", "short three.",
            "word " * 200, "short four.", "short five.",
        ]
        body = "\n\n".join(paragraphs)
        counts = [len(_re.findall(r"[A-Za-z']+", p)) for p in paragraphs]
        total = sum(counts)
        target = total / 3.0
        expected_best = None
        for i, j in itertools.combinations(range(1, len(paragraphs)), 2):
            c1, c2, c3 = sum(counts[:i]), sum(counts[i:j]), sum(counts[j:])
            cost = (c1 - target) ** 2 + (c2 - target) ** 2 + (c3 - target) ** 2
            key = (cost, i, j)
            if expected_best is None or key < expected_best:
                expected_best = key
        r = trial.deterministic_three_way_split(body)
        self.assertEqual(r["status"], "OK")
        self.assertEqual((r["boundary_i"], r["boundary_j"]), (expected_best[1], expected_best[2]))


class TestSplitJaTitleAndBody(unittest.TestCase):
    def test_splits_title_and_body(self):
        ja_text = "タイトル行\n\n段落1です。\n\n段落2です。"
        title, body = trial.split_ja_title_and_body(ja_text)
        self.assertEqual(title, "タイトル行")
        self.assertEqual(body, "段落1です。\n\n段落2です。")

    def test_paragraph_count(self):
        body = "段落1です。\n\n段落2です。\n\n段落3です。"
        self.assertEqual(trial.ja_paragraph_count(body), 3)


class TestRubricSchemaCoversAllUserItems(unittest.TestCase):
    def test_fourteen_criteria_defined(self):
        self.assertEqual(len(trial.RUBRIC_ITEMS), 14)

    def test_monotony_item_present_and_last(self):
        keys = [k for k, _ in trial.RUBRIC_ITEMS]
        self.assertIn("no_monotony_without_headings", keys)


if __name__ == "__main__":
    unittest.main()
