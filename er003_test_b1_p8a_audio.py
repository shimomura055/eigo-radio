# ============================================================
# er003_test_b1_p8a_audio.py
# ER-003-B1-P8A: er003_b1_p8a_audioの回帰テスト
# ============================================================
# 実TTS/QA/ファイルI/O呼び出しは行わない。接続ロジックは合成波形で検証する。

import unittest

import numpy as np

import er003_b1_p8a_audio as p8a


def _tone(n_samples: int, value: float = 0.3) -> "np.ndarray":
    return np.full(n_samples, value, dtype=np.float64)


class ConcatenatePreviewAndBodyTests(unittest.TestCase):
    def setUp(self):
        self.sr = 1000
        # preview: 発話(300)+既存無音(50) / body: 既存無音(80)+発話(300)
        self.preview = np.concatenate([_tone(300, 0.5), _tone(50, 0.0)])
        self.body = np.concatenate([_tone(80, 0.0), _tone(300, 0.4)])

    def test_effective_gap_is_exactly_target(self):
        result = p8a.concatenate_preview_and_body(self.preview, self.body, self.sr, pause_seconds=0.8)
        self.assertAlmostEqual(result["effective_gap_seconds"], 0.8, places=6)

    def test_speech_content_unchanged_both_sides(self):
        result = p8a.concatenate_preview_and_body(self.preview, self.body, self.sr, pause_seconds=0.8)
        self.assertTrue(result["preview_trailing_adjustment"]["speech_content_unchanged"])
        self.assertTrue(result["body_leading_adjustment"]["speech_content_unchanged"])

    def test_body_audio_follows_preview_audio_in_order(self):
        result = p8a.concatenate_preview_and_body(self.preview, self.body, self.sr, pause_seconds=0.8)
        combined = result["combined"].tolist()
        idx_05 = combined.index(0.5)
        idx_04 = combined.index(0.4)
        self.assertLess(idx_05, idx_04)

    def test_no_crossfade_no_content_loss(self):
        # previewの発話(0.5)とbodyの発話(0.4)の値が、それぞれの長さ分だけ
        # そのまま残っていること(混合・減衰されていない)を確認する。
        result = p8a.concatenate_preview_and_body(self.preview, self.body, self.sr, pause_seconds=0.8)
        combined = result["combined"]
        self.assertEqual(int(np.sum(combined == 0.5)), 300)
        self.assertEqual(int(np.sum(combined == 0.4)), 300)

    def test_body_start_sample_matches_reported_position(self):
        result = p8a.concatenate_preview_and_body(self.preview, self.body, self.sr, pause_seconds=0.8)
        start = result["body_start_sample_in_combined"]
        self.assertAlmostEqual(result["combined"][start], 0.4, places=6)


class ModelIsolationTests(unittest.TestCase):
    def test_preview_and_body_models_differ(self):
        result = p8a.check_model_isolation()
        self.assertTrue(result["isolated"])
        self.assertEqual(result["preview_model"], "gemini-3.1-flash-tts-preview")
        self.assertEqual(result["article_body_model"], "gemini-2.5-pro-preview-tts")
        self.assertTrue(result["article_body_model_is_frozen_spec"])


class LoudnessDiagnosticsTests(unittest.TestCase):
    def test_reports_expected_fields(self):
        samples = _tone(2000, 0.3)
        result = p8a.loudness_diagnostics(samples, 1000, "test")
        self.assertEqual(result["label"], "test")
        self.assertAlmostEqual(result["peak"], 0.3, places=5)
        self.assertAlmostEqual(result["rms"], 0.3, places=5)
        self.assertFalse(result["clipping_detected"])


class ExtractTransitionClipTests(unittest.TestCase):
    def test_clip_bounds_respect_array_edges(self):
        combined = _tone(1000, 0.1)
        clip = p8a.extract_transition_clip(combined, 100, body_start_sample=500,
                                            preview_tail_seconds=10, body_head_seconds=10)
        self.assertEqual(len(clip), 1000)  # 全体が範囲内に収まる


if __name__ == "__main__":
    unittest.main()
