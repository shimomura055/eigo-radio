# ============================================================
# er013_family_c_future_qa_test_06.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
# ============================================================
# 決定的部分のみのテスト(API呼び出しなし、¥0)。run_project_regression.py
# --pattern "er013*_test_*.py" から収集される。
# ============================================================
from __future__ import annotations

import unittest

import er013_family_c_future_provocation_06 as prov6
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_safety_06 as safety6
import er013_family_c_future_spark_gate_06 as spark6
import er013_family_c_future_writer_06 as writer6


class ProvocationTest(unittest.TestCase):
    def _make_parsed(self, scores_by_id):
        candidates = []
        for cid, scores in scores_by_id.items():
            c = {"id": cid, "premise": f"premise {cid}", "core_provocation": f"cp {cid}",
                 "safety_boundary_note": "note"}
            c.update(scores)
            candidates.append(c)
        return {"candidates": candidates, "selected_id": list(scores_by_id.keys())[0],
                "selection_rationale": "because it is the most interesting one"}

    def test_build_score_table_totals_and_selected_flag(self):
        parsed = self._make_parsed({
            "CP-01": {axis: 2 for axis in prov6.SIX_AXES},
            "CP-02": {axis: 3 for axis in prov6.SIX_AXES},
        })
        table = prov6.build_score_table(parsed)
        row1 = next(r for r in table if r["id"] == "CP-01")
        row2 = next(r for r in table if r["id"] == "CP-02")
        self.assertEqual(row1["total_score"], 12)
        self.assertEqual(row2["total_score"], 18)
        self.assertTrue(row1["is_selected"])
        self.assertFalse(row2["is_selected"])

    def test_get_selected_candidate_found(self):
        parsed = self._make_parsed({"CP-01": {axis: 2 for axis in prov6.SIX_AXES}})
        selected = prov6.get_selected_candidate(parsed)
        self.assertEqual(selected["id"], "CP-01")

    def test_get_selected_candidate_missing_raises(self):
        parsed = self._make_parsed({"CP-01": {axis: 2 for axis in prov6.SIX_AXES}})
        parsed["selected_id"] = "CP-99"
        with self.assertRaises(RuntimeError):
            prov6.get_selected_candidate(parsed)


class WriterContractTest(unittest.TestCase):
    def test_constraint_count_is_five(self):
        self.assertEqual(writer6.CONSTRAINT_COUNT, 5)
        self.assertEqual(len(writer6.CONSTRAINT_LIST), 5)

    def test_markers_reused_unmodified_from_writer_02(self):
        import er013_family_c_future_writer_02 as fcw2
        self.assertEqual(writer6.IMAGINED_OPEN_TEMPLATE, fcw2.IMAGINED_OPEN_TEMPLATE)
        self.assertEqual(writer6.FACT_OPEN_TEMPLATE, fcw2.FACT_OPEN_TEMPLATE)
        self.assertEqual(writer6.MAX_FACT_EXCEPTIONS, 2)

    def test_build_prompt_contains_core_provocation_and_markers(self):
        prompt = writer6.build_family_c_writer_v6_prompt(
            core_provocation="What if a robot slowly made your choices for you?",
            premise="A future where a home robot quietly takes over daily decisions.",
            theme_label="the future of home robots",
            ledger_excerpt="- HR-001: some verified fact",
        )
        self.assertIn("What if a robot slowly made your choices for you?", prompt)
        self.assertIn("[[IMAGINED:", prompt)
        self.assertIn("[[FACT:", prompt)
        self.assertIn("350 words", prompt)

    def test_build_prompt_with_improvement_note(self):
        prompt = writer6.build_family_c_writer_v6_prompt(
            core_provocation="cp", premise="p", theme_label="t", ledger_excerpt="l",
            improvement_note="Make the future leap stronger.")
        self.assertIn("Make the future leap stronger.", prompt)


class SparkGateTest(unittest.TestCase):
    def _scores(self, **overrides):
        base = {axis: 2 for axis in spark6.AXES}
        base.update(overrides)
        base["three_directions_check"] = {"directions_found": ["a"], "reinforces_core_provocation": True,
                                           "dilution_note": ""}
        base["one_sentence_why_interesting"] = "because it raises a real question"
        return base

    def test_pass_when_all_axes_ge_2(self):
        result = spark6.compute_verdict(self._scores())
        self.assertEqual(result["verdict"], "PASS")

    def test_fail_when_future_leap_low(self):
        result = spark6.compute_verdict(self._scores(future_leap=1))
        self.assertEqual(result["verdict"], "FAIL")
        cause = spark6.classify_failure_cause(result)
        self.assertEqual(cause["category"], "Future Leap不足")

    def test_fail_when_core_provocation_clarity_low(self):
        result = spark6.compute_verdict(self._scores(core_provocation_clarity=0))
        self.assertEqual(result["verdict"], "FAIL")
        cause = spark6.classify_failure_cause(result)
        self.assertEqual(cause["category"], "Core Provocation弱い")

    def test_voices_diluted_detected(self):
        scores = self._scores(curiosity=1)
        scores["three_directions_check"]["reinforces_core_provocation"] = False
        result = spark6.compute_verdict(scores)
        self.assertTrue(result["voices_diluted"])
        cause = spark6.classify_failure_cause(result)
        self.assertEqual(cause["category"], "3 Voicesで希釈")

    def test_failure_cause_categories_are_the_delegated_seven(self):
        self.assertEqual(len(spark6.FAILURE_CAUSE_CATEGORIES), 7)


class SafetyLayerExtractionTest(unittest.TestCase):
    def test_extract_layers_separates_fact_imagined_and_bridge(self):
        article = (
            "[[META]]internal notes[[/META]]\n"
            "Intro bridge sentence connecting today to tomorrow.\n"
            "[[FACT: HR-001]]Robot vacuums are common today.[[/FACT]]\n"
            "More bridge text here.\n"
            "[[IMAGINED: around 2035]]A robot quietly folds the laundry.[[/IMAGINED]]\n"
            "Closing bridge reflection."
        )
        layers = safety6.extract_layers(article)
        self.assertEqual(len(layers["fact_blocks"]), 1)
        self.assertEqual(layers["fact_blocks"][0]["ref_id"], "HR-001")
        self.assertEqual(len(layers["imagined_blocks"]), 1)
        self.assertEqual(layers["imagined_blocks"][0]["timeframe"], "around 2035")
        self.assertNotIn("internal notes", layers["text_no_meta"])
        self.assertNotIn("Robot vacuums are common today.", layers["bridge_text"])
        self.assertNotIn("quietly folds the laundry", layers["bridge_text"])
        self.assertIn("Intro bridge sentence", layers["bridge_text"])
        self.assertIn("Robot vacuums are common today.", layers["reader_text"])
        self.assertIn("quietly folds the laundry", layers["reader_text"])
        self.assertNotIn("[[FACT:", layers["reader_text"])
        self.assertNotIn("[[IMAGINED:", layers["reader_text"])

    def test_decisive_checks_on_imagined_blocks(self):
        good_blocks = [{"timeframe": "around 2035", "body": "A robot folds laundry.", "start": 0, "end": 1}]
        bad_blocks_no_timeframe = [{"timeframe": "", "body": "A robot folds laundry.", "start": 0, "end": 1}]
        bad_blocks_fact_leak = [{"timeframe": "around 2035",
                                  "body": "[[FACT: HR-001]]leaked[[/FACT]]", "start": 0, "end": 1}]
        self.assertEqual(len(fcq2.check_fact_markers_inside_imagined(good_blocks)), 0)
        self.assertEqual(len(fcq2.check_fact_markers_inside_imagined(bad_blocks_fact_leak)), 1)
        self.assertEqual(bad_blocks_no_timeframe[0]["timeframe"].strip(), "")


if __name__ == "__main__":
    unittest.main()
