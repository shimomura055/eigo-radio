"""PNMH-PLAN-01 委任_03: Trial専用の純関数試作 proto_multiword_span_01.py のunit test(API 0・Production経路無変更・ファイル出力なし)。
ユーザー判断(2026-10-22)の反映確認: ストレス記号の差でNGにしない / 音素が異なる誤発音はNG / Bi-us型はNG維持(V8) /
entity_likeは代表発音限定 / 既存の誤PASS防止ガード(文字読み・略語・数値否定・OOV・脱落追加)維持。
実行: .venv/Scripts/python.exe docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/test_proto_multiword_span_v3_01.py (ディレクトリ名にハイフンがありunittest -mは不可)。
"""
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import proto_multiword_span_01 as P

v3 = P.multiword_span_equivalent_v3
v2 = P.multiword_span_equivalent

class SpanLevel(unittest.TestCase):
    def test_stress_only_difference_is_pass(self):          # byus=B AY1 AH0 S / buy us=B AY1 + AH1 S
        self.assertTrue(v3(["byus"], ["buy", "us"]))
        self.assertTrue(v3(["byus"], ["by", "us"]))
    def test_general_words_pass(self):
        self.assertTrue(v3(["onto"], ["on", "to"]))
        self.assertTrue(v3(["already"], ["all", "ready"]))
    def test_reverse_direction_pass(self):                  # canonical複数語 / ASR 1語
        self.assertTrue(v3(["all", "ready"], ["already"]))
        self.assertFalse(v3(["buy", "us"], ["byus"]))   # canonical側に2字token(us)=G5(canonical側3字未満)で非救済=既存ガード維持
    def test_different_phonemes_are_ng(self):
        for asr in (["buy", "a"], ["buy", "us", "us"], ["buy", "us", "on"], ["buy", "us", "an"], ["bus", "s"]):
            self.assertFalse(v3(["byus"], asr), asr)
    def test_drop_or_add_is_ng(self):
        self.assertFalse(v3(["byus"], ["buy"]))             # 1:1扱い=本関数の対象外(既存経路で非同音)
        self.assertFalse(v3(["byus"], ["buy", "us", "an"]))
    def test_bius_type_is_ng_in_v3_but_pass_in_v2(self):    # U-BI: NG維持(V8)。v2(V1)はPASSしてしまう=差の固定
        self.assertTrue(v2(["bias"], ["bi", "us"]))
        self.assertFalse(v3(["bias"], ["bi", "us"]))
        self.assertIn("V8", (lambda d: (v3(["bias"], ["bi", "us"], detail=d), d["why"])[1])({}))
    def test_known_residual_by_us_is_pass(self):            # 既知の限界(DESIGN_OPTIONS §4-3): 機能語byは区別できない
        self.assertTrue(v3(["bias"], ["by", "us"]))
    def test_letter_reading_guards_kept(self):
        for c, a in ((["us"], ["u", "s"]), (["am"], ["a", "m"]), (["melos"], ["mellow", "s"]), (["ai"], ["a", "i"])):
            self.assertFalse(v3(c, a), (c, a))
    def test_acronym_guard_kept(self):                       # ai phone -> iphone (canonical側3字未満)
        self.assertFalse(v3(["ai", "phone"], ["iphone"]))
    def test_oov_is_undecidable(self):
        self.assertFalse(v3(["byus"], ["xqzv", "us"]))
    def test_number_negation_guard(self):
        self.assertFalse(v3(["byus"], ["buy", "not"]))
        self.assertFalse(v3(["two"], ["to", "o"]))
    def test_too_long_and_both_multi(self):
        self.assertFalse(v3(["byus"], ["b", "u", "y", "s"]))
        self.assertFalse(v3(["buy", "us"], ["by", "us"]))
    def test_non_alpha(self):
        self.assertFalse(v3(["byus"], ["buy", "us2"]))
    def test_entity_like_representative_only(self):
        self.assertTrue(v3(["today"], ["to", "day"]))                   # 全variant比較ならPASS
        self.assertFalse(v3(["today"], ["to", "day"], entity_like=True))  # 固有名詞らしい語は代表発音のみ=非救済
        self.assertTrue(v3(["byus"], ["buy", "us"], entity_like=True))   # 代表発音で一致する正例は維持
    def test_default_v2_behaviour_unchanged(self):
        self.assertTrue(v2(["byus"], ["buy", "us"])); self.assertFalse(v2(["us"], ["u", "s"]))

class SentenceLevelInMemory(unittest.TestCase):
    """val.protected_check をメモリ上でのみpatch(ファイル無変更)。v3 wrapper を差し込んで文単位の最終判定を確認。"""
    @classmethod
    def setUpClass(cls):
        P.install_proto()
        P.val.__dict__["PROTO_MULTIWORD"] = lambda c, a: v3(c, a)
        import er006_secondary_asr_01 as sec
        cls.sec = sec
    def judge(self, c, a):
        r = P.val.classify_asr_match(c, a)
        if r.should_pass: return "PASS"
        if self.sec.is_entity_like_mismatch(r) or self.sec.is_homophone_candidate_mismatch(r):
            if self.sec._step_alternate_pass(r): return "PASS"
        return "NOT_PASS"
    def test_byus_buy_us_pass(self):
        self.assertEqual(self.judge("The service is called byUs now.", "The service is called buy us now."), "PASS")
    def test_bius_sentence_ng(self):                          # BI1
        self.assertEqual(self.judge("The service is called bias now.", "The service is called Bi-us now."), "NOT_PASS")
    def test_near_sounds_ng(self):
        for a in ("BIOS", "buys", "bus", "buy", "buy us on", "buy a"):
            self.assertEqual(self.judge("The service is called byUs now.", f"The service is called {a} now."), "NOT_PASS", a)
    def test_ai_phone_iphone_ng(self):
        self.assertEqual(self.judge("Some AI Phone Calls Had Humans Behind the Scenes.", "Some iPhone calls had humans behind the scenes."), "NOT_PASS")
    def test_real_mispronunciation_baus_ng(self):             # BI2
        self.assertEqual(self.judge("It is pronounced bias.", "It is pronounced Baus."), "NOT_PASS")

if __name__ == "__main__":
    unittest.main(verbosity=2)
