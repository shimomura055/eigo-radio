# -*- coding: utf-8 -*-
"""er110_family_y_redelivery_audio_01 offline test(API 0)。実行: .venv\\Scripts\\python.exe -m pytest er110_family_y_redelivery_audio_01_test_01.py
注意: 有料runの入口(main/cmd_*)を --paid 付きで呼ぶtestは書かない(過去事故FYT17の再発防止)。承認ファイル・--paid が無いとき例外で止まることだけを確認する。"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import tempfile
import unittest

import er110_family_y_redelivery_audio_01 as rd
import er110_family_y_text_trial_01 as y0

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_FILE = os.path.join(ROOT, "er110_family_y_redelivery_audio_01.py")


class TestIsolation(unittest.TestCase):
    def test_no_production_reference(self):
        """どのProduction/共有.pyも本moduleをimportしない(er110_family_y_* とそのtest以外からの参照0)。"""
        bad = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(f)
            if b.startswith("er110_family_y_"):
                continue
            try:
                t = open(f, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "er110_family_y_redelivery" in t:
                bad.append(b)
        self.assertEqual(bad, [])

    def test_no_env_flag_switch(self):
        src = open(SRC_FILE, encoding="utf-8").read()
        self.assertNotIn("os.environ", src)
        self.assertNotIn("getenv", src)

    def test_default_off_no_paid_flag_raises_before_any_side_effect(self):
        before = set(glob.glob(os.path.join(ROOT, rd.RD, "**", "*"), recursive=True))
        for fn in (rd.cmd_ja, rd.cmd_english, rd.cmd_scaffold):
            with self.assertRaises(RuntimeError):
                fn(argparse.Namespace(paid=False, s3=False))
        with self.assertRaises(RuntimeError):
            rd.cmd_audio(argparse.Namespace(paid=False, stage="tts", level="both", budget_jpy=1.0))
        after = set(glob.glob(os.path.join(ROOT, rd.RD, "**", "*"), recursive=True))
        self.assertEqual(before, after)

    def test_paid_flag_without_approval_file_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                rd.require_paid(True, os.path.join(d, "nope.json"))

    def test_read_cap_reads_given_path_not_a_baked_default(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.json")
            json.dump({"cap_jpy": 12}, open(p, "w"))
            self.assertEqual(rd.read_cap(p)["cap_jpy"], 12)
            json.dump({"cap_jpy": -1}, open(p, "w"))
            with self.assertRaises(RuntimeError):
                rd.read_cap(p)

    def test_audio_module_redirect_is_restored(self):
        import er110_family_y_audio_trial_01 as old
        before = (old.BASE, old.SRC, old.OUT_ROOT)
        with rd.audio_module_redirected() as o:
            self.assertEqual((o.SRC, o.OUT_ROOT), (rd.RD, rd.AUDIO_ROOT))
        self.assertEqual((old.BASE, old.SRC, old.OUT_ROOT), before)

    def test_persona_patch_is_restored(self):
        import er110_family_y_persona_text_trial_01 as p
        prev = (p.COMMON_PREMISE_JA, p.TENSION_RULES, y0.THEME_TAG)
        with rd.patched_persona_module():
            self.assertEqual(p.COMMON_PREMISE_JA, rd.PREMISE_JA)
            self.assertNotIn("スマホ", p.TENSION_RULES)
            self.assertEqual(y0.THEME_TAG, rd.THEME_TAG)
        self.assertEqual((p.COMMON_PREMISE_JA, p.TENSION_RULES, y0.THEME_TAG), prev)


class TestVoices(unittest.TestCase):
    def test_z_rule_matches_fixed_slots(self):
        r = rd.verify_voice_assignment()
        self.assertTrue(r["match"])
        self.assertEqual(r["z_rule_assignment"], {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"})
        self.assertEqual(r["narrator"], "Aoede")


class TestR0AndAssembly(unittest.TestCase):
    def test_r0_loaded_unchanged(self):
        r0 = rd.load_r0()
        self.assertEqual(r0["title"], rd.TITLE_JA)
        self.assertIn("不在票を入れて帰るとき", r0["voice_1"])
        self.assertIn("そう思うわたしが悪いの？", r0["voice_2"])
        self.assertIn("営業所が近くて", r0["voice_3"])

    def test_assemble_five_paragraph_contract(self):
        r0 = rd.load_r0()
        ja = rd.assemble_ja("宅配便が届くはずの日、玄関のチャイムを待ったことはあるだろうか。ここに、立場も暮らしも違う3人の声を並べる。", r0,
                            "3人とも、荷物が確実に届いてほしい。ただ、困る場所が違う。あなたは、荷物が届くはずの日、どこで待っている？")
        parsed = y0.parse_article(ja)
        self.assertEqual(len(parsed["paragraphs"]), 5)
        self.assertTrue(parsed["paragraphs"][0].endswith(rd.DISCLOSURE_JA))
        self.assertEqual(parsed["paragraphs"][1], r0["voice_1"])
        self.assertEqual(parsed["paragraphs"][3], r0["voice_3"])
        self.assertTrue(y0.check_contract(parsed)["ok"], y0.check_contract(parsed))

    def test_lead_spec_is_taken_from_y0_verbatim_and_check_lead(self):
        spec = rd.lead_spec_from_y0()
        self.assertIn("リード(語り手の声、約110字)", spec)
        self.assertIn(spec, rd.build_lead_prompt())
        ok = "宅配便が届くはずの日、玄関のチャイムを待ったことはあるだろうか。ここに、立場も暮らしも違う3人の声を並べる。".replace("3", "三")
        self.assertTrue(rd.check_lead(ok)["ok"], rd.check_lead(ok))
        self.assertFalse(rd.check_lead("私は取材した。")["ok"])
        self.assertFalse(rd.check_lead("短い。")["ok"])


class TestChecks(unittest.TestCase):
    def test_mapping_check_pass_and_detect_swap(self):
        ja = ["導入。", "私は不在票を入れて帰る。送料を見直して。", "わたしは午前に指定した。夫も働く。", "僕は営業所やロッカーで受け取る。", "まとめ。"]
        en = ["Intro.", "I leave a notice slip. Shipping should change.", "I picked a morning slot. My husband works too.", "I use a locker or the office to collect.", "Closing."]
        r = rd.mapping_check(ja, {"adv": en, "std": en})
        self.assertTrue(r["ok"], r)
        swapped = [en[0], en[2], en[1], en[3], en[4]]
        self.assertFalse(rd.mapping_check(ja, {"adv": swapped, "std": en})["ok"])
        self.assertFalse(rd.mapping_check(ja, {"adv": en[:4], "std": en})["ok"])

    def test_shingle_hits(self):
        src = {"a": "これは出典の文章でとても長い連続した一致を確認するための例文です。ほかにもあります。"}
        self.assertEqual(len(rd.shingle_hits_ja("これは出典の文章でとても長い連続した一致を確認するための例文です", src, 20)), 1)
        self.assertEqual(rd.shingle_hits_ja("まったく別の内容の文章だけがここにあります。それだけです。", src, 20), [])
        s2 = {"b": "the quick brown fox jumps over the lazy dog every single day"}
        self.assertEqual(len(rd.shingle_hits_en("Yes the quick brown fox jumps over the lazy dog.", s2, 8)), 1)
        self.assertEqual(rd.shingle_hits_en("A totally different sentence appears here for sure.", s2, 8), [])

    def test_real_r0_has_no_20char_hits_against_sources(self):
        r0 = open(os.path.join(ROOT, rd.SRC_R0, "article_ja.md"), encoding="utf-8").read()
        srcs = rd.load_sources(os.path.join(ROOT, rd.SOURCES_DIR))
        self.assertGreater(len(srcs), 100)
        self.assertEqual(rd.shingle_hits_ja(r0, srcs, 20), [])


if __name__ == "__main__":
    unittest.main()
