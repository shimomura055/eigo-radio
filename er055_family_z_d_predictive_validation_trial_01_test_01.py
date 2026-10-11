# test for er055 driver (mock/fake only, no paid API)
import copy
import os
import tempfile
import types
import unittest

import er055_family_z_d_predictive_validation_trial_01 as d


def _fake_seed():
    return {"original_summary": "s", "seed_elements": ["a", "b"], "discarded_elements": ["x"],
            "conversion_plan": "plan"}


class FakeResp:
    def __init__(self, model, text):
        self.model, self.output_text, self.id = model, text, "fake"
        self.usage = types.SimpleNamespace(
            input_tokens=1000, output_tokens=1000,
            input_tokens_details=types.SimpleNamespace(cached_tokens=0),
            output_tokens_details=types.SimpleNamespace(reasoning_tokens=10))


class FakeClient:
    def __init__(self, model):
        self.calls = 0
        self.responses = types.SimpleNamespace(create=self._create)
        self.model = model

    def _create(self, **kw):
        import json
        self.calls += 1
        if "text" in kw:
            return FakeResp(self.model, json.dumps(_fake_seed()))
        return FakeResp(self.model, "### T\n\n" + " ".join(["w"] * 300))


class T(unittest.TestCase):
    def test_same_prompt_except_source_title_author(self):
        msgs = {}
        for w in d.WORK_ORDER:
            src = d.load_source(w)["text"]
            dev, user = d.build_seed_messages("raw", w, src)
            msgs[w] = (dev, user.replace(src.strip(), "<SRC>")
                       .replace(d.WORKS[w]["title_ja"], "<T>").replace(d.WORKS[w]["author_ja"], "<A>"))
        self.assertEqual(msgs["L13"], msgs["L11"])
        self.assertEqual(d.build_story_prompt(_fake_seed()), d.build_story_prompt(copy.deepcopy(_fake_seed())))

    def test_identical_to_trial02_constants_and_story_prompt(self):
        import er018_fiction_external_seed_selection_criteria_trial_02 as t2
        import er018_fiction_story_dna_e_axis_redesign_01 as ea
        self.assertEqual(d.SEED_DEVELOPER_MESSAGE, t2.SEED_DEVELOPER_MESSAGE)
        self.assertEqual(d.SEED_USER_TEMPLATE_BRIEF, t2.SEED_USER_TEMPLATE)
        self.assertEqual(d.SEED_JSON_SCHEMA, t2.SEED_JSON_SCHEMA)
        self.assertEqual(d.STORY_PROMPT_TEMPLATE, t2.STORY_PROMPT_TEMPLATE)
        self.assertEqual(d.WRITER_DEVELOPER_MESSAGE, ea.WRITER_DEVELOPER_MESSAGE)
        self.assertEqual(d.build_story_prompt(_fake_seed()), t2.build_story_prompt(_fake_seed()))
        # brief mode == 既存方式のSeed user message
        brief = {"source_brief": "B", "conversion_plan": "C"}
        _, u = d.build_seed_messages("brief", "L13", "", brief)
        self.assertEqual(u, t2.SEED_USER_TEMPLATE.format(source_brief="B", conversion_plan="C"))
        self.assertEqual((d.SEED_EFFORT, d.STORY_EFFORT, d.STORY_MAX_ATTEMPTS), ("medium", "high", 2))

    def test_raw_template_differs_only_in_header(self):
        a = d.SEED_USER_TEMPLATE_BRIEF.replace(d._BRIEF_HEADER, "")
        b = d.SEED_USER_TEMPLATE_RAW.replace(d._RAW_HEADER, "")
        self.assertEqual(a, b)

    def test_no_leak_tokens(self):
        for w in d.WORK_ORDER:
            dev, user = d.build_seed_messages("raw", w, d.load_source(w)["text"])
            for t in d.LEAK_TOKENS:
                self.assertNotIn(t, dev + user)

    def test_deny_guard(self):
        for p in ("er054_output/family_z_story_pool_trial_01/SEALED_PAST_RESULTS_L01_L06.json",
                  "er054_output/family_z_story_pool_trial_01/PHASE_C_RESULTS_02.json",
                  "er054_output/family_z_story_quality_model_comparison_trial_01/PAST_COMPARISON_01.md",
                  "er054_output/family_z_story_pool_trial_01/screening/L13.json",
                  "er054_output/family_z_story_quality_model_comparison_trial_01/SCORE_TABLE_01.md"):
            with self.assertRaises(d.SealedAccessError):
                d.read_text_guarded(p)
        d.assert_not_sealed(os.path.join(d.SRC_DIR, "L13", "text_plain.txt"))

    def test_real_rejected_without_approval(self):
        self.assertEqual(d.main(["--mode", "real", "--model", "gpt-6-luna"]), 2)
        self.assertEqual(d.main(["--mode", "real", "--approved-budget-jpy", "5"]), 2)  # model未指定
        self.assertEqual(d.main(["--mode", "real", "--model", "gpt-6-luna", "--approved-budget-jpy", "0.1"]), 2)
        self.assertEqual(d.main(["--mode", "real", "--model", "gpt-4o", "--approved-budget-jpy", "5"]), 2)

    def test_allowed_models_fixed(self):
        self.assertEqual(d.ALLOWED_MODELS, ("gpt-5.6-luna", "gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"))

    def test_production_routing_untouched(self):
        import er006_model_routing_contract_01 as r
        before = copy.deepcopy(r.PROCESS_MODEL_MAP)
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(d.main(["--mode", "mock", "--out-dir", td]), 0)
        self.assertEqual(before, r.PROCESS_MODEL_MAP)
        src = open(d.__file__, encoding="utf-8").read()
        self.assertNotIn("er006_model_routing", src.replace("er006_model_routing_contract_01.py", ""))

    def test_mock_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(d.main(["--mode", "mock", "--out-dir", td]), 0)
            for w in d.WORK_ORDER:
                for f in ("seed.json", "story_en.md", "run_meta.json"):
                    self.assertTrue(os.path.exists(os.path.join(td, w, f)))
            import json
            m = json.load(open(os.path.join(td, "L13", "run_meta.json"), encoding="utf-8"))
            for k in ("requested_model", "actual_model_story", "usage", "cost_jpy", "elapsed_sec",
                      "prompt_sha256", "developer_messages", "word_count", "rights"):
                self.assertIn(k, m)
            m2 = json.load(open(os.path.join(td, "L11", "run_meta.json"), encoding="utf-8"))
            # 差分は原作由来のsha(seed_user)のみ、story developer/seed developerは同一
            self.assertEqual(m["prompt_sha256"]["seed_developer"], m2["prompt_sha256"]["seed_developer"])
            self.assertEqual(m["prompt_sha256"]["story_developer"], m2["prompt_sha256"]["story_developer"])
            self.assertEqual(m["prompt_sha256"]["story_user"], m2["prompt_sha256"]["story_user"])  # mock seed同一

    def test_budget_guard_and_actual_model_check(self):
        pr = d.load_prices("gpt-6-luna")
        with tempfile.TemporaryDirectory() as td:
            budget = {"spent_jpy": 0.0, "approved_jpy": 0.0001}
            r = d.Runner("real", "gpt-6-luna", FakeClient("gpt-6-luna"))
            with self.assertRaises(RuntimeError) as c:
                d.run_work("L13", r, "raw", td, pr, budget, None)
            self.assertIn("budget_guard", str(c.exception))
            budget = {"spent_jpy": 0.0, "approved_jpy": 5.0}
            m = d.run_work("L13", r, "raw", td, pr, budget, None)
            self.assertGreater(m["cost_jpy"]["total"], 0)
            bad = d.Runner("real", "gpt-6-luna", FakeClient("gpt-5.6-luna"))
            with self.assertRaises(RuntimeError) as c:
                d.run_work("L11", bad, "raw", td, pr, {"spent_jpy": 0.0, "approved_jpy": 5.0}, None)
            self.assertIn("STOP", str(c.exception))

    def test_rights_gate(self):
        for w in d.WORK_ORDER:
            r = d.check_rights(w, d.load_source(w))
            self.assertEqual(r["gate"], "PASS")


if __name__ == "__main__":
    unittest.main()
