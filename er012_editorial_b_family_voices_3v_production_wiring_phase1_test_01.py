# ============================================================
# er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01
# ============================================================
# Gate 3/4向け単体テスト(API呼び出し無し、¥0)。EDITORIAL-B-FAMILY-
# PRODUCTION-PATH-PHASE1-WIRING-01の既存
# er012_editorial_b_family_production_phase1_test_01.py(2V)と同型の
# パターンで、3V(3声Voice構成)配線の契約を検証する。
#   1. registry.build_required_structure()拡張の契約テスト
#      (voice_c省略時は既存2V出力とbyte一致、voice_c指定時は3V16segment)。
#   2. B_FAMILY_B1_3V_REQUIRED_SEGMENTSの内容検査(16 segment・
#      point_one/two/three命名がTrial側build_required_structure_3v()の
#      出力と一致すること)。
#   3. VOICE_ASSIGNMENT["voice_c"]=Schedar、VOICE_FALLBACKにvoice_cキーが
#      無いこと(専用fallback声を持たない2026-09-10決定の固定)。
#   4. Comment 2/3のVoice数非依存汎用化(役割マーカーは維持、count固有の
#      具体的言い回しは除去されていること)。
#   5. split_six_voice_sections()/build_parts_3v()の構造parserテスト。
#   6. resolve_voice_names_3v()(Voice A/Bは既存fallback再利用、Voice Cは
#      専用fallback無し)。
#   7. build_b1_voices_timeline_3v()の契約テスト(既存build_b1_timeline()を
#      呼ばない、共有Key Phrase block builderを使う、Voice 1/2/3 bodyを
#      含む)。
#   8. run_tts_3v()の安全機構(OPEN-121/OPE-122)契約テスト(mock、実API
#      呼び出しなし)。
#   9. DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVELの"B1"キー拡張が既存
#      A-Family/2V B-Family判定(既存segment名)へ影響しないこと。
#  10. runner main()のlevel="b1_3v"分岐契約テスト。
#  11. Trial専用実装(er012_editorial_b_voices_3v_audio_trial_01)を
#      Production module(registry/production_01/production_runner_01)が
#      モジュールレベルでimportしていないこと(STOP条件(d)の裏付け)。
from __future__ import annotations

import unittest
from unittest import mock

import er003_v1_n3_01_assemble as asm
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_production_01 as b1prod

ARTICLE_SIX_SECTIONS = """# Title Here

## Heading One

Sentence one. Sentence two.

### Voice 1 Heading

Voice 1 body text here.

### Voice 2 Heading

Voice 2 body text here.

### Voice 3 Heading

Voice 3 body text here.

## Tension Heading

Tension body text here.

## Closing Heading

Closing body text here.
"""

ARTICLE_WRONG_SECTION_COUNT_FOR_3V = """# Title Here

## Heading One

Sentence one. Sentence two.

### Voice A Heading

Voice A body text here.

### Voice B Heading

Voice B body text here.

## Tension Heading

Tension body text here.

## Closing Heading

Closing body text here.
"""


class RegistryVoiceCArgumentBackwardCompatibilityTests(unittest.TestCase):
    """voice_c省略時、build_required_structure()の出力が既存2V(修正前)と
    byte単位で同一であることを固定する(Gate 3 item1「既存2V経路は
    無変更」の裏付け)。"""

    _EXPECTED_2V_B1_SEGMENTS = (
        ("topic_intro", "Charon"), ("preview", "Charon"),
        ("comment_1", "Charon"), ("comment_2", "Charon"),
        ("comment_3", "Charon"), ("comment_4", "Charon"),
        ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
        ("point_one", "Algieba"), ("point_two", "Erinome"),
        ("full_story_part1", None), ("full_story_part2", None),
        ("tension_reflection", None), ("in_one_line", None),
    )

    def test_voice_c_omitted_matches_pre_existing_2v_b1_output(self):
        result = registry.build_required_structure("b1", "Algieba", "Erinome")
        self.assertEqual(result["segments"], self._EXPECTED_2V_B1_SEGMENTS)
        self.assertEqual(result["key_phrase_ranks"], 5)
        self.assertEqual(result["key_phrase_subkey_count"], 2)

    def test_voice_c_explicit_none_is_identical_to_omitted(self):
        with_none = registry.build_required_structure("b1", "Algieba", "Erinome", voice_c=None)
        omitted = registry.build_required_structure("b1", "Algieba", "Erinome")
        self.assertEqual(with_none, omitted)

    def test_a2_level_unaffected_by_voice_c_extension(self):
        # a2側にvoice_c指定時の3V分岐は無い(3VはB1のみ対応)。voice_c省略時の
        # 既存a2出力が変わっていないことを確認する。
        result = registry.build_required_structure("a2", "Algieba", "Erinome")
        self.assertEqual(len(result["segments"]), 15)
        names = [n for n, _ in result["segments"]]
        self.assertNotIn("point_three", names)
        self.assertNotIn("point_three_heading", names)


class RegistryVoiceCArgument3VStructureTests(unittest.TestCase):
    """voice_c指定時、3V required_structure(16 segment、point_one/two/
    three命名)がTrial側build_required_structure_3v()の出力と一致すること
    (2重定義解消、registry側が正本)。"""

    _EXPECTED_3V_B1_SEGMENTS = (
        ("topic_intro", "Charon"), ("preview", "Charon"),
        ("comment_1", "Charon"), ("comment_2", "Charon"),
        ("comment_3", "Charon"), ("comment_4", "Charon"),
        ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
        ("point_three_heading", "Aoede"),
        ("point_one", "Algieba"), ("point_two", "Erinome"), ("point_three", "Schedar"),
        ("full_story_part1", None), ("full_story_part2", None),
        ("tension_reflection", None), ("in_one_line", None),
    )

    def test_voice_c_specified_returns_16_segments_in_expected_order(self):
        result = registry.build_required_structure("b1", "Algieba", "Erinome", voice_c="Schedar")
        self.assertEqual(result["segments"], self._EXPECTED_3V_B1_SEGMENTS)
        self.assertEqual(len(result["segments"]), 16)

    def test_matches_registry_b_family_b1_3v_required_segments_constant(self):
        role_names = tuple((name, role) for name, role in registry.B_FAMILY_B1_3V_REQUIRED_SEGMENTS)
        expected_role_names = (
            ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
            ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
            ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
            ("point_one_heading", "narrator_aoede_en"), ("point_two_heading", "narrator_aoede_en"),
            ("point_three_heading", "narrator_aoede_en"),
            ("point_one", "voice_a"), ("point_two", "voice_b"), ("point_three", "voice_c"),
            ("full_story_part1", None), ("full_story_part2", None),
            (registry.EXTRA_SEGMENT_NAME, None), ("in_one_line", None),
        )
        self.assertEqual(role_names, expected_role_names)

    def test_b1_3v_config_registered_under_editorial_type(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("b1_3v", editorial_type)
        b1_3v_config = registry.get_editorial_type_b1_3v()
        self.assertIs(b1_3v_config, editorial_type["b1_3v"])
        self.assertEqual(b1_3v_config["key_phrase_ranks"], 5)
        self.assertEqual(b1_3v_config["key_phrase_subkey_count"], 2)


class VoiceCAssignmentAndNoFallbackTests(unittest.TestCase):
    """2026-09-10ユーザー決定: Voice 3=Schedar本採用、専用fallback声なし。"""

    def test_voice_c_is_schedar(self):
        self.assertEqual(registry.VOICE_ASSIGNMENT["voice_c"], "Schedar")

    def test_voice_fallback_has_no_dedicated_voice_c_entry(self):
        self.assertNotIn("voice_c", registry.VOICE_FALLBACK)

    def test_voice_a_b_assignment_and_fallback_unchanged(self):
        self.assertEqual(registry.VOICE_ASSIGNMENT["voice_a"], "Algieba")
        self.assertEqual(registry.VOICE_ASSIGNMENT["voice_b"], "Erinome")
        self.assertEqual(registry.VOICE_FALLBACK["voice_a"], "Schedar")
        self.assertEqual(registry.VOICE_FALLBACK["voice_b"], "Sulafat")


class CommentTwoThreeVoiceCountIndependentGeneralizationTests(unittest.TestCase):
    """Comment 2/3のVoice数非依存汎用化(2026-09-10ユーザー決定)。役割
    マーカー(意味)は維持したまま、count固有の具体的言い回し
    (「One Voice/Another Voice」「2つの声」「どちらか一方」等)を除去した
    ことを固定する。Comment 1/4は本タスクで一切変更していないことも
    合わせて確認する(既存test_comment_1_bans_the_question_phrase等と
    重複しない範囲での追加確認)。"""

    def test_comment_2_role_markers_preserved(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("Hookの問いから「ここから異なるVoiceを聞く」への橋渡し",
                      editorial_type["comment_roles"]["comment_2"])

    def test_comment_3_role_markers_preserved(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("なぜ違って感じるのか", editorial_type["comment_roles"]["comment_3"])

    def test_comment_2_no_longer_hardcodes_one_voice_another_voice_count(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        c2 = editorial_type["comment_roles"]["comment_2"]
        self.assertNotIn("One Voiceの後、続けてAnother Voice", c2)
        self.assertNotIn("One Voice・Another Voiceの具体的な内容の先取り", c2)

    def test_comment_3_no_longer_hardcodes_exactly_two_voices(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        c3 = editorial_type["comment_roles"]["comment_3"]
        self.assertNotIn("One Voice・Another Voice", c3)
        self.assertNotIn("2つの声", c3)
        self.assertNotIn("どちらか一方の声", c3)

    def test_comment_1_and_4_unchanged_by_this_task(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn("Listening Focus", editorial_type["comment_roles"]["comment_1"])
        self.assertIn("一段深い問い", editorial_type["comment_roles"]["comment_4"])


class SplitSixVoiceSectionsTests(unittest.TestCase):
    def test_valid_six_section_article_parses(self):
        sections = b1prod.split_six_voice_sections(ARTICLE_SIX_SECTIONS)
        self.assertIsNotNone(sections)
        self.assertEqual(sections["voice_1_heading"], "Voice 1 Heading")
        self.assertEqual(sections["voice_2_heading"], "Voice 2 Heading")
        self.assertEqual(sections["voice_3_heading"], "Voice 3 Heading")
        self.assertIn("Tension body text here.", sections["tension_body"])
        self.assertIn("Closing body text here.", sections["closing_body"])

    def test_five_section_article_returns_none(self):
        # 既存2V(5区切り)記事は3Vパーサーでは検出失敗(Noneを返す)。
        sections = b1prod.split_six_voice_sections(ARTICLE_WRONG_SECTION_COUNT_FOR_3V)
        self.assertIsNone(sections)

    def test_no_title_returns_none(self):
        self.assertIsNone(b1prod.split_six_voice_sections("## Heading only, no title\n\nBody.\n"))

    def test_existing_five_section_parser_unaffected(self):
        # split_five_voice_sections()(2V、既存)は本タスクで無変更のまま、
        # 6区切り記事は検出失敗することを確認する(相互非干渉の裏付け)。
        self.assertIsNone(b1prod.split_five_voice_sections(ARTICLE_SIX_SECTIONS))


class BuildParts3vTests(unittest.TestCase):
    def test_build_parts_3v_extracts_point_three_fields(self):
        parts = b1prod.build_parts_3v(ARTICLE_SIX_SECTIONS)
        self.assertEqual(parts["point_three_heading"], "Voice 3 Heading.")
        self.assertIn("Voice 3 body text here.", parts["point_three_body"])
        self.assertEqual(parts["point_one_heading"], "Voice 1 Heading.")
        self.assertEqual(parts["point_two_heading"], "Voice 2 Heading.")


class ResolveVoiceNames3vTests(unittest.TestCase):
    def test_all_three_voices_available(self):
        sample_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"}, "Schedar": {"status": "OK"}}
        voice_a, voice_b, voice_c, reasons = b1prod.resolve_voice_names_3v(sample_results)
        self.assertEqual((voice_a, voice_b, voice_c), ("Algieba", "Erinome", "Schedar"))
        self.assertEqual(reasons, {})

    def test_voice_a_unavailable_still_uses_existing_fallback_logic(self):
        sample_results = {"Algieba": {"status": "ERROR", "error": "technical failure"},
                           "Erinome": {"status": "OK"}, "Schedar": {"status": "OK"}}
        voice_a, voice_b, voice_c, reasons = b1prod.resolve_voice_names_3v(sample_results)
        self.assertEqual(voice_a, "Schedar")  # 既存voice_a fallback(無変更のresolve_voice_names()経由)
        self.assertEqual(voice_c, "Schedar")  # Voice 3は常にSchedar(専用fallbackなし)
        self.assertIn("voice_a", reasons)

    def test_voice_c_unavailable_has_no_dedicated_fallback_and_stays_schedar(self):
        sample_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"},
                           "Schedar": {"status": "ERROR", "error": "technical failure"}}
        voice_a, voice_b, voice_c, reasons = b1prod.resolve_voice_names_3v(sample_results)
        self.assertEqual(voice_c, "Schedar")  # 代替声を発明しない(既存Human Review Lockへ委ねる)
        self.assertIn("voice_c", reasons)
        self.assertIn("Human Review Lock", reasons["voice_c"])


class BuildB1VoicesTimeline3vContractTests(unittest.TestCase):
    """既存build_b1_voices_timeline()(2V、無変更)・既存asm.build_b1_timeline()
    (A-Family)いずれも呼ばないこと、共有Key Phrase block builderは呼ぶことを
    確認する契約テスト(実TTS/実Assembly実行はしない、モックのみ)。"""

    def _fake_parts(self):
        stereo = lambda: [[0.0, 0.0]] * 10  # noqa: E731
        b1 = {name: stereo() for name in (
            "preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "full_story_part1", "full_story_part2",
            "point_one_heading", "point_one", "point_two_heading", "point_two",
            "point_three_heading", "point_three",
            "in_one_line", b1prod.EXTRA_SEGMENT_NAME)}
        return {
            "intro": stereo(), "welcome": stereo(), "topic_intro": stereo(), "notification": stereo(),
            "preview_intro": stereo(), "key_phrases_intro": stereo(), "full_story_intro": stereo(),
            "point_notification": stereo(), "outro": stereo(), "kp_items": [], "b1_segments": b1,
        }

    def test_does_not_call_existing_2v_or_a_family_timeline_builders(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_timeline") as mocked_a_family_timeline, \
             mock.patch.object(b1prod, "build_b1_voices_timeline") as mocked_2v_timeline:
            seq = b1prod.build_b1_voices_timeline_3v(parts, "Algieba", "Erinome", "Schedar")
            mocked_a_family_timeline.assert_not_called()
            mocked_2v_timeline.assert_not_called()
        labels = [name for name, _ in seq]
        self.assertTrue(any(label.startswith("Tension:") for label in labels))
        self.assertTrue(any("Voice 1 body" in label for label in labels))
        self.assertTrue(any("Voice 2 body" in label for label in labels))
        self.assertTrue(any("Voice 3 body" in label for label in labels))

    def test_uses_shared_key_phrase_block_builder(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_key_phrase_blocks", wraps=asm.build_b1_key_phrase_blocks) as spy:
            b1prod.build_b1_voices_timeline_3v(parts, "Algieba", "Erinome", "Schedar")
            spy.assert_called_once()


class RunTts3vBodySegmentSafetyFeatureContractTests(unittest.TestCase):
    """run_tts_3v()が、本文相当segment(Hook part1/2、Voice A/B/C=point_one/
    two/three)呼び出しではOPEN-121/OPEN-122フラグを有効化し、A-Familyでも
    対象外のsegment(Tension・Closing=in_one_line)には適用しない(2V
    Phase1との対称性維持)ことを、実TTS/実API呼び出しなしで検証する。"""

    def _fake_parts(self):
        return {
            "title": "Sample Title", "part1": "Hook sentence one.", "part2": "Hook sentence two.",
            "point_one_heading": "Voice 1 Heading.", "point_one_body": "Voice 1 body text.",
            "point_two_heading": "Voice 2 Heading.", "point_two_body": "Voice 2 body text.",
            "point_three_heading": "Voice 3 Heading.", "point_three_body": "Voice 3 body text.",
            "in_one_line": "Closing line text.", "tension_body": "Tension body text.",
        }

    def _fake_support_texts(self):
        return {"preview": "Preview text.", "comment_1": "C1.", "comment_2": "C2.",
                "comment_3": "C3.", "comment_4": "C4."}

    def _ok(self, *_a, **_kw):
        return {"status": "OK", "canonical_text": "x"}

    def test_body_segments_get_safety_features_enabled_and_non_body_segments_do_not(self):
        parts = self._fake_parts()
        support = self._fake_support_texts()
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok), \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin",
                                side_effect=self._ok) as voice_body_mock, \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin",
                                side_effect=self._ok) as narration_mock:
            b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration")

        voice_body_calls = {c.args[2]: c.kwargs for c in voice_body_mock.call_args_list}
        for voice_name in ("Algieba", "Erinome", "Schedar"):
            kwargs = voice_body_calls[voice_name]
            self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"], voice_name)
            self.assertTrue(kwargs["enable_repetition_qa"], voice_name)

        narration_calls = {call.args[1].rsplit("/", 1)[-1].replace(".wav", ""): call.kwargs
                           for call in narration_mock.call_args_list}
        for name in ("full_story_part1", "full_story_part2"):
            kwargs = narration_calls[name]
            self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"], name)
            self.assertTrue(kwargs["enable_repetition_qa"], name)
        for name in (b1prod.EXTRA_SEGMENT_NAME, "in_one_line"):
            kwargs = narration_calls[name]
            self.assertFalse(kwargs["enable_connected_speech_equivalence_layer"], name)
            self.assertFalse(kwargs["enable_repetition_qa"], name)
        self.assertTrue(narration_calls["in_one_line"]["disfluency_qa"])
        self.assertFalse(narration_calls[b1prod.EXTRA_SEGMENT_NAME]["disfluency_qa"])

    def test_narrator_headings_include_point_three_heading(self):
        parts = self._fake_parts()
        support = self._fake_support_texts()
        with mock.patch.object(b1prod.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(b1prod.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(b1prod.point_headings, "generate", side_effect=self._ok) as heading_mock, \
             mock.patch.object(b1prod, "generate_voice_body_wide_margin", side_effect=self._ok), \
             mock.patch.object(b1prod.news_tail_fix, "generate_news_narration_wide_margin", side_effect=self._ok):
            results = b1prod.run_tts_3v(parts, support, "Algieba", "Erinome", "Schedar", "out/narration")
        heading_paths = [c.args[1] for c in heading_mock.call_args_list]
        self.assertTrue(any("point_three_heading.wav" in p for p in heading_paths))
        self.assertIn("point_three", results)
        self.assertIn("point_three_heading", results)


class DisfluencyQaMandatoryDictB1NonRegressionTests(unittest.TestCase):
    """共有Gate辞書("B1"キー)への`point_three_heading`追加が、既存A-Family/
    2V B-Family判定(既存segment名)へ影響しないこと(1エントリ追加のみで
    あることの裏付け)。"""

    def test_existing_b1_entries_still_present(self):
        b1_entries = asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]
        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
                     "in_one_line", "point_one_heading", "point_two_heading"):
            self.assertIn(name, b1_entries)

    def test_point_three_heading_added_to_b1_only(self):
        self.assertIn("point_three_heading", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"])
        self.assertNotIn("point_three_heading", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"])
        self.assertNotIn("point_three_heading", asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B_FAMILY_A2"])

    def test_a2_and_b_family_a2_entries_unchanged(self):
        self.assertEqual(
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"],
            ("in_one_line", "point_one_heading", "point_two_heading"))
        self.assertEqual(
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["A2"],
            asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B_FAMILY_A2"])

    def test_b1_entry_count_grew_by_exactly_one(self):
        # 修正前(2V Phase1/A2配線完了時点)は8件だった。今回1件追加のみで9件。
        self.assertEqual(len(asm.DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]), 9)


class RunnerLevelB1_3VDispatchTests(unittest.TestCase):
    """runner main()のlevel="b1_3v"分岐契約テスト: main()がsys.argv[2]==
    "b1_3v"のときmain_b1_3v()を呼び、main_a2()は呼ばないこと。既存
    "a2"/既定("b1")分岐は本タスクで変更していないことも確認する。"""

    def test_level_b1_3v_dispatches_to_main_b1_3v(self):
        with mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "b1_3v"]):
            runner.main()
        main_b1_3v_mock.assert_called_once()
        main_a2_mock.assert_not_called()

    def test_level_a2_does_not_dispatch_to_main_b1_3v(self):
        with mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner.sys, "argv", ["prog", "all", "a2"]):
            runner.main()
        main_a2_mock.assert_called_once()
        main_b1_3v_mock.assert_not_called()

    def test_default_level_does_not_dispatch_to_main_b1_3v_or_main_a2(self):
        fake_prep = {"article_text": "# Title\n", "parts": {"point_one_body": "x"}}
        fake_scaffold_result = {"support_status": {"preview": "OK"}, "deviation": {"overall_status": "LEDGER_COMPLIANT"}}
        with mock.patch.object(runner, "main_a2") as main_a2_mock, \
             mock.patch.object(runner, "main_b1_3v") as main_b1_3v_mock, \
             mock.patch.object(runner.sys, "argv", ["prog"]), \
             mock.patch.object(runner, "prepare", return_value=fake_prep), \
             mock.patch.object(runner, "voice_check", return_value={"voice_a": "Algieba", "voice_b": "Erinome", "reasons": {}}), \
             mock.patch.object(runner, "reuse_key_phrases"), \
             mock.patch.object(runner, "run_scaffold", return_value=fake_scaffold_result), \
             mock.patch.object(runner, "run_tts"), \
             mock.patch.object(runner, "finalize_tts_results"), \
             mock.patch.object(runner, "run_assembly", return_value={"status": "GATE_BLOCKED"}), \
             mock.patch.object(runner, "load_json", return_value={}), \
             mock.patch.object(runner, "save_json"), \
             mock.patch.object(runner, "assert_budget_ok", return_value=0.0), \
             mock.patch.object(runner, "compute_cost_jpy_so_far", return_value=(0.0, {})), \
             mock.patch.object(runner.cl, "install"), \
             mock.patch("builtins.open", mock.mock_open(read_data="dummy ledger text")):
            runner.main()
        main_a2_mock.assert_not_called()
        main_b1_3v_mock.assert_not_called()


class NoTrialScriptModuleLevelImportTests(unittest.TestCase):
    """STOP条件(d)「Trial専用実装への依存が残る」の裏付け: registry・
    production_01・production_runner_01のいずれも、Trialスクリプト
    (モジュール名に"trial"を含む)をモジュールレベルでimportしていない
    ことを、実ファイルのASTを解析して確認する。"""

    def _module_level_imports(self, path: str) -> list:
        import ast
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        return imported_modules

    def test_registry_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_editorial_type_registry_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_voices_production_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_voices_production_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])

    def test_production_runner_module_does_not_import_any_trial_script(self):
        imports = self._module_level_imports("er012_b_family_production_runner_01.py")
        self.assertEqual([m for m in imports if "trial" in m], [])


if __name__ == "__main__":
    unittest.main()
