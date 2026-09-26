#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er020_tts_local_rewrite_natural_english_qa_trial_02_test_01.py

管理ID: TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02

Offline test(API呼び出し0件、¥0)。Luna(候補生成/QA)・TTS/ASR呼び出しは
すべてモックへ差し替える(実際のAPIコストは発生しない)。

pin対象:
  1. 7 Gateが固定された順序(1-5がLLM判定、6-7がharness機械判定)で
     すべて揃うこと。
  2. Natural English Gate(5)がFAILの候補はall_seven_gates_pass=False
     になり、select_final_candidate()が選ばない(=TTSへ渡らない)こと。
  3. 局所性(criterion 6): 問題span遠方を書き換えた候補はFAILになること。
  4. 非全文Rewrite(criterion 7): unchanged_ratio閾値未満はFAILになる
     こと。
  5. 全候補が7 Gate中どれかでFAILの場合、
     status=NO_CANDIDATE_PASSED_ALL_SEVEN_GATESとなりTTSがスキップ
     される(run_selected_ttsが一切呼ばれない)こと。
  6. TTS attempt上限が2であること(cool-downなしでattempt1->NGなら
     attempt2、PASSなら即終了)。
  7. Production module無変更(git diffが空であることの確認)。
"""

from __future__ import annotations

import os
import subprocess
import unittest
from unittest import mock

import er020_tts_local_rewrite_natural_english_qa_trial_02 as m

TEST_OUT_DIR = "er020_output/tts_local_rewrite_natural_english_qa_trial_02/_test_scratch"

TARGET = {
    "segment_id": "comment_4",
    "segment_role": "Comment(Story Recovery + Bridge to In One Line)",
    "canonical_text": (
        "The service looked like AI, but the work behind it was not always "
        "done by AI alone. Now, let’s bring the main point together."
    ),
    "context_before_segment_id": "full_story_part3",
    "context_before_text": "Some context before.",
    "context_after_segment_id": "in_one_line",
    "context_after_text": "AI may make the call, but people also need to know who is really behind the voice.",
    "problem_span_text": "bring the main point together",
    "source": "test-fixture",
}


def _gate(passed: bool, reason: str = "reason"):
    return {"pass": passed, "reason": reason}


def _all_pass_qa(candidate_id: str):
    return {
        "candidate_id": candidate_id,
        "meaning_preserved": _gate(True),
        "role_preserved": _gate(True),
        "fact_non_contradiction": _gate(True),
        "context_connection": _gate(True),
        "natural_english": _gate(True, "sounds natural"),
    }


class ProblemSpanLocationTest(unittest.TestCase):
    def test_finds_problem_span_token_range(self):
        rng = m.find_problem_span_token_range(TARGET["canonical_text"], TARGET["problem_span_text"])
        self.assertTrue(rng["found"])
        # "bring the main point together" = 5 tokens
        self.assertEqual(rng["end"] - rng["start"], 5)


class LocalityCheckTest(unittest.TestCase):
    def setUp(self):
        self.rng = m.find_problem_span_token_range(TARGET["canonical_text"], TARGET["problem_span_text"])

    def test_localized_minimal_swap_passes_criterion6(self):
        rewritten = TARGET["canonical_text"].replace("main point", "main idea")
        result = m.check_locality(TARGET["canonical_text"], rewritten, self.rng)
        self.assertTrue(result["criterion6_localized_to_problem_span"])
        self.assertTrue(result["criterion7_not_full_rewrite"])

    def test_change_far_from_problem_span_fails_criterion6(self):
        # 冒頭("The service")を変更(問題spanから遠い箇所への変更)
        rewritten = TARGET["canonical_text"].replace(
            "The service looked like AI", "This particular offering seemed like AI")
        result = m.check_locality(TARGET["canonical_text"], rewritten, self.rng)
        self.assertFalse(result["criterion6_localized_to_problem_span"])

    def test_full_rewrite_fails_criterion7(self):
        rewritten = "People thought a machine did everything, yet a person helped in secret."
        result = m.check_locality(TARGET["canonical_text"], rewritten, self.rng)
        self.assertFalse(result["criterion7_not_full_rewrite"])
        self.assertLess(result["unchanged_ratio"], m.prior_trial.LOCAL_REWRITE_MIN_UNCHANGED_RATIO)


class FullSegmentFormatSafetyNetTest(unittest.TestCase):
    """回帰テスト(実行時に実際に発生したバグ): 初回実行でLuna候補生成が
    'rewritten_segment'に全文ではなく置換phraseのみを返した
    (プロンプトの指示不足)。プロンプト修正後も、将来のモデル出力ゆれに
    備えた安全網がmalformedな候補をall_seven_gates_pass=Falseへ落とし、
    TTSへ渡さないことをpinする。"""

    def setUp(self):
        self.rng = m.find_problem_span_token_range(TARGET["canonical_text"], TARGET["problem_span_text"])

    def test_full_segment_passes_format_check(self):
        rewritten = TARGET["canonical_text"].replace("main point", "main idea")
        self.assertTrue(m.validate_candidate_is_full_segment(TARGET["canonical_text"], rewritten))

    def test_phrase_only_fails_format_check(self):
        self.assertFalse(m.validate_candidate_is_full_segment(TARGET["canonical_text"], "sum up the main takeaway"))

    def test_malformed_candidate_is_excluded_even_if_qa_all_pass(self):
        malformed_candidate = {
            "id": "candidate_bad", "rewrite_type": "short_phrase_rewrite",
            "rewritten_segment": "sum up the main takeaway",  # phraseのみ(バグ再現)
            "changed_span_before": "bring the main point together",
            "changed_span_after": "sum up the main takeaway", "rationale": "r",
        }
        qa_evals = [_all_pass_qa("candidate_bad")]
        records = m.build_full_candidate_records(TARGET, [malformed_candidate], qa_evals, self.rng)
        self.assertFalse(records[0]["is_full_segment_format_valid"])
        self.assertFalse(records[0]["all_seven_gates_pass"])


class TtsStabilityHeuristicTest(unittest.TestCase):
    def test_flags_plural_s_risk_for_regular_noun(self):
        h = m.tts_stability_heuristic("idea")
        self.assertIn("idea", h["plural_s_risk_words"])
        self.assertIn("idea", h["would_be_classified_benign_plural_pair_if_asr_added_s"])
        self.assertTrue(h["would_be_classified_benign_plural_pair_if_asr_added_s"]["idea"])

    def test_flags_word_final_plosive_consonant(self):
        h = m.tts_stability_heuristic("point")
        self.assertIn("point", h["word_final_plosive_consonant_words"])


class SevenGateIntegrationTest(unittest.TestCase):
    """Natural English Gate(5)がFAILの候補は、他が全PASSでも
    all_seven_gates_pass=Falseになり、選定candidateから除外されることを
    pinする(=TTSへ絶対に渡らない)。"""

    def setUp(self):
        self.rng = m.find_problem_span_token_range(TARGET["canonical_text"], TARGET["problem_span_text"])
        self.good_candidate = {
            "id": "candidate_1", "rewrite_type": "single_word_swap",
            "rewritten_segment": TARGET["canonical_text"].replace("main point", "main idea"),
            "changed_span_before": "point", "changed_span_after": "idea", "rationale": "r",
        }
        self.bad_natural_candidate = {
            "id": "candidate_2", "rewrite_type": "short_phrase_rewrite",
            "rewritten_segment": TARGET["canonical_text"].replace(
                "bring the main point together", "conjoin the principal notion"),
            "changed_span_before": "bring the main point together",
            "changed_span_after": "conjoin the principal notion", "rationale": "r",
        }

    def test_natural_english_fail_blocks_candidate(self):
        qa_evals = [
            _all_pass_qa("candidate_1"),
            {**_all_pass_qa("candidate_2"), "natural_english": _gate(False, "stilted, not idiomatic")},
        ]
        records = m.build_full_candidate_records(
            TARGET, [self.good_candidate, self.bad_natural_candidate], qa_evals, self.rng)
        by_id = {r["id"]: r for r in records}
        self.assertTrue(by_id["candidate_1"]["all_seven_gates_pass"])
        self.assertFalse(by_id["candidate_2"]["all_seven_gates_pass"])
        self.assertFalse(by_id["candidate_2"]["seven_gates"]["5_natural_english_gate"])

        selection = m.select_final_candidate(records)
        self.assertEqual(selection["selected"]["id"], "candidate_1")
        self.assertNotIn("candidate_2", selection.get("all_passing_candidate_ids", []))

    def test_no_candidate_passes_skips_tts(self):
        qa_evals = [
            {**_all_pass_qa("candidate_1"), "natural_english": _gate(False, "not natural")},
            {**_all_pass_qa("candidate_2"), "meaning_preserved": _gate(False, "meaning drifted")},
        ]
        records = m.build_full_candidate_records(
            TARGET, [self.good_candidate, self.bad_natural_candidate], qa_evals, self.rng)
        selection = m.select_final_candidate(records)
        self.assertIsNone(selection["selected"])
        self.assertEqual(selection["status"], "NO_CANDIDATE_PASSED_ALL_SEVEN_GATES")

        with mock.patch.object(m, "run_single_tts_attempt") as mocked_tts:
            if selection["selected"] is not None:
                m.run_selected_tts(selection["selected"], TEST_OUT_DIR)
            mocked_tts.assert_not_called()


class SelectedTtsAttemptCapTest(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_OUT_DIR, exist_ok=True)
        self._orig_out_dir = m.OUT_DIR
        self._orig_log_path = m.ATTEMPT_LOG_PATH
        m.OUT_DIR = TEST_OUT_DIR
        m.ATTEMPT_LOG_PATH = f"{TEST_OUT_DIR}/attempt_log.jsonl"

    def tearDown(self):
        m.OUT_DIR = self._orig_out_dir
        m.ATTEMPT_LOG_PATH = self._orig_log_path

    def _rec(self, attempt, passed, asr_text="x"):
        return {
            "segment": "comment_4", "canonical_text": "x", "attempt": attempt,
            "timestamp": f"2026-09-26T09:0{attempt}:00+09:00", "model": "gemini-2.5-pro-preview-tts",
            "voice": "Charon", "route": "english_style_prefix", "tts_execution_mode": "STANDARD",
            "tts_input_sha256": "deadbeef", "asr_text": asr_text,
            "classification": "EXACT_MATCH" if passed else "ASR_VALIDATION_UNCERTAIN",
            "classification_reason": "r", "cascade_audio_classification": "x",
            "pass": passed, "human_intervention": False, "raw_status": "OK",
            "raw_reason": None, "attempt_wav_path": f"/tmp/a{attempt}.wav", "disfluency_checked": True,
        }

    def test_stops_at_attempt1_if_pass(self):
        selected = {"id": "candidate_1", "rewritten_segment": "text"}
        with mock.patch.object(m, "run_single_tts_attempt", side_effect=[self._rec(1, True)]):
            result = m.run_selected_tts(selected, TEST_OUT_DIR)
        self.assertEqual(result["status"], "PASS_AT_ATTEMPT_1")
        self.assertEqual(len(result["attempts"]), 1)

    def test_two_attempts_max_then_locked(self):
        selected = {"id": "candidate_1", "rewritten_segment": "text"}
        with mock.patch.object(m, "run_single_tts_attempt",
                                side_effect=[self._rec(1, False), self._rec(2, False)]) as mocked:
            result = m.run_selected_tts(selected, TEST_OUT_DIR)
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(result["status"], "NG_AFTER_2_ATTEMPTS(HUMAN_REVIEW_LOCKED)")


class ProductionModuleUnchangedTest(unittest.TestCase):
    def test_production_modules_have_no_uncommitted_diff_caused_by_this_trial(self):
        protected_paths = [
            "er003_v1_sing01_voice01_generate.py",
            "er011_human_review_lock_01.py",
            "er007_ja_secondary_asr_01.py",
            "er019_family_x_pointless_tts_01.py",
            "er020_tts_cooldown_local_rewrite_trial_01.py",
        ]
        result = subprocess.run(
            ["git", "diff", "--stat", "--"] + protected_paths,
            cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.stdout.strip(), "",
                          f"Production/前回Trial module差分が検出されました: {result.stdout}")


if __name__ == "__main__":
    unittest.main()
