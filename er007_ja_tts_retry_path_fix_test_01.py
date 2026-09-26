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
# fallback1回=合計3回」へ固定した。
#
# ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26(同日、
# ユーザー正式決定・上記の一部方針を撤回): wiring-25では「callerが
# max_attemptsに6・10等を渡す既存呼び出し元の総予算は縮小しない」
# としていたが、これを撤回し、対象Production経路は例外なくTOTAL3回へ
# クランプする(caller指定によらない)よう変更した。
#
# 本ファイルはその正式仕様の回帰確認(Case A〜D、standard/fallback上限、
# caller指定max_attempts(6/10等)のTOTAL3への収束、Key Phrase専用
# 4回構成への非干渉)も合わせて持つ。
# ============================================================
from __future__ import annotations

import contextlib
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

    def test_larger_explicit_max_attempts_still_converges_to_total_three(self):
        """ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26(2026-09-04、
        ユーザー正式決定・wiring-25の「総予算6は縮小しない」方針を撤回):
        既存の呼び出し元(例: er006_audio_cost_pilot_02_shared_narration.
        ensure_fixed_japanese_segmentがmax_attempts=6を指定、または
        er003_v1_iran01_b1_kp_homophone_fix.pyがmax_attempts=10を指定)が
        あっても、対象Production経路は例外なくTOTAL3回(標準2+fallback1)へ
        クランプされる。"""
        cascade_results = [(False, False, "TRUE_CONTENT_MISMATCH")] * 3
        mock_tts, result = _run_generate_charon_japanese(cascade_results, max_attempts=6)

        self.assertEqual(mock_tts.call_count, 3, "max_attempts=6を渡してもTOTAL3でクランプされる")
        self.assertEqual(len(result["standard_attempts_log"]), 2)
        self.assertEqual(len(result["fallback_attempts_log"]), 1)
        self.assertEqual(result["status"], "STOPPED")

    def test_max_attempts_ten_also_converges_to_total_three(self):
        """er003_v1_iran01_b1_kp_homophone_fix.py実例(max_attempts=10)相当。"""
        cascade_results = [(False, False, "TRUE_CONTENT_MISMATCH")] * 3
        mock_tts, result = _run_generate_charon_japanese(cascade_results, max_attempts=10)

        self.assertEqual(mock_tts.call_count, 3, "max_attempts=10を渡してもTOTAL3でクランプされる")
        self.assertEqual(len(result["standard_attempts_log"]), 2)
        self.assertEqual(len(result["fallback_attempts_log"]), 1)
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

    def test_larger_max_attempts_still_converges_to_total_three(self):
        """ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26(2026-09-04、
        ユーザー正式決定・wiring-25の「総予算6は縮小しない」方針を撤回):
        既存の呼び出し元(例: generate_a2_japanese_with_reading_safetyの
        既定max_attempts=6)があっても、標準経路は常にstandard_attempts
        (既定2)回のみ、fallbackはPRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS
        (既定1)回のみへクランプされる(総予算6を維持しない)。"""
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
        self.assertEqual(mock_min.call_count, 1, "max_attempts=6を渡してもfallbackは1回でクランプされる")
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

    def test_larger_max_attempts_still_converges_to_total_three(self):
        """ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26: 英語側
        (Key Phrase以外)も、callerがmax_attempts=6等を渡してもTOTAL3へ
        クランプされる。"""
        realistic_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(crosslevel_common, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_attempts_log}) as mock_std, \
             mock.patch.object(crosslevel_common.repro01, "generate_english_component_minimal_instruction",
                                return_value={"status": "OK", "text": "test text", "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(crosslevel_common.routing, "transcribe", return_value=("test text", None)), \
             mock.patch.object(crosslevel_common.pronun_ledger, "get_hint_for_text", return_value=[]), \
             mock.patch.object(crosslevel_common.secondary_asr, "evaluate_attempt_with_cascade",
                                return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))):
            result = crosslevel_common.generate_english_segment_with_fallback(
                "test text", "dummy.wav", "test", max_attempts=6)

        self.assertEqual(mock_std.call_args.kwargs["max_attempts"], 2)
        self.assertEqual(mock_min.call_count, 1, "max_attempts=6を渡してもfallbackは1回でクランプされる")
        self.assertEqual(result["status"], "STOPPED")

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


class A2CooldownLocalRewriteWiringTests(unittest.TestCase):
    """TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01(修正1回目、
    Fable差し戻し対応): er003_v1_crosslevel_audio_02_common.
    generate_english_segment_with_fallback()のfallback(minimal
    instruction)経路へ配線したcool-down(er020_tts_retry_local_rewrite_01.
    maybe_cooldown_before_attempt、B1と同一のmodule関数)とLocal Rewrite
    回復(run_local_rewrite_recovery、同上)の回帰確認。"""

    REALISTIC_STANDARD_LOG = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]

    def _enter_base_mocks(self, stack):
        """standard(2回)+fallback(1回)がともにASR不一致で終わる状況を
        再現する、共通のmock(cool-down/Local Rewrite以外)を1つの
        contextlib.ExitStackへまとめて入れる(patch対象の重複を避ける)。"""
        stack.enter_context(mock.patch.object(
            crosslevel_common, "generate_narration_snippet_verified_strict",
            return_value={"status": "STOPPED", "attempts_log": list(self.REALISTIC_STANDARD_LOG)}))
        stack.enter_context(mock.patch.object(
            crosslevel_common.repro01, "generate_english_component_minimal_instruction",
            return_value={"status": "OK", "text": "test text", "path": "dummy.wav"}))
        stack.enter_context(mock.patch.object(
            crosslevel_common.routing, "transcribe", return_value=("wrong text", None)))
        stack.enter_context(mock.patch.object(
            crosslevel_common.pronun_ledger, "get_hint_for_text", return_value=[]))
        stack.enter_context(mock.patch.object(
            crosslevel_common.secondary_asr, "evaluate_attempt_with_cascade",
            return_value=(False, False, _fake_cls("TRUE_CONTENT_MISMATCH"))))

    def test_cooldown_not_invoked_when_connected_speech_disabled(self):
        """既存呼び出し元(enable_connected_speech_equivalence_layer=False
        既定)は、fallbackの3回目attemptに到達しても実sleepが一切発生しない
        (cooldown_gate_enabled=Falseのため即座にNoneを返すだけ)。"""
        with contextlib.ExitStack() as stack:
            self._enter_base_mocks(stack)
            mock_sleep = stack.enter_context(mock.patch("time.sleep"))
            result = crosslevel_common.generate_english_segment_with_fallback(
                "test text", "dummy_out.wav", "test", enable_connected_speech_equivalence_layer=False)
        mock_sleep.assert_not_called()
        self.assertEqual(result.get("cooldown_events"), [])

    def test_cooldown_invoked_before_fallback_when_connected_speech_enabled(self):
        """enable_connected_speech_equivalence_layer=Trueの場合、fallback
        (総予算3回の実質最終attempt)の直前でretry_primitive.
        maybe_cooldown_before_attempt(B1と同一のmodule関数)が実際に
        正しい引数(overall_attempt=3, max_attempts=3, gate=True)で呼ばれる
        ことを確認する。実sleepを避けるため、関数自体はwrapsで包み内部の
        sleep_fnだけ明示的にmockへ差し替える(maybe_cooldown_before_
        attempt自身がsleep_fnを引数化しているのはこのテストのため)。"""
        real_fn = crosslevel_common.retry_primitive.maybe_cooldown_before_attempt
        mock_sleep = mock.Mock()

        def _wrapped(attempt, max_attempts, cooldown_gate_enabled, sleep_fn=mock_sleep, **kw):
            return real_fn(attempt, max_attempts, cooldown_gate_enabled, sleep_fn=sleep_fn, **kw)

        with contextlib.ExitStack() as stack:
            self._enter_base_mocks(stack)
            mock_cooldown_fn = stack.enter_context(mock.patch.object(
                crosslevel_common.retry_primitive, "maybe_cooldown_before_attempt", side_effect=_wrapped))
            result = crosslevel_common.generate_english_segment_with_fallback(
                "test text", "dummy_out.wav", "test", enable_connected_speech_equivalence_layer=True)
        mock_sleep.assert_called_once_with(600.0)
        mock_cooldown_fn.assert_called_once_with(3, 3, True)
        self.assertEqual(len(result.get("cooldown_events") or []), 1,
                          "総予算3回のうちfallback(3回目)の直前で1回だけcool-downが発火する")
        self.assertEqual(result["cooldown_events"][0]["cooldown_requested_seconds"], 600.0)
        self.assertEqual(result["cooldown_events"][0]["attempt_after_cooldown"], 3)

    def test_local_rewrite_recovery_resolves_before_human_review(self):
        """Local Rewrite回復(run_local_rewrite_recovery)がRESOLVED_BY_
        LOCAL_REWRITEを返した場合、fallback失敗後もstatus="OK"のまま確定し
        (Human Review Lockへ進まない、ユーザー承認済み仕様D)、B1と同じ
        retry_primitive.run_local_rewrite_recoveryが実際に呼ばれる。"""
        recovered = {"status": "RESOLVED_BY_LOCAL_REWRITE",
                     "retts_result": {"status": "OK", "text": "rewritten", "path": "dummy_out.wav"}}
        with contextlib.ExitStack() as stack:
            self._enter_base_mocks(stack)
            stack.enter_context(mock.patch.object(
                crosslevel_common.retry_primitive, "maybe_cooldown_before_attempt", return_value=None))
            mock_recovery = stack.enter_context(mock.patch.object(
                crosslevel_common.retry_primitive, "run_local_rewrite_recovery", return_value=recovered))
            # _local_rewrite_recovery_for_english_segment_with_fallback()は
            # review_lock._has_valid_narration_layout()が標準layout
            # (".../<theme>/<level>/narration/<segment>.wav")の場合のみ
            # run_local_rewrite_recoveryを呼ぶ設計(B1の2ヘルパーと同じ
            # 安全設計)のため、テストでも標準layoutのpathを使う。
            result = crosslevel_common.generate_english_segment_with_fallback(
                "test text", "unittest_scratch_theme/a2/narration/test_segment.wav", "test",
                enable_connected_speech_equivalence_layer=True)
        self.assertTrue(mock_recovery.called)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result.get("local_rewrite_recovery"), recovered)
        self.assertTrue(result.get("fallback_used"))

    def test_local_rewrite_recovery_failure_still_reaches_human_review(self):
        """Local Rewrite回復が失敗(RESOLVED_BY_LOCAL_REWRITE以外)の場合は、
        従来通りSTOPPEDのままHuman Review Lockへ進む(B1と同一のHuman
        Review Lock到達条件)。"""
        failed_recovery = {"status": "HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA"}
        with contextlib.ExitStack() as stack:
            self._enter_base_mocks(stack)
            stack.enter_context(mock.patch.object(
                crosslevel_common.retry_primitive, "maybe_cooldown_before_attempt", return_value=None))
            mock_recovery = stack.enter_context(mock.patch.object(
                crosslevel_common.retry_primitive, "run_local_rewrite_recovery", return_value=failed_recovery))
            result = crosslevel_common.generate_english_segment_with_fallback(
                "test text", "unittest_scratch_theme/a2/narration/test_segment.wav", "test",
                enable_connected_speech_equivalence_layer=True)
        self.assertTrue(mock_recovery.called)
        self.assertEqual(result["status"], "STOPPED")
        self.assertNotIn("local_rewrite_recovery", result)

    def test_local_rewrite_recovery_not_attempted_when_connected_speech_disabled(self):
        """既存呼び出し元(enable_connected_speech_equivalence_layer=False
        既定)は、fallbackが失敗してもrun_local_rewrite_recovery自体が
        一切呼ばれない(既存挙動を変えない)。"""
        with contextlib.ExitStack() as stack:
            self._enter_base_mocks(stack)
            mock_recovery = stack.enter_context(mock.patch.object(
                crosslevel_common.retry_primitive, "run_local_rewrite_recovery"))
            result = crosslevel_common.generate_english_segment_with_fallback(
                "test text", "dummy_out.wav", "test", enable_connected_speech_equivalence_layer=False)
        mock_recovery.assert_not_called()
        self.assertEqual(result["status"], "STOPPED")


class A2TopicIntroConnectedSpeechRoleWiringTests(unittest.TestCase):
    """TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01(修正1回目):
    A2 topic_introが、B1(er003_v1_n3_01_tts_generate.generate_b1_segments)
    と同じくrole→適用判定を必ずretry_primitive.connected_speech_
    enabled_for()経由で参照すること(旧: 引数自体を渡していなかった漏れ)
    のregression guard(ソースベース確認、既存の`test_key_phrase_
    component_verified_does_not_reference_standard2_split`と同じ手法)。"""

    def test_a2_topic_intro_call_references_connected_speech_enabled_for(self):
        import inspect
        source = inspect.getsource(n3.generate_a2_segments)
        # topic_intro呼び出し直後にenable_connected_speech_equivalence_layer
        # 引数が渡されていることを確認する(ハードコードされたFalse/省略ではない)。
        topic_intro_block = source.split('results["topic_intro"]', 1)[1].split(")\n", 1)[0]
        self.assertIn("connected_speech_enabled_for", topic_intro_block)


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
