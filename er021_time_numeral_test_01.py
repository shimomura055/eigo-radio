"""ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02: 隣接数詞語の時刻形統一(案C、er021 `_try_clock_pair`)の固定test。API 0。
EQ=最終判定がPASS系 / NE=PASS不可 / PIN=現行挙動(pin値)を固定。Opus OPUS_REVIEW_01の追加test全件(OF-TN-01〜04, 論点2/4)を転記。
CASESは docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/test_matrix_02.py(修正前/後の実測)からも参照する。"""
from __future__ import annotations

import unittest
from unittest import mock

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er021_en_asr_semantic_equivalence_production_01 as t1
import er078_asr_unified_judge_01 as uj
import er109_xz_scope_01 as xz

PASS_STATES = ("PASS", "PASS_WITH_WARNING")

# (group, canon, asr, expect, role, note)   expect: "EQ" | "NE" | ("PIN", bool=最終PASSか)
CASES: list = []


def _add(g, c, x, e, role="FULL_STORY", note=""):
    CASES.append((g, c, x, e, role, note))


# OF-TN-02 am/pm
_add("OF-TN-02", "At 10 thirty pm", "At 10 30 pm", "EQ")
_add("OF-TN-02", "At ten thirty pm", "At 10 30 pm", "EQ")
_add("OF-TN-02", "At ten thirty pm", "At 10 30 am", "NE")
# OF-TN-01 後続のpercent/通貨
_add("OF-TN-01", "10 twenty-dollar bills", "10 $20 bills", "EQ")
_add("OF-TN-01", "2 fifteen percent", "2 15%", "EQ")
_add("OF-TN-01", "3 twenty euros", "3 €20", "EQ")
_add("OF-TN-01", "twelve fifty dollars", "$12.50", "NE")
# OF-TN-03 and
_add("OF-TN-03", "between 9 and 10 thirty", "between 9 and ten-thirty", "EQ", note="Opus原例`between nine and ten-thirty`はnine側が別件X-3(数詞run `nine and ten`のmis-parse)で不成立のため9を数字にして分離")
_add("OF-TN-03", "between 9 and 10 thirty", "between nine and ten-thirty", "EQ", note="OPEN-489修正で解消(旧PIN-。Opus原例)")
_add("OF-TN-03", "between 9 and ten thirty", "between 9 and 1030", "NE")
_add("OF-TN-03", "between nine and ten thirty", "between nine and 1030", "NE")
_add("OF-TN-03", "one hundred and ten", "110", "EQ")
_add("OF-TN-03", "and ten thirty", "and 1030", "NE")
# OPEN-489(委任_04): 数詞語runの"and"は『scale語の直後+数詞語が続く』場合だけ数の一部。それ以外は接続詞でrunを分割
_add("OPEN-489", "between 9 and 11", "between nine and eleven", "EQ", note="報告原例")
_add("OPEN-489", "between nine and eleven", "between nine and eleven", "EQ")
_add("OPEN-489", "between nine and eleven", "between 9 and 11", "EQ")
_add("OPEN-489", "between 9 and 10", "between nine and ten", "EQ", note="ten and ...: 旧は年ペア1010扱い")
_add("OPEN-489", "between 10 and 11", "between ten and eleven", "EQ", note="旧は1011の年ペア読み")
_add("OPEN-489", "between 20 and 30", "between twenty and thirty", "EQ", note="旧は2030")
_add("OPEN-489", "seven and eight children", "7 and 8 children", "EQ")
_add("OPEN-489", "two and three", "2 and 3", "EQ")
_add("OPEN-489", "between nine and eleven", "between 9 and 12", "NE")
_add("OPEN-489", "between nine and eleven", "between 8 and 11", "NE")
_add("OPEN-489", "between nine and eleven", "between nine and twelve", "NE")
_add("OPEN-489", "between 9 and 11", "between 9 and 11 and 12", "NE", note="余分な数")
_add("OPEN-489", "between nine and eleven", "between 11 and 9", "NE", note="順序入替")
_add("OPEN-489", "between ten and eleven", "between 1011 and", "NE", note="年ペア桁連結と別物")
_add("OPEN-489", "one hundred and ten", "110", "EQ", note="scale語直後のandは数の一部(維持)")
_add("OPEN-489", "two thousand and five", "2005", "EQ")
_add("OPEN-489", "one hundred and ten", "100 and 10", "NE")
_add("OPEN-489", "one hundred and ten", "1010", "NE")
_add("OPEN-489", "two hundred and fifty and sixty", "250 and 60", "EQ", note="2つ目のandは接続詞")
_add("OPEN-489", "between nine and ten thirty", "between 9 and 10:30", "EQ", note="and後の時刻形(_try_clock_pair)と干渉しない")
_add("OPEN-489", "between nine and ten thirty", "between 9 and 1030", "NE")
_add("OPEN-489", "between nine and ten-thirty", "between 9 and 10:30", "EQ")
_add("OPEN-489", "in nineteen ninety and twenty twenty", "in 1990 and 2020", "EQ", note="年号2つ+and")
_add("OPEN-489", "from 1990 to 2020", "from nineteen ninety to twenty twenty", "EQ", note="年号維持")
_add("OPEN-489", "five and a half", "5.5", ("PIN", False), note="and a half系は本件対象外(現行値固定)")
_add("OPEN-489", "ten dollars and fifty cents", "$10 and 50 cents", "EQ", note="金額")
_add("OPEN-489", "ten dollars and fifty cents", "$10 and 15 cents", "NE")
# 非Tier1 role(KP)
_add("KP", "ten thirty", "1030", "NE", "KEY_PHRASE")
_add("KP", "ten thirty", "10:30", "EQ", "KEY_PHRASE")
_add("KP", "ten thirty", "10 30", "EQ", "KEY_PHRASE")
# 年号
_add("YEAR", "in 1215", "in twelve fifteen", "NE", note="PIN(開示): 年号の語形<->桁連結は不一致側。本文経路では修正前から同じ向き")
_add("YEAR", "in 2010", "in twenty ten", "EQ")
_add("YEAR", "in 1066", "in ten sixty six", "EQ")
_add("YEAR", "in 1905", "in nineteen oh five", ("PIN", False))
# 名詞後続
_add("NOUN", "the 10 thirty bus", "the 10:30 bus", "EQ")
_add("NOUN", "the eleven fifteen train", "the 11:15 train", "EQ")
# 複数時刻
_add("MULTI", "from 9 fifteen to 10 thirty", "from 9:15 to 10:30", "EQ")
_add("MULTI", "at 9 fifteen, 10 thirty", "at 9:15, 10:30", "EQ")
# 基本
_add("BASIC", "ten thirty-five", "10:35", "EQ")
_add("BASIC", "ten-thirty a.m.", "10:30 a.m.", "EQ")
_add("BASIC", "one fifteen", "1:15", "EQ")
_add("BASIC", "one fifteen", "fifteen", ("PIN", False))
_add("BASIC", "ten oh five", "10:05", ("PIN", False))
_add("BASIC", "ten o'clock", "10 o'clock", "EQ")
# 実対(c8): 出所=『二十年後』(FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01)c8のslot/attempt。2表記とも
_add("C8", "At 10 thirty", "At ten-thirty", "EQ", note="ROOT_CAUSE_01記載の実対")
_add("C8", "At ten thirty", "At 10:30", "EQ", note="PRODUCTION_PLAN_01記載の実対")
# 異常系(代表)
_add("NEG", "At ten thirty", "At 1030", "NE")
_add("NEG", "At 1030", "At ten thirty", "NE")
_add("NEG", "At ten thirty five", "At 1035", "NE")
_add("NEG", "At ten thirty", "At 10:13", "NE")
_add("NEG", "At ten thirty", "At 11:30", "NE")
_add("NEG", "Chapter eleven fifty is long", "Chapter 1150 is long", "NE")
_add("NEG", "Magna Carta in twelve fifteen", "Magna Carta in 1215", "NE")
# F-1(別commit=委任_02 H): thirty 5 を合成数35として読む修正後はEQ(修正前は分類層が30 5と読んでPIN=NG。TEST_MATRIX_02は修正前のPINで記録)
_add("F-1", "At 10 thirty 5", "At 10:35", "EQ", note="F-1修正後(commit 2)でEQ")
_add("F-1", "At 12 forty 5", "At 12:45", "EQ", note="F-1修正後でEQ")


def judge_primary(canon: str, asr: str, role: str = "FULL_STORY"):
    """正式経路の純関数でPrimary 1本の最終判定を再現(adapterと同じ組立。Secondaryは呼べない)。telemetry自動追記はno-op化。"""
    with mock.patch.object(t1, "append_telemetry_log", lambda *a, **k: None):
        cls = val.classify_asr_match(canon, asr, role=role)
        primary = {"passed": bool(cls.should_pass), "text": asr, "label": cls.classification,
                   "equivalence_basis": sec._equivalence_basis_of(cls) if cls.should_pass else None}
        ctx = uj.AttemptCtx(canonical_text=canon, wav_sha256="sim", audio_seconds=10.0)
        r = uj.unified_judge(ctx, primary, lambda c: uj.SecondaryOutcome(None, error="sim_no_secondary"), lang="en", role=role)
    return r.state, r.reason_code, cls


def final_pass(canon, asr, role="FULL_STORY") -> bool:
    return judge_primary(canon, asr, role)[0] in PASS_STATES


class TimeNumeralCases(unittest.TestCase):
    def test_cases(self):
        for g, c, x, e, role, note in CASES:
            with self.subTest(group=g, canon=c, asr=x):
                got = final_pass(c, x, role)
                if e == "EQ":
                    self.assertTrue(got, f"{c!r}||{x!r} should PASS")
                elif e == "NE":
                    self.assertFalse(got, f"{c!r}||{x!r} must NOT pass")
                else:
                    self.assertEqual(got, e[1], f"PIN {c!r}||{x!r}")


class XZScopeEr109(unittest.TestCase):
    """OF-TN-04: X/Z scope ON(er109同音救済を含む正式経路)でも桁連結/年号形の誤PASSは生じない。#66は承認規則(PIN)。"""
    NE = [("At ten thirty", "At 1030"), ("At 1030", "At ten thirty"), ("At ten thirty five", "At 1035"),
          ("Chapter eleven fifty is long", "Chapter 1150 is long"), ("Magna Carta in twelve fifteen", "Magna Carta in 1215")]

    def test_ne_and_pin_in_scope(self):
        for fam in ("X", "Z"):
            with xz.run_scope(fam):
                self.assertTrue(xz.is_active_for_run())
                for c, x in self.NE:
                    with self.subTest(fam=fam, canon=c, asr=x):
                        self.assertFalse(final_pass(c, x), f"{c!r}||{x!r} must stay NG under scope {fam}")
                with self.subTest(fam=fam, pin="#66"):
                    self.assertTrue(final_pass("At 1030", "At 10:30"))  # er109承認規則(CURRENT_SPEC.md:2970): 数字1030<->10:30
                    self.assertIsNotNone(xz.decision("At 1030", "At 10:30"))


class SecondaryPaths(unittest.TestCase):
    def _judge(self, canon, primary_text, secondary_text):
        with mock.patch.object(t1, "append_telemetry_log", lambda *a, **k: None):
            cls = val.classify_asr_match(canon, primary_text, role="FULL_STORY")
            primary = {"passed": bool(cls.should_pass), "text": primary_text, "label": cls.classification,
                       "equivalence_basis": sec._equivalence_basis_of(cls) if cls.should_pass else None}
            ctx = uj.AttemptCtx(canonical_text=canon, wav_sha256="sim", audio_seconds=10.0)
            calls = []

            def sfn(c):
                calls.append(1)
                return uj.SecondaryOutcome(secondary_text)
            def accept(c, stext):  # adapter(er006_secondary_asr_01._secondary_accept)の中核: 既存分類器のshould_pass
                cs = val.classify_asr_match(c, stext, role="FULL_STORY")
                return bool(cs.should_pass), cs.classification
            r = uj.unified_judge(ctx, primary, sfn, lang="en", role="FULL_STORY", secondary_accept_fn=accept)
        return r, calls

    def test_primary_time_swap_is_p1_pin(self):
        for canon in ("At 10 thirty", "At ten thirty"):
            r, calls = self._judge(canon, "At 10:13", "At 10:30")
            self.assertNotIn(r.state, PASS_STATES)
            self.assertEqual(r.state, "NG_PROTECTED")  # PIN: 時刻取り違えはP1で確定(Secondary呼出なし)
            self.assertEqual(calls, [])

    def test_secondary_digit_pair_passes_tier1(self):
        # Primary NG(他要因: 余分な語banana) -> Secondary `10 30`でTier1 PASS
        for canon in ("At 10 thirty", "At ten thirty"):
            r, calls = self._judge(canon, "At ten thirty banana", "At 10 30")
            self.assertTrue(calls, "Secondary should be called")
            self.assertIn(r.state, PASS_STATES, (canon, r.state, r.reason_code))


class CanonAtoms(unittest.TestCase):
    def test_atoms(self):
        a = t1._tier1_atoms("At ten thirty")
        b = t1._tier1_atoms("At 10 thirty")
        self.assertEqual([x for x in a if x["kind"] != "literal"], [x for x in b if x["kind"] != "literal"])
        self.assertEqual([x["value"] for x in a if x["kind"] == "number"], [10, 30])

    def test_year_pair_reading_unchanged(self):
        # 13以上の時/年号は従来の年ペア読み(1つのnumber atom)
        self.assertEqual([x["value"] for x in t1._tier1_atoms("nineteen ninety nine") if x["kind"] == "number"], [1999])
        self.assertEqual([x["value"] for x in t1._tier1_atoms("twenty twenty") if x["kind"] == "number"], [2020])

    def test_minute_range_constant(self):
        self.assertEqual((t1._CLOCK_MINUTE_MIN, t1._CLOCK_MINUTE_MAX), (10, 59))



class AndSplitOpen489(unittest.TestCase):
    """OPEN-489(委任_04): 数詞語runの`and`はscale語直後だけ数の一部。それ以外は接続詞でrunを分割する(er021 atom化 + er006 正規化)。"""

    def _nums(self, text):
        return [str(x["value"]) for x in t1._tier1_atoms(text) if x["kind"] == "number"]

    def test_er021_atoms_split_at_conjunction(self):
        self.assertEqual(self._nums("between nine and eleven"), ["9", "11"])
        self.assertEqual(self._nums("between ten and eleven"), ["10", "11"])      # 旧: 年ペア読み1011
        self.assertEqual(self._nums("between twenty and thirty"), ["20", "30"])  # 旧: 2030
        self.assertEqual(self._nums("seven and eight children"), ["7", "8"])

    def test_er021_scale_word_and_kept(self):
        self.assertEqual(self._nums("one hundred and ten"), ["110"])
        self.assertEqual(self._nums("two thousand and five"), ["2005"])
        self.assertEqual(self._nums("two hundred and fifty and sixty"), ["250", "60"])
        self.assertEqual(self._nums("in nineteen ninety and twenty twenty"), ["1990", "2020"])

    def test_er006_normalize_splits_not_drops(self):
        n = val.normalize_numeric
        self.assertEqual(n("between nine and eleven"), "between 9 and 11")
        self.assertEqual(n("between ten and twenty"), "between 10 and 20")
        self.assertEqual(n("one hundred and two"), "102")
        self.assertEqual(n("Her husband and two young brothers"), "her husband and 2 young brothers")  # 2026-10-23是正(and+数詞語)を維持


if __name__ == "__main__":
    unittest.main()
