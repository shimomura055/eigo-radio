# ============================================================
# er008_disfluency_qa_18_test_01.py
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18
# ============================================================
import os
import unittest

import er008_disfluency_qa_18 as qa

KP2_EN_WAV = "er006_output/pool_pilot_01/pool_n8_airport_line/a2/narration/kp2_en.wav"
CLEAN_WAVS = [
    "er006_output/pool_pilot_01/pool_n8_airport_line/a2/narration/point_one.wav",
    "er006_output/pool_pilot_01/pool_n8_airport_line/a2/narration/point_one_heading.wav",
    "er006_output/pool_pilot_01/pool_n8_airport_line/b1b/narration/preview.wav",
    "er006_output/pool_pilot_01/pool_n8_airport_line/a2/narration/in_one_line.wav",
]


class DetectAdjacentWordRepetitionLogicTests(unittest.TestCase):
    def test_positive_case(self):
        words = [{"text": " uneven,", "start": 0.0, "end": 0.84, "probability": 0.53},
                 {"text": " uneven", "start": 0.84, "end": 1.50, "probability": 0.92},
                 {"text": " choice.", "start": 1.50, "end": 1.88, "probability": 0.90}]
        repeats = qa.detect_adjacent_word_repetition(words)
        self.assertEqual(len(repeats), 1)
        self.assertEqual(repeats[0]["token"], "uneven")

    def test_negative_case(self):
        words = [{"text": " Why", "start": 0.0, "end": 0.46, "probability": 0.95},
                 {"text": " does", "start": 0.46, "end": 1.06, "probability": 0.88},
                 {"text": " a", "start": 1.06, "end": 1.26, "probability": 0.99}]
        self.assertEqual(qa.detect_adjacent_word_repetition(words), [])

    def test_does_not_flag_multiword_phrase_repeat(self):
        # 隣接単語1語の完全一致のみを対象とし、フレーズ単位の繰り返しは
        # 対象外とする(定義を意図的に狭くしてfalse positiveを避ける)。
        words = [{"text": " very", "start": 0.0, "end": 0.2, "probability": 0.9},
                 {"text": " good", "start": 0.2, "end": 0.4, "probability": 0.9},
                 {"text": " very", "start": 0.4, "end": 0.6, "probability": 0.9},
                 {"text": " good", "start": 0.6, "end": 0.8, "probability": 0.9}]
        self.assertEqual(qa.detect_adjacent_word_repetition(words), [])


class ApplyDisfluencyGateTests(unittest.TestCase):
    """ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: Production配線用ゲート
    (apply_disfluency_gate)が、対象外の場合に一切追加処理(=faster-whisper
    呼び出し)を行わないことを確認する(存在しないwavパスを渡し、呼ばれて
    いればFileNotFoundError等で失敗するはずの経路を確認する)。"""

    def test_disabled_does_not_check_and_passes_through(self):
        result = qa.apply_disfluency_gate(True, "nonexistent_path.wav", enabled=False)
        self.assertTrue(result["verified"])
        self.assertFalse(result["disfluency_checked"])
        self.assertIsNone(result["disfluency_evidence"])

    def test_not_verified_does_not_check(self):
        result = qa.apply_disfluency_gate(False, "nonexistent_path.wav", enabled=True)
        self.assertFalse(result["verified"])
        self.assertFalse(result["disfluency_checked"])

    def test_enabled_and_verified_flags_real_defect(self):
        if not os.path.exists(KP2_EN_WAV):
            self.skipTest("No.8 fixture wav not present in this environment")
        result = qa.apply_disfluency_gate(True, KP2_EN_WAV, language="en", enabled=True)
        self.assertFalse(result["verified"])
        self.assertTrue(result["disfluency_checked"])
        self.assertTrue(result["disfluency_evidence"]["flagged"])

    def test_enabled_and_verified_passes_clean_audio(self):
        clean = next((p for p in CLEAN_WAVS if os.path.exists(p)), None)
        if clean is None:
            self.skipTest("No clean fixture wav present in this environment")
        result = qa.apply_disfluency_gate(True, clean, language="en", enabled=True)
        self.assertTrue(result["verified"])
        self.assertTrue(result["disfluency_checked"])
        self.assertFalse(result["disfluency_evidence"]["flagged"])


@unittest.skipUnless(os.path.exists(KP2_EN_WAV), "No.8 fixture wav not present in this environment")
class RealAudioEvidenceTests(unittest.TestCase):
    """No.8実データに基づく回帰テスト(このQA機構が実際に導入される前提と
    なった実音声での検知証拠を、以後も継続的に守る)。"""

    def test_kp2_en_real_defect_is_flagged(self):
        result = qa.check_segment_for_disfluency(KP2_EN_WAV, language="en", model_size="small")
        self.assertTrue(result["flagged"], result)
        self.assertTrue(any(r["token"] == "uneven" for r in result["repeats"]))

    def test_clean_segments_are_not_flagged(self):
        checked = 0
        for path in CLEAN_WAVS:
            if not os.path.exists(path):
                continue
            result = qa.check_segment_for_disfluency(path, language="en", model_size="small")
            self.assertFalse(result["flagged"], (path, result))
            checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
