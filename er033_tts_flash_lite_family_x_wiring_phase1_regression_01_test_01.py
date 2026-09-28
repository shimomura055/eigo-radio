# ============================================================
# er033_tts_flash_lite_family_x_wiring_phase1_regression_01_test_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 1
# ============================================================
# ¥0、API呼び出し無し。既定backend("structured_separation")が、Phase 1で
# tts_backend引数を新規追加した各choke point関数において、既存呼び出し
# (tts_backendを一切渡さない既存Family A/B/C呼び出し元と同一の呼び方)と
# byte-identicalなprompt/call_fn構築を行うことを、
# `er002_common._call_tts_with_retry`をmockして検証する(実際のTTS/ASR
# APIは一切呼ばない)。out_pathには標準命名慣習に従わない単純な文字列
# ("dummy_out.wav")を使い、Human Review Lock(er011)を意図的にbypassする
# (既存test群と同じ確立済みパターン、er011_human_review_lock_01.
# _has_valid_narration_layoutのdocstring参照)。
from __future__ import annotations

import unittest
from unittest import mock

import er002_common as common
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01

DUMMY_OUT_PATH = "dummy_out.wav"


class _RecordingCallTtsWithRetry:
    """common._call_tts_with_retry()の差し替え。呼ばれた(call_fn, prompt)を
    全件記録し、常にok=Falseを返す(実TTS呼び出しをせず、STOPPED経路へ
    即座に進ませて後続コード[ASR/write_wav等]を一切実行させない)。"""

    def __init__(self):
        self.calls = []

    def __call__(self, tts_call_fn, prompt, max_retry=0, sleep_fn=None):
        self.calls.append((tts_call_fn, prompt))
        return None, 0, False, "forced_stop_for_test"


def _patched_retry():
    return mock.patch.object(common, "_call_tts_with_retry", new_callable=_RecordingCallTtsWithRetry)


class P9aGenerateNarrationSnippetDefaultBackendTests(unittest.TestCase):
    """既存呼び出し元(p9a.generate_narration_snippetをtts_backend無しで
    呼ぶ、既存Production/testの慣習)と同じ形。"""

    def test_english_default_backend_prompt_matches_legacy(self):
        recorder = _patched_retry()
        with recorder as fake:
            result = p9a.generate_narration_snippet("Hello there.", "en", DUMMY_OUT_PATH)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("Hello there.", p9a.ENGLISH_STYLE_PREFIX))

    def test_japanese_default_backend_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            result = p9a.generate_narration_snippet("こんにちは。", "ja", DUMMY_OUT_PATH)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("こんにちは。", p9a.JAPANESE_STYLE_PREFIX))

    def test_explicit_tts_call_fn_bypasses_backend_branch_unchanged(self):
        # 既存呼び出し元(repro01.generate_narration_snippet_verified_strict
        # 等)はtts_call_fnを明示的に渡す。この経路はtts_backend分岐を
        # 経由しない(既存挙動、設計書§(a-3)のtts_call_fn is not None分岐)。
        sentinel_call_fn = object()
        with _patched_retry() as fake:
            p9a.generate_narration_snippet(
                "Hello.", "en", DUMMY_OUT_PATH, tts_call_fn=sentinel_call_fn)
        self.assertIs(fake.calls[0][0], sentinel_call_fn)


class VoiceCharonEnglishDefaultBackendTests(unittest.TestCase):
    def test_standard_attempt_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            result = voice01.generate_charon_english("Topic intro text.", DUMMY_OUT_PATH, max_attempts=1)
        self.assertEqual(result["status"], "STOPPED")
        # 1attempt内でstandard+fallbackの2回_call_tts_with_retryが呼ばれる。
        self.assertEqual(len(fake.calls), 2)
        _, standard_prompt = fake.calls[0]
        self.assertEqual(standard_prompt, p4c.build_tts_prompt("Topic intro text.", p9a.ENGLISH_STYLE_PREFIX))
        _, fallback_prompt = fake.calls[1]
        self.assertEqual(fallback_prompt, p4c.build_tts_prompt("Topic intro text.", repro01.MINIMAL_INSTRUCTION_PREFIX))

    def test_style_prefix_override_still_applied_to_standard_attempt(self):
        with _patched_retry() as fake:
            voice01.generate_charon_english(
                "Preview text.", DUMMY_OUT_PATH, max_attempts=1,
                style_prefix_override=n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM)
        _, standard_prompt = fake.calls[0]
        self.assertEqual(
            standard_prompt, p4c.build_tts_prompt("Preview text.", n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM))


class VoiceCharonEnglishFlashLiteFallbackStyleTests(unittest.TestCase):
    """TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(BL-3、
    修正3回目、2026-09-28、Opus L2所見): tts_backend=
    "speech_metadata_flash_lite"の場合、fallback(発話区間検出失敗時の
    minimal instruction)発火時のspeech_metadata.styleが、既存の長い
    repro01.MINIMAL_INSTRUCTION_PREFIXではなく、
    `er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN_
    FALLBACK[0]`であることを確認する(Repro01MinimalInstruction
    FlashLiteFallbackStyleTestsと同じ検証パターンをvoice01側へ適用)。
    既定backendはVoiceCharonEnglishDefaultBackendTestsでbyte-identicalの
    ままであることを別途確認済み(無影響)。"""

    def test_flash_lite_backend_uses_short_fallback_style_not_legacy_minimal_prefix(self):
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        with _patched_retry() as fake:
            voice01.generate_charon_english(
                "Topic intro text.", DUMMY_OUT_PATH, max_attempts=1,
                tts_backend="speech_metadata_flash_lite")
        self.assertEqual(len(fake.calls), 2)
        _, fallback_prompt = fake.calls[1]
        text, style = fallback_prompt
        self.assertEqual(text, "Topic intro text.")
        self.assertEqual(style, fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])
        self.assertNotEqual(style, repro01.MINIMAL_INSTRUCTION_PREFIX)


class VoiceCharonJapaneseDefaultBackendTests(unittest.TestCase):
    def test_standard_attempt_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            result = voice01.generate_charon_japanese(
                "こんにちは、世界。", DUMMY_OUT_PATH, "こんにちは", standard_attempts=1, max_attempts=1)
        self.assertEqual(result["status"], "STOPPED")
        self.assertGreaterEqual(len(fake.calls), 1)
        _, standard_prompt = fake.calls[0]
        self.assertEqual(standard_prompt, p4c.build_tts_prompt("こんにちは、世界。", p9a.JAPANESE_STYLE_PREFIX))

    def test_minimal_instruction_fallback_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            voice01.generate_charon_japanese_minimal_instruction("こんにちは。", DUMMY_OUT_PATH)
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("こんにちは。", voice01.MINIMAL_INSTRUCTION_PREFIX_JA))


class Repro01MinimalInstructionDefaultBackendTests(unittest.TestCase):
    def test_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            repro01.generate_english_component_minimal_instruction("Some phrase.", DUMMY_OUT_PATH)
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("Some phrase.", repro01.MINIMAL_INSTRUCTION_PREFIX))


class Repro01MinimalInstructionFlashLiteFallbackStyleTests(unittest.TestCase):
    """TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(D-1、
    2026-09-28): tts_backend="speech_metadata_flash_lite"の場合、fallback
    (minimal instruction)発火時のspeech_metadata.styleが、既存の長い
    MINIMAL_INSTRUCTION_PREFIX(legacy structured separation専用の
    "warm podcast announcer voice"指示)ではなく、
    `er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN_
    FALLBACK[0]`(短いTrial実測済みfallback style)であることを確認する。
    既定backend(structured_separation)は上記
    Repro01MinimalInstructionDefaultBackendTestsでbyte-identicalのまま
    であることを別途確認済み(無影響)。"""

    def test_flash_lite_backend_uses_short_fallback_style_not_legacy_minimal_prefix(self):
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        with _patched_retry() as fake:
            repro01.generate_english_component_minimal_instruction(
                "Some phrase.", DUMMY_OUT_PATH, tts_backend="speech_metadata_flash_lite")
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        text, style = prompt
        self.assertEqual(text, "Some phrase.")
        self.assertEqual(style, fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])
        self.assertNotEqual(style, repro01.MINIMAL_INSTRUCTION_PREFIX)


class NewsTailFixDefaultBackendTests(unittest.TestCase):
    def test_standard_attempt_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            result = news_tail_fix.generate_news_narration_wide_margin(
                "Full story text.", DUMMY_OUT_PATH, max_attempts=1)
        self.assertEqual(result["status"], "STOPPED")
        # 1attempt内で標準+fallback(repro01.generate_english_component_
        # minimal_instruction経由)の2回_call_tts_with_retryが呼ばれる。
        self.assertEqual(len(fake.calls), 2)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("Full story text.", p9a.ENGLISH_STYLE_PREFIX))
        _, fallback_prompt = fake.calls[1]
        self.assertEqual(fallback_prompt, p4c.build_tts_prompt("Full story text.", repro01.MINIMAL_INSTRUCTION_PREFIX))

    def test_style_prefix_override_new_param_defaults_to_none_unchanged(self):
        # 新規追加のstyle_prefix_override引数を渡さない既存呼び出し元は
        # 無変更のまま(既定None=p9a.ENGLISH_STYLE_PREFIX)。
        with _patched_retry() as fake:
            news_tail_fix.generate_news_narration_wide_margin(
                "Text.", DUMMY_OUT_PATH, max_attempts=1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("Text.", p9a.ENGLISH_STYLE_PREFIX))

    def test_explicit_style_prefix_override_is_applied(self):
        with _patched_retry() as fake:
            news_tail_fix.generate_news_narration_wide_margin(
                "Text.", DUMMY_OUT_PATH, max_attempts=1, style_prefix_override="calm, steady news narration")
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("Text.", "calm, steady news narration"))


class PointHeadingsDefaultBackendTests(unittest.TestCase):
    def test_standard_attempt_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            result = point_headings.generate("Point One.", DUMMY_OUT_PATH, max_attempts=1)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("Point One.", p9a.ENGLISH_STYLE_PREFIX))


class PointHeadingsFlashLiteFallbackStyleTests(unittest.TestCase):
    """TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(BL-3、
    修正3回目、2026-09-28、Opus L2所見): point_headings.generate()の
    minimal_fallback(attempt > minimal_after)経路も、tts_backend=
    "speech_metadata_flash_lite"の場合はFAMILY_X_ROLE_STYLE_EN_
    FALLBACK[0]を使う(既定backendはPointHeadingsDefaultBackendTestsで
    byte-identicalのまま無変更)。"""

    def test_flash_lite_backend_uses_short_fallback_style_on_minimal_fallback_attempt(self):
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        with _patched_retry() as fake:
            point_headings.generate(
                "Point One.", DUMMY_OUT_PATH, max_attempts=2,
                tts_backend="speech_metadata_flash_lite")
        # attempt1=standard(english_style_prefix)、attempt2=minimal_fallback。
        self.assertEqual(len(fake.calls), 2)
        _, fallback_prompt = fake.calls[1]
        text, style = fallback_prompt
        self.assertEqual(text, "Point One.")
        self.assertEqual(style, fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])
        self.assertNotEqual(style, repro01.MINIMAL_INSTRUCTION_PREFIX)


class A2JapaneseMinimalInstructionDefaultBackendTests(unittest.TestCase):
    def test_prompt_matches_legacy(self):
        with _patched_retry() as fake:
            n3_tts._generate_a2_japanese_minimal_instruction("短い日本語。", DUMMY_OUT_PATH)
        self.assertEqual(len(fake.calls), 1)
        _, prompt = fake.calls[0]
        self.assertEqual(prompt, p4c.build_tts_prompt("短い日本語。", n3_tts._A2_JA_MINIMAL_INSTRUCTION_PREFIX))


class TtsBackendSignatureBackwardCompatibilityTests(unittest.TestCase):
    """新規tts_backend引数が、既存の位置引数呼び出し・既存keyword引数の
    どちらにも影響しない(既定値付きkeyword-onlyまたは末尾引数として
    追加されている)ことを、実際の呼び出しで確認する(署名検査ではなく
    実挙動で確認する、値の取り違えを検出するため)。"""

    def test_generate_charon_english_positional_call_unaffected(self):
        with _patched_retry():
            result = voice01.generate_charon_english("Text.", DUMMY_OUT_PATH)
        self.assertIn(result["status"], ("STOPPED", "ASR_VALIDATION_UNCERTAIN"))

    def test_generate_news_narration_wide_margin_positional_call_unaffected(self):
        with _patched_retry():
            result = news_tail_fix.generate_news_narration_wide_margin("Text.", DUMMY_OUT_PATH)
        self.assertIn(result["status"], ("STOPPED", "ASR_VALIDATION_UNCERTAIN"))


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        P9aGenerateNarrationSnippetDefaultBackendTests, VoiceCharonEnglishDefaultBackendTests,
        VoiceCharonEnglishFlashLiteFallbackStyleTests,
        VoiceCharonJapaneseDefaultBackendTests, Repro01MinimalInstructionDefaultBackendTests,
        Repro01MinimalInstructionFlashLiteFallbackStyleTests,
        NewsTailFixDefaultBackendTests, PointHeadingsDefaultBackendTests,
        PointHeadingsFlashLiteFallbackStyleTests,
        A2JapaneseMinimalInstructionDefaultBackendTests, TtsBackendSignatureBackwardCompatibilityTests,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
