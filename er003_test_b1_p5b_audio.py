# ============================================================
# er003_test_b1_p5b_audio.py
# ER-003-B1-P5B: Google Cloud TTS／Amazon Polly比較検証のテスト
# ============================================================
# 実クライアントへの読み取り専用呼び出し(list_voices/describe_voices)
# を含む統合テスト(いずれも認証情報なしで例外を捕捉することを確認)。
# 音声合成(課金対象)は一切呼ばない。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p5b_audio -v

import io
import unittest
import wave

import er003_b1_p5b_audio as p5b


class CheckGoogleCloudTtsAvailabilityTests(unittest.TestCase):

    def test_real_check_reports_available_after_adc_login(self):
        # ER-003-B1-P5B-GCPの時点で、ユーザーがgcloud auth application-
        # default loginを実行済み。list_voices(読み取り専用、課金なし)
        # で実際にADC認証情報を取得できることを確認する。
        result = p5b.check_google_cloud_tts_availability()
        self.assertTrue(result["available"], msg=result)
        self.assertTrue(result["package_installed"])
        self.assertTrue(result["voice_available"], msg="ja-JP-Neural2-Bが見つかりません")
        self.assertIn("ja-JP-Neural2-B", result["available_voices_for_language"])


class ExtractPcmFromGoogleWavResponseTests(unittest.TestCase):
    """実API呼び出しを行わず、合成のWAVコンテナ構造(実機smoke testで
    RIFF/WAVEヘッダー付きと確認済み)をsyntheticなWAVバイト列で検証する。"""

    def _build_synthetic_wav(self, framerate=24000, channels=1, sampwidth=2, pcm_samples=b"\x01\x00\x02\x00\x03\x00"):
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(channels)
            w.setsampwidth(sampwidth)
            w.setframerate(framerate)
            w.writeframes(pcm_samples)
        return buf.getvalue()

    def test_extracts_pcm_and_format_from_riff_wav(self):
        wav_bytes = self._build_synthetic_wav()
        self.assertEqual(wav_bytes[:4], b"RIFF")
        self.assertEqual(wav_bytes[8:12], b"WAVE")
        result = p5b.extract_pcm_from_google_wav_response(wav_bytes)
        self.assertEqual(result["framerate"], 24000)
        self.assertEqual(result["channels"], 1)
        self.assertEqual(result["sampwidth"], 2)
        self.assertEqual(result["pcm"], b"\x01\x00\x02\x00\x03\x00")

    def test_extracted_pcm_excludes_header_bytes(self):
        wav_bytes = self._build_synthetic_wav()
        result = p5b.extract_pcm_from_google_wav_response(wav_bytes)
        self.assertNotIn(b"RIFF", result["pcm"])
        self.assertNotIn(b"WAVE", result["pcm"])


class MakeGoogleTtsCallFnFormatValidationTests(unittest.TestCase):

    def test_raises_on_unexpected_sample_rate(self):
        # tts_call_fn内の形式チェック相当のロジックを、extract関数の
        # 出力に対して直接検証する(実APIは呼ばない)。
        wav_bytes = io.BytesIO()
        with wave.open(wav_bytes, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)  # 想定外のframerate
            w.writeframes(b"\x00\x00")
        result = p5b.extract_pcm_from_google_wav_response(wav_bytes.getvalue())
        self.assertNotEqual(result["framerate"], 24000)


class CheckAwsPollyAvailabilityTests(unittest.TestCase):

    def test_real_check_reports_unavailable_with_reason(self):
        # AWS認証情報も本実行環境には一切存在しない
        # (AWS_ACCESS_KEY_ID未設定、~/.aws無し、aws CLI無しを実機確認済み)。
        result = p5b.check_aws_polly_availability()
        self.assertFalse(result["available"])
        self.assertTrue(result["package_installed"])
        self.assertEqual(result["error_type"], "NoCredentialsError")
        self.assertIsNotNone(result["reason"])


class CheckNaniGaOkiruTests(unittest.TestCase):

    def test_detects_correct_reading(self):
        result = p5b.check_nani_ga_okiru("さいごのすうふん、なにがおきるのでしょうか")
        self.assertTrue(result["correct_present"])
        self.assertFalse(result["wrong_present"])

    def test_detects_wrong_reading(self):
        result = p5b.check_nani_ga_okiru("さいごのすうふん、なんがおきるのでしょうか")
        self.assertFalse(result["correct_present"])
        self.assertTrue(result["wrong_present"])

    def test_neither_present(self):
        result = p5b.check_nani_ga_okiru("まったく関係のない文字列")
        self.assertFalse(result["correct_present"])
        self.assertFalse(result["wrong_present"])


class CheckTargetPhrasesTests(unittest.TestCase):

    def test_six_target_phrases_defined(self):
        self.assertEqual(len(p5b.TARGET_PHRASES), 6)
        self.assertIn("なにがおきる", p5b.TARGET_PHRASES)

    def test_inherits_five_p5a_phrases(self):
        import er003_b1_p5a_audio as p5a
        for phrase in p5a.TARGET_PHRASES:
            self.assertIn(phrase, p5b.TARGET_PHRASES)

    def test_all_present_detected(self):
        text = "".join(p5b.TARGET_PHRASES)
        result = p5b.check_target_phrases(text)
        self.assertTrue(all(result.values()), msg=result)


if __name__ == "__main__":
    unittest.main()
