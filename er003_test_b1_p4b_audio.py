# ============================================================
# er003_test_b1_p4b_audio.py
# ER-003-B1-P4B: 短文分割＋単一「合図」マーカーのテスト
# ============================================================
# 実TTS・実MFA呼び出しは行わない。chunk分割・静的検証ロジックのみを
# 対象とする。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p4b_audio -v

import json
import unittest

import er003_b1_p4b_audio as p4b


def _real_pattern_a_and_used_forms():
    with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
        data = json.load(f)
    pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
    return pattern_a["text"], pattern_a["used_forms"]


class BuildChunkPlanTests(unittest.TestCase):

    def test_produces_six_chunks(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        self.assertEqual(len(plan), 6)

    def test_five_marker_chunks_one_normal_chunk(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        marker_chunks = [c for c in plan if c["chunk_type"] == "marker"]
        normal_chunks = [c for c in plan if c["chunk_type"] == "normal"]
        self.assertEqual(len(marker_chunks), 5)
        self.assertEqual(len(normal_chunks), 1)

    def test_marker_chunks_cover_all_five_used_forms_in_order(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        marker_chunks = [c for c in plan if c["chunk_type"] == "marker"]
        self.assertEqual([c["used_form"] for c in marker_chunks], [
            "shot on target", "take players off", "a narrow lead",
            "close the door to the final", "stoppage time",
        ])

    def test_chunks_reconstruct_pattern_a_exactly(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        reconstructed = "".join(c["source_text"] for c in plan)
        self.assertEqual(reconstructed, text)

    def test_normal_chunk_contains_last_few_minutes_phrase(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        normal_chunk = next(c for c in plan if c["chunk_type"] == "normal")
        self.assertTrue(normal_chunk["contains_last_few_minutes"])
        self.assertIn("最後の数分", normal_chunk["source_text"])

    def test_only_normal_chunk_flagged_for_last_few_minutes(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        flagged = [c for c in plan if c["contains_last_few_minutes"]]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]["chunk_type"], "normal")

    def test_marker_chunk_tts_text_has_marker_not_used_form(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        for c in plan:
            if c["chunk_type"] == "marker":
                self.assertNotIn(c["used_form"], c["tts_text"])
                self.assertEqual(c["tts_text"].count(p4b.MARKER_TOKEN), 1)

    def test_normal_chunk_tts_text_equals_source_text(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        normal_chunk = next(c for c in plan if c["chunk_type"] == "normal")
        self.assertEqual(normal_chunk["tts_text"], normal_chunk["source_text"])

    def test_chunk_order_is_sequential(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        self.assertEqual([c["order"] for c in plan], [1, 2, 3, 4, 5, 6])
        self.assertEqual([c["chunk_id"] for c in plan], ["01", "02", "03", "04", "05", "06"])

    def test_raises_if_multiple_used_forms_in_one_chunk(self):
        text = "shot on target and take players off in one sentence"
        used_forms = [
            {"canonical_english": "shot on target", "used_form": "shot on target"},
            {"canonical_english": "take a player off", "used_form": "take players off"},
        ]
        with self.assertRaises(ValueError):
            p4b.build_chunk_plan(text, used_forms)


class VerifyChunkPlanStaticTests(unittest.TestCase):

    def test_real_chunk_plan_passes_all_checks(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        result = p4b.verify_chunk_plan_static(plan, text)
        self.assertTrue(result["all_passed"], msg=result)
        self.assertEqual(result["marker_chunk_count"], 5)
        self.assertEqual(result["total_marker_count"], 5)
        self.assertTrue(result["all_used_forms_absent_in_tts"])

    def test_fails_when_used_form_residue_present(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        plan[0]["tts_text"] = plan[0]["tts_text"].replace(p4b.MARKER_TOKEN, plan[0]["used_form"])
        result = p4b.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])

    def test_fails_when_ascii_letters_present_in_normal_chunk(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        normal_chunk = next(c for c in plan if c["chunk_type"] == "normal")
        normal_chunk["tts_text"] = normal_chunk["tts_text"] + "extra"
        result = p4b.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])

    def test_fails_when_marker_missing_from_marker_chunk(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        plan[0]["tts_text"] = plan[0]["tts_text"].replace(p4b.MARKER_TOKEN, "")
        result = p4b.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])

    def test_fails_when_marker_appears_in_normal_chunk(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        normal_chunk = next(c for c in plan if c["chunk_type"] == "normal")
        normal_chunk["tts_text"] = normal_chunk["tts_text"] + p4b.MARKER_TOKEN
        result = p4b.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])

    def test_fails_when_reconstruction_broken(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p4b.build_chunk_plan(text, used_forms)
        plan[0]["source_text"] = plan[0]["source_text"][:-1]
        result = p4b.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["reconstruction_matches"])
        self.assertFalse(result["all_passed"])


class ReuseIdentityTests(unittest.TestCase):

    def test_instruction_reused_from_p4(self):
        import er003_b1_p4_audio as p4
        self.assertEqual(p4b.JAPANESE_STYLE_PREFIX, p4.JAPANESE_STYLE_PREFIX)
        self.assertEqual(p4b.ENGLISH_STYLE_PREFIX, p4.ENGLISH_STYLE_PREFIX)

    def test_gap_targets_reused_from_p4(self):
        self.assertEqual(p4b.GAP_BEFORE_TARGET_SECONDS, 0.40)
        self.assertEqual(p4b.GAP_AFTER_TARGET_SECONDS, 0.30)
        self.assertEqual(p4b.GAP_TOLERANCE_SECONDS, 0.03)

    def test_marker_token_is_single_generic_word(self):
        self.assertEqual(p4b.MARKER_TOKEN, "合図")
        self.assertEqual(p4b.MARKER_TOKEN_SEQUENCE, ("合図",))

    def test_module_does_not_reimplement_mfa_or_gap_functions(self):
        for name in ("run_mfa_align", "adjust_trailing_silence", "adjust_leading_silence",
                     "find_speech_bounds", "parse_textgrid_words_tier"):
            self.assertFalse(hasattr(p4b, name), msg=name)


if __name__ == "__main__":
    unittest.main()
