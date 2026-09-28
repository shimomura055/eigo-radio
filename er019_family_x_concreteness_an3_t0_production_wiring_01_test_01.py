"""FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(Phase B、委任_02)

Family X JA Writer正式経路(er019_family_x_ja_writer_o_r1_r2_01.py)へ配線した
AN3(A3+N2)Concreteness Controlブロック/reminderの静的整合性テスト。
実APIは一切呼ばない(build_original_prompt()はプロンプト文字列を組み立てる
だけで、API呼び出しは行わない純粋関数)。
"""

from __future__ import annotations

import hashlib
import inspect
import re
import unittest

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er015_news_iterative_entertainment_trial_01 as trial01
import er015_news_original_baseline_repro_01 as repro01
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er037_family_xy_concreteness_control_trial_01 as trial_an


def _normalize(text: str) -> str:
    """改行・空白の表記ゆれを正規化して比較するためのヘルパー(テスト専用)。"""
    return re.sub(r"\s+", " ", text).strip()


class ConcretenessAN3BlockVerbatimTests(unittest.TestCase):
    def test_block_matches_trial_a3_plus_n2_after_normalization(self):
        expected = trial_an.PATTERNS_A["A3"] + "\n" + trial_an.PATTERNS_N["N2"]
        self.assertEqual(_normalize(jaw.CONCRETENESS_CONTROL_AN3_BLOCK), _normalize(expected))

    def test_block_matches_combo_patterns_an(self):
        self.assertEqual(
            _normalize(jaw.CONCRETENESS_CONTROL_AN3_BLOCK),
            _normalize(trial_an.COMBO_PATTERNS["AN"]),
        )


class BuildOriginalPromptIncludesAN3Tests(unittest.TestCase):
    def test_prompt_includes_block_without_must_fix(self):
        prompt = jaw.build_original_prompt("Storyline one line.", "Brief text here.")
        self.assertIn(_normalize(jaw.CONCRETENESS_CONTROL_AN3_BLOCK), _normalize(prompt))

    def test_prompt_includes_block_with_must_fix(self):
        must_fix = [{
            "fact_id": "FACT-001",
            "claim_in_article": "claim text",
            "issue": "issue text",
            "explanation": "explanation text",
        }]
        prompt = jaw.build_original_prompt(
            "Storyline one line.", "Brief text here.",
            must_fix=must_fix, full_ledger_text="Full ledger text.",
        )
        self.assertIn(_normalize(jaw.CONCRETENESS_CONTROL_AN3_BLOCK), _normalize(prompt))
        # must_fixブロックもそのまま含まれていること(既存挙動の非破壊確認)
        self.assertIn("【必ず解消すべき指摘(Fact Check MAJOR)】", prompt)

    def test_block_appears_after_symbol_prevention_block(self):
        prompt = jaw.build_original_prompt("Storyline one line.", "Brief text here.")
        symbol_idx = prompt.find(jaw.SYMBOL_PREVENTION_BLOCK_JA.strip())
        an3_idx = prompt.find(jaw.CONCRETENESS_CONTROL_AN3_BLOCK.strip())
        self.assertGreater(symbol_idx, -1)
        self.assertGreater(an3_idx, -1)
        self.assertLess(symbol_idx, an3_idx)


class R1R2ReminderThreeLocationsTests(unittest.TestCase):
    """R1/R2は関数化されておらず3箇所に個別実装されている(設計書§1a)ため、
    ソースを読み、3箇所すべてにREMINDERが含まれることをassertする。"""

    @classmethod
    def setUpClass(cls):
        cls.source = inspect.getsource(jaw)

    def test_reminder_constant_defined_once(self):
        count = self.source.count("CONCRETENESS_CONTROL_AN3_REMINDER_JA = (")
        self.assertEqual(count, 1)

    def test_reminder_referenced_in_five_locations_total(self):
        # 定義1 + verbatim_shas()内1 + 通常r1r2ループ1 + r2 must-fix1 + r2 symbol must-fix1 = 5
        count = self.source.count("CONCRETENESS_CONTROL_AN3_REMINDER_JA")
        self.assertEqual(count, 5)

    def test_normal_r1_r2_loop_references_reminder(self):
        m = re.search(
            r'for stage_key in \("r1", "r2"\):\s*instruction = \((.*?)\)',
            self.source, re.DOTALL,
        )
        self.assertIsNotNone(m, "通常r1/r2ループのinstruction組み立てが見つかりません")
        self.assertIn("CONCRETENESS_CONTROL_AN3_REMINDER_JA", m.group(1))
        self.assertIn("SYMBOL_PREVENTION_BLOCK_JA", m.group(1))

    def test_r2_must_fix_instruction_references_reminder(self):
        m = re.search(
            r'r2_must_fix_instruction = \((.*?)\)\n            r1_response_id',
            self.source, re.DOTALL,
        )
        self.assertIsNotNone(m, "r2_must_fix_instructionの組み立てが見つかりません")
        self.assertIn("CONCRETENESS_CONTROL_AN3_REMINDER_JA", m.group(1))
        # 設計書§7で報告された既存の非対称性(SYMBOL_PREVENTION_BLOCK_JAが
        # この箇所には元々含まれない)は本タスクのスコープ外として維持する
        # (OPEN-227として別途記録)。
        self.assertNotIn("SYMBOL_PREVENTION_BLOCK_JA", m.group(1))

    def test_r2_symbol_instruction_references_reminder(self):
        m = re.search(
            r'r2_symbol_instruction = \((.*?)\)\n        r1_response_id_for_symbol',
            self.source, re.DOTALL,
        )
        self.assertIsNotNone(m, "r2_symbol_instructionの組み立てが見つかりません")
        self.assertIn("CONCRETENESS_CONTROL_AN3_REMINDER_JA", m.group(1))
        self.assertIn("SYMBOL_PREVENTION_BLOCK_JA", m.group(1))


class T1NonContaminationTests(unittest.TestCase):
    """T1(Trial限定・Production混入禁止対象、設計書§2-2)の文言が
    Production側(JA Writer/Advanced化)に混入していないことを確認する。"""

    T1_PHRASES = (
        "Trial-only additional instruction",
        "not already in the Japanese article",
    )

    def test_ja_writer_source_has_no_t1_phrases(self):
        source = inspect.getsource(jaw)
        for phrase in self.T1_PHRASES:
            self.assertNotIn(phrase, source)

    def test_advanced_adaptation_source_has_no_t1_phrases(self):
        source = inspect.getsource(adv_gen)
        for phrase in self.T1_PHRASES:
            self.assertNotIn(phrase, source)


class VerbatimShasIncludeAN3KeysTests(unittest.TestCase):
    def test_verbatim_shas_has_two_new_keys_with_correct_values(self):
        shas = jaw.verbatim_shas()
        self.assertIn("concreteness_an3_block_sha256", shas)
        self.assertIn("concreteness_an3_reminder_sha256", shas)
        self.assertEqual(
            shas["concreteness_an3_block_sha256"],
            hashlib.sha256(jaw.CONCRETENESS_CONTROL_AN3_BLOCK.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            shas["concreteness_an3_reminder_sha256"],
            hashlib.sha256(jaw.CONCRETENESS_CONTROL_AN3_REMINDER_JA.encode("utf-8")).hexdigest(),
        )

    def test_verbatim_shas_still_has_original_four_keys(self):
        shas = jaw.verbatim_shas()
        for key in (
            "r0_prompt_sha256", "developer_message_sha256",
            "r1_instruction_sha256", "r2_instruction_sha256",
        ):
            self.assertIn(key, shas)


class ExistingConstantsUnchangedTests(unittest.TestCase):
    """R0_PROMPT/REVISION_INSTRUCTIONSは別定数追記方式のため無変更のまま
    (設計書§4-2)。系譜元Trialとの逐語一致が崩れていないことを再確認する。"""

    def test_r0_prompt_verbatim_matches_repro01(self):
        self.assertEqual(jaw.R0_PROMPT, repro01.R0_PROMPT)

    def test_revision_instructions_verbatim_match_trial01(self):
        self.assertEqual(jaw.REVISION_INSTRUCTIONS["r1"], trial01.REVISION_INSTRUCTIONS["r1"])
        self.assertEqual(jaw.REVISION_INSTRUCTIONS["r2"], trial01.REVISION_INSTRUCTIONS["r2"])


class AdvancedVocabRuleUnchangedTests(unittest.TestCase):
    """Advanced化Promptは本タスクで一切変更しない(設計書§3-4)。既存の
    固定sha256(ADVANCED_VOCAB_RULE_V2_SHA256)との一致を再確認することで、
    本タスク開始時点からの無変更を保証する。"""

    def test_advanced_vocab_rule_v2_block_sha256_unchanged(self):
        actual = hashlib.sha256(
            adv_gen.ADVANCED_VOCAB_RULE_V2_BLOCK.encode("utf-8")
        ).hexdigest()
        self.assertEqual(actual, adv_gen.ADVANCED_VOCAB_RULE_V2_SHA256)


if __name__ == "__main__":
    unittest.main()
