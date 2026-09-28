# ============================================================
# er036_family_y_voice_structure_trial_01_test_01.py
# FAMILY-Y-VOICE-STRUCTURE-TRIAL-01: 単体test(API呼び出しなし、\xa50、mock)
# ============================================================
from __future__ import annotations

import inspect
import unittest

import er019_family_x_ja_writer_o_r1_r2_01 as fx_r1r2
import er019_family_x_storyline_b3_fact_selection_01 as storyline_b3
import er036_family_y_voice_structure_trial_01 as trial


RAW_LEDGER_SAMPLE = """テーマ: sample

=== VOICE_1_EVIDENCE(Applicant) ===

[VOICE_1_EVIDENCE] 1-01(R1_fact_alpha): 米国の求職者の49%が、採用選考で
使われるAIツールは偏っていると考えている。
  source: Sample Source
  (https://example.com/alpha)
  verification: CONFIRMED

[VOICE_1_EVIDENCE] 1-02(R1_fact_beta): 別の応募者は、AIが信頼性のスコアを
つけたと述べた。
  source: Sample Source 2
  verification: PARTIALLY_CONFIRMED

=== VOICE_2_EVIDENCE(Recruiter) ===

[VOICE_2_EVIDENCE] 2-01(R2_fact_gamma): 採用担当者はAIツールで応募書類を
分類している。
  source: Sample Source 3
  verification: CONFIRMED

=== VOICE_3_EVIDENCE(Business Owner) ===

[VOICE_3_EVIDENCE] 3-01(R2_fact_delta): 経営者はAI導入後にコストが下がった
という報告を読んでいる。
  source: Sample Source 4
  verification: CONFIRMED

=== VOICE_4_EVIDENCE(Fairness) ===

[VOICE_4_EVIDENCE] 4-01(R1_fact_epsilon): これはVoice 4専用のfactであり、
3V記事では除外されるべきである。
  source: Sample Source 5
  verification: CONFIRMED

=== CROSS_REFERENCE ===

[CROSS_REFERENCE] X-01(R2_fact_zeta): 多くの大企業が自動雇用意思決定
ツールを使っている。
  source: Sample Source 6
  verification: CONFIRMED
"""


class LedgerAdapterTests(unittest.TestCase):
    def test_parse_ledger_entries_extracts_fields(self):
        entries = trial.parse_ledger_entries(RAW_LEDGER_SAMPLE)
        fact_ids = {e["fact_id"] for e in entries}
        for expected in ("R1_fact_alpha", "R1_fact_beta", "R2_fact_gamma",
                          "R2_fact_delta", "R1_fact_epsilon", "R2_fact_zeta"):
            self.assertIn(expected, fact_ids)
        by_id = {e["fact_id"]: e for e in entries}
        self.assertEqual(by_id["R1_fact_alpha"]["verification"], "CONFIRMED")
        self.assertEqual(by_id["R1_fact_beta"]["verification"], "PARTIALLY_CONFIRMED")
        self.assertEqual(by_id["R1_fact_alpha"]["voice_tag"], "1")
        self.assertIsNone(by_id["R2_fact_zeta"]["voice_tag"])  # CROSS_REFERENCE

    def test_build_family_x_compatible_ledger_text_excludes_voice4_and_unconfirmed(self):
        ledger_text, confirmed = trial.build_family_x_compatible_ledger_text(
            RAW_LEDGER_SAMPLE, num_visible_voices=3)
        fact_ids = {e["fact_id"] for e in confirmed}
        self.assertNotIn("R1_fact_epsilon", fact_ids)  # Voice 4 excluded
        self.assertNotIn("R1_fact_beta", fact_ids)  # not CONFIRMED
        for expected in ("R1_fact_alpha", "R2_fact_gamma", "R2_fact_delta", "R2_fact_zeta"):
            self.assertIn(expected, fact_ids)
        self.assertIn("[VERIFIED] R1_fact_alpha:", ledger_text)
        # Family X既存関数(無変更)が本Trialアダプタの出力を実際に読み取れることを確認
        extracted_ids = set(storyline_b3.extract_fact_ids_from_ledger(ledger_text))
        self.assertEqual(extracted_ids, fact_ids)


class VoiceAssignmentValidationTests(unittest.TestCase):
    def test_accepts_valid_1_or_2_fact_assignment(self):
        parsed = {
            "voices": [
                {"voice_key": "voice_1", "stakeholder": "Applicant", "angle": "a",
                 "fact_ids": ["R1_fact_alpha"]},
                {"voice_key": "voice_2", "stakeholder": "Recruiter", "angle": "b",
                 "fact_ids": ["R2_fact_gamma"]},
                {"voice_key": "voice_3", "stakeholder": "Business Owner", "angle": "c",
                 "fact_ids": ["R1_fact_alpha", "R2_fact_delta"]},
            ]
        }
        errors = trial.validate_voice_assignment(
            parsed, ["R1_fact_alpha", "R2_fact_gamma", "R2_fact_delta"])
        self.assertEqual(errors, [])

    def test_rejects_all_voices_same_fact_set(self):
        parsed = {
            "voices": [
                {"voice_key": "voice_1", "stakeholder": "Applicant", "angle": "a",
                 "fact_ids": ["R1_fact_alpha"]},
                {"voice_key": "voice_2", "stakeholder": "Recruiter", "angle": "b",
                 "fact_ids": ["R1_fact_alpha"]},
                {"voice_key": "voice_3", "stakeholder": "Business Owner", "angle": "c",
                 "fact_ids": ["R1_fact_alpha"]},
            ]
        }
        errors = trial.validate_voice_assignment(parsed, ["R1_fact_alpha"])
        self.assertIn("ALL_VOICES_SAME_FACT_SET", errors)

    def test_rejects_more_than_2_facts(self):
        parsed = {
            "voices": [
                {"voice_key": "voice_1", "stakeholder": "Applicant", "angle": "a",
                 "fact_ids": ["R1_fact_alpha", "R2_fact_gamma", "R2_fact_delta"]},
                {"voice_key": "voice_2", "stakeholder": "Recruiter", "angle": "b",
                 "fact_ids": ["R2_fact_gamma"]},
                {"voice_key": "voice_3", "stakeholder": "Business Owner", "angle": "c",
                 "fact_ids": ["R2_fact_delta"]},
            ]
        }
        errors = trial.validate_voice_assignment(
            parsed, ["R1_fact_alpha", "R2_fact_gamma", "R2_fact_delta"])
        self.assertTrue(any("FACT_IDS_COUNT_OUT_OF_RANGE" in e for e in errors))

    def test_rejects_unknown_fact_id(self):
        parsed = {
            "voices": [
                {"voice_key": "voice_1", "stakeholder": "Applicant", "angle": "a",
                 "fact_ids": ["NOT_A_REAL_FACT_ID"]},
                {"voice_key": "voice_2", "stakeholder": "Recruiter", "angle": "b",
                 "fact_ids": ["R2_fact_gamma"]},
                {"voice_key": "voice_3", "stakeholder": "Business Owner", "angle": "c",
                 "fact_ids": ["R2_fact_delta"]},
            ]
        }
        errors = trial.validate_voice_assignment(
            parsed, ["R1_fact_alpha", "R2_fact_gamma", "R2_fact_delta"])
        self.assertTrue(any("UNKNOWN_FACT_ID" in e for e in errors))


class DeterministicMetricsTests(unittest.TestCase):
    def test_detect_fact_intro_opener_true_cases(self):
        self.assertTrue(trial.detect_fact_intro_opener(
            "According to the report, many people are worried. I am too."))
        self.assertTrue(trial.detect_fact_intro_opener(
            "The study found that most workers feel this way. I feel it too."))
        self.assertTrue(trial.detect_fact_intro_opener(
            "A survey found that half of workers agree. That matches my own feeling."))
        self.assertTrue(trial.detect_fact_intro_opener(
            "49% of workers say the tool is biased. I am one of them."))

    def test_detect_fact_intro_opener_false_case_first_person_opening(self):
        self.assertFalse(trial.detect_fact_intro_opener(
            "I speak to a camera every time I apply for a job. Software scores my voice and face."))

    def test_find_abstraction_positions_detects_term_and_relative_position(self):
        text = "I worry about my own job today. " + ("x " * 50) + \
            "In the end this is about society and trust."
        hits = trial.find_abstraction_positions(text)
        terms = {h["term"] for h in hits}
        self.assertIn("society", terms)
        self.assertIn("trust", terms)
        for h in hits:
            self.assertGreater(h["relative_position"], 0.5)

    def test_run_deterministic_metrics_reports_fact_overlap_between_voices(self):
        sections = {
            "hook_body": "hook text " * 10,
            "voice_1_body": "I worry about my score. This is my story.",
            "voice_2_body": "I sort resumes every day. This is my job.",
            "voice_3_body": "I check the dashboard weekly. This is my role.",
            "tension_body": "tension text " * 10,
            "closing_body": "closing text " * 10,
        }
        voice_fact_ids = {
            "voice_1": ["R1_fact_alpha"],
            "voice_2": ["R2_fact_gamma"],
            "voice_3": ["R1_fact_alpha", "R2_fact_delta"],
        }
        metrics = trial.run_deterministic_metrics(sections, voice_fact_ids)
        overlap = metrics["fact_id_overlap_between_voices"]
        self.assertEqual(overlap["pairwise_shared_fact_ids"]["voice_1_vs_voice_3"], ["R1_fact_alpha"])
        self.assertEqual(overlap["pairwise_shared_fact_ids"]["voice_1_vs_voice_2"], [])
        self.assertTrue(overlap["any_shared"])


class ExistingFamilyXReuseTests(unittest.TestCase):
    def test_r1_to_r2_uses_family_x_existing_revision_instructions_and_chaining(self):
        # Family Xの既存Revision指示文(逐語、日本語)がそのまま使われることをassertする
        # (Family Y専用Revision仕様を新設していないことの技術的な裏付け)。
        self.assertIs(trial.fx_r1r2, fx_r1r2)
        src = inspect.getsource(trial.run_r1_to_r2)
        self.assertIn('fx_r1r2.REVISION_INSTRUCTIONS["r1"]', src)
        self.assertIn('fx_r1r2.REVISION_INSTRUCTIONS["r2"]', src)
        self.assertIn("fx_r1r2.call_with_previous_response_id", src)
        self.assertEqual(
            fx_r1r2.REVISION_INSTRUCTIONS["r1"],
            "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。")
        self.assertEqual(
            fx_r1r2.REVISION_INSTRUCTIONS["r2"],
            "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。")

    def test_fact_selection_uses_family_x_existing_function_unmodified(self):
        src = inspect.getsource(trial.run_step1_fact_selection)
        self.assertIn("storyline_b3.run_storyline_b3_selection", src)


class MarkdownAssemblyParseRoundTripTests(unittest.TestCase):
    def test_assemble_markdown_produces_six_heading_structure_parseable_by_family_b(self):
        sections = {
            "hook_heading": "Hook H", "hook_body": "hook body text.",
            "voice_1_heading": "Voice 1: A", "voice_1_body": "I am voice one.",
            "voice_2_heading": "Voice 2: B", "voice_2_body": "I am voice two.",
            "voice_3_heading": "Voice 3: C", "voice_3_body": "I am voice three.",
            "tension_heading": "Why", "tension_body": "tension body text.",
            "closing_heading": "What it means", "closing_body": "closing body text.",
        }
        md = trial.assemble_markdown(sections, "Sample Title")
        parsed = trial.parse_article_or_raise(md, "unit-test")
        self.assertEqual(parsed["voice_1_body"], "I am voice one.")
        self.assertEqual(parsed["voice_2_body"], "I am voice two.")
        self.assertEqual(parsed["voice_3_body"], "I am voice three.")
        self.assertEqual(parsed["tension_body"], "tension body text.")
        self.assertEqual(parsed["closing_body"], "closing body text.")


if __name__ == "__main__":
    unittest.main()
