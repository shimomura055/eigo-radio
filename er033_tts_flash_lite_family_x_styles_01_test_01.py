# ============================================================
# er033_tts_flash_lite_family_x_styles_01_test_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 1
# ============================================================
# ¥0、API呼び出し無し。role別style定数モジュールが(1) Trial実測値
# (er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py)とbyte一致
# すること、(2) 既存Production plan_role文字列(FAMILY_X_B1_SEGMENT_ORDER/
# FAMILY_X_A2_SEGMENT_ORDER)の6-roleを過不足なくカバーすることを確認する。
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import er019_family_x_audio_plan_01 as plan
import er033_tts_flash_lite_family_x_styles_01 as fl_styles
import er044_tts_variable_spoken_role_style_trial_02 as trial02

_STAGE3_PATH = Path(__file__).with_name("er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py")

# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28)で
# TOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3roleがE0(Stage3実測値)からE2
# (TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02実測・ユーザー承認値)へ更新
# されたため、E0のままのroleとE2へ更新されたroleを分けてテストする。
_E2_UPDATED_ROLES = frozenset({"TOPIC_INTRO", "FULL_STORY", "IN_ONE_LINE"})
_E0_UNCHANGED_ROLES = frozenset({"PREVIEW", "COMMENT", "HEADING_READOUT"})

_SIX_ROLES = frozenset({
    "TOPIC_INTRO", "PREVIEW", "COMMENT", "FULL_STORY", "HEADING_READOUT", "IN_ONE_LINE",
})


def _load_stage3_module():
    """Trial script(er022_..._stage3.py)を、実行(TTS呼び出し等の
    副作用)せずに、ROLE_ATTEMPT1_STYLE/FALLBACK_STYLES定数だけを
    読み取るためにモジュールとしてimportする(if __name__=='__main__'
    ブロック配下のrun_stage3()は本test内では一切呼ばない)。"""
    spec = importlib.util.spec_from_file_location("_stage3_readonly", _STAGE3_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RoleStyleMatchesTrialEvidenceTests(unittest.TestCase):
    def test_stage3_script_exists(self):
        self.assertTrue(_STAGE3_PATH.exists(), f"Trial script not found: {_STAGE3_PATH}")

    def test_unchanged_role_style_en_byte_identical_to_trial_stage3(self):
        # TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B):
        # PREVIEW/COMMENT/HEADING_READOUTはE2未検証のため不変のまま(E0)。
        stage3 = _load_stage3_module()
        for role in _E0_UNCHANGED_ROLES:
            with self.subTest(role=role):
                self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN[role], stage3.ROLE_ATTEMPT1_STYLE[role])

    def test_updated_role_style_en_byte_identical_to_trial02_e2(self):
        # TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
        # ユーザー正式決定(E2、TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02)を
        # 逐語反映したことを確認する(stage3のE0とはもはや異なる)。
        for role in _E2_UPDATED_ROLES:
            with self.subTest(role=role):
                self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN[role], trial02.E_PATTERN_STYLES[role]["E2"])

    def test_fallback_styles_byte_identical_to_trial_stage3(self):
        stage3 = _load_stage3_module()
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK, stage3.FALLBACK_STYLES)


class RoleStyleCoversExistingPlanRolesTests(unittest.TestCase):
    """設計書§(d): Trialの6-role分類は既存Production
    FAMILY_X_B1_SEGMENT_ORDER/FAMILY_X_A2_SEGMENT_ORDERのplan_role文字列と
    一致する(新規に発明した分類ではない)ことを確認する。plan側には
    SFX/FIXED_SHARED/KEY_PHRASE/JAPANESE_TITLE等、Phase 1のstyle辞書が
    意図的にカバーしない役割も含まれる(SFX=効果音、FIXED_SHARED=
    再利用済み既存音声、KEY_PHRASE=別のMaster Audio Store経路、
    JAPANESE_TITLE=JA専用でTrial未検証、設計書§(d)/委任文のスコープ限定
    どおり)。ここでは「6-roleの各役割名が実際にplanへ実在すること」を
    確認する(逆方向: styleの側からplanへの存在確認)。"""

    def _plan_roles(self, segment_order) -> set:
        return {entry[2] for entry in segment_order}

    def test_all_six_style_roles_exist_in_b1_plan(self):
        roles = self._plan_roles(plan.FAMILY_X_B1_SEGMENT_ORDER)
        missing = _SIX_ROLES - roles
        self.assertEqual(missing, set(), f"6-role style keys missing from B1 plan: {missing}")

    def test_all_six_style_roles_exist_in_a2_plan(self):
        roles = self._plan_roles(plan.FAMILY_X_A2_SEGMENT_ORDER)
        missing = _SIX_ROLES - roles
        self.assertEqual(missing, set(), f"6-role style keys missing from A2 plan: {missing}")

    def test_style_dict_has_exactly_six_roles(self):
        self.assertEqual(set(fl_styles.FAMILY_X_ROLE_STYLE_EN.keys()), set(_SIX_ROLES))

    def test_all_style_values_are_non_empty_strings(self):
        for role, style in fl_styles.FAMILY_X_ROLE_STYLE_EN.items():
            with self.subTest(role=role):
                self.assertIsInstance(style, str)
                self.assertTrue(style.strip())


class ModelNameConstantTests(unittest.TestCase):
    def test_flash_lite_model_name_matches_trial(self):
        self.assertEqual(fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "gemini-3.8-flash-lite-tts")


class DanglingReferenceCheckTests(unittest.TestCase):
    """設計書§(d): このモジュール自体が定数辞書のみで構成され、import時に
    副作用(API呼び出し等)が一切発生しないことを確認する(importするだけで
    何のクライアントも作られない、既存Family A/B/C runnerが誤って
    importしても実害が無いことの裏付け)。"""

    def test_module_has_no_callables_besides_dunder(self):
        # "annotations"は`from __future__ import annotations`が作る
        # __future__.Feature値であり、本モジュールの定数ではない(除外)。
        public_names = [n for n in dir(fl_styles) if not n.startswith("_") and n != "annotations"]
        non_dict_str_values = [
            n for n in public_names
            if not isinstance(getattr(fl_styles, n), (dict, str, list, tuple, frozenset, int, float))
        ]
        self.assertEqual(non_dict_str_values, [],
                          f"Unexpected non-constant public members: {non_dict_str_values}")


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        RoleStyleMatchesTrialEvidenceTests, RoleStyleCoversExistingPlanRolesTests,
        ModelNameConstantTests, DanglingReferenceCheckTests,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
