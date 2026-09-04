# ============================================================
# er007_ja_tts_retry_path_fix_test_01.py
# ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part A:
# stop_retrying=True後にTTS再生成が止まることを、実TTS/ASRを一切呼ばず
# mockで確認する(受入条件A-3: TTS生成回数=1)。
#
# ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25(2026-09-04、
# ユーザー正式決定)で、標準経路+minimal instruction fallback経路を持つ
# 3関数(generate_charon_japanese/generate_a2_japanese_with_fallback/
# generate_english_segment_with_fallback)の試行回数配分を「標準2回+
# fallback1回=合計3回」へ固定した。本ファイルはその正式仕様の回帰確認
# (Case A〜D、standard/fallback上限、Key Phrase専用4回構成への非干渉)
# も合わせて持つ。
# ============================================================
from __future__ import annotations

import types
import unittest
from unittest import mock

import numpy as np

import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_n3_01_tts_generate as n3
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01
import er011_human_review_lock_01 as review_lock

_DUMMY_TRIM_INFO = {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0}


def _fake_cls(classification: str):
    return types.SimpleNamespace(classification=classification)


class SharedBudgetConstantsTests(unittest.TestCase):
    """ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25で新設した
    review_lockの内訳定数(SSOT)が、正式決定通りの値であることを保証
    する。"""

    def test_standard_plus_fallback_equals_total(self):
        self.assertEqual(review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS, 2)
        self.assertEqual(review_lock.PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS, 1)
        self.assertEqual(review_lock.PRODUCTION_MAX_TTS_ATTEMPTS, 3)
        self.assertEqual(
            review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS + review_lock.PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS,
            review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)


def _run_generate_charon_japanese(cascade_results, **kwargs):
    """cascade_results: [(verified_content, stop_retrying, classification_str), ...]を
    呼び出し順(標準経路の各attempt→fallback経路の各attempt)で
    ja_secondary.evaluate_attempt_ja_with_cascadeの戻り値として消費する。"""
    with mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn",
                            return_value=lambda *a, **k: None), \
         mock.patch.object(voice01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
         mock.patch.object(voice01.common, "_call_tts_with_retry",
                            return_value=(b"pcm", 0, True, None)) as mock_tts, \
         mock.patch.object(voice01.common, "pcm_bytes_to_float_mono",
                            return_value=np.zeros(100, dtype=np.float32)), \
         mock.patch.object(voice01.p3u, "trim_english_keyword_silence",
                            return_value=(np.zeros(100, dtype=np.float32), dict(_DUMMY_TRIM_INFO))), \
         mock.patch.object(voice01.safety, "detect_duration_anomaly",
                            return_value={"is_anomaly": False}), \
         mock.patch.object(voice01.common, "write_wav_float", return_value=None), \
         mock.patch.object(voice01.common, "measure_metrics",
                            return_value={"clipping_detected": False}), \
         mock.patch.object(voice01.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
         mock.patch.object(voice01.ja_secondary, "evaluate_attempt_ja_with_cascade",
                            side_effect=[(v, s, _fake_cls(c)) for (v, s, c) in cascade_results]):
        result = voice01.generate_charon_japanese("テスト文", "dummy_out.wav", "テス", **kwargs)
    return mock_tts, result


class VoiceCharonJapaneseStandard2Fallback1Tests(unittest.TestCase):
    """er003_v1_sing01_voice01_generate.generate_charon_japanese()"""

    def test_stop_retrying_true_tts_call_count_is_exactly_one(self):
        """Cascadeがstop_retrying=Trueを返したら、標準経路1回だけでTTSを
        打ち切り、attempt 2以降(フォールバック経路含む)へ進まないこと
        (受入条件A-3)。"""
        mock_tts, result = _run_generate_charon_japanese(
            [(False, True, "ASR_VALIDATION_UNCERTAIN")], max_attempts=6)

        self.assertEqual(mock_tts.call_count, 1,
                          "stop_retrying=True後にTTSが再生成されてはいけない(受入条件A-3)")
        self.assertEqual(result["status"], "ASR_VALIDATION_UNCERTAIN")
        self.assertFalse(result["asr_verified"])

    def test_case_a_standard_pass_on_first_attempt_stops_at_one_call(self):
        """Case A: 標準1回目PASS→1回で終了。"""
        mock_tts, result = _run_generate_charon_japanese([(True, False, "MATCH")])

        self.assertEqual(mock_tts.call_count, 1)
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertFalse(result["fallback_used"])

    def test_case_b_standard_ng_then_pass_stops_at_two_calls(self):
        """Case B: 標準1 NG、標準2 PASS→2回で終了(fallbackは呼ばれない)。"""
        mock_tts, result = _run_generate_charon_japanese([
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (True, False, "MATCH"),
        ])

        self.assertEqual(mock_tts.call_count, 2)
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertFalse(result["fallback_used"])

    def test_case_c_standard_exhausted_fallback_fires_and_passes_as_third_attempt(self):
        """Case C: 標準1 NG、標準2 NG、Fallback PASS→3回目がMinimal
        instructionとして実際に発火し、標準2回+fallback1回=合計3回で
        採用される。旧仕様(標準経路がmax_attempts全てを消費)ではこの
        3回目(fallback)が絶対に発火しなかった(fallback_budget=0固定
        バグ)。"""
        mock_tts, result = _run_generate_charon_japanese([
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (True, False, "MATCH"),
        ])

        self.assertEqual(mock_tts.call_count, 3,
                          "標準2回+fallback1回(3回目に実際にminimal instructionが発火)")
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertTrue(result["fallback_used"], "3回目はfallback(minimal instruction)経由での採用")
        self.assertEqual(len(result["standard_attempts_log"]), 2)
        self.assertEqual(len(result["fallback_attempts_log"]), 1)

    def test_case_d_standard_and_fallback_both_ng_stops_with_total_three_attempts(self):
        """Case D: 標準1 NG、標準2 NG、Fallback NG→3回でSTOP(fail-closed、
        誤った音声を採用しない)。"""
        mock_tts, result = _run_generate_charon_japanese([
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
        ])

        self.assertEqual(mock_tts.call_count, 3)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(result["standard_attempts_log"]), 2)
        self.assertEqual(len(result["fallback_attempts_log"]), 1)

    def test_standard_attempts_never_exceed_two_by_default(self):
        _, result = _run_generate_charon_japanese([
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
        ])
        self.assertLessEqual(len(result["standard_attempts_log"]), review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS)

    def test_fallback_attempts_never_exceed_one_by_default(self):
        _, result = _run_generate_charon_japanese([
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
            (False, False, "TRUE_CONTENT_MISMATCH"),
        ])
        self.assertLessEqual(len(result["fallback_attempts_log"]),
                              review_lock.PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS)

    def test_larger_explicit_max_attempts_still_caps_standard_at_two_but_expands_fallback(self):
        """既存の呼び出し元(例: er006_audio_cost_pilot_02_shared_narration.
        ensure_fixed_japanese_segmentがmax_attempts=6を指定)がある場合でも、
        標準経路は常にstandard_attempts(既定2)回のみで、差分(6-2=4回)は
        fallbackへ回る。総予算6は変更しない(該当しない別用途を勝手に
        3回へ縮小しない)一方、fallbackが常に0固定だった不具合は解消
        される。"""
        cascade_results = [(False, False, "TRUE_CONTENT_MISMATCH")] * 6
        mock_tts, result = _run_generate_charon_japanese(cascade_results, max_attempts=6)

        self.assertEqual(mock_tts.call_count, 6)
        self.assertEqual(len(result["standard_attempts_log"]), 2)
        self.assertEqual(len(result["fallback_attempts_log"]), 4)
        self.assertEqual(result["status"], "STOPPED")


class A2JapaneseFallbackStandard2Fallback1Tests(unittest.TestCase):
    """er003_v1_n3_01_tts_generate.generate_a2_japanese_with_fallback()の
    自前フォールバック経路(minimal instruction)。"""

    def test_standard_pass_returns_immediately_without_fallback(self):
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "OK", "attempts_log": [{"attempt": 1}]}) as mock_std, \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction") as mock_min:
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス")

        mock_std.assert_called_once()
        self.assertEqual(mock_std.call_args.kwargs["max_attempts"], 2,
                          "標準経路にはPRODUCTION_STANDARD_TTS_ATTEMPTS(2)回分の予算しか渡さない")
        mock_min.assert_not_called()
        self.assertFalse(result["fallback_used"])

    def test_stop_retrying_true_minimal_instruction_called_exactly_once(self):
        # 標準経路が実際に(早期returnせず)2回消費した現実的なattempts_log。
        # 旧テストの空リストmockはfallback_budgetが常に0になる不具合を
        # 隠していたため、実際の長さに揃える。
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}), \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(n3.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, True, _fake_cls("ASR_VALIDATION_UNCERTAIN"))):
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス")

        self.assertEqual(mock_min.call_count, 1,
                          "stop_retrying=True後にTTS(minimal instruction)が再生成されてはいけない(受入条件A-3)")
        self.assertEqual(result["status"], "ASR_VALIDATION_UNCERTAIN")
        self.assertFalse(result["asr_verified"])

    def test_fallback_fires_and_passes_as_third_attempt(self):
        """Case C相当: 標準2回消費後、fallback予算1回で実際に発火・合格する。"""
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}), \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(n3.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(True, False, _fake_cls("MATCH"))):
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス")

        self.assertEqual(mock_min.call_count, 1,
                          "標準経路2回消費後、fallback予算は1回(PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS)")
        self.assertTrue(result["asr_verified"])
        self.assertTrue(result["fallback_used"])

    def test_fallback_ng_stops_with_total_three_attempts(self):
        """Case D相当: 標準2回+fallback1回(合計上限3回)とも不合格でSTOP。"""
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}), \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(n3.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))):
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス")

        self.assertEqual(mock_min.call_count, 1,
                          "fallback予算は1回のみ(旧仕様では残り予算=max_attempts-2=1のはずが、"
                          "標準経路がmax_attempts全消費のため実際は0だった)")
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(realistic_attempts_log) + mock_min.call_count, 3, "総試行回数(標準2+fallback1)は3")

    def test_larger_max_attempts_still_expands_fallback_not_standard(self):
        """既存の呼び出し元(例: max_attempts=6)がある場合でも、標準経路は
        常にstandard_attempts(既定2)回のみで、差分がfallbackへ回る
        (総予算6は変更しないが、fallbackが0固定だった不具合は解消される)。"""
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}) as mock_std, \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=("ダミー書き起こし", None)), \
             mock.patch.object(n3.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))):
            result = n3.generate_a2_japanese_with_fallback("テスト文", "dummy.wav", "テス", max_attempts=6)

        self.assertEqual(mock_std.call_args.kwargs["max_attempts"], 2)
        self.assertEqual(mock_min.call_count, 4, "6-2=4回がfallbackへ")
        self.assertEqual(result["status"], "STOPPED")


class EnglishSegmentFallbackStandard2Fallback1Tests(unittest.TestCase):
    """er003_v1_crosslevel_audio_02_common.generate_english_segment_with_
    fallback()(Key Phrase以外の英語ナレーションsegment用fallback。日本語
    側の2関数と同じER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25の
    対象)。"""

    def test_standard_pass_returns_immediately_without_fallback(self):
        with mock.patch.object(crosslevel_common, "generate_narration_snippet_verified_strict",
                                return_value={"status": "OK", "attempts_log": [{"attempt": 1}]}) as mock_std, \
             mock.patch.object(crosslevel_common.repro01, "generate_english_component_minimal_instruction") as mock_min:
            result = crosslevel_common.generate_english_segment_with_fallback("test text", "dummy.wav", "test")

        self.assertEqual(mock_std.call_args.kwargs["max_attempts"], 2,
                          "標準経路にはPRODUCTION_STANDARD_TTS_ATTEMPTS(2)回分の予算しか渡さない")
        mock_min.assert_not_called()
        self.assertFalse(result["fallback_used"])

    def test_fallback_fires_and_passes_as_third_attempt(self):
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(crosslevel_common, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}), \
             mock.patch.object(crosslevel_common.repro01, "generate_english_component_minimal_instruction",
                                return_value={"status": "OK", "text": "test text", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(crosslevel_common.routing, "transcribe", return_value=("test text", None)), \
             mock.patch.object(crosslevel_common.pronun_ledger, "get_hint_for_text", return_value=[]), \
             mock.patch.object(crosslevel_common.secondary_asr, "evaluate_attempt_with_cascade",
                                return_value=(True, False, _fake_cls("MATCH"))):
            result = crosslevel_common.generate_english_segment_with_fallback("test text", "dummy.wav", "test")

        self.assertEqual(mock_min.call_count, 1,
                          "標準経路2回消費後、fallback予算は1回(PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS)")
        self.assertTrue(result["asr_verified"])
        self.assertTrue(result["fallback_used"])

    def test_fallback_ng_stops_with_total_three_attempts(self):
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(crosslevel_common, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}), \
             mock.patch.object(crosslevel_common.repro01, "generate_english_component_minimal_instruction",
                                return_value={"status": "OK", "text": "test text", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(crosslevel_common.routing, "transcribe", return_value=("test text", None)), \
             mock.patch.object(crosslevel_common.pronun_ledger, "get_hint_for_text", return_value=[]), \
             mock.patch.object(crosslevel_common.secondary_asr, "evaluate_attempt_with_cascade",
                                return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))):
            result = crosslevel_common.generate_english_segment_with_fallback("test text", "dummy.wav", "test")

        self.assertEqual(mock_min.call_count, 1)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(realistic_attempts_log) + mock_min.call_count, 3, "総試行回数(標準2+fallback1)は3")

    def test_human_review_locked_standard_never_reaches_fallback(self):
        """ER-011-HUMAN-REVIEW-COST-GUARD-01: standard経路がHuman Review
        Lockでブロックされた場合、今回の変更後もfallbackへは進まない
        (fallbackは未ガードの直接TTS/ASR呼び出しのため)。"""
        with mock.patch.object(crosslevel_common, "generate_narration_snippet_verified_strict",
                                return_value={"status": "HUMAN_REVIEW_LOCKED", "attempts_log": []}), \
             mock.patch.object(crosslevel_common.repro01,
                                "generate_english_component_minimal_instruction") as mock_min:
            result = crosslevel_common.generate_english_segment_with_fallback("test text", "dummy.wav", "test")

        mock_min.assert_not_called()
        self.assertFalse(result["fallback_used"])


class KeyPhraseSpecUnaffectedTests(unittest.TestCase):
    """ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25は、Key Phrase
    英語Component専用の独立した4回構成(ER-010-NO9-KEYPHRASE-MINIMAL-
    ENGLISHLOCK-PRODUCTION-WIRING-22、Primary Minimal最大2+English Lock
    Fallback最大2=合計4)には一切影響しないことを保証するregression
    guard(§11 Dangling Reference Check相当)。"""

    def test_key_phrase_total_max_attempts_still_four(self):
        self.assertEqual(repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS, 2)
        self.assertEqual(repro01.KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS, 2)
        self.assertEqual(repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS, 4)

    def test_key_phrase_component_verified_does_not_reference_standard2_split(self):
        import inspect
        source = inspect.getsource(repro01.generate_key_phrase_component_verified)
        self.assertNotIn("PRODUCTION_STANDARD_TTS_ATTEMPTS", source)
        self.assertNotIn("standard_attempts", source)


if __name__ == "__main__":
    unittest.main()
