# ============================================================
# er003_test_b1_p5c_audio.py
# ER-003-B1-P5C: GCP漢字かな交じり入力検証のテスト
# ============================================================
# 実TTS呼び出しは行わない。入力読み込み・ハッシュ検証・marker置換の
# 静的QA・対象句チェックロジックを対象とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p5c_audio -v

import unittest

import er003_b1_p4_audio as p4
import er003_b1_p5c_audio as p5c


class LoadMarkedTextInputTests(unittest.TestCase):

    def test_real_file_loads_and_hash_matches(self):
        result = p5c.load_marked_text_input()
        self.assertEqual(result["sha256"], p5c.P4D_MARKED_TEXT_EXPECTED_SHA256)
        self.assertGreater(len(result["text"]), 0)

    def test_raises_on_hash_mismatch(self):
        with self.assertRaises(ValueError):
            p5c.load_marked_text_input(expected_sha256="0" * 64)

    def test_loaded_text_contains_kanji_not_hiragana_only(self):
        result = p5c.load_marked_text_input()
        self.assertIn("守備", result["text"])
        self.assertIn("目印", result["text"])


class LoadUsedFormsTests(unittest.TestCase):

    def test_returns_five_used_forms(self):
        used_forms = p5c.load_used_forms()
        self.assertEqual(len(used_forms), 5)
        used_form_strings = [uf["used_form"] for uf in used_forms]
        self.assertIn("shot on target", used_form_strings)
        self.assertIn("stoppage time", used_form_strings)


class VerifyMarkerReplacementTests(unittest.TestCase):

    def test_real_input_passes_all_checks(self):
        marked = p5c.load_marked_text_input()
        pattern_a_text = p4.load_pattern_a_text()
        used_forms = p5c.load_used_forms()
        result = p5c.verify_marker_replacement(marked["text"], pattern_a_text, used_forms)
        self.assertTrue(result["all_passed"], msg=result)
        self.assertTrue(result["reconstruction_matches_pattern_a"])
        self.assertTrue(result["used_form_residue_all_zero"])
        self.assertEqual(result["marker_count"], 5)
        self.assertTrue(result["not_hiragana_converted"])
        self.assertTrue(all(result["kanji_target_phrase_presence_in_source"].values()), msg=result)

    def test_fails_when_used_form_residue_present(self):
        marked = p5c.load_marked_text_input()
        pattern_a_text = p4.load_pattern_a_text()
        used_forms = p5c.load_used_forms()
        tampered = marked["text"].replace("目印", "shot on target", 1)
        result = p5c.verify_marker_replacement(tampered, pattern_a_text, used_forms)
        self.assertFalse(result["all_passed"])

    def test_fails_when_hiragana_converted(self):
        pattern_a_text = p4.load_pattern_a_text()
        used_forms = p5c.load_used_forms()
        # 漢字を含まない(全てひらがな)文字列を模す
        hiragana_only = "ぜんはんは" * 10
        result = p5c.verify_marker_replacement(hiragana_only, pattern_a_text, used_forms)
        self.assertFalse(result["not_hiragana_converted"])
        self.assertFalse(result["all_passed"])

    def test_fails_when_reconstruction_does_not_match_pattern_a(self):
        marked = p5c.load_marked_text_input()
        pattern_a_text = p4.load_pattern_a_text()
        used_forms = p5c.load_used_forms()
        tampered = marked["text"] + "余分な文字"
        result = p5c.verify_marker_replacement(tampered, pattern_a_text, used_forms)
        self.assertFalse(result["reconstruction_matches_pattern_a"])
        self.assertFalse(result["all_passed"])


class CheckKanjiTargetPhrasesTests(unittest.TestCase):

    def test_detects_all_phrases_when_present(self):
        # KANJI_TARGET_PHRASESには「目印という決断で」が既に1件「目印」を
        # 含むため、追加の4件と合わせて合計5件になるようにする。
        text = "".join(p5c.KANJI_TARGET_PHRASES) + "目印目印目印目印"
        result = p5c.check_kanji_target_phrases(text)
        for phrase in p5c.KANJI_TARGET_PHRASES:
            self.assertTrue(result[phrase], msg=phrase)
        self.assertEqual(result["目印_count"], 5)

    def test_missing_phrase_reported_absent(self):
        result = p5c.check_kanji_target_phrases("まったく関係のない文字列")
        self.assertFalse(result["何が起きる"])
        self.assertEqual(result["目印_count"], 0)

    def test_six_phrases_defined(self):
        self.assertEqual(len(p5c.KANJI_TARGET_PHRASES), 6)


if __name__ == "__main__":
    unittest.main()
