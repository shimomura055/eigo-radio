# ============================================================
# er022_tts_gemini_3_8_flash_lite_ab_trial_01_test.py
# TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01(単体テスト、API課金なし)
# ============================================================
# model_b_override()がProduction定数(er003_b1_p9a_audio.ENGLISH_MODEL_NAME/
# JAPANESE_MODEL_NAME)を必ず復元すること(例外発生時も含む)だけを
# 検証する。実際のTTS/ASR API callはモックし、課金は発生させない。
from __future__ import annotations

import unittest
from unittest import mock

import er003_b1_p9a_audio as p9a
import er022_tts_gemini_3_8_flash_lite_ab_trial_01 as trial


class ModelBOverrideTest(unittest.TestCase):
    def test_override_and_restore(self):
        orig_en, orig_ja = p9a.ENGLISH_MODEL_NAME, p9a.JAPANESE_MODEL_NAME
        with trial.model_b_override():
            self.assertEqual(p9a.ENGLISH_MODEL_NAME, trial.MODEL_B)
            self.assertEqual(p9a.JAPANESE_MODEL_NAME, trial.MODEL_B)
        self.assertEqual(p9a.ENGLISH_MODEL_NAME, orig_en)
        self.assertEqual(p9a.JAPANESE_MODEL_NAME, orig_ja)

    def test_override_restores_even_on_exception(self):
        orig_en, orig_ja = p9a.ENGLISH_MODEL_NAME, p9a.JAPANESE_MODEL_NAME
        with self.assertRaises(RuntimeError):
            with trial.model_b_override():
                self.assertEqual(p9a.ENGLISH_MODEL_NAME, trial.MODEL_B)
                raise RuntimeError("boom")
        self.assertEqual(p9a.ENGLISH_MODEL_NAME, orig_en)
        self.assertEqual(p9a.JAPANESE_MODEL_NAME, orig_ja)

    def test_does_not_touch_frozen_common_model_name(self):
        """common.MODEL_NAME(ER-002凍結仕様)はmodel_b_override()の対象
        外であることを確認する(topic_intro専用経路がこの定数を一切
        参照しないという設計判断の裏付け)。"""
        import er002_common as common
        orig = common.MODEL_NAME
        with trial.model_b_override():
            self.assertEqual(common.MODEL_NAME, orig)
        self.assertEqual(common.MODEL_NAME, orig)


class TopicIntroWithModelTest(unittest.TestCase):
    def test_verified_on_first_attempt_uses_shared_primitives_only(self):
        """generate_topic_intro_with_model()が、ASR検証に成功した時点で
        即座に返す(不要な追加API callを課金しない)ことを、TTS/ASRを
        モックして確認する。"""
        import numpy as np
        # 1秒分のmono 16bit相当の擬似音声(無音判定を避けるため単純な
        # sine波、実際の発話内容の検証はここでは行わない)。
        t = np.linspace(0, 1, 24000, endpoint=False)
        fake_samples = (np.sin(2 * np.pi * 220 * t) * 0.2 * 32767).astype("int16")
        fake_pcm = fake_samples.tobytes()

        def fake_make_tts_call_fn_for_model(model_name, voice_name, client=None):
            def _fn(prompt):
                return fake_pcm
            return _fn

        with mock.patch.object(trial.p7a, "make_tts_call_fn_for_model",
                                side_effect=fake_make_tts_call_fn_for_model) as m_call, \
             mock.patch.object(trial.routing, "transcribe",
                                return_value=("Today's topic is a test.", None)) as m_asr, \
             mock.patch.object(trial.common, "write_wav_float") as m_write:
            result = trial.generate_topic_intro_with_model(
                "Today's topic is a test.", "dummy_out.wav", trial.MODEL_B, "Charon")
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertEqual(m_call.call_count, 1)
        self.assertEqual(m_asr.call_count, 1)
        self.assertEqual(m_write.call_count, 1)


if __name__ == "__main__":
    unittest.main()
