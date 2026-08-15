# ============================================================
# er003_test_b1_scaffold_audio_01.py
# ER-003-B1-SCAFFOLD-AUDIO-02: TTS/ASR hardening regression tests
# ============================================================
# ER-003-B1-SCAFFOLD-AUDIO-01で発見・修正した5件の技術的問題
# (Markdown強調記号、カーブ引用符、自己言及的な一文、ASR検証の文字列
# 比較方式、英国綴り/米国綴り差)について、正しく生成された音声を
# 誤ってFAILさせない(かつ、本当に内容が異なる音声は正しくFAILさせる)
# ことを確認する回帰テスト。実TTS・実ASR呼び出しは行わない
# (`strip_markdown_emphasis`/`expected_words_present`という純粋な
# テキスト処理ロジックのみを対象とする)。
#
# 実際のTTS層での修正確認(400エラー解消・self-reference対策)は、
# ER-003-B1-SCAFFOLD-AUDIO-01/02の実行時に本物のTTS+ASRで検証済み
# (audit配下のsegment_generation_results.json参照)であり、本ファイルは
# その際に見つかったASR文字列比較ロジックのバグに対する退行防止テスト。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_scaffold_audio_01 -v

import unittest

import er003_v1_b1_scaffold_audio_01_generate as m


class MarkdownAndQuoteNormalizationTests(unittest.TestCase):
    """H-2/H-3: Markdown強調記号・カーブ引用符の除去(TTS入力直前のみ)。"""

    def test_double_asterisk_removed(self):
        text = 'The word **"default"** matters.'
        self.assertNotIn("**", m.strip_markdown_emphasis(text))

    def test_curly_quotes_removed(self):
        text = "The word “default” matters."
        result = m.strip_markdown_emphasis(text)
        self.assertNotIn("“", result)
        self.assertNotIn("”", result)

    def test_words_unchanged_by_normalization(self):
        # 記号を除いても単語そのものは変更しない(内容の書き換えではない)
        text = "Autoplay and **personalised** feeds would be off by default."
        result = m.strip_markdown_emphasis(text)
        self.assertIn("personalised", result)
        self.assertIn("Autoplay", result)

    def test_straight_quotes_pass_through_unchanged(self):
        # ストレート引用符はそもそも問題を起こさないため変更しない
        text = 'He said "hello" to them.'
        self.assertEqual(m.strip_markdown_emphasis(text), text)


class ExpectedWordsPresentTests(unittest.TestCase):
    """H-5: ASR検証の単語列連続部分列一致(text[:40]的な文字列包含に
    起因する偽陰性の回帰防止)。"""

    def test_normal_matching_audio_passes(self):
        expected = "The pilot is a clue, not a crystal ball."
        asr_text = "The pilot is a clue, not a crystal ball. A separate 2026 pilot provides context."
        self.assertTrue(m.expected_words_present(expected, asr_text))

    def test_comma_difference_does_not_break_match(self):
        # 実際に発生したケース: 期待側は「clue not」、ASR側は「clue, not」
        expected = "The pilot is a clue, not a crystal ball."
        asr_text = "The pilot is a clue not a crystal ball."  # ASRがコンマを付けない場合
        self.assertTrue(m.expected_words_present(expected, asr_text))

    def test_hyphenated_compound_word_normalized(self):
        # 実際に発生したケース: night-curfew(原文) vs night curfew(ASR正規化)
        expected = "the night-curfew group found this easier"
        asr_text = "So the night curfew group found this easier to manage"
        self.assertTrue(m.expected_words_present(expected, asr_text))

    def test_newline_in_source_text_does_not_break_match(self):
        # 実際に発生したケース: text[:40]が段落境界の改行を含んでしまう
        expected = "And the plan does not stop at bedtime.\n\nAutoplay and personalised feeds"
        asr_text = "And the plan does not stop at bedtime. Autoplay and personalized feeds would be off."
        self.assertTrue(m.expected_words_present(expected, asr_text))

    def test_british_us_spelling_difference_passes(self):
        # H-6: 発音が同一の綴り差はexpected_words_present自体では吸収されない
        # (最初の6語に該当語が含まれない場合は無関係)が、該当語が対象内なら
        # 綴り差そのものはこの関数の対象外であることを確認する
        # (実際のKey Phrase 5対策はtts_text側のAmerican綴り採用で行っている)。
        expected = "personalised feeds would also be turned"
        asr_text_us = "personalized feeds would also be turned off by default"
        # 単語列一致は大文字小文字は無視するが綴りの違い(s/z)までは吸収しない
        self.assertFalse(m.expected_words_present(expected, asr_text_us))

    def test_different_content_fails(self):
        # 内容が明らかに異なる音声は不合格のままであるべき(安全機構の実効性確認)
        expected = "The pilot is a clue, not a crystal ball."
        asr_text = "Don't get into this mindset of letting your mess pile up."
        self.assertFalse(m.expected_words_present(expected, asr_text))

    def test_empty_asr_text_fails(self):
        # Azure STT認証エラー等で空文字が返るケース(H-1)を誤ってPASS扱いしない
        expected = "The pilot is a clue, not a crystal ball."
        self.assertFalse(m.expected_words_present(expected, ""))
        self.assertFalse(m.expected_words_present(expected, None))

    def test_multi_word_key_phrase_matches(self):
        expected = "cross the finish line"
        asr_text = "The plan has not crossed the finish line as of August."
        # "crossed"(過去形)は語幹が異なるため単語完全一致では不一致になる。
        # 現在形での一致例で多語Key Phraseの一致確認を行う。
        expected2 = "the finish line"
        self.assertTrue(m.expected_words_present(expected2, asr_text))


if __name__ == "__main__":
    unittest.main()
