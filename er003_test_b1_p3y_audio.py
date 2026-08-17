# ============================================================
# er003_test_b1_p3y_audio.py
# ER-003-B1-P3Y: 日本語用instruction＋カタカナマーカー置換検証のテスト
# ============================================================
# 実TTS・実MFA呼び出しは行わない。instruction差分ロジック・カタカナ
# マーカー原稿構築ロジックのみを対象とする(MFA関連の関数はP3Wで既に
# テスト済みであり、marker_tokensを引数化済みのため再実装・再テスト
# しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3y_audio -v

import unittest

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3t_audio as p3t
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w
import er003_b1_p3y_audio as p3y


class SourceConstantsTests(unittest.TestCase):

    def test_source_constants_reused_from_p3t(self):
        self.assertEqual(p3y.SOURCE_INTEGRATED_SENTENCE, p3t.SOURCE_INTEGRATED_SENTENCE)
        self.assertEqual(p3y.SOURCE_JAPANESE_FULL_SENTENCE, p3t.SOURCE_JAPANESE_FULL_SENTENCE)
        self.assertEqual(p3y.SOURCE_ENGLISH_KEYWORD, p3t.SOURCE_ENGLISH_KEYWORD)

    def test_voice_reused_from_p3r(self):
        self.assertEqual(p3y.VOICE_NAME, p3r.VOICE_NAME)

    def test_boundary_pause_reused_from_p3u(self):
        self.assertEqual(p3y.BOUNDARY_PAUSE_SECONDS, p3u.BOUNDARY_PAUSE_SECONDS)
        self.assertEqual(p3y.BOUNDARY_PAUSE_SECONDS, 0.12)

    def test_existing_english_audio_path_reused_from_p3w(self):
        self.assertEqual(p3y.EXISTING_EN_TRIMMED_PATH, p3w.EXISTING_EN_TRIMMED_PATH)


class BuildJapaneseStylePrefixTests(unittest.TestCase):

    def test_replaces_only_the_language_line(self):
        diff = p3y.build_instruction_diff()
        self.assertTrue(diff["only_one_line_changed"], msg=diff["changed_lines"])
        self.assertTrue(diff["line_count_equal"])

    def test_changed_line_is_the_first_line(self):
        diff = p3y.build_instruction_diff()
        self.assertEqual(diff["changed_line_indices"], [0])

    def test_before_line_matches_known_english_instruction(self):
        diff = p3y.build_instruction_diff()
        self.assertEqual(diff["changed_lines"][0]["before"], p3y._ORIGINAL_LANGUAGE_LINE)

    def test_after_line_matches_japanese_instruction(self):
        diff = p3y.build_instruction_diff()
        self.assertEqual(diff["changed_lines"][0]["after"], p3y._JAPANESE_LANGUAGE_LINE)

    def test_level2_instruction_unchanged(self):
        """LEVEL2_INSTRUCTIONはer002_commonから無変更のまま連結されて
        いることを確認する。"""
        prefix = p3y.build_japanese_style_prefix()
        self.assertIn(common.LEVEL2_INSTRUCTION, prefix)

    def test_point_label_fidelity_rule_excluded_by_default(self):
        """ER-003-N3-ROOT-FIX-01: instruction leakage対策。POINT_LABEL_
        FIDELITY_RULE(Point One/Point Two/In One Lineという構成ラベル
        文字列を読み上げさせる指示)は、現行のセグメント単位生成では
        不要かつ漏れの原因となるため、既定では含まれないことを確認する。"""
        prefix = p3y.build_japanese_style_prefix()
        self.assertNotIn(common.POINT_LABEL_FIDELITY_RULE, prefix)
        self.assertNotIn("Point One", prefix)
        self.assertNotIn("Point Two", prefix)
        self.assertNotIn("In One Line", prefix)

    def test_point_label_fidelity_rule_included_when_opted_in(self):
        """真に一括生成方式でPoint/In One Lineの読み上げが必要な場合は、
        明示的にinclude_point_label_fidelity=Trueで有効化できること。"""
        prefix = p3y.build_japanese_style_prefix(include_point_label_fidelity=True)
        self.assertIn(common.POINT_LABEL_FIDELITY_RULE, prefix)

    def test_japanese_prefix_does_not_contain_original_language_line(self):
        prefix = p3y.build_japanese_style_prefix()
        self.assertNotIn(p3y._ORIGINAL_LANGUAGE_LINE, prefix)

    def test_japanese_prefix_passes_shared_assertions(self):
        """assert_no_wpm_specification / assert_no_genre_leakageを
        通過すること(内部でraiseしないことを確認)。"""
        try:
            p3y.build_japanese_style_prefix()
        except AssertionError as e:
            self.fail(f"共有アサーションで失敗: {e}")


class BuildTtsPromptTests(unittest.TestCase):

    def test_uses_japanese_style_prefix_by_default(self):
        prompt = p3y.build_tts_prompt("テスト本文")
        self.assertTrue(prompt.startswith(p3y._JAPANESE_LANGUAGE_LINE))
        self.assertTrue(prompt.endswith("テスト本文"))

    def test_accepts_explicit_style_prefix(self):
        prompt = p3y.build_tts_prompt("本文", style_prefix="カスタム")
        self.assertEqual(prompt, "カスタム本文")


class BuildTtsKatakanaMarkerScriptTests(unittest.TestCase):

    def test_inserts_marker_at_correct_position(self):
        script = p3y.build_tts_katakana_marker_script()
        self.assertIn("枠内シュート、ショット・オン・ターゲットを記録できないまま", script)

    def test_marker_appears_exactly_once(self):
        script = p3y.build_tts_katakana_marker_script()
        self.assertEqual(script.count(p3y.KATAKANA_MARKER), 1)

    def test_no_vocabulary_or_word_order_change_besides_marker(self):
        source = p3y.SOURCE_JAPANESE_FULL_SENTENCE
        script = p3y.build_tts_katakana_marker_script(source)
        without_marker = script.replace(f"、{p3y.KATAKANA_MARKER}", "")
        self.assertEqual(without_marker, source)

    def test_raises_if_marker_position_not_found(self):
        with self.assertRaises(ValueError):
            p3y.build_tts_katakana_marker_script("この文には挿入位置がありません。")

    def test_marker_is_katakana_not_meta_instruction_like_p3w(self):
        """P3Wの「キーワード挿入位置」(メタ的表現)とは異なり、文脈上
        自然なカタカナ語であることを確認する(語句が異なることのみ機械
        確認。意味の自然さそのものは対象外)。"""
        self.assertNotEqual(p3y.KATAKANA_MARKER, "キーワード挿入位置")
        self.assertIn("・", p3y.KATAKANA_MARKER)


class MfaReuseTests(unittest.TestCase):
    """MFA関連機能はP3Wのものをそのまま再利用する。カタカナマーカーの
    トークン列に対しても、find_marker_spanをmarker_tokens引数付きで
    そのまま使えることを確認する(再実装しない)。"""

    def test_find_marker_span_reused_from_p3w(self):
        self.assertIs(p3y.p3w.find_marker_span, p3w.find_marker_span)

    def test_run_mfa_align_reused_from_p3w(self):
        self.assertIs(p3y.p3w.run_mfa_align, p3w.run_mfa_align)

    def test_marker_token_sequence_matches_real_tokenizer_output(self):
        """実機のMFA日本語tokenizerでの実測(手動確認済み: 'ショット'/
        'オン'/'ターゲット'の3token)と一致することを固定化する。"""
        self.assertEqual(p3y.MARKER_TOKEN_SEQUENCE, ("ショット", "オン", "ターゲット"))

    def test_find_marker_span_works_with_katakana_sequence(self):
        words = [
            {"xmin": 0.0, "xmax": 0.5, "text": "シュート"},
            {"xmin": 0.5, "xmax": 0.8, "text": "ショット"},
            {"xmin": 0.8, "xmax": 1.0, "text": "オン"},
            {"xmin": 1.0, "xmax": 1.4, "text": "ターゲット"},
            {"xmin": 1.4, "xmax": 1.6, "text": "を"},
        ]
        result, error = p3w.find_marker_span(words, marker_tokens=p3y.MARKER_TOKEN_SEQUENCE)
        self.assertIsNone(error)
        self.assertEqual(result["marker_start_seconds"], 0.5)
        self.assertEqual(result["marker_end_seconds"], 1.4)
        self.assertEqual(result["preceding_token"], "シュート")
        self.assertEqual(result["following_token"], "を")


if __name__ == "__main__":
    unittest.main()
