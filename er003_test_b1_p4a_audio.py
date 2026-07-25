# ============================================================
# er003_test_b1_p4a_audio.py
# ER-003-B1-P4A: Preview TTS入力監査と5マーカー再生成のテスト
# ============================================================
# 実TTS呼び出しは行わない。静的監査ロジック・マーカー修正ロジック・
# 事前確定チェックのみを対象とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p4a_audio -v

import json
import unittest

import er003_b1_p4_audio as p4
import er003_b1_p4a_audio as p4a


class AuditTtsInputTests(unittest.TestCase):

    def _real_used_forms(self):
        with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
            data = json.load(f)
        pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
        return pattern_a["text"], pattern_a["used_forms"]

    def test_classifies_actual_p4_input_as_case_b(self):
        """P4で実際に使ったTTS入力ファイルを監査し、Case Bと判定される
        ことを確認する(used form残存0・marker5件各1回・ASCII残存0)。"""
        with open(p4a.P4_TTS_INPUT_PATH, encoding="utf-8") as f:
            actual_p4_input = f.read()
        text, used_forms = self._real_used_forms()
        marker_map = p4.build_marker_map(text, used_forms)
        result = p4a.audit_tts_input(actual_p4_input, p4a._USED_FORMS, marker_map)
        self.assertEqual(result["case"], "B")
        self.assertTrue(result["all_used_forms_absent"])
        self.assertTrue(result["all_markers_present_once"])
        self.assertTrue(result["no_ascii_letters"])
        self.assertEqual(result["marker_total"], 5)

    def test_classifies_case_a_when_used_form_residue_present(self):
        text_with_residue = "前半は激しい接触と緊張が続き、close the door to the finalが現実になりそうな時"
        marker_map = [{"katakana_marker": "第四の合図", "used_form": "close the door to the final"}]
        result = p4a.audit_tts_input(text_with_residue, ["close the door to the final"], marker_map)
        self.assertEqual(result["case"], "A")
        self.assertFalse(result["all_used_forms_absent"])

    def test_classifies_case_a_when_ascii_letters_present_elsewhere(self):
        text = "前半はShotオンターゲットを記録できないまま"
        marker_map = [{"katakana_marker": "ショット・オン・ターゲット", "used_form": "shot on target"}]
        result = p4a.audit_tts_input(text, ["shot on target"], marker_map)
        self.assertEqual(result["case"], "A")
        self.assertFalse(result["no_ascii_letters"])

    def test_detects_missing_marker_as_unclassified(self):
        text = "前半は激しい接触と緊張が続き、を記録できないまま"
        marker_map = [{"katakana_marker": "ショット・オン・ターゲット", "used_form": "shot on target"}]
        result = p4a.audit_tts_input(text, ["shot on target"], marker_map)
        self.assertEqual(result["case"], "UNCLASSIFIED")


class BuildMarkerMapFixedTests(unittest.TestCase):

    def _real_data(self):
        with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
            data = json.load(f)
        pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
        return pattern_a["text"], pattern_a["used_forms"]

    def test_only_close_the_door_marker_changes(self):
        text, used_forms = self._real_data()
        original_map = p4.build_marker_map(text, used_forms)
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)

        original_by_form = {e["used_form"]: e["katakana_marker"] for e in original_map}
        fixed_by_form = {e["used_form"]: e["katakana_marker"] for e in fixed_map}

        for used_form in original_by_form:
            if used_form == "close the door to the final":
                self.assertNotEqual(fixed_by_form[used_form], original_by_form[used_form])
                self.assertEqual(fixed_by_form[used_form], "第四の合図")
            else:
                self.assertEqual(fixed_by_form[used_form], original_by_form[used_form])

    def test_replacement_marker_has_no_ascii_or_katakana(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        close_entry = next(e for e in fixed_map if e["used_form"] == "close the door to the final")
        marker = close_entry["katakana_marker"]
        self.assertFalse(p4a._ASCII_LETTER_PATTERN.search(marker))
        self.assertFalse(any("゠" <= ch <= "ヿ" for ch in marker))  # カタカナ範囲

    def test_replacement_marker_not_originally_in_pattern_a(self):
        text, used_forms = self._real_data()
        self.assertNotIn("第四の合図", text)

    def test_marker_type_recorded(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        close_entry = next(e for e in fixed_map if e["used_form"] == "close the door to the final")
        self.assertEqual(close_entry["marker_type"], "japanese_unique_phrase")
        other_entry = next(e for e in fixed_map if e["used_form"] == "shot on target")
        self.assertEqual(other_entry["marker_type"], "katakana")


class BuildTtsScriptWithMarkersFixedTests(unittest.TestCase):

    def _real_data(self):
        with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
            data = json.load(f)
        pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
        return pattern_a["text"], pattern_a["used_forms"]

    def test_script_contains_fixed_marker_not_original_katakana(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        script = p4a.build_tts_script_with_markers_fixed(text, fixed_map)
        self.assertIn("第四の合図", script)
        self.assertNotIn("クローズ・ザ・ドア・トゥ・ザ・ファイナル", script)
        self.assertNotIn("close the door to the final", script)

    def test_other_four_markers_unchanged_in_script(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        script = p4a.build_tts_script_with_markers_fixed(text, fixed_map)
        for marker in ("ショット・オン・ターゲット", "テイク・プレイヤーズ・オフ",
                       "ア・ナロー・リード", "ストッページ・タイム"):
            self.assertEqual(script.count(marker), 1)


class VerifyPreCallChecksTests(unittest.TestCase):

    def _real_data(self):
        with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
            data = json.load(f)
        pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
        return pattern_a["text"], pattern_a["used_forms"]

    def test_real_fixed_script_passes_all_checks(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        script = p4a.build_tts_script_with_markers_fixed(text, fixed_map)
        checks = p4a.verify_pre_call_checks(script, fixed_map, text)
        self.assertTrue(checks["all_passed"], msg=checks)

    def test_fails_when_used_form_residue_injected(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        script = p4a.build_tts_script_with_markers_fixed(text, fixed_map)
        broken_script = script.replace("第四の合図", "close the door to the final")
        checks = p4a.verify_pre_call_checks(broken_script, fixed_map, text)
        self.assertFalse(checks["all_passed"])
        self.assertFalse(checks["ascii_letter_count_zero"])

    def test_fails_when_marker_duplicated(self):
        text, used_forms = self._real_data()
        fixed_map = p4a.build_marker_map_fixed(text, used_forms)
        script = p4a.build_tts_script_with_markers_fixed(text, fixed_map)
        broken_script = script + "第四の合図"
        checks = p4a.verify_pre_call_checks(broken_script, fixed_map, text)
        self.assertFalse(checks["all_passed"])
        self.assertFalse(checks["marker_counts_all_one"])


if __name__ == "__main__":
    unittest.main()
