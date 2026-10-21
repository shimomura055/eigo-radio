"""er094_multiword_homophone_01 のunit test(API 0・ファイル出力なし)。
実行: .venv/Scripts/python.exe -m unittest er094_multiword_homophone_01_test_01 -v
A-2(配線後): 文単位テストは実コード(val.protected_checkの配線済み呼出)を直接叩く。exec差替えpatchは廃止(P-06、二重適用防止)。
before=MULTIWORD_HOMOPHONE_ENABLED=False(rollback定数=現行挙動)、after=True(既定)。"""
import inspect, json, os, re, sys, unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er094_multiword_homophone_01 as mw
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec

CASES = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "TRIAL_CASES_01.json")


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


class SentenceLevelRealCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cases = json.load(open(CASES, encoding="utf-8"))
        cls.cases = cases
        mw.MULTIWORD_HOMOPHONE_ENABLED = False
        try:
            cls.before = {c["id"]: judge(c["canonical"], c["asr"]) for c in cases}   # 定数OFF=現行
        finally:
            mw.MULTIWORD_HOMOPHONE_ENABLED = True
        cls.after = {c["id"]: judge(c["canonical"], c["asr"]) for c in cases}
        mw.MULTIWORD_HOMOPHONE_ENABLED = False
        try:
            cls.after_off = {c["id"]: judge(c["canonical"], c["asr"]) for c in cases}
        finally:
            mw.MULTIWORD_HOMOPHONE_ENABLED = True
    def test_wired_real_code_no_exec_patch(self):
        src = inspect.getsource(val.protected_check)
        self.assertEqual(src.count("_mw_homophone.multiword_homophone_candidate("), 1)   # 呼出1回(二重適用なし)
        self.assertNotIn("_MW_CAND", src)
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
    def test_off_dicts_byte_identical(self):
        # OFF(定数False)時: 判定dict(content_word_diffs)にadditiveキーが現れない
        mw.MULTIWORD_HOMOPHONE_ENABLED = False
        try:
            r = val.classify_asr_match("The service is called byUs now.", "The service is called buy us now.")
            for d in r.protected.content_word_diffs:
                self.assertNotIn("multiword_homophone", d)
            self.assertEqual(val.multiword_steps_extra(r.protected.content_word_diffs), {})
        finally:
            mw.MULTIWORD_HOMOPHONE_ENABLED = True
    def test_additive_key_only_on_hit_with_original_spans(self):
        r = val.classify_asr_match("Try byUs now.", "Try buy us now.")
        hits = [d for d in r.protected.content_word_diffs if d.get("multiword_homophone")]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["multiword_homophone"], {"canonical_span": ["byus"], "asr_span": ["buy", "us"]})
        self.assertEqual(val.multiword_steps_extra(r.protected.content_word_diffs)["multiword_homophone_spans"],
                         [{"canonical_span": ["byus"], "asr_span": ["buy", "us"]}])
        # 1:1同音(既存経路)にはキーが付かない
        r2 = val.classify_asr_match("We wait here.", "We weight here.")
        self.assertFalse([d for d in r2.protected.content_word_diffs if "multiword_homophone" in d])
    def test_bius_negative_article_text_byUs(self):
        # P-07: canonicalは記事実テキスト byUs。adapter(Primary->Secondary->最終)での判定はruntime evidenceで別途記録
        S = "The service is called %s now."
        j = judge(S % "byUs", S % "Bi-us")
        self.assertTrue(j.startswith("NOT_PASS"), j)
        d = {}
        self.assertFalse(mw.multiword_span_equivalent_v3(["byus"], ["bi", "us"], detail=d))
        self.assertIn("V8", d["why"])


    def test_bius_sentence_ng(self):
        S = "The service is called %s now."
        self.assertTrue(judge(S % "bias", S % "Bi-us").startswith("NOT_PASS"))


class StaticChecks(unittest.TestCase):
    PROD = [f for f in os.listdir(ROOT) if f.endswith(".py") and f.startswith("er") and "_test" not in f
            and "validation_test" not in f]
    def test_no_production_py_assigns_flag(self):
        pat = re.compile(r"^[ 	]*[\w.]*MULTIWORD_HOMOPHONE_ENABLED[ 	]*=(?!=)|setattr\([^)]*MULTIWORD_HOMOPHONE_ENABLED", re.M)
        bad = []
        for f in self.PROD:
            if f == "er094_multiword_homophone_01.py":
                continue
            with open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore") as fh:
                t = fh.read()
            if pat.search(t):
                bad.append(f)
        # 代入してよいのはtest/measure/run系のみ(Productionではない)。ここでは tools/trial/測定系の命名を除外
        bad = [f for f in bad if not re.search(r"(test|measure|trial|probe|evidence|regression)", f)]
        self.assertEqual(bad, [])
    def test_only_val_imports_er094(self):
        users = []
        for f in self.PROD:
            if f == "er094_multiword_homophone_01.py":
                continue
            with open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore") as fh:
                t = fh.read()
            if re.search(r"^\s*(import|from)\s+er094_multiword_homophone_01", t, re.M):
                users.append(f)
        users = [f for f in users if not re.search(r"(test|measure|trial|probe|evidence|regression)", f)]
        self.assertEqual(users, ["er006_preprod_hardening_01_validation.py"])
    def test_hr_lock_has_no_rejudge_auto_unlock(self):
        t = open(os.path.join(ROOT, "er019_family_x_validation_inheritance_01.py"), encoding="utf-8").read()
        i = t.index("def rejudge_with_current_judge")
        body = t[i:i + 2500]
        self.assertNotRegex(body, r"(?i)unlock|hr_lock|release_lock|clear_lock")


class J11RejudgeActualBehavior(unittest.TestCase):
    """P-01: 再判定経路(rejudge_with_current_judge)はshould_passのみで判定し_step_alternate_passを通らない。
    多語同音一致(ASR_VALIDATION_UNCERTAIN系)は再判定でshould_pass=False=従来どおり再生成(安全側。既存1:1同音と同じ)。"""
    def test_rejudge_path_uses_should_pass_only(self):
        import er019_family_x_validation_inheritance_01 as inh
        src = inspect.getsource(inh.rejudge_with_current_judge)
        self.assertIn("should_pass", src)
        self.assertNotIn("_step_alternate_pass", src)
    def test_multiword_homophone_is_not_should_pass_on_plain_classify(self):
        S = "The service is called %s now."
        r = val.classify_asr_match(S % "byUs", S % "buy us")
        self.assertFalse(r.should_pass)                       # 再判定はF1_REJUDGE_NG側(安全側。1:1同音と同挙動)
        r11 = val.classify_asr_match("We wait here.", "We weight here.")
        self.assertFalse(r11.should_pass)                     # 既存1:1同音も同じ
        self.assertTrue(sec.is_homophone_candidate_mismatch(r))   # 通常cascade入口(_step_alternate_pass)でのみ救済


class AdapterEvidenceKeys(unittest.TestCase):
    """P-03: 証跡(steps[*]とasr_judgement.adapter)は一致時のみ付与・判定不変・OFF時はキー無し。"""
    @classmethod
    def setUpClass(cls):
        import tempfile, wave
        cls.d = tempfile.mkdtemp()
        cls.wav = os.path.join(cls.d, "x.wav")
        with wave.open(cls.wav, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000); f.writeframes(b"\0\0" * 16000)
        cls._orig_az = sec.get_full_text_via_azure_stt_with_phrase_list
        sec.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (_ for _ in ()).throw(AssertionError("Secondary must not be called"))
    @classmethod
    def tearDownClass(cls):
        sec.get_full_text_via_azure_stt_with_phrase_list = cls._orig_az
    def _run(self, canon, asr):
        return sec.evaluate_attempt_with_cascade_detail(canon, asr, [], self.wav, language="en-US", ledger_phrases=[])
    def test_keys_on_hit_only(self):
        d = self._run("The service is called byUs now.", "The service is called buy us now.")
        self.assertTrue(d["verified"])
        self.assertEqual(d["steps"][0]["multiword_homophone_spans"], [{"canonical_span": ["byus"], "asr_span": ["buy", "us"]}])
        self.assertEqual(d["asr_judgement"]["adapter"]["multiword_homophone_spans"], d["steps"][0]["multiword_homophone_spans"])
        d2 = self._run("We wait here.", "We wait here.")
        self.assertNotIn("multiword_homophone_spans", d2["steps"][0])
        self.assertNotIn("multiword_homophone_spans", d2["asr_judgement"]["adapter"])
    def test_off_has_no_keys_and_not_verified(self):
        mw.MULTIWORD_HOMOPHONE_ENABLED = False
        try:
            d = sec.evaluate_attempt_with_cascade_detail("The service is called byUs now.", "The service is called buy us now.", [], self.wav,
                                                          language="en-US", ledger_phrases=[], cascade_enabled=False)
            self.assertNotIn("multiword_homophone_spans", d["steps"][0])
        finally:
            mw.MULTIWORD_HOMOPHONE_ENABLED = True


if __name__ == "__main__":
    unittest.main(verbosity=2)
