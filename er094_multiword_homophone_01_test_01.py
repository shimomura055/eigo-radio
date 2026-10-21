"""er094_multiword_homophone_01 のunit test(API 0・未配線module・ファイル出力なし)。
実行: .venv/Scripts/python.exe -m unittest er094_multiword_homophone_01_test_01 -v
文単位テストは val.protected_check のソースを「メモリ上でのみ」patch(A-2で入れる予定の2行と同一)して検証する。
Production既存ファイルは編集しない(A-1)。"""
import importlib, inspect, json, os, sys, unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er094_multiword_homophone_01 as mw
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec

CASES = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "TRIAL_CASES_01.json")
_OLD = "                    homophone_candidate = bool(result_h)\n"
_NEW = _OLD + ("                if not homophone_candidate and _MW_CAND(canon_span, asr_span, entity_like):\n"
               "                    homophone_candidate = True\n")


def _patch_val():
    src = inspect.getsource(val.protected_check)
    assert _OLD in src
    val.__dict__["_MW_CAND"] = mw.multiword_homophone_candidate
    exec(compile(src.replace(_OLD, _NEW), "<er094_patched_protected_check>", "exec"), val.__dict__)


def _unpatch_val():
    importlib.reload(val)
    importlib.reload(sec)


def judge(c, a):
    r = val.classify_asr_match(c, a)
    if r.should_pass:
        return "PASS(" + r.classification + ")"
    if sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r):
        lab = sec._step_alternate_pass(r)
        if lab:
            return "PASS(" + lab + ")"
    return "NOT_PASS(" + r.classification + ")"


v3 = mw.multiword_span_equivalent_v3


class SpanLevel(unittest.TestCase):
    def test_stress_only_difference_is_pass(self):
        self.assertTrue(v3(["byus"], ["buy", "us"]))
        self.assertTrue(v3(["byus"], ["by", "us"]))
    def test_general_words_pass(self):
        self.assertTrue(v3(["onto"], ["on", "to"]))
        self.assertTrue(v3(["already"], ["all", "ready"]))
    def test_reverse_direction_canonical_multi(self):
        self.assertTrue(v3(["all", "ready"], ["already"]))
        self.assertFalse(v3(["buy", "us"], ["byus"]))           # G5: canonical側3字未満
    def test_different_phonemes_ng(self):
        for asr in (["buy", "a"], ["buy", "us", "us"], ["buy", "us", "on"], ["buy", "us", "an"], ["bus", "s"]):
            self.assertFalse(v3(["byus"], asr), asr)
    def test_drop_or_add_ng(self):
        self.assertFalse(v3(["byus"], ["buy"]))
        self.assertFalse(v3(["byus"], ["buy", "us", "an"]))
    def test_V8_bius_ng(self):
        d = {}
        self.assertFalse(v3(["bias"], ["bi", "us"], detail=d))
        self.assertIn("V8", d["why"])
        self.assertFalse(v3(["bias"], ["bi", "us"], entity_like=True))
    def test_V8_function_word_two_letter_ok(self):               # 既知の残存: by us
        self.assertTrue(v3(["bias"], ["by", "us"]))
    def test_V8_closed_set_membership(self):
        self.assertIn("us", mw.FW2); self.assertIn("by", mw.FW2); self.assertNotIn("bi", mw.FW2)
        self.assertFalse(v3(["bias"], ["bi", "us"]))
    def test_G5_acronym_and_letter_reading(self):
        for c, a in ((["us"], ["u", "s"]), (["am"], ["a", "m"]), (["melos"], ["mellow", "s"]), (["ai"], ["a", "i"])):
            self.assertFalse(v3(c, a), (c, a))
        self.assertFalse(v3(["ai", "phone"], ["iphone"]))
    def test_oov_undecidable(self):
        self.assertFalse(v3(["byus"], ["xqzv", "us"]))
        d = {}; v3(["byus"], ["xqzv", "us"], detail=d); self.assertIn("OOV", d["why"])
    def test_number_negation_guard(self):
        self.assertFalse(v3(["byus"], ["buy", "not"]))
        self.assertFalse(v3(["two"], ["to", "o"]))
        self.assertFalse(v3(["byus"], ["buy", "2"]))
    def test_length_and_both_multi(self):
        self.assertFalse(v3(["byus"], ["b", "u", "y", "s"]))
        self.assertFalse(v3(["buy", "us"], ["by", "us"]))
    def test_one_to_one_not_handled(self):                       # 既存1:1経路は無変更(本関数は対象外)
        self.assertFalse(v3(["wait"], ["weight"]))
    def test_non_alpha_and_case(self):
        self.assertFalse(v3(["byus"], ["buy", "us2"]))
        self.assertFalse(v3(["byus"], ["Buy", "us"]))
    def test_entity_like_representative_only(self):
        self.assertTrue(v3(["today"], ["to", "day"]))
        self.assertFalse(v3(["today"], ["to", "day"], entity_like=True))
        self.assertTrue(v3(["byus"], ["buy", "us"], entity_like=True))
    def test_adjacency_only_is_structural(self):
        # 関数は渡されたspan(SequenceMatcherの隣接opcode)だけを比較する。離れた語の結合は入力として表現できない
        self.assertFalse(v3(["byus"], ["buy", "x", "us"]))        # 間に別語=連結不一致
    def test_entry_point_fail_closed_and_rollback(self):
        self.assertTrue(mw.multiword_homophone_candidate(["byus"], ["buy", "us"], False))
        self.assertFalse(mw.multiword_homophone_candidate(None, ["buy", "us"], False))   # 例外->非救済
        mw.MULTIWORD_HOMOPHONE_ENABLED = False
        try:
            self.assertFalse(mw.multiword_homophone_candidate(["byus"], ["buy", "us"], False))
        finally:
            mw.MULTIWORD_HOMOPHONE_ENABLED = True
    def test_default_is_on(self):
        self.assertIs(mw.MULTIWORD_HOMOPHONE_ENABLED, True)


class SentenceLevelInMemory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _unpatch_val()
        cases = json.load(open(CASES, encoding="utf-8"))
        cls.cases = cases
        cls.before = {c["id"]: judge(c["canonical"], c["asr"]) for c in cases}   # 未patch=現行
        _patch_val()
        cls.after = {c["id"]: judge(c["canonical"], c["asr"]) for c in cases}
        mw.MULTIWORD_HOMOPHONE_ENABLED = False
        cls.after_off = {c["id"]: judge(c["canonical"], c["asr"]) for c in cases}   # rollback時
        mw.MULTIWORD_HOMOPHONE_ENABLED = True
    @classmethod
    def tearDownClass(cls):
        _unpatch_val()
    def test_41_cases_count(self):
        self.assertEqual(len(self.cases), 41)
    def test_41_cases_expectations(self):
        ng = []
        for c in self.cases:
            a, e = self.after[c["id"]], c["expect"]
            if e == "PASS": ok = a.startswith("PASS")
            elif e == "NOT_PASS": ok = a.startswith("NOT_PASS")
            elif e == "REVIEW": ok = a == "PASS(HOMOPHONE_MATCH_NUMBER_EXCEPTION)"
            else: ok = a == self.before[c["id"]]
            if not ok: ng.append((c["id"], e, a))
        self.assertEqual(ng, [])
    def test_matches_trial_after_v3(self):
        diffs = [(c["id"], c["after_v3"], self.after[c["id"]]) for c in self.cases
                 if "after_v3" in c and c["after_v3"] != self.after[c["id"]]]
        self.assertEqual(diffs, [])
    def test_no_pass_to_ng_and_no_new_false_pass(self):
        for c in self.cases:
            b, a = self.before[c["id"]], self.after[c["id"]]
            if b.startswith("PASS"): self.assertTrue(a.startswith("PASS"), c["id"])      # PASS->NG 0
            if c["expect"] == "NOT_PASS": self.assertTrue(a.startswith("NOT_PASS"), c["id"])  # 新規誤PASS 0
    def test_rollback_flag_off_is_identical_to_current(self):
        self.assertEqual(self.before, self.after_off)
    def test_bius_sentence_ng(self):
        S = "The service is called %s now."
        self.assertTrue(judge(S % "bias", S % "Bi-us").startswith("NOT_PASS"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
