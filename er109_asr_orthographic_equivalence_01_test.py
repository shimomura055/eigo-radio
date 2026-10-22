# -*- coding: utf-8 -*-
"""er109_asr_orthographic_equivalence_01 のtest(API 0・未配線プロトタイプ)。
実行: .venv\\Scripts\\python.exe -m unittest er109_asr_orthographic_equivalence_01_test -v
構成: (1)正例(発音同一の異表記は同値) (2)負例(発音が異なるものは同値にしない=誤同値0) (3)fail-closed(未登録/解析不能/欠落・付加)
      (4)監査出力 (5)Production隔離(DefaultOffIsolation: 既定OFF・Production既存fileから未参照・純関数=外部呼出/ファイル書込なし)。"""
from __future__ import annotations

import ast
import glob
import os
import unittest

import er109_asr_orthographic_equivalence_01 as e

ROOT = os.path.dirname(os.path.abspath(__file__))


def eq(c, a, **kw):
    return e.evaluate(c, a, **kw).equivalent


class Positives(unittest.TestCase):
    def test_user_examples(self):
        self.assertTrue(eq("one", "1"))
        self.assertTrue(eq("pump one's fist", "Pump 1's fist."))
        self.assertTrue(eq("pump 1's fist", "Pump one's fist."))      # 逆方向

    def test_numbers(self):
        for c, a in [("twelve years", "12 years"), ("third place", "3rd place"), ("the twenty first century", "the 21st century"),
                     ("in twenty twenty four", "in 2024"), ("in two thousand and five", "in 2005"), ("three point five", "3.5"),
                     ("at five thirty", "at 5:30"), ("at five o'clock", "at 5:00"), ("thirty percent", "30%"), ("30 percent", "30%"),
                     ("five dollars", "$5"), ("five dollars and fifty cents", "$5.50"), ("the nineties", "the 90s"),
                     ("minus five", "-5"), ("one thousand two hundred", "1,200"), ("two's company", "2's company"),
                     ("In one, activity", "In 1, activity")]:
            with self.subTest(c=c, a=a):
                self.assertTrue(eq(c, a))

    def test_symbols_abbreviations(self):
        for c, a in [("rock & roll", "rock and roll"), ("two plus two", "2 + 2"), ("Tom vs. Jerry", "Tom versus Jerry"),
                     ("Mr. Smith", "mister Smith"), ("OK", "okay"), ("FBI agent", "F B I agent"),
                     ("the AI model", "the A.I. model"), ("5 min.", "5 minutes")]:
            with self.subTest(c=c, a=a):
                self.assertTrue(eq(c, a))

    def test_contractions_and_homophones(self):
        for c, a in [("it's", "its"), ("they're here", "their here"), ("I'm here", "I am here"), ("I can't go", "I cannot go"),
                     ("wait here", "weight here"), ("grey sky", "gray sky"), ("he passed", "he past"), ("by us", "buy us"),
                     ("a lot of", "alot of"), ("every one of them", "everyone of them"),
                     ("well-being", "well being"), ("state-of-the-art", "state of the art"), ("e-mail", "email")]:
            with self.subTest(c=c, a=a):
                self.assertTrue(eq(c, a))


class Negatives(unittest.TestCase):
    def test_different_numbers(self):
        for c, a in [("two", "three"), ("2 apples", "3 apples"), ("ten", "100"), ("in 1990", "in 1999"), ("3.5", "35"),
                     ("$5", "5%"), ("thirteen", "thirty"), ("fifteen", "fifty"), ("the 3rd", "the 4th"), ("1,000", "1.000"),
                     ("at 5:30", "at 5:13")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))

    def test_known_ng_examples(self):
        for c, a in [("take part", "take tart"), ("take part", "take apart"), ("Melos", "Mellows"), ("a ship", "a sheep"),
                     ("three men", "tree men"), ("very good", "berry good"), ("the word", "the world"), ("increase", "decrease")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))

    def test_negation_and_omission(self):
        for c, a in [("I can't go", "I can go"), ("I don't know", "I do know"), ("is not", "is"), ("not shot on target", "shot on target"),
                     ("um, I think so", "I think so"), ("go home", "go")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))

    def test_oronym_is_outside_approved_multiword_conditions(self):
        # 音素列は同一だが、承認済み多語同音条件(PNMH-01: 1:n・単一文字token禁止等)の外 = 新規救済範囲(ユーザー判断)なので同値にしない
        self.assertFalse(eq("ice cream", "I scream"))

    def test_pronunciation_differs_but_spelling_variant(self):
        for c, a in [("he learned", "he learnt"), ("it burned", "it burnt"), ("my mum", "my mom"), ("gonna go", "going to go"),
                     ("because it works", "'cause it works"), ("I want to go", "I wanna go")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))


class OpusMustFix(unittest.TestCase):
    """委任_02: Opus必須レビュー P-01〜P-08 の是正test(誤同値になってはいけない実例=CMUで確認済み)。"""

    def test_p01_stress_is_binary_not_removed(self):
        for c, a in [("billow", "below"), ("for tea", "40"), ("the billow", "the below")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))
        self.assertTrue(eq("ok", "okay"))          # OW1/OW2は同じ『強勢あり』=同値を維持

    def test_p02_weak_form_only_match_is_not_equivalent(self):
        for c, a in [("are", "or"), ("we're here", "were here"), ("our house", "are house"), ("are you", "our you"),
                     ("I'll go", "ill go"), ("he'll go", "hell go"), ("we'll go", "well go")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))

    def test_p03_heteronym_is_not_equalized(self):
        for c, a in [("lead pipe", "led pipe"), ("a desert", "a dessert"), ("the wind", "the wined"), ("bass drum", "base drum"),
                     ("I read it", "I red it"), ("I won", "I one"), ("route", "root")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))
        # 単一読みのcanonical + 綴りの違いは従来どおり同値(seize/sees型)
        self.assertTrue(eq("seize it", "sees it"))
        self.assertFalse(eq("seize it", "cease it"))

    def test_p04_ambiguous_abbreviations_fail_closed(self):
        for c, a in [("St. Louis", "Street Louis"), ("St. Louis", "Saint Louis"), ("Dr. Lee", "drive Lee"), ("Dr. Lee", "doctor Lee"),
                     ("Mt. Fuji", "mountain Fuji"), ("# 5", "number 5"), ("# 5", "hash 5"), ("TV show", "television show"),
                     ("tv show", "television show"), ("the st. is", "the street is")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))
        self.assertTrue(eq("5 min.", "5 minutes"))   # 同じ語の活用違いだけの略語は許す
        self.assertTrue(eq("TV show", "TV show"))

    def test_p07_ordinary_words_in_numeric_span_limited(self):
        self.assertFalse(eq("for tea", "40"))
        self.assertFalse(eq("I eat 40", "I eat for tea"))
        self.assertTrue(eq("to go", "2 go"))
        self.assertTrue(eq("for sale", "4 sale"))
        self.assertTrue(eq("one hundred and five", "105"))

    def test_p08_warning_policy_and_audit_fields(self):
        r = e.evaluate("no way", "know way")
        self.assertTrue(r.equivalent)
        self.assertEqual(r.verdict, "PASS_WITH_WARNING")
        self.assertIn("negation_word_homophone", r.warnings)
        r2 = e.evaluate("thirty percent", "30%")
        self.assertEqual(r2.verdict, "PASS")        # 決定的規則=警告なし
        a = r2.audit()
        for k in ("version", "flag_enabled", "stress_mode", "verdict", "warnings"):
            self.assertIn(k, a)
        sp = a["spans"][0]
        for k in ("matched_variants", "representative_match", "heteronym_guard"):
            self.assertIn(k, sp)
        self.assertFalse(a["flag_enabled"])

    def test_p09_known_leaks_remain_ng_fail_closed(self):
        # 記録済みの未救済(C/E分類): 誤同値にはならず従来どおり不合格のまま
        for c, a in [("March 5", "March fifth"), ("$5 million", "five million dollars"), ("24/7", "twenty four seven"),
                     ("World War II", "World War 2"), ("organise it", "organize it")]:
            with self.subTest(c=c, a=a):
                self.assertFalse(eq(c, a))

    def test_single_letter_token_not_equalized(self):
        self.assertFalse(eq("a cup of tea", "a cup of T"))


class FailClosed(unittest.TestCase):
    def test_unregistered_word_is_not_equalized(self):
        r = e.evaluate("analyze data", "analyse data")      # analyse=CMU未登録
        self.assertFalse(r.equivalent)
        self.assertTrue(r.reason.startswith("incomparable"))

    def test_one_side_empty(self):
        r = e.evaluate("is not", "is")
        self.assertFalse(r.equivalent)
        self.assertTrue(r.reason.startswith("one_side_empty"))

    def test_none_and_empty(self):
        self.assertFalse(eq(None, "x"))
        self.assertFalse(eq("x", None))
        self.assertFalse(eq("", "x"))

    def test_long_digit_string_ambiguous(self):
        self.assertFalse(eq("one two three four five six", "123456"))

    def test_span_too_long(self):
        c = "one two three four five six seven eight"
        self.assertFalse(eq(c, "1 2 3 4 5 6 7 9"))


class Audit(unittest.TestCase):
    def test_audit_contains_rules_spans_and_originals(self):
        r = e.evaluate("pump one's fist", "Pump 1's fist.")
        a = r.audit()
        self.assertEqual(a["version"], e.LAYER_VERSION)
        self.assertTrue(a["equivalent"])
        self.assertIn("number_spoken_form", a["rules"])
        self.assertEqual(a["spans"][0]["canon"], ["one's"])
        self.assertEqual(a["spans"][0]["asr"], ["1's"])
        self.assertEqual(a["spans"][0]["why"], "phoneme_equal")

    def test_representative_only_is_stricter_or_equal(self):
        # 代表発音のみは any-variant の部分集合(より厳格)。弱形 to/tew は any-variant のみ同値
        self.assertTrue(eq("jump to", "jump too"))
        self.assertFalse(eq("take part", "take tart", representative_only=True))


class ProductionIsolation(unittest.TestCase):
    """未承認機能のDefaultOffIsolation: 既定OFF、Production既存fileから未参照、純関数(通信・ファイル書込なし)。"""

    def test_flag_default_off_and_single_reader(self):
        self.assertFalse(e.ORTHOGRAPHIC_EQUIVALENCE_ENABLED)
        self.assertFalse(e.is_enabled())

    def test_no_production_file_imports_er109(self):
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            base = os.path.basename(p)
            if base.startswith("er109_"):
                continue
            try:
                tree = ast.parse(open(p, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [n.name for n in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                if any(n.startswith("er109_asr_orthographic_equivalence_01") for n in names):
                    offenders.append(base)
        self.assertEqual(sorted(set(offenders)), [], f"er109をimportするProduction/他file: {offenders}")

    def test_module_has_no_network_or_file_write(self):
        src = open(os.path.join(ROOT, "er109_asr_orthographic_equivalence_01.py"), encoding="utf-8").read()
        for bad in ("import requests", "import socket", "urllib", "open(", ".write(", "subprocess", "os.system"):
            self.assertNotIn(bad, src)

    def test_validator_untouched_by_prototype(self):
        src = open(os.path.join(ROOT, "er006_preprod_hardening_01_validation.py"), encoding="utf-8").read()
        self.assertNotIn("er109", src)
        src2 = open(os.path.join(ROOT, "er104_kp_three_asr_vote_01.py"), encoding="utf-8").read()
        self.assertNotIn("er109", src2)


if __name__ == "__main__":
    unittest.main()
