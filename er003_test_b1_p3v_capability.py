# ============================================================
# er003_test_b1_p3v_capability.py
# ER-003-B1-P3V Phase 1: TTS API機能確認のテスト
# ============================================================
# 実TTS・実API呼び出しは行わない。インストール済みgoogle-genai SDKの
# 型定義を実際に調べ、Break/Mark/Timestamp系フィールドが存在しないこと
# (=現状の判定結果)を機械的に確認する。SDKが将来更新されてこれらの
# フィールドが追加された場合は、本テストが失敗して気づける設計とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3v_capability -v

import unittest

import er002_common as common
import er003_b1_p3v_capability as cap


class CheckTtsCapabilityTests(unittest.TestCase):

    def setUp(self):
        self.result = cap.check_tts_capability()

    def test_reports_actual_model_and_sdk(self):
        self.assertEqual(self.result["tts_model"], common.MODEL_NAME)
        self.assertEqual(self.result["sdk_name"], "google-genai")
        self.assertNotEqual(self.result["sdk_version"], "unknown")

    def test_speech_config_has_no_break_or_mark_fields(self):
        self.assertEqual(self.result["speech_config_fields"],
                          sorted(["language_code", "multi_speaker_voice_config", "voice_config"]))
        self.assertFalse(self.result["native_break_supported"])
        self.assertFalse(self.result["mark_timepoint_supported"])

    def test_part_has_no_timestamp_or_offset_fields(self):
        self.assertNotIn("timestamp", [f.lower() for f in self.result["part_fields"]])
        self.assertFalse(self.result["tts_timestamp_supported"])
        self.assertEqual(self.result["tts_timestamp_candidate_fields"], [])

    def test_ssml_break_not_supported(self):
        self.assertFalse(self.result["ssml_break_supported"])

    def test_no_capability_available_in_current_environment(self):
        """本テストは現在の環境における判定結果を固定化する。SDKが将来
        Break/Mark/Timestampへ対応した場合はこのテストが失敗し、
        Phase 2A/2Bへ進める可能性が生まれたことを示す。"""
        self.assertFalse(self.result["any_capability_available"])

    def test_part_metadata_is_not_treated_as_timestamp_support(self):
        """Part.part_metadataは汎用dictでありサーバーからタイミング情報が
        自動的に入る仕組みではないため、timestamp対応とは判定しない。"""
        self.assertIn("part_metadata", self.result["part_fields"])
        self.assertNotIn("part_metadata", self.result["tts_timestamp_candidate_fields"])

    def test_result_contains_required_report_fields(self):
        required_keys = {
            "tts_model", "sdk_name", "sdk_version", "request_form", "response_form",
            "native_break_supported", "ssml_break_supported",
            "mark_timepoint_supported", "tts_timestamp_supported",
            "sdk_offset_metadata_supported", "any_capability_available",
        }
        self.assertTrue(required_keys.issubset(self.result.keys()))


if __name__ == "__main__":
    unittest.main()
