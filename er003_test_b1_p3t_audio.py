# ============================================================
# er003_test_b1_p3t_audio.py
# ER-003-B1-P3T: 日本語通し音声への英語Key Phrase差し込み検証のテスト
# ============================================================
# 実API・実TTSは一切行わない。すべて合成データ・既存成果物の読み込みの
# み。共有コード(er002_common/er002_gemini_client/er003_b1_p3r_audio/
# er003_b1_p3s_audio)は変更していないため、本ファイルは新規追加分
# (句読点挿入・無音検出・差し込み)だけに絞る。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3t_audio -v

import unittest

import numpy as np

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3s_audio as p3s
import er003_b1_p3t_audio as p3t


class SourceConstantsTests(unittest.TestCase):

    def test_integrated_sentence_contains_japanese_and_english(self):
        self.assertIn("枠内シュート", p3t.SOURCE_INTEGRATED_SENTENCE)
        self.assertIn("shot on target", p3t.SOURCE_INTEGRATED_SENTENCE)

    def test_japanese_full_sentence_has_no_english(self):
        self.assertNotIn("shot on target", p3t.SOURCE_JAPANESE_FULL_SENTENCE)
        self.assertIn("枠内シュートを記録できないまま", p3t.SOURCE_JAPANESE_FULL_SENTENCE)

    def test_japanese_full_sentence_is_grammatically_complete_removal(self):
        """英語Key Phraseを取り除いた形が、元の統合原稿の日本語部分と
        一致することを確認する(語句を勝手に変更していない)。"""
        without_english = p3t.SOURCE_INTEGRATED_SENTENCE.replace(
            "、" + p3t.SOURCE_ENGLISH_KEYWORD, "")
        self.assertEqual(without_english, p3t.SOURCE_JAPANESE_FULL_SENTENCE)

    def test_english_keyword_matches_p3s(self):
        self.assertEqual(p3t.SOURCE_ENGLISH_KEYWORD, p3s.DEFAULT_KEY_PHRASE)


class BuildTtsScriptTests(unittest.TestCase):

    def test_inserts_exactly_one_comma_at_insertion_point(self):
        script = p3t.build_tts_japanese_script()
        self.assertEqual(script, p3t.SOURCE_JAPANESE_FULL_SENTENCE.replace(
            "枠内シュートを記録できないまま", "枠内シュート、を記録できないまま"))

    def test_no_vocabulary_word_order_or_particle_change(self):
        """句読点1文字の追加以外、文字の並びが変わっていないことを
        文字数差分で確認する(語彙・語順・助詞の変更なし)。"""
        source = p3t.SOURCE_JAPANESE_FULL_SENTENCE
        script = p3t.build_tts_japanese_script(source)
        self.assertEqual(len(script), len(source) + 1)
        self.assertEqual(script.replace("、", ""), source.replace("、", ""))

    def test_raises_if_marker_not_found(self):
        with self.assertRaises(ValueError):
            p3t.build_tts_japanese_script("この文には挿入位置がありません。")

    def test_inserted_comma_matches_original_integrated_punctuation_position(self):
        """追加した読点の位置が、元の統合原稿で英語Key Phraseの直前に
        あった読点と同じ位置であることを確認する(恣意的な新規追加では
        ない)。"""
        script = p3t.build_tts_japanese_script()
        # 元の統合原稿: "...枠内シュート、shot on targetを..."
        # スクリプト:     "...枠内シュート、を..."
        self.assertIn("枠内シュート、を記録できないまま", script)
        self.assertIn("枠内シュート、shot on targetを記録できないまま", p3t.SOURCE_INTEGRATED_SENTENCE)


class FindPauseWindowTests(unittest.TestCase):

    def _make_signal(self, sample_rate=24000, speech_before_s=1.0, silence_s=0.3, speech_after_s=1.0,
                     speech_amplitude=0.3, noise_amplitude=0.3):
        rng = np.random.default_rng(42)
        before = rng.uniform(-speech_amplitude, speech_amplitude, int(sample_rate * speech_before_s))
        silence = rng.uniform(-0.001, 0.001, int(sample_rate * silence_s))
        after = rng.uniform(-noise_amplitude, noise_amplitude, int(sample_rate * speech_after_s))
        return np.concatenate([before, silence, after]).astype(np.float64), sample_rate

    def test_detects_silence_window_in_synthetic_signal(self):
        samples, sr = self._make_signal()
        result = p3t.find_pause_window(samples, sr)
        self.assertIsNotNone(result)
        # 無音区間はおよそ1.0秒付近から1.3秒付近にあるはず
        self.assertGreater(result["start_seconds"], 0.8)
        self.assertLess(result["end_seconds"], 1.5)
        self.assertGreater(result["duration_seconds"], 0.1)

    def test_center_sample_is_between_start_and_end(self):
        samples, sr = self._make_signal()
        result = p3t.find_pause_window(samples, sr)
        self.assertGreaterEqual(result["center_sample"], result["start_sample"])
        self.assertLessEqual(result["center_sample"], result["end_sample"])

    def test_returns_none_when_no_silence_present(self):
        rng = np.random.default_rng(1)
        samples = rng.uniform(-0.3, 0.3, 24000 * 2).astype(np.float64)
        result = p3t.find_pause_window(samples, 24000)
        self.assertIsNone(result)

    def test_excludes_leading_and_trailing_silence_by_default(self):
        """先頭・末尾の一定区間は探索対象から除外され、無音のまま始まる
        /終わる音声で誤検出しないことを確認する。"""
        sr = 24000
        rng = np.random.default_rng(7)
        leading_silence = np.zeros(int(sr * 0.1))
        speech = rng.uniform(-0.3, 0.3, int(sr * 1.0))
        trailing_silence = np.zeros(int(sr * 0.1))
        samples = np.concatenate([leading_silence, speech, trailing_silence]).astype(np.float64)
        result = p3t.find_pause_window(samples, sr, exclude_start_seconds=0.15, exclude_end_seconds=0.15)
        # exclude窓が0.15秒なのに対し先頭無音は0.1秒しかないため、除外
        # 範囲内で完結し候補として拾われないはず
        if result is not None:
            self.assertGreater(result["start_seconds"], 0.05)


class SpliceTests(unittest.TestCase):

    def test_splice_preserves_all_audio_content(self):
        sr = 24000
        ja = np.linspace(-0.5, 0.5, sr).astype(np.float64)
        en = np.full(sr // 4, 0.9, dtype=np.float64)
        pause_window = {"center_sample": sr // 2, "start_sample": sr // 2 - 100, "end_sample": sr // 2 + 100}
        result = p3t.splice_english_into_japanese(ja, en, pause_window, sr, boundary_pause_seconds=0.2)

        expected_len = len(ja) + len(en) + 2 * int(sr * 0.2)
        self.assertEqual(len(result), expected_len)

    def test_splice_order_is_ja_before_en_ja_after(self):
        sr = 24000
        ja_before_marker = np.full(1000, 0.1, dtype=np.float64)
        ja_after_marker = np.full(1000, 0.2, dtype=np.float64)
        ja = np.concatenate([ja_before_marker, ja_after_marker])
        en = np.full(500, 0.9, dtype=np.float64)
        pause_window = {"center_sample": 1000, "start_sample": 900, "end_sample": 1100}
        result = p3t.splice_english_into_japanese(ja, en, pause_window, sr, boundary_pause_seconds=0.0)

        self.assertTrue(np.all(result[:1000] == 0.1))
        self.assertTrue(np.all(result[1000:1500] == 0.9))
        self.assertTrue(np.all(result[1500:] == 0.2))

    def test_splice_inserts_boundary_pauses_of_requested_length(self):
        sr = 24000
        ja = np.full(2000, 0.1, dtype=np.float64)
        en = np.full(500, 0.9, dtype=np.float64)
        pause_window = {"center_sample": 1000, "start_sample": 900, "end_sample": 1100}
        result = p3t.splice_english_into_japanese(ja, en, pause_window, sr, boundary_pause_seconds=0.2)
        pause_len = int(sr * 0.2)
        # en直前・直後のpause_len分がゼロであることを確認
        self.assertTrue(np.all(result[1000:1000 + pause_len] == 0.0))
        self.assertTrue(np.all(result[1000 + pause_len + 500:1000 + pause_len + 500 + pause_len] == 0.0))

    def test_splice_does_not_trim_ja_before_or_after_content(self):
        """center分割点の前後でja音声そのものが削られていないことを
        確認する(枠内シュートの途中やをの直前音を削らない、という
        安全要件に対応)。"""
        sr = 24000
        ja = np.arange(2000, dtype=np.float64)
        en = np.zeros(100, dtype=np.float64)
        pause_window = {"center_sample": 1234, "start_sample": 1200, "end_sample": 1300}
        result = p3t.splice_english_into_japanese(ja, en, pause_window, sr, boundary_pause_seconds=0.0)
        np.testing.assert_array_equal(result[:1234], ja[:1234])
        np.testing.assert_array_equal(result[1234 + 100:], ja[1234:])


class ReuseIdentityTests(unittest.TestCase):

    def test_voice_and_paths_reused_from_p3r_p3s(self):
        self.assertEqual(p3t.VOICE_NAME, p3r.VOICE_NAME)
        self.assertEqual(p3t.PATTERN_A_SOURCE_PATH, p3s.PATTERN_A_SOURCE_PATH)
        self.assertIs(p3t.sha256_text, p3r.sha256_text)
        self.assertIs(p3t.build_style_prefix, p3r.build_style_prefix)
        self.assertIs(p3t.build_tts_prompt, p3r.build_tts_prompt)

    def test_join_pause_and_retry_match_p3s(self):
        self.assertEqual(p3t.JOIN_PAUSE_SECONDS, p3s.JOIN_PAUSE_SECONDS)
        self.assertEqual(p3t.MAX_TTS_TECHNICAL_RETRY, p3s.MAX_TTS_TECHNICAL_RETRY)

    def test_style_prefix_unchanged_from_common(self):
        self.assertEqual(p3t.build_style_prefix(), common.build_style_prefix())

    def test_module_has_no_new_retry_gate_or_qa_functions(self):
        for name in ("evaluate_qa_for_audio", "run_tts_content_attempts", "call_qa_with_retry"):
            self.assertFalse(hasattr(p3t, name), msg=name)


if __name__ == "__main__":
    unittest.main()
