import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

import er044_tts_variable_spoken_role_style_trial_02 as vr2
import er006_master_audio_store_01 as store
import er003_b1_p9a_audio as p9a


class TestPatternWordingVerbatim(unittest.TestCase):
    def test_j0_is_actual_production_japanese_style_prefix(self):
        # J0は真のProduction現状(p9a.JAPANESE_STYLE_PREFIX)そのものであり、
        # delegationが想定した「落ち着いた、自然な話し言葉で」(Task B新規値)
        # ではないことを固定する(design doc §1-2の発見)。
        self.assertEqual(vr2.J_PATTERN_STYLES["J0"], p9a.JAPANESE_STYLE_PREFIX)
        self.assertNotEqual(vr2.J_PATTERN_STYLES["J0"], "落ち着いた、自然な話し言葉で")

    def test_j1_j2_j3_verbatim(self):
        self.assertEqual(
            vr2.J_PATTERN_STYLES["J1"],
            "落ち着いた、自然な話し言葉で。意味の流れに合わせて軽く抑揚をつけてください。")
        self.assertEqual(
            vr2.J_PATTERN_STYLES["J2"],
            "落ち着いた、自然な話し言葉で。強調点や話の転換に応じて抑揚をつけてください。大げさにしないでください。")
        self.assertEqual(
            vr2.J_PATTERN_STYLES["J3"],
            "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
            "演技がかった話し方は避けてください。")

    def test_e2_matches_production_family_x_role_style(self):
        # TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
        # ユーザー正式決定によりProduction側(fl_styles.FAMILY_X_ROLE_STYLE_EN)
        # はE0からE2へ更新済みのため、比較対象をE0からE2へ更新する(このTrial
        # スクリプト自身のE_PATTERN_STYLES辞書は無変更、逐語比較のみ変更)。
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        self.assertEqual(vr2.E_PATTERN_STYLES["FULL_STORY"]["E2"], fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"])
        self.assertEqual(vr2.E_PATTERN_STYLES["IN_ONE_LINE"]["E2"], fl_styles.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"])
        self.assertEqual(vr2.E_PATTERN_STYLES["TOPIC_INTRO"]["E2"], fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"])

    def test_all_new_styles_have_no_wpm_specification(self):
        import er002_common as common
        for p, s in vr2.J_PATTERN_STYLES.items():
            if p == "J0":
                continue
            common.assert_no_wpm_specification(s)  # raises if violated
        for role, pmap in vr2.E_PATTERN_STYLES.items():
            for p, s in pmap.items():
                common.assert_no_wpm_specification(s)


class TestFixedPhraseSegmentsNotInScope(unittest.TestCase):
    def test_fixed_shell_segment_names_excluded(self):
        fixed_names = {
            "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
            "num_one", "num_two", "num_three", "num_four", "num_five", "point_explanation",
        }
        all_targets = set(vr2.JA_SEGMENTS_REQUIRED) | set(vr2.JA_SEGMENTS_OPTIONAL) | \
            set(vr2.EN_SEGMENTS_REQUIRED) | set(vr2.EN_SEGMENTS_OPTIONAL)
        self.assertEqual(all_targets & fixed_names, set())

    def test_key_phrase_segments_excluded(self):
        all_targets = set(vr2.JA_SEGMENTS_REQUIRED) | set(vr2.JA_SEGMENTS_OPTIONAL) | \
            set(vr2.EN_SEGMENTS_REQUIRED) | set(vr2.EN_SEGMENTS_OPTIONAL)
        for name in all_targets:
            self.assertFalse(name.startswith("kp"))
            self.assertFalse(name.startswith("meaning_"))


class TestStoreIsolationRestored(unittest.TestCase):
    def test_trial_master_audio_store_restores_production_globals(self):
        orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
        with vr2.trial_master_audio_store("er044_output/tts_variable_spoken_role_style_trial_02/master_store"):
            self.assertNotEqual(store.STORE_DIR, orig[0])
            self.assertTrue(store.STORE_DIR.startswith("er044_output/"))
        self.assertEqual(
            (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH), orig)

    def test_no_writes_to_production_store_path_string(self):
        # 静的チェック: このモジュール内でProduction Store固定pathを
        # 直接書き込みで参照している箇所が無いこと(文字列走査)。
        with open(os.path.join(os.path.dirname(__file__),
                                "er044_tts_variable_spoken_role_style_trial_02.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('"er006_output/master_audio_store_01', src)


class TestNoStageAllOrFullRunFunction(unittest.TestCase):
    def test_no_stage_all_argument_or_run_tts_stage_function(self):
        self.assertFalse(hasattr(vr2, "run_tts_stage"))
        self.assertFalse(hasattr(vr2, "run_assemble_stage"))
        parser = vr2.build_arg_parser()
        help_text = parser.format_help()
        self.assertNotIn("--stage", help_text)

    def test_cli_requires_single_segment_and_explicit_patterns(self):
        parser = vr2.build_arg_parser()
        actions = {a.dest for a in parser._actions}
        self.assertIn("segment", actions)
        self.assertIn("patterns", actions)
        self.assertNotIn("stage", actions)


class TestJ0E0ReuseSourcePaths(unittest.TestCase):
    def test_reuse_source_dirs_are_read_only_existing_trial_or_prior_run_paths(self):
        self.assertTrue(vr2.J0_REUSE_SOURCE_DIR.startswith("er019_output/"))
        self.assertTrue(vr2.E0_REUSE_SOURCE_DIR.startswith("er038_output/"))


if __name__ == "__main__":
    unittest.main()
