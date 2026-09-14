# ============================================================
# er013_family_c_future_qa_test_07.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07
# ============================================================
# 決定的部分のみのテスト(API呼び出しなし、¥0)。run_project_regression.py
# --pattern "er013*_test_*.py" から収集される。
# ============================================================
from __future__ import annotations

import unittest

import er013_family_c_future_provocation_07 as prov7
import er013_family_c_future_writer_07 as writer7


def _make_candidate(cid, scale, combined_with=None, **overrides):
    c = {
        "id": cid, "scale": scale, "combined_with": combined_with,
        "premise": f"premise {cid}", "core_provocation": f"cp {cid}",
        "what_is_the_future": "future", "what_is_interesting": "interesting",
        "what_would_surprise_the_reader": "surprise", "what_happens_as_a_story": "story",
        "reference_six_axis_scores": {axis: 2 for axis in prov7.SIX_AXES_REFERENCE},
        "safety_boundary_note": "note",
    }
    c.update(overrides)
    return c


class ScaleLensDefinitionTest(unittest.TestCase):
    def test_five_scales_and_lenses_defined(self):
        self.assertEqual(prov7.SCALES, ["A_intimate", "B_societal", "C_radical"])
        self.assertEqual(prov7.LENSES, ["D_second_order", "E_inversion"])
        self.assertEqual(len(prov7.ALL_SCALE_LENS), 5)
        for key in prov7.ALL_SCALE_LENS:
            self.assertIn(key, prov7.SCALE_LENS_DEFINITIONS)

    def test_candidate_prompt_requests_all_five_scales_with_distribution(self):
        prompt = prov7.build_candidate_prompt("the future of home robots", "note", "ledger")
        self.assertIn("3 to 4 candidates with scale=\"A_intimate\"", prompt)
        self.assertIn("3 to 4 candidates with scale=\"B_societal\"", prompt)
        self.assertIn("3 to 4 candidates with scale=\"C_radical\"", prompt)
        self.assertIn("1 to 2 candidates with scale=\"D_second_order\"", prompt)
        self.assertIn("1 to 2 candidates with scale=\"E_inversion\"", prompt)
        self.assertIn("Do NOT select a single winner here", prompt)


class ScoreTableReferenceTest(unittest.TestCase):
    def test_build_score_table_reference_is_non_selecting(self):
        parsed = {"candidates": [
            _make_candidate("CP-A1", "A_intimate",
                             reference_six_axis_scores={axis: 3 for axis in prov7.SIX_AXES_REFERENCE}),
            _make_candidate("CP-B1", "B_societal",
                             reference_six_axis_scores={axis: 1 for axis in prov7.SIX_AXES_REFERENCE}),
        ]}
        table = prov7.build_score_table_reference(parsed)
        row_a = next(r for r in table if r["id"] == "CP-A1")
        row_b = next(r for r in table if r["id"] == "CP-B1")
        self.assertEqual(row_a["reference_total_score"], 18)
        self.assertEqual(row_b["reference_total_score"], 6)
        self.assertNotIn("is_selected", row_a)  # v6と異なり選定フラグを持たない


class RankingValidationTest(unittest.TestCase):
    def test_validate_ranking_accepts_valid_full_ranking(self):
        ranking_parsed = {"ranking": [
            {"rank": 1, "id": "CP-A1", "reason": "r1"},
            {"rank": 2, "id": "CP-B1", "reason": "r2"},
        ]}
        prov7.validate_ranking(ranking_parsed, ["CP-A1", "CP-B1"])  # raises on failure

    def test_validate_ranking_rejects_tied_ranks(self):
        ranking_parsed = {"ranking": [
            {"rank": 1, "id": "CP-A1", "reason": "r1"},
            {"rank": 1, "id": "CP-B1", "reason": "r2"},
        ]}
        with self.assertRaises(RuntimeError):
            prov7.validate_ranking(ranking_parsed, ["CP-A1", "CP-B1"])

    def test_validate_ranking_rejects_mismatched_ids(self):
        ranking_parsed = {"ranking": [
            {"rank": 1, "id": "CP-A1", "reason": "r1"},
            {"rank": 2, "id": "CP-ZZ", "reason": "r2"},
        ]}
        with self.assertRaises(RuntimeError):
            prov7.validate_ranking(ranking_parsed, ["CP-A1", "CP-B1"])

    def test_validate_ranking_rejects_count_mismatch(self):
        ranking_parsed = {"ranking": [{"rank": 1, "id": "CP-A1", "reason": "r1"}]}
        with self.assertRaises(RuntimeError):
            prov7.validate_ranking(ranking_parsed, ["CP-A1", "CP-B1"])


class RepresentativeSelectionTest(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            _make_candidate("CP-A1", "A_intimate"),
            _make_candidate("CP-A2", "A_intimate"),
            _make_candidate("CP-B1", "B_societal"),
            _make_candidate("CP-C1", "C_radical"),
            _make_candidate("CP-D1", "D_second_order", combined_with="B_societal"),
            _make_candidate("CP-E1", "E_inversion"),
        ]

    def test_top_pick_per_scale_uses_best_rank_not_id_order(self):
        ranking_parsed = {
            "ranking": [
                {"rank": 1, "id": "CP-A2", "reason": "stronger than CP-A1"},
                {"rank": 2, "id": "CP-B1", "reason": "b"},
                {"rank": 3, "id": "CP-C1", "reason": "c"},
                {"rank": 4, "id": "CP-A1", "reason": "weaker angle"},
                {"rank": 5, "id": "CP-D1", "reason": "d"},
                {"rank": 6, "id": "CP-E1", "reason": "e"},
            ],
            "extra_lens_recommendation": {"recommended": False, "id": None, "reason": "no clear case"},
        }
        selection = prov7.compute_representative_selection(self.candidates, ranking_parsed)
        self.assertEqual(selection["top_pick_by_scale"]["A_intimate"], "CP-A2")
        self.assertEqual(selection["top_pick_by_scale"]["B_societal"], "CP-B1")
        self.assertEqual(selection["top_pick_by_scale"]["C_radical"], "CP-C1")
        self.assertFalse(selection["extra_lens_included"])
        self.assertIsNone(selection["extra_lens_id"])

    def test_extra_lens_included_when_recommended_and_is_a_lens_candidate(self):
        ranking_parsed = {
            "ranking": [
                {"rank": 1, "id": "CP-D1", "reason": "unexpectedly strong"},
                {"rank": 2, "id": "CP-A1", "reason": "a"},
                {"rank": 3, "id": "CP-B1", "reason": "b"},
                {"rank": 4, "id": "CP-C1", "reason": "c"},
                {"rank": 5, "id": "CP-A2", "reason": "a2"},
                {"rank": 6, "id": "CP-E1", "reason": "e"},
            ],
            "extra_lens_recommendation": {"recommended": True, "id": "CP-D1",
                                           "reason": "clearly stronger than the scale winners"},
        }
        selection = prov7.compute_representative_selection(self.candidates, ranking_parsed)
        self.assertTrue(selection["extra_lens_included"])
        self.assertEqual(selection["extra_lens_id"], "CP-D1")

    def test_extra_lens_recommendation_pointing_to_non_lens_candidate_is_ignored(self):
        ranking_parsed = {
            "ranking": [
                {"rank": 1, "id": "CP-A1", "reason": "a"},
                {"rank": 2, "id": "CP-A2", "reason": "a2"},
                {"rank": 3, "id": "CP-B1", "reason": "b"},
                {"rank": 4, "id": "CP-C1", "reason": "c"},
                {"rank": 5, "id": "CP-D1", "reason": "d"},
                {"rank": 6, "id": "CP-E1", "reason": "e"},
            ],
            "extra_lens_recommendation": {"recommended": True, "id": "CP-A1",
                                           "reason": "technically-invalid recommendation (not a D/E id)"},
        }
        selection = prov7.compute_representative_selection(self.candidates, ranking_parsed)
        self.assertFalse(selection["extra_lens_included"])
        self.assertIsNone(selection["extra_lens_id"])


class WriterV7ContractTest(unittest.TestCase):
    def test_constraint_count_is_five_same_as_v6(self):
        self.assertEqual(writer7.CONSTRAINT_COUNT, 5)
        self.assertEqual(len(writer7.CONSTRAINT_LIST), 5)

    def test_markers_reused_unmodified_from_writer_02(self):
        import er013_family_c_future_writer_02 as fcw2
        self.assertEqual(writer7.IMAGINED_OPEN_TEMPLATE, fcw2.IMAGINED_OPEN_TEMPLATE)
        self.assertEqual(writer7.FACT_OPEN_TEMPLATE, fcw2.FACT_OPEN_TEMPLATE)
        self.assertEqual(writer7.MAX_FACT_EXCEPTIONS, 2)

    def test_prompt_defaults_current_fact_to_zero_and_forbids_stat_sentences(self):
        prompt = writer7.build_family_c_writer_v7_prompt(
            core_provocation="What if a robot understood your life better than you do?",
            premise="A future where a home robot quietly takes over daily decisions.",
            theme_label="the future of home robots",
            ledger_excerpt="- HR-001: some verified fact",
        )
        self.assertIn("default is ZERO", prompt)
        self.assertIn("should be\nrare", prompt)
        self.assertIn("In 2023, more than", prompt)  # forbidden-example is quoted to warn against it
        self.assertIn("[[IMAGINED:", prompt)
        self.assertIn("[[FACT:", prompt)
        self.assertIn("350 words", prompt)
        self.assertNotIn("Cite AT MOST", prompt)  # v6の圧力の強い表現は撤廃済み

    def test_prompt_with_improvement_note(self):
        prompt = writer7.build_family_c_writer_v7_prompt(
            core_provocation="cp", premise="p", theme_label="t", ledger_excerpt="l",
            improvement_note="Make the future leap stronger.")
        self.assertIn("Make the future leap stronger.", prompt)


if __name__ == "__main__":
    unittest.main()
