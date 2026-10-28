# -*- coding: utf-8 -*-
"""FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 委任_01 test。API 0(mock/fake clientのみ)。
(1)Comment3 Z方式の参照範囲規則・lint・retry/fallback (2)Comment1/2/4/Preview・X Adv・役割文の不変(sha固定)
(3)未配線ガード(委任_01時点では runner が新moduleを参照しない。委任_02の配線時に意図的に反転する)。"""
import contextlib
import glob
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.getcwd())
import er003_v1_iran01_a2_generate as a2gen
import er019_family_x_audio_plan_01 as plan
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_std_comment3_z_method_01 as c3z

AI_ISLAND_PARTS = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/parts.json"
TRIAL_LOG = "docs/research/FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01/after_generation_log_01.json"
BAD = "結論として、塗りました。"
CLEAN = "前半では実験をしました。では結果はどうでしょうか。"


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def ai_parts():
    return json.load(open(AI_ISLAND_PARTS, encoding="utf-8"))


class FakeSupport:
    """run_support(role, context)互換。textsを順に返す(尽きたら最後を繰り返す)。"""

    def __init__(self, texts):
        self.texts = list(texts)
        self.calls = []

    def __call__(self, role, ctx):
        self.calls.append((role, ctx))
        t = self.texts[min(len(self.calls) - 1, len(self.texts) - 1)]
        return {"status": "OK", "text": t, "prompt": "P", "attempts": []}


class RoleSameAsZTest(unittest.TestCase):
    def test_role_is_existing_constant_unmodified(self):
        self.assertIs(c3z.COMMENT3_Z_ROLE, a2gen.COMMENT_2_ROLE)
        self.assertEqual(c3z.COMMENT3_Z_ROLE_SHA256, sha(a2gen.COMMENT_2_ROLE))
        self.assertEqual(c3z.COMMENT3_Z_ROLE_SHA256, "0268c9f1deac5ce7619a6bfd7e5ea12b8d39a87c3eb915d2266703b6b86c1d22")

    def test_role_same_as_trial_after(self):
        d = json.load(open(TRIAL_LOG, encoding="utf-8"))
        c = d["comments"]["comment_3"]
        self.assertEqual(c["full_prompt"], a2gen.build_support_prompt(c3z.COMMENT3_Z_ROLE, c["context_block"]))


class ExcerptRuleTest(unittest.TestCase):
    def test_ai_island_matches_trial_scope_and_stops_before_result(self):
        i = c3z.build_part3_excerpt(ai_parts()["part3"])
        self.assertEqual(i["excerpt"], "The researchers also erased a way to “throw rocks to get more blocks” from one AI’s memory.")
        self.assertEqual(i["cut_reason"], "RESULT_SENTENCE")
        self.assertNotIn("went down", i["excerpt"])
        self.assertNotIn("Even so", i["excerpt"])
        self.assertFalse(i["fallback_no_excerpt"])

    def test_context_uses_trial_labels_and_excerpt(self):
        p = ai_parts()
        ctx = c3z.build_comment3_context_x_std(p)
        self.assertTrue(ctx.startswith("【すでに聞いた本文(前半)】\n" + p["part1"]))
        self.assertIn("【これから聞く本文(後半)】\nThe researchers also erased", ctx)
        self.assertNotIn("Even so", ctx)
        self.assertNotIn("average number of towers it could build went down", ctx)

    def test_conclusion_marker_first_sentence_falls_back_to_part12_only(self):
        p3 = "However, the estimate is rough and not a rule for every firm.\n\nA second paragraph about cups."
        i = c3z.build_part3_excerpt(p3)
        self.assertTrue(i["fallback_no_excerpt"])
        self.assertEqual(i["excerpt"], "")
        self.assertTrue(i["cut_reason"].startswith("CONCLUSION_MARKER"))
        ctx = c3z.build_comment3_context_x_std({"part1": "A", "part2": "B", "part3": p3}, i)
        self.assertNotIn("これから聞く本文", ctx)
        self.assertNotIn("cups", ctx)

    def test_result_verbs_numbers_and_comparisons_cut(self):
        base = "Researchers visited the old market near the harbor last spring."
        for bad in ("They found that sales rose sharply.", "The group had 40 stores.", "Prices were higher than before.",
                    "Sales fell by half.", "It turned out to be wrong.", "The study showed a clear pattern.",
                    "There were three of them.", "Nothing had not changed."):
            with self.subTest(bad=bad):
                i = c3z.build_part3_excerpt(base + " " + bad)
                self.assertEqual(i["excerpt"], base)
                self.assertEqual(i["cut_reason"], "RESULT_SENTENCE")

    def test_caps_paragraph_sentence_word(self):
        s = "The shop opened in the old town near the river."
        i = c3z.build_part3_excerpt(" ".join([s] * 6))
        self.assertEqual(i["passed_sentence_count"], c3z.MAX_EXCERPT_SENTENCES)
        self.assertEqual(i["cut_reason"], "MAX_SENTENCES")
        i2 = c3z.build_part3_excerpt("\n\n".join([s, s, s]))
        self.assertEqual(i2["passed_paragraph_indices"], [0, 1])
        self.assertEqual(i2["cut_reason"], "MAX_PARAGRAPHS")
        long = "The " + " ".join(["slow"] * 50) + " market opened."
        i3 = c3z.build_part3_excerpt(long + " " + long)
        self.assertEqual(i3["passed_sentence_count"], 1)
        self.assertEqual(i3["cut_reason"], "MAX_WORDS")

    def test_too_short_excerpt_falls_back(self):
        i = c3z.build_part3_excerpt("This list matters. Large bags had not disappeared.")
        self.assertTrue(i["fallback_no_excerpt"])
        self.assertEqual(i["excerpt"], "")

    def test_never_unconditional_ratio(self):
        p3 = "The team tested a small idea in the town center.\n\n" + "\n\n".join(["Sales rose by 12 percent."] * 8)
        i = c3z.build_part3_excerpt(p3)
        self.assertNotIn("rose", i["excerpt"])


class LintTest(unittest.TestCase):
    KW = dict(part1="The shop sold tea.", part2="Later it sold coffee.", excerpt="The owner tried a new menu.",
              withheld_text="Sales rose by 40 percent after the Zeppelin event.")

    def lint(self, t, **over):
        return [v["code"] for v in c3z.comment3_spoiler_lint(t, **{**self.KW, **over})]

    def test_trial_before_and_after_pass(self):
        c = json.load(open(TRIAL_LOG, encoding="utf-8"))["comments"]["comment_3"]
        p = ai_parts()
        i = c3z.build_part3_excerpt(p["part3"])
        for t in (c["text"], c["before_text"]):
            self.assertEqual(c3z.comment3_spoiler_lint(t, part1=p["part1"], part2=p["part2"], excerpt=i["excerpt"], withheld_text=i["withheld_text"]), [])

    def test_clean_japanese_passes(self):
        self.assertEqual(self.lint("前半ではお茶を売りました。では新しいメニューで何が起きるでしょうか。"), [])

    def test_withheld_number_detected(self):
        self.assertIn("WITHHELD_NUMBER", self.lint("売り上げは40%増えました。"))
        self.assertIn("WITHHELD_NUMBER", self.lint("売り上げは４０パーセント増えました。"))

    def test_visible_number_not_flagged(self):
        self.assertEqual(self.lint("40杯売れました。", part1="The shop sold 40 cups."), [])

    def test_withheld_term_conclusion_word_struct_label(self):
        self.assertIn("WITHHELD_TERM", self.lint("後半でZeppelinに注目してください。"))
        self.assertIn("CONCLUSION_WORD", self.lint(BAD))
        self.assertIn("STRUCT_LABEL", self.lint("Part 3を聞きましょう。"))

    def test_story_vocab_not_applied(self):
        self.assertEqual(self.lint("この記事ではお茶の話をします。ニュースです。"), [])


class RunTest(unittest.TestCase):
    def test_ok_first_try(self):
        f = FakeSupport([CLEAN])
        r = c3z.run_comment3_z_method(f, ai_parts())
        self.assertEqual(r["status"], "OK")
        self.assertEqual(len(f.calls), 1)
        self.assertIs(f.calls[0][0], a2gen.COMMENT_2_ROLE)
        a = r["comment3_z_audit"]
        self.assertEqual(a["mode"], "Z_EXCERPT")
        self.assertEqual(a["lint_retry_count"], 0)
        self.assertEqual(a["excerpt"]["passed_sentence_count"], 1)
        self.assertEqual(a["role_sha256"], c3z.COMMENT3_Z_ROLE_SHA256)

    def test_lint_violation_retries_once_same_context(self):
        f = FakeSupport([BAD, CLEAN])
        r = c3z.run_comment3_z_method(f, ai_parts())
        self.assertEqual(r["status"], "OK")
        self.assertEqual(len(f.calls), 2)
        self.assertEqual(f.calls[0][1], f.calls[1][1])
        self.assertEqual(r["comment3_z_audit"]["lint_retry_count"], 1)

    def test_second_violation_falls_back_to_part12_only(self):
        f = FakeSupport([BAD, BAD, CLEAN])
        r = c3z.run_comment3_z_method(f, ai_parts())
        self.assertEqual(r["status"], "OK")
        self.assertEqual(len(f.calls), 3)
        self.assertNotIn("これから聞く本文", f.calls[2][1])
        self.assertEqual(r["comment3_z_audit"]["final_context_mode"], "PART12_ONLY_LINT_FALLBACK")

    def test_all_violate_fails_closed_without_text(self):
        r = c3z.run_comment3_z_method(FakeSupport([BAD]), ai_parts())
        self.assertEqual(r["status"], "COMMENT3_SPOILER_LINT_FAILED")
        self.assertIsNone(r["text"])
        self.assertEqual(r["rejected_text"], BAD)
        self.assertEqual(len(r["comment3_z_audit"]["attempts"]), 3)

    def test_no_excerpt_case_two_calls_max_then_fail(self):
        parts = {"part1": "A.", "part2": "B.", "part3": "However, it ends here."}
        f = FakeSupport([BAD])
        r = c3z.run_comment3_z_method(f, parts)
        self.assertEqual(len(f.calls), 2)
        self.assertEqual(r["status"], "COMMENT3_SPOILER_LINT_FAILED")
        self.assertEqual(r["comment3_z_audit"]["mode"], "PART12_ONLY_NO_SAFE_EXCERPT")

    def test_technical_failure_passes_through(self):
        def f(role, ctx):
            return {"status": "TECHNICAL_GENERATION_FAILED", "text": None, "prompt": "P", "attempts": []}
        r = c3z.run_comment3_z_method(f, ai_parts())
        self.assertEqual(r["status"], "TECHNICAL_GENERATION_FAILED")


class RegressionPinsTest(unittest.TestCase):
    """Comment 1/2/4/Preview・X Adv・役割文/参照範囲/生成順が従来のまま(委任_01の変更が及ばないこと)。"""
    PINS = {
        "C1": "905dfba75ce7cbb8c4dfec5f3b41e988f06b1d445dca82bacee56ef74bab4309",
        "C2": "0268c9f1deac5ce7619a6bfd7e5ea12b8d39a87c3eb915d2266703b6b86c1d22",
        "PREVIEW": "903665be871c5c7f380e73611bc188d96cf6b7e3fb24422b9db673e7938807ae",
        "X_A2_C3_LEGACY": "e245ef6e36276a7c1df19668e52574151f9f488225407d26953f742d18ad7e16",
        "X_A2_C4": "22feebde438ad5ec70d6a3ce19e067bc0c5fa3890de3fc600b5c6477278a3663",
        "X_B1_C3": "c766e4443051797c19ad3f64e812c41d9b75d81c2f4a3451457c01b52c0b0b02",
        "X_B1_C4": "505f4e80fba94ec5fcce1f38d0199cb61bd6794c45f484c632a4833055b651b0",
        "S_C1": "f4532b5aa9141f6ce85f2c6b33f9982f5077080db45b76776bdd34721b0d2914",
        "S_C2": "4d6ee3381e96ce78e471fe6b0d4baea99b5c3f793369c3465055b1f009fa57c4",
        "S_C4": "bf2f10fb8b01982633517c9c6e0cd65f92f7b61f3a17160fb1c425d96281f285",
        "S_PREVIEW": "a84097f212c2e18fab4ec1cd67f46d0eb1ab5f5bda7e9448fb4ede8b6ca16f50"
}

    def test_role_constants_sha_pinned(self):
        cur = {"C1": a2gen.COMMENT_1_ROLE, "C2": a2gen.COMMENT_2_ROLE, "PREVIEW": a2gen.PREVIEW_ROLE,
               "X_A2_C3_LEGACY": plan.FAMILY_X_A2_COMMENT_3_ROLE, "X_A2_C4": plan.FAMILY_X_A2_COMMENT_4_ROLE,
               "X_B1_C3": plan.FAMILY_X_B1_COMMENT_3_ROLE, "X_B1_C4": plan.FAMILY_X_B1_COMMENT_4_ROLE}
        for k, v in cur.items():
            with self.subTest(k=k):
                self.assertEqual(sha(v), self.PINS[k])

    def _run_scaffold(self):
        calls = []

        class R:
            def __init__(s, t):
                s.output_text = t
                s.model = "m"
                s.id = "id"

        class Client:
            class responses:
                @staticmethod
                def create(**kw):
                    calls.append(kw["input"][1]["content"])
                    return R("テスト文です。")
        parts = {"title": "T", "in_one_line": "OL.", "part1": "P1 text.", "part2": "P2 text.", "part3": "P3 text. It rose by 5 percent."}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(runner, "_a2_support_model", return_value="m"), \
                contextlib.redirect_stdout(io.StringIO()):
            runner.run_family_x_a2_scaffold(Client, parts, d)
        return calls

    def test_scaffold_order_and_contexts_unchanged_for_c1_c2_c4_preview(self):
        calls = self._run_scaffold()
        self.assertEqual(len(calls), 5)
        self.assertTrue(calls[0].startswith(a2gen.COMMENT_1_ROLE))
        self.assertIn("【これから聞く本文(本文1、英語)】\nP1 text.", calls[0])
        self.assertTrue(calls[1].startswith(a2gen.COMMENT_2_ROLE))
        self.assertIn("【すでに聞いた本文(本文1)】\nP1 text.\n\n【これから聞く本文(本文2)】\nP2 text.", calls[1])
        self.assertTrue(calls[3].startswith(plan.FAMILY_X_A2_COMMENT_4_ROLE))
        self.assertIn("【本文1】\nP1 text.\n\n【本文2】\nP2 text.\n\n【本文3】\nP3 text. It rose by 5 percent.", calls[3])
        self.assertIn("【エピソード全文(参考、新しいFactの追加禁止)】", calls[4])
        for k, i in (("S_C1", 0), ("S_C2", 1), ("S_C4", 3), ("S_PREVIEW", 4)):
            with self.subTest(k=k):
                self.assertEqual(sha(calls[i]), self.PINS[k])

    def test_unwired_state_guard_comment3_still_legacy(self):
        """委任_01の状態ピン: runnerは新moduleを参照せず、Comment 3は従来(X役割文・Part1+Part2)。委任_02の配線時にこのtestを意図的に反転する。"""
        calls = self._run_scaffold()
        self.assertTrue(calls[2].startswith(plan.FAMILY_X_A2_COMMENT_3_ROLE))
        self.assertNotIn("P3 text", calls[2])
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertNotIn("comment3_z_method", src)
        self.assertNotIn("er019_family_x_std_comment3", src)

    def test_no_other_module_imports_new_module(self):
        for p in glob.glob("*.py"):
            if p.startswith("er019_family_x_std_comment3_z_method_01"):
                continue
            with self.subTest(p=p):
                self.assertNotIn("er019_family_x_std_comment3_z_method_01", open(p, encoding="utf-8", errors="ignore").read())


if __name__ == "__main__":
    unittest.main()
