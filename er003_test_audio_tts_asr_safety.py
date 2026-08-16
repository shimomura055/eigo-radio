# ============================================================
# er003_test_audio_tts_asr_safety.py
# ER-003-AUDIO-HARDENING-01: 共通TTS/ASR安全処理の回帰テストマトリクス
# ============================================================
# er003_audio_tts_asr_safety.pyが、ER-003-AUDIO-HARDENING-01仕様の
# 「4. Regression Test matrix」で要求された全ケースを満たすことを
# 確認する。実TTS/実ASR呼び出しは行わない(純粋なテキスト処理・判定
# ロジックのみを対象とする)。TTS層での実際の修正効果(400エラー解消)
# は、ER-003-B1-SCAFFOLD-AUDIO-01/02の実行時に本物のTTS+ASRで検証済み
# (各audit/segment_generation_results.json参照)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_audio_tts_asr_safety -v

import unittest

import er003_audio_tts_asr_safety as safety


class TtsInputNormalizationTests(unittest.TestCase):
    """A. TTS入力正規化: Markdown/カーブ引用符/自己言及ヒント。"""

    def test_markdown_bold_removed(self):
        text = 'The word **"default"** matters.'
        result = safety.strip_markdown_for_tts(text)
        self.assertNotIn("**", result)

    def test_straight_quotes_normal_processing(self):
        text = 'He said "hello" to them.'
        self.assertEqual(safety.strip_markdown_for_tts(text), text)

    def test_curly_quotes_normal_processing(self):
        text = "The word “default” matters."
        result = safety.strip_markdown_for_tts(text)
        self.assertNotIn("“", result)
        self.assertNotIn("”", result)

    def test_canonical_text_unchanged_by_normalization_call_itself(self):
        # 正規化関数はコピーを返すだけで、呼び出し元の元変数を書き換えない
        original = 'The word **"default"** matters.'
        _ = safety.strip_markdown_for_tts(original)
        self.assertEqual(original, 'The word **"default"** matters.')

    def test_self_referential_pattern_flagged(self):
        text = "The word default matters."
        self.assertTrue(safety.looks_self_referential(text))

    def test_ordinary_sentence_not_flagged(self):
        text = "Britain is planning new rules for teenagers."
        self.assertFalse(safety.looks_self_referential(text))


class JapaneseFractionReadingTests(unittest.TestCase):
    """ER-003-AUDIO-JP-READING-SAFETY-01: 日本語分数表現「N分のM」の
    「分」読み対策(to_tts_safe_japanese_fraction_reading)。"""

    def test_simple_fraction_gets_explicit_reading(self):
        result = safety.to_tts_safe_japanese_fraction_reading("5分の1")
        self.assertEqual(result, "5ぶんの1")

    def test_multiple_fraction_examples(self):
        cases = {
            "2分の1": "2ぶんの1",
            "3分の1": "3ぶんの1",
            "4分の3": "4ぶんの3",
            "5分の1": "5ぶんの1",
            "10分の3": "10ぶんの3",
        }
        for original, expected in cases.items():
            with self.subTest(original=original):
                self.assertEqual(safety.to_tts_safe_japanese_fraction_reading(original), expected)

    def test_fraction_embedded_in_sentence(self):
        original = "世界の石油の約5分の1を運ぶ"
        result = safety.to_tts_safe_japanese_fraction_reading(original)
        self.assertEqual(result, "世界の石油の約5ぶんの1を運ぶ")

    def test_fullwidth_digits_also_handled(self):
        result = safety.to_tts_safe_japanese_fraction_reading("５分の１")
        self.assertEqual(result, "５ぶんの１")

    def test_canonical_text_unchanged_by_normalization_call_itself(self):
        # 正規化関数はコピーを返すだけで、呼び出し元の元変数を書き換えない。
        # 記事本文・Key Phrase japanese_gloss等の表示用フィールドは、
        # この関数を通した後も呼び出し元では元のまま参照できること。
        canonical = "5分の1"
        _ = safety.to_tts_safe_japanese_fraction_reading(canonical)
        self.assertEqual(canonical, "5分の1")

    def test_time_expression_minutes_not_converted(self):
        # "5分待つ"のような時間表現の「分」(ふん)は変換してはならない
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading("5分待つ"), "5分待つ")

    def test_time_expression_after_not_converted(self):
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading("10分後"), "10分後")

    def test_time_expression_duration_not_converted(self):
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading("3分間"), "3分間")

    def test_no_false_positive_for_no_wo_non_digit(self):
        # 「N分の」の後が数字でない場合(分数ではない)は変換しない
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading("5分の休憩"), "5分の休憩")

    def test_no_fraction_no_change(self):
        text = "ホルムズ海峡は世界のエネルギー市場にとって重要だ"
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading(text), text)

    def test_empty_string(self):
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading(""), "")

    def test_none_input_returns_empty_string(self):
        self.assertEqual(safety.to_tts_safe_japanese_fraction_reading(None), "")


class TtsFallbackOrchestrationTests(unittest.TestCase):
    """B. self-referential/TTS拒否時のfallback機構(primary失敗→fallback)。"""

    def test_primary_success_no_fallback_needed(self):
        calls = []

        def primary(text, out_path):
            calls.append("primary")
            return {"status": "OK"}

        def fallback(text, out_path):
            calls.append("fallback")
            return {"status": "OK"}

        r = safety.generate_tts_with_fallback("hello", "/tmp/x.wav", primary, fallback)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["instruction_type"], "primary")
        self.assertEqual(calls, ["primary"])

    def test_primary_fails_fallback_succeeds(self):
        def primary(text, out_path):
            return {"status": "REJECTED", "reason": "400 self-referential"}

        def fallback(text, out_path):
            return {"status": "OK"}

        r = safety.generate_tts_with_fallback("The word default matters.", "/tmp/x.wav", primary, fallback)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["instruction_type"], "fallback")

    def test_both_fail_returns_stopped_for_human_review(self):
        def primary(text, out_path):
            return {"status": "REJECTED"}

        def fallback(text, out_path):
            return {"status": "REJECTED"}

        r = safety.generate_tts_with_fallback("x", "/tmp/x.wav", primary, fallback, max_attempts=2)
        self.assertEqual(r["status"], "STOPPED")
        self.assertEqual(r["instruction_type"], "human_review_required")


class AsrValidationMatrixTests(unittest.TestCase):
    """C/D/E: ASR検証正規化の回帰テストマトリクス(仕様4節の表に対応)。"""

    def test_exact_match_passes(self):
        expected = "The pilot is a clue, not a crystal ball."
        asr = "The pilot is a clue, not a crystal ball."
        r = safety.validate_asr_match(expected, asr)
        self.assertEqual(r["verdict"], safety.EXACT_MATCH)
        self.assertTrue(r["passed"])

    def test_punctuation_difference_passes(self):
        expected = "The pilot is a clue, not a crystal ball."
        asr = "The pilot is a clue not a crystal ball"  # コンマ・ピリオド無し
        r = safety.validate_asr_match(expected, asr)
        self.assertTrue(r["passed"])

    def test_capitalization_difference_passes(self):
        expected = "Britain is planning new rules."
        asr = "britain is planning new rules."
        r = safety.validate_asr_match(expected, asr)
        self.assertTrue(r["passed"])

    def test_british_us_spelling_personalised_personalized_passes(self):
        expected = "personalised feeds would also be turned"
        asr = "personalized feeds would also be turned off by default"
        r = safety.validate_asr_match(expected, asr)
        self.assertEqual(r["verdict"], safety.NORMALIZED_MATCH)
        self.assertTrue(r["passed"])

    def test_word_omission_fails(self):
        expected = "the night curfew group found this easier to manage"
        asr = "the curfew group found this easier to manage"  # "night"欠落
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])
        self.assertEqual(r["verdict"], safety.FAIL)

    def test_number_changed_fails(self):
        expected = "the pilot ran for six weeks in total"
        asr = "the pilot ran for sixty weeks in total"
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])

    def test_negation_added_fails(self):
        expected = "the plan does not stop at bedtime"
        asr = "the plan does stop at bedtime"  # "not"脱落=意味が反転
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])

    def test_negation_removed_fails(self):
        expected = "the plan does stop at bedtime"
        asr = "the plan does not stop at bedtime"  # "not"が追加=意味が反転
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])

    def test_unrelated_sentence_fails(self):
        expected = "The pilot is a clue, not a crystal ball."
        asr = "Don't get into this mindset of letting your mess pile up."
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])

    def test_empty_asr_text_fails(self):
        expected = "The pilot is a clue, not a crystal ball."
        r = safety.validate_asr_match(expected, "")
        self.assertEqual(r["verdict"], safety.FAIL)
        self.assertFalse(r["passed"])

    def test_none_asr_text_fails(self):
        expected = "The pilot is a clue, not a crystal ball."
        r = safety.validate_asr_match(expected, None)
        self.assertFalse(r["passed"])

    def test_azure_auth_error_never_passes(self):
        # Azure STT 401等、ASR自体が実行できなかったケース。
        # asr_textがNone/空であっても、明示的なエラー理由込みでFAILにする。
        expected = "The pilot is a clue, not a crystal ball."
        r = safety.validate_asr_match(expected, None, asr_error="401 Authentication error")
        self.assertEqual(r["verdict"], safety.FAIL)
        self.assertFalse(r["passed"])
        self.assertIn("PASS forbidden", r["reason"])

    def test_long_unrelated_hallucination_fails(self):
        # 過去に観測された「無関係な内容を長時間読み上げる」タイプの
        # 失敗モードを模したケース(ASRが別の長文を書き起こした状態)。
        expected = "The pilot is a clue, not a crystal ball."
        asr = ("In other news today, market analysts are watching several "
               "unrelated developments across a completely different sector "
               "that has nothing to do with this topic at all this week.")
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])

    def test_hyphenated_compound_word_normalized_still_passes(self):
        expected = "the night-curfew group found this easier"
        asr = "so the night curfew group found this easier to manage"
        r = safety.validate_asr_match(expected, asr)
        self.assertTrue(r["passed"])

    def test_audit_trail_fields_present(self):
        expected = "personalised feeds would also be turned"
        asr = "personalized feeds would also be turned off"
        r = safety.validate_asr_match(expected, asr)
        for key in ("expected_text", "normalized_expected_words", "asr_text",
                    "normalized_actual_words", "verdict", "passed", "reason"):
            self.assertIn(key, r)

    def test_does_not_over_normalize_different_content(self):
        # 綴り正規化を許容しても、内容が異なるものまで通してしまわないこと
        expected = "curfew applies from ten pm to six am"
        asr = "colour applies from ten pm to six am"  # わざと無関係な語へ差し替え
        r = safety.validate_asr_match(expected, asr)
        self.assertFalse(r["passed"])


if __name__ == "__main__":
    unittest.main()
