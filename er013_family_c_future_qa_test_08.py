# ============================================================
# er013_family_c_future_qa_test_08.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08
# ============================================================
# 決定的部分のみのテスト(API呼び出しなし、¥0)。run_project_regression.py
# --pattern "er013*_test_*.py" から収集される。
# ============================================================
from __future__ import annotations

import unittest

import er013_family_c_future_eval_08 as eval8
import er013_family_c_future_provocation_08 as prov8
import er013_family_c_future_trial_08_run as trial08
import er013_family_c_future_writer_08 as writer8


class WriterV8ConstraintTest(unittest.TestCase):
    def test_constraint_count_is_six(self):
        self.assertEqual(writer8.CONSTRAINT_COUNT, 6)
        self.assertEqual(len(writer8.CONSTRAINT_LIST), 6)

    def test_word_target_and_range_match_delegation(self):
        self.assertEqual(writer8.WORD_TARGET, 350)
        self.assertEqual(writer8.WORD_ACCEPTABLE_RANGE, (300, 420))

    def test_max_characters_is_three(self):
        self.assertEqual(writer8.MAX_CHARACTERS, 3)

    def test_prompt_forbids_fact_and_mentions_character_limit(self):
        prompt = writer8.build_family_c_writer_v8_prompt("a core provocation", "the future of home robots")
        self.assertIn("forbidden, not optional", prompt)
        self.assertIn("ZERO current-fact sentences", prompt)
        self.assertIn("3 at the absolute most", prompt)
        self.assertNotIn("[[FACT:", prompt)  # FACTマーカーの使い方自体を提示しない

    def test_prompt_does_not_impose_scale_or_fixed_angles(self):
        prompt = writer8.build_family_c_writer_v8_prompt("a core provocation", "the future of memory")
        for banned in ("Intimate", "Societal", "Radical", "convenience appeal", "quiet shift"):
            self.assertNotIn(banned, prompt)


class ProvocationV8Test(unittest.TestCase):
    def test_select_core_idea_valid(self):
        parsed = {
            "candidates": [
                {"id": "c1", "core_provocation": "cp1", "why_interesting": "w1"},
                {"id": "c2", "core_provocation": "cp2", "why_interesting": "w2"},
            ],
            "selected_id": "c2", "selection_reason": "reason",
        }
        result = prov8.select_core_idea(parsed)
        self.assertEqual(result["selected"]["id"], "c2")
        self.assertEqual(result["candidate_count"], 2)

    def test_select_core_idea_invalid_id_raises(self):
        parsed = {
            "candidates": [{"id": "c1", "core_provocation": "cp1", "why_interesting": "w1"}],
            "selected_id": "does_not_exist", "selection_reason": "reason",
        }
        with self.assertRaises(RuntimeError):
            prov8.select_core_idea(parsed)

    def test_candidate_schema_allows_1_to_3(self):
        schema = prov8.CORE_IDEA_JSON_SCHEMA["schema"]["properties"]["candidates"]
        self.assertEqual(schema["minItems"], 1)
        self.assertEqual(schema["maxItems"], 3)


class EvalV8CharacterCountTest(unittest.TestCase):
    def test_proper_noun_excludes_sentence_start(self):
        text = "Maya walked home. She thought about her mother the whole way."
        candidates = eval8.find_proper_noun_candidates(text)
        self.assertIn("Maya", candidates)
        self.assertNotIn("She", candidates)  # 文頭語は除外

    def test_relationship_reference_detected(self):
        text = "She called her mother and told his friend the news."
        refs = eval8.find_relationship_references(text)
        self.assertIn("her mother", refs)
        self.assertIn("his friend", refs)

    def test_count_characters_heuristic_combines(self):
        text = "Maya looked at her mother. Her friend Tom waved back."
        result = eval8.count_characters_heuristic(text)
        self.assertGreaterEqual(result["proper_noun_count"], 1)
        self.assertGreaterEqual(result["relationship_reference_count"], 1)
        self.assertEqual(
            result["estimated_total_characters"],
            result["proper_noun_count"] + result["relationship_reference_count"])

    def test_listening_metrics_basic(self):
        text = "This is short. This is also short."
        metrics = eval8.compute_listening_metrics(text)
        self.assertEqual(metrics["sentence_count"], 2)
        self.assertEqual(metrics["avg_sentence_word_count"], 3.5)  # (3 + 4) / 2


class TrialRunUtilityTest(unittest.TestCase):
    def test_theme_config_has_five_themes_with_required_keys(self):
        self.assertEqual(list(trial08.THEME_CONFIG_08.keys()), trial08.THEME_ORDER)
        self.assertEqual(len(trial08.THEME_CONFIG_08), 5)
        for cfg in trial08.THEME_CONFIG_08.values():
            for key in ("theme_label_en", "topic_ja_placeholder", "inspiration_note"):
                self.assertIn(key, cfg)
                self.assertTrue(cfg[key])

    def test_extract_title_if_present_detects_short_first_line(self):
        text = "A Quiet Morning\nMaya woke up and the room already knew her mood."
        title, body = trial08.extract_title_if_present(text)
        self.assertEqual(title, "A Quiet Morning")
        self.assertNotIn("A Quiet Morning", body)

    def test_extract_title_if_present_no_title_when_first_line_is_prose(self):
        text = "Maya woke up and the room already knew her mood, which was unusual."
        title, body = trial08.extract_title_if_present(text)
        self.assertIsNone(title)
        self.assertEqual(body, text)

    def test_scan_current_fact_leak_detects_year_and_percent(self):
        leaked = "In 2023, more than 40% of homes had a robot, according to a report."
        result = trial08.scan_current_fact_leak(leaked)
        self.assertGreater(result["leak_count"], 0)

    def test_scan_current_fact_leak_clean_text_has_zero_hits(self):
        clean = "Maya looked out the window and wondered what her mother would say."
        result = trial08.scan_current_fact_leak(clean)
        self.assertEqual(result["leak_count"], 0)

    def test_budget_guard_raises_when_over_hard_cap(self):
        with self.assertRaises(RuntimeError):
            trial08.budget_guard("test_stage", "er013_output/__nonexistent_log__.jsonl",
                                  hard_cap_jpy=-1.0, soft_target_jpy=0.0)

    def test_budget_guard_passes_when_under_hard_cap(self):
        total = trial08.budget_guard("test_stage", "er013_output/__nonexistent_log__.jsonl",
                                      hard_cap_jpy=100.0, soft_target_jpy=50.0)
        self.assertEqual(total["total_jpy"], 0.0)


if __name__ == "__main__":
    unittest.main()
