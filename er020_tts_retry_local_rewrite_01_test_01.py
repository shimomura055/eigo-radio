#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er020_tts_retry_local_rewrite_01_test_01.py

管理ID: TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01

Offline test(API呼び出し0件、¥0)。LLM(Luna)/sleep/TTSはすべてモックへ
差し替える(実際の10分待機・実際のAPIコストは発生しない)。tempdirへ
すべてのファイル出力を隔離する(本番er011_output/er020_output配下を
汚染しない)。

pin対象:
  1. role→適用判定の単一集約(resolve_narrative_role/
     connected_speech_enabled_for)が5 role全てでTrue・Heading/Key
     Phrase/未知segmentでFalseを返す。
  2. cool-downがattempt1/2では発火せず、max_attempts>=3の最終attempt
     でのみ、かつcooldown_gate_enabled=Trueの場合のみ発火する。
  3. Local Rewrite回復パイプライン(候補生成->7 Gate QA->選定->再TTS)の
     全4分岐(RESOLVED/NO_CANDIDATE_PASSED_QA/RETTS_FAILED/NO_NG_SPAN)。
  4. compute_unchanged_ratio/validate_candidate_is_full_segment/
     check_locality/select_final_candidateの機械判定。
  5. 呼び出し元ヘルパー(_local_rewrite_recovery_for_charon_english/
     _local_rewrite_recovery_for_news_narration)が、標準layout外の
     out_pathに対して安全にNoneを返す(API呼び出し無し)。
"""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

import er020_tts_retry_local_rewrite_01 as m


class RoleTaxonomyTest(unittest.TestCase):
    def test_five_applicable_roles_true(self):
        applicable = ["full_story_part1", "full_story_part2", "full_story_part3",
                      "point_one", "point_two",
                      "comment_1", "comment_2", "comment_3", "comment_4",
                      "preview", "topic_intro", "in_one_line"]
        for seg in applicable:
            with self.subTest(seg=seg):
                self.assertTrue(m.connected_speech_enabled_for(seg), seg)

    def test_two_non_applicable_roles_false(self):
        for seg in ("point_one_heading", "point_two_heading", "kp1_en", "kp3_ja"):
            with self.subTest(seg=seg):
                self.assertFalse(m.connected_speech_enabled_for(seg), seg)

    def test_unknown_and_none_are_false(self):
        self.assertFalse(m.connected_speech_enabled_for("welcome"))
        self.assertFalse(m.connected_speech_enabled_for(None))

    def test_role_labels_resolve_for_all_five(self):
        for seg in ("full_story_part1", "comment_2", "preview", "topic_intro", "in_one_line"):
            label = m.role_label_for(seg)
            self.assertNotIn("segment '", label)


class CooldownTest(unittest.TestCase):
    def test_no_cooldown_when_gate_disabled(self):
        sleep_fn = mock.Mock()
        result = m.maybe_cooldown_before_attempt(3, 3, cooldown_gate_enabled=False, sleep_fn=sleep_fn)
        self.assertIsNone(result)
        sleep_fn.assert_not_called()

    def test_no_cooldown_on_attempt_1_or_2(self):
        sleep_fn = mock.Mock()
        self.assertIsNone(m.maybe_cooldown_before_attempt(1, 3, True, sleep_fn=sleep_fn))
        self.assertIsNone(m.maybe_cooldown_before_attempt(2, 3, True, sleep_fn=sleep_fn))
        sleep_fn.assert_not_called()

    def test_cooldown_fires_on_final_attempt_of_3(self):
        sleep_fn = mock.Mock()
        record = m.maybe_cooldown_before_attempt(3, 3, True, sleep_fn=sleep_fn)
        sleep_fn.assert_called_once_with(m.COOLDOWN_SECONDS)
        self.assertEqual(record["cooldown_requested_seconds"], m.COOLDOWN_SECONDS)
        self.assertEqual(record["attempt_before_cooldown"], 2)
        self.assertEqual(record["attempt_after_cooldown"], 3)

    def test_no_cooldown_when_max_attempts_below_3(self):
        sleep_fn = mock.Mock()
        self.assertIsNone(m.maybe_cooldown_before_attempt(2, 2, True, sleep_fn=sleep_fn))
        sleep_fn.assert_not_called()


class SpanAndLocalityTest(unittest.TestCase):
    def test_identify_ng_span_found(self):
        canon = "let's bring the main point together before we close."
        asr = "let's bring the main points together before we close."
        span = m.identify_ng_span(canon, asr)
        self.assertTrue(span["found"])
        self.assertEqual(span["canonical_changed_words"], ["point"])
        self.assertEqual(span["asr_changed_words"], ["points"])

    def test_identify_ng_span_not_found_when_identical(self):
        text = "this segment matches exactly."
        span = m.identify_ng_span(text, text)
        self.assertFalse(span["found"])

    def test_compute_unchanged_ratio_high_for_single_word_swap(self):
        orig = "let's bring the main point together before we close."
        new = "let's bring the main idea together before we close."
        ratio = m.compute_unchanged_ratio(orig, new)
        self.assertGreaterEqual(ratio, 0.7)

    def test_compute_unchanged_ratio_low_for_full_rewrite(self):
        orig = "let's bring the main point together before we close."
        new = "here is a completely different sentence about something else entirely now."
        ratio = m.compute_unchanged_ratio(orig, new)
        self.assertLess(ratio, 0.7)

    def test_validate_candidate_is_full_segment(self):
        orig = "Let's bring the main point together before we close."
        good = "Let's bring the main idea together before we close."
        bad = "the main idea"
        self.assertTrue(m.validate_candidate_is_full_segment(orig, good))
        self.assertFalse(m.validate_candidate_is_full_segment(orig, bad))

    def test_check_locality_flags_out_of_window_edit(self):
        orig = "let's bring the main point together before we close for today."
        span_range = m.find_problem_span_token_range(orig, "main point")
        self.assertTrue(span_range["found"])
        localized = "let's bring the main idea together before we close for today."
        out_of_window = "let's start bring the main point together before we finish for today."
        loc_ok = m.check_locality(orig, localized, span_range)
        loc_bad = m.check_locality(orig, out_of_window, span_range)
        self.assertTrue(loc_ok["criterion6_localized_to_problem_span"])
        self.assertFalse(loc_bad["criterion6_localized_to_problem_span"])


def _gate(passed: bool, reason: str = "ok"):
    return {"pass": passed, "reason": reason}


def _candidate(cid: str, rewritten: str, before="main point", after="main idea"):
    return {"id": cid, "rewrite_type": "single_word_swap", "rewritten_segment": rewritten,
            "changed_span_before": before, "changed_span_after": after, "rationale": "test"}


class SelectFinalCandidateTest(unittest.TestCase):
    def test_no_candidate_passes(self):
        orig = "let's bring the main point together."
        candidates = [_candidate("c1", "let's bring the main idea together.")]
        qa_evals = [{"candidate_id": "c1", "meaning_preserved": _gate(True), "role_preserved": _gate(True),
                     "fact_non_contradiction": _gate(True), "context_connection": _gate(True),
                     "natural_english": _gate(False, "not natural")}]
        span_range = m.find_problem_span_token_range(orig, "main point")
        records = m.build_full_candidate_records(orig, candidates, qa_evals, span_range)
        selection = m.select_final_candidate(records)
        self.assertIsNone(selection["selected"])
        self.assertEqual(selection["status"], "NO_CANDIDATE_PASSED_ALL_SEVEN_GATES")

    def test_one_candidate_passes_all_gates(self):
        orig = "let's bring the main point together."
        candidates = [_candidate("c1", "let's bring the main idea together.")]
        qa_evals = [{"candidate_id": "c1", "meaning_preserved": _gate(True), "role_preserved": _gate(True),
                     "fact_non_contradiction": _gate(True), "context_connection": _gate(True),
                     "natural_english": _gate(True, "natural")}]
        span_range = m.find_problem_span_token_range(orig, "main point")
        records = m.build_full_candidate_records(orig, candidates, qa_evals, span_range)
        selection = m.select_final_candidate(records)
        self.assertIsNotNone(selection["selected"])
        self.assertEqual(selection["selected"]["id"], "c1")
        self.assertEqual(selection["status"], "SELECTED")


class RunLocalRewriteRecoveryTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.out_dir = self._tmpdir.name

    def tearDown(self):
        self._tmpdir.cleanup()

    def _fake_client(self, candidate_gen_result, qa_result):
        client = mock.Mock()

        def _create(*args, **kwargs):
            schema_name = kwargs.get("text", {}).get("format", {}).get("name", "")
            resp = mock.Mock()
            if "candidates" in schema_name:
                import json as _json
                resp.output_text = _json.dumps(candidate_gen_result)
            else:
                import json as _json
                resp.output_text = _json.dumps(qa_result)
            resp.model = "gpt-5.6-luna"
            resp.id = "resp_test"
            return resp

        client.responses.create.side_effect = _create
        return client

    def test_no_ng_span_short_circuits(self):
        text = "identical text segment."
        client = mock.Mock()
        recovery = m.run_local_rewrite_recovery(
            segment_id="comment_4", canonical_text=text, last_asr_text=text,
            retts_fn=mock.Mock(), out_dir=self.out_dir, client=client)
        self.assertEqual(recovery["status"], "HUMAN_REVIEW_LOCKED_NO_NG_SPAN")
        client.responses.create.assert_not_called()

    def test_resolved_by_local_rewrite(self):
        canonical = "let's bring the main point together before we close."
        asr = "let's bring the main points together before we close."
        candidate_gen_result = {"candidates": [
            _candidate("c1", "let's bring the main idea together before we close."),
        ]}
        qa_result = {"evaluations": [
            {"candidate_id": "c1", "meaning_preserved": _gate(True), "role_preserved": _gate(True),
             "fact_non_contradiction": _gate(True), "context_connection": _gate(True),
             "natural_english": _gate(True)},
        ]}
        client = self._fake_client(candidate_gen_result, qa_result)
        retts_fn = mock.Mock(return_value={"status": "OK", "asr_text": "let's bring the main idea together."})
        recovery = m.run_local_rewrite_recovery(
            segment_id="comment_4", canonical_text=canonical, last_asr_text=asr,
            retts_fn=retts_fn, out_dir=self.out_dir, client=client)
        self.assertEqual(recovery["status"], "RESOLVED_BY_LOCAL_REWRITE")
        retts_fn.assert_called_once_with("let's bring the main idea together before we close.")
        self.assertTrue(os.path.exists(f"{self.out_dir}/local_rewrite_recovery_comment_4.json"))

    def test_no_candidate_passes_qa_locks_for_human_review(self):
        canonical = "let's bring the main point together before we close."
        asr = "let's bring the main points together before we close."
        candidate_gen_result = {"candidates": [
            _candidate("c1", "let's bring the main idea together before we close."),
        ]}
        qa_result = {"evaluations": [
            {"candidate_id": "c1", "meaning_preserved": _gate(True), "role_preserved": _gate(True),
             "fact_non_contradiction": _gate(True), "context_connection": _gate(True),
             "natural_english": _gate(False, "sounds stilted")},
        ]}
        client = self._fake_client(candidate_gen_result, qa_result)
        retts_fn = mock.Mock()
        recovery = m.run_local_rewrite_recovery(
            segment_id="comment_4", canonical_text=canonical, last_asr_text=asr,
            retts_fn=retts_fn, out_dir=self.out_dir, client=client)
        self.assertEqual(recovery["status"], "HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA")
        retts_fn.assert_not_called()

    def test_retts_failure_locks_for_human_review(self):
        canonical = "let's bring the main point together before we close."
        asr = "let's bring the main points together before we close."
        candidate_gen_result = {"candidates": [
            _candidate("c1", "let's bring the main idea together before we close."),
        ]}
        qa_result = {"evaluations": [
            {"candidate_id": "c1", "meaning_preserved": _gate(True), "role_preserved": _gate(True),
             "fact_non_contradiction": _gate(True), "context_connection": _gate(True),
             "natural_english": _gate(True)},
        ]}
        client = self._fake_client(candidate_gen_result, qa_result)
        retts_fn = mock.Mock(return_value={"status": "ASR_VALIDATION_UNCERTAIN", "asr_text": "still wrong"})
        recovery = m.run_local_rewrite_recovery(
            segment_id="comment_4", canonical_text=canonical, last_asr_text=asr,
            retts_fn=retts_fn, out_dir=self.out_dir, client=client)
        self.assertEqual(recovery["status"], "HUMAN_REVIEW_LOCKED_RETTS_FAILED")


class CallSiteHelperSafetyTest(unittest.TestCase):
    """呼び出し元ヘルパーが、標準layout外のout_pathに対してAPI呼び出し
    無しで安全にNoneを返すことを確認する(review_lockの既存レイアウト
    チェックをそのまま尊重する設計の検証)。"""

    def test_charon_english_helper_returns_none_for_nonstandard_path(self):
        import er003_v1_sing01_voice01_generate as voice01
        result = voice01._local_rewrite_recovery_for_charon_english(
            "some text", "/tmp/not_a_standard_layout.wav", "some asr text",
            None, False, True)
        self.assertIsNone(result)

    def test_news_narration_helper_returns_none_for_nonstandard_path(self):
        import er003_v1_sing01_news_tail_fix as news_tail_fix
        result = news_tail_fix._local_rewrite_recovery_for_news_narration(
            "some text", "/tmp/not_a_standard_layout.wav", "some asr text", 15, False, True, False)
        self.assertIsNone(result)

    def test_a2_english_segment_fallback_helper_returns_none_for_nonstandard_path(self):
        """TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01(修正1回目):
        A2経路(er003_v1_crosslevel_audio_02_common.
        generate_english_segment_with_fallback)専用のLocal Rewrite回復
        ヘルパーも、B1側の2ヘルパーと同じ安全設計(標準layout外はAPI呼び出し
        無しでNone)であることを確認する。"""
        import er003_v1_crosslevel_audio_02_common as crosslevel_common
        result = crosslevel_common._local_rewrite_recovery_for_english_segment_with_fallback(
            "some text", "/tmp/not_a_standard_layout.wav", "some asr text", 60, True, False, False,
            [{"attempt": 1}, {"attempt": 2}], [{"attempt": 1}], [])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
