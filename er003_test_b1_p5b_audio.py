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

import unittest

import er003_b1_p5b_audio as p5b


class CheckGoogleCloudTtsAvailabilityTests(unittest.TestCase):

    def test_real_check_reports_unavailable_with_reason(self):
        # このプロジェクトの実行環境には、GCP認証情報が一切存在しない
        # (GOOGLE_APPLICATION_CREDENTIALS未設定、~/.config/gcloud無し、
        # gcloud CLI無しを実機確認済み)。パッケージはインストール済みの
        # ため、DefaultCredentialsErrorで不可と判定されるはず。
        result = p5b.check_google_cloud_tts_availability()
        self.assertFalse(result["available"])
        self.assertTrue(result["package_installed"])
        self.assertEqual(result["error_type"], "DefaultCredentialsError")
        self.assertIsNotNone(result["reason"])


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
