# ============================================================
# er010_no9_function_word_reduction_production_wiring_27_test.py
# ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1
# ============================================================
# Trial 26で検証・ユーザー承認済みのfunction-word/article reduction原則
# が、Key Phrase英語TTSのProduction一般仕様(KEY_PHRASE_MINIMAL_
# INSTRUCTION_PREFIX)へ正しく配線され、Primary(Minimal)・Fallback
# (English Lock)の両方へ適用され、既存の安全策・retry回数配分・
# reentrancy guardのいずれも壊していないことを確認する回帰テスト。

from __future__ import annotations

import unittest

import er003_v1_repro01_main_generate as repro01


class FunctionWordReductionWiringTests(unittest.TestCase):
    def test_suffix_applied_to_minimal_instruction(self):
        self.assertIn(repro01.FUNCTION_WORD_REDUCTION_SUFFIX, repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)

    def test_suffix_applied_to_english_lock_instruction_too(self):
        # English LockはMinimal instructionを起点に構築されるため、
        # function-word reductionはFallbackへも自動的に適用される。
        self.assertIn(repro01.FUNCTION_WORD_REDUCTION_SUFFIX, repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)

    def test_core_safeguards_not_removed(self):
        core = repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT
        for phrase in (
            "naturally and clearly", "exactly once", "do not add explanations",
            "do not add, omit, or change any words",
            "not as separate words read one at a time",
            "not trailed off into silence",
            "do not over-emphasize or exaggerate any single sound",
        ):
            self.assertIn(phrase, core)

    def test_suffix_is_general_principle_not_a_catch_hardcode(self):
        suffix = repro01.FUNCTION_WORD_REDUCTION_SUFFIX
        self.assertNotIn("a catch", suffix)
        self.assertIn("articles", suffix)
        self.assertIn('"a", "an", "the"', suffix)

    def test_suffix_explicitly_forbids_omitting_the_function_word(self):
        self.assertIn("Do not omit or drop the function word", repro01.FUNCTION_WORD_REDUCTION_SUFFIX)

    def test_minimal_instruction_prefix_equals_core_plus_suffix(self):
        self.assertEqual(
            repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX,
            repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT + repro01.FUNCTION_WORD_REDUCTION_SUFFIX)

    def test_english_lock_instruction_still_additive_not_replacement(self):
        self.assertTrue(
            repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION.startswith(repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX))
        self.assertIn("English word or phrase", repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)

    def test_retry_budget_unchanged_by_wiring(self):
        self.assertEqual(repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS, 2)
        self.assertEqual(repro01.KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS, 2)
        self.assertEqual(repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS, 4)

    def test_primary_then_fallback_both_use_function_word_reduction(self):
        """Minimal 2回ともNG→English Lockへfallbackする既存の分岐で、
        実際にstyle_prefix_overrideとして渡されるテキストの両方に
        function-word reduction suffixが含まれることを確認する
        (実TTS課金なし、既存テスト群と同じモックパターン)。"""
        calls = []
        orig = repro01.generate_narration_snippet_verified_strict

        def fake(text, language, out_path, expected_substring, **kwargs):
            calls.append(kwargs.get("style_prefix_override"))
            if kwargs.get("style_prefix_override") == repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX:
                return {"status": "STOPPED", "reason": "強制失敗(mock)",
                        "attempts_log": [{"attempt": 1, "asr_text": "x"}, {"attempt": 2, "asr_text": "x"}]}
            return {"status": "OK", "attempts_log": [{"attempt": 1, "asr_text": "an idea"}]}

        repro01.generate_narration_snippet_verified_strict = fake
        try:
            result = repro01.generate_key_phrase_component_verified("an idea", "dummy_out.wav")
        finally:
            repro01.generate_narration_snippet_verified_strict = orig

        self.assertEqual(result["status"], "OK")
        self.assertEqual(len(calls), 2)
        for style_prefix in calls:
            self.assertIn(repro01.FUNCTION_WORD_REDUCTION_SUFFIX, style_prefix)


if __name__ == "__main__":
    unittest.main()
