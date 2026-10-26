# -*- coding: utf-8 -*-
"""FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_01: Family Y Advanced Comment 2削除(ユーザー正式承認 2026-10-26)の回帰test(API 0・network遮断)。

固定するもの: Advancedはsupport 3種(preview/comment_1/comment_3)でComment 2を生成せず、検査・TTS・組立・ページ・resumeでも参照しない。
Standard(a2、日本語側)は現状維持(4種、role文・Preview roleとも無変更)。X共有のPREVIEW_ROLE自体は無変更(Y側で派生)。
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402
import er121_family_y_runner_01_test_01 as rt  # noqa: E402  (mock ctx helperを再利用)


def setUpModule():
    rt.setUpModule()


def tearDownModule():
    rt.tearDownModule()
    assert rt.BLOCK["net"] == 0 and rt.BLOCK["client"] == 0


class Structure(unittest.TestCase):
    def test_support_names_per_level(self):
        self.assertEqual(ys.support_names("b1b"), ("preview", "comment_1", "comment_3"))
        self.assertEqual(ys.support_names("a2"), ("preview", "comment_1", "comment_2", "comment_3"))
        self.assertEqual(ys.body_comment_names("b1b"), ("comment_1", "comment_3"))
        self.assertEqual(ys.body_comment_names("a2"), ("comment_1", "comment_2", "comment_3"))
        self.assertEqual(ys.Y_REMOVED_SUPPORT_NAMES, {"b1b": ("comment_2",), "a2": ()})
        with self.assertRaises(KeyError):
            ys.support_names("x")

    def test_comment2_role_only_for_standard(self):
        self.assertEqual(set(ys.Y_COMMENT_2_ROLE), {"a2"})
        self.assertEqual(set(ys.Y_COMMENT_3_ROLE), {"a2", "b1b"})            # Comment 3(Tension側)は両levelで維持

    def test_advanced_preview_role_drops_only_comment2_references(self):
        import er003_v1_b1_scaffold_01_generate as g
        base = g.PREVIEW_ROLE
        out = ys.advanced_preview_role(base)
        self.assertNotIn("Comment 2", out)
        self.assertNotIn("{comment_2}", out)
        self.assertIn("{comment_1}", out)
        out.format(comment_1="C1 text")                                      # comment_2無しでformatできる
        a, b = base.split("\n"), out.split("\n")
        removed = [x for x in a if x not in b]
        added = [x for x in b if x not in a]
        self.assertEqual(len(removed), 4)           # 重複回避bullet・参照文・【Comment 2】見出し・{comment_2}
        self.assertEqual(len(added), 2)
        self.assertTrue(all("Comment 1" in x for x in added))

    def test_advanced_preview_role_fails_loud_when_base_changes(self):
        with self.assertRaises(ValueError):
            ys.advanced_preview_role("Comment 1だけの別文面{comment_1}")

    def test_standard_preview_role_untouched(self):
        import er003_v1_iran01_a2_generate as g2
        self.assertIn("{comment_2}", g2.PREVIEW_ROLE)                          # Standardは共有roleをそのまま使う(Y側で派生しない)


class WriteLevelInputs(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="y_c2_")
        self.parsed = {"title": "T", "segments": {s: f"text {s}" for s in ys.Y_SEGMENT_IDS}}
        self.sup = {"preview": "P", "comment_1": "C1", "comment_2": "C2 legacy", "comment_3": "C3"}

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_advanced_ignores_legacy_comment2(self):
        """旧run(comment_2入りのsupport)をresumeしても、Advancedは書き出さず・検査せず・parts.jsonに削除注記を残す。"""
        ya.write_level_inputs(self.d, "b1b", self.parsed, self.sup)
        got = json.load(open(f"{self.d}/b1b/support_texts.json", encoding="utf-8"))
        self.assertEqual(sorted(got), ["comment_1", "comment_3", "preview"])
        parts = json.load(open(f"{self.d}/b1b/parts.json", encoding="utf-8"))
        self.assertEqual(parts["removed_by_spec"], {"comment_2": ys.COMMENT2_REMOVED_SPEC})

    def test_advanced_does_not_require_comment2(self):
        sup = {k: v for k, v in self.sup.items() if k != "comment_2"}
        ya.write_level_inputs(self.d, "b1b", self.parsed, sup)

    def test_standard_still_requires_comment2(self):
        sup = {k: v for k, v in self.sup.items() if k != "comment_2"}
        with self.assertRaises(ya.YAudioStop):
            ya.write_level_inputs(self.d, "a2", self.parsed, sup)
        ya.write_level_inputs(self.d, "a2", self.parsed, self.sup)
        got = json.load(open(f"{self.d}/a2/support_texts.json", encoding="utf-8"))
        self.assertEqual(sorted(got), ["comment_1", "comment_2", "comment_3", "preview"])
        self.assertNotIn("removed_by_spec", json.load(open(f"{self.d}/a2/parts.json", encoding="utf-8")))


class BodySeq(unittest.TestCase):
    def _seg(self, level):
        names = (*ys.Y_SEGMENT_IDS, *ys.body_comment_names(level))
        return {n: n for n in names}

    def test_advanced_order(self):
        seq = ya._body_seq(self._seg("b1b"), 0.8, 1.0, "b1b")
        parts = [p for p, _ in seq if not str(p).startswith("pause")]
        want = ["Comment 1", ys.PAGE_LABEL[ys.Y_LEAD]]
        for i in (1, 2, 3):
            want += [ys.PAGE_LABEL[f"y_intro_{i}"], ys.PAGE_LABEL[f"y_voice_{i}"]]
        want += ["Comment 3", ys.PAGE_LABEL[ys.Y_CLOSING]]
        self.assertEqual(parts, want)
        self.assertNotIn("Comment 2", parts)

    def test_standard_order_unchanged(self):
        seq = ya._body_seq(self._seg("a2"), 0.8, 1.0, "a2")
        parts = [p for p, _ in seq if not str(p).startswith("pause")]
        self.assertEqual(parts[:4], ["Comment 1", ys.PAGE_LABEL[ys.Y_LEAD], "Comment 2", ys.PAGE_LABEL["y_intro_1"]])
        self.assertEqual(parts[-3:], [ys.PAGE_LABEL["y_voice_3"], "Comment 3", ys.PAGE_LABEL[ys.Y_CLOSING]])


class SupportStageCalls(unittest.TestCase):
    """support stageのLLM call構成: Advanced=comment_1/comment_3/preview(3)、Standard=4。Advancedのroleに『Comment 2』が無い。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="y_c2s_")
        cls.rec = []

        def support_fn(client, role, block, model=None, **k):
            cls.rec.append((role, block))
            return {"status": "OK", "text": f"mock support {len(cls.rec)}", "attempts": []}
        cls.ctx = rt._ctx(cls.root, hooks={"support_fn": support_fn})
        with rt._quiet():
            r.run_stages(cls.ctx, ["seed_check", "text", "translate"])
            cls.n0 = len(cls.rec)
            r.run_stages(cls.ctx, ["support"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_call_counts_and_roles(self):
        calls = self.rec[self.n0:]
        self.assertEqual(len(calls), 3 + 4)
        adv, std = calls[:3], calls[3:]
        self.assertEqual(len([c for c in std if "Comment 2(役割" in c[0]]), 1)
        self.assertEqual(len([c for c in adv if "Comment 2" in c[0]]), 0, "Advancedのどのroleにも『Comment 2』が現れない")
        self.assertEqual(len([c for c in adv if "Comment 3(役割" in c[0]]), 1)
        self.assertEqual(len([c for c in adv if "Comment 2" in c[1]]), 0)

    def test_support_docs(self):
        a = json.load(open(f"{self.ctx.out_dir}/support/b1b_support.json", encoding="utf-8"))
        s = json.load(open(f"{self.ctx.out_dir}/support/a2_support.json", encoding="utf-8"))
        self.assertEqual(sorted(k for k in a if not k.startswith("_")), ["comment_1", "comment_3", "preview"])
        self.assertEqual(sorted(k for k in s if not k.startswith("_")), ["comment_1", "comment_2", "comment_3", "preview"])
        self.assertEqual(sorted(a["_meta"]["attempts"]), ["comment_1", "comment_3", "preview"])
        self.assertEqual(a["_meta"]["removed_by_spec"], {"comment_2": ys.COMMENT2_REMOVED_SPEC})


class NoResidualReferences(unittest.TestCase):
    def test_no_hardcoded_four_support_tuple_outside_standard_definition(self):
        """Production moduleにlevel非依存の4種tuple直書きが残っていない(comment_2はStandardの定義/分岐だけ)。"""
        needle = '("preview", "comment_1", "comment_2", "comment_3")'
        for fn in ("er121_family_y_audio_01.py", "er121_family_y_runner_01.py"):
            self.assertNotIn(needle, open(os.path.join(ROOT, fn), encoding="utf-8").read(), fn)
        sst = open(os.path.join(ROOT, "er121_family_y_structure_01.py"), encoding="utf-8").read()
        self.assertEqual(sst.count(needle), 1, "Standardのsupport_names定義1か所だけ")


if __name__ == "__main__":
    unittest.main()
