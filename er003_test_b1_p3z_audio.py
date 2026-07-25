# ============================================================
# er003_test_b1_p3z_audio.py
# ER-003-B1-P3Z: 英語前後の間・9パターン比較のテスト
# ============================================================
# 実TTS・実MFA呼び出しは行わない。無音調整ロジック(trim/pad)と
# パターン生成ロジックのみを対象とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3z_audio -v

import unittest

import numpy as np

import er003_b1_p3z_audio as p3z


class BuildPatternsTests(unittest.TestCase):

    def test_generates_nine_patterns(self):
        patterns = p3z.build_patterns()
        self.assertEqual(len(patterns), 9)

    def test_covers_all_3x3_combinations(self):
        patterns = p3z.build_patterns()
        combos = {(p["gap_before_seconds"], p["gap_after_seconds"]) for p in patterns}
        expected = {(b, a) for b in p3z.GAP_VALUES for a in p3z.GAP_VALUES}
        self.assertEqual(combos, expected)

    def test_filenames_encode_seconds_and_are_unique(self):
        patterns = p3z.build_patterns()
        filenames = [p["filename"] for p in patterns]
        self.assertEqual(len(filenames), len(set(filenames)))
        p1 = next(p for p in patterns if p["no"] == "01")
        self.assertEqual(p1["filename"], "01_A01_gap_before_0p2s_after_0p2s_dynamics3.wav")
        p9 = next(p for p in patterns if p["no"] == "09")
        self.assertEqual(p9["filename"], "09_A01_gap_before_0p4s_after_0p4s_dynamics3.wav")

    def test_numbering_is_01_to_09_in_order(self):
        patterns = p3z.build_patterns()
        self.assertEqual([p["no"] for p in patterns], [f"{i:02d}" for i in range(1, 10)])


class MeasureComponentSilenceTests(unittest.TestCase):

    def test_measures_leading_and_trailing_silence(self):
        sr = 24000
        rng = np.random.default_rng(1)
        lead = np.zeros(int(sr * 0.1))
        speech = rng.uniform(-0.3, 0.3, int(sr * 0.5))
        trail = np.zeros(int(sr * 0.15))
        samples = np.concatenate([lead, speech, trail]).astype(np.float64)
        result = p3z.measure_component_silence(samples, sr)
        self.assertAlmostEqual(result["leading_silence_seconds"], 0.1, delta=0.02)
        self.assertAlmostEqual(result["trailing_silence_seconds"], 0.15, delta=0.02)


class AdjustTrailingSilenceTests(unittest.TestCase):

    def _make_signal(self, sr=24000, speech_len_s=0.5, trailing_len_s=0.32):
        rng = np.random.default_rng(2)
        speech = rng.uniform(-0.3, 0.3, int(sr * speech_len_s)).astype(np.float64)
        trail = np.zeros(int(sr * trailing_len_s), dtype=np.float64)
        samples = np.concatenate([speech, trail])
        speech_end_sample = len(speech)
        return samples, sr, speech_end_sample

    def test_trims_when_target_smaller_than_natural(self):
        samples, sr, speech_end = self._make_signal()
        result, info = p3z.adjust_trailing_silence(samples, sr, speech_end, target_trailing_seconds=0.12)
        self.assertAlmostEqual(info["achieved_trailing_seconds"], 0.12, delta=0.001)
        self.assertTrue(info["speech_content_unchanged"])
        self.assertEqual(len(result), speech_end + int(round(0.12 * sr)))

    def test_pads_when_target_larger_than_natural(self):
        samples, sr, speech_end = self._make_signal(trailing_len_s=0.08)
        result, info = p3z.adjust_trailing_silence(samples, sr, speech_end, target_trailing_seconds=0.32)
        self.assertAlmostEqual(info["achieved_trailing_seconds"], 0.32, delta=0.001)
        self.assertTrue(info["speech_content_unchanged"])

    def test_never_touches_speech_content(self):
        samples, sr, speech_end = self._make_signal()
        speech_before = samples[:speech_end].copy()
        result, info = p3z.adjust_trailing_silence(samples, sr, speech_end, target_trailing_seconds=0.0)
        np.testing.assert_array_equal(result[:speech_end], speech_before)

    def test_raises_on_negative_target(self):
        samples, sr, speech_end = self._make_signal()
        with self.assertRaises(ValueError):
            p3z.adjust_trailing_silence(samples, sr, speech_end, target_trailing_seconds=-0.1)


class AdjustLeadingSilenceTests(unittest.TestCase):

    def _make_signal(self, sr=24000, leading_len_s=0.0, speech_len_s=0.5):
        rng = np.random.default_rng(3)
        lead = np.zeros(int(sr * leading_len_s), dtype=np.float64)
        speech = rng.uniform(-0.3, 0.3, int(sr * speech_len_s)).astype(np.float64)
        samples = np.concatenate([lead, speech])
        speech_start_sample = len(lead)
        return samples, sr, speech_start_sample

    def test_pads_when_target_larger_than_natural_zero(self):
        samples, sr, speech_start = self._make_signal(leading_len_s=0.0)
        result, info = p3z.adjust_leading_silence(samples, sr, speech_start, target_leading_seconds=0.22)
        self.assertAlmostEqual(info["achieved_leading_seconds"], 0.22, delta=0.001)
        self.assertTrue(info["speech_content_unchanged"])

    def test_trims_when_target_smaller_than_natural(self):
        samples, sr, speech_start = self._make_signal(leading_len_s=0.3)
        result, info = p3z.adjust_leading_silence(samples, sr, speech_start, target_leading_seconds=0.1)
        self.assertAlmostEqual(info["achieved_leading_seconds"], 0.1, delta=0.001)
        self.assertTrue(info["speech_content_unchanged"])

    def test_never_touches_speech_content(self):
        samples, sr, speech_start = self._make_signal(leading_len_s=0.0, speech_len_s=0.5)
        speech_after = samples[speech_start:].copy()
        result, info = p3z.adjust_leading_silence(samples, sr, speech_start, target_leading_seconds=0.4)
        new_start = int(round(0.4 * sr))
        np.testing.assert_array_equal(result[new_start:], speech_after)

    def test_raises_on_negative_target(self):
        samples, sr, speech_start = self._make_signal()
        with self.assertRaises(ValueError):
            p3z.adjust_leading_silence(samples, sr, speech_start, target_leading_seconds=-0.1)


class RealComponentFeasibilityTests(unittest.TestCase):
    """P3Yの実成果物に対する実測値(手動確認済み: ja_before trailing=
    0.32s, en leading/trailing=0.08s/0.08s, ja_after leading=0.0s)を
    ハードコードし、9パターン全てが安全に(発話を削らず)達成可能で
    あることを固定化する。"""

    _JA_BEFORE_TRAILING = 0.32
    _EN_LEADING = 0.08
    _EN_TRAILING = 0.08
    _JA_AFTER_LEADING = 0.0

    def test_all_before_targets_achievable_without_cutting_speech(self):
        for target in p3z.GAP_VALUES:
            needed_ja_before_trailing = target - self._EN_LEADING
            self.assertGreaterEqual(needed_ja_before_trailing, 0, msg=f"target={target}")

    def test_all_after_targets_achievable_without_cutting_speech(self):
        for target in p3z.GAP_VALUES:
            needed_ja_after_leading = target - self._EN_TRAILING
            self.assertGreaterEqual(needed_ja_after_leading, 0, msg=f"target={target}")


if __name__ == "__main__":
    unittest.main()
