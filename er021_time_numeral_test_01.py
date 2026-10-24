"""ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02: 隣接数詞語の時刻形統一(案C、er021 `_try_clock_pair`)の固定test。API 0。
EQ=最終判定がPASS系 / NE=PASS不可 / PIN=現行挙動(pin値)を固定。Opus OPUS_REVIEW_01の追加test全件(OF-TN-01〜04, 論点2/4)を転記。
CASESは docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/test_matrix_02.py(修正前/後の実測)からも参照する。"""
from __future__ import annotations

import os
import tempfile
import unittest
import wave
from unittest import mock

import er006_preprod_hardening_01_validation as val
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er103_proper_noun_alarm_policy_01 as pol
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
# OPEN-487(委任_05): despaced()が数字-数字境界の空白を消さない(1:30=`1 30`と`130`を分かち書き差として一致させない)
_add("O487", "one hundred thirty people", "1:30 people", "NE")
_add("O487", "1:30 people", "one hundred thirty people", "NE")
_add("O487", "130 people", "1:30 people", "NE")
_add("O487", "one hundred thirty people", "1 30 people", "NE")
_add("O487", "10 30", "1030", "NE")
_add("O487", "3 10-minute rounds", "310 minute rounds", "NE")
_add("O487", "storymaking", "story making", "EQ", note="複合語分かち書き差は従来どおり")
_add("O487", "e mail", "email", "EQ")
_add("O487", "covid 19", "covid19", "EQ", note="文字-数字境界は不変")
_add("O487", "a wide-scale empirical study", "Widescale empirical study.", "EQ", note="冠詞除外despace")


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


_WAV = os.path.join(tempfile.gettempdir(), "er021_time_numeral_test_silence.wav")
with wave.open(_WAV, "wb") as _w:
    _w.setnchannels(1)
    _w.setsampwidth(1)
    _w.setframerate(8000)
    _w.writeframes(b"\x00" * 8000)


def adapter_state(canon: str, asr: str, scope=None) -> str:
    """正式Primary chain(er006_secondary_asr_01.evaluate_attempt_with_cascade_detail=er109救済を含む)を、Secondary=Primaryと同文のmockで駆動して最終stateを返す
    (er109_xz_scope_01_test_01.Base.adapterと同じ組立。API 0)。scope in (X, Z)でX/Z run scope内。"""
    patches = [
        mock.patch.object(sec, "_resolve_unresolved_entity_for_review", lambda span: {"pronunciation_hint": "", "confidence": "unconfirmed", "sources": []}),
        mock.patch.object(sec, "_log_human_review", lambda d: None),
        mock.patch.object(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None),
        mock.patch.object(routing, "transcribe", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Primary#2 forbidden"))),
        mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", lambda w, language="en-US", phrases=None, **kw: (asr, None)),
    ]
    for p in patches:
        p.start()
    try:
        sec.reset_secondary_cache()

        def go():
            return sec.evaluate_attempt_with_cascade_detail(canon, asr, [], _WAV, language="en-US", cascade_enabled=True,
                                                            segment_id="full_story_part1", attempt_ctx={"slot": 1, "is_last_slot": True})
        if scope in ("X", "Z"):
            with pol.run_scope(scope), xz.run_scope(scope):
                d = go()
        else:
            d = go()
    finally:
        for p in reversed(patches):
            p.stop()
    return d["asr_judgement"]["state"]


class XZScopeEr109(unittest.TestCase):
    """OF-TN-04: X/Z scope ON(er109同音救済を含む正式Primary chain)でも桁連結/年号形の誤PASSは生じない。#66(`1030`<->`10:30`)は承認済みer109規則(PIN)。
    OPEN-487(委任_05)以降、`1030`<->`10:30`は一次分類(despace偶然一致)ではNGとなり、X/Zはer109が救済、A/B/C Legacyは非救済(開示)。"""
    NE = [("At ten thirty", "At 1030"), ("At 1030", "At ten thirty"), ("At ten thirty five", "At 1035"),
          ("Chapter eleven fifty is long", "Chapter 1150 is long"), ("Magna Carta in twelve fifteen", "Magna Carta in 1215"),
          ("one hundred thirty people", "1:30 people"), ("1:30 people", "one hundred thirty people")]

    def test_ne_and_pin_in_scope(self):
        for fam in ("X", "Z"):
            for c, x in self.NE:
                with self.subTest(fam=fam, canon=c, asr=x):
                    self.assertNotIn(adapter_state(c, x, fam), PASS_STATES, f"{c!r}||{x!r} must stay NG under scope {fam}")
            with self.subTest(fam=fam, pin="#66"):
                with xz.run_scope(fam):
                    self.assertIsNotNone(xz.decision("At 1030", "At 10:30"))
                self.assertIn(adapter_state("At 1030", "At 10:30", fam), PASS_STATES)   # er109承認規則(CURRENT_SPEC.md:2970): 数字1030<->10:30
                self.assertIn(adapter_state("At 10:30", "At 1030", fam), PASS_STATES)
            with self.subTest(fam=fam, pin="digits<->H:MM"):
                # 同じer109規則(数字列<->H:MM同音)の1桁時: X/Zは従来どおり救済(承認済み規則の範囲、開示)。数詞語(one hundred thirty)<->1:30は救済されない(上のNE)
                self.assertIn(adapter_state("130 people", "1:30 people", fam), PASS_STATES)

    def test_legacy_not_rescued(self):
        # A/B/C Legacy(scope外)は非救済(OPEN-487開示): 一次分類NG、Secondaryが同文のためNG確定
        self.assertNotIn(adapter_state("At 1030", "At 10:30", None), PASS_STATES)
        self.assertNotIn(adapter_state("130 people", "1:30 people", None), PASS_STATES)


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


class Despace487(unittest.TestCase):
    """OPEN-487(委任_05): despaced()/冠詞除外despaceは数字-数字境界の空白を残す。文字を含む分かち書き差は不変。"""

    def test_despaced_keeps_digit_digit_boundary(self):
        self.assertNotEqual(val.despaced("1:30 people"), val.despaced("130 people"))
        self.assertNotEqual(val.despaced("1 30"), val.despaced("130"))
        self.assertEqual(val.despaced("web site"), val.despaced("website"))
        self.assertEqual(val.despaced("story-making"), val.despaced("storymaking"))
        self.assertEqual(val.despaced("covid 19"), val.despaced("covid19"))   # 文字-数字境界は連結のまま
        self.assertEqual(val.despaced("blitz scaling"), "blitzscaling")      # 数字を含まない語は不変

    def test_primary_classification_ng_for_time_vs_cardinal(self):
        for c, x in (("one hundred thirty people", "1:30 people"), ("130 people", "1:30 people"),
                     ("one hundred thirty people", "1 30 people"), ("10 30", "1030")):
            with self.subTest(c=c, x=x):
                self.assertFalse(val.classify_asr_match(c, x).should_pass)


if __name__ == "__main__":
    unittest.main()
