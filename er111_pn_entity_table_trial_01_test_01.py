# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_02: Run Entity Table(RET) Trial の単体テスト。API 0(LLMは全てmock)。実ファイル書込なし。
正式経路(er103/er006/er019/val/runner)から本Trialが参照されないこと(AST)、表なし/空で er103 と同値であること(SC-1)、
負例(OF-PN2-01〜04)、失敗注入(SC-6)、保存entry再判定/Local Rewrite(OF-PN2-06)、drift guard(OF-PN2-11)を固定する。"""
import ast
import glob
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er006_preprod_hardening_01_validation as val
import er103_proper_noun_alarm_policy_01 as pol
import er111_pn_entity_table_trial_01 as ret
import er111_pn_trial_evaluate_01 as ev

HERE = os.path.dirname(os.path.abspath(__file__))


def mock_llm(a=(), b=None, fail_a=None, fail_b=None):
    """a=call A の entities, b=call B の entities(None なら a と同じ)。fail_* は例外クラス。"""
    calls = []

    def f(text, pid):
        calls.append(pid)
        if pid == "A":
            if fail_a:
                raise fail_a("boom")
            return {"entities": [dict(surface=s, category=c) for s, c in a], "usage": {"jpy": 0.01}}
        if fail_b:
            raise fail_b("boom")
        return {"entities": [dict(surface=s, category=c) for s, c in (a if b is None else b)], "usage": {"jpy": 0.01}}
    f.calls = calls
    return f


def decide(canon, prim, sec, table=None, led=frozenset(), role="FULL_STORY", ret3=True, orig=False):
    kw = dict(canonical_text=canon, primary_cls=val.classify_asr_match(canon, prim), secondary_cls=val.classify_asr_match(canon, sec),
              primary_text=prim, secondary_text=sec, judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role=role, p3_entry="p3_primary_ng")
    if orig:
        return pol.evaluate_alarm_eligibility(enabled=True, ledger_surfaces=led, **kw)
    return ev.evaluate_alarm_eligibility_pn(enabled=True, ledger_surfaces=led, table=table, ret3=ret3, **kw)


def E(surface, words, cat="person", grade="confirmed", elig=None, inits=()):
    return ret.Entry(surface, list(words), cat, grade, ["t"], list(words if elig is None else elig), list(inits))


def sig(d):
    return (d.accept, d.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence, x.similarity_primary, x.similarity_secondary) for x in d.diffs], repr(d.detail))


class BuilderTest(unittest.TestCase):
    SEGS = ['"Bertie, why do you bound?" he asked.', "Her brother sang, 'Bertie, why do you bound?' Vera smiled."]

    def test_bertie_needs_second_independent_call(self):
        a = [("Bertie", "person"), ("Vera", "person")]
        tb = ret.build_entity_table(self.SEGS, llm=mock_llm(a))
        g = {e.surface: e.grade for e in tb.entries}
        self.assertEqual(g["Bertie"], "confirmed")            # call B が一致
        # call B が一致しない場合は weak(LLM単独では証拠にならない = OF-PN2-03)
        tb2 = ret.build_entity_table(self.SEGS, llm=mock_llm(a, b=[("Vera", "person")]))
        g2 = {e.surface: e.grade for e in tb2.entries}
        self.assertEqual(g2["Bertie"], "weak")
        self.assertIn("no_independent_support", [n for e in tb2.entries if e.surface == "Bertie" for n in e.notes])
        self.assertTrue(all(not e.usable for e in tb2.entries if e.surface == "Bertie"))

    def test_call_b_longer_span_does_not_change_category(self):
        # 実データ(SC-9再構築)で見つかった不具合: call Bが歌詞行 "Bertie, why do you bound?" を work_title として挙げても、
        # それは別実体(歌詞行)であり "Bertie"(person)のカテゴリを下げない。同じ語列で work_title と判定された場合のみ厳しい側へ。
        segs = ["'Bertie, why do you bound?' sang the boy."]
        a = [("Bertie", "person")]
        tb = ret.build_entity_table(segs, llm=mock_llm(a, b=[("Bertie, why do you bound?", "work_title")]))
        e = [x for x in tb.entries if x.surface == "Bertie"][0]
        self.assertEqual((e.grade, e.category), ("confirmed", "person"))
        tb2 = ret.build_entity_table(segs, llm=mock_llm(a, b=[("Bertie", "work_title")]))
        e2 = [x for x in tb2.entries if x.surface == "Bertie"][0]
        self.assertFalse(e2.usable)                                   # 判定が割れたら厳しい側(OF-PN2-04)
        self.assertIn("category_downgraded_by_call2", e2.notes)

    def test_second_call_not_made_when_independent_support_exists(self):
        # Vera が文中大文字(独立裏付け)なら call B は不要
        llm = mock_llm([("Vera", "person")])
        ret.build_entity_table(["She said that Vera was very kind."], llm=llm)
        self.assertEqual(llm.calls, ["A"])

    def test_hallucination_and_title_and_heading_dropped(self):
        segs = ["Today we read The Crimson Petal and the White in the old library.", "Vera Chen"]
        a = [("Ghost Person", "person"), ("The Crimson Petal and the White", "work_title"), ("Vera Chen", "person")]
        tb = ret.build_entity_table(segs, llm=mock_llm(a))
        reasons = {d["surface"]: d["reason"] for d in tb.meta["dropped"]}
        self.assertEqual(reasons["Ghost Person"], "not_verbatim")
        self.assertEqual(reasons["The Crimson Petal and the White"], "long_phrase")
        self.assertEqual(reasons["Vera Chen"], "heading_or_title_line")

    def test_category_rule_work_title_cmu_in_token_not_evidence(self):
        text = ["She read the Petal Quarterly yesterday and then Bertie came."]
        a = [("Petal Quarterly", "work_title"), ("Bertie", "person")]
        tb = ret.build_entity_table(text, llm=mock_llm(a))
        d = {e.surface: e for e in tb.entries}
        self.assertNotIn("petal", d["Petal Quarterly"].eligible)       # OF-PN2-04: 作品名中のCMU収録の低頻度一般語に証拠を付けない
        self.assertIn("bertie", d["Bertie"].eligible)
        # brand_product / person ではCMU収録の非一般語にも付く
        tb2 = ret.build_entity_table(text, llm=mock_llm([("Petal", "brand_product")]))
        self.assertIn("petal", [t for e in tb2.entries for t in e.eligible])

    def test_general_word_name_has_no_eligible_token(self):
        tb = ret.build_entity_table(["Mark told Rose that Will had paid.", "Iran was mentioned."],
                                    llm=mock_llm([("Mark", "person"), ("Rose", "person"), ("Will", "person"), ("Iran", "place")]))
        self.assertTrue(all(not e.eligible for e in tb.entries))
        self.assertEqual(len(tb.meta["blocked_general_person_place"]), 4)       # OF-PN2-09(ii): 件数記録
        self.assertTrue(tb.is_empty())

    def test_lowercase_form_in_text_removes_eligibility(self):
        tb = ret.build_entity_table(["Roasting beans is easy. We like roasting coffee. Bertie arrived."],
                                    llm=mock_llm([("Roasting", "other_named"), ("Bertie", "person")]))
        d = {e.surface: e for e in tb.entries}
        self.assertNotIn("roasting", d["Roasting"].eligible)

    def test_initials_merge(self):
        segs = ["We met L. Mimoun at the cafe yesterday."]
        tb = ret.build_entity_table(segs, llm=mock_llm([("L.", "person"), ("Mimoun", "person")]))
        names = [e.surface for e in tb.entries]
        self.assertIn("L. Mimoun", names)
        self.assertNotIn("L.", names)
        e = [x for x in tb.entries if x.surface == "L. Mimoun"][0]
        self.assertEqual(e.initials, ["l"])

    def test_verbatim_pre_and_post_supply_and_quotes(self):
        # 供給前text(pre_text)にだけ出る表記でも逐語検証できる。引用符向きの違いを吸収する(OF-PN2-05)
        seg = ret.Seg(text="He said it was Kate’s bag.", pre_text="He said it was Khaite’s bag.")
        tb = ret.build_entity_table([seg], llm=mock_llm([("Khaite", "brand_product")]))
        self.assertIn("khaite", [t for e in tb.entries for t in e.words])
        seg2 = ret.Seg(text="It was a “Bertie” moment, said Vera.")
        tb2 = ret.build_entity_table([seg2], llm=mock_llm([("Bertie", "person")]))
        self.assertTrue(any(e.surface == "Bertie" for e in tb2.entries))

    def test_declared_entities_and_seed_helper(self):
        seed = {"source_essentials": {"key_roles": [{"name": "Framton", "keep_name": True}, {"role": "aunt", "keep_name": False}]}}
        dec = ret.declared_from_z_seed(seed)
        self.assertEqual([d["name"] for d in dec], ["Framton"])
        tb = ret.build_entity_table(["Framton Nuttel arrived."], declared=dec, llm=mock_llm([]))
        e = [x for x in tb.entries if x.grade == "declared"][0]
        self.assertTrue(e.usable)

    def test_lm_failures_are_fail_closed_and_never_raise(self):
        segs = ["Bertie sang. Vera smiled."]
        for exc in (RuntimeError, TimeoutError, ValueError):
            tb = ret.build_entity_table(segs, llm=mock_llm(fail_a=exc))
            self.assertEqual(tb.status, "LLM_UNAVAILABLE")
            self.assertTrue(tb.is_empty())
            self.assertIn("llm_error", tb.meta)
        # 不正JSON/空/refusal 相当
        for ents in ([{"nope": 1}], [{"surface": 5, "category": "person"}], [{"surface": "Bertie", "category": "weird"}], []):
            def bad(text, pid, ents=ents):
                return {"entities": ents}
            tb = ret.build_entity_table(segs, llm=bad)
            self.assertTrue(tb.is_empty())
        def none_entities(text, pid):
            return {"entities": None}
        self.assertTrue(ret.build_entity_table(segs, llm=none_entities).is_empty())
        # call B 失敗 -> PARTIAL、独立裏付けのないentryは weak
        tb = ret.build_entity_table(["Bertie, why?"], llm=mock_llm([("Bertie", "person")], fail_b=RuntimeError))
        self.assertEqual(tb.status, "PARTIAL_NO_CALL2")
        self.assertTrue(tb.is_empty())

    def test_no_llm_no_api(self):
        tb = ret.build_entity_table(["Bertie sang."], llm=None)
        self.assertEqual(tb.status, "LLM_NOT_CONFIGURED")
        self.assertTrue(tb.is_empty())


class PositionBindingTest(unittest.TestCase):
    """OF-PN2-01: 証拠は語集合でなく実体の出現位置に紐づく。"""

    def test_general_token_of_multiword_entity_is_not_bag_evidence(self):
        tb = ret.EntityTable([E("Elena Will", ["elena", "will"], elig=["elena"])])
        gr, _ = tb.grant_for_phrase("I think Elena Will arrived. She will go.", ["will"])
        self.assertEqual(gr, frozenset())                              # 'will' は eligible でない
        gr, _ = tb.grant_for_phrase("She will go.", ["elena"])           # 実体がそのsegmentに無い
        self.assertEqual(gr, frozenset())
        gr, _ = tb.grant_for_phrase("I think Elena Will arrived.", ["elena"])
        self.assertEqual(gr, frozenset({"elena"}))

    def test_phrase_straddling_entity_boundary_gets_no_grant(self):
        tb = ret.EntityTable([E("Reicher", ["reicher"])])
        gr, info = tb.grant_for_phrase("Reicher will say so today.", ["reicher", "will"])
        self.assertEqual(gr, frozenset())

    def test_all_occurrences_must_be_inside_entity(self):
        tb = ret.EntityTable([E("Reicher", ["reicher"])])
        # 小文字の同形(実体出現でない)があるなら grant しない(保守側)
        gr, _ = tb.grant_for_phrase("Reicher came. Later the reicher left.", ["reicher"])
        self.assertEqual(gr, frozenset())

    def test_capital_consistency_in_occurrence(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        self.assertEqual(tb.grant_for_phrase("bertie sang.", ["bertie"])[0], frozenset())
        self.assertEqual(tb.grant_for_phrase("Bertie sang.", ["bertie"])[0], frozenset({"bertie"}))

    def test_internal_initial_only_inside_entity(self):
        tb = ret.EntityTable([E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        gr, _ = tb.grant_for_phrase("We met L. Mimoun today.", ["l", "mimoun"])
        self.assertEqual(gr, frozenset({"l", "mimoun"}))
        gr, _ = tb.grant_for_phrase("We met L. Smith today. Mimoun left.", ["l"])
        self.assertEqual(gr, frozenset())

    def test_general_in_phrase_ablation_is_position_bound(self):
        tb = ret.EntityTable([E("Stephen Reicher", ["stephen", "reicher"], elig=["reicher"])], general_in_phrase=True)
        gr, _ = tb.grant_for_phrase("Stephen Reicher said so.", ["stephen", "reicher"])
        self.assertEqual(gr, frozenset({"stephen", "reicher"}))
        gr, _ = tb.grant_for_phrase("Stephen went home. Reicher said so.", ["stephen"])
        self.assertEqual(gr, frozenset())

    def test_possessive(self):
        tb = ret.EntityTable([E("Khaite", ["khaite"])])
        gr, _ = tb.grant_for_phrase("It was Khaite's bag.", ["khaite", "s"])
        self.assertIn("khaite", gr)


class AcceptanceTest(unittest.TestCase):
    def test_bertie_accepted_with_table_not_without(self):
        canon = '"Bertie, why do you bound?"'
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        self.assertFalse(decide(canon, "Birdie, why do you bound?", "Birdie, why do you bound?", None).accept)
        d = decide(canon, "Birdie, why do you bound?", "Birdie, why do you bound?", tb)
        self.assertTrue(d.accept)
        self.assertEqual(d.diffs[0].evidence, "entity_table:confirmed:person")
        self.assertIn("entity_table", d.detail)
        self.assertEqual(d.detail["entity_table"]["entries_used"][0]["surface"], "Bertie")
        self.assertIn("similarity_band", d.detail["alarm_labels"][0])

    def test_general_word_misread_still_blocked(self):
        # 表があっても Muse->use(両ASRが一般語)・Iran/Mark型(全token一般語)は不受理のまま
        tb = ret.EntityTable([E("Muse", ["muse"], "brand_product")])
        d = decide("Meta released Muse yesterday.", "Meta released use yesterday.", "Meta released use yesterday.", tb)
        self.assertFalse(d.accept)
        tb2 = ret.EntityTable([E("Iran", ["iran"], "place", elig=[])])
        d = decide("Iran signed it.", "Iron signed it.", "Iron signed it.", tb2)
        self.assertFalse(d.accept)

    def test_number_and_negation_still_blocked(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        self.assertFalse(decide("Bertie sang.", "Bert two sang.", "Bert two sang.", tb).accept)
        self.assertFalse(decide("Bertie sang.", "Bert not sang.", "Bert not sang.", tb).accept)

    def test_table_never_loosens_boundaries_vs_ledger_equivalent(self):
        # 表由来の判定は「同一tokenをLedger登録した場合」より緩くならない(位置紐づけのため、実体外では付与されない)
        tb = ret.EntityTable([E("Elena Will", ["elena", "will"], elig=["elena"])])
        for canon, p in (("Elena Will came. She will go.", "Elena Wheel came. She will go."),
                         ("Elena came.", "Alina came.")):
            d_tab = decide(canon, p, p, tb)
            d_led = decide(canon, p, p, None, led=frozenset({"elena", "will"}), orig=True)
            self.assertTrue((not d_tab.accept) or d_led.accept)


class Ret3Test(unittest.TestCase):
    def test_entity_run_span_accepted_and_labeled(self):
        tb = ret.EntityTable([E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        c = "We met L. Mimoun at the cafe yesterday."
        o = decide(c, "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday.", None, orig=True)
        self.assertEqual(o.reason, pol.R_SECONDARY_NOT_ENTITY_ONLY)         # 現行は不受理
        d = decide(c, "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday.", tb)
        self.assertTrue(d.accept)
        self.assertTrue(d.detail["entity_table"]["ret3"])
        self.assertEqual(d.detail["entity_table"]["ret3"][0]["span"], "l mimoun")

    def test_adjacent_entities_with_comma_ok_but_word_between_not(self):
        tb = ret.EntityTable([E("Altuzarra", ["altuzarra"], "brand_product"), E("Toteme", ["toteme"], "brand_product")])
        c = "Bags by Celine, Altuzarra, Toteme appeared."
        self.assertTrue(decide(c, "Bags by Celine, Altusara, Toteme appeared.", "Bags by Celine, altusara totem appeared.", tb).accept)
        c2 = "Bags by Altuzarra and Toteme appeared."
        d = decide(c2, "Bags by Altusara and Toteme appeared.", "Bags by altusara and totem appeared.", tb)
        # 'and' は区切り語。span が canonical で 'altuzarra' 'and'... を巻き込む場合は RET-3 では許容されない
        self.assertFalse(d.accept and d.detail.get("entity_table", {}).get("ret3"))

    def test_negative_neighbor_general_word(self):
        # Melos drank -> mellow strength: 'drank' は実体でないので従来どおり不受理
        tb = ret.EntityTable([E("Melos", ["melos"])])
        d = decide("Melos drank water slowly.", "Mellow drank water slowly.", "Mellow strength water slowly.", tb)
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_SECONDARY_NOT_ENTITY_ONLY)
        # Reicher will -> riker well: 別実体tokenでなく一般語 'will' の偶然隣接
        tb2 = ret.EntityTable([E("Reicher", ["reicher"]), E("Will Smith", ["will", "smith"], elig=[])])
        d = decide("Reicher will say so today.", "Riker will say so today.", "Riker well say so today.", tb2)
        self.assertFalse(d.accept)

    def test_function_word_number_negation_swallowed_by_span(self):
        # 機能語(the/and)・数値・否定語を巻き込んだ span は RET-3 の対象外 = 判定は常に er103 原本と同じ(RET-3 は緩めない)
        tb = ret.EntityTable([E("Melos", ["melos"])])
        for c, p, s in (("Melos the king left.", "Mellow the king left.", "Mellow a ring left."),
                        ("Melos two left.", "Mellow two left.", "Mellow too left."),
                        ("Melos not left.", "Mellow not left.", "Mellow knot left."),
                        ("Melos and Toteme left.", "Mellow and Toteme left.", "Mellow end Toteme left.")):
            o = decide(c, p, s, None, orig=True)
            d = decide(c, p, s, tb)
            self.assertEqual((d.accept, d.reason), (o.accept, o.reason), c)
            self.assertFalse(d.detail.get("entity_table", {}).get("ret3"), c)

    def test_p03_applies_to_synthesized_span(self):
        # 合成spanでもPrimary/Secondary両ASR句が一般語に揃えば不受理
        tb = ret.EntityTable([E("Kristie Tse", ["kristie", "tse"])])
        d = decide("Researcher Kristie Tse found it.", "Researcher Kristie say found it.", "Researcher christie say found it.", tb)
        self.assertFalse(d.accept)

    def test_ret3_off_equals_original(self):
        tb = ret.EntityTable([E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        c = "We met L. Mimoun at the cafe yesterday."
        p, s = "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday."
        o = decide(c, p, s, None, orig=True)
        d = decide(c, p, s, tb, ret3=False)
        self.assertEqual((d.accept, d.reason), (o.accept, o.reason))


class EquivalenceTest(unittest.TestCase):
    """SC-1: 表なし/空/無関係表で er103 と完全一致。"""
    CASES = [
        ("The Khaite bag was small.", "The Kite bag was small.", "The Kite bag was small."),
        ("Bertie sang loudly.", "Birdie sang loudly.", "Birdie sang loudly."),
        ("We met L. Mimoun at the cafe yesterday.", "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday."),
        ("Melos drank water slowly.", "Mellow drank water slowly.", "Mellow strength water slowly."),
        ("Stephen Reicher said so.", "Steven Reichert said so.", "Steven Reichert said so."),
        ("The market fell by 25 percent.", "The market fell by 52 percent.", "The market fell by 52 percent."),
        ("Muse launched today.", "Use launched today.", "Use launched today."),
    ]

    def test_none_empty_unrelated_tables_are_identical(self):
        unrelated = ret.EntityTable([E("Zzyzx Qwerty", ["zzyzx", "qwerty"])])
        for c, p, s in self.CASES:
            base = decide(c, p, s, None, orig=True)
            for tb in (None, ret.EntityTable([]), unrelated):
                d = decide(c, p, s, tb)
                a, b = sig(d), sig(base)
                if tb is unrelated:                      # 診断キー ret3_rejected のみ許容
                    a = (a[0], a[1], a[2], a[3].replace(", 'ret3_rejected': 'span_not_one_entity_run'", ""))
                self.assertEqual(a, b, (c, tb))

    def test_drift_guard_retired_replaced_by_production_differential(self):
        """ASR-QUALITY PN 委任_04(Production統合): 複製元er103の`evaluate_alarm_eligibility`は本体へRETが統合されたため旧drift guard(ORIG_SOURCE_SHA256のうち
        evaluate_alarm_eligibility)は意味を失った(複製=Trial資料として残置)。代替=Trial関数とProduction本体の差分test(Trialはtestからのみimport。
        全コーパス版は er103_run_entity_table_test_01.py::TestEquivalenceW02)。ここでは代表ケースで accept/reason/diffs(evidence含む)が一致することを固定する。"""
        tb = ret.EntityTable([E("Bertie", ["bertie"]), E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        cases = self.CASES + [('"Bertie, why do you bound?"', '"Birdie, why do you bound?"', '"Birdie, why do you bound?"'),
                              ("We met L. Mimoun at the cafe yesterday.", "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday.")]
        import er103_run_entity_table_01 as prod_ret
        ptb = prod_ret.table_from_saved_entries([e.to_dict() for e in tb.entries])
        for c, p, s in cases:
            kw = dict(canonical_text=c, primary_cls=val.classify_asr_match(c, p), secondary_cls=val.classify_asr_match(c, s), primary_text=p,
                      secondary_text=s, judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY", p3_entry="p3_primary_ng")
            a = ev.evaluate_alarm_eligibility_pn(enabled=True, table=tb, **kw)
            b = pol.evaluate_alarm_eligibility(enabled=True, entity_table=ptb, **kw)
            self.assertEqual((a.accept, a.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence) for x in a.diffs]),
                             (b.accept, b.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence) for x in b.diffs]), c)

    def test_disabled_and_ja_and_kp_unchanged(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        kw = dict(canonical_text="Bertie sang.", primary_cls=val.classify_asr_match("Bertie sang.", "Birdie sang."),
                  secondary_cls=val.classify_asr_match("Bertie sang.", "Birdie sang."), primary_text="Birdie sang.", secondary_text="Birdie sang.",
                  judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", p3_entry="p3_primary_ng")
        self.assertEqual(ev.evaluate_alarm_eligibility_pn(enabled=False, role="FULL_STORY", table=tb, **kw).reason, pol.R_DISABLED)
        self.assertEqual(ev.evaluate_alarm_eligibility_pn(enabled=True, role="KEY_PHRASE", table=tb, **kw).reason, pol.R_ROLE)
        self.assertEqual(ev.evaluate_alarm_eligibility_pn(enabled=True, role="FULL_STORY", vote_required=True, table=tb, **kw).reason, pol.R_DUAL)
        self.assertEqual(ev.evaluate_alarm_eligibility_pn(enabled=True, role="FULL_STORY", lang="ja", table=tb, **kw).reason, pol.R_LANG)


class SavedEntriesAndLocalRewriteTest(unittest.TestCase):
    def test_rejudge_from_saved_entries_without_llm_or_table_sha(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        canon = '"Bertie, why do you bound?"'
        d = decide(canon, "Birdie, why do you bound?", "Birdie, why do you bound?", tb)
        saved = d.detail["entity_table"]["entries_used"]
        tb2 = ret.table_from_saved_entries(saved)                            # LLMを呼ばない・shaは別でよい
        d2 = decide(canon, "Birdie, why do you bound?", "Birdie, why do you bound?", tb2)
        self.assertTrue(d2.accept)
        # 保存entryが当該segment textに逐語出現しなければ証拠にならない
        d3 = decide("Someone sang loudly.", "Somebody sang loudly.", "Somebody sang loudly.", tb2)
        self.assertFalse(d3.accept)

    def test_local_rewrite_merge_never_shrinks_table(self):
        base = ret.build_entity_table(["Bertie, why? said Vera."], llm=mock_llm([("Bertie", "person"), ("Vera", "person")]))
        n0 = len(base.entries)
        merged = ret.merge_for_local_rewrite(base, ["Nigel came."], llm=mock_llm([("Nigel", "person")]))
        self.assertGreaterEqual(len(merged.entries), n0)
        self.assertTrue({e.surface for e in base.entries} <= {e.surface for e in merged.entries})
        # 変更segmentのNERが失敗しても既存entryは維持
        merged2 = ret.merge_for_local_rewrite(base, ["Nigel came."], llm=mock_llm(fail_a=RuntimeError))
        self.assertEqual(len(merged2.entries), n0)

    def test_run_holder_is_cleaned_in_finally(self):
        self.assertIsNone(ret.current_table())
        tb = ret.EntityTable([])
        try:
            with ret.run_table(tb):
                self.assertIs(ret.current_table(), tb)
                raise RuntimeError("x")
        except RuntimeError:
            pass
        self.assertIsNone(ret.current_table())

    def test_roundtrip_json(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])], meta={"a": 1})
        d = tb.to_dict()
        tb2 = ret.EntityTable.from_dict(d)
        self.assertEqual(tb2.sha256(), tb.sha256())


class IsolationTest(unittest.TestCase):
    """正式経路から本Trialが参照されない/Trialが書込・flagを持たない(DefaultOffIsolation型)。"""

    def test_no_production_module_imports_trial(self):
        offenders = []
        for f in glob.glob(os.path.join(HERE, "*.py")):
            b = os.path.basename(f)
            if b.startswith("er111_pn_") or b.startswith("er111_ukus_"):
                continue
            if "test" in b:
                continue
            try:
                with open(f, encoding="utf-8") as fh:
                    src = fh.read()
            except Exception:
                continue
            if "er111_pn_" not in src:
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                names = []
                if isinstance(n, ast.Import):
                    names = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    names = [n.module or ""]
                if any(x.startswith("er111_pn_") for x in names):
                    offenders.append(b)
        self.assertEqual(offenders, [], "正式/他経路のmoduleが er111_pn_* を import している: %s" % offenders)

    def test_er103_does_not_know_trial_and_no_flag_added(self):
        with open(os.path.join(HERE, "er103_proper_noun_alarm_policy_01.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("er111_pn_", src)
        # 委任_04: Production本体にRETが統合されたため`entity_table`引数は存在してよい(Trial moduleへの参照が無いことだけを固定)
        for f in ("er111_pn_entity_table_trial_01.py", "er111_pn_trial_evaluate_01.py"):
            with open(os.path.join(HERE, f), encoding="utf-8") as fh:
                s = fh.read()
            self.assertNotRegex(s, r"(?m)^[A-Z_]*ENABLED\s*=")                # 11-7 flag を作らない
            self.assertNotIn("os.environ", s)
            self.assertNotIn("pol.PROPER_NOUN_ALARM_POLICY_ENABLED =", s)
            self.assertNotIn("upsert", s)

    def test_default_off_no_api_no_side_effect(self):
        # llm未指定=API 0・ファイル書込0。評価functionはtable未指定で副作用なし
        before = set(os.listdir(HERE))
        tb = ret.build_entity_table(["Bertie sang."])
        self.assertEqual(tb.status, "LLM_NOT_CONFIGURED")
        d = decide("Bertie sang.", "Birdie sang.", "Birdie sang.", None)
        self.assertFalse(d.accept)
        self.assertEqual(before, set(os.listdir(HERE)))
        self.assertIsNone(ret.current_table())

    def test_real_llm_has_cost_guard(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            log = os.path.join(td, "u.jsonl")
            open(log, "w").write('{"jpy": 29.5}\n')
            with self.assertRaises(ret.CostCapExceeded):
                ret.llm_ner_real("x", "A", usage_log=log)


if __name__ == "__main__":
    unittest.main()
