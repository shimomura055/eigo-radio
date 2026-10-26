# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03: 区分1(承認済み規則への準拠修正)のProduction適用の回帰test(API 0)。

固定する性質:
  (1) 敵対的85件(adversarial_01.json: conversions 22 / have_roles 40 / past 8 / idiom 15)がProduction新コードで期待どおり
  (2) A/B/C経路(allow_inflection_normalization=False)の出力は変更前(git HEAD)とバイト一致(abc_golden_01.json、1002件)
  (3) AI島a2の`studied separately`->`study separately`が全文選定のvalidatorでPASS(保存済み応答の机上確認。HR候補は再生成しない)
  (4) `heated debate`型(V+名詞=形容詞化分詞)・`increased supply`(-ly名詞)は原形化しない / `has spread`等はaux / rang through->ring through /
      lay・wound・ground・bore・boundは補完しない
  (5) 【委任_02で改訂=旧規則の撤去】旧(5)『区分2[慣用句の閉表・救済フロー]はProductionに未配線(受理面が増えていない)』は、ユーザーの正式採用(2026-10-26)による
      救済方式の配線で撤去。代わりに、(a)文脈外[旧経路・A/B/C・他呼出元]では従来と完全に同一、(b)er125.rescue_context[=generate_candidates実行中]内でのみ
      辞書見出し一致の助動詞始まり慣用句が受理され、(c)`will be missed`/`could not bear`/`time is money`/`is money`/名詞主語のことわざ/完全文は文脈内でも引き続き拒否される、を固定する。
      これは受理基準の緩和test化ではなく、承認済み方式の配線に伴う期待値の更新(改訂理由=FIX_01.md M4)。
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
import er125_kp_rescue_production_01 as er125   # noqa: E402

RD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02")


import contextlib   # noqa: E402


@contextlib.contextmanager
def _ctx_on(env="1"):
    """generate_candidates文脈をON(+EIGO_KP_RESCUEを明示固定。シェルの値に依存しない)にして実行する。"""
    prev = os.environ.get(er125.KILL_SWITCH_ENV)
    os.environ[er125.KILL_SWITCH_ENV] = env
    tok = er125._rescue_ctx.set(True)
    try:
        yield
    finally:
        er125._rescue_ctx.reset(tok)
        if prev is None:
            os.environ.pop(er125.KILL_SWITCH_ENV, None)
        else:
            os.environ[er125.KILL_SWITCH_ENV] = prev


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

    def test_idiom_exceptions_only_inside_candidate_generation_context(self):
        """旧test_idiom_exceptions_are_not_wired の改訂(M4・旧規則の撤去)。
        (a)文脈外(旧経路): 法助動詞/be系を含む句は従来どおり拒否(例外は元からProductionで通る形=ASCII縮約`can't`の beggars can't be choosers のみ)。
        (b)文脈内(generate_candidates実行中): 敵対的15件がadversarial_01.jsonの期待どおり(allowed=辞書見出し一致の助動詞始まり慣用句のみ。blocked=名詞主語のことわざ・完全文・疑問文・倒置・be系)。"""
        for c in ADV["idiom"]:
            blocked = ft.contains_finite_aux_role_based(c["phrase"])
            already_allowed_in_head = c["phrase"] == "beggars can't be choosers"
            self.assertEqual(blocked, not already_allowed_in_head, c)
        with _ctx_on():
            for c in ADV["idiom"]:
                self.assertEqual(ft.contains_finite_aux_role_based(c["phrase"]), c["expect"] == "blocked", c)


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
        """M4(旧規則の撤去): 旧assert『can of worms がblocked』は、文脈外(旧経路)では引き続き成立、er125.rescue_context内では辞書見出し一致のため通る(配線による期待値の更新)。
        `will be missed`/`could not bear`/`time is money`/`is money` は文脈の内外を問わず拒否のまま(緩和なし)。"""
        self.assertFalse(ft.contains_finite_aux_role_based("have a say"))
        self.assertFalse(ft.contains_finite_aux_role_based("had a problem"))
        for ph in ["will be missed", "could not bear", "time is money", "can of worms", "is money"]:
            self.assertTrue(ft.contains_finite_aux_role_based(ph), ph)               # 文脈外=旧経路は従来どおり
        with _ctx_on():
            self.assertFalse(ft.contains_finite_aux_role_based("can of worms"))      # 辞書見出し+構造条件に一致(旧規則の撤去)
            for ph in ["will be missed", "could not bear", "time is money", "is money"]:
                self.assertTrue(ft.contains_finite_aux_role_based(ph), ph)           # 引き続き拒否
        with _ctx_on("0"):
            self.assertTrue(ft.contains_finite_aux_role_based("can of worms"))      # kill switch OFF=従来動作

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

    def test_quant_determiner_guard_applied_positive_and_negative(self):
        """KPRW1 委任_01 区分1: 量化詞限定詞guard是正(承認文『直後が限定詞なら原形化』の限定詞に量化詞を含める)。fulltext経路限定。
        量化詞はguard用の閉表`_QUANT_DET`にのみ追加し、既存`_GUARD_DET`(他用途)は不変。"""
        for det in ("no", "each", "every", "all", "both", "another", "either", "neither", "several", "few", "many", "much", "enough"):
            self.assertIn(det, ft._QUANT_DET)
            self.assertNotIn(det, ft._GUARD_DET)
        # 正例: 動詞活用形+量化詞(+名詞) -> 原形
        for key, disp in (("accept no responsibility", "accepts no responsibility"), ("keep no secrets", "kept no secrets"),
                          ("raise every hand", "raised every hand"), ("take many questions", "took many questions"),
                          ("make enough noise", "made enough noise"), ("give each student", "gave each student")):
            self.assertIsNotNone(ft.find_inflection_window(key, disp), (key, disp))
        # 負例: 形容詞化分詞・名詞・前方活用不一致・非動詞位置・誤原形は不受理のまま
        for key, disp in (("heat many", "heated many"), ("limit no gain", "limited no gain"), ("hop no fence", "hoped no fence"),
                          ("the accept no", "the accepts no"), ("rise each", "rice each"), ("new every day", "news every day"), ("mean each case", "means each case")):
            self.assertIsNone(ft.find_inflection_window(key, disp), (key, disp))
        # A/B/C(allow_inflection_normalization=False)は無影響
        r = kc.validate_canonicalization_item("accept no responsibility", "accepts no responsibility", "accepts no responsibility",
                                              normalization_reason="lemma_normalization", original_span="accepts no responsibility",
                                              allow_inflection_normalization=False)
        self.assertFalse(r["ok"])
        r2 = kc.validate_canonicalization_item("accept no responsibility", "accepts no responsibility", "accepts no responsibility",
                                               normalization_reason="lemma_normalization", original_span="accepts no responsibility",
                                               allow_inflection_normalization=True)
        self.assertTrue(r2["ok"], r2)

    def test_rescue_wiring_in_er105_is_limited_to_approved_hooks(self):
        """旧test_rescue_flow_not_wired_in_er105 の改訂(旧規則の撤去): 旧設計の閉表/DEV module/スロット一般化/部分句候補はer105に入っていない。
        er125への参照は遅延import関数`_rescue()`経由の3か所(H1 contains_finite_aux_role_based / H2 validate_and_resolve)のみ。"""
        with open(os.path.join(ROOT, "er105_kp_fulltext_selector_01.py"), encoding="utf-8") as f:
            src = f.read()
        for token in ("idiom_closed_table", "import er123", "slot_generalization", "subspan_candidates", "KP_RESCUE"):
            self.assertNotIn(token, src, token)
        self.assertNotIn("\nimport er125", src)                # top-level importなし(循環回避)。遅延importのみ
        self.assertEqual(src.count("_rescue()."), 2)             # H1 idiom_aux_exception_applies / H2 rescue_selection_item
        self.assertEqual(src.count("import er125_kp_rescue_production_01"), 1)


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
