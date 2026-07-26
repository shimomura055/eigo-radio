# ============================================================
# er003_test_b1_p5a_audio.py
# ER-003-B1-P5A: 日本語TTS原稿忠実性スクリーニングのテスト
# ============================================================
# P4D入力の読み込み・ハッシュ検証・エンジン可用性判定・対象句チェック
# ロジックを対象とする。Azure Speech呼び出しは、最小限の短文1回だけ
# 実サブプロセス相当の実APIコールを行う統合テストを含む(Gemini TTS・
# 全文生成は呼ばない)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p5a_audio -v

import tempfile
import unittest

import er003_b1_p5a_audio as p5a


class LoadP4dInputTests(unittest.TestCase):

    def test_real_p4d_input_loads_and_hash_matches(self):
        result = p5a.load_p4d_input()
        self.assertEqual(result["sha256"], p5a.P4D_EXPECTED_HIRAGANA_SHA256)
        self.assertGreater(len(result["text"]), 0)

    def test_raises_on_hash_mismatch(self):
        with self.assertRaises(ValueError):
            p5a.load_p4d_input(expected_sha256="0" * 64)

    def test_raises_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            p5a.load_p4d_input(hiragana_path="does_not_exist.txt")

    def test_marked_text_loads(self):
        text = p5a.load_p4d_marked_text()
        self.assertIn("目印", text)
        self.assertEqual(text.count("目印"), 5)


class CheckEngineAvailabilityTests(unittest.TestCase):

    def test_returns_all_three_candidates(self):
        result = p5a.check_engine_availability()
        self.assertIn("google_cloud_tts", result)
        self.assertIn("azure_speech", result)
        self.assertIn("amazon_polly", result)

    def test_unavailable_candidates_have_reason(self):
        result = p5a.check_engine_availability()
        for engine, info in result.items():
            if not info["available"]:
                self.assertIsNotNone(info["reason"], msg=engine)

    def test_azure_speech_available_in_this_environment(self):
        # このプロジェクトでは既にSPEECH_KEY/SPEECH_REGIONが.envに設定済み
        # (Azure STTで既に使用中)であり、SDKもインストール済みのため、
        # Azure Speechだけは利用可能であるはず(実機確認済み)。
        result = p5a.check_engine_availability()
        self.assertTrue(result["azure_speech"]["available"], msg=result["azure_speech"])


class CheckTargetPhrasesTests(unittest.TestCase):

    def test_all_five_phrases_detected_when_present(self):
        text = "".join(p5a.TARGET_PHRASES)
        result = p5a.check_target_phrases(text)
        self.assertTrue(all(result.values()), msg=result)

    def test_missing_phrase_reported_as_absent(self):
        text = "せんしゅをこうたいでさげる、しゅびをかため、わずかなりーど、さいごのすうふん"
        result = p5a.check_target_phrases(text)
        self.assertFalse(result["めじるしというけつだんで"])
        self.assertTrue(result["せんしゅをこうたいでさげる"])

    def test_five_target_phrases_defined(self):
        self.assertEqual(len(p5a.TARGET_PHRASES), 5)


class AzureTtsCallFnIntegrationTests(unittest.TestCase):
    """実Azure Speech APIへの最小限のサブプロセス相当呼び出しを含む
    統合テスト(短文1回のみ、全文生成やGemini TTSは呼ばない)。"""

    def test_minimal_real_call_returns_pcm_and_metadata(self):
        tts_call_fn = p5a.make_azure_tts_call_fn()
        pcm = tts_call_fn("テスト")
        self.assertIsInstance(pcm, bytes)
        self.assertGreater(len(pcm), 0)
        self.assertIsNotNone(tts_call_fn.last_result_metadata)
        self.assertEqual(tts_call_fn.last_result_metadata["voice_name"], p5a.AZURE_VOICE_NAME)


class AsrReadingNormalizeTests(unittest.TestCase):

    def test_real_sudachi_pipeline_normalizes_kanji_text(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = p5a.asr_reading_normalize("守備を固め", tmp_dir)
        self.assertEqual(result, "しゅびをかため")


if __name__ == "__main__":
    unittest.main()
