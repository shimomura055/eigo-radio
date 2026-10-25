# -*- coding: utf-8 -*-
"""proto_reading_compare_02 (v2) の unit test。API 0 (socket guard)、Production file不変更。
実行: cd <repo root>; PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_reading_compare_02_test_01.py
v1 testは `proto_reading_compare_01_test_01.py` を別途そのまま実行(v1凍結の確認)。本testはv1継承部分=「Primary側はv1と判定同一」と、追加規則の検証。"""
import ast, hashlib, json, sys, unittest
sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_reading_compare_01 as P1
import proto_reading_compare_02 as P2
import er007_ja_asr_validator_01 as javal
import er078_asr_value_guard_01 as vg
import n1_pairs_01 as N1
import er066_ja_asr_orthographic_equivalence_01_cases as c1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as c2

HERE = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
V1_SHA = "8799aa60fed66e2d78eea00bb263e99ebf069db83c6fe1d3191d1d96870c1733"


def setUpModule():
    E.api0_guard_on()


def tearDownModule():
    E.api0_guard_off()


def cls_of(c, a):
    return javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)


def key(r):
    return (r.equal, r.kind, r.label, r.warnings, r.cause, r.blocked_by, r.why)


class TestFreeze(unittest.TestCase):
    def test_v1_frozen(self):
        self.assertEqual(hashlib.sha256(open(HERE + "proto_reading_compare_01.py", "rb").read()).hexdigest(), V1_SHA)

    def test_no_copy_of_production_functions(self):
        src = open(HERE + "proto_reading_compare_02.py", encoding="utf8").read()
        defs = {n.name for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}
        for f in ("_ja_value_form", "is_irregular_sig", "extract_atoms_ja", "_numeric_value_equivalence", "_scg_c2_candidate"):
            self.assertNotIn(f, defs)
        self.assertIs(P2.vg, vg)

    def test_not_imported_by_production(self):
        import glob
        for p in glob.glob("*.py"):
            if p.startswith(("er", "run_", "main")):
                t = open(p, encoding="utf8", errors="ignore").read()
                self.assertNotIn("proto_reading_compare_02", t, p)


class TestPrimaryIdenticalToV1(unittest.TestCase):
    """Primary側(side既定)はv1と全入力で同一。"""
    def test_primary_same_on_all_corpora(self):
        pairs = [(p["canon"], p["asr"]) for p in N1.all_pairs()]
        pairs += [(c, a) for c, a, *_ in c1.POSITIVE] + [(r[0], r[1]) for r in c2.POSITIVE_02]
        pairs += [(c, a) for c, a, *_ in c1.NEGATIVE] + [(r[0], r[1]) for r in c2.NEGATIVE_02]
        pairs += [("月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密", "月の死は八千九百本超。その奥に潜む岩の上着の秘密。"),
                  ("三日目", "3日目"), ("三日待った", "3日待った。")]
        self.assertGreater(len(pairs), 200)
        for c, a in pairs:
            cl = cls_of(c, a)
            self.assertEqual(key(P1.pron_value_equivalence(c, a, cls=cl)), key(P2.pron_value_equivalence(c, a, cls=cl)), (c, a))


class TestSecondaryA4aIrregular(unittest.TestCase):
    def test_n3_21_back_to_ng(self):
        c, a = "三日待った", "3日待った。"
        cl = cls_of(c, a)
        r1 = P1.pron_value_equivalence(c, a, cls=cl, ); r1s = P1.pron_value_equivalence(c, a, cls=cl)
        self.assertTrue(r1s.equal and r1s.kind == "VALUE_ONLY")               # v1: 誤PASS
        r2 = P2.pron_value_equivalence(c, a, cls=cl, side="secondary")
        self.assertFalse(r2.equal)
        self.assertEqual(r2.blocked_by, "A4a_irregular_reading")
        self.assertTrue(r2.why.startswith("a4a_irregular_reading_value:"))
        sb, a4a, a4b, _ = E.secondary_accept_kind(c, a)
        self.assertEqual((sb, a4a, a4b), (False, False, False))

    def test_irregular_family_all_blocked_on_secondary(self):
        for c, a in [("二十歳になった", "20歳になった"), ("一日待った", "1日待った"), ("二日待った", "2日待った"),
                     ("七日待った", "7日待った"), ("三日待った", "三日待った。".replace("三", "3"))]:
            cl = cls_of(c, a)
            r = P2.pron_value_equivalence(c, a, cls=cl, side="secondary")
            self.assertFalse(r.equal, (c, a, r))

    def test_regular_values_still_accepted_on_secondary(self):
        for c, a in [("8,900本あった", "8900本あった"), ("百本あった", "100本あった"), ("十一日待った", "11日待った")]:
            cl = cls_of(c, a)
            r1 = P1.pron_value_equivalence(c, a, cls=cl)
            r2 = P2.pron_value_equivalence(c, a, cls=cl, side="secondary")
            self.assertEqual(key(r1), key(r2), (c, a))
            if cl.classification == "TRUE_CONTENT_MISMATCH":
                self.assertTrue(r2.equal, (c, a, r2))

    def test_primary_irregular_value_only_unchanged(self):
        c, a = "三日待った", "3日待った。"
        r = P2.pron_value_equivalence(c, a, cls=cls_of(c, a))   # side=primary: Production既存の受理を失わない
        self.assertTrue(r.equal and r.kind == "VALUE_ONLY")
        self.assertIn(vg.WARN_IRREGULAR_READING, r.warnings)

    def test_negation_guard_still_first(self):
        r = P2.pron_value_equivalence("三日待たなかった", "3日待った", side="secondary")
        self.assertFalse(r.equal)


class TestEvalDeterministicOutputs(unittest.TestCase):
    def test_saved_diff_matches_expectation(self):
        d = json.load(open(HERE + "eval_api0_v2_01_diff.out.json", encoding="utf8"))
        self.assertEqual([x["id"] for x in d["n3"]], ["N3-21"])
        self.assertEqual(d["n3"][0]["v2"], False)
        self.assertEqual(d["summary"]["n3_incremental_false_pass_incl_a4a_v2"], [])
        self.assertEqual(d["summary"]["n1_incremental_false_pass_incl_a4_v2"], [])
        self.assertEqual(d["p4"]["v2_regressions"], 0)
        self.assertEqual(d["p3"]["lost"], [])
        self.assertEqual(d["moon"], [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
