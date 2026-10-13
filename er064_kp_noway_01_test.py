# FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_01 test (JPY0、LLM呼出なし)
# 検証: (1)追加段落に評価語句・特定語・既存候補句がない(hardcode禁止) (2)P0X = P0 + 追加段落のみ(6セル) (3)Production側ファイル無変更
# (4)案BのValidator通過可否(have/had系はINVALID、no way to know系はPASS) (5)有料run安全装置 (6)計画のjob数 (7)対照のsha一致
# 使い方: PYTHONPATH=. PYTHONUTF8=1 .venv/Scripts/python.exe er064_kp_noway_01_test.py
import ast
import glob
import json
import os
import re
import subprocess
import sys
import unittest

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_prompts as PR  # noqa: E402
import er064_kp_noway_01_analyze as AN  # noqa: E402
import er064_kp_noway_01_offline as OFF  # noqa: E402
import er064_kp_noway_01_prompts as NP  # noqa: E402
import er064_kp_noway_01_run as NR  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402

R1 = "er064_output/kp_integrated_opt_01/round1"
OFFJ = json.load(open("er064_output/kp_no_way_fix_01/offline_check_01.json", encoding="utf-8"))
ANCHORS = json.load(open(f"{R1}/anchors_r1.json", encoding="utf-8"))["anchors"]


class Hardcode(unittest.TestCase):
    def test_added_paragraph_has_no_eval_or_specific_words(self):
        t = NP.ADDED_PARAGRAPH.lower()
        for w in OFF.BAN_WORDS:
            self.assertNotIn(w, t, w)
        for a in ANCHORS:
            self.assertNotIn(a["label"].lower(), t, a["label"])
            self.assertIsNone(re.search(a["full"], t), a["label"])

    def test_added_paragraph_has_no_existing_candidate_phrase(self):
        t = NP.ADDED_PARAGRAPH.lower()
        for v in json.load(open(f"{R1}/shortlists_r1.json", encoding="utf-8"))["articles"].values():
            for c in v["M2"]["candidates"]:
                if len(c["surface_form"].split()) >= 2:
                    self.assertNotIn(c["surface_form"].lower(), t, c["surface_form"])

    def test_prompts_module_code_has_no_specific_words(self):
        tree = ast.parse(open("er064_kp_noway_01_prompts.py", encoding="utf-8").read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                for w in OFF.BAN_WORDS:
                    self.assertNotIn(w, n.value.lower(), (w, n.value[:40]))

    def test_offline_json_hardcode_pass(self):
        self.assertTrue(OFFJ["hardcode_check"]["pass"])


class PromptDiff(unittest.TestCase):
    def test_p0x_is_p0_plus_one_paragraph_all_cells(self):
        for art, lv in OFF.CELLS:
            b = MC.build_pattern(f"{art}_{lv}", "M2")
            cb = R.cand_block(b["rows_text"])
            m0, mx = PR.render("P0", lv, cb), NP.render_p0x(cb)
            self.assertNotEqual(m0, mx)
            self.assertEqual(mx.replace("\n\n" + NP.ADDED_PARAGRAPH, "", 1), m0, (art, lv))
            self.assertEqual(mx.count(NP.ADDED_PARAGRAPH), 1)

    def test_anchor_paragraph_exactly_once_in_p0(self):
        self.assertEqual(NP.B1.before_static().count(NP.ANCHOR_PARAGRAPH), 1)

    def test_control_runs_reusable_by_sha(self):
        for k, v in OFFJ["prompt"]["cells"].items():
            self.assertTrue(v["control"]["msg_sha256_set_match_current_P0"], k)
            self.assertTrue(v["control"]["rows_sha256_set_match"], k)

    def test_added_paragraph_single_paragraph_and_japanese(self):
        self.assertNotIn("\n", NP.ADDED_PARAGRAPH)
        self.assertLess(len(NP.ADDED_PARAGRAPH), 300)


class ProductionUntouched(unittest.TestCase):
    def test_no_production_file_modified(self):
        r = subprocess.run(["git", "status", "--porcelain", "--", "er003_key_words_canonicalization.py", "er003_key_words_min_unit.py",
                            "er030_key_phrase_db_hybrid_selector_01.py", "er030_key_phrase_db_hybrid_source_reference_contract_01.py",
                            "er030_key_phrase_db_hybrid_core_01.py", "er011_key_phrase_set_redundancy_qa_01.py",
                            "er064_kp_int_01_prompts.py", "er064_kp_int_01_run.py", "er064_kp_int_01_machine.py", "er064_kp_opt_01_prompt_build.py"],
                           capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")


class ValidatorCaseB(unittest.TestCase):
    def _v(self, d):
        return [x for x in OFFJ["case_b_validator_check"] if x["display_phrase"] == d][0]

    def test_have_had_forms_invalid_by_existing_finite_aux_rule(self):
        for d in ("have no way to know", "had no way to know", "have no way"):
            v = self._v(d)
            self.assertEqual(v["selection_status"], "KEY_WORDS_STRUCTURE_INVALID", d)
            self.assertFalse(v["rule7_unchanged_key_phrase"]["ok"], d)

    def test_no_aux_extended_forms_pass_gate_and_rule7(self):
        for d in ("no way to know", "no way to", "no way to know whether"):
            v = self._v(d)
            self.assertEqual(v["selection_status"], "KEY_WORDS_STRUCTURE_PASS", d)
            self.assertTrue(v["rule7_unchanged_key_phrase"]["ok"], d)
            self.assertEqual(v["fake_calls"], 1)

    def test_six_words_invalid(self):
        self.assertEqual(self._v("no way to know whether they")["selection_status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_rule7_blocks_canonicalization_only_expansion(self):
        c = [x for x in OFFJ["canonicalization_rule_checks"] if x["case"].startswith("A.")][0]
        self.assertFalse(c["ok"])

    def test_offline_made_no_llm_call(self):
        self.assertEqual(OFFJ["llm_calls"], 0)


class RunnerSafety(unittest.TestCase):
    def test_plan_is_20_jobs(self):
        self.assertEqual(len(NR.all_specs()), 20)
        self.assertEqual(len(NR.all_specs(1)), 5)
        self.assertEqual(len(NR.all_specs(2)), 15)
        self.assertEqual(NR.PLAN[0], ("meta", "adv", 5))

    def test_paid_run_refused_without_authorization(self):
        env = dict(os.environ)
        env.pop("KP_NOWAY_PAID_RUN_AUTHORIZED", None)
        r = subprocess.run([sys.executable, "er064_kp_noway_01_run.py", "--mode", "run", "--budget-cap-jpy", "30", "--stage", "1"], capture_output=True, text=True, env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("未承認", (r.stdout + r.stderr))
        self.assertFalse(glob.glob("er064_output/kp_no_way_fix_01/runs/*"))
        self.assertFalse(os.path.exists("er064_output/kp_no_way_fix_01/cost_run_02.json"))

    def test_cap_above_authorization_refused(self):
        env = dict(os.environ, KP_NOWAY_PAID_RUN_AUTHORIZED="10")
        r = subprocess.run([sys.executable, "er064_kp_noway_01_run.py", "--mode", "run", "--budget-cap-jpy", "30", "--stage", "1"], capture_output=True, text=True, env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists("er064_output/kp_no_way_fix_01/cost_run_02.json"))

    def test_prep_builds_without_llm_client(self):
        import er064_kp_idiom_trial_01_select as S
        orig = S.UsageClient.__init__

        def boom(*a, **k):
            raise AssertionError("LLM client constructed in offline path")
        S.UsageClient.__init__ = boom
        try:
            ctx = NR.build_ctx_x("meta", ("adv",))
            self.assertIn(("meta", "adv", "M2P0X"), ctx)
        finally:
            S.UsageClient.__init__ = orig


class Analyzer(unittest.TestCase):
    def test_tolerant_verbatim_and_fragment_indicator(self):
        self.assertTrue(AN.tolerant_verbatim("push prices up", "Rising costs pushed prices up last year"))
        self.assertFalse(AN.literal_verbatim("push prices up", "Rising costs pushed prices up last year"))
        self.assertFalse(AN.tolerant_verbatim("have no way to tell", "users had no way to know"))

    def test_control_baseline_matches_round3_scores(self):
        b = json.load(open("er064_output/kp_no_way_fix_01/control_baseline_01.json", encoding="utf-8"))["cells"]
        self.assertAlmostEqual(b["coffee_adv"]["mean_score"], 38.0, 1)
        self.assertAlmostEqual(b["coffee_std"]["mean_score"], 33.33, 1)
        self.assertEqual(b["meta_adv"]["no_way_class"], {"bare": 2})


if __name__ == "__main__":
    unittest.main(verbosity=2)
