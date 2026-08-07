# ============================================================
# er003_test_b1_p9a_audio.py
# ER-003-B1-P9A: er003_b1_p9a_audioの回帰テスト
# ============================================================
# 実TTS/外部mp3ファイル呼び出しは行わない。gain計算・リサンプリング・
# 無音生成のロジックのみを合成データで検証する。

import unittest

import numpy as np

import er003_b1_p9a_audio as p9a


class RmsPeakTests(unittest.TestCase):
    def test_rms_of_constant_signal(self):
        samples = np.full(1000, 0.5)
        self.assertAlmostEqual(p9a.rms(samples), 0.5, places=6)

    def test_peak_of_signal(self):
        samples = np.array([0.1, -0.9, 0.3])
        self.assertAlmostEqual(p9a.peak(samples), 0.9, places=6)

    def test_rms_of_empty_signal_is_zero(self):
        self.assertEqual(p9a.rms(np.array([])), 0.0)


class ComputeGainForTargetRmsTests(unittest.TestCase):
    def test_gain_scales_rms_to_target(self):
        samples = np.full(1000, 0.2)
        gain = p9a.compute_gain_for_target_rms(samples, target_rms=0.1)
        self.assertAlmostEqual(gain, 0.5, places=6)
        self.assertAlmostEqual(p9a.rms(samples * gain), 0.1, places=6)

    def test_gain_is_capped_by_peak_safety(self):
        # RMS基準だと大きなgainが必要だが、ピークが1.0近くにあるため
        # max_peakで頭打ちになることを確認する。
        samples = np.array([0.001] * 999 + [0.9])
        gain = p9a.compute_gain_for_target_rms(samples, target_rms=1.0, max_peak=0.95)
        self.assertLessEqual(np.max(np.abs(samples * gain)), 0.95 + 1e-9)

    def test_silent_input_returns_unity_gain(self):
        samples = np.zeros(1000)
        gain = p9a.compute_gain_for_target_rms(samples, target_rms=0.1)
        self.assertEqual(gain, 1.0)


class SilenceStereoTests(unittest.TestCase):
    def test_shape_and_duration(self):
        sr = 48000
        sec = 0.5
        result = p9a.silence_stereo(sec, sr=sr)
        self.assertEqual(result.shape, (int(sec * sr), 2))
        self.assertTrue(np.all(result == 0.0))

    def test_zero_duration_gives_empty_array(self):
        result = p9a.silence_stereo(0.0)
        self.assertEqual(len(result), 0)


class MonoToStereoResampleTests(unittest.TestCase):
    def test_output_is_stereo_with_l_equals_r(self):
        mono_24k = np.sin(np.linspace(0, 2 * np.pi * 10, 24000))  # 1秒、10Hz相当のダミー波形
        stereo = p9a.mono_24k_to_stereo_target(mono_24k, target_sr=48000)
        self.assertEqual(stereo.shape[1], 2)
        self.assertTrue(np.allclose(stereo[:, 0], stereo[:, 1]))

    def test_duration_preserved_after_resample(self):
        # 24000Hzから48000Hzへの単純upsampleでは、秒数(内容の速度)が
        # 変わらないことを確認する(不当なtime-stretchが起きていないか)。
        mono_24k = np.zeros(24000)  # ちょうど1秒
        stereo = p9a.mono_24k_to_stereo_target(mono_24k, target_sr=48000)
        duration_seconds = len(stereo) / 48000
        self.assertAlmostEqual(duration_seconds, 1.0, places=2)


class NarrationTextConstantsTests(unittest.TestCase):
    def test_narration_texts_match_user_instruction_verbatim(self):
        self.assertEqual(p9a.PODCAST_NAME_TEXT, "English Your Way.")
        self.assertEqual(p9a.PREVIEW_INTRO_TEXT, "Here's a quick preview.")
        self.assertEqual(p9a.FULL_STORY_INTRO_TEXT, "Now, the full story.")

    def test_pause_durations_are_within_instructed_ranges(self):
        self.assertEqual(p9a.PAUSE_AFTER_PODCAST_NAME_SECONDS, 0.5)
        self.assertTrue(0.5 <= p9a.PAUSE_BETWEEN_TITLES_SECONDS <= 0.8)
        self.assertEqual(p9a.PAUSE_AFTER_JAPANESE_TITLE_SECONDS, 0.5)
        self.assertTrue(0.3 <= p9a.PAUSE_AFTER_NOTIFICATION_SECONDS <= 0.5)
        self.assertEqual(p9a.PAUSE_AFTER_PREVIEW_INTRO_SECONDS, 0.5)
        self.assertEqual(p9a.PAUSE_AFTER_PREVIEW_SECONDS, 0.5)
        self.assertEqual(p9a.PAUSE_AFTER_FULL_STORY_INTRO_SECONDS, 0.7)
        self.assertEqual(p9a.PAUSE_AFTER_FULL_STORY_SECONDS, 0.5)
        self.assertEqual(p9a.PAUSE_AFTER_INTRO_SECONDS, 0.0)
        self.assertEqual(p9a.PAUSE_AFTER_OUTRO_SECONDS, 0.0)


if __name__ == "__main__":
    unittest.main()
