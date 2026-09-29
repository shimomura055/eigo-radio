# ============================================================
# er019_family_x_flash_lite_role_style_wiring_02_test_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest \
#       er019_family_x_flash_lite_role_style_wiring_02_test_01 -v
#
# API呼び出し: 0(実TTS/ASR呼び出しは全てmock)。
#
# 対象(B-2、ユーザー確定仕様): Family X runnerが
# `--tts-backend speech_metadata_flash_lite`選択時、6-role styleを
# Standard(A2)/Advanced(B1B)両方へ適用すること、Standard固有の速度調整
# 仕様(既承認`A2_SLOWER_PACE_INSTRUCTION`)は6-role styleと連結され
# 失われないこと、既定backend(structured_separation)は無変更のままで
# あることを確認する。
# 対象(C、ユーザー確定仕様): Key Phrase(shared_narration経由)へも
# tts_backendがそのまま伝播すること。
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as n3_tts
import er019_family_x_audio_production_runner_01 as runner
import er033_tts_flash_lite_family_x_styles_01 as fl_styles


def _ok(*_a, **_kw):
    return {"status": "OK", "canonical_text": "x"}


class B1RoleStyleFlashLiteTests(unittest.TestCase):
    """Advanced(B1B)は既存どおり6-role styleのみ(速度調整の対象外)。
    既定backendではstyle_prefix_overrideが一切渡らない(既存挙動維持)。"""

    def _make_b1b_dir(self, tmpdir):
        parts = {
            "title": "Sample Title", "part1": "Part one text.",
            "part2": "Body two text.", "heading1": "Heading One.", "body2": "Body two text.",
            "part3": "Body three text.", "heading2": "Heading Two.", "body3": "Body three text.",
            "in_one_line": "In one line text.",
        }
        support = {"preview": "Preview.", "comment_1": "C1.", "comment_2": "C2.",
                   "comment_3": "C3.", "comment_4": "C4."}
        b1b_dir = os.path.join(tmpdir, "b1b")
        os.makedirs(b1b_dir, exist_ok=True)
        with open(os.path.join(b1b_dir, "parts.json"), "w", encoding="utf-8") as f:
            json.dump(parts, f)
        with open(os.path.join(b1b_dir, "b1_support_texts.json"), "w", encoding="utf-8") as f:
            json.dump(support, f)
        return b1b_dir

    def test_flash_lite_backend_passes_six_role_style_to_full_story_and_preview(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_b1_role_style_")
        try:
            self._make_b1b_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
                 mock.patch.object(runner.voice01, "generate_charon_english", side_effect=_ok) as charon_mock, \
                 mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin",
                                    side_effect=_ok) as wide_margin_mock, \
                 mock.patch.object(runner.point_headings, "generate", side_effect=_ok) as heading_mock:
                runner.generate_family_x_b1_segments(tmpdir, tts_backend="speech_metadata_flash_lite")

            # preview: role PREVIEW
            preview_call = next(c for c in charon_mock.call_args_list if c.args[:1] == ("Preview.",) or
                                 (c.args and "Preview" in str(c.args[0])))
            self.assertEqual(preview_call.kwargs.get("style_prefix_override"),
                              fl_styles.FAMILY_X_ROLE_STYLE_EN["PREVIEW"])
            # full_story_part1: role FULL_STORY, no slowdown suffix
            fs1_call = wide_margin_mock.call_args_list[0]
            self.assertEqual(fs1_call.kwargs.get("style_prefix_override"),
                              fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"])
            self.assertNotIn(n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip(),
                              fs1_call.kwargs.get("style_prefix_override") or "")
            # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1): Heading Readout撤去。
            # point_headings.generate()はFamily X新構造からは一切呼ばれない
            # (定数FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"]自体は削除せず
            # 未使用のまま残置、他Family[point_one_heading等]は無影響)。
            self.assertEqual(heading_mock.call_args_list, [])
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_default_backend_does_not_pass_style_prefix_override_for_preview(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_b1_role_style_default_")
        try:
            self._make_b1b_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
                 mock.patch.object(runner.voice01, "generate_charon_english", side_effect=_ok) as charon_mock, \
                 mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin",
                                    side_effect=_ok), \
                 mock.patch.object(runner.point_headings, "generate", side_effect=_ok):
                runner.generate_family_x_b1_segments(tmpdir)  # 既定backend

            preview_call = next(c for c in charon_mock.call_args_list if c.args and "Preview" in str(c.args[0]))
            self.assertEqual(preview_call.kwargs.get("style_prefix_override"), n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class A2RoleStyleFlashLiteTests(unittest.TestCase):
    """Standard(A2)はFAMILY-X-02(B-2)で新たに6-role styleが適用される。
    かつ既承認のA2_SLOWER_PACE_INSTRUCTION(6% post-process前提の速度調整
    仕様)が失われず、6-role styleと連結されることを確認する。"""

    def _make_a2_dir(self, tmpdir):
        parts = {
            "title": "Sample Title", "title_tts": "Sample Title",
            "part1": "Part one text.", "part2": "Body two text.", "heading1": "Heading One.", "body2": "Body two text.",
            "part3": "Body three text.", "heading2": "Heading Two.", "body3": "Body three text.", "in_one_line": "In one line text.",
        }
        support = {"preview": "プレビュー。", "comment_1": "コメント1。", "comment_2": "コメント2。",
                   "comment_3": "コメント3。", "comment_4": "コメント4。"}
        a2_dir = os.path.join(tmpdir, "a2")
        os.makedirs(a2_dir, exist_ok=True)
        with open(os.path.join(a2_dir, "parts.json"), "w", encoding="utf-8") as f:
            json.dump(parts, f)
        with open(os.path.join(a2_dir, "a2_support_texts.json"), "w", encoding="utf-8") as f:
            json.dump(support, f)
        return a2_dir

    def test_flash_lite_backend_combines_role_style_with_approved_slower_pace_instruction(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_role_style_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok) as topic_intro_mock, \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown",
                                    side_effect=_ok) as slowdown_mock:
                runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル",
                                                      tts_backend="speech_metadata_flash_lite")

            # topic_intro: role適用のみ(slowdown対象外)
            topic_intro_call = topic_intro_mock.call_args_list[0]
            self.assertEqual(topic_intro_call.kwargs.get("style_prefix_override"),
                              fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"])

            # full_story_part1/in_one_line/full_story_part2/3: role+slower連結、
            # 既承認instruction文言(逐語)を含む。
            expected_slower_suffix = n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()
            found_full_story = False
            found_in_one_line = False
            for call in slowdown_mock.call_args_list:
                style = call.kwargs.get("style_prefix_override") or ""
                self.assertIn(expected_slower_suffix, style,
                              f"既承認のA2_SLOWER_PACE_INSTRUCTION(逐語)が失われている: {style!r}")
                self.assertNotEqual(style, n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                                     "6-role styleが適用されず旧prefixのままになっている")
                if style.startswith(fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]):
                    found_full_story = True
                if style.startswith(fl_styles.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"]):
                    found_in_one_line = True
            self.assertTrue(found_full_story, "FULL_STORY roleが少なくとも1回適用されるはず")
            self.assertTrue(found_in_one_line, "IN_ONE_LINE roleが少なくとも1回適用されるはず")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_flash_lite_role_style_combined_with_slower_pace_is_wpm_guarded(self):
        # N-7是正(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02
        # 修正3回目、2026-09-28、Opus L2所見): legacy A2_ENGLISH_STYLE_
        # PREFIX_SLOWERはモジュール読み込み時にassert_no_wpm_specification()
        # で検査済みだが、_role_style_slower()の合成文字列(6-role短style+
        # 減速instruction)はガードされていなかった(非対称)。role style
        # 定数へ意図的にWPM数値指定を注入し、AssertionErrorが伝播する
        # (=ガードが実際に効いている)ことを確認する。
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_role_style_wpm_guard_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(fl_styles, "FAMILY_X_ROLE_STYLE_EN",
                                    {**fl_styles.FAMILY_X_ROLE_STYLE_EN,
                                     "FULL_STORY": "steady, 150 words per minute"}), \
                 mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok):
                with self.assertRaises(AssertionError):
                    runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル",
                                                          tts_backend="speech_metadata_flash_lite")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_default_backend_keeps_legacy_slower_prefix_unchanged(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_role_style_default_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown",
                                    side_effect=_ok) as slowdown_mock:
                runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル")  # 既定backend

            for call in slowdown_mock.call_args_list:
                self.assertEqual(call.kwargs.get("style_prefix_override"), n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class KeyPhraseBackendPropagationTests(unittest.TestCase):
    """C(ユーザー確定仕様): Key Phrase(shared_narration経由)へもtts_backend
    がそのまま伝播することを、B1/A2それぞれの_generate_key_phrase_
    segments_*経由で確認する。"""

    def test_b1_key_phrase_segments_receive_tts_backend(self):
        # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4、2026-09-29): Advanced
        # (b1b)Key Phraseの中間roleが日本語意味(generate_charon_japanese_
        # with_reading_safety)から英語解説(generate_key_phrase_explanation_
        # en_verified)へ変わったため、本testもtts_backend伝播先を追従させる
        # (tts_backend伝播という検証意図自体は無変更)。
        kp = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "見送る",
                          "display_phrase": "opt out", "source_sentence": "Users can opt out."}]}
        explanation_bundle = {"items": {1: {"english_explanation": "to choose not to take part",
                                             "qa": {"passed": True}, "status": "OK"}},
                               "audit": {}}
        with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=_ok) as en_mock, \
             mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=explanation_bundle), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                side_effect=_ok) as expl_mock:
            runner._generate_key_phrase_segments_b1(kp, "dummy_dir", tts_backend="speech_metadata_flash_lite")
        self.assertEqual(en_mock.call_args_list[0].kwargs.get("tts_backend"), "speech_metadata_flash_lite")
        self.assertEqual(expl_mock.call_args_list[0].kwargs.get("tts_backend"), "speech_metadata_flash_lite")

    def test_a2_key_phrase_segments_receive_tts_backend(self):
        kp = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "見送る"}]}
        with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=_ok) as en_mock, \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                side_effect=_ok) as ja_mock, \
             mock.patch.object(runner.n3_tts, "resolve_key_phrase_ja_gloss_tts",
                                return_value=("みおくる", False)):
            runner._generate_key_phrase_segments_a2(kp, "dummy_dir", tts_backend="speech_metadata_flash_lite")
        self.assertEqual(en_mock.call_args_list[0].kwargs.get("tts_backend"), "speech_metadata_flash_lite")
        self.assertEqual(ja_mock.call_args_list[0].kwargs.get("tts_backend"), "speech_metadata_flash_lite")

    def test_shared_narration_receives_tts_backend_for_b1_and_a2(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_kp_shared_narration_")
        try:
            os.makedirs(os.path.join(tmpdir, "b1b"), exist_ok=True)
            parts = {"title": "T", "part1": "P1.", "part2": "B2.", "part3": "B3.",
                     "heading1": "H1.", "body2": "B2.",
                     "heading2": "H2.", "body3": "B3.", "in_one_line": "IOL."}
            support = {"preview": "Pv.", "comment_1": "C1.", "comment_2": "C2.",
                       "comment_3": "C3.", "comment_4": "C4."}
            with open(os.path.join(tmpdir, "b1b", "parts.json"), "w", encoding="utf-8") as f:
                json.dump(parts, f)
            with open(os.path.join(tmpdir, "b1b", "b1_support_texts.json"), "w", encoding="utf-8") as f:
                json.dump(support, f)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1") as shared_mock, \
                 mock.patch.object(runner.voice01, "generate_charon_english", side_effect=_ok), \
                 mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin", side_effect=_ok), \
                 mock.patch.object(runner.point_headings, "generate", side_effect=_ok):
                runner.generate_family_x_b1_segments(tmpdir, tts_backend="speech_metadata_flash_lite")
            self.assertEqual(shared_mock.call_args.kwargs.get("tts_backend"), "speech_metadata_flash_lite")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (B1RoleStyleFlashLiteTests, A2RoleStyleFlashLiteTests, KeyPhraseBackendPropagationTests):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner_ = unittest.TextTestRunner(verbosity=2)
    result = runner_.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
