# ============================================================
# er012_editorial_b_family_production_phase1_test_01.py
# 管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01
# ============================================================
# Gate 3/4向け単体テスト(API呼び出し無し)。
#   1. registryのvoice_assignmentが実際のTTS呼び出し引数(fallback含む)と
#      一致すること。
#   2. split_five_voice_sections()が5見出し以外(想定外構造)でNoneを
#      返すこと(ガードの単体テスト)。
#   3. build_b1_voices_timeline()が既存asm.build_b1_timeline()を一切
#      呼ばず、Tension slotをseq内に含むこと(契約テスト、モック使用)。
#   4. resolve_voice_names()のfallback分岐(API不可時にSchedar/Sulafat
#      へ切替)の単体テスト。
#   5. 修正指示1回目(OPEN-121/OPEN-122安全機構の本文segmentへの適用):
#      本文相当segment呼び出しで、A-Family既存Production
#      (er003_v1_n3_01_tts_generate.py 745-754行目)と同一規約に基づき
#      enable_connected_speech_equivalence_layer/enable_repetition_qaが
#      有効になること、かつA-Familyでも対象外のsegment(Tension・Closing)
#      には適用しないこと(対称性維持)の契約テスト。
from __future__ import annotations

import unittest
from unittest import mock

import er003_v1_n3_01_assemble as asm
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_production_01 as b1prod

ARTICLE_FIVE_SECTIONS = """# Title Here

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

ARTICLE_WRONG_SECTION_COUNT = """# Title Here

## Only One Heading

Some body text.
"""


class RegistryVoiceAssignmentTests(unittest.TestCase):
    def test_voice_assignment_matches_approved_names(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertEqual(editorial_type["voice_assignment"]["voice_a"], "Algieba")
        self.assertEqual(editorial_type["voice_assignment"]["voice_b"], "Erinome")
        self.assertEqual(editorial_type["voice_assignment"]["narrator"], "Aoede")
        self.assertEqual(editorial_type["voice_fallback"]["voice_a"], "Schedar")
        self.assertEqual(editorial_type["voice_fallback"]["voice_b"], "Sulafat")

    def test_comment_roles_present_for_all_four(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        for key in ("comment_1", "comment_2", "comment_3", "comment_4"):
            self.assertIn(key, editorial_type["comment_roles"])
            self.assertTrue(editorial_type["comment_roles"][key].strip())

    def test_comment_1_bans_the_question_phrase(self):
        # EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11の禁止句
        # 追加がregistry側の実体にも反映されていることを確認する。
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertIn('"the question"という語句そのもの', editorial_type["comment_roles"]["comment_1"])

    def test_first_person_not_mechanically_enforced_phase1(self):
        editorial_type = registry.get_editorial_type("b_family_voices")
        self.assertFalse(editorial_type["first_person_mechanically_enforced"])


class SplitFiveVoiceSectionsTests(unittest.TestCase):
    def test_valid_five_section_article_parses(self):
        sections = b1prod.split_five_voice_sections(ARTICLE_FIVE_SECTIONS)
        self.assertIsNotNone(sections)
        self.assertEqual(sections["voice_a_heading"], "Voice A Heading")
        self.assertEqual(sections["voice_b_heading"], "Voice B Heading")
        self.assertIn("Tension body text here.", sections["tension_body"])
        self.assertIn("Closing body text here.", sections["closing_body"])

    def test_wrong_section_count_returns_none(self):
        sections = b1prod.split_five_voice_sections(ARTICLE_WRONG_SECTION_COUNT)
        self.assertIsNone(sections)

    def test_no_title_returns_none(self):
        sections = b1prod.split_five_voice_sections("## Heading only, no title\n\nBody.\n")
        self.assertIsNone(sections)


class ResolveVoiceNamesFallbackTests(unittest.TestCase):
    def test_both_voices_available_uses_approved_names(self):
        sample_results = {"Algieba": {"status": "OK"}, "Erinome": {"status": "OK"}}
        voice_a, voice_b, reasons = b1prod.resolve_voice_names(sample_results)
        self.assertEqual(voice_a, "Algieba")
        self.assertEqual(voice_b, "Erinome")
        self.assertEqual(reasons, {})

    def test_voice_a_unavailable_falls_back_to_schedar(self):
        sample_results = {"Algieba": {"status": "ERROR", "error": "technical failure"},
                           "Erinome": {"status": "OK"}}
        voice_a, voice_b, reasons = b1prod.resolve_voice_names(sample_results)
        self.assertEqual(voice_a, "Schedar")
        self.assertEqual(voice_b, "Erinome")
        self.assertIn("voice_a", reasons)

    def test_voice_b_unavailable_falls_back_to_sulafat(self):
        sample_results = {"Algieba": {"status": "OK"},
                           "Erinome": {"status": "ERROR", "error": "technical failure"}}
        voice_a, voice_b, reasons = b1prod.resolve_voice_names(sample_results)
        self.assertEqual(voice_a, "Algieba")
        self.assertEqual(voice_b, "Sulafat")
        self.assertIn("voice_b", reasons)


class BuildB1VoicesTimelineContractTests(unittest.TestCase):
    """既存asm.build_b1_timeline()(11-part固定、A-Family/既存B1が使う関数)を
    一切呼ばないこと、かつ既存共有primitive(build_b1_key_phrase_blocks等)は
    呼ぶことを確認する契約テスト(実TTS/実Assembly実行はしない、モックのみ)。"""

    def _fake_parts(self):
        stereo = lambda: [[0.0, 0.0]] * 10  # noqa: E731 (テスト専用の軽量プレースホルダ)
        b1 = {name: stereo() for name in (
            "preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "full_story_part1", "full_story_part2", "point_one_heading", "point_one",
            "point_two_heading", "point_two", "in_one_line", b1prod.EXTRA_SEGMENT_NAME)}
        return {
            "intro": stereo(), "welcome": stereo(), "topic_intro": stereo(), "notification": stereo(),
            "preview_intro": stereo(), "key_phrases_intro": stereo(), "full_story_intro": stereo(),
            "point_notification": stereo(), "outro": stereo(), "kp_items": [], "b1_segments": b1,
        }

    def test_build_b1_voices_timeline_does_not_call_existing_build_b1_timeline(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_timeline") as mocked_old_timeline:
            seq = b1prod.build_b1_voices_timeline(parts, "Algieba", "Erinome")
            mocked_old_timeline.assert_not_called()
        labels = [name for name, _ in seq]
        self.assertTrue(any(label.startswith("Tension:") for label in labels))
        self.assertTrue(any("Voice A body" in label for label in labels))
        self.assertTrue(any("Voice B body" in label for label in labels))

    def test_build_b1_voices_timeline_uses_shared_key_phrase_block_builder(self):
        parts = self._fake_parts()
        with mock.patch.object(asm, "build_b1_key_phrase_blocks", wraps=asm.build_b1_key_phrase_blocks) as spy:
            b1prod.build_b1_voices_timeline(parts, "Algieba", "Erinome")
            spy.assert_called_once()


class VoiceBodySafetyFeatureDefaultsTests(unittest.TestCase):
    """修正指示1回目: generate_voice_body_wide_margin(Voice A/B本文専用
    関数)の既定値が、A-Family既存Production(OPEN-121/OPE-122対象4segment)
    と同じくTrueであることの単体テスト(実TTS呼び出しなし、シグネチャ検査)。"""

    def test_defaults_enable_connected_speech_and_repetition_qa(self):
        import inspect
        sig = inspect.signature(b1prod.generate_voice_body_wide_margin)
        self.assertIs(sig.parameters["enable_connected_speech_equivalence_layer"].default, True)
        self.assertIs(sig.parameters["enable_repetition_qa"].default, True)


class RunTtsBodySegmentSafetyFeatureContractTests(unittest.TestCase):
    """修正指示1回目の中心契約テスト: er012_b_family_production_runner_01.
    run_tts()が、本文相当segment(Hook part1/2=full_story_part1/2、
    Voice A=point_one、Voice B=point_two)呼び出しではOPEN-121/OPEN-122
    フラグを有効化し、A-Familyでも対象外のsegment(Tension・Closing=
    in_one_line)には適用しない(A-Familyとの対称性維持)ことを、実TTS/
    実API呼び出しなしで(全生成関数をモック化して)検証する。"""

    def _fake_parts(self):
        return {
            "title": "Sample Title", "part1": "Hook sentence one.", "part2": "Hook sentence two.",
            "point_one_heading": "One Voice Heading.", "point_one_body": "Voice A body text.",
            "point_two_heading": "Another Voice Heading.", "point_two_body": "Voice B body text.",
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
        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(runner.voice01, "generate_charon_english", side_effect=self._ok), \
             mock.patch.object(runner.point_headings, "generate", side_effect=self._ok), \
             mock.patch.object(runner.b1prod, "generate_voice_body_wide_margin",
                                side_effect=self._ok) as voice_body_mock, \
             mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin",
                                side_effect=self._ok) as narration_mock:
            runner.run_tts(parts, support, "Algieba", "Erinome")

        # Voice A/B(point_one/point_two)は常にTrue(A-Familyの4segment
        # 集合の一員)。
        voice_body_calls = {c.args[2]: c.kwargs for c in voice_body_mock.call_args_list}
        for voice_name in ("Algieba", "Erinome"):
            kwargs = voice_body_calls[voice_name]
            self.assertTrue(kwargs["enable_connected_speech_equivalence_layer"])
            self.assertTrue(kwargs["enable_repetition_qa"])

        # Hook part1/2(full_story_part1/2)はTrue、Tension・Closing
        # (in_one_line)はA-Familyでも対象外のためFalse。
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
        # disfluency_qaの既存規約(in_one_lineのみTrue)が今回の変更で
        # 壊れていないことも合わせて確認する。
        self.assertTrue(narration_calls["in_one_line"]["disfluency_qa"])
        self.assertFalse(narration_calls[b1prod.EXTRA_SEGMENT_NAME]["disfluency_qa"])


if __name__ == "__main__":
    unittest.main()
