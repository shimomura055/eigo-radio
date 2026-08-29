# ============================================================
# er008_n8_reicher_pronunciation_22_test_01.py
# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22: No.8 B1 full_story_part1
# ("Stephen Reicher")で、4回独立ASR全てが一貫して誤読した実データを受け、
# TTS入力・ASR比較対象のテキストにのみ"Reicher"->"Riker"の発音safe-
# readingを適用したことの回帰テスト。article.md/parts.json(表示用の
# 記事本文)は無変更のままであることは別途、本文ファイルへの非変更で
# 保証される(このテストはtts_safe_news_en()の変換ロジックのみ検証)。
# ============================================================
import unittest

import er003_v1_n3_01_tts_generate as tg


class ReicherPronunciationSafeReadingTests(unittest.TestCase):
    def test_reicher_is_respelled_for_tts_input(self):
        text = "Psychologist Stephen Reicher explains it as a response to uneven risks."
        safe = tg.tts_safe_news_en(text)
        self.assertIn("Riker", safe)
        self.assertNotIn("Reicher", safe)

    def test_unrelated_names_are_not_affected(self):
        text = "Kristie Tse links the behavior to anxiety."
        safe = tg.tts_safe_news_en(text)
        self.assertIn("Kristie Tse", safe)

    def test_does_not_match_substring_inside_other_words(self):
        # 単語境界(\b)で区切っているため、"Reicher"を含む別の語(架空例)を
        # 誤って部分置換しないことを確認する。
        text = "The overreicherous plan was announced."
        safe = tg.tts_safe_name_pronunciation_en(text)
        self.assertEqual(safe, text)


if __name__ == "__main__":
    unittest.main()
