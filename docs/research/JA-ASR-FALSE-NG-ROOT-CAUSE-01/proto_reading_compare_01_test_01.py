# -*- coding: utf-8 -*-
"""proto_reading_compare_01 (v1) の unit test。API 0 (socket guard)、Production file不変更。
実行: PYTHONUTF8=1 .venv/Scripts/python.exe -m unittest docs.research... は不可なので
      cd <repo root>; PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_reading_compare_01_test_01.py
"""
import ast, glob, os, re, sys, types, unittest
sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_01 as E
import proto_reading_compare_01 as P
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import er066_ja_asr_orthographic_equivalence_01_cases as c1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as c2

MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
HERE = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"


def setUpModule():
    E.api0_guard_on()


def tearDownModule():
    E.api0_guard_off()


def cls_of(c, a, er=None):
    return javal.classify_ja_asr_match(c, a, expected_readings=er, allow_reading_resolver=False)


class TestM7Parity(unittest.TestCase):
    def test_uses_production_functions_not_copies(self):
        with open(HERE + "proto_reading_compare_01.py", encoding="utf8") as fh:
            src = fh.read()
        defs = {n.name for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}
        for forbidden in ("_ja_value_form", "value_form", "strip_digit_commas", "_numeric_value_equivalence", "_scg_c2_candidate"):
            self.assertNotIn(forbidden, defs)
        self.assertIs(P.sec._ja_value_form, sec._ja_value_form)

    def test_value_form_none_when_no_atom_matches_production(self):
        self.assertIsNone(sec._ja_value_form("月のしわ"))

    def test_v1_is_superset_of_production_value_layer(self):
        """Productionの `_numeric_value_equivalence` が受理する対は、v1もVALUE_ONLY(同ラベル)で受理する。"""
        pairs = [(c, a) for c, a, *_ in c1.POSITIVE] + [(r[0], r[1]) for r in c2.POSITIVE_02] + \
                [(c, a) for c, a, *_ in c1.NEGATIVE] + [(r[0], r[1]) for r in c2.NEGATIVE_02]
        n_prod = 0
        for c, a in pairs:
            cl = cls_of(c, a)
            pr = E._ORIG_NUM(c, a, cl)
            if pr is None:
                continue
            n_prod += 1
            r = P.pron_value_equivalence(c, a, cls=cl)
            self.assertTrue(r.equal and r.kind == "VALUE_ONLY" and r.label == pr.classification, (c, a, r))
        self.assertGreater(n_prod, 20)

    def test_v1_only_extra_gate_difference_is_number_mismatches_nonempty(self):
        """v1 VALUE_ONLY でProductionが受理しない対は、number_mismatchesが空(桁区切り等)のものだけ。"""
        for c, a in [("売上は1,200円です", "売上は1200円です")]:
            cl = cls_of(c, a)
            self.assertIsNone(E._ORIG_NUM(c, a, cl))
            self.assertEqual(cl.protected.number_mismatches, [])
            self.assertTrue(P.pron_value_equivalence(c, a, cls=cl).equal)


class TestM1(unittest.TestCase):
    def test_c2_reverse_blocks_numeric_sentence(self):
        r = P.pron_value_equivalence("3人できょう話した", "三人で今日話した")
        self.assertFalse(r.equal)
        self.assertEqual(r.blocked_by, "C2_heterophone")

    def test_c2_forward_span_blocks(self):
        r = P.pron_value_equivalence("三人で今日話した", "3人でこんにち話した")
        self.assertFalse(r.equal, r)

    def test_a7_registered_reading_blocks(self):
        self.assertTrue(P.pron_value_equivalence("月のしわ、8,900本超", "月の詩は8900本超").equal)
        r = P.pron_value_equivalence("月のしわ、8,900本超", "月の詩は8900本超", expected_readings={"しわ": "シワ"})
        self.assertFalse(r.equal)
        self.assertEqual(r.blocked_by, "A7_reading_dictionary")

    def test_c2_applies_on_secondary_path_too(self):
        _, a4a, a4b, r = E.secondary_accept_kind("3人できょう話した", "三人で今日話した")
        self.assertFalse(a4a or a4b)


class TestM3(unittest.TestCase):
    def test_number_diff_requires_value_guard_equal(self):
        for c, a in [("三本ください", "さんほんください"), ("三人で行く", "さんにんで行く"), ("六百円です", "ろくひゃくえんです"),
                     ("二十歳になった", "にじゅっさいになった")]:
            cl = cls_of(c, a)
            r = P.pron_value_equivalence(c, a, cls=cl)
            self.assertFalse(r.equal, (c, a, r))

    def test_stub_number_mismatch_with_no_values_blocked(self):
        c, a = "月のしわ", "月の詩は"
        cl = cls_of(c, a)
        self.assertEqual(vg.value_guard(c, a, "ja").kind, vg.NO_VALUES)
        fake = types.SimpleNamespace(classification=cl.classification, similarity_ratio=cl.similarity_ratio,
                                     protected=types.SimpleNamespace(number_mismatches=[("9", "")], negation_mismatches=[],
                                                                      content_diffs=cl.protected.content_diffs))
        self.assertFalse(P.pron_value_equivalence(c, a, cls=fake).equal)
        self.assertTrue(P.pron_value_equivalence(c, a, cls=cl).equal)   # 数字差が無い場合のみNO_VALUESでも可

    def test_unknown_diff_ambiguous_blocked(self):
        for c, a in [("1,2,3個", "123個"), ("月のしわ、8,900本超", "月の詩は8800本超"), ("会議は十分で終わる", "会議は10分で終わる")]:
            self.assertFalse(P.pron_value_equivalence(c, a).equal, (c, a))

    def test_negation_blocked(self):
        self.assertFalse(P.pron_value_equivalence("彼女は来ない", "彼女は来る").equal)
        self.assertFalse(P.pron_value_equivalence("三人は行きません", "三人は行きます").equal)

    def test_p1_value_diff_still_ng_protected_for_moon_attempt1_and_3(self):
        for t in ("月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。", "月の氏は8000900本超。その奥に潜む岩の上着の秘密。"):
            n = E.primary_stage(MOON, t, True)
            self.assertEqual((n["state"], n["reason"]), ("NG_PROTECTED", "p1_value_diff"))
            self.assertFalse(n["primary_pass"])


class TestM2FinalGateAndLabels(unittest.TestCase):
    def test_new_label_not_reading_match(self):
        self.assertNotIn(P.PRON_LABEL, sec._READING_MATCH_CLASSIFICATIONS)
        self.assertNotIn(P.PRON_LABEL, uj.APPROVED_EQUIVALENCE_BASES)
        self.assertNotIn(P.PRON_LABEL, sec.SCG_PASS_CLASSIFICATIONS)

    def _judge(self, canon, text, warn=()):
        ctx = uj.AttemptCtx(canonical_text=canon, wav_sha256="nosha:test", audio_seconds=3.0, length_ok=True, max_len=400,
                            cache=uj.SecondaryCache())
        pr = uj.PrimaryResult(passed=True, text=text, label=P.PRON_LABEL, equivalence_basis=None, warning_labels=tuple(warn), signals={})
        called = []
        def sfn(_c):
            called.append(1)
            return uj.SecondaryOutcome(None, error="api0_stub")
        return uj.unified_judge(ctx, pr, sfn, lang="ja", role=None), called

    def test_final_and_gate_applied_true_and_pass_with_warning(self):
        jr, called = self._judge(MOON, "月の死は八千九百本超。その奥に潜む岩の上着の秘密。", warn=(P.W_PRON,))
        fg = jr.audit_record["final_gate"]
        self.assertTrue(fg["applied"], fg)
        self.assertEqual(jr.state, uj.PASS_WITH_WARNING)
        self.assertIn(P.W_PRON, jr.warning_labels)
        self.assertEqual(called, [])

    def test_final_gate_rejects_value_diff_even_if_layer_wrongly_passed(self):
        jr, _ = self._judge(MOON, "月の詩は8800本超。その奥に潜む岩の上着の秘密。", warn=(P.W_PRON,))
        self.assertEqual(jr.state, uj.NG_PROTECTED)
        self.assertEqual(jr.reason_code, "final_gate_value_diff")

    def test_final_gate_rejects_negation_diff(self):
        jr, _ = self._judge("彼女は来ない", "彼女は来る")
        self.assertEqual(jr.state, uj.NG_PROTECTED)


class TestR2Warnings(unittest.TestCase):
    def test_irregular_reading_warning_survives_v1_rescue(self):
        c, a = "三日間、月のしわ", "3日間、月の詩は"
        r = P.pron_value_equivalence(c, a)
        self.assertTrue(r.equal, r)
        self.assertIn(vg.WARN_IRREGULAR_READING, r.warnings)
        self.assertIn(P.W_PRON, r.warnings)

    def test_adapter_swap_moon_attempt2_passes_with_warning_labels(self):
        n = E.primary_stage(MOON, "月の死は八千九百本超。その奥に潜む岩の上着の秘密。", True)
        self.assertEqual(n["label"], P.PRON_LABEL)
        self.assertTrue(n["primary_pass"])
        self.assertIn(P.W_PRON, n["warnings"])
        b = E.primary_stage(MOON, "月の死は八千九百本超。その奥に潜む岩の上着の秘密。", False)
        self.assertFalse(b["primary_pass"])


class TestA4Split(unittest.TestCase):
    def test_a4a_value_only_vs_a4b_pron(self):
        base, a4a, a4b, _ = E.secondary_accept_kind("三人で、お店に行きます", "3人で、お店に行きます")
        self.assertEqual((base, a4a, a4b), (False, True, False))
        base, a4a, a4b, _ = E.secondary_accept_kind(MOON, "月の詩は8900本超。その奥に潜む岩の上着の秘密。")
        self.assertEqual((base, a4a, a4b), (False, False, True))
        base, a4a, a4b, _ = E.secondary_accept_kind("三人で、お店に行きます", "三人でお店に行きます")
        self.assertEqual((base, a4a, a4b), (True, False, False))


class TestIsolation(unittest.TestCase):
    def test_production_not_importing_prototype(self):
        hits = []
        for p in glob.glob("er*.py") + glob.glob("*.py"):
            try:
                with open(p, encoding="utf8") as fh:
                    txt = fh.read()
                if re.search(r"proto_reading_compare_01|pron_value_equivalence", txt):
                    hits.append(p)
            except Exception:
                pass
        self.assertEqual(hits, [])

    def test_monkeypatch_restored_and_no_network(self):
        orig = sec._numeric_value_equivalence
        E.primary_stage(MOON, "月の死は八千九百本超。その奥に潜む岩の上着の秘密。", True)
        self.assertIs(sec._numeric_value_equivalence, orig)
        self.assertIs(sec._numeric_value_equivalence, E._ORIG_NUM)


if __name__ == "__main__":
    unittest.main(verbosity=1)
