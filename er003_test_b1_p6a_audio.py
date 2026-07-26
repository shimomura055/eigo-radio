# ============================================================
# er003_test_b1_p6a_audio.py
# ER-003-B1-P6A: 本編分割・接続方式のPreview適用検証のテスト
# ============================================================
# 実TTS呼び出しは行わない。chunk分割・静的検証・対象句チェック
# ロジックのみを対象とする(P4B/P4Cのテストパターンを踏襲)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p6a_audio -v

import json
import unittest

import er003_b1_p6a_audio as p6a


def _real_pattern_a_and_used_forms():
    with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
        data = json.load(f)
    pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
    return pattern_a["text"], pattern_a["used_forms"]


class BuildChunkPlanTests(unittest.TestCase):

    def test_produces_four_chunks(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        self.assertEqual(len(plan), 4)

    def test_reconstructs_pattern_a_exactly(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        reconstructed = "".join(c["source_text"] for c in plan)
        self.assertEqual(reconstructed, text)

    def test_chunk_marker_counts_match_expected_used_forms(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        # 文1=shot on target(1件), 文2=take players off+a narrow lead(2件),
        # 文3=close the door to the final+stoppage time(2件), 文4=0件
        self.assertEqual([len(c["used_forms"]) for c in plan], [1, 2, 2, 0])

    def test_used_forms_in_correct_order_per_chunk(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        self.assertEqual(plan[0]["used_forms"], ["shot on target"])
        self.assertEqual(plan[1]["used_forms"], ["take players off", "a narrow lead"])
        self.assertEqual(plan[2]["used_forms"], ["close the door to the final", "stoppage time"])
        self.assertEqual(plan[3]["used_forms"], [])

    def test_chunk_types(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        self.assertEqual([c["chunk_type"] for c in plan], ["marker", "marker", "marker", "normal"])

    def test_tts_text_has_markers_not_used_forms(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        for c in plan:
            for uf in c["used_forms"]:
                self.assertNotIn(uf, c["tts_text"])
            self.assertEqual(c["tts_text"].count(p6a.MARKER_TOKEN), len(c["used_forms"]))

    def test_normal_chunk_tts_text_equals_source(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        self.assertEqual(plan[3]["tts_text"], plan[3]["source_text"])

    def test_last_chunk_contains_last_few_minutes_and_nani_ga_okiru(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        self.assertIn("最後の数分", plan[3]["source_text"])
        self.assertIn("何が起きるのでしょうか", plan[3]["source_text"])

    def test_second_chunk_contains_narrow_lead_not_isolated(self):
        # 「わずかなリード」を独立した短いchunkにしない(指示section5)。
        # chunk2は「後半に試合が動くと」から始まる長い文の一部として
        # 含まれていることを確認する。
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        self.assertIn("後半に試合が動くと", plan[1]["source_text"])
        self.assertIn("わずかなリード", plan[1]["source_text"])


class VerifyChunkPlanStaticTests(unittest.TestCase):

    def test_real_chunk_plan_passes_all_checks(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        result = p6a.verify_chunk_plan_static(plan, text)
        self.assertTrue(result["all_passed"], msg=result)
        self.assertEqual(result["chunk_count"], 4)
        self.assertEqual(result["total_marker_count"], 5)
        self.assertTrue(result["used_form_count_is_five"])
        self.assertTrue(all(result["kanji_target_phrase_presence"].values()), msg=result)

    def test_fails_when_used_form_residue_present(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        plan[0]["tts_text"] = plan[0]["tts_text"].replace(p6a.MARKER_TOKEN, plan[0]["used_forms"][0])
        result = p6a.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])

    def test_fails_when_marker_count_wrong_in_multi_marker_chunk(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        # chunk2(2marker)から1つだけ消す
        plan[1]["tts_text"] = plan[1]["tts_text"].replace(p6a.MARKER_TOKEN, "", 1)
        result = p6a.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])
        self.assertFalse(result["total_marker_count_is_five"])

    def test_fails_on_reconstruction_mismatch(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        plan[0]["source_text"] = plan[0]["source_text"][:-1]
        result = p6a.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["reconstruction_matches"])
        self.assertFalse(result["all_passed"])

    def test_fails_when_ascii_letters_present(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6a.build_chunk_plan(text, used_forms)
        plan[3]["tts_text"] = plan[3]["tts_text"] + "extra"
        result = p6a.verify_chunk_plan_static(plan, text)
        self.assertFalse(result["all_passed"])


class CheckKanjiTargetPhrasesTests(unittest.TestCase):

    def test_detects_all_present_phrases(self):
        text = "".join(p6a.KANJI_TARGET_PHRASES) + "目印目印目印目印目印"
        result = p6a.check_kanji_target_phrases(text)
        for phrase in p6a.KANJI_TARGET_PHRASES:
            self.assertTrue(result[phrase], msg=phrase)
        self.assertEqual(result["目印_count"], 5)

    def test_missing_phrase_reported_absent(self):
        result = p6a.check_kanji_target_phrases("まったく関係のない文字列")
        self.assertFalse(result["最後の数分"])


class ReuseIdentityTests(unittest.TestCase):

    def test_instruction_reused_from_p4b(self):
        import er003_b1_p4b_audio as p4b
        self.assertEqual(p6a.JAPANESE_STYLE_PREFIX, p4b.JAPANESE_STYLE_PREFIX)

    def test_join_pause_matches_honpen_section_join_pause(self):
        import er002_common as common
        self.assertEqual(p6a.JA_CHUNK_JOIN_PAUSE_SECONDS, common.SECTION_JOIN_PAUSE_SECONDS)
        self.assertEqual(p6a.JA_CHUNK_JOIN_PAUSE_SECONDS, 0.8)

    def test_gap_targets_reused_from_p4b(self):
        self.assertEqual(p6a.GAP_BEFORE_TARGET_SECONDS, 0.40)
        self.assertEqual(p6a.GAP_AFTER_TARGET_SECONDS, 0.30)

    def test_module_does_not_reimplement_shared_functions(self):
        for name in ("run_mfa_align", "adjust_trailing_silence", "adjust_leading_silence",
                     "find_speech_bounds", "assemble_audio", "apply_dynamics3_once", "normalize_pcm"):
            self.assertFalse(hasattr(p6a, name), msg=name)


if __name__ == "__main__":
    unittest.main()
