# ============================================================
# er008_a2_postprocess_slowdown_01_test_01.py
# ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11: 6%time-stretchユーティリティの
# 回帰テスト(ER-008-A2-TIMESTRETCH-ABC-10で実データ検証済みの処理を
# 再利用しているだけだが、Production配線後もこの中核関数が壊れていない
# ことを継続的に確認する)。
# ============================================================
from __future__ import annotations

import os
import tempfile
import unittest
import wave

import numpy as np

import er008_a2_postprocess_slowdown_01 as slowdown


def _write_tone_wav(path: str, duration_seconds: float = 3.0, freq: float = 220.0, sr: int = 24000) -> None:
    t = np.linspace(0, duration_seconds, int(sr * duration_seconds), endpoint=False)
    samples = (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float64)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


class A2SlowdownPostprocessTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.src = os.path.join(self.tmpdir, "src.wav")
        _write_tone_wav(self.src, duration_seconds=3.0)

    def test_default_slowdown_is_six_percent(self):
        self.assertEqual(slowdown.A2_SLOWDOWN_PERCENT, 6.0)

    def test_apply_slowdown_stretches_duration_by_target_percent(self):
        dst = os.path.join(self.tmpdir, "dst.wav")
        result = slowdown.apply_a2_slowdown(self.src, dst, slowdown_pct=6.0)
        self.assertTrue(os.path.exists(dst))
        self.assertAlmostEqual(result["slowdown_pct_actual"], 6.0, delta=0.5)
        self.assertGreater(result["dst_duration_seconds"], result["src_duration_seconds"])

    def test_apply_slowdown_at_three_and_nine_percent(self):
        for pct in (3.0, 9.0):
            with self.subTest(pct=pct):
                dst = os.path.join(self.tmpdir, f"dst_{pct}.wav")
                result = slowdown.apply_a2_slowdown(self.src, dst, slowdown_pct=pct)
                self.assertAlmostEqual(result["slowdown_pct_actual"], pct, delta=0.5)

    def test_output_is_valid_wav_same_format(self):
        dst = os.path.join(self.tmpdir, "dst2.wav")
        slowdown.apply_a2_slowdown(self.src, dst, slowdown_pct=6.0)
        with wave.open(dst, "rb") as w:
            self.assertEqual(w.getframerate(), 24000)
            self.assertEqual(w.getnchannels(), 1)
            self.assertEqual(w.getsampwidth(), 2)

    def test_rejects_out_of_range_slowdown(self):
        dst = os.path.join(self.tmpdir, "dst3.wav")
        with self.assertRaises(AssertionError):
            slowdown.apply_a2_slowdown(self.src, dst, slowdown_pct=-99.9)


if __name__ == "__main__":
    unittest.main()
