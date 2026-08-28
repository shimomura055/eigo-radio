# ============================================================
# er008_internal_label_gate_18_test_01.py
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18
# ============================================================
import unittest

import er003_audio_tts_asr_safety as safety


class EnglishInternalLabelGateTests(unittest.TestCase):
    def test_detects_part_2_leak_reproduces_no8_incident(self):
        text = ("People may line up early because waiting feels safer than risking a "
                "problem later. In Part 2, what is American Airlines doing to manage "
                "this behavior?")
        findings = safety.detect_internal_production_labels_in_english_text(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["token"], "Part 2")
        self.assertTrue(safety.english_internal_label_gate_requires_stop(findings))

    def test_detects_word_form_ordinal_labels(self):
        cases = [
            ("As we heard in Point One, this matters.", "Point One"),
            ("Comment 3 will bridge this to the points.", "Comment 3"),
            ("See Section II for details.", "Section II"),
        ]
        for text, expected_token in cases:
            findings = safety.detect_internal_production_labels_in_english_text(text)
            self.assertTrue(any(f["token"] == expected_token for f in findings), (text, findings))

    def test_does_not_flag_normal_usage_of_part_and_point(self):
        clean_sentences = [
            "In part, this happens because of limited overhead bin space.",
            "This is part of a larger pattern in airport behavior.",
            "What is the point of standing in line this early?",
            "Point taken: the risk is asymmetric.",
            "The gate area became crowded as more passengers joined.",
        ]
        for text in clean_sentences:
            self.assertEqual(safety.detect_internal_production_labels_in_english_text(text), [], text)

    def test_no8_original_comment_2_text_would_have_been_blocked(self):
        """No.8で実際にProductionへ流出した本文そのものを再現し、今回の
        gateがそれをブロックできることを確認する(実データ回帰テスト)。"""
        original_leaked_text = (
            "People may line up early because waiting feels safer than risking a "
            "problem later. In Part 2, what is American Airlines doing to manage "
            "this behavior?"
        )
        findings = safety.detect_internal_production_labels_in_english_text(original_leaked_text)
        self.assertTrue(safety.english_internal_label_gate_requires_stop(findings))


if __name__ == "__main__":
    unittest.main()
