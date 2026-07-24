# ============================================================
# er003_test_b1_p3s_audio.py
# ER-003-B1-P3S: 日英分離TTS・短尺結合サンプル検証のテスト
# ============================================================
# 実API・実TTSは一切行わない。すべてモック・既存成果物の読み込みのみ。
# 共有コード(er002_common/er002_gemini_client/er003_b1_p3r_audio)は
# 変更していないため、本ファイルは新規追加分(select_excerptの切り出し
# ロジック)だけに絞る(大規模なテスト追加はしない)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3s_audio -v

import unittest

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3s_audio as p3s

SAMPLE_PATTERN_A_TEXT = (
    "前半は静かに進みました。両チームとも枠内シュート、shot on targetを記録できないまま、"
    "均衡が保たれます。後半に動きが出て、選手を交代で下げる、take players offという判断も"
    "ありました。"
)


class SelectExcerptTests(unittest.TestCase):

    def test_extracts_three_spans_for_default_key_phrase(self):
        result = p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT)
        self.assertEqual(result["key_phrase"], "shot on target")
        self.assertEqual(result["ja_before"], "両チームとも枠内シュート、")
        self.assertEqual(result["en_keyword"], "shot on target")
        self.assertEqual(result["ja_after"], "を記録できないまま、均衡が保たれます。")

    def test_reconstructed_matches_original_substring(self):
        result = p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT)
        self.assertIn(result["reconstructed"], SAMPLE_PATTERN_A_TEXT)

    def test_no_punctuation_adjustment_by_default(self):
        result = p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT)
        self.assertFalse(result["punctuation_adjusted"])

    def test_ja_before_starts_after_preceding_terminal_punctuation(self):
        """先行する文(「前半は静かに進みました。」)を含めず、直前の
        文末記号の直後から始まることを確認する。"""
        result = p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT)
        self.assertNotIn("前半は静かに進みました", result["ja_before"])

    def test_ja_after_stops_at_next_terminal_punctuation(self):
        """後続の文(「後半に動きが出て...」)を含まないことを確認する。"""
        result = p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT)
        self.assertNotIn("後半に動きが出て", result["ja_after"])
        self.assertTrue(result["ja_after"].endswith("。"))

    def test_alternative_key_phrase_extracts_correctly(self):
        """5表現のうち他の表現でも同じロジックで切り出せることの確認
        (指示section 4の「他の4表現から選ぶ」フォールバックに対応)。"""
        result = p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT, key_phrase="take players off")
        self.assertEqual(result["key_phrase"], "take players off")
        self.assertIn("選手を交代で下げる", result["ja_before"])
        self.assertTrue(result["ja_after"].strip())

    def test_missing_key_phrase_raises(self):
        with self.assertRaises(ValueError):
            p3s.select_excerpt(SAMPLE_PATTERN_A_TEXT, key_phrase="not in the text at all")

    def test_first_sentence_key_phrase_with_no_preceding_terminal(self):
        """Key Phraseが原稿冒頭の文にある場合(直前に「。」がない)、
        文頭からja_beforeを取ることを確認する。"""
        text = "枠内シュート、shot on targetが焦点でした。次の文が続きます。"
        result = p3s.select_excerpt(text)
        self.assertEqual(result["ja_before"], "枠内シュート、")

    def test_real_pattern_a_default_excerpt(self):
        """実際のPattern A原稿(ER-003-B1-P2の実成果物)に対して、
        既定のKey Phrase(shot on target)で切り出せることを確認する。"""
        pattern_a = p3s.load_pattern_a_text()
        result = p3s.select_excerpt(pattern_a)
        self.assertEqual(result["key_phrase"], "shot on target")
        self.assertTrue(result["ja_before"].strip())
        self.assertTrue(result["ja_after"].strip())
        self.assertIn(result["reconstructed"], pattern_a)


class ReuseIdentityTests(unittest.TestCase):
    """ER-003-B1-P3RのTTS instruction/voice/source読み込みロジックを
    再利用しており、独自に再定義していないことを確認する。"""

    def test_voice_name_matches_p3r(self):
        self.assertEqual(p3s.VOICE_NAME, p3r.VOICE_NAME)
        self.assertEqual(p3s.VOICE_NAME, "Aoede")

    def test_pattern_a_source_path_matches_p3r(self):
        self.assertEqual(p3s.PATTERN_A_SOURCE_PATH, p3r.PATTERN_A_SOURCE_PATH)

    def test_load_pattern_a_text_is_p3r_function(self):
        self.assertIs(p3s.load_pattern_a_text, p3r.load_pattern_a_text)

    def test_build_style_prefix_is_p3r_function(self):
        self.assertIs(p3s.build_style_prefix, p3r.build_style_prefix)
        self.assertEqual(p3s.build_style_prefix(), common.build_style_prefix())

    def test_build_tts_prompt_is_p3r_function(self):
        self.assertIs(p3s.build_tts_prompt, p3r.build_tts_prompt)

    def test_sha256_text_is_p3r_function(self):
        self.assertIs(p3s.sha256_text, p3r.sha256_text)

    def test_join_pause_is_02_seconds_not_08(self):
        """本ステージ限定の初回技術値(0.2秒)であり、正式仕様の0.8秒
        (er002_common.SECTION_JOIN_PAUSE_SECONDS)とは別であることを
        確認する。"""
        self.assertEqual(p3s.JOIN_PAUSE_SECONDS, 0.2)
        self.assertNotEqual(p3s.JOIN_PAUSE_SECONDS, common.SECTION_JOIN_PAUSE_SECONDS)

    def test_max_technical_retry_is_1(self):
        self.assertEqual(p3s.MAX_TTS_TECHNICAL_RETRY, 1)

    def test_module_has_no_new_retry_gate_or_qa_functions(self):
        for name in ("evaluate_qa_for_audio", "run_tts_content_attempts", "call_qa_with_retry"):
            self.assertFalse(hasattr(p3s, name), msg=name)


if __name__ == "__main__":
    unittest.main()
