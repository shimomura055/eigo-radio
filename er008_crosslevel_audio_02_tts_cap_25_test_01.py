# ============================================================
# er008_crosslevel_audio_02_tts_cap_25_test.py
# ER-008-N8-CLOSEOUT-GOVERNANCE-25 (2): 横断loop監査で発見した、
# er003_v1_crosslevel_audio_02_common.py::generate_text_segments()の
# 日本語segment分岐が、Production SSOT(review_lock.PRODUCTION_MAX_TTS_ATTEMPTS=3)
# を2倍上回るmax_attempts=6をハードコードしていた件のregression test。
# 修正後は明示的にSSOT定数を参照するようになっている。
# ============================================================
import shutil
import tempfile
import unittest

import er003_v1_crosslevel_audio_02_common as clac
import er011_human_review_lock_01 as review_lock


class JapaneseSegmentUsesProductionSsotCapTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er008_gov25_")
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)
        self.captured_kwargs = {}

        def fake_generate_narration_snippet_verified_strict(text, language, out_path, expected_substring,
                                                              max_attempts=None, max_extra_chars=None, **kwargs):
            self.captured_kwargs["max_attempts"] = max_attempts
            with open(out_path, "wb") as f:
                f.write(b"")
            return {"status": "OK", "attempts_log": []}

        self._orig = clac.generate_narration_snippet_verified_strict
        clac.generate_narration_snippet_verified_strict = fake_generate_narration_snippet_verified_strict
        self.addCleanup(setattr, clac, "generate_narration_snippet_verified_strict", self._orig)

    def test_japanese_branch_uses_ssot_cap_not_hardcoded_six(self):
        config = {
            "out_dir": self.tmp_dir,
            "segments": [("comment_1", "テストコメント", "ja", "テスト", 60)],
        }
        clac.generate_text_segments(config)
        self.assertEqual(self.captured_kwargs["max_attempts"], review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
        self.assertNotEqual(self.captured_kwargs["max_attempts"], 6,
                             "旧ハードコード値6が再導入されていないことを確認する")


if __name__ == "__main__":
    unittest.main()
