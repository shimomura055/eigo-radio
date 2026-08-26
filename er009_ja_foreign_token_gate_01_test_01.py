# ============================================================
# er009_ja_foreign_token_gate_01_test_01.py
# ER-009-JA-FOREIGN-TOKEN-GATE-01: Acceptance Tests
# ============================================================
# 対象: er003_audio_tts_asr_safety.classify_foreign_tokens_in_japanese_
# text()/foreign_token_gate_requires_stop()(4分類の核となる判定ロジック)
# と、er003_v1_n3_01_tts_generate.pyの日本語TTS入口(B1:
# generate_charon_japanese_with_reading_safety、A2:
# generate_a2_japanese_with_reading_safety)への配線。
#
# いずれもHUMAN_REVIEW判定時はTTS呼び出し自体を行わずSTOPPEDで早期
# returnするため、実際のAPI呼び出しは一切発生しない(pure-Python test)。
from __future__ import annotations

import unittest

import er003_audio_tts_asr_safety as safety
import er003_v1_n3_01_tts_generate as tg

NEEDS_PARAPHRASE = safety.FOREIGN_TOKEN_NEEDS_PARAPHRASE
READING_DICT = safety.FOREIGN_TOKEN_READING_DICTIONARY
ENGLISH_PRON = safety.FOREIGN_TOKEN_ENGLISH_PRONUNCIATION
HUMAN_REVIEW = safety.FOREIGN_TOKEN_HUMAN_REVIEW


class ClassifyForeignTokensCoreTests(unittest.TestCase):
    """4分類の核となる判定ロジック。"""

    def test_1_no4_real_example_part1_label_is_needs_paraphrase(self):
        # No.4 pool_n4_supermarket a2/comment_2の実例(修正前)。
        text = ("Part 1では、店が売り場の配置を変え、買い物客が最初に見る商品を"
                "変えたことを聞きました。では、その後、商品の売れ方はどう変わったのでしょうか。")
        findings = safety.classify_foreign_tokens_in_japanese_text(text)
        categories = [f["category"] for f in findings]
        self.assertIn(NEEDS_PARAPHRASE, categories)
        self.assertNotIn(HUMAN_REVIEW, categories)
        self.assertFalse(safety.foreign_token_gate_requires_stop(findings))
        # "Part 1"というtoken全体が1件のNEEDS_PARAPHRASEとして検出され、
        # "Part"だけが別途HUMAN_REVIEWへ二重計上されないこと。
        self.assertEqual(len([f for f in findings if f["category"] == NEEDS_PARAPHRASE]), 1)

    def test_2_no4_fixed_text_has_no_findings(self):
        # No.4 comment_2の修正後(ユーザー指示による言い換え)。
        text = ("物語の前半では、店が売り場の配置を変え、買い物客が最初に見る商品を"
                "変えたことを聞きました。では、その後、商品の売れ方はどう変わったのでしょうか。")
        findings = safety.classify_foreign_tokens_in_japanese_text(text)
        self.assertEqual(findings, [])
        self.assertFalse(safety.foreign_token_gate_requires_stop(findings))

    def test_3_point_label_variants_detected(self):
        for label in ("Point 2", "Comment 3", "Section IV", "Step 1"):
            with self.subTest(label=label):
                findings = safety.classify_foreign_tokens_in_japanese_text(f"今回は{label}について話します。")
                self.assertTrue(any(f["category"] == NEEDS_PARAPHRASE for f in findings), label)

    def test_4_reading_dictionary_term_classified(self):
        findings = safety.classify_foreign_tokens_in_japanese_text("自宅のWi-Fiが遅いという相談です。")
        self.assertTrue(any(f["category"] == READING_DICT for f in findings))
        self.assertFalse(safety.foreign_token_gate_requires_stop(findings))

    def test_5_known_key_phrase_term_classified_as_english_pronunciation(self):
        text = "この記事の重要表現はstandard deviationです。"
        findings = safety.classify_foreign_tokens_in_japanese_text(
            text, known_key_phrase_terms=["standard deviation"])
        self.assertTrue(any(f["category"] == ENGLISH_PRON for f in findings))
        self.assertFalse(safety.foreign_token_gate_requires_stop(findings))

    def test_6_key_phrase_term_not_passed_falls_back_to_human_review(self):
        # known_key_phrase_termsを渡さない場合、同じ英語表現はHUMAN_REVIEW
        # へ回る(黙って見逃さない、既存モジュールの過剰正規化禁止方針)。
        text = "この記事の重要表現はstandard deviationです。"
        findings = safety.classify_foreign_tokens_in_japanese_text(text)
        self.assertTrue(any(f["category"] == HUMAN_REVIEW for f in findings))
        self.assertTrue(safety.foreign_token_gate_requires_stop(findings))

    def test_7_unknown_stray_latin_token_is_human_review_and_stops_gate(self):
        findings = safety.classify_foreign_tokens_in_japanese_text("これはGloobargax社の事例です。")
        self.assertTrue(any(f["category"] == HUMAN_REVIEW for f in findings))
        self.assertTrue(safety.foreign_token_gate_requires_stop(findings))

    def test_8_no_false_positive_on_plain_japanese_with_numerals(self):
        # 既存の助数詞・年号・漢数字パターン(OPEN-73/ER-008-B1-POINT2-
        # FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07の実例)で誤検知しない。
        texts = [
            "2026年の調査によると、二つの視点から見ていきます。",
            "研究では、レイアウトを変えた店で、商品の売れ方に変化が見られました。",
            "衝動買いという言葉について説明します。",
        ]
        for text in texts:
            with self.subTest(text=text):
                findings = safety.classify_foreign_tokens_in_japanese_text(text)
                self.assertEqual(findings, [], text)

    def test_9_no4_other_a2_japanese_segments_have_no_findings(self):
        # No.4 pool_n4_supermarket a2の他segment(preview/comment_1/3/4/
        # japanese_title)は今回の監査で問題なしと確認済み。回帰確認として
        # 固定する。
        texts = [
            "スーパーの商品棚は、なぜ何度も場所が変わるのか",
            "店が商品の場所を変える理由に注目してください。",
            "このニュースは、商品の置き場所や見え方が、買い物と関係することを示しています。"
            "研究では、レイアウトを変えた店で、商品の売れ方に変化が見られました。これから、"
            "店の作りが選択にどう関わるのか、そして棚を動かす意味を二つの視点から見ていきます。",
            "ここまで、買い物には、買う人の気持ちだけでなく、店の空間も関わることを見てきました。"
            "また、棚や通路の配置を変えることは、店での体験や買い物のしやすさにも関係します。"
            "では、記事の要点を英語で確認しましょう。",
        ]
        for text in texts:
            with self.subTest(text=text[:20]):
                findings = safety.classify_foreign_tokens_in_japanese_text(text)
                self.assertEqual(findings, [], text)

    def test_10_empty_and_none_text_returns_no_findings(self):
        self.assertEqual(safety.classify_foreign_tokens_in_japanese_text(""), [])
        self.assertEqual(safety.classify_foreign_tokens_in_japanese_text(None), [])


class WiringStopsBeforeTtsCallTests(unittest.TestCase):
    """B1/A2の日本語TTS入口が、HUMAN_REVIEW判定時にTTS呼び出し自体を
    行わずSTOPPEDで早期returnすること(既存detect_gloss_placeholder_
    notation()と同じ設計)を確認する。STOPPED分岐はTTS/ASR呼び出しの
    手前でreturnするため、実際のAPI呼び出しは発生しない。"""

    def test_a2_human_review_text_stops_before_tts_and_logs(self):
        text = "これはGloobargaxxx社に関する日本語の説明文です。"
        r = tg.generate_a2_japanese_with_reading_safety(text, "does_not_matter.wav", "これは")
        self.assertEqual(r["status"], "STOPPED")
        self.assertIn("foreign_token_findings", r)
        self.assertTrue(any(f["category"] == HUMAN_REVIEW for f in r["foreign_token_findings"]))

    def test_b1_human_review_text_stops_before_tts_and_logs(self):
        text = "これはGloobargaxxx社に関する日本語の説明文です。"
        r = tg.generate_charon_japanese_with_reading_safety(text, "does_not_matter.wav", "これは")
        self.assertEqual(r["status"], "STOPPED")
        self.assertIn("foreign_token_findings", r)
        self.assertTrue(any(f["category"] == HUMAN_REVIEW for f in r["foreign_token_findings"]))

    def test_a2_needs_paraphrase_only_does_not_early_stop(self):
        # NEEDS_JAPANESE_PARAPHRASEだけの場合はgate自体はブロックしない
        # (過検知でProduction全体を止めないため)。この関数はブロックしない
        # 限りTTS呼び出しへ進むため、ここではgate判定のみを検証する
        # (実TTS呼び出しは行わせない)。
        text = "Part 1では、店が売り場の配置を変えました。"
        findings = safety.classify_foreign_tokens_in_japanese_text(text)
        self.assertFalse(safety.foreign_token_gate_requires_stop(findings))


if __name__ == "__main__":
    unittest.main()
