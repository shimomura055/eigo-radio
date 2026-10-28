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
               "X_A2_C4": plan.FAMILY_X_A2_COMMENT_4_ROLE,
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

    def test_wired_comment3_uses_z_role_and_fallback_context(self):
        """配線後(委任_02、旧unwiredピンの反転): Comment 3はZ役割文(COMMENT_2_ROLE)。fake partsはPart3が短くfallback=Part1+Part2のみ。"""
        calls = self._run_scaffold()
        self.assertTrue(calls[2].startswith(a2gen.COMMENT_2_ROLE))
        self.assertNotIn("P3 text", calls[2])
        self.assertNotIn("【これから聞く本文(後半)】", calls[2])
        self.assertIn("【すでに聞いた本文(前半)】\nP1 text.\n\nP2 text.", calls[2])

    def test_legacy_c3_role_removed_from_repo_source(self):
        """Opus R-4: 旧FAMILY_X_A2_COMMENT_3_ROLEは撤去済み。runner/planのソースが参照しない。"""
        for f in ("er019_family_x_audio_production_runner_01.py", "er019_family_x_audio_plan_01.py"):
            src = open(f, encoding="utf-8").read()
            self.assertNotIn("plan.FAMILY_X_A2_COMMENT_3_ROLE", src)
            self.assertNotIn("FAMILY_X_A2_COMMENT_3_ROLE =", src)
        self.assertFalse(hasattr(plan, "FAMILY_X_A2_COMMENT_3_ROLE"))

    def test_no_other_module_imports_new_module(self):
        """配線後: importしてよいのはX Std runner(と本test)だけ。Y/Z/X Advancedのモジュールは参照しない。"""
        for p in glob.glob("*.py"):
            if p.startswith("er019_family_x_std_comment3_z_method_01") or p == "er019_family_x_audio_production_runner_01.py":
                continue
            with self.subTest(p=p):
                self.assertNotIn("er019_family_x_std_comment3_z_method_01", open(p, encoding="utf-8", errors="ignore").read())


# ===== 委任_02: Opus M/R反映 =====
LONG_P3 = "The team also removed one tool from the first group. It was a small change. People talked about it for days."


def long_parts():
    return {"part1": "P1 text.", "part2": "P2 text.", "part3": LONG_P3 + "\n\nAfter that, the number went down by 5 percent."}


class M1R2Test(unittest.TestCase):
    def test_negative_contractions_and_modal_not_cut(self):
        for sent in ("It didn’t work.", "It wasn't clear to anyone.", "Experts say the plan will not help.",
                     "They cannot say why.", "It can’t be fixed.", "That won’t change.", "They couldn’t finish."):
            with self.subTest(sent=sent):
                self.assertTrue(c3z.RESULT_SENTENCE_RE.search(sent))
                info = c3z.build_part3_excerpt("People talked about it for many days in the town hall. " + sent)
                self.assertNotIn(sent, info["excerpt"])

    def test_r2_vocab_and_sentence_start(self):
        for sent in ("The plan failed.", "Most groups agreed.", "The vote was lost."):
            self.assertTrue(c3z.RESULT_SENTENCE_RE.search(sent), sent)
        for sent in ("So the Moon may have cooled.", "Still the work went on.", "Thus we begin.", "Therefore it matters."):
            self.assertTrue(c3z.SENTENCE_START_CONCLUSION_RE.search(sent), sent)
        self.assertFalse(c3z.SENTENCE_START_CONCLUSION_RE.search("Soon the work began."))

    def test_seven_article_fallback_count_within_limit(self):
        base = "er019_output/family_x_audio_production_wiring_01/"
        arts = ["ai_island_temple__run_form_prod_01", "coffee_prices__run_m2p0_n01_01", "moon_shrinking__run_ms_03",
                "small_bag__run_kpq_02", "uk_train_speaker_playback__run_nws_02", "tesla_spacex_merger_talks__run_nws_01",
                "paycheck_personality__run_pp_02"]
        fb = 0
        for a in arts:
            pth = base + a + "/a2/parts.json"
            if not os.path.exists(pth):
                self.skipTest("run dir missing: " + a)
            fb += c3z.build_part3_excerpt(json.load(open(pth, encoding="utf-8"))["part3"])["fallback_no_excerpt"]
        self.assertLessEqual(fb, 4)   # Opus R-2: 4/7超なら語を絞る/ユーザー進言


class R1QuestionTest(unittest.TestCase):
    def lint(self, t):
        return c3z.comment3_spoiler_lint(t, part1="a", part2="b", excerpt="", withheld_text="")

    def test_question_sentences_with_conclusion_words_pass(self):
        for t in ("では、最終的に塔作りの結果はどう変わるのでしょうか。", "結局、何が分かったのでしょうか。",
                  "これで証明できるのでしょうか？", "実験を行いました。では、結局どうなったのでしょうか"):
            with self.subTest(t=t):
                self.assertEqual(self.lint(t), [])

    def test_declarative_conclusion_words_still_blocked(self):
        for t in ("結局、AIは塔を作りました。", "結論は明らかです。", "実験で証明されました。では、どうなるでしょうか。"):
            with self.subTest(t=t):
                self.assertIn("CONCLUSION_WORD", [v["code"] for v in self.lint(t)])


class AuditM5Test(unittest.TestCase):
    def test_every_attempt_records_text_ids_hashes_and_parts_sha(self):
        n = {"i": 0}

        def f(role, ctx):
            n["i"] += 1
            return {"status": "OK", "text": BAD if n["i"] < 3 else CLEAN, "prompt": "PROMPT%d" % n["i"],
                    "attempts": [{"status": "OK", "model": "mdl", "response_id": "resp%d" % n["i"]}],
                    "j2_range_normalized": n["i"] == 1}
        parts = long_parts()
        r = c3z.run_comment3_z_method(f, parts)
        a = r["comment3_z_audit"]
        self.assertEqual(r["status"], "OK")
        self.assertEqual(len(a["attempts"]), 3)
        self.assertEqual([e["text"] for e in a["attempts"]], [BAD, BAD, CLEAN])
        self.assertEqual([e["response_id"] for e in a["attempts"]], ["resp1", "resp2", "resp3"])
        self.assertEqual(a["attempts"][0]["model"], "mdl")
        self.assertEqual(a["attempts"][0]["prompt_sha256"], sha("PROMPT1"))
        self.assertTrue(a["attempts"][0]["j2_range_normalized"])
        self.assertFalse(a["attempts"][1]["j2_range_normalized"])
        self.assertEqual(a["parts_sha256"], {k: sha(parts[k]) for k in ("part1", "part2", "part3")})
        self.assertEqual(a["method_version"], c3z.COMMENT3_Z_METHOD_VERSION)

    def test_excerpt_case_is_z_excerpt_and_excludes_result_sentence(self):
        f = FakeSupport([CLEAN])
        r = c3z.run_comment3_z_method(f, long_parts())
        self.assertEqual(r["comment3_z_audit"]["mode"], "Z_EXCERPT")
        ctx = f.calls[0][1]
        self.assertIn("【これから聞く本文(後半)】\nThe team also removed one tool", ctx)
        self.assertNotIn("went down", ctx)
        self.assertEqual(len(f.calls), 1)

    def test_overlap_note_non_blocking(self):
        n = c3z.compute_c2_c3_overlap_notes("塔を作るAIの数が変わりました。", "塔を作るAIの数を調べます。")
        self.assertGreaterEqual(n["count"], 1)
        self.assertIsNone(c3z.compute_c2_c3_overlap_notes(None, "x")["count"])


class MergeRegenTest(unittest.TestCase):
    PRIOR = {"preview": "p", "comment_1": "c1", "comment_2": "c2", "comment_3": "old", "comment_4": "c4"}

    def test_merge_replaces_only_comment3(self):
        new = c3z.merge_regenerated_comment3(self.PRIOR, {"status": "OK", "text": "new"})
        self.assertEqual(new["comment_3"], "new")
        for k in ("preview", "comment_1", "comment_2", "comment_4"):
            self.assertEqual(new[k], self.PRIOR[k])

    def test_merge_refuses_non_ok_and_null_other_keys(self):
        with self.assertRaises(ValueError):
            c3z.merge_regenerated_comment3(self.PRIOR, {"status": "COMMENT3_SPOILER_LINT_FAILED", "text": None})
        with self.assertRaises(ValueError):
            c3z.merge_regenerated_comment3(dict(self.PRIOR, comment_1=None), {"status": "OK", "text": "n"})


def _fake_client(texts, calls):
    class R:
        def __init__(s, t):
            s.output_text = t
            s.model = "m"
            s.id = "id%d" % len(calls)

    class Client:
        class responses:
            @staticmethod
            def create(**kw):
                calls.append(kw["input"][1]["content"])
                return R(texts[min(len(calls) - 1, len(texts) - 1)])
    return Client


class WiredScaffoldTest(unittest.TestCase):
    PARTS = {"title": "T", "in_one_line": "OL.", "part1": "P1 text.", "part2": "P2 text.",
             "part3": LONG_P3 + "\n\nAfter that, the number went down by 5 percent."}

    def _scaffold(self, texts):
        calls = []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(runner, "_a2_support_model", return_value="m"), \
                contextlib.redirect_stdout(io.StringIO()):
            res = runner.run_family_x_a2_scaffold(_fake_client(texts, calls), self.PARTS, d)
            files = {"texts": os.path.exists(f"{d}/a2_support_texts.json"), "audit": os.path.exists(f"{d}/audit/a2_support_generation.json")}
            audit = json.load(open(f"{d}/audit/a2_support_generation.json", encoding="utf-8"))
        return res, calls, files, audit

    def test_normal_run_has_five_llm_calls_and_excerpt_in_c3(self):
        res, calls, files, audit = self._scaffold(["テスト文です。"])
        self.assertEqual(len(calls), 5)
        self.assertTrue(calls[2].startswith(a2gen.COMMENT_2_ROLE))
        self.assertIn("【これから聞く本文(後半)】\nThe team also removed one tool", calls[2])
        self.assertNotIn("went down", calls[2])
        self.assertTrue(files["texts"])
        self.assertEqual(audit["comment_3"]["comment3_z_audit"]["method_version"], c3z.COMMENT3_Z_METHOD_VERSION)
        self.assertIn("c2_c3_overlap_note", audit["comment_3"]["comment3_z_audit"])

    def test_j2_applied_to_comment3(self):
        res, calls, files, audit = self._scaffold(["6〜8件です。"])
        self.assertEqual(res["comment_3"]["text"], "6から8件です。")
        self.assertTrue(res["comment_3"]["j2_range_normalized"])

    def test_comment3_failure_stops_before_c4_preview_and_writes_no_null_texts(self):
        res, calls, files, audit = self._scaffold(["結論として、塗りました。"] * 20)
        self.assertEqual(len(calls), 2 + 3)   # C1, C2, C3x3(lint) -> C4/Previewは呼ばない
        self.assertEqual(res["comment_3"]["status"], "COMMENT3_SPOILER_LINT_FAILED")
        self.assertNotIn("comment_4", res)
        self.assertFalse(files["texts"])
        self.assertTrue(files["audit"])
        self.assertEqual(len(audit["comment_3"]["comment3_z_audit"]["attempts"]), 3)
        self.assertIsNone(audit["comment_3"]["text"])
        self.assertTrue(audit["comment_3"]["rejected_text"])


class StopAndTtsGuardTest(unittest.TestCase):
    def test_theme_scaffold_marks_support_stage_failed_and_skips_kp(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = f"{d}/src", f"{d}/out"
            os.makedirs(f"{src}/a2")
            art = "# T\n\nP1 text sentence one.\n\nP2 text sentence two.\n\nP3 text sentence three.\n\n## In one line\nOL."
            open(f"{src}/a2/article.md", "w", encoding="utf-8").write(art)
            fake_support = {"comment_1": {"status": "OK", "text": "a"}, "comment_2": {"status": "OK", "text": "b"},
                            "comment_3": {"status": "COMMENT3_SPOILER_LINT_FAILED", "text": None}}
            kp = mock.Mock()
            kp.return_value.review_resume_valid.return_value = False
            kp.return_value.run_kp_with_review.side_effect = AssertionError("KPは呼ばれてはならない")
            with mock.patch.object(runner, "run_family_x_a2_scaffold", return_value=fake_support), \
                    mock.patch.object(runner, "record_scaffold_article_sha"), \
                    mock.patch.object(runner, "run_part2_candidates_x", return_value={"status": "OK", "state": "NONE", "pending": None}), \
                    mock.patch.object(runner, "_kpw", kp), contextlib.redirect_stdout(io.StringIO()):
                res = runner.run_theme_scaffold(object(), src, out, ["a2"])
            self.assertIn("SUPPORT_STAGE_FAILED", res["a2"]["support_stage_status"])
            self.assertTrue(os.path.exists(f"{out}/a2/{runner.SUPPORT_STAGE_FAILED_MARKER}"))
            self.assertEqual(res["a2"]["comment3_method"], c3z.COMMENT3_Z_METHOD_VERSION)

    def test_main_exits_rc3_on_support_stage_status(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        i = src.index('_sup_fail = {lv')
        self.assertIn("sys.exit(3)", src[i:i + 1400])
        self.assertIn('support_stage_status', src[i:i + 400])

    def test_tts_entry_rejects_null_support_before_paid_tts(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        i = src.index('support = load_json(f"{out_dir}/a2_support_texts.json")')
        j = src.index("shared_narration_raw_a2 =", i)
        seg = src[i:j]
        self.assertIn("_bad_support", seg)
        self.assertIn("SUPPORT_STAGE_FAILED_MARKER", seg)
        self.assertIn("raise RuntimeError", seg)


class RegenerateSupportTest(unittest.TestCase):
    def _setup(self, d):
        src, out = f"{d}/src", f"{d}/out"
        os.makedirs(f"{src}/a2")
        os.makedirs(f"{out}/a2/audit")
        art = "# T\n\nP1 text sentence one.\n\nP2 text sentence two.\n\n" + LONG_P3 + " After that, the number went down by 5 percent.\n\n## In one line\nOL."
        open(f"{src}/a2/article.md", "w", encoding="utf-8").write(art)
        prior = {"preview": "pv", "comment_1": "c1", "comment_2": "c2old", "comment_3": "old3", "comment_4": "c4"}
        json.dump(prior, open(f"{out}/a2/a2_support_texts.json", "w", encoding="utf-8"), ensure_ascii=False)
        audit0 = {"preview": {"status": "OK", "text": "pv"}, "comment_1": {"status": "OK"}, "comment_2": {"status": "OK"},
                  "comment_3": {"status": "OK", "text": "old3"}, "comment_4": {"status": "OK"}}
        json.dump(audit0, open(f"{out}/a2/audit/a2_support_generation.json", "w", encoding="utf-8"))
        return src, out, prior, audit0

    def test_regenerates_only_comment3_and_merges_audit(self):
        with tempfile.TemporaryDirectory() as d:
            src, out, prior, audit0 = self._setup(d)
            calls = []
            with mock.patch.object(runner, "_a2_support_model", return_value="m"), contextlib.redirect_stdout(io.StringIO()):
                r = runner.run_regenerate_support_comment3(_fake_client(["塔を作る話です。では、どうなるのでしょうか。"], calls), src, out)
            self.assertEqual(r["status"], "OK")
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0].startswith(a2gen.COMMENT_2_ROLE))
            self.assertIn("【これから聞く本文(後半)】\nThe team also removed one tool", calls[0])
            self.assertNotIn("went down", calls[0])
            new = json.load(open(f"{out}/a2/a2_support_texts.json", encoding="utf-8"))
            self.assertNotEqual(new["comment_3"], "old3")
            for k in ("preview", "comment_1", "comment_2", "comment_4"):
                self.assertEqual(sha(new[k]), sha(prior[k]))
            aud = json.load(open(f"{out}/a2/audit/a2_support_generation.json", encoding="utf-8"))
            for k in ("preview", "comment_1", "comment_2", "comment_4"):
                self.assertEqual(aud[k], audit0[k])   # 元のauditを保持
            self.assertEqual(aud["comment_3_history"], [audit0["comment_3"]])
            self.assertEqual(aud["comment_3"]["comment3_z_audit"]["regenerated_by"], "--regenerate-support comment_3")
            self.assertTrue(os.path.exists(f"{out}/a2/a2_support_texts.before_c3_regen.json"))
            # KP / study_text / parts は触らない
            self.assertEqual(sorted(os.listdir(f"{out}/a2")), ["a2_support_texts.before_c3_regen.json", "a2_support_texts.json", "audit"])

    def test_failure_leaves_texts_unchanged_and_sets_marker(self):
        with tempfile.TemporaryDirectory() as d:
            src, out, prior, audit0 = self._setup(d)
            calls = []
            with mock.patch.object(runner, "_a2_support_model", return_value="m"), contextlib.redirect_stdout(io.StringIO()):
                r = runner.run_regenerate_support_comment3(_fake_client(["結論として、塗りました。"], calls), src, out)
            self.assertEqual(r["status"], "COMMENT3_SPOILER_LINT_FAILED")
            self.assertEqual(json.load(open(f"{out}/a2/a2_support_texts.json", encoding="utf-8")), prior)
            self.assertEqual(json.load(open(f"{out}/a2/audit/a2_support_generation.json", encoding="utf-8")), audit0)
            self.assertTrue(os.path.exists(f"{out}/a2/{runner.SUPPORT_STAGE_FAILED_MARKER}"))

    def test_first_path_and_regen_path_share_one_helper(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertEqual(src.count("_a2_comment3_z(client"), 3)   # def + scaffold + regenerate
        self.assertEqual(src.count("c3z.run_comment3_z_method("), 1)   # 呼出はhelper内の1か所のみ


if __name__ == "__main__":
    unittest.main()
