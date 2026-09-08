# ============================================================
# er011_open128_method_d_local_asr_confirm_production_wiring_01_test_01.py
# OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01
# ============================================================
# 監視対象: er011_open121_repetition_qa_production_01.py(方式D 2段判定
# `confirm_by_local_asr_overlap()`・`analyze_profile_d_long_lag()`・
# `run_spectral_checks()`・`evaluate_repetition_qa()`のASR共有リファクタ)。
#
# 実行方法: .venv/Scripts/python.exe er011_open128_method_d_local_asr_
#   confirm_production_wiring_01_test_01.py
from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import er008_disfluency_qa_18 as dq18
import er011_open121_repetition_qa_production_01 as repetition_qa

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
FLAG23_TABLE = os.path.join(REPO_ROOT, "er011_output", "method_d_flag23_review_01", "classification_table.json")


def _load_flag23():
    with open(FLAG23_TABLE, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Part 1: confirm_by_local_asr_overlap()単体(合成data、difflib比率+
# 最長連続一致語数のロジック確認)
# ============================================================
class ConfirmByLocalAsrOverlapUnitTests(unittest.TestCase):
    def _words(self, tokens_with_times):
        return [{"text": t, "start": s, "end": e} for t, s, e in tokens_with_times]

    def test_true_duplicate_high_overlap_confirmed(self):
        # 2箇所とも"the cat sat down quietly"(完全一致、lcs_words=5)。
        words = self._words([
            ("the", 0.0, 0.2), ("cat", 0.2, 0.4), ("sat", 0.4, 0.6),
            ("down", 0.6, 0.8), ("quietly", 0.8, 1.0),
            ("the", 10.0, 10.2), ("cat", 10.2, 10.4), ("sat", 10.4, 10.6),
            ("down", 10.6, 10.8), ("quietly", 10.8, 11.0),
        ])
        r = repetition_qa.confirm_by_local_asr_overlap(words, time_a=0.5, time_b=10.5)
        self.assertTrue(r["confirmed"], r)
        self.assertGreaterEqual(r["lcs_words"], 3)

    def test_unrelated_content_low_overlap_not_confirmed(self):
        words = self._words([
            ("the", 0.0, 0.2), ("weather", 0.2, 0.4), ("was", 0.4, 0.6),
            ("nice", 0.6, 0.8), ("today", 0.8, 1.0),
            ("she", 10.0, 10.2), ("bought", 10.2, 10.4), ("apples", 10.4, 10.6),
            ("at", 10.6, 10.8), ("market", 10.8, 11.0),
        ])
        r = repetition_qa.confirm_by_local_asr_overlap(words, time_a=0.5, time_b=10.5)
        self.assertFalse(r["confirmed"], r)
        self.assertLess(r["lcs_words"], 3)

    def test_empty_window_not_confirmed(self):
        words = self._words([("hello", 0.0, 0.2)])
        r = repetition_qa.confirm_by_local_asr_overlap(words, time_a=50.0, time_b=90.0)
        self.assertFalse(r["confirmed"], r)


# ============================================================
# Part 2: analyze_profile_d_long_lag()の2段判定(words引数)・後方互換
# ============================================================
class AnalyzeProfileDTwoStageTests(unittest.TestCase):
    def _bundle_no_sim(self):
        return {"sim": None, "hop_ms": 10.0}

    def test_c_acoustic_not_flagged_does_not_call_asr_confirmation(self):
        # acoustic_flagged=Falseの場合、局所ASR確認関数自体を呼ばない
        # (追加計算コストゼロを保証)。
        calls = {"n": 0}
        orig = repetition_qa.confirm_by_local_asr_overlap

        def tracking(*a, **k):
            calls["n"] += 1
            return orig(*a, **k)

        with mock.patch.object(repetition_qa, "confirm_by_local_asr_overlap", side_effect=tracking):
            r = repetition_qa.analyze_profile_d_long_lag(self._bundle_no_sim(), words=[{"text": "x", "start": 0, "end": 1}])
        self.assertFalse(r["acoustic_flagged"])
        self.assertFalse(r["flagged"])
        self.assertIsNone(r["local_asr_confirmation"])
        self.assertEqual(calls["n"], 0)

    def test_words_none_keeps_legacy_acoustic_only_behavior(self):
        # 後方互換: words=None(既定)の場合は従来通りacoustic判定のみ。
        r = repetition_qa.analyze_profile_d_long_lag(self._bundle_no_sim())
        self.assertFalse(r["flagged"])
        self.assertIn("acoustic_flagged", r)
        self.assertIsNone(r["local_asr_confirmation"])


# ============================================================
# Part 3: Production entry経由runtime確認(実wav、確定TP8件+確定FP15件、
# method_d_flag23_review_01/classification_table.json)。
# ============================================================
@unittest.skipUnless(os.path.exists(FLAG23_TABLE), "method_d_flag23_review_01 classification_table.json not present")
class Flag23ProductionEntryClassificationTests(unittest.TestCase):
    """全23件を対象にした統合テストは実行時間が長い(faster-whisper x 23)
    ため、代表2件(TP1件・FP1件)のみをCIとして残し、全件検証は
    er011_output/open128_method_d_local_asr_wiring_01/run_runtime_evidence.py
    (Runtime evidence)で実施する。"""

    def test_known_tp_point_two_bug_confirmed_flagged(self):
        rows = _load_flag23()
        row = rows[2]  # open112_trial13::...::a2::point_two(真の重複)
        self.assertEqual(row["classification"], "真の重複(証拠あり)")
        r = repetition_qa.evaluate_repetition_qa(row["path"], row["canonical_text"], language="en")
        self.assertTrue(r["method_d_spectral_long_lag"]["acoustic_flagged"], r)
        self.assertIsNotNone(r["method_d_spectral_long_lag"]["local_asr_confirmation"])
        self.assertTrue(r["method_d_spectral_long_lag"]["local_asr_confirmation"]["confirmed"], r)
        self.assertTrue(r["method_d_spectral_long_lag"]["flagged"], r)

    def test_known_fp_pool_benches_topic_intro_not_confirmed(self):
        rows = _load_flag23()
        row = next(r for r in rows if r["item_id"].endswith("pool_benches::b1b::topic_intro"))
        self.assertEqual(row["classification"], "誤flagの可能性高")
        r = repetition_qa.evaluate_repetition_qa(row["path"], row["canonical_text"], language="en")
        self.assertTrue(r["method_d_spectral_long_lag"]["acoustic_flagged"], r)
        self.assertIsNotNone(r["method_d_spectral_long_lag"]["local_asr_confirmation"])
        self.assertFalse(r["method_d_spectral_long_lag"]["local_asr_confirmation"]["confirmed"], r)
        self.assertFalse(r["method_d_spectral_long_lag"]["flagged"], r)


# ============================================================
# Part 4: ASR共有(同一音声への二重ASR回避)・ASR失敗時の挙動が方式Aと
# 同一であることのmock検証(実API/実ASR呼び出しなし)。
# ============================================================
class AsrSharingAndFailureParityTests(unittest.TestCase):
    def setUp(self):
        self.orig_transcribe = dq18.transcribe_verbatim
        self.orig_compute_bundle = repetition_qa.compute_shared_self_similarity

    def tearDown(self):
        dq18.transcribe_verbatim = self.orig_transcribe
        repetition_qa.compute_shared_self_similarity = self.orig_compute_bundle

    def _fake_bundle_with_flagged_d(self):
        # min_lag_s=1.0秒(hop_ms=10 -> 100フレーム)、run長閾値0.12秒
        # (12フレーム)を満たすよう、lag=100フレームの対角帯を40フレーム分
        # 連続して高類似度(0.99)にする(acoustic_flagged=True想定)。
        import numpy as np
        n = 140
        sim = np.zeros((n, n))
        np.fill_diagonal(sim, 1.0)
        for i in range(n - 100):
            sim[i, i + 100] = 0.99
            sim[i + 100, i] = 0.99
        return {"path": "fake.wav", "sample_rate": 16000, "duration_seconds": 1.4,
                "hop_ms": 10.0, "frame_ms": 25.0, "sim": sim, "n_frames": n}

    def test_transcribe_called_exactly_once_when_method_d_acoustic_flags(self):
        calls = {"n": 0}
        words = [{"text": "hello", "start": 0.0, "end": 0.2},
                  {"text": "world", "start": 0.2, "end": 0.4}]

        def fake_transcribe(*a, **k):
            calls["n"] += 1
            return words

        dq18.transcribe_verbatim = fake_transcribe
        repetition_qa.compute_shared_self_similarity = lambda path: self._fake_bundle_with_flagged_d()

        r = repetition_qa.evaluate_repetition_qa("fake.wav", "hello world", language="en")
        self.assertEqual(calls["n"], 1, "方式A・方式D(局所ASR確認)で同一ASR結果を共有し、"
                                          "transcribe_verbatimは1回のみ呼ばれること")
        self.assertIsNotNone(r["method_d_spectral_long_lag"]["local_asr_confirmation"])

    def test_asr_failure_propagates_same_as_method_a_no_new_fallback(self):
        # 現行仕様: transcribe_verbatim失敗時は例外がそのまま伝播する
        # (方式Aのrun_ngram_check()と同一挙動、新規fail-open/fail-closed
        # 設計を追加していないことの確認)。
        def failing_transcribe(*a, **k):
            raise RuntimeError("ASR backend unavailable")

        dq18.transcribe_verbatim = failing_transcribe
        with self.assertRaises(RuntimeError):
            repetition_qa.evaluate_repetition_qa("fake.wav", "hello world", language="en")
        # 比較対象: 方式A単体(run_ngram_check)も同じ例外伝播。
        with self.assertRaises(RuntimeError):
            repetition_qa.run_ngram_check("fake.wav", "hello world", language="en")


if __name__ == "__main__":
    unittest.main()
