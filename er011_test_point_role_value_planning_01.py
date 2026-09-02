# ============================================================
# er011_test_point_role_value_planning_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Point Role Planning + Point
# Value QAのテスト
# ============================================================
import json
import unittest

import er011_point_role_value_planning_01 as rp

GOOD_PLAN = {
    "point_one": {
        "role": "a methodological nuance", "new_listener_takeaway": "why the comparison is fair",
        "evidence_anchor": "the fare-threshold comparison", "why_it_matters": "it shows the effect is real",
        "must_not_overlap_with_full_story": "the headline finding itself",
        "must_not_overlap_with_other_point": "the psychological reason people comply",
    },
    "point_two": {
        "role": "a psychological reason", "new_listener_takeaway": "why people follow suggested amounts",
        "evidence_anchor": "the anchoring literature cited in the Ledger",
        "why_it_matters": "it explains listener's own behavior",
        "must_not_overlap_with_full_story": "the headline finding itself",
        "must_not_overlap_with_other_point": "the methodological nuance",
    },
}

GOOD_VALUE_QA = {
    "point_one": {f: "PASS" for f in rp.VALUE_QA_FIELDS} | {"reasoning": "新しい示唆がある。"},
    "point_two": {f: "PASS" for f in rp.VALUE_QA_FIELDS} | {"reasoning": "新しい示唆がある。"},
}


class RolePlanningPromptTests(unittest.TestCase):
    def test_prompt_contains_topic_and_ledger(self):
        prompt = rp.ROLE_PLANNING_PROMPT_TEMPLATE.format(topic="TOPIC_MARKER", verified_ledger_text="LEDGER_MARKER")
        self.assertIn("TOPIC_MARKER", prompt)
        self.assertIn("LEDGER_MARKER", prompt)

    def test_build_role_planning_block_contains_all_fields(self):
        block = rp.build_role_planning_block(GOOD_PLAN)
        for point in ("point_one", "point_two"):
            for field in rp._ROLE_PLAN_FIELDS:
                self.assertIn(GOOD_PLAN[point][field], block)


class RunPointRolePlanningFakeClientTests(unittest.TestCase):
    def test_success_path_returns_parsed_plan(self):
        raw = json.dumps(GOOD_PLAN)

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_1"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        result = rp.run_point_role_planning(FakeClient(), "topic", "ledger", model="fake-model",
                                             reasoning_effort="high")
        self.assertEqual(result["parsed"], GOOD_PLAN)
        self.assertEqual(result["model"], "fake-model")

    def test_model_mismatch_raises(self):
        class FakeResponse:
            model = "wrong-model"
            output_text = json.dumps(GOOD_PLAN)
            id = "resp_fake_2"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        with self.assertRaises(rp.RolePlanningModelMismatchError):
            rp.run_point_role_planning(FakeClient(), "topic", "ledger", model="fake-model",
                                        reasoning_effort="high")


class RunPointValueQaFakeClientTests(unittest.TestCase):
    def test_all_pass_yields_pass_status(self):
        raw = json.dumps(GOOD_VALUE_QA)

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_3"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        result = rp.run_point_value_qa(FakeClient(), "full story", "point one body", "point two body",
                                        model="fake-model", reasoning_effort="high")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["per_point"]["point_one"]["fail_fields"], [])

    def test_caveat_only_point_flagged_ng(self):
        bad = json.loads(json.dumps(GOOD_VALUE_QA))
        bad["point_two"]["qa_not_caveat_only"] = "FAIL"
        bad["point_two"]["qa_adds_new_value"] = "FAIL"
        bad["point_two"]["reasoning"] = "留保のみで構成されている。"
        raw = json.dumps(bad)

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_4"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        result = rp.run_point_value_qa(FakeClient(), "full story", "point one body", "point two body",
                                        model="fake-model", reasoning_effort="high")
        self.assertEqual(result["status"], "NG")
        self.assertIn("qa_not_caveat_only", result["per_point"]["point_two"]["fail_fields"])
        self.assertIn("qa_adds_new_value", result["per_point"]["point_two"]["fail_fields"])
        self.assertEqual(result["per_point"]["point_one"]["fail_fields"], [])

    def test_model_mismatch_raises(self):
        class FakeResponse:
            model = "wrong-model"
            output_text = json.dumps(GOOD_VALUE_QA)
            id = "resp_fake_5"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        with self.assertRaises(rp.ValueQaModelMismatchError):
            rp.run_point_value_qa(FakeClient(), "full story", "p1", "p2", model="fake-model",
                                   reasoning_effort="high")

    def test_missing_field_marks_item_not_ok(self):
        bad = json.loads(json.dumps(GOOD_VALUE_QA))
        del bad["point_one"]["qa_adds_new_value"]
        raw = json.dumps(bad)

        class FakeResponse:
            model = "fake-model"
            output_text = raw
            id = "resp_fake_6"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        result = rp.run_point_value_qa(FakeClient(), "full story", "p1", "p2", model="fake-model",
                                        reasoning_effort="high")
        self.assertEqual(result["status"], "NG")
        self.assertFalse(result["per_point"]["point_one"]["ok"])


class DiagnosticNoteTests(unittest.TestCase):
    def test_note_mentions_failing_fields_and_reasoning(self):
        value_qa_result = {
            "per_point": {
                "point_one": {"ok": True, "fail_fields": [], "reasoning": ""},
                "point_two": {"ok": True, "fail_fields": ["qa_not_caveat_only", "qa_adds_new_value"],
                              "reasoning": "留保のみで構成されている。"},
            }
        }
        note = rp.build_value_qa_diagnostic_note(value_qa_result)
        self.assertIn("Point Two failed", note)
        self.assertIn("qa_not_caveat_only", note)
        self.assertIn("留保のみで構成されている", note)
        self.assertNotIn("Point One failed", note)


if __name__ == "__main__":
    unittest.main()
