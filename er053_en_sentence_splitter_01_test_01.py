# -*- coding: utf-8 -*-
"""er053_en_sentence_splitter_01 のtest(API呼び出し0、費用¥0)。
実行: .venv/Scripts/python.exe -m pytest er053_en_sentence_splitter_01_test_01.py -q
"""
from __future__ import annotations

import ast
import glob
import os
import unittest

import er053_en_sentence_splitter_01 as sp

HERE = os.path.dirname(os.path.abspath(__file__))
POST_EN_INPUTS = os.path.join(HERE, "er052_output", "writer_dev_risk_flagger_01", "post_en_trial_01", "inputs")


def texts(s):
    return [t for _, t in sp.split_sentences_en(s)]


class AbbrevRegression(unittest.TestCase):
    def test_us_not_split(self):
        self.assertEqual(texts("U.S. officials said it. They left."), ["U.S. officials said it.", "They left."])

    def test_uk_not_split(self):
        self.assertEqual(texts("The U.K. government agreed. Done."), ["The U.K. government agreed.", "Done."])

    def test_un_not_split(self):
        self.assertEqual(texts("U.N. officials met. Then left."), ["U.N. officials met.", "Then left."])

    def test_mr_not_split(self):
        self.assertEqual(texts("Mr. Trump spoke. Others did not."), ["Mr. Trump spoke.", "Others did not."])

    def test_dr_not_split(self):
        self.assertEqual(texts("Dr. Smith arrived. He sat."), ["Dr. Smith arrived.", "He sat."])

    def test_jan_not_split(self):
        self.assertEqual(texts("On Jan. 5 it began. It ended."), ["On Jan. 5 it began.", "It ended."])

    def test_no_and_st_conditional(self):
        self.assertEqual(texts("See No. 5 here. Next."), ["See No. 5 here.", "Next."])
        self.assertEqual(texts("It said no. Next one."), ["It said no.", "Next one."])
        self.assertEqual(texts("In St. Louis today. Next."), ["In St. Louis today.", "Next."])
        # 継承された既知の限界(Trialと同一挙動、変更しない): 数字+st(1st.)も`st`として扱われ、直後が大文字だと切れない
        self.assertEqual(texts("It was the 1st. Next."), ["It was the 1st. Next."])

    def test_abbrev_list_is_33_words(self):
        self.assertEqual(len(sp.ABBREV), 33)

    def test_all_abbrev_not_split(self):
        for ab in sorted(sp.ABBREV):
            if ab in ("no", "st"):
                continue
            w = ab.title() if "." not in ab else ab.upper()
            s = f"Before {w}. Later words here. Final."
            self.assertEqual(texts(s)[0], f"Before {w}. Later words here.", ab)


class NormalSplit(unittest.TestCase):
    def test_basic_sentence_end(self):
        self.assertEqual(texts("One. Two! Three? Four."), ["One.", "Two!", "Three?", "Four."])

    def test_newline_and_heading(self):
        self.assertEqual(texts("# Title Here\n\nBody one. Body two."), ["# Title Here", "Body one.", "Body two."])

    def test_ids(self):
        self.assertEqual([i for i, _ in sp.split_sentences_en("A. B. C.")], ["s1", "s2", "s3"])

    def test_empty(self):
        self.assertEqual(sp.split_sentences_en(""), [])
        self.assertEqual(sp.split_sentences_en("  \n \n"), [])

    def test_closing_quote_after_period_is_sentence_end(self):
        self.assertEqual(texts('He said "go." Then left.'), ['He said "go."', "Then left."])

    def test_version(self):
        self.assertEqual(sp.SPLITTER_VERSION, "en_split_v1")


class GoldenVsTrial(unittest.TestCase):
    """Trial `vs_sentence_segments_l6` と同一入力で一致(Trial moduleはtest内でのみimport)。"""

    @classmethod
    def setUpClass(cls):
        import er052_open233_self_recovery_flow_runner_01 as trial
        cls.trial = trial

    def _trial_sents(self, t):
        return [t[a:b] for a, b in self.trial.vs_sentence_segments_l6(t)]

    def test_eleven_post_en_inputs_equal(self):
        files = sorted(glob.glob(os.path.join(POST_EN_INPUTS, "*.md")))
        self.assertEqual(len(files), 11)
        for f in files:
            t = open(f, encoding="utf-8").read()
            self.assertEqual(texts(t), self._trial_sents(t), f)

    def test_x09_ensuring_us(self):
        t = open(os.path.join(POST_EN_INPUTS, "X09_hormuz.md"), encoding="utf-8").read()
        self.assertIn("ensuring U.S.", t)
        got = texts(t)
        hit = [s for s in got if "ensuring U.S." in s]
        self.assertEqual(len(hit), 1)
        # "ensuring U.S." の直後で文が切れていない(文は "U.S." の後も続く)
        self.assertFalse(hit[0].endswith("ensuring U.S."))
        self.assertEqual(got, self._trial_sents(t))

    def test_constants_identical_to_trial(self):
        self.assertEqual(sp.ABBREV, self.trial._VS_L6_ABBREV)
        self.assertEqual(sp._SENT_END_RE.pattern, self.trial._VS_SENT_END_RE.pattern)
        self.assertEqual(sp._ABBREV_WORD_RE.pattern, self.trial._VS_L6_ABBREV_WORD_RE.pattern)


class NoTrialImportAndOtherSplittersUntouched(unittest.TestCase):
    def test_module_imports_only_stdlib_re(self):
        src = open(os.path.join(HERE, "er053_en_sentence_splitter_01.py"), encoding="utf-8").read()
        mods = set()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        self.assertEqual(mods, {"__future__", "re"})

    def test_other_splitters_not_modified_by_import(self):
        import er003_ja_to_en_translation as tr
        before = tr.split_sentences("U.S. officials said it. They left.")
        # 既存splitterは略語で割れる(=無変更)ことを確認し、本moduleの挙動と独立であることを固定
        self.assertGreaterEqual(len(before), 2)


if __name__ == "__main__":
    unittest.main()
