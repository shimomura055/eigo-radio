# ============================================================
# er003_test_b1_p3u_audio.py
# ER-003-B1-P3U: 正確な語句境界への英語Key Phrase差し込み再検証のテスト
# ============================================================
# 実API・実TTS・実Azure STT呼び出しは一切行わない。境界特定ロジックは
# 実際にAzure STTから得られた単語タイムスタンプ列(er003_output/b1_p3t/
# A01/raw/ja_full_sentence.wavを解析した結果をハードコード化したもの)
# を使い、無音長を一切使わずに正しい境界(5.35秒)を再現できることを
# 確認する。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3u_audio -v

import unittest

import numpy as np

import er003_b1_p3t_audio as p3t
import er003_b1_p3u_audio as p3u

# ER-003-B1-P3TのA01 ja_full_sentence.wavに対する実際のAzure STT
# (NBest[0].Words、ja-JP、Detailed、単語レベルタイムスタンプ)結果を
# そのまま書き起こしたもの。オフセット/長さの単位はAzureのtick
# (100ナノ秒単位)。
_REAL_AZURE_WORDS_TICKS = [
    ("前", 2300000, 3200000), ("半", 5500000, 2800000), ("は", 8300000, 3200000),
    ("激", 11500000, 1600000), ("し", 13100000, 1200000), ("い", 14300000, 800000),
    ("接", 15100000, 2400000), ("触", 17500000, 1600000), ("と", 19100000, 1200000),
    ("緊", 20300000, 2400000), ("張", 22700000, 1600000), ("が", 24300000, 1600000),
    ("続", 25900000, 2400000), ("き", 28300000, 3600000), ("今", 32700000, 1600000),
    ("日", 34300000, 800000), ("チ", 35100000, 800000), ("ー", 35900000, 2000000),
    ("ム", 37900000, 1200000), ("と", 39100000, 1200000), ("も", 40300000, 2400000),
    ("枠", 42700000, 4400000), ("内", 47100000, 2000000), ("シ", 49100000, 800000),
    ("ュ", 49900000, 800000), ("ー", 50700000, 2000000), ("ト", 52700000, 800000),
    ("を", 53500000, 800000), ("記", 54300000, 1200000), ("録", 55500000, 2000000),
    ("で", 57500000, 800000), ("き", 58300000, 1200000), ("な", 59500000, 800000),
    ("い", 60300000, 800000), ("ま", 61100000, 1200000), ("ま", 62300000, 2000000),
    ("静", 64300000, 3200000), ("か", 67500000, 1200000), ("な", 68700000, 800000),
    ("均", 69500000, 2400000), ("衡", 71900000, 2400000), ("が", 74300000, 2400000),
    ("保", 76700000, 1200000), ("た", 77900000, 800000), ("れ", 78700000, 1200000),
    ("ま", 79900000, 1200000), ("す", 81100000, 1200000),
]


def _words_from_ticks(entries):
    return [
        {
            "word": w,
            "start_seconds": offset / 10_000_000,
            "end_seconds": (offset + duration) / 10_000_000,
            "confidence": 0.9,
        }
        for w, offset, duration in entries
    ]


class FindKeywordBoundaryRealDataTests(unittest.TestCase):

    def test_boundary_matches_real_azure_stt_result(self):
        words = _words_from_ticks(_REAL_AZURE_WORDS_TICKS)
        result, error = p3u.find_keyword_boundary(words)
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["shuuto_end_seconds"], 5.35, places=4)
        self.assertAlmostEqual(result["wo_start_seconds"], 5.35, places=4)
        self.assertAlmostEqual(result["boundary_seconds"], 5.35, places=4)
        self.assertAlmostEqual(result["gap_seconds"], 0.0, places=4)
        self.assertAlmostEqual(result["shuuto_start_seconds"], 4.91, places=4)

    def test_boundary_differs_from_previous_wrong_p3t_cut(self):
        """前回P3Tが採用した3.16秒(最長無音の中心)とは全く異なる位置
        (約2.19秒の差)であることを確認する。"""
        words = _words_from_ticks(_REAL_AZURE_WORDS_TICKS)
        result, _ = p3u.find_keyword_boundary(words)
        previous_wrong_cut = 3.16
        diff = result["boundary_seconds"] - previous_wrong_cut
        self.assertGreater(diff, 2.0)
        self.assertLess(diff, 2.3)


class FindKeywordBoundaryStopConditionTests(unittest.TestCase):

    def test_returns_none_when_wo_appears_zero_times(self):
        entries = [e for e in _REAL_AZURE_WORDS_TICKS if e[0] != "を"]
        words = _words_from_ticks(entries)
        result, error = p3u.find_keyword_boundary(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_wo_appears_multiple_times(self):
        entries = list(_REAL_AZURE_WORDS_TICKS) + [("を", 90000000, 800000)]
        words = _words_from_ticks(entries)
        result, error = p3u.find_keyword_boundary(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_preceding_word_is_not_shuuto(self):
        entries = [
            ("枠", 42700000, 4400000), ("内", 47100000, 2000000),
            ("を", 53500000, 800000), ("記", 54300000, 1200000),
        ]
        words = _words_from_ticks(entries)
        result, error = p3u.find_keyword_boundary(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_shuuto_sequence_broken(self):
        entries = [
            ("シ", 49100000, 800000), ("ー", 50700000, 2000000),  # ュが欠落
            ("ト", 52700000, 800000), ("を", 53500000, 800000),
        ]
        words = _words_from_ticks(entries)
        result, error = p3u.find_keyword_boundary(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_on_empty_word_list(self):
        result, error = p3u.find_keyword_boundary([])
        self.assertIsNone(result)
        self.assertIsNotNone(error)


class FindSpeechBoundsTests(unittest.TestCase):

    def _make_signal(self, sr=24000, lead_s=0.16, speech_s=1.07, trail_s=2.46):
        rng = np.random.default_rng(3)
        lead = np.zeros(int(sr * lead_s))
        speech = rng.uniform(-0.3, 0.3, int(sr * speech_s))
        trail = np.zeros(int(sr * trail_s))
        return np.concatenate([lead, speech, trail]).astype(np.float64), sr, len(lead), len(lead) + len(speech)

    def test_detects_speech_region_matching_known_en_keyword_shape(self):
        samples, sr, expected_start, expected_end = self._make_signal()
        bounds = p3u.find_speech_bounds(samples, sr)
        self.assertIsNotNone(bounds)
        start, end = bounds
        self.assertAlmostEqual(start / sr, expected_start / sr, delta=0.03)
        self.assertAlmostEqual(end / sr, expected_end / sr, delta=0.03)

    def test_returns_none_for_all_silence(self):
        samples = np.zeros(24000, dtype=np.float64)
        self.assertIsNone(p3u.find_speech_bounds(samples, 24000))


class TrimEnglishKeywordSilenceTests(unittest.TestCase):

    def test_trim_retains_safety_margin_and_all_speech(self):
        sr = 24000
        rng = np.random.default_rng(9)
        lead = np.zeros(int(sr * 0.16))
        speech = rng.uniform(-0.3, 0.3, int(sr * 1.07))
        trail = np.zeros(int(sr * 2.46))
        samples = np.concatenate([lead, speech, trail]).astype(np.float64)

        trimmed, info = p3u.trim_english_keyword_silence(samples, sr, safety_margin_seconds=0.08)
        self.assertIsNotNone(trimmed)
        self.assertAlmostEqual(info["leading_margin_retained_seconds"], 0.08, delta=0.005)
        self.assertAlmostEqual(info["trailing_margin_retained_seconds"], 0.08, delta=0.005)
        # トリム後の長さは speech + 2*margin 前後
        expected_len_s = 1.07 + 2 * 0.08
        self.assertAlmostEqual(info["trimmed_duration_seconds"], expected_len_s, delta=0.03)

    def test_trim_never_cuts_into_speech(self):
        """マージンがraw無音より大きい極端なケースでも、発話区間自体は
        必ず残る(0側にクランプされる)ことを確認する。"""
        sr = 24000
        rng = np.random.default_rng(5)
        lead = np.zeros(int(sr * 0.02))
        speech = rng.uniform(-0.3, 0.3, int(sr * 0.5))
        trail = np.zeros(int(sr * 0.02))
        samples = np.concatenate([lead, speech, trail]).astype(np.float64)

        trimmed, info = p3u.trim_english_keyword_silence(samples, sr, safety_margin_seconds=0.08)
        self.assertGreaterEqual(len(trimmed), len(speech))

    def test_returns_none_for_all_silence_input(self):
        samples = np.zeros(24000, dtype=np.float64)
        trimmed, info = p3u.trim_english_keyword_silence(samples, 24000)
        self.assertIsNone(trimmed)
        self.assertIsNone(info)


class SplitJapaneseAtBoundaryTests(unittest.TestCase):

    def test_splits_at_exact_sample_position(self):
        sr = 24000
        samples = np.arange(sr * 2, dtype=np.float64)
        before, after = p3u.split_japanese_at_boundary(samples, sr, boundary_seconds=1.0)
        self.assertEqual(len(before), sr)
        self.assertEqual(len(after), sr)
        np.testing.assert_array_equal(before, samples[:sr])
        np.testing.assert_array_equal(after, samples[sr:])

    def test_no_content_lost_across_split(self):
        sr = 24000
        samples = np.arange(sr, dtype=np.float64)
        before, after = p3u.split_japanese_at_boundary(samples, sr, boundary_seconds=0.35)
        self.assertEqual(len(before) + len(after), len(samples))

    def test_clamps_boundary_within_bounds(self):
        sr = 24000
        samples = np.arange(1000, dtype=np.float64)
        before, after = p3u.split_japanese_at_boundary(samples, sr, boundary_seconds=999.0)
        self.assertEqual(len(before), 1000)
        self.assertEqual(len(after), 0)


class JoinWithBoundaryPausesTests(unittest.TestCase):

    def test_join_order_and_pause_length(self):
        sr = 24000
        ja_before = np.full(1000, 0.1, dtype=np.float64)
        en = np.full(500, 0.9, dtype=np.float64)
        ja_after = np.full(1000, 0.2, dtype=np.float64)
        result = p3u.join_with_boundary_pauses(ja_before, en, ja_after, sr, boundary_pause_seconds=0.12)

        pause_len = int(round(sr * 0.12))
        self.assertTrue(np.all(result[:1000] == 0.1))
        self.assertTrue(np.all(result[1000:1000 + pause_len] == 0.0))
        self.assertTrue(np.all(result[1000 + pause_len:1000 + pause_len + 500] == 0.9))
        self.assertTrue(np.all(result[1000 + pause_len + 500:1000 + pause_len + 500 + pause_len] == 0.0))
        self.assertTrue(np.all(result[1000 + 2 * pause_len + 500:] == 0.2))

    def test_total_length_matches_sum_of_parts(self):
        sr = 24000
        ja_before = np.zeros(2000, dtype=np.float64)
        en = np.zeros(300, dtype=np.float64)
        ja_after = np.zeros(1500, dtype=np.float64)
        result = p3u.join_with_boundary_pauses(ja_before, en, ja_after, sr, boundary_pause_seconds=0.12)
        pause_len = int(round(sr * 0.12))
        self.assertEqual(len(result), 2000 + 300 + 1500 + 2 * pause_len)

    def test_uses_default_pause_of_012_seconds_distinct_from_p3s_p3t(self):
        self.assertEqual(p3u.BOUNDARY_PAUSE_SECONDS, 0.12)
        self.assertNotEqual(p3u.BOUNDARY_PAUSE_SECONDS, p3t.JOIN_PAUSE_SECONDS)


class ReuseIdentityTests(unittest.TestCase):

    def test_source_constants_reused_from_p3t(self):
        self.assertEqual(p3u.SOURCE_JAPANESE_FULL_SENTENCE, p3t.SOURCE_JAPANESE_FULL_SENTENCE)
        self.assertEqual(p3u.SOURCE_ENGLISH_KEYWORD, p3t.SOURCE_ENGLISH_KEYWORD)

    def test_existing_audio_paths_point_to_p3t_output(self):
        self.assertIn("b1_p3t", p3u.EXISTING_JA_PATH)
        self.assertIn("b1_p3t", p3u.EXISTING_EN_PATH)
        self.assertIn("raw", p3u.EXISTING_JA_PATH)

    def test_module_has_no_new_tts_call_functions(self):
        for name in ("make_tts_call_fn", "generate_content", "_call_tts_with_retry"):
            self.assertFalse(hasattr(p3u, name), msg=name)

    def test_module_does_not_use_pause_window_heuristic(self):
        """P3Uの核心要件: find_pause_window(最長無音ヒューリスティック)
        を境界特定の根拠として一切import/再エクスポートしていないこと。"""
        self.assertFalse(hasattr(p3u, "find_pause_window"))


if __name__ == "__main__":
    unittest.main()
