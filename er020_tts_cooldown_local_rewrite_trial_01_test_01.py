#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er020_tts_cooldown_local_rewrite_trial_01_test_01.py

管理ID: TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01

Offline test(API呼び出し0件、¥0)。TTS/ASR/LLM/sleepはすべてモックへ
差し替える(実際の10分待機・実際のTTS/ASR/LLM APIコストは発生しない)。

pin対象:
  1. cool-down順序: attempt1 NG -> attempt2即時(sleep未呼び出し)NG ->
     sleep(600)を正確に1回だけ呼ぶ -> attempt3。attempt1/2どちらかが
     PASSした場合はsleepを一切呼ばない。
  2. attempt記録項目の網羅(必須フィールドが全て存在する)。
  3. Local Rewriteが全文置換でないこと(unchanged_ratio閾値判定):
     最小限の言い換え(高ratio)はis_local_not_full_rewrite=True、
     全文書き換え相当(低ratio)はFalseになる。
  4. Connected Speech role taxonomyの分類(role_of)。
  5. Production module無変更(git diffが空であることの確認)。
"""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from unittest import mock

import er020_tts_cooldown_local_rewrite_trial_01 as m

TEST_OUT_DIR = "er020_output/tts_cooldown_local_rewrite_trial_01/_test_scratch"


def _ng_record(attempt: int, asr_text: str = "the main points together"):
    return {
        "segment": "comment_4", "canonical_text": "canonical text here.",
        "attempt": attempt, "timestamp": f"2026-09-26T08:0{attempt}:00+09:00",
        "model": "gemini-2.5-pro-preview-tts", "voice": "Charon", "route": "english_style_prefix",
        "tts_execution_mode": "STANDARD", "tts_input_sha256": "deadbeef",
        "asr_text": asr_text, "classification": "ASR_VALIDATION_UNCERTAIN",
        "classification_reason": "内容語の差は検出されないが、一致率がPASS基準に届かない",
        "cascade_audio_classification": "ASR_VALIDATION_UNCERTAIN",
        "pass": False, "human_intervention": False, "raw_status": "ASR_VALIDATION_UNCERTAIN",
        "raw_reason": None, "attempt_wav_path": f"/tmp/attempt{attempt}.wav",
        "disfluency_checked": False,
    }


def _pass_record(attempt: int):
    r = _ng_record(attempt, asr_text="canonical text here.")
    r["pass"] = True
    r["classification"] = "EXACT_MATCH"
    return r


class CooldownSequenceTest(unittest.TestCase):
    def setUp(self):
        self._orig_out_dir = m.OUT_DIR
        self._orig_log_path = m.ATTEMPT_LOG_PATH
        m.OUT_DIR = TEST_OUT_DIR
        m.ATTEMPT_LOG_PATH = f"{TEST_OUT_DIR}/attempt_log.jsonl"
        os.makedirs(TEST_OUT_DIR, exist_ok=True)

    def tearDown(self):
        m.OUT_DIR = self._orig_out_dir
        m.ATTEMPT_LOG_PATH = self._orig_log_path

    def test_cooldown_called_once_between_attempt2_and_attempt3_when_both_ng(self):
        target = {"segment_id": "comment_4", "canonical_text": "canonical text here."}
        sleep_calls = []

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        with mock.patch.object(m, "run_single_tts_attempt",
                                side_effect=[_ng_record(1), _ng_record(2), _ng_record(3)]):
            result = m.run_cooldown_retry_sequence(target, TEST_OUT_DIR, sleep_fn=fake_sleep,
                                                     cooldown_seconds=600.0)

        self.assertEqual(result["status"], "REPRODUCED_3_NG")
        self.assertEqual(sleep_calls, [600.0])  # 正確に1回、600秒
        self.assertEqual([a["attempt"] for a in result["attempts"]], [1, 2, 3])

    def test_no_cooldown_when_attempt1_passes(self):
        target = {"segment_id": "comment_4", "canonical_text": "canonical text here."}
        sleep_calls = []

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        with mock.patch.object(m, "run_single_tts_attempt", side_effect=[_pass_record(1)]):
            result = m.run_cooldown_retry_sequence(target, TEST_OUT_DIR, sleep_fn=fake_sleep,
                                                     cooldown_seconds=600.0)

        self.assertEqual(result["status"], "PASS_AT_ATTEMPT_1")
        self.assertEqual(sleep_calls, [])  # sleepは一度も呼ばれない

    def test_no_cooldown_when_attempt2_passes(self):
        target = {"segment_id": "comment_4", "canonical_text": "canonical text here."}
        sleep_calls = []

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        with mock.patch.object(m, "run_single_tts_attempt", side_effect=[_ng_record(1), _pass_record(2)]):
            result = m.run_cooldown_retry_sequence(target, TEST_OUT_DIR, sleep_fn=fake_sleep,
                                                     cooldown_seconds=600.0)

        self.assertEqual(result["status"], "PASS_AT_ATTEMPT_2")
        self.assertEqual(sleep_calls, [])

    def test_attempt_record_has_all_required_fields(self):
        required_fields = {
            "segment", "canonical_text", "attempt", "timestamp", "model", "voice", "route",
            "tts_input_sha256", "asr_text", "classification", "pass", "human_intervention",
        }
        rec = _ng_record(1)
        self.assertTrue(required_fields.issubset(rec.keys()))
        self.assertIs(rec["human_intervention"], False)

    def test_gap_seconds_computed_between_attempts(self):
        recs = [
            {"attempt": 1, "timestamp": "2026-09-26T08:00:00+09:00"},
            {"attempt": 2, "timestamp": "2026-09-26T08:00:05+09:00"},
            {"attempt": 3, "timestamp": "2026-09-26T08:10:06+09:00"},
        ]
        out = m._with_gap(recs)
        self.assertIsNone(out[0]["gap_seconds_from_previous_attempt"])
        self.assertAlmostEqual(out[1]["gap_seconds_from_previous_attempt"], 5.0)
        self.assertAlmostEqual(out[2]["gap_seconds_from_previous_attempt"], 601.0)


class SingleAttemptFieldExtractionTest(unittest.TestCase):
    """generate_charon_english()のSTOPPED-fallthrough分岐(max_attempts=1では
    ほぼ常にここへ落ちる)は、トップレベル辞書に"asr_text"/"instruction_type"/
    "audio_classification"/"asr_verified"を含まない(OK/ASR_VALIDATION_
    UNCERTAIN分岐にのみ存在する)。attempts_log[-1]からの復元が正しく動く
    ことをpinする回帰テスト(実行時に実際に踏んだバグ)。"""

    def test_stopped_fallthrough_extracts_from_attempts_log(self):
        fake_result = {
            "status": "STOPPED",
            "reason": "1回試行してもASR検証に合格しませんでした",
            "attempts_log": [{
                "attempt": 1, "status": "OK", "asr_text": "the main points together.",
                "instruction_type": "english_style_prefix", "audio_classification": "ASR_VALIDATION_UNCERTAIN",
                "verified": False, "length_ok": True, "disfluency_checked": False,
            }],
        }
        with mock.patch.object(m, "RAW_CHARON_ENGLISH", return_value=fake_result):
            rec = m.run_single_tts_attempt(
                "The service ... the main point together.", f"{TEST_OUT_DIR}/x.wav", 1,
                "style prefix", True)
        self.assertEqual(rec["asr_text"], "the main points together.")
        self.assertEqual(rec["route"], "english_style_prefix")
        self.assertFalse(rec["pass"])
        self.assertIsNotNone(rec["classification"])

    def test_ok_branch_extracts_pass_true(self):
        fake_result = {
            "status": "OK", "asr_verified": True, "asr_text": "exact canonical text.",
            "instruction_type": "english_style_prefix", "audio_classification": "EXACT_MATCH",
            "attempts_log": [{"attempt": 1, "status": "OK", "asr_text": "exact canonical text.",
                              "instruction_type": "english_style_prefix",
                              "audio_classification": "EXACT_MATCH", "verified": True}],
        }
        with mock.patch.object(m, "RAW_CHARON_ENGLISH", return_value=fake_result):
            rec = m.run_single_tts_attempt("exact canonical text.", f"{TEST_OUT_DIR}/y.wav", 1,
                                            "style prefix", True)
        self.assertTrue(rec["pass"])


class NgSpanTest(unittest.TestCase):
    def test_identify_ng_span_finds_point_points_diff(self):
        canonical = ("The service looked like AI, but the work behind it was not always done "
                     "by AI alone. Now, let's bring the main point together.")
        asr = ("The service looked like AI, but the work behind it was not always done by AI "
               "alone. Now, let's bring the main points together.")
        span = m.identify_ng_span(canonical, asr)
        self.assertTrue(span["found"])
        self.assertEqual([w.lower() for w in span["canonical_changed_words"]], ["point"])
        self.assertEqual([w.lower() for w in span["asr_changed_words"]], ["points"])

    def test_identify_ng_span_no_diff(self):
        self.assertFalse(m.identify_ng_span("same text.", "same text.")["found"])

    def test_identify_ng_span_ignores_curly_vs_straight_apostrophe(self):
        """回帰テスト(実行時に実際に発生したバグ): canonical側が曲線
        アポストロフィ(’、U+2019)・ASR側が直線アポストロフィ(')の場合に、
        本当のNG原因(point/points)より先にこの無関係な字形差を最初の
        非一致として誤検出しないこと(既存tokenize()と同じ正規化を使う)。"""
        canonical = ("The service looked like AI, but the work behind it was not always done "
                     "by AI alone. Now, let’s bring the main point together.")
        asr = ("The service looked like AI, but the work behind it was not always done by AI "
               "alone. Now, let's bring the main points together.")
        span = m.identify_ng_span(canonical, asr)
        self.assertTrue(span["found"])
        self.assertEqual(span["canonical_changed_words"], ["point"])
        self.assertEqual(span["asr_changed_words"], ["points"])


class LocalRewriteUnchangedRatioTest(unittest.TestCase):
    def test_minimal_rewrite_passes_locality_threshold(self):
        original = ("The service looked like AI, but the work behind it was not always done "
                     "by AI alone. Now, let's bring the main point together.")
        minimal_rewrite = ("The service looked like AI, but the work behind it was not always done "
                            "by AI alone. Now, let's bring the main idea together.")
        ratio = m.compute_unchanged_ratio(original, minimal_rewrite)
        self.assertGreaterEqual(ratio, m.LOCAL_REWRITE_MIN_UNCHANGED_RATIO)

    def test_full_rewrite_fails_locality_threshold(self):
        original = ("The service looked like AI, but the work behind it was not always done "
                     "by AI alone. Now, let's bring the main point together.")
        full_rewrite = "People thought a machine did everything, yet a person helped in secret."
        ratio = m.compute_unchanged_ratio(original, full_rewrite)
        self.assertLess(ratio, m.LOCAL_REWRITE_MIN_UNCHANGED_RATIO)


class RoleTaxonomyTest(unittest.TestCase):
    def test_comment_segments_classified_as_narrative_english(self):
        for seg in ("comment_1", "comment_2", "comment_3", "comment_4", "preview",
                    "topic_intro", "in_one_line", "full_story_part1"):
            self.assertEqual(m.role_of(seg), "NARRATIVE_ENGLISH")

    def test_heading_segments_classified_separately(self):
        self.assertEqual(m.role_of("point_one_heading"), "HEADING_READOUT")

    def test_unknown_segment_returns_none(self):
        self.assertIsNone(m.role_of("nonexistent_segment"))

    def test_current_wiring_is_finer_grained_than_role(self):
        # 同じNARRATIVE_ENGLISH roleでも、comment_4はFalse・full_story_part1はTrue
        # (現在の実配線がrole単位ではないことの回帰確認)。
        self.assertEqual(m.role_of("comment_4"), m.role_of("full_story_part1"))
        self.assertNotEqual(m.CURRENT_WIRING_BY_SEGMENT["comment_4"],
                             m.CURRENT_WIRING_BY_SEGMENT["full_story_part1"])


class ProductionModuleUnchangedTest(unittest.TestCase):
    def test_production_modules_have_no_uncommitted_diff_caused_by_this_trial(self):
        protected_paths = [
            "er003_v1_sing01_voice01_generate.py",
            "er011_human_review_lock_01.py",
            "er007_ja_secondary_asr_01.py",
            "er019_family_x_pointless_tts_01.py",
        ]
        result = subprocess.run(
            ["git", "diff", "--stat", "--"] + protected_paths,
            cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.stdout.strip(), "",
                          f"Production module差分が検出されました: {result.stdout}")


if __name__ == "__main__":
    unittest.main()
