# ============================================================
# er007_reading_validation_wiring_test_01.py
# NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b:
# expected_readings(辞書登録トークンの確定読み)が、B1(voice01.
# generate_charon_japanese)・A2/共有(repro01.generate_narration_snippet_
# verified_strict、ja分岐のみ)経由でja_secondary.evaluate_attempt_ja_
# with_cascade()まで正しく転送されること、英語分岐(language="en")には
# 一切影響しないことを、TTS/ASRを全てmockした状態で確認する(実API呼び出し
# なし)。
# ============================================================
from __future__ import annotations

import os
import shutil
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01

_DUMMY_TRIM_INFO = {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0}


def _fake_cls(classification: str):
    return types.SimpleNamespace(classification=classification)


class Voice01CharonExpectedReadingsForwardingTests(unittest.TestCase):
    """B1経路(voice01.generate_charon_japanese)の標準経路・fallback経路
    両方が、expected_readingsをja_secondary.evaluate_attempt_ja_with_
    cascade()へそのまま転送すること。"""

    def _run(self, cascade_results, **kwargs):
        with mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn",
                                return_value=lambda *a, **k: None), \
             mock.patch.object(voice01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
             mock.patch.object(voice01.common, "_call_tts_with_retry",
                                return_value=(b"pcm", 0, True, None)), \
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
                                side_effect=[(v, s, _fake_cls(c)) for (v, s, c) in cascade_results]) as mock_cascade:
            result = voice01.generate_charon_japanese("テスト文", "dummy_out.wav", "テス", **kwargs)
        return mock_cascade, result

    def test_standard_path_forwards_expected_readings(self):
        mock_cascade, result = self._run(
            [(True, False, "PHONETIC_MATCH")], expected_readings={"meta": "メタ"})
        self.assertEqual(mock_cascade.call_count, 1)
        self.assertEqual(mock_cascade.call_args.kwargs.get("expected_readings"), {"meta": "メタ"})
        self.assertTrue(result["asr_verified"])

    def test_fallback_path_forwards_expected_readings(self):
        # 標準経路2回とも不合格(entity-like等でstop_retryingはFalse)→
        # fallback(minimal instruction)経路が発火し、そちらの
        # evaluate_attempt_ja_with_cascade呼び出しにもexpected_readingsが
        # 転送されること。
        with mock.patch.object(voice01, "generate_charon_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "テスト文", "path": "dummy_out.wav"}):
            mock_cascade, result = self._run(
                [(False, False, "TRUE_CONTENT_MISMATCH"), (False, False, "TRUE_CONTENT_MISMATCH"),
                 (True, False, "PHONETIC_MATCH")],
                expected_readings={"meta": "メタ"})
        self.assertEqual(mock_cascade.call_count, 3)
        for call in mock_cascade.call_args_list:
            self.assertEqual(call.kwargs.get("expected_readings"), {"meta": "メタ"})
        self.assertTrue(result["asr_verified"])
        self.assertTrue(result["fallback_used"])

    def test_default_none_unchanged(self):
        mock_cascade, result = self._run([(True, False, "PHONETIC_MATCH")])
        self.assertIsNone(mock_cascade.call_args.kwargs.get("expected_readings"))


class Repro01JaBranchExpectedReadingsForwardingTests(unittest.TestCase):
    """repro01.generate_narration_snippet_verified_strict()のja分岐が
    expected_readingsをja_secondary.evaluate_attempt_ja_with_cascade()へ
    転送すること。英語分岐(language="en")は無変更(expected_readings自体を
    受け取っても、日本語専用のja_secondary呼び出しには一切関与しない)。
    review_lock guard(check_before_generation等のファイルI/O)を避けるため
    .__wrapped__で素の関数を直接呼ぶ(既存er011_tts_attempt_audio_
    retention_wiring_01_test.pyと同じ手法)。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er007_reading_validation_wiring_test_")
        self.out_path = os.path.join(self.tmp_dir, "dummy_out.wav").replace("\\", "/")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _fake_generate_narration_snippet(self, text, language, out_path, tts_call_fn=None,
                                          safety_margin_seconds=None, style_prefix_override=None):
        with open(out_path, "wb") as f:
            f.write(b"FAKE_AUDIO")
        return {"status": "OK", "text": text, "language": language, "path": out_path,
                "duration_seconds": 1.0}

    def test_ja_branch_forwards_expected_readings(self):
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=self._fake_generate_narration_snippet), \
             mock.patch.object(repro01.routing, "transcribe", return_value=("メタが説明しました", None)), \
             mock.patch.object(repro01.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(True, False, _fake_cls("PHONETIC_MATCH"))) as mock_cascade:
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("Metaが説明しました", "ja", self.out_path, "Meta",
                           max_attempts=3, expected_readings={"meta": "メタ"})
        self.assertEqual(result["status"], "OK")
        mock_cascade.assert_called_once()
        self.assertEqual(mock_cascade.call_args.kwargs.get("expected_readings"), {"meta": "メタ"})

    def test_en_branch_unaffected_by_expected_readings_argument(self):
        # language="en"の場合、expected_readingsを渡してもja_secondary側の
        # 呼び出しは一切発生せず(そもそもja分岐に入らない)、既存の英語
        # Validator(secondary_asr.evaluate_attempt_with_cascade)が従来通り
        # 呼ばれることを確認する(TypeErrorにならないことも含めた後方互換
        # 確認)。
        def fake_en_evaluate(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                              cascade_enabled=None, force_secondary=False,
                              enable_non_latin_cascade=False,
                              enable_connected_speech_equivalence_layer=False, detail_out=None):
            return True, False, _fake_cls("EXACT_MATCH")

        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=self._fake_generate_narration_snippet), \
             mock.patch.object(repro01.routing, "transcribe", return_value=("test phrase", None)), \
             mock.patch.object(repro01.ja_secondary, "evaluate_attempt_ja_with_cascade") as mock_ja_cascade, \
             mock.patch.object(repro01.secondary_asr, "evaluate_attempt_with_cascade",
                                side_effect=fake_en_evaluate) as mock_en_cascade:
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("test phrase", "en", self.out_path, "test phrase",
                           max_attempts=3, expected_readings={"meta": "メタ"})
        self.assertEqual(result["status"], "OK")
        mock_ja_cascade.assert_not_called()
        mock_en_cascade.assert_called_once()

    def test_default_none_unchanged_for_ja_branch(self):
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=self._fake_generate_narration_snippet), \
             mock.patch.object(repro01.routing, "transcribe", return_value=("テスト文", None)), \
             mock.patch.object(repro01.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(True, False, _fake_cls("EXACT_MATCH"))) as mock_cascade:
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("テスト文", "ja", self.out_path, "テス", max_attempts=3)
        self.assertEqual(result["status"], "OK")
        self.assertIsNone(mock_cascade.call_args.kwargs.get("expected_readings"))


if __name__ == "__main__":
    unittest.main()
