# ============================================================
# er012_b_family_voices_variable_voice_count_test_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-
# WIRING-01(OPEN-151)
# ============================================================
# Gate 3向け単体テスト(API呼び出し無し、¥0)。「Production Writerを2/3
# Voices可変へ一般化する」(2026-09-14ユーザー正式決定、APPROVED_FOR_
# PRODUCTION)の配線契約を検証する。
#   1. make_theme_config()の2/3受付・1/4拒否・2V時external_constraint拒否。
#   2. 2V Focus Module block生成(build_focus_module_block_2v)の内容契約
#      (両Voice Cardの内容が現れる、5区切り形式、3V専用の一人称指示・
#      「3人」文言を含まない)。
#   3. 2V Leakage Check(schema/prompt)がleak_binary_camp_split・
#      leak_tension_constraint_integrationを含まないこと。
#   4. 2V Overlap monitoring(4値)の契約。
#   5. split_five_voice_sections()がProduction正式関数(b1prod)への
#      委譲であること。
#   6. registry.build_required_structure()が2V(voice_c省略)・3V(voice_c
#      指定)いずれも無変更のまま動作すること(既存registryの可変voice数
#      シグネチャが本タスク以前から存在することの回帰確認、新規実装では
#      ない)。
#   7. runner: main_b1_2v()のwrite_new_theme呼び出し契約、main()の
#      level="b1_2v"分岐契約(既存main_b1_3v/main_a2分岐は無変更)。
#   8. 3V regression evidence(バイト不変性): git HEAD時点のコード
#      (writer_generic_before.py、er014_output/four_type_observation_01/
#      voices/へ`git show HEAD:...`で保存済み)のpure関数出力と、改修後
#      コードの出力が同一入力に対してbyte単位で一致すること。
from __future__ import annotations

import importlib.util
import types
import unittest
from unittest import mock

import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_production_01 as b1prod
import er012_b_family_voices_theme_ai_screening_01 as theme_ai_screening
import er012_b_family_voices_writer_generic_01 as wg

_BEFORE_PATH = "er014_output/four_type_observation_01/voices/writer_generic_before.py"


def _load_before_module():
    spec = importlib.util.spec_from_file_location("wg_before_snapshot_open151", _BEFORE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================
# 1. make_theme_config(): 2/3受付・1/4拒否・2V時external_constraint拒否
# ============================================================
class MakeThemeConfigVariableVoiceCountTests(unittest.TestCase):
    def test_accepts_two_voice_cards(self):
        cfg = wg.make_theme_config(
            theme_id="t", topic_ja="topic", ledger_path="x.txt",
            voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2],
            tension_common_ground_value="g", tension_asymmetry_value="a")
        self.assertEqual(len(cfg["voice_cards"]), 2)

    def test_accepts_three_voice_cards(self):
        cfg = wg.make_theme_config(
            theme_id="t", topic_ja="topic", ledger_path="x.txt",
            voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2,
                         theme_ai_screening.VOICE_CARD_3],
            tension_common_ground_value="g", tension_asymmetry_value="a")
        self.assertEqual(len(cfg["voice_cards"]), 3)

    def test_rejects_one_voice_card(self):
        with self.assertRaises(ValueError):
            wg.make_theme_config(
                theme_id="t", topic_ja="topic", ledger_path="x.txt",
                voice_cards=[theme_ai_screening.VOICE_CARD_1],
                tension_common_ground_value="g", tension_asymmetry_value="a")

    def test_rejects_four_voice_cards(self):
        with self.assertRaises(ValueError):
            wg.make_theme_config(
                theme_id="t", topic_ja="topic", ledger_path="x.txt",
                voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2,
                             theme_ai_screening.VOICE_CARD_3, theme_ai_screening.VOICE_CARD_1],
                tension_common_ground_value="g", tension_asymmetry_value="a")

    def test_two_voice_cards_reject_external_constraint(self):
        ext = wg.make_external_constraint(evidence_voice_number=3, items_text="dummy")
        with self.assertRaises(ValueError):
            wg.make_theme_config(
                theme_id="t", topic_ja="topic", ledger_path="x.txt",
                voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2],
                tension_common_ground_value="g", tension_asymmetry_value="a",
                external_constraint=ext)

    def test_three_voice_cards_still_accept_external_constraint(self):
        ext = wg.make_external_constraint(evidence_voice_number=4, items_text="dummy")
        cfg = wg.make_theme_config(
            theme_id="t", topic_ja="topic", ledger_path="x.txt",
            voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2,
                         theme_ai_screening.VOICE_CARD_3],
            tension_common_ground_value="g", tension_asymmetry_value="a",
            external_constraint=ext)
        self.assertEqual(cfg["external_constraint"], ext)


# ============================================================
# 2. build_focus_module_block_2v(): 内容契約
# ============================================================
class TwoVoiceFocusModuleBlockTests(unittest.TestCase):
    def setUp(self):
        self.theme_config = wg.make_theme_config(
            theme_id="t2v", topic_ja="topic", ledger_path="x.txt",
            voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2],
            tension_common_ground_value="共通の望み", tension_asymmetry_value="非対称の説明")
        self.block = wg.build_focus_module_block_2v(self.theme_config)

    def test_both_voice_cards_appear(self):
        for card in (theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2):
            self.assertIn(card["person"], self.block)
            self.assertIn(card["stake"], self.block)

    def test_reference_phrases_included(self):
        self.assertIn(theme_ai_screening.VOICE_CARD_1["reference_phrase"], self.block)
        self.assertIn(theme_ai_screening.VOICE_CARD_2["reference_phrase"], self.block)

    def test_five_section_structure_instruction_present(self):
        self.assertIn("5区切り構造", self.block)
        self.assertIn("## The Question", self.block)
        self.assertIn("## [Tensionの見出し", self.block)
        self.assertIn("## [Closingの見出し", self.block)

    def test_does_not_mention_three_person_wording(self):
        # 3V専用の「3人」「一人称"I"」指示が2Vへ混入していないことを確認する。
        self.assertNotIn("3人", self.block)
        self.assertNotIn('一人称"I"', self.block)

    def test_experiential_claim_grounding_block_present(self):
        # 恒久Writer原則(Voice数非依存)は2Vでも常時含まれる。
        self.assertIn(wg.COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK, self.block)

    def test_anchor_insertion_works_for_2v_block(self):
        candidate = wg.build_candidate_template(self.block)
        self.assertEqual(candidate.count(wg.ANCHOR), 1)
        self.assertIn(self.block, candidate)


# ============================================================
# 3. 2V Leakage Check(schema/prompt)
# ============================================================
class TwoVoiceLeakageCheckTests(unittest.TestCase):
    def test_schema_excludes_binary_camp_split_and_constraint_integration(self):
        schema, fields = wg.build_leakage_schema_2v()
        self.assertNotIn("leak_binary_camp_split", fields["tension"])
        self.assertNotIn(wg.TENSION_LEAKAGE_FIELD_CONSTRAINT_INTEGRATION, fields["tension"])
        self.assertIn("voice_a", fields)
        self.assertIn("voice_b", fields)
        self.assertNotIn("voice_1", fields)

    def test_schema_voice_fields_match_generic_voice_leakage_fields(self):
        _, fields = wg.build_leakage_schema_2v()
        self.assertEqual(fields["voice_a"], wg.VOICE_LEAKAGE_FIELDS)
        self.assertEqual(fields["voice_b"], wg.VOICE_LEAKAGE_FIELDS)

    def test_prompt_mentions_voice_a_and_voice_b_bodies(self):
        sections = {"voice_a_body": "AAA text", "voice_b_body": "BBB text",
                    "tension_body": "TTT text", "closing_body": "CCC text"}
        prompt = wg.build_leakage_check_prompt_2v(sections)
        self.assertIn("AAA text", prompt)
        self.assertIn("BBB text", prompt)
        self.assertNotIn("leak_binary_camp_split", prompt)
        self.assertNotIn("leak_tension_constraint_integration", prompt)


# ============================================================
# 4. 2V Overlap monitoring(4値)
# ============================================================
class TwoVoiceOverlapMonitoringTests(unittest.TestCase):
    def test_returns_four_values_and_matches_naming(self):
        sections = {
            "hook_body": "Hook sentence about the topic.",
            "voice_a_body": "Voice A talks about their own morning routine and needs.",
            "voice_b_body": "Voice B talks about a completely different concern and worry.",
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            summary = wg.run_overlap_monitoring_2v(sections, tmp)
        self.assertEqual(summary["directed_voice_pair_count"], 2)
        self.assertEqual(summary["voice_vs_hook_count"], 2)
        self.assertIn("voice_a_vs_voice_b", summary["directed_voice_pairs"])
        self.assertIn("voice_b_vs_voice_a", summary["directed_voice_pairs"])
        self.assertIn("voice_a_vs_hook", summary["voice_vs_hook"])
        self.assertIn("voice_b_vs_hook", summary["voice_vs_hook"])


# ============================================================
# 5. split_five_voice_sections(): Production正式関数への委譲
# ============================================================
class SplitFiveVoiceSectionsDelegationTests(unittest.TestCase):
    ARTICLE = """# Title

## The Question

Hook body.

### One Voice: A

Voice a body.

### Another Voice: B

Voice b body.

## Why They See It Differently

Tension body.

## What This Tells Us

Closing body.
"""

    def test_delegates_to_b1prod_split_five_voice_sections(self):
        expected = b1prod.split_five_voice_sections(self.ARTICLE)
        actual = wg.split_five_voice_sections(self.ARTICLE)
        self.assertEqual(expected, actual)

    def test_downstream_functions_use_matching_keys_no_api(self):
        sections = wg.split_five_voice_sections(self.ARTICLE)
        self.assertIsNotNone(sections)
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            overlap = wg.run_overlap_monitoring_2v(sections, tmp)
        self.assertIn("directed_voice_pairs", overlap)
        prompt = wg.build_leakage_check_prompt_2v(sections)
        self.assertIn("Voice a body.", prompt)
        self.assertIn("Voice b body.", prompt)


# ============================================================
# 6. registry.build_required_structure(): 可変voice数(既存機能の回帰確認)
# ============================================================
class RegistryGateDictVariableVoiceCountRegressionTests(unittest.TestCase):
    """本タスクではregistry.pyを一切変更していない(git diff --statで
    確認済み)。build_required_structure()が2V(voice_c省略)・3V
    (voice_c指定)いずれも既に動作することを、変更なしのまま再確認する
    (Gate 3項目3「registry可変voice数」は既存実装で既に充足済み)。"""

    def test_level_b1_works_without_voice_c(self):
        structure = registry.build_required_structure(level="b1", voice_a="Algieba", voice_b="Erinome")
        self.assertIsInstance(structure, dict)
        self.assertGreater(len(structure), 0)

    def test_level_b1_3v_requires_voice_c(self):
        structure = registry.build_required_structure(
            level="b1_3v", voice_a="Algieba", voice_b="Erinome", voice_c="Schedar")
        self.assertIsInstance(structure, dict)
        with self.assertRaises(ValueError):
            registry.build_required_structure(level="b1_3v", voice_a="Algieba", voice_b="Erinome")


# ============================================================
# 7. runner: main_b1_2v() + level="b1_2v"分岐
# ============================================================
class MainB12VWriteNewThemeContractTests(unittest.TestCase):
    def test_write_new_theme_calls_run_writer_stage_generic_with_theme_config(self):
        fake_theme_mod = types.SimpleNamespace(THEME_CONFIG={"voice_cards": [1, 2]})
        with mock.patch.object(runner.sys, "argv",
                                ["prog", "write_new_theme", "b1_2v", "fake_theme_module_x", "out/dir"]), \
             mock.patch("importlib.import_module", return_value=fake_theme_mod) as import_mock, \
             mock.patch.object(runner.writer_generic, "run_writer_stage_generic",
                                return_value={"status": "DONE"}) as run_mock:
            runner.main_b1_2v()
        import_mock.assert_called_once_with("fake_theme_module_x")
        run_mock.assert_called_once_with(fake_theme_mod.THEME_CONFIG, "out/dir")

    def test_non_write_new_theme_stage_raises_system_exit(self):
        with mock.patch.object(runner.sys, "argv", ["prog", "tts", "b1_2v"]):
            with self.assertRaises(SystemExit):
                runner.main_b1_2v()

    def test_missing_theme_module_raises_system_exit(self):
        with mock.patch.object(runner.sys, "argv", ["prog", "write_new_theme", "b1_2v"]):
            with self.assertRaises(SystemExit):
                runner.main_b1_2v()


class RunnerLevelB12VDispatchTests(unittest.TestCase):
    """既存main_b1_3v/main_a2/既定("b1")分岐には一切影響しないことを確認する。"""

    def test_level_b1_2v_dispatches_to_main_b1_2v(self):
        with mock.patch.object(runner, "main_b1_2v") as main_b1_2v_mock, \
             mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "write_new_theme", "b1_2v"]):
            runner.main()
        main_b1_2v_mock.assert_called_once()
        main_b1_3v_mock.assert_not_called()
        main_a2_mock.assert_not_called()

    def test_level_b1_3v_does_not_dispatch_to_main_b1_2v(self):
        with mock.patch.object(runner, "main_b1_2v") as main_b1_2v_mock, \
             mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "b1_3v"]):
            runner.main()
        main_b1_3v_mock.assert_called_once()
        main_b1_2v_mock.assert_not_called()

    def test_level_a2_does_not_dispatch_to_main_b1_2v(self):
        with mock.patch.object(runner, "main_b1_2v") as main_b1_2v_mock, \
             mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "a2"]):
            runner.main()
        main_a2_mock.assert_called_once()
        main_b1_2v_mock.assert_not_called()


# ============================================================
# 8. 3V regression evidence: git HEAD版とのbyte不変性
# ============================================================
class ThreeVoiceByteInvarianceAgainstHeadTests(unittest.TestCase):
    """改修前(git HEAD、writer_generic_before.py)コードのpure関数出力と、
    改修後コード(本ファイルがimportするer012_b_family_voices_writer_
    generic_01)の出力が、同一入力に対してbyte単位で一致することを確認
    する(3V regression evidence、API呼び出し無し、¥0)。"""

    @classmethod
    def setUpClass(cls):
        cls.wg_before = _load_before_module()

    def test_build_focus_module_block_3v_byte_identical(self):
        before = self.wg_before.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        after = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        self.assertEqual(before, after)

    def test_build_candidate_template_byte_identical(self):
        block_before = self.wg_before.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        block_after = wg.build_focus_module_block_3v(theme_ai_screening.THEME_CONFIG)
        cand_before = self.wg_before.build_candidate_template(block_before)
        cand_after = wg.build_candidate_template(block_after)
        self.assertEqual(cand_before, cand_after)

    def test_leakage_schema_3v_identical(self):
        sb_on, fb_on = self.wg_before.build_leakage_schema_3v(True)
        sa_on, fa_on = wg.build_leakage_schema_3v(True)
        self.assertEqual(sb_on, sa_on)
        self.assertEqual(fb_on, fa_on)
        sb_off, fb_off = self.wg_before.build_leakage_schema_3v(False)
        sa_off, fa_off = wg.build_leakage_schema_3v(False)
        self.assertEqual(sb_off, sa_off)

    def test_leakage_check_prompt_3v_identical(self):
        sections = {
            "voice_1_body": "v1 body text.", "voice_2_body": "v2 body text.",
            "voice_3_body": "v3 body text.", "tension_body": "t body.", "closing_body": "c body.",
        }
        before = self.wg_before.build_leakage_check_prompt_3v(sections, True)
        after = wg.build_leakage_check_prompt_3v(sections, True)
        self.assertEqual(before, after)

    def test_ledger_fragment_visible_voices_only_identical(self):
        ledger_text = (
            "[VOICE_1_EVIDENCE] 1-01(fact_a): line.\n\n"
            "[VOICE_4_EVIDENCE] 4-01(fact_c): line.\n\n"
            "[VOICE_3_EVIDENCE] 3-01(fact_d): line.\n"
        )
        before = self.wg_before.build_ledger_fragment_visible_voices_only(ledger_text, num_visible_voices=3)
        after = wg.build_ledger_fragment_visible_voices_only(ledger_text, num_visible_voices=3)
        self.assertEqual(before, after)

    def test_make_theme_config_dict_identical_for_three_cards(self):
        before_cfg = self.wg_before.make_theme_config(
            theme_id="t", topic_ja="topic", ledger_path="x.txt",
            voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2,
                         theme_ai_screening.VOICE_CARD_3],
            tension_common_ground_value="g", tension_asymmetry_value="a")
        after_cfg = wg.make_theme_config(
            theme_id="t", topic_ja="topic", ledger_path="x.txt",
            voice_cards=[theme_ai_screening.VOICE_CARD_1, theme_ai_screening.VOICE_CARD_2,
                         theme_ai_screening.VOICE_CARD_3],
            tension_common_ground_value="g", tension_asymmetry_value="a")
        self.assertEqual(before_cfg, after_cfg)

    def test_source_of_untouched_3v_functions_unchanged(self):
        """3V専用関数のsourceがimportlib経由でも文字列として完全一致する
        ことを確認する(git diffでの無変更確認の二重チェック)。retry/
        fallback機構(run_ledger_deviation_and_local_rewrite、Voice数に
        依存しない共通関数)もここに含め、2V/3V双方で同一実装が再利用
        されていることを保証する。"""
        import inspect
        names = [
            "build_focus_module_block_3v", "run_fact_check_a_prime_3v",
            "run_overlap_monitoring_3v", "build_leakage_schema_3v",
            "build_leakage_check_prompt_3v", "run_analytical_leakage_check_3v",
            "build_leakage_corrective_note_3v", "run_voices_pattern_3v",
            "run_pipeline_3v", "run_ledger_deviation_and_local_rewrite",
            "_generate_and_compress_article_3v", "_apply_b_family_voice_safety_gate",
            "split_six_voice_sections", "build_ledger_fragment_visible_voices_only",
            "run_phase_a", "build_candidate_prompt",
        ]
        for name in names:
            before_src = inspect.getsource(getattr(self.wg_before, name))
            after_src = inspect.getsource(getattr(wg, name))
            self.assertEqual(before_src, after_src, f"{name}のsourceが変更されています")


if __name__ == "__main__":
    unittest.main()
