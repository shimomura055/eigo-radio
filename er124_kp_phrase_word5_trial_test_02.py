# -*- coding: utf-8 -*-
"""KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 のtest(API 0)。W5 Promptの条件順・DefaultOffIsolation・P7再利用の安全条件を固定する。"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er124_kp_phrase_word_trial_01 as t   # noqa: E402


class W5PromptTests(unittest.TestCase):
    def test_w3_prompt_unchanged(self):
        self.assertTrue(t.W3_SHA.startswith("7a9c47a01410bd9f"))

    def test_five_conditions_in_user_order_and_no_extra(self):
        nums = re.findall(r"^(\d+)\. \*\*(.+?)\*\*", t.W5_TEXT, flags=re.M)
        self.assertEqual([n for n, _ in nums], ["1", "2", "3", "4", "5"])
        self.assertEqual([h.split("（")[0] for _, h in nums],
                         ["本文一致", "1語", "上級者向けの学習価値", "易しい語の除外", "単語単体の学習価値"])

    def test_mandatory_vs_optional(self):
        lines = {l[0]: l for l in t.W5_TEXT.split("\n") if re.match(r"^[1-5]\. ", l)}
        self.assertIn("絶対条件", lines["1"])
        self.assertIn("絶対条件", lines["2"])
        for k in "345":
            self.assertNotIn("絶対条件", lines[k])
            self.assertNotIn("（必須）", lines[k])
        self.assertIn("ただし必須条件にはしない", lines["5"])

    def test_supplements_and_limits(self):
        for s in ("条件3・4を、条件5より必ず優先する", "不当に除外しない", "それだけを理由に一律除外しない", "新たな絶対条件にはしない",
                  "最大5つ", "最大5件", "数合わせはしない", "条件1・2(本文一致と1語)は必須"):
            self.assertIn(s, t.W5_TEXT)
        self.assertNotIn("重複の回避", t.W5_TEXT)          # W3の条件6(含有語を選ばない)は撤去
        self.assertNotIn("フレーズ側で学べるため選ばない", t.W5_TEXT)

    def test_message_keeps_phrase_input_structure(self):
        m = t.build_w3_message("The text.", ["take a detour"], t.W5_TEXT)
        self.assertTrue(m.startswith(t.W5_TEXT))
        self.assertEqual(t.parse_already(m), ["take a detour"])
        self.assertEqual(t.W5_MAX, 5)


class ReuseTests(unittest.TestCase):
    def test_replay_factory_refuses_changed_message(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "trial_result.json")
            json.dump({"state": {"p7_raw": "{}", "p7_model": "m", "messages": {"p7": {"sha256": "x", "prompt_sha256": t.P7_SHA}}}}, open(p, "w"))
            st = t.TrialState()
            f = t.make_p7_replay_factory(p, st)
            with self.assertRaises(RuntimeError):
                f("other message", "m")

    def test_replay_factory_returns_stored_raw_without_api(self):
        import hashlib
        msg = "hello"
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "trial_result.json")
            json.dump({"state": {"p7_raw": '{"items":[]}', "p7_model": "m",
                                 "messages": {"p7": {"sha256": hashlib.sha256(msg.encode()).hexdigest(), "prompt_sha256": t.P7_SHA}}}}, open(p, "w"))
            st = t.TrialState()
            raw, model, rid = t.make_p7_replay_factory(p, st)(msg, "x")()
            self.assertEqual((raw, model), ('{"items":[]}', "m"))
            self.assertTrue(rid.startswith("reused:"))

    def test_p7w5_requires_reuse_arg(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "er124_kp_phrase_word_trial_01.py"), "run-one", "--article", "monkeys_paw",
                            "--level", "a2", "--method", "p7w5"], cwd=ROOT, capture_output=True, text=True,
                           env=dict(os.environ, OPENAI_API_KEY="", PYTHONUTF8="1"))
        self.assertNotEqual(r.returncode, 0)

    def test_run_root_split(self):
        self.assertIn("WORD5-TRIAL-02", t.run_root("p7w5"))
        self.assertIn("WORD3-TRIAL-01", t.run_root("p7w3"))


class IsolationTests(unittest.TestCase):
    PROD = ["er119_kp_candidates_01.py", "er119_kp_human_review_01.py", "er119_kp_human_review_cli_01.py", "er105_kp_fulltext_selector_01.py",
            "er003_key_words_canonicalization.py", "er003_key_words_min_unit.py", "er119_kp_prompt_2v_01.py", "er119_kp_wiring_01.py",
            "er125_kp_candidate_max_01.py"]

    def test_production_does_not_reference_trial_or_w5(self):
        for f in self.PROD + ["er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
                              "er003_v1_n3_01_scaffold_generate.py"]:
            p = os.path.join(ROOT, f)
            if not os.path.exists(p):
                continue
            s = open(p, encoding="utf-8").read()
            self.assertNotIn("er124_kp_phrase_word", s, f)
            self.assertNotIn("W5_TEXT", s, f)

    def test_production_files_not_modified_vs_head(self):
        r = subprocess.run(["git", "diff", "--stat", "--"] + [f for f in self.PROD if os.path.exists(os.path.join(ROOT, f))],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")

    def test_kp_candidate_max_untouched_by_import(self):
        import er119_kp_human_review_01 as rv
        before = rv.KP_CANDIDATE_MAX
        self.assertEqual(rv.KP_CANDIDATE_MAX, before)
        self.assertEqual(before, 8)


if __name__ == "__main__":
    unittest.main()
