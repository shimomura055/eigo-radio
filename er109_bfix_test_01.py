# -*- coding: utf-8 -*-
"""B不具合3件の最小修正のtest(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 C)。API 0。
実行: .venv\Scripts\python.exe -m unittest er109_bfix_test_01 -v
B-1 複合序数の値ガード / B-2 1語・短文のratioゲートが承認済み同音救済より先行 / B-3 `60 %`。
方向は『不合格->合格』のみ。値が違う/内容が違う/同形異音語/弱形のみ一致/強勢差は従来どおり不合格のままであることも固定する。"""
from __future__ import annotations

import unittest

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er008_asr_variant_hardening_15_homophone_en as hp
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg


def passes(c, a, seg=None):
    cls = val.classify_asr_match(c, a, segment_id=seg)
    return bool(cls.should_pass or S._step_alternate_pass(cls)), cls


class B1CompoundOrdinal(unittest.TestCase):
    def test_compound_ordinal_equal(self):
        for s, h in [("the twenty first century", "the 21st century"), ("the sixty eighth day", "the 68th day"),
                     ("thirty second place", "32nd place"), ("the 21st century", "the twenty first century"),
                     ("twenty-first", "21st")]:
            with self.subTest(s=s, h=h):
                self.assertEqual(vg._guard_en(s, h).kind, vg.EQUAL)

    def test_value_differences_remain_diff(self):
        for s, h in [("the twenty first century", "the 22nd century"), ("sixty eighth", "68"), ("sixty eighth", "the 69th"),
                     ("twenty first", "twenty second")]:
            with self.subTest(s=s, h=h):
                self.assertEqual(vg._guard_en(s, h).kind, vg.DIFF)

    def test_final_gate_no_longer_reneges_classify_pass(self):
        c, a = "it was the twenty first century", "it was the 21st century"
        ok, cls = passes(c, a, "full_story_part1")
        self.assertTrue(ok)
        vgr, neg = uj._protected(c, a, "en")
        self.assertNotEqual(vgr.kind, vg.DIFF)
        self.assertFalse(neg)

    def test_reuses_single_function_not_reimplemented(self):
        import inspect
        src = inspect.getsource(vg._en_atom_text)
        self.assertIn("_convert_compound_ordinal_words", src)


class B3SpacedPercent(unittest.TestCase):
    def test_spaced_percent_equal(self):
        for s, h in [("60 percent", "60 %"), ("sixty percent", "60 %"), ("60 %", "60%")]:
            with self.subTest(s=s, h=h):
                self.assertEqual(vg._guard_en(s, h).kind, vg.EQUAL)

    def test_value_difference_remains_diff(self):
        self.assertEqual(vg._guard_en("60 percent", "61 %").kind, vg.DIFF)
        self.assertEqual(vg._guard_en("60 percent", "60").kind, vg.DIFF)


class B2RatioGateBeforeHomophone(unittest.TestCase):
    def test_zhe_stored_case_seize_sees_now_passes(self):
        ok, cls = passes("seize", "sees")
        self.assertTrue(ok)
        self.assertEqual(S._step_alternate_pass(cls), "HOMOPHONE_EQUIVALENT")

    def test_one_word_homophones_pass(self):
        for c, a in [("wait", "weight"), ("seize", "seas"), ("one", "won"), ("night", "knight"), ("mail", "male")]:
            with self.subTest(c=c, a=a):
                self.assertTrue(passes(c, a)[0])

    def test_phoneme_differs_stays_ng(self):
        for c, a in [("seize", "cease"), ("take part", "take tart"), ("seize", "dog"), ("increase", "decrease")]:
            with self.subTest(c=c, a=a):
                ok, cls = passes(c, a)
                self.assertFalse(ok)

    def test_p03_heteronym_and_weak_and_stress_stay_ng(self):
        # 1語KPの同形異音語/弱形のみ一致/強勢差は、新たに到達可能になる経路でも救済しない(Opus P-01〜P-03)
        for c, a in [("lead", "led"), ("desert", "dessert"), ("are", "or"), ("our", "are"), ("read", "red"), ("billow", "below"),
                     ("won", "one")]:
            with self.subTest(c=c, a=a):
                ok, cls = passes(c, a)
                self.assertFalse(ok)
                self.assertEqual(cls.classification, "TTS_FAILURE")      # 従来どおり(blind retryの対象)

    def test_negation_and_number_gates_unchanged(self):
        self.assertFalse(passes("not seize", "seize")[0])
        self.assertFalse(passes("two apples", "three apples")[0])

    def test_entity_like_is_not_bypassed(self):
        # 大文字始まり(固有名詞らしい語)は迂回対象外=従来のentity経路のまま
        cls = val.classify_asr_match("Seize", "sees")
        self.assertNotEqual(cls.classification, "HOMOPHONE_EQUIVALENT")

    def test_stopword_swap_not_bypassed(self):
        self.assertEqual(val.classify_asr_match("to", "too").classification, "TTS_FAILURE")

    def test_multi_token_unchanged(self):
        ok, cls = passes("the day was fine", "the day was fine")
        self.assertTrue(ok)

    def test_strict_pair_function(self):
        self.assertTrue(hp.strict_homophone_pair("seize", "sees"))
        self.assertFalse(hp.strict_homophone_pair("are", "or"))
        self.assertFalse(hp.strict_homophone_pair("lead", "led"))
        self.assertFalse(hp.strict_homophone_pair("billow", "below"))
        self.assertIsNone(hp.strict_homophone_pair("zzzzq", "seize"))
        self.assertTrue(hp.strict_homophone_pair("ok", "okay"))


if __name__ == "__main__":
    unittest.main()
