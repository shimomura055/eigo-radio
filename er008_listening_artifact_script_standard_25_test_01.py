# ============================================================
# er008_listening_artifact_script_standard_25_test.py
# ER-008-N8-CLOSEOUT-GOVERNANCE-25 (5/8): 試聴Artifactの全script掲載標準の
# 欠落検知が実際に機能することを確認するfixture test。
# ============================================================
import unittest

import er008_listening_artifact_script_standard_25 as std


def _all_required_keys(level):
    return {key for key, _, has_script in std.REQUIRED_SEGMENTS_BY_LEVEL[level] if has_script}


class FullScriptCoverageTests(unittest.TestCase):
    def test_a2_complete_set_has_no_missing(self):
        present = _all_required_keys("A2")
        missing = std.check_full_script_coverage(
            "A2", present, key_phrase_count=3, key_phrase_en_present=3, key_phrase_ja_present=3)
        self.assertEqual(missing, [])

    def test_b1_complete_set_has_no_missing(self):
        present = _all_required_keys("B1")
        missing = std.check_full_script_coverage(
            "B1", present, key_phrase_count=3, key_phrase_en_present=3, key_phrase_ja_present=3)
        self.assertEqual(missing, [])

    def test_missing_single_segment_is_detected(self):
        present = _all_required_keys("A2") - {"point_two"}
        missing = std.check_full_script_coverage(
            "A2", present, key_phrase_count=2, key_phrase_en_present=2, key_phrase_ja_present=2)
        self.assertIn("Point Two", missing)

    def test_missing_key_phrase_translation_is_detected(self):
        present = _all_required_keys("A2")
        missing = std.check_full_script_coverage(
            "A2", present, key_phrase_count=3, key_phrase_en_present=3, key_phrase_ja_present=2)
        self.assertTrue(any("Key Phrase JA" in m for m in missing))

    def test_missing_key_phrase_english_is_detected(self):
        present = _all_required_keys("B1")
        missing = std.check_full_script_coverage(
            "B1", present, key_phrase_count=4, key_phrase_en_present=1, key_phrase_ja_present=4)
        self.assertTrue(any("Key Phrase EN" in m for m in missing))

    def test_unknown_level_raises(self):
        with self.assertRaises(ValueError):
            std.check_full_script_coverage("B2", set(), 0, 0, 0)

    def test_b1_has_no_japanese_title_or_point_explanation_requirement(self):
        # B1にはJapanese title/Point explanation segmentが存在しない
        # (build_b1_timeline()に対応する参照が無いことをer003_v1_n3_01_assemble.pyで確認済み)。
        b1_keys = {key for key, _, _ in std.B1_REQUIRED_SEGMENTS}
        self.assertNotIn("japanese_title", b1_keys)
        self.assertNotIn("point_explanation", b1_keys)


if __name__ == "__main__":
    unittest.main()
