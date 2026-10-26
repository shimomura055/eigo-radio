# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03: 区分1(承認済み規則への準拠修正)のProduction適用の回帰test(API 0)。

固定する性質:
  (1) 敵対的85件(adversarial_01.json: conversions 22 / have_roles 40 / past 8 / idiom 15)がProduction新コードで期待どおり
  (2) A/B/C経路(allow_inflection_normalization=False)の出力は変更前(git HEAD)とバイト一致(abc_golden_01.json、1002件)
  (3) AI島a2の`studied separately`->`study separately`が全文選定のvalidatorでPASS(保存済み応答の机上確認。HR候補は再生成しない)
  (4) `heated debate`型(V+名詞=形容詞化分詞)・`increased supply`(-ly名詞)は原形化しない / `has spread`等はaux / rang through->ring through /
      lay・wound・ground・bore・boundは補完しない
  (5) 区分2(慣用句の閉表・量化詞限定詞guard・辞書裏付けguard・救済フロー)はProductionに未配線(受理面が増えていない)
実行: $env:PYTHONPATH="netblock_harness_01"; py -m pytest er105_kp_rule_compliance_test_01.py -q   (または run_project_regression --pattern "er105*_test_*.py")
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er003_key_words_canonicalization as kc   # noqa: E402
import er105_kp_fulltext_selector_01 as ft      # noqa: E402

RD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02")


def _load(name):
    with open(os.path.join(RD, name), encoding="utf-8") as f:
        return json.load(f)


ADV = _load("adversarial_01.json")


class TestAdversarial85(unittest.TestCase):
    def test_fixture_size_is_85(self):
        n = sum(len(ADV[k]) for k in ("conversions", "have_roles", "past_forms_must_not_be_added", "past_forms_must_be_added", "idiom"))
        self.assertEqual(n, 85)

    def test_conversions(self):
        for c in ADV["conversions"]:
            got = ft.find_inflection_window(c["key"], c["display"]) is not None
            want = c["expect"] in ("accept", "preexisting_accept")
            self.assertEqual(got, want, c)
            # 最終Gateと同一引数のvalidatorでも同じ(全文選定itemのみ allow_inflection_normalization=True)
            ok = kc.validate_canonicalization_item(c["key"], c["display"], c["display"], normalization_reason="lemma_normalization",
                                                   original_span=c["display"], allow_inflection_normalization=True)["ok"]
            self.assertEqual(ok, want, c)

    def test_have_roles(self):
        for c in ADV["have_roles"]:
            got = [r for t, r in ft.finite_aux_roles(c["phrase"]) if t in ft._HAVE]
            self.assertEqual(got, c["expect"], c)

    def test_past_forms(self):
        for w in ADV["past_forms_must_not_be_added"]:
            self.assertNotIn(w, ft._PAST_ONLY_IRREGULAR, w)
            self.assertNotIn(w, ft._AMBIGUOUS_IRREGULAR, w)
        for w in ADV["past_forms_must_be_added"]:
            self.assertTrue(w in ft._PAST_ONLY_IRREGULAR or w in ft._AMBIGUOUS_IRREGULAR, w)

    def test_idiom_exceptions_are_not_wired(self):
        """区分2(慣用句の閉表)は未配線: 閉表で例外になる句も含め、法助動詞/be系を含む句はProductionでは従来どおり拒否。
        例外は元からProductionで通る形(ASCII縮約`can't`が1トークンで語形リストをすり抜ける beggars can't be choosers)のみ。"""
        for c in ADV["idiom"]:
            blocked = ft.contains_finite_aux_role_based(c["phrase"])
            already_allowed_in_head = c["phrase"] == "beggars can't be choosers"
            self.assertEqual(blocked, not already_allowed_in_head, c)


class TestRuleStatements(unittest.TestCase):
    def test_heated_debate_type_not_normalized(self):
        for k, d in [("heat debate", "heated debate"), ("use cars", "used cars"), ("raise concern", "raised concerns"),
                     ("stun timely rescue", "stunned timely rescue"), ("stop short", "stopped short")]:
            self.assertFalse(ft.is_valid_inflection_normalization(k, d), (k, d))

    def test_ly_noun_and_wrong_lemma_rejected(self):
        for k, d in [("increase supply", "increased supply"), ("fail rally", "failed rally"), ("hop quietly", "hoped quietly"),
                     ("dig well", "dug well"), ("cancel reply", "cancelled reply")]:
            self.assertIsNone(ft.find_inflection_window(k, d), (k, d))

    def test_adverb_normalization_accepted(self):
        for k, d in [("study separately", "studied separately"), ("work quietly", "worked quietly"), ("try hard", "tried hard"),
                     ("look at separately", "looked at separately")]:
            self.assertIsNotNone(ft.find_inflection_window(k, d), (k, d))

    def test_ly_adverb_guard_data_is_closed(self):
        self.assertFalse(ft.is_manner_adverb("supply"))
        self.assertFalse(ft.is_manner_adverb("friendly"))
        self.assertFalse(ft.is_manner_adverb("well"))
        self.assertTrue(ft.is_manner_adverb("separately"))
        self.assertTrue(ft.is_manner_adverb("happily"))

    def test_has_spread_and_participles_are_aux(self):
        for ph in ["has spread", "have quit", "has more than doubled", "have all gone", "had the board known", "Has Vera been", "have been"]:
            self.assertTrue(ft.contains_finite_aux_role_based(ph), ph)

    def test_lexical_have_not_blocked_but_modals_and_be_remain_blocked(self):
        self.assertFalse(ft.contains_finite_aux_role_based("have a say"))
        self.assertFalse(ft.contains_finite_aux_role_based("had a problem"))
        for ph in ["will be missed", "could not bear", "time is money", "can of worms", "is money"]:
            self.assertTrue(ft.contains_finite_aux_role_based(ph), ph)

    def test_rang_through_and_completed_past_table(self):
        self.assertIsNotNone(ft.find_inflection_window("ring through", "rang through"))
        self.assertIsNotNone(ft.find_inflection_window("sing along", "sang along"))
        for w in ("lay", "wound", "ground", "bore", "bound"):
            self.assertNotIn(w, ft._PAST_ONLY_IRREGULAR)
            self.assertNotIn(w, ft._AMBIGUOUS_IRREGULAR)

    def test_past_table_completion_is_idempotent_and_never_overwrites(self):
        before = (dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR))
        ft._complete_past_tables()
        self.assertEqual(before, (dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR)))
        for w, lemma in {"gave": "give", "took": "take", "led": "lead", "given": "give", "saw": "see"}.items():     # 既存のエントリは不変
            self.assertEqual((ft._PAST_ONLY_IRREGULAR.get(w) or ft._AMBIGUOUS_IRREGULAR.get(w)), lemma)

    def test_quant_determiner_guard_not_applied(self):
        """区分2相当(量化詞限定詞guard: kept no secrets->keep no secrets)は本委任の範囲外=未適用(受理面を広げない)。"""
        for det in ("no", "each", "every", "all", "both", "another", "either", "neither", "several", "few", "many", "much", "enough"):
            self.assertNotIn(det, ft._GUARD_DET)
        self.assertIsNone(ft.find_inflection_window("raise every hand", "raised every hand"))

    def test_rescue_flow_not_wired_in_er105(self):
        src = open(os.path.join(ROOT, "er105_kp_fulltext_selector_01.py"), encoding="utf-8").read()
        for token in ("idiom_closed_table", "import er123", "reanchor", "slot_generalization", "subspan_candidates", "KP_RESCUE"):
            self.assertNotIn(token, src, token)


class TestAbcByteIdentical(unittest.TestCase):
    """A/B/C経路(allow_inflection_normalization=False)の判定結果は変更前Production(git HEAD)と完全一致(golden 1002件)。"""

    def test_golden(self):
        g = _load("abc_golden_01.json")
        self.assertGreaterEqual(g["n"], 1000)
        for row in g["rows"]:
            key, disp, span, reason, orig = row["args"]
            r = kc.validate_canonicalization_item(key, disp, span, normalization_reason=reason, original_span=orig, allow_inflection_normalization=False)
            self.assertEqual(json.dumps(r, sort_keys=True, ensure_ascii=False), json.dumps(row["result"], sort_keys=True, ensure_ascii=False), row["args"])
            self.assertEqual(kc._contains_finite_auxiliary(key), row["aux"], row["args"])

    def test_shared_aux_list_function_unchanged(self):
        self.assertEqual(kc._FINITE_AUX_WORDS, {"is", "are", "was", "were", "has", "have", "had", "will", "would", "can", "could", "should",
                                                  "may", "might", "must"})
        self.assertTrue(kc._contains_finite_auxiliary("have a say"))      # A/B/C共有関数は語形リスト判定のまま

    def test_abc_path_still_rejects_have_lexical_and_adverb_normalization(self):
        r = kc.validate_canonicalization_item("have a say", "have a say", "have a say", original_span="have a say", allow_inflection_normalization=False)
        self.assertIn("有限助動詞が含まれている", r["reasons"])
        r2 = kc.validate_canonicalization_item("study separately", "studied separately", "studied separately",
                                               normalization_reason="lemma_normalization", original_span="studied separately",
                                               allow_inflection_normalization=False)
        self.assertFalse(r2["ok"])
        # 全文選定itemでは同じ入力が通る
        r3 = kc.validate_canonicalization_item("have a say", "have a say", "have a say", original_span="have a say", allow_inflection_normalization=True)
        self.assertNotIn("有限助動詞が含まれている", r3["reasons"])


class TestAiIslandA2(unittest.TestCase):
    """AI島a2の除外句(保存済み応答のdropped[])が、Production新コードのvalidatorでPASSすること(机上。HR候補は再生成・確定しない)。"""
    P = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "ai_island_temple__run_ai_01", "a2", "key_phrases", "kp_candidates.json")

    def test_studied_separately_passes_validator(self):
        if not os.path.exists(self.P):
            self.skipTest("run_ai_01 artifact not present")
        d = json.load(open(self.P, encoding="utf-8"))
        dropped = [x for x in d["dropped"] if x["phrase"] == "studied separately"]
        self.assertEqual(len(dropped), 1)
        r = kc.validate_canonicalization_item("study separately", "studied separately", "studied separately",
                                              normalization_reason="lemma_normalization", original_span="studied separately",
                                              allow_inflection_normalization=True)
        self.assertTrue(r["ok"], r)
        # CMU(語構成の発音辞書登録)も従来の同一検査で通る
        import er108_kp_cmu_lexicon_gate_01 as cmu
        self.assertEqual(cmu.reasons_for_phrase("study separately"), [])


if __name__ == "__main__":
    unittest.main()
