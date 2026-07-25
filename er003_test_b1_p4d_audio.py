# ============================================================
# er003_test_b1_p4d_audio.py
# ER-003-B1-P4D: 全文ひらがな読み正規化のテスト
# ============================================================
# marker置換・カタカナ→ひらがな変換・静的検証ロジックを対象とする。
# tokenize自体は隔離MFA環境(SudachiPy導入済み)への実サブプロセス呼び
# 出しを1回だけ行う統合テストを含む(TTS・Azure STTは呼ばない)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p4d_audio -v

import json
import tempfile
import unittest

import er003_b1_p4d_audio as p4d


def _real_pattern_a_and_used_forms():
    with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
        data = json.load(f)
    pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
    return pattern_a["text"], pattern_a["used_forms"]


class BuildMarkerReplacedSourceTests(unittest.TestCase):

    def test_real_pattern_a_produces_five_markers_zero_residue(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        result = p4d.build_marker_replaced_source(text, used_forms)
        self.assertTrue(result["marker_count_is_five"])
        self.assertTrue(result["used_form_residue_all_zero"])
        self.assertEqual(result["marker_count"], 5)

    def test_marked_text_reversible_in_appearance_order(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        result = p4d.build_marker_replaced_source(text, used_forms)
        reconstructed = result["marked_text"]
        for e in result["marker_map"]:
            reconstructed = reconstructed.replace(p4d.MARKER_TOKEN, e["used_form"], 1)
        self.assertEqual(reconstructed, text)

    def test_marked_text_length_reflects_replacement(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        result = p4d.build_marker_replaced_source(text, used_forms)
        total_used_form_chars = sum(len(uf["used_form"]) for uf in used_forms)
        expected_len = len(text) - total_used_form_chars + 5 * len(p4d.MARKER_TOKEN)
        self.assertEqual(len(result["marked_text"]), expected_len)

    def test_raises_on_missing_used_form(self):
        with self.assertRaises(ValueError):
            p4d.build_marker_replaced_source("何もない文章です。", [{"used_form": "shot on target", "canonical_english": "x", "rank": 1, "japanese_gloss_used": "x"}])


class KatakanaToHiraganaTests(unittest.TestCase):

    def test_basic_katakana_conversion(self):
        self.assertEqual(p4d.katakana_to_hiragana("メジルシ"), "めじるし")

    def test_long_vowel_mark_preserved(self):
        self.assertEqual(p4d.katakana_to_hiragana("リード"), "りーど")

    def test_non_katakana_passthrough(self):
        self.assertEqual(p4d.katakana_to_hiragana("、。―"), "、。―")

    def test_mixed_string(self):
        self.assertEqual(p4d.katakana_to_hiragana("ゼンハン"), "ぜんはん")


class BuildReadingMapTests(unittest.TestCase):

    def test_symbol_token_keeps_surface_not_reading_form(self):
        # 実機で確認済み: SudachiPyは「―」のreading_formに「キゴウ」
        # (実際の読みではない汎用ラベル)を返す。品詞が補助記号の場合は
        # reading_formを使わずsurfaceをそのまま保持しなければならない。
        morphemes = [{"surface": "―", "dictionary_form": "―", "reading_form": "キゴウ",
                      "part_of_speech": ["補助記号", "一般", "*", "*", "*", "*"]}]
        reading_map = p4d.build_reading_map(morphemes)
        self.assertEqual(reading_map[0]["hiragana_form"], "―")
        self.assertTrue(reading_map[0]["is_symbol"])

    def test_word_token_converts_reading_form(self):
        morphemes = [{"surface": "前半", "dictionary_form": "前半", "reading_form": "ゼンハン",
                      "part_of_speech": ["名詞", "普通名詞", "副詞可能", "*", "*", "*"]}]
        reading_map = p4d.build_reading_map(morphemes)
        self.assertEqual(reading_map[0]["hiragana_form"], "ぜんはん")
        self.assertFalse(reading_map[0]["is_symbol"])

    def test_marker_token_flagged_and_converted(self):
        morphemes = [{"surface": "目印", "dictionary_form": "目印", "reading_form": "メジルシ",
                      "part_of_speech": ["名詞", "普通名詞", "一般", "*", "*", "*"]}]
        reading_map = p4d.build_reading_map(morphemes)
        self.assertTrue(reading_map[0]["is_marker"])
        self.assertEqual(reading_map[0]["hiragana_form"], p4d.MARKER_HIRAGANA)

    def test_conjugated_verb_uses_surface_reading_not_dictionary_form_reading(self):
        # 「固め」(連用形)のreading_formはカタメ。辞書形「固める」の
        # 読み(カタメル)を使ってはいけない(「しゅびをかためる」化の
        # 原因になった問題の再発防止)。
        morphemes = [{"surface": "固め", "dictionary_form": "固める", "reading_form": "カタメ",
                      "part_of_speech": ["動詞", "一般", "*", "*", "下一段-マ行", "連用形-一般"]}]
        reading_map = p4d.build_reading_map(morphemes)
        self.assertEqual(reading_map[0]["hiragana_form"], "かため")

    def test_source_position_tracks_character_offset(self):
        morphemes = [
            {"surface": "前半", "dictionary_form": "前半", "reading_form": "ゼンハン", "part_of_speech": ["名詞"] * 6},
            {"surface": "は", "dictionary_form": "は", "reading_form": "ハ", "part_of_speech": ["助詞"] * 6},
        ]
        reading_map = p4d.build_reading_map(morphemes)
        self.assertEqual(reading_map[0]["source_position"], 0)
        self.assertEqual(reading_map[1]["source_position"], 2)

    def test_build_full_hiragana_script_no_added_whitespace(self):
        morphemes = [
            {"surface": "前半", "dictionary_form": "前半", "reading_form": "ゼンハン", "part_of_speech": ["名詞"] * 6},
            {"surface": "は", "dictionary_form": "は", "reading_form": "ハ", "part_of_speech": ["助詞"] * 6},
        ]
        reading_map = p4d.build_reading_map(morphemes)
        script = p4d.build_full_hiragana_script(reading_map)
        self.assertEqual(script, "ぜんはんは")
        self.assertNotIn(" ", script)


class VerifyReadingConversionTests(unittest.TestCase):

    def _valid_reading_map(self):
        morphemes = [
            {"surface": "前半", "dictionary_form": "前半", "reading_form": "ゼンハン", "part_of_speech": ["名詞"] * 6},
            {"surface": "目印", "dictionary_form": "目印", "reading_form": "メジルシ", "part_of_speech": ["名詞"] * 6},
            {"surface": "。", "dictionary_form": "。", "reading_form": "。", "part_of_speech": ["補助記号", "句点", "*", "*", "*", "*"]},
        ] * 5  # 5回出現するmarkerを模す(marker_hiragana_count_is_fiveを満たすため)
        return p4d.build_reading_map(morphemes)

    def test_passes_on_valid_conversion(self):
        reading_map = self._valid_reading_map()
        marked_text = "".join(e["surface"] for e in reading_map)
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertTrue(result["all_passed"], msg=result)

    def test_fails_on_unconvertible_token(self):
        reading_map = self._valid_reading_map()
        reading_map[0]["hiragana_form"] = None
        marked_text = "".join(e["surface"] for e in reading_map)
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertFalse(result["all_passed"])
        self.assertEqual(len(result["unconvertible_tokens"]), 1)

    def test_fails_on_residual_kanji(self):
        reading_map = self._valid_reading_map()
        reading_map[0]["hiragana_form"] = "前半"  # 変換漏れを模す
        marked_text = "".join(e["surface"] for e in reading_map)
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertFalse(result["kanji_count_is_zero"])
        self.assertFalse(result["all_passed"])

    def test_fails_on_residual_katakana_letter(self):
        reading_map = self._valid_reading_map()
        reading_map[0]["hiragana_form"] = "ゼンハン"  # ひらがな化されていない
        marked_text = "".join(e["surface"] for e in reading_map)
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertFalse(result["katakana_letter_count_is_zero"])
        self.assertFalse(result["all_passed"])

    def test_long_vowel_mark_does_not_count_as_residual_katakana(self):
        reading_map = self._valid_reading_map()
        reading_map[0]["hiragana_form"] = "りーど"
        marked_text = "".join(e["surface"] for e in reading_map)
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertTrue(result["katakana_letter_count_is_zero"])

    def test_fails_when_marker_count_not_five(self):
        reading_map = self._valid_reading_map()[:3]  # markerが1回だけになる
        marked_text = "".join(e["surface"] for e in reading_map)
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertFalse(result["marker_hiragana_count_is_five"])
        self.assertFalse(result["all_passed"])

    def test_fails_on_reconstruction_mismatch(self):
        reading_map = self._valid_reading_map()
        marked_text = "".join(e["surface"] for e in reading_map) + "余分な文字"
        script = p4d.build_full_hiragana_script(reading_map)
        result = p4d.verify_reading_conversion(marked_text, reading_map, script)
        self.assertFalse(result["reconstruction_matches"])
        self.assertFalse(result["all_passed"])


class CheckFullTextContentTests(unittest.TestCase):

    def test_passes_on_close_match_with_marker_present_five_times(self):
        marked = "前半は目印です。目印です。目印です。目印です。目印です。"
        recognized = "前半は目印です。目印です。目印です。目印です。目印です。"
        result = p4d.check_full_text_content(recognized, marked)
        self.assertTrue(result["is_japanese"])
        self.assertTrue(result["marker_occurrence_total_is_five"])
        self.assertTrue(result["similarity_ok"])

    def test_tolerates_hiragana_marker_spelling_variant(self):
        marked = "前半は目印です。"
        recognized = "前半はめじるしです。"
        result = p4d.check_full_text_content(recognized, marked)
        self.assertEqual(result["marker_occurrences_by_spelling"]["めじるし"], 1)

    def test_fails_when_content_becomes_english(self):
        marked = "前半は目印です。"
        result = p4d.check_full_text_content("this is english", marked)
        self.assertFalse(result["is_japanese"])
        self.assertFalse(result["no_unintended_english"])

    def test_fails_when_marker_count_not_five(self):
        marked = "前半は目印です。目印です。"
        result = p4d.check_full_text_content("前半は目印です。目印です。", marked)
        self.assertFalse(result["marker_occurrence_total_is_five"])


class CheckKeyExpressionsTests(unittest.TestCase):

    def test_detects_all_three_expected_expressions(self):
        script = "まえはさいごのすうふんでしゅびをかためわずかなりーどをまもる"
        result = p4d.check_key_expressions(script)
        self.assertTrue(result["last_few_minutes"]["present"])
        self.assertTrue(result["defend"]["present"])
        self.assertFalse(result["defend"]["forbidden_form_present"])
        self.assertTrue(result["narrow_lead"]["present"])

    def test_detects_forbidden_defend_form(self):
        script = "しゅびをかためるところ"
        result = p4d.check_key_expressions(script)
        self.assertTrue(result["defend"]["forbidden_form_present"])

    def test_missing_expression_reported_as_absent(self):
        script = "まったく関係のない文字列"
        result = p4d.check_key_expressions(script)
        self.assertFalse(result["last_few_minutes"]["present"])


class SudachiTokenizeIntegrationTests(unittest.TestCase):
    """隔離MFA環境への実サブプロセス呼び出しを含む統合テスト
    (TTS・Azure STTは呼ばない)。"""

    def test_real_pattern_a_full_pipeline_matches_expected_key_expressions(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        marked = p4d.build_marker_replaced_source(text, used_forms)
        self.assertTrue(marked["marker_count_is_five"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            morphemes = p4d.sudachi_tokenize(marked["marked_text"], tmp_dir)

        reading_map = p4d.build_reading_map(morphemes)
        script = p4d.build_full_hiragana_script(reading_map)
        verification = p4d.verify_reading_conversion(marked["marked_text"], reading_map, script)
        self.assertTrue(verification["all_passed"], msg=verification)

        key_expr = p4d.check_key_expressions(script)
        self.assertTrue(key_expr["last_few_minutes"]["present"], msg=script)
        self.assertTrue(key_expr["defend"]["present"], msg=script)
        self.assertFalse(key_expr["defend"]["forbidden_form_present"], msg=script)
        self.assertTrue(key_expr["narrow_lead"]["present"], msg=script)


if __name__ == "__main__":
    unittest.main()
