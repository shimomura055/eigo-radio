# ============================================================
# er007_ja_tts_retry_path_fix_test_01.py
# ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part A:
# stop_retrying=True後にTTS再生成が止まることを、実TTS/ASRを一切呼ばず
# mockで確認する(受入条件A-3: TTS生成回数=1)。
# ============================================================
from __future__ import annotations

import types
import unittest
from unittest import mock

import numpy as np

import er003_v1_n3_01_tts_generate as n3
import er003_v1_sing01_voice01_generate as voice01

_DUMMY_TRIM_INFO = {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0}


def _fake_cls(classification: str):
    return types.SimpleNamespace(classification=classification)


class VoiceCharonJapaneseStopRetryingTests(unittest.TestCase):
    """er003_v1_sing01_voice01_generate.generate_charon_japanese()"""

    def test_stop_retrying_true_tts_call_count_is_exactly_one(self):
        """Cascadeがstop_retrying=Trueを返したら、標準経路1回だけでTTSを
        打ち切り、attempt 2以降(フォールバック経路含む)へ進まないこと
        (受入条件A-3)。"""
        with mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn",
                                return_value=lambda *a, **k: None), \
             mock.patch.object(voice01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
             mock.patch.object(voice01.common, "_call_tts_with_retry",
                                return_value=(b"pcm", 0, True, None)) as mock_tts, \
             mock.patch.object(voice01.common, "pcm_bytes_to_float_mono",
                                return_value=np.zeros(100, dtype=np.float32)), \
             mock.patch.object(voice01.p3u, "trim_english_keyword_silence",
                                return_value=(np.zeros(100, dtype=np.float32), dict(_DUMMY_TRIM_INFO))), \
             mock.patch.object(voice01.safety, "detect_duration_anomaly",
                                return_value={"is_anomaly": False}), \
             mock.patch.object(voice01.common, "write_wav_float", return_value=None), \
             mock.patch.object(voice01.common, "measure_metrics",
                                return_value={"clipping_detected": False}), \
             mock.patch.object(voice01.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(voice01.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, True, _fake_cls("ASR_VALIDATION_UNCERTAIN"))):
            result = voice01.generate_charon_japanese("テスト文", "dummy_out.wav", "テス", max_attempts=6)

        self.assertEqual(mock_tts.call_count, 1,
                          "stop_retrying=True後にTTSが再生成されてはいけない(受入条件A-3)")
        self.assertEqual(result["status"], "ASR_VALIDATION_UNCERTAIN")
        self.assertFalse(result["asr_verified"])

    def test_stop_retrying_false_still_retries_normally(self):
        """回帰確認: stop_retrying=Falseの通常ケースでは、従来通りattempt 2
        以降へ進む(今回の修正が通常retryを壊していないこと)。"""
        with mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn",
                                return_value=lambda *a, **k: None), \
             mock.patch.object(voice01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
             mock.patch.object(voice01.common, "_call_tts_with_retry",
                                return_value=(b"pcm", 0, True, None)) as mock_tts, \
             mock.patch.object(voice01.common, "pcm_bytes_to_float_mono",
                                return_value=np.zeros(100, dtype=np.float32)), \
             mock.patch.object(voice01.p3u, "trim_english_keyword_silence",
                                return_value=(np.zeros(100, dtype=np.float32), dict(_DUMMY_TRIM_INFO))), \
             mock.patch.object(voice01.safety, "detect_duration_anomaly",
                                return_value={"is_anomaly": False}), \
             mock.patch.object(voice01.common, "write_wav_float", return_value=None), \
             mock.patch.object(voice01.common, "measure_metrics",
                                return_value={"clipping_detected": False}), \
             mock.patch.object(voice01.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(voice01.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))):
            result = voice01.generate_charon_japanese("テスト文", "dummy_out.wav", "テス", max_attempts=2)

        # 標準経路2回+フォールバック経路2回=4回呼ばれ、最終的にSTOPPEDになる
        self.assertEqual(mock_tts.call_count, 4)
        self.assertEqual(result["status"], "STOPPED")


class A2JapaneseFallbackStopRetryingTests(unittest.TestCase):
    """er003_v1_n3_01_tts_generate.generate_a2_japanese_with_fallback()の
    自前フォールバック経路(minimal instruction)。"""

    def test_stop_retrying_true_minimal_instruction_called_exactly_once(self):
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": []}), \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(n3.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, True, _fake_cls("ASR_VALIDATION_UNCERTAIN"))):
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス", max_attempts=6)

        self.assertEqual(mock_min.call_count, 1,
                          "stop_retrying=True後にTTS(minimal instruction)が再生成されてはいけない(受入条件A-3)")
        self.assertEqual(result["status"], "ASR_VALIDATION_UNCERTAIN")
        self.assertFalse(result["asr_verified"])

    def test_stop_retrying_false_still_retries_normally(self):
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": []}), \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(n3.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))):
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス", max_attempts=3)

        self.assertEqual(mock_min.call_count, 3)
        self.assertEqual(result["status"], "STOPPED")


if __name__ == "__main__":
    unittest.main()
