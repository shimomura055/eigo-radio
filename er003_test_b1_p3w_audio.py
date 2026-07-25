# ============================================================
# er003_test_b1_p3w_audio.py
# ER-003-B1-P3W: MFAマーカー置換・短尺検証のテスト(TTSスクリプト構築・
# marker区間削除ロジックのみ。MFA自体は外部ツールのため、この単体テスト
# では起動しない)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3w_audio -v

import unittest

import numpy as np

import er003_b1_p3r_audio as p3r
import er003_b1_p3t_audio as p3t
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w


class SourceConstantsTests(unittest.TestCase):

    def test_source_constants_reused_from_p3t(self):
        self.assertEqual(p3w.SOURCE_INTEGRATED_SENTENCE, p3t.SOURCE_INTEGRATED_SENTENCE)
        self.assertEqual(p3w.SOURCE_JAPANESE_FULL_SENTENCE, p3t.SOURCE_JAPANESE_FULL_SENTENCE)
        self.assertEqual(p3w.SOURCE_ENGLISH_KEYWORD, p3t.SOURCE_ENGLISH_KEYWORD)

    def test_voice_reused_from_p3r(self):
        self.assertEqual(p3w.VOICE_NAME, p3r.VOICE_NAME)

    def test_boundary_pause_reused_from_p3u(self):
        self.assertEqual(p3w.BOUNDARY_PAUSE_SECONDS, p3u.BOUNDARY_PAUSE_SECONDS)
        self.assertEqual(p3w.BOUNDARY_PAUSE_SECONDS, 0.12)


class BuildTtsMarkerScriptTests(unittest.TestCase):

    def test_inserts_marker_token_at_correct_position(self):
        script = p3w.build_tts_marker_script()
        self.assertIn("枠内シュート、キーワード挿入位置を記録できないまま", script)

    def test_marker_token_appears_exactly_once(self):
        script = p3w.build_tts_marker_script()
        self.assertEqual(script.count(p3w.MARKER_TOKEN), 1)

    def test_no_vocabulary_or_word_order_change_besides_marker(self):
        """マーカー語追加以外、承認済み原稿の語彙・語順が変わっていない
        ことを確認する(承認済み原稿の語句・意味の変更は禁止)。"""
        source = p3w.SOURCE_JAPANESE_FULL_SENTENCE
        script = p3w.build_tts_marker_script(source)
        without_marker = script.replace(f"、{p3w.MARKER_TOKEN}", "")
        self.assertEqual(without_marker, source)

    def test_raises_if_marker_position_not_found(self):
        with self.assertRaises(ValueError):
            p3w.build_tts_marker_script("この文には挿入位置がありません。")

    def test_marker_token_is_speakable_japanese_not_symbol(self):
        """マーカーがGemini TTSに読み上げ可能な日本語語句であり、記号や
        タグではないことを確認する(P3Vで確認した通りマークアップは
        機能しないため)。"""
        self.assertNotIn("<", p3w.MARKER_TOKEN)
        self.assertNotIn(">", p3w.MARKER_TOKEN)
        self.assertTrue(all(ord(c) > 127 for c in p3w.MARKER_TOKEN))


class RemoveMarkerSpanTests(unittest.TestCase):

    def test_removes_marker_region_completely(self):
        sr = 24000
        samples = np.arange(sr * 2, dtype=np.float64)  # 2秒分、値=サンプル番号
        before, after = p3w.remove_marker_span(samples, sr, marker_start_seconds=1.0, marker_end_seconds=1.5)
        np.testing.assert_array_equal(before, samples[:sr])
        np.testing.assert_array_equal(after, samples[int(sr * 1.5):])

    def test_before_and_after_do_not_contain_marker_content(self):
        sr = 24000
        marker_value = 999.0
        before_part = np.zeros(sr, dtype=np.float64)
        marker_part = np.full(int(sr * 0.3), marker_value, dtype=np.float64)
        after_part = np.ones(sr, dtype=np.float64)
        samples = np.concatenate([before_part, marker_part, after_part])

        before, after = p3w.remove_marker_span(samples, sr, marker_start_seconds=1.0, marker_end_seconds=1.3)
        self.assertNotIn(marker_value, before)
        self.assertNotIn(marker_value, after)

    def test_raises_when_end_not_after_start(self):
        sr = 24000
        samples = np.zeros(sr, dtype=np.float64)
        with self.assertRaises(ValueError):
            p3w.remove_marker_span(samples, sr, marker_start_seconds=1.0, marker_end_seconds=1.0)
        with self.assertRaises(ValueError):
            p3w.remove_marker_span(samples, sr, marker_start_seconds=1.5, marker_end_seconds=1.0)

    def test_clamps_within_bounds(self):
        sr = 24000
        samples = np.arange(1000, dtype=np.float64)
        before, after = p3w.remove_marker_span(samples, sr, marker_start_seconds=999.0, marker_end_seconds=9999.0)
        self.assertEqual(len(before), 1000)
        self.assertEqual(len(after), 0)


class ParseTextgridWordsTierTests(unittest.TestCase):

    _SAMPLE_TEXTGRID = '''File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0
xmax = 2.0
tiers? <exists>
size = 2
item []:
    item [1]:
        class = "IntervalTier"
        name = "words"
        xmin = 0
        xmax = 2.0
        intervals: size = 3
        intervals [1]:
            xmin = 0.0
            xmax = 0.5
            text = "abc"
        intervals [2]:
            xmin = 0.5
            xmax = 1.0
            text = ""
        intervals [3]:
            xmin = 1.0
            xmax = 2.0
            text = "def"
    item [2]:
        class = "IntervalTier"
        name = "phones"
        xmin = 0
        xmax = 2.0
        intervals: size = 1
        intervals [1]:
            xmin = 0.0
            xmax = 2.0
            text = "should_not_appear"
'''

    def setUp(self):
        import tempfile
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".TextGrid", delete=False, encoding="utf-8")
        self._tmp.write(self._SAMPLE_TEXTGRID)
        self._tmp.close()

    def tearDown(self):
        import os
        os.unlink(self._tmp.name)

    def test_parses_words_tier_intervals_in_order(self):
        words = p3w.parse_textgrid_words_tier(self._tmp.name)
        self.assertEqual([w["text"] for w in words], ["abc", "", "def"])
        self.assertEqual(words[0]["xmin"], 0.0)
        self.assertEqual(words[0]["xmax"], 0.5)
        self.assertEqual(words[2]["xmin"], 1.0)
        self.assertEqual(words[2]["xmax"], 2.0)

    def test_does_not_pick_up_phones_tier_content(self):
        words = p3w.parse_textgrid_words_tier(self._tmp.name)
        texts = [w["text"] for w in words]
        self.assertNotIn("should_not_appear", texts)

    def test_raises_if_words_tier_missing(self):
        import tempfile
        import os
        content = self._SAMPLE_TEXTGRID.replace('name = "words"', 'name = "other"')
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".TextGrid", delete=False, encoding="utf-8")
        tmp.write(content)
        tmp.close()
        try:
            with self.assertRaises(ValueError):
                p3w.parse_textgrid_words_tier(tmp.name)
        finally:
            os.unlink(tmp.name)


class ParseRealSmokeTestTextgridTests(unittest.TestCase):
    """MFAスモークテストで実際に生成されたTextGridがあれば、それを使って
    パーサーを検証する(存在しない場合はスキップ)。"""

    _PATH = "mfa_tool/smoke_test_output/ja_full_sentence.TextGrid"

    def setUp(self):
        import os
        if not os.path.exists(self._PATH):
            self.skipTest("MFAスモークテスト出力が存在しないためスキップ")

    def test_word_order_matches_source_sentence(self):
        words = p3w.parse_textgrid_words_tier(self._PATH)
        texts = [w["text"] for w in words if w["text"] != ""]
        self.assertEqual(texts, [
            "前半", "は", "激しい", "接触", "と", "緊張", "が", "続き",
            "両", "チーム", "とも", "枠内", "シュート", "を", "記録",
            "できない", "まま", "静か", "な", "均衡", "が", "保たれます",
        ])

    def test_shuuto_wo_boundary_is_contiguous(self):
        words = p3w.parse_textgrid_words_tier(self._PATH)
        shuuto = next(w for w in words if w["text"] == "シュート")
        wo = next(w for w in words if w["text"] == "を")
        self.assertEqual(shuuto["xmax"], wo["xmin"])


class FindMarkerSpanTests(unittest.TestCase):
    """実機のMFA(japanese_mfa tokenizer)は、マーカー語「キーワード挿入
    位置」を辞書内の3語("キーワード"/"挿入"/"位置")へ分割して認識する
    ことを実際のTextGrid出力で確認済み。find_marker_spanはデフォルトで
    この3語の連続を探す(p3w.MARKER_TOKEN_SEQUENCE)。"""

    def _words(self, marker_tokens=None):
        marker_tokens = marker_tokens if marker_tokens is not None else p3w.MARKER_TOKEN_SEQUENCE
        words = [
            {"xmin": 0.0, "xmax": 0.5, "text": "枠内"},
            {"xmin": 0.5, "xmax": 1.0, "text": "シュート"},
        ]
        t = 1.0
        for tok in marker_tokens:
            words.append({"xmin": t, "xmax": t + 0.3, "text": tok})
            t += 0.3
        words.append({"xmin": t, "xmax": t + 0.2, "text": "を"})
        words.append({"xmin": t + 0.2, "xmax": t + 0.7, "text": "記録"})
        return words

    def test_finds_marker_span_with_correct_neighbors(self):
        result, error = p3w.find_marker_span(self._words())
        self.assertIsNone(error)
        self.assertEqual(result["marker_token_count"], 3)
        self.assertEqual(result["marker_tokens"], list(p3w.MARKER_TOKEN_SEQUENCE))
        self.assertEqual(result["marker_start_seconds"], 1.0)
        self.assertAlmostEqual(result["marker_end_seconds"], 1.9)
        self.assertEqual(result["preceding_token"], "シュート")
        self.assertEqual(result["following_token"], "を")

    def test_tolerates_silence_gap_between_marker_subtokens(self):
        """実機の2回目のTTS生成では「キーワード」と「挿入」の間に短い
        間(無音interval)が入ったが、それでも一続きのマーカーとして
        認識できることを確認する(無音の長さは判定根拠にせず、語順の
        一致のみを見る)。"""
        words = [
            {"xmin": 5.36, "xmax": 5.79, "text": "シュート"},
            {"xmin": 5.79, "xmax": 6.2, "text": "キーワード"},
            {"xmin": 6.2, "xmax": 6.36, "text": ""},
            {"xmin": 6.36, "xmax": 6.58, "text": "挿入"},
            {"xmin": 6.58, "xmax": 6.71, "text": "位置"},
            {"xmin": 6.71, "xmax": 6.82, "text": "を"},
        ]
        result, error = p3w.find_marker_span(words)
        self.assertIsNone(error)
        self.assertEqual(result["marker_start_seconds"], 5.79)
        self.assertEqual(result["marker_end_seconds"], 6.71)
        self.assertEqual(result["preceding_token"], "シュート")
        self.assertEqual(result["following_token"], "を")

    def test_returns_none_when_marker_not_found(self):
        words = self._words()
        for w in words:
            if w["text"] in p3w.MARKER_TOKEN_SEQUENCE:
                w["text"] = "別の語"
        result, error = p3w.find_marker_span(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_marker_sequence_appears_multiple_times(self):
        words = self._words()
        words.extend(self._words()[2:5])  # マーカー3語をもう一度末尾に追加
        result, error = p3w.find_marker_span(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_preceding_token_is_not_shuuto(self):
        words = self._words()
        words[1]["text"] = "別の語"  # マーカー直前(index 1 = "シュート")を差し替え
        result, error = p3w.find_marker_span(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_following_token_is_not_wo(self):
        words = self._words()
        wo_idx = next(i for i, w in enumerate(words) if w["text"] == "を")
        words[wo_idx]["text"] = "別の語"
        result, error = p3w.find_marker_span(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_returns_none_when_marker_at_edge_of_utterance(self):
        words = self._words()[2:]  # マーカーが先頭(直前語なし)
        result, error = p3w.find_marker_span(words)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_handles_single_token_marker_span(self):
        """カスタムのmarker_tokensとして単一tokenを渡した場合も動作する
        ことを確認する(将来別のマーカー語を使う場合への一般性)。"""
        words = [
            {"xmin": 0.0, "xmax": 0.5, "text": "シュート"},
            {"xmin": 0.5, "xmax": 0.9, "text": "テスト"},
            {"xmin": 0.9, "xmax": 1.1, "text": "を"},
        ]
        result, error = p3w.find_marker_span(words, marker_tokens=("テスト",))
        self.assertIsNone(error)
        self.assertEqual(result["marker_token_count"], 1)
        self.assertEqual(result["marker_start_seconds"], 0.5)
        self.assertEqual(result["marker_end_seconds"], 0.9)


class ReuseIdentityTests(unittest.TestCase):

    def test_uses_existing_trimmed_english_audio_path(self):
        self.assertIn("b1_p3u", p3w.EXISTING_EN_TRIMMED_PATH)
        self.assertIn("en_shot_on_target_trimmed.wav", p3w.EXISTING_EN_TRIMMED_PATH)

    def test_smoke_test_target_is_existing_p3t_audio(self):
        self.assertEqual(p3w.SMOKE_TEST_WAV_PATH, "er003_output/b1_p3t/A01/raw/ja_full_sentence.wav")
        self.assertEqual(p3w.SMOKE_TEST_TEXT, p3t.SOURCE_JAPANESE_FULL_SENTENCE)

    def test_module_has_no_pause_window_or_asr_functions(self):
        """最長無音・ASR境界推定への逆戻りが実装に含まれていないことを
        確認する。"""
        for name in ("find_pause_window", "get_word_timestamps_via_azure_stt", "find_keyword_boundary"):
            self.assertFalse(hasattr(p3w, name), msg=name)


if __name__ == "__main__":
    unittest.main()
