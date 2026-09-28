# ============================================================
# er037_family_xy_concreteness_control_trial_01_test_01.py
# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01: 単体test(API呼び出しなし、¥0)
# ============================================================
from __future__ import annotations

import hashlib
import unittest

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er019_family_x_ja_writer_o_r1_r2_01 as jaw

import er037_family_xy_concreteness_control_trial_01 as trial


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class TestDeterministicMetrics(unittest.TestCase):
    def test_numeric_token_count_basic(self):
        text = "被害額は約1200万円で、事故は9月13日午前11時4分に発生した。"
        result = trial.count_numeric_tokens(text)
        self.assertGreaterEqual(result["numeric_token_count"], 3)
        self.assertGreaterEqual(result["over_precision_count"], 1)

    def test_over_precision_time_and_percent(self):
        text = "The meeting was at 11:04 and the rate rose 12.5%."
        result = trial.count_numeric_tokens(text)
        self.assertGreaterEqual(result["over_precision_count"], 2)

    def test_entities_ja_katakana_and_roman(self):
        text = "Metaは新しいAIサービスMuseを発表した。担当者はコンシェルジュと呼んだ。"
        entities = trial.extract_entities_ja(text)
        self.assertIn("Meta", entities)
        self.assertIn("Muse", entities)
        self.assertTrue(any("コンシェルジュ" in e or "コンシェルジュ" == e for e in entities))

    def test_entities_en_excludes_sentence_initial_and_stopwords(self):
        text = "The company said Hilton reported strong results. In fact, IBM agreed too."
        entities = trial.extract_entities_en(text)
        self.assertIn("Hilton", entities)
        self.assertIn("IBM", entities)
        self.assertNotIn("The", entities)
        self.assertNotIn("In", entities)

    def test_diff_new_tokens_only_returns_ledger_present_tokens(self):
        prev = {"Meta"}
        cur = {"Meta", "Muse", "InventedCo"}
        ledger = "[VERIFIED] fact_id:F1 Meta launched Muse in a small pilot."
        new_tokens = trial.diff_new_tokens(prev, cur, ledger)
        self.assertIn("Muse", new_tokens)
        self.assertNotIn("InventedCo", new_tokens)
        self.assertNotIn("Meta", new_tokens)

    def test_word_count_mixed_ja_en(self):
        text = "This is a test text テスト用の日本語文章です"
        wc = trial.word_count(text)
        self.assertGreater(wc, 0)


class TestPatternText(unittest.TestCase):
    def test_a0_is_empty_addition(self):
        self.assertEqual(trial.pattern_text("A0"), "")

    def test_a_patterns_are_nonempty_and_short(self):
        for pid in ["A1", "A2", "A3", "A4", "A5"]:
            text = trial.pattern_text(pid)
            self.assertTrue(text)
            self.assertLess(len(text), 120, f"{pid} should be a short single-sentence addition")

    def test_n_patterns_defined(self):
        for pid in ["N1", "N2"]:
            self.assertTrue(trial.pattern_text(pid))

    def test_unknown_pattern_raises(self):
        with self.assertRaises(ValueError):
            trial.pattern_text("Z9")


class TestProductionPromptsUnchanged(unittest.TestCase):
    """正式Promptファイル(er019_family_x_ja_writer_o_r1_r2_01 /
    er003_v1_n3_01_advanced_adaptation_generate)の定数が、本Trial
    モジュールをimportし各種関数を呼び出した後も一切変化していないことを
    sha256で確認する(Production無変更の直接的な証拠)。"""

    def setUp(self):
        self.r0_prompt_sha_before = _sha(jaw.R0_PROMPT)
        self.dev_message_sha_before = _sha(jaw.DEVELOPER_MESSAGE)
        self.r1_instruction_sha_before = _sha(jaw.REVISION_INSTRUCTIONS["r1"])
        self.r2_instruction_sha_before = _sha(jaw.REVISION_INSTRUCTIONS["r2"])
        self.advanced_vocab_sha_before = adv_gen.ADVANCED_VOCAB_RULE_V2_SHA256

    def test_prompts_unchanged_after_building_pattern_prompt(self):
        # Trial側でOriginal Promptを組み立てる操作(実API呼び出しはしない)。
        base_prompt = jaw.build_original_prompt("テストStoryline", "[VERIFIED] fact_id:F1 test fact")
        for pid in ["A0", "A1", "A2", "A3", "A4", "A5", "N1", "N2"]:
            extra = trial.pattern_text(pid)
            _ = base_prompt if not extra else base_prompt + "\n\n" + extra

        self.assertEqual(_sha(jaw.R0_PROMPT), self.r0_prompt_sha_before)
        self.assertEqual(_sha(jaw.DEVELOPER_MESSAGE), self.dev_message_sha_before)
        self.assertEqual(_sha(jaw.REVISION_INSTRUCTIONS["r1"]), self.r1_instruction_sha_before)
        self.assertEqual(_sha(jaw.REVISION_INSTRUCTIONS["r2"]), self.r2_instruction_sha_before)
        self.assertEqual(adv_gen.ADVANCED_VOCAB_RULE_V2_SHA256, self.advanced_vocab_sha_before)

    def test_advanced_build_prompt_unchanged_shape(self):
        # build_prompt()自体を無変更のまま呼び出せること(Trial側で.replace()等の
        # 改変を行っていないことの間接確認)。
        prompt = adv_gen.build_prompt("テスト記事本文です。")
        self.assertIn("[Japanese article]", prompt)
        self.assertIn(adv_gen.ADVANCED_VOCAB_RULE_V2_BLOCK, prompt)


if __name__ == "__main__":
    unittest.main()
