"""FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(Phase B、委任_02。
修正=ユーザー決定によるR1/R2 reminder削除の反映、委任_04)

Family X JA Writer正式経路(er019_family_x_ja_writer_o_r1_r2_01.py)へ配線した
AN3(A3+N2)Concreteness Controlブロックの静的整合性テスト。AN3はOriginal側
のみ(Trial-02=er037/er039と同一条件)。R1/R2のreminderはTrial-02で検証
されていない未Trial追加仕様だったため、ユーザー正式決定(2026-09-28)により
削除し、R1/R2はPhase B以前(commit b814f241)の逐語(既存Revision指示のみ)
に戻っていることを確認する。実APIは一切呼ばない(build_original_prompt()は
プロンプト文字列を組み立てるだけで、API呼び出しは行わない純粋関数)。
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

    def test_old_fact_check_args_removed_c2(self):
        """C2(2026-10-10): 旧Fact Checker起点のmust_fix/full_ledger_text引数とmust-fixブロックは物理削除済み。
        AN3ブロックを含む通常promptは不変(E5 golden比較はer053_family_x_factlock_ja_writer_01_testで担保)。"""
        with self.assertRaises(TypeError):
            jaw.build_original_prompt("S", "B", must_fix=[{"fact_id": "F"}], full_ledger_text="L")
        self.assertFalse(hasattr(jaw, "build_must_fix_block"))
        prompt = jaw.build_original_prompt("Storyline one line.", "Brief text here.")
        self.assertIn(_normalize(jaw.CONCRETENESS_CONTROL_AN3_BLOCK), _normalize(prompt))
        self.assertNotIn("Fact Check MAJOR", prompt)

    def test_block_appears_after_symbol_prevention_block(self):
        prompt = jaw.build_original_prompt("Storyline one line.", "Brief text here.")
        symbol_idx = prompt.find(jaw.SYMBOL_PREVENTION_BLOCK_JA.strip())
        an3_idx = prompt.find(jaw.CONCRETENESS_CONTROL_AN3_BLOCK.strip())
        self.assertGreater(symbol_idx, -1)
        self.assertGreater(an3_idx, -1)
        self.assertLess(symbol_idx, an3_idx)


class R1R2NoReminderThreeLocationsTests(unittest.TestCase):
    """FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(修正、委任_04):
    ユーザー正式決定(2026-09-28)により、R1/R2のreminderはTrial-02で検証
    されていない未Trial追加仕様だったため削除した。R1/R2は関数化されて
    おらず3箇所に個別実装されている(設計書§1a)ため、ソースを読み、
    3箇所すべてがPhase B以前(commit b814f241)の逐語に戻っている
    (=reminderが含まれない)ことをassertする。"""

    @classmethod
    def setUpClass(cls):
        cls.source = inspect.getsource(jaw)

    def test_reminder_constant_not_defined(self):
        self.assertFalse(hasattr(jaw, "CONCRETENESS_CONTROL_AN3_REMINDER_JA"))
        self.assertNotIn("CONCRETENESS_CONTROL_AN3_REMINDER_JA", self.source)

    def test_reminder_phrase_absent_from_source(self):
        self.assertNotIn("再び増やさない", self.source)

    def test_normal_r1_r2_loop_matches_phase_b_before(self):
        m = re.search(
            r'for stage_key in \("r1", "r2"\):\s*instruction = ([^\n]+)\n',
            self.source,
        )
        self.assertIsNotNone(m, "通常r1/r2ループのinstruction組み立てが見つかりません")
        self.assertEqual(
            m.group(1).strip(),
            'REVISION_INSTRUCTIONS[stage_key] + SYMBOL_PREVENTION_BLOCK_JA',
        )

    def test_r2_must_fix_instruction_removed_c2(self):
        """C2: R2のFact Check must-fix instruction組み立て(旧Fact Checker起点)は物理削除済み。"""
        self.assertNotIn("r2_must_fix_instruction", self.source)
        self.assertNotIn("build_must_fix_block", self.source)

    def test_r2_symbol_instruction_matches_phase_b_before(self):
        m = re.search(
            r'r2_symbol_instruction = \((.*?)\)\n        r1_response_id_for_symbol',
            self.source, re.DOTALL,
        )
        self.assertIsNotNone(m, "r2_symbol_instructionの組み立てが見つかりません")
        self.assertEqual(
            _normalize(m.group(1)),
            _normalize(
                'REVISION_INSTRUCTIONS["r2"] + SYMBOL_PREVENTION_BLOCK_JA + "\\n\\n"\n'
                '            + safety.build_symbol_violation_prompt_note(r2_symbol_findings)'
            ),
        )
        self.assertNotIn("CONCRETENESS_CONTROL_AN3_REMINDER_JA", m.group(1))


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


class VerbatimShasAN3KeyTests(unittest.TestCase):
    def test_verbatim_shas_has_block_key_with_correct_value(self):
        shas = jaw.verbatim_shas()
        self.assertIn("concreteness_an3_block_sha256", shas)
        self.assertEqual(
            shas["concreteness_an3_block_sha256"],
            hashlib.sha256(jaw.CONCRETENESS_CONTROL_AN3_BLOCK.encode("utf-8")).hexdigest(),
        )

    def test_verbatim_shas_has_no_reminder_key(self):
        # FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(修正、委任_04):
        # ユーザー正式決定によりreminder自体を削除したため、
        # verbatim_shas()にconcreteness_an3_reminder_sha256は存在しない。
        shas = jaw.verbatim_shas()
        self.assertNotIn("concreteness_an3_reminder_sha256", shas)

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
