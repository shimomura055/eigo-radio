# ============================================================
# er019_family_x_variable_role_style_wiring_01_test_01.py
# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest \
#       er019_family_x_variable_role_style_wiring_01_test_01 -v
#
# API呼び出し: 0(実TTS/ASR呼び出しは全てmock)。¥0。
#
# 対象: ユーザー正式決定(JA=J3、EN=E2、APPROVED_FOR_PRODUCTION、
# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02)を、既存のPRODUCTION_WIRED
# 済み6-role style機構(speech_metadata_flash_lite backend限定)へ配線
# したことを確認する。
#   (a) FAMILY_X_ROLE_STYLE_JA / E2 3roleがer044のJ3/E2と逐語一致
#   (b) 既定backendではJA style overrideがNone(従来PREFIX)、Flash-Lite
#       明示時のみJ3
#   (c) generate_a2_japanese_with_reading_safetyの既定呼び出しが従来と
#       同一のprefix(None=JAPANESE_STYLE_PREFIX)を転送する
#   (d) shell固定phraseのstyle解決関数が本変更の影響を受けない(逐語不変)
#   (e) Key Phrase系Roleが無変更
#   (f) fallback経路がoverrideの影響を受けない(既存テキスト流用のまま)
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as n3_tts
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er019_family_x_audio_production_runner_01 as runner
import er033_tts_flash_lite_family_x_styles_01 as fl_styles
import er044_tts_variable_spoken_role_style_trial_02 as trial02


def _ok(*_a, **_kw):
    return {"status": "OK", "canonical_text": "x"}


class J3E2VerbatimMatchTests(unittest.TestCase):
    """(a) Production定数がTrial-02実測・ユーザー承認値と逐語一致すること。"""

    def test_family_x_role_style_ja_matches_trial02_j3_verbatim(self):
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_JA, trial02.J_PATTERN_STYLES["J3"])

    def test_family_x_role_style_en_e2_roles_match_trial02_verbatim(self):
        for role in ("TOPIC_INTRO", "FULL_STORY", "IN_ONE_LINE"):
            with self.subTest(role=role):
                self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN[role], trial02.E_PATTERN_STYLES[role]["E2"])

    def test_unaffected_en_roles_unchanged(self):
        # PREVIEW/COMMENT/HEADING_READOUTはE2未検証のため対象外(不変)。
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["PREVIEW"], "calm, conversational")
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["COMMENT"], "calm, conversational")
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"], "brief and clear")


class P9aJapaneseBranchSymmetryTests(unittest.TestCase):
    """p9a.generate_narration_snippet()のja分岐がen分岐と対称化されたこと
    (style_prefix_override or JAPANESE_STYLE_PREFIX)。"""

    def test_ja_default_override_none_uses_japanese_style_prefix(self):
        captured = {}

        def fake_call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None):
            captured["prompt"] = prompt
            return None, 0, False, "forced_stop_for_test"

        with mock.patch.object(p9a.common, "_call_tts_with_retry", side_effect=fake_call_tts_with_retry):
            p9a.generate_narration_snippet("こんにちは。", "ja", "dummy_out.wav")
        self.assertEqual(captured["prompt"], p9a.p4c.build_tts_prompt("こんにちは。", p9a.JAPANESE_STYLE_PREFIX))

    def test_ja_explicit_override_replaces_japanese_style_prefix(self):
        captured = {}

        def fake_call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None):
            captured["prompt"] = prompt
            return None, 0, False, "forced_stop_for_test"

        with mock.patch.object(p9a.common, "_call_tts_with_retry", side_effect=fake_call_tts_with_retry):
            p9a.generate_narration_snippet(
                "こんにちは。", "ja", "dummy_out.wav",
                style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA)
        self.assertEqual(
            captured["prompt"], p9a.p4c.build_tts_prompt("こんにちは。", fl_styles.FAMILY_X_ROLE_STYLE_JA))
        # 置換方式であること(長文PREFIXとの併記ではない、Trial-02と同一)。
        self.assertNotIn(p9a.JAPANESE_STYLE_PREFIX, captured["prompt"].replace(
            p9a.p4c.build_tts_prompt("こんにちは。", fl_styles.FAMILY_X_ROLE_STYLE_JA), ""))


class RunnerBackendGateTests(unittest.TestCase):
    """(b) Family Xランナーの_role_style_ja()相当の挙動: 既定backendでは
    Noneを転送(従来PREFIX維持)、Flash-Lite明示時のみJ3を転送する。"""

    def _make_a2_dir(self, tmpdir):
        parts = {
            "title": "Sample Title", "title_tts": "Sample Title",
            "part1": "Part one text.", "heading1": "Heading One.", "body2": "Body two text.",
            "heading2": "Heading Two.", "body3": "Body three text.", "in_one_line": "In one line text.",
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

    def test_flash_lite_backend_passes_j3_to_preview_and_comments_only(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_ja_role_style_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok) as ja_mock, \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok):
                runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル",
                                                      tts_backend="speech_metadata_flash_lite")

            # japanese_title(1回目の呼び出し)はTrial-02のJA_SEGMENTS対象外
            # =style_prefix_overrideを渡さない(既定None)。
            title_call = ja_mock.call_args_list[0]
            self.assertIsNone(title_call.kwargs.get("style_prefix_override"))

            # preview/comment_1〜4(2回目以降の呼び出し)はJ3を渡す。
            for call in ja_mock.call_args_list[1:]:
                self.assertEqual(call.kwargs.get("style_prefix_override"), fl_styles.FAMILY_X_ROLE_STYLE_JA)
            self.assertEqual(len(ja_mock.call_args_list), 6)  # japanese_title + preview + comment_1-4
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_default_backend_does_not_pass_j3_to_preview_and_comments(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_ja_role_style_default_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok) as ja_mock, \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok):
                runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル")  # 既定backend

            for call in ja_mock.call_args_list:
                self.assertIsNone(call.kwargs.get("style_prefix_override"))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class ReadingSafetyDefaultForwardingTests(unittest.TestCase):
    """(c) generate_a2_japanese_with_reading_safetyの既定呼び出しが従来と
    同一のprefix(override=None)をgenerate_a2_japanese_with_fallbackへ
    転送すること(モック)。"""

    def test_default_call_forwards_style_prefix_override_none(self):
        with mock.patch.object(n3_tts, "generate_a2_japanese_with_fallback",
                                side_effect=_ok) as fallback_mock:
            n3_tts.generate_a2_japanese_with_reading_safety("テスト文", "dummy.wav", "テス")
        self.assertIn("style_prefix_override", fallback_mock.call_args.kwargs)
        self.assertIsNone(fallback_mock.call_args.kwargs["style_prefix_override"])

    def test_explicit_override_forwarded_unchanged(self):
        with mock.patch.object(n3_tts, "generate_a2_japanese_with_fallback",
                                side_effect=_ok) as fallback_mock:
            n3_tts.generate_a2_japanese_with_reading_safety(
                "テスト文", "dummy.wav", "テス", style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA)
        self.assertEqual(fallback_mock.call_args.kwargs["style_prefix_override"], fl_styles.FAMILY_X_ROLE_STYLE_JA)


class ShellFixedPhraseUnaffectedTests(unittest.TestCase):
    """(d) 固定Master phrase(shell)のstyle解決関数が本変更の影響を受けない
    (逐語不変)ことを確認する。"""

    def test_shell_english_style_resolution_literal_unchanged(self):
        self.assertIsNone(shared_narration._resolve_shell_english_style_prefix_override("structured_separation"))
        self.assertEqual(
            shared_narration._resolve_shell_english_style_prefix_override("speech_metadata_flash_lite"),
            "natural, clear, conversational")
        # FAMILY_X_ROLE_STYLE_EN_FALLBACK自体もJ3/E2配線の対象外(不変)。
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK, ["natural, clear, conversational", "clear"])

    def test_shell_version_constant_unchanged(self):
        self.assertEqual(shared_narration.SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION,
                          "v2_flash_lite_short_style")


class KeyPhraseRoleUnchangedTests(unittest.TestCase):
    """(e) Key Phrase系(A2/B1双方)は本変更の対象外であり、
    generate_a2_japanese_with_reading_safety呼び出しにstyle_prefix_override
    を渡さない(=既存JAPANESE_STYLE_PREFIXのまま)ことを確認する。"""

    def test_a2_key_phrase_segments_do_not_receive_style_prefix_override(self):
        kp = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "見送る"}]}
        with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=_ok), \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                side_effect=_ok) as ja_mock, \
             mock.patch.object(runner.n3_tts, "resolve_key_phrase_ja_gloss_tts",
                                return_value=("みおくる", False)):
            runner._generate_key_phrase_segments_a2(kp, "dummy_dir", tts_backend="speech_metadata_flash_lite")
        self.assertNotIn("style_prefix_override", ja_mock.call_args_list[0].kwargs)


class FallbackPathUnaffectedTests(unittest.TestCase):
    """(f) fallback(minimal instruction)経路はstyle_prefix_overrideの
    影響を受けない(FAMILY-X-02 D-1の方針どおり、既存テキスト流用のまま)。"""

    def test_fallback_minimal_instruction_ignores_style_prefix_override(self):
        standard_stopped = {"status": "STOPPED", "reason": "forced", "attempts_log": []}
        with mock.patch.object(n3_tts.c, "generate_narration_snippet_verified_strict",
                                return_value=standard_stopped) as standard_mock, \
             mock.patch.object(n3_tts, "_generate_a2_japanese_minimal_instruction",
                                side_effect=_ok) as minimal_mock:
            n3_tts.generate_a2_japanese_with_fallback(
                "テスト文", "dummy.wav", "テス", style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA)
        # 標準経路へはoverrideが転送される。
        self.assertEqual(standard_mock.call_args.kwargs.get("style_prefix_override"),
                          fl_styles.FAMILY_X_ROLE_STYLE_JA)
        # fallback(minimal instruction)経路はstyle_prefix_overrideを一切
        # 受け取らない(既存テキスト_A2_JA_MINIMAL_INSTRUCTION_PREFIX流用のまま)。
        self.assertNotIn("style_prefix_override", minimal_mock.call_args.kwargs)


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        J3E2VerbatimMatchTests, P9aJapaneseBranchSymmetryTests, RunnerBackendGateTests,
        ReadingSafetyDefaultForwardingTests, ShellFixedPhraseUnaffectedTests,
        KeyPhraseRoleUnchangedTests, FallbackPathUnaffectedTests,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner_ = unittest.TextTestRunner(verbosity=2)
    result = runner_.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
