# -*- coding: utf-8 -*-
"""er110_family_y_redelivery_revision_01 offline test(API 0)。有料run入口(cmd_gen)を --paid 付きで呼ぶtestは書かない。"""
from __future__ import annotations

import argparse
import glob
import os
import tempfile
import unittest

import er110_family_y_persona_text_trial_01 as p
import er110_family_y_redelivery_audio_01 as rr
import er110_family_y_redelivery_revision_01 as rv
import er110_family_y_text_trial_01 as y0

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "er110_family_y_redelivery_revision_01.py")


class TestIsolation(unittest.TestCase):
    def test_no_production_reference(self):
        bad = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(f)
            if b.startswith("er110_family_y_"):
                continue
            try:
                t = open(f, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "er110_family_y_redelivery_revision" in t:
                bad.append(b)
        self.assertEqual(bad, [])

    def test_no_env_flag(self):
        s = open(SRC, encoding="utf-8").read()
        self.assertNotIn("os.environ", s)
        self.assertNotIn("getenv", s)

    def test_default_off_no_paid_flag_raises_without_side_effect(self):
        before = set(glob.glob(os.path.join(ROOT, rv.REV, "**", "*"), recursive=True))
        with self.assertRaises(RuntimeError):
            rv.cmd_gen(argparse.Namespace(paid=False, stages="lead"))
        self.assertEqual(before, set(glob.glob(os.path.join(ROOT, rv.REV, "**", "*"), recursive=True)))

    def test_paid_without_approval_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                rv.require_paid(True, os.path.join(d, "none.json"))

    def test_existing_runner_default_unchanged(self):
        """従来版(委任_27)のコマンド・定数は無変更(他Familyにも触れない)。"""
        s = open(os.path.join(ROOT, "er110_family_y_redelivery_audio_01.py"), encoding="utf-8").read()
        self.assertIn('choices=("ja", "english", "scaffold", "rights", "audio")', s)
        self.assertNotIn("revision_01", s)
        self.assertIn("DISCLOSURE_JA", s)

    def test_module_restores_persona_rules(self):
        before = (p.TENSION_RULES, p.COMMON_PREMISE_JA, y0.THEME_TAG, p.build_tension_rewrite_prompt)
        with rv.patched_closing_module():
            self.assertEqual(p.TENSION_RULES, rv.CLOSING_RULES)
            self.assertEqual(y0.THEME_TAG, rv.THEME_TAG)
            rv._CURRENT_ANGLE["id"] = "B"
            pr = p.build_tension_rewrite_prompt({"voice_1": "a"}, "t", [{"fail_fields": ["leak_evidence_subject"], "reasoning": "r", "quoted_evidence": "q"}])
            self.assertIn(rv.ANGLES["B"]["name"], pr)
        self.assertEqual(before, (p.TENSION_RULES, p.COMMON_PREMISE_JA, y0.THEME_TAG, p.build_tension_rewrite_prompt))
        self.assertIsNone(rv._CURRENT_ANGLE["id"])

    def test_no_in_one_line_generation_in_revision_module(self):
        s = open(SRC, encoding="utf-8").read()
        for name in ("_advanced_in_one_line", "fx_iol", "efam"):
            self.assertNotIn(name, s)


class TestChecks(unittest.TestCase):
    GOOD_LEAD = ("荷物が届くはずの日、家にいたのに不在票が入っていた。そんな経験はないだろうか。再配達に料金を取るといっても、すべての再配達から取る案もあれば、"
                 "くり返す家だけに取る案もある。さて、誰がどんな理由で払うのだろう。ここに、立場も暮らしも違う三人の声を並べる。")

    def test_lead_ok(self):
        self.assertTrue(rv.check_lead(self.GOOD_LEAD)["ok"], rv.check_lead(self.GOOD_LEAD))

    def test_lead_rejects_old_disclosure(self):
        v = rv.check_lead(self.GOOD_LEAD + rr.DISCLOSURE_JA)["violations"]
        self.assertIn("HAS_AI_EDIT_ANNOUNCEMENT", v)

    def test_lead_rejects_short_and_no_preview(self):
        v = rv.check_lead("荷物が届く日の話だ。")["violations"]
        self.assertTrue(any(x.startswith("LENGTH") for x in v))
        self.assertIn("NO_PREVIEW_OF_THREE_VOICES", v)

    def test_intro_checks(self):
        body = "不在票を入れて帰るときは、私もやはり少し気持ちが沈む。"
        ok = rv.check_intro("最初に話すのは、毎日荷物を配って回っている、現役の宅配ドライバーだ。", "voice_1", body)
        self.assertTrue(ok["ok"], ok)
        self.assertIn("FORESHADOWS_CLAIM_WORD", rv.check_intro("最初に話すのは、宅配ドライバー。再配達は有料に反対の人。", "voice_1", body)["violations"])
        self.assertIn("ROLE_NOT_CONVEYED", rv.check_intro("最初に話すのは、ある男性。", "voice_1", body)["violations"])
        self.assertIn("HAS_FIRST_PERSON", rv.check_intro("私は宅配ドライバーだ。", "voice_1", body)["violations"])
        self.assertIn("INTRO_OBJECT_NOT_IN_OWN_VOICE:宅配ボックス", rv.check_intro("最後に話すのは、宅配ボックスで受け取る宅配ドライバーだ。", "voice_1", body)["violations"])
        self.assertIn("COPIES_VOICE_BODY_10CHARS", rv.check_intro("不在票を入れて帰るときは、やはり少し気持ちが沈む宅配ドライバー。", "voice_1", body)["violations"])

    def test_closing_rejects_obvious_conclusion_and_non_question(self):
        v = rv.check_closing("立場によって答えが分かれる。それが結論だ。")["violations"]
        self.assertIn("OBVIOUS_CONCLUSION_PHRASE", v)
        self.assertIn("NOT_ENDING_WITH_QUESTION", v)

    def test_angles_are_three_and_distinct(self):
        self.assertEqual(list(rv.ANGLES), ["A", "B", "C"])
        self.assertEqual(len({a["name"] for a in rv.ANGLES.values()}), 3)
        self.assertEqual(len({a["brief"] for a in rv.ANGLES.values()}), 3)

    def test_closing_prompt_contains_angle_and_voices_not_other_angles(self):
        r0 = rr.load_r0()
        voices = {s: r0[s] for s in rv.SLOTS}
        for aid, a in rv.ANGLES.items():
            pr = rv.build_closing_prompt(voices, aid)
            self.assertIn(a["name"], pr)
            for s in rv.SLOTS:
                self.assertIn(voices[s], pr)
            for oid, o in rv.ANGLES.items():
                if oid != aid:
                    self.assertNotIn(o["name"], pr)

    def test_lead_prompt_has_scope_and_no_disclosure_text(self):
        pr = rv.build_lead_prompt()
        self.assertIn("テーマの範囲", pr)
        self.assertNotIn(rr.DISCLOSURE_JA, pr)

    def test_intro_prompt_uses_theme_data_and_forbids_foreshadow(self):
        r0 = rr.load_r0()
        pr = rv.build_intro_prompt(rv.load_theme_sheets(), {s: r0[s] for s in rv.SLOTS})
        self.assertIn("現役の宅配ドライバー", pr)
        self.assertIn("先取りしない", pr)


class TestAssembly(unittest.TestCase):
    def setUp(self):
        self.r0 = rr.load_r0()
        self.voices = {s: self.r0[s] for s in rv.SLOTS}
        self.intros = {"voice_1": "最初に話すのは、毎日荷物を配って回る宅配ドライバー。", "voice_2": "次は、夫婦とも仕事で家を空けがちな受取人。",
                       "voice_3": "最後は、営業所やロッカーで受け取る工夫をしている受取人。"}
        self.txt = rv.render_revised(self.r0["title"], TestChecks.GOOD_LEAD, self.intros, self.voices, "不在とはなにか。誰の言葉だろう？")

    def test_five_parts_bodies_identical_no_iol_no_disclosure(self):
        c = rv.check_revised(self.txt, self.r0)
        self.assertTrue(c["ok"], c)
        d = rv.parse_revised(self.txt)
        self.assertEqual(len(d["voices"]), 3)
        self.assertNotIn(rr.DISCLOSURE_JA, self.txt)

    def test_body_change_detected(self):
        bad = self.txt.replace("不在票を入れて帰る", "不在票を入れて戻る", 1)
        self.assertIn("VOICE_BODY_CHANGED:voice_1", rv.check_revised(bad, self.r0)["violations"])

    def test_iol_detected(self):
        self.assertIn("IN_ONE_LINE_PRESENT", rv.check_revised(self.txt + "\n## In one line\nx\n", self.r0)["violations"])

    def test_mapping_ok_and_swap_detected(self):
        d = rv.parse_revised(self.txt)
        self.assertTrue(rv.mapping_check_revised({"ja": d})["ok"])
        sw = dict(d)
        sw["voices"] = [d["voices"][1], d["voices"][0], d["voices"][2]]
        self.assertFalse(rv.mapping_check_revised({"ja": sw})["ok"])

    def test_old_ja_unchanged(self):
        old = open(rv.OLD_ARTICLE, "rb").read()
        self.assertEqual(len(rv.load_old_ja()), 5)
        self.assertIn(rr.DISCLOSURE_JA.encode("utf-8"), old)

    def test_length_table_ratios(self):
        rows = rv.length_table(rv.load_old_ja(), rv.parse_revised(self.txt))
        self.assertEqual(rows[-1]["part"], "計")
        self.assertEqual(rows[0]["old"], 142)

    def test_segment_plan_levels_no_iol_narrator_from_existing(self):
        import er110_family_y_audio_trial_01 as old
        for lv in ("a2", "b1b"):
            plan = rv.revised_segment_plan(lv)
            roles = [r for r, _s, _v in plan]
            self.assertEqual(roles, ["lead", "intro_voice_1", "voice_1", "intro_voice_2", "voice_2", "intro_voice_3", "voice_3", "closing"])
            self.assertFalse(any("one_line" in r for r in roles))
            self.assertEqual(plan[1][2], old.Y_VOICE_OF["full_story_part1"])
            self.assertEqual([v for r, _s, v in plan if r.startswith("voice_")], ["Algieba", "Zephyr", "Schedar"])
        with self.assertRaises(ValueError):
            rv.revised_segment_plan("x")


if __name__ == "__main__":
    unittest.main()
