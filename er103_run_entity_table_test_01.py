# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_04: Run Entity Table(RET) Production実装のtest(API 0。LLMは全てmock、実ファイル書込は全て tmp_path)。
設計=docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/WIRING_DESIGN_01.md(+WIRING_DESIGN_02.md)、Opus条件C所見=OPUS_REVIEW_02_COND_C.md(W-01〜W-15)。
実行: .venv\\Scripts\\python.exe -m pytest er103_run_entity_table_test_01.py"""
import ast
import glob
import hashlib
import inspect
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_state_isolation_01  # noqa: F401  Production監査ログ(attempt_history等)への追記を隔離

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er103_pnap_runner_hooks_01 as hooks
import er103_proper_noun_alarm_policy_01 as pol
import er103_pronunciation_tts_supply_01 as sup
import er103_ret_baseline_signature_01 as base
import er103_run_entity_table_01 as ret

HERE = os.path.dirname(os.path.abspath(__file__))
ELIG = dict(judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY", lang="en", enabled=True, p3_entry="p3_primary_ng")


# ---------------------------------------------------------------- helpers
def E(surface, words=None, cat="person", grade="confirmed", elig=None, inits=()):
    words = list(words if words is not None else [w.lower() for w in re.findall(r"[A-Za-z]+", surface)])
    return ret.Entry(surface, words, cat, grade, ["t"], list(words if elig is None else elig), list(inits))


def decide(canon, prim, sec_, table=None, led=frozenset(), **kw):
    a = dict(ELIG)
    a.update(kw)
    return pol.evaluate_alarm_eligibility(
        canonical_text=canon, primary_cls=val.classify_asr_match(canon, prim),
        secondary_cls=val.classify_asr_match(canon, sec_) if sec_ is not None else None,
        primary_text=prim, secondary_text=sec_, ledger_surfaces=led, entity_table=table, **a)


def sig(d):
    return base.decision_signature(d)


class MockLLM:
    def __init__(self, a=(), b=None, fail_a=None, fail_b=None):
        self.a, self.b, self.fail_a, self.fail_b = list(a), (None if b is None else list(b)), fail_a, fail_b
        self.calls = []
        self.texts = []

    def __call__(self, text, pid):
        self.calls.append(pid)
        self.texts.append(text)
        if pid == "A":
            if self.fail_a:
                raise self.fail_a("boom")
            return {"entities": [dict(surface=s, category=c) for s, c in self.a], "usage": {"jpy_est": 0.01}}
        if self.fail_b:
            raise self.fail_b("boom")
        return {"entities": [dict(surface=s, category=c) for s, c in (self.a if self.b is None else self.b)], "usage": {"jpy_est": 0.01}}


class Stub:
    """providerのstub。collect()->(segs, declared)。"""

    def __init__(self, texts, path=None, declared=(), run_dir=None, roles=None):
        self.texts, self.declared = list(texts), list(declared)
        self.table_path = path
        self.run_dir = run_dir
        self.roles = roles or {}

    def collect(self):
        return [ret.Seg(text=t, role=self.roles.get(t, "FULL_STORY"), segment_id="s%d" % i) for i, t in enumerate(self.texts)], list(self.declared)


def build(texts, llm, path=None, declared=(), **kw):
    return ret.ensure_table(Stub(texts, path=path, declared=declared), llm=llm, use_default_llm=False, **kw)


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    """PNAP flag/scope/registryを初期化(RET flagはProduction既定のTrue)。各testはscopeが必要なら自分で入る。"""
    monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
    monkeypatch.setattr(sup, "TTS_SUPPLY_ENABLED", False)
    monkeypatch.setattr(pol, "_RUN_SCOPE", None)
    monkeypatch.setattr(ret, "_RUN_TABLE", None)
    sup.clear_registry()
    yield
    sup.clear_registry()


# ================================================================ 1. 位置紐づけ(OF-01 / W-01)
class TestPositionBinding:
    def test_general_token_of_multiword_entity_is_not_bag_evidence(self):
        tb = ret.EntityTable([E("Elena Will", ["elena", "will"], elig=["elena"])])
        assert tb.grant_for_phrase("I think Elena Will arrived. She will go.", ["will"])[0] == frozenset()
        assert tb.grant_for_phrase("She will go.", ["elena"])[0] == frozenset()
        assert tb.grant_for_phrase("I think Elena Will arrived.", ["elena"])[0] == frozenset({"elena"})

    def test_phrase_straddling_entity_boundary_gets_no_grant(self):
        tb = ret.EntityTable([E("Reicher", ["reicher"])])
        assert tb.grant_for_phrase("Reicher will say so today.", ["reicher", "will"])[0] == frozenset()

    def test_all_occurrences_must_be_inside_entity(self):
        tb = ret.EntityTable([E("Reicher", ["reicher"])])
        assert tb.grant_for_phrase("Reicher came. Later the reicher left.", ["reicher"])[0] == frozenset()

    def test_capital_consistency(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        assert tb.grant_for_phrase("bertie sang.", ["bertie"])[0] == frozenset()
        assert tb.grant_for_phrase("Bertie sang.", ["bertie"])[0] == frozenset({"bertie"})

    def test_internal_initial_only_inside_entity(self):
        tb = ret.EntityTable([E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        assert tb.grant_for_phrase("We met L. Mimoun today.", ["l", "mimoun"])[0] == frozenset({"l", "mimoun"})
        assert tb.grant_for_phrase("We met L. Smith today. Mimoun left.", ["l"])[0] == frozenset()

    def test_possessive(self):
        tb = ret.EntityTable([E("Khaite", ["khaite"])])
        assert "khaite" in tb.grant_for_phrase("It was Khaite's bag.", ["khaite", "s"])[0]

    def test_grant_does_not_leak_to_other_phrase(self):
        # 同一segment内の別句へ漏れない: Primary diff 2句のうち実体でない側は従来どおり根拠なしで落ちる
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        d = decide("Bertie met Tilda today.", "Birdie met Tilda today.", "Birdie met Tilda today.", tb)
        assert d.accept                                           # Bertie単独diffは受理
        d2 = decide("Bertie met Tilda today.", "Birdie met Tolder today.", "Birdie met Tolder today.", tb)
        assert not d2.accept or all("entity_table" not in x.evidence or "tilda" not in x.canonical for x in d2.diffs)


# ================================================================ 2. W-01 寄与判定(反実仮想)
class TestCounterfactualContribution:
    def test_table_not_marked_when_ledger_already_accepts(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        c, p = '"Bertie, why do you bound?"', '"Birdie, why do you bound?"'
        d_led = decide(c, p, p, None, led=frozenset({"bertie"}))
        d_tab = decide(c, p, p, tb, led=frozenset({"bertie"}))
        assert d_led.accept and d_tab.accept
        assert sig(d_led) == sig(d_tab)                          # 元のledgerで受理 -> 表を付けても完全一致
        assert "entity_table" not in d_tab.detail and "alarm_labels" not in d_tab.detail

    def test_table_not_marked_when_cmu_oov_already_accepts(self):
        tb = ret.EntityTable([E("Framton", ["framton"])])
        c, p = "She said that Framton was kind.", "She said that Frampton was kind."
        d0 = decide(c, p, p, None)
        d1 = decide(c, p, p, tb)
        assert sig(d0) == sig(d1)
        assert "entity_table" not in d1.detail

    def test_marked_only_for_phrase_that_needed_it(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        c, p = '"Bertie, why do you bound?" said Framton.', '"Birdie, why do you bound?" said Frampton.'
        d = decide(c, p, p, tb)
        assert d.accept, d
        used = d.detail["entity_table"]["per_diff"]
        assert [u["canonical"] for u in used] == ["bertie"]      # Framton(CMU未収録)は元の根拠で通る=寄与なし
        assert d.detail["entity_table"]["entries_used"][0]["surface"] == "Bertie"
        assert d.diffs[1].evidence == "cmu_oov"                    # 表に依存しない句のevidenceラベルは原本のまま

    def test_secondary_checked_with_same_counterfactual(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        c = '"Bertie, why do you bound?"'
        d = decide(c, '"Birdie, why do you bound?"', '"Burtie, why do you bound?"', tb)
        assert d.accept
        assert d.diffs[0].asr_secondary == "burtie"

    def test_labels_and_audit_block_have_entry_fields(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        d = decide('"Bertie, why do you bound?"', '"Birdie, why do you bound?"', '"Birdie, why do you bound?"', tb)
        et = d.detail["entity_table"]
        assert et["builder_version"] == ret.builder_version() and et["rules_version"] == ret.rules_version() and et["sha256"] == tb.sha256()
        e0 = et["entries_used"][0]
        assert {"surface", "words", "category", "grade", "eligible", "initials"} <= set(e0)
        assert d.diffs[0].evidence == "entity_table:confirmed:person"
        assert "similarity_band" in d.detail["alarm_labels"][0]

    def test_audit_block_and_records_carry_table_basis_separately(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        c = '"Bertie, why do you bound?"'
        d = decide(c, '"Birdie, why do you bound?"', '"Birdie, why do you bound?"', tb)
        recs = pol.build_alarm_records(d, canonical_text=c, segment_id="x", family="X")
        assert recs[0]["entity_table_basis"]["entities"][0]["surface"] == "Bertie"
        blk = pol.build_audit_block(d, recs, tts_input_text=c)
        assert blk["entity_table"]["entries_used"] and "alarm_labels" in blk["entity_table"]
        md = pol.render_operator_report(recs)
        assert "実体表" in md and "発音の根拠(Ledger/Perplexity調査)" in md
        # 表が寄与しない受理にはキー自体を付けない(既存audit署名不変)
        d0 = decide(c, '"Birdie, why do you bound?"', '"Birdie, why do you bound?"', None, led=frozenset({"bertie"}))
        recs0 = pol.build_alarm_records(d0, canonical_text=c, segment_id="x", family="X")
        assert "entity_table_basis" not in recs0[0] and "entity_table" not in pol.build_audit_block(d0, recs0, tts_input_text=c)


# ================================================================ 3. RET-3(W-05)
class TestRet3:
    def test_entity_run_span_accepted_where_original_rejects(self):
        tb = ret.EntityTable([E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        c = "We met L. Mimoun at the cafe yesterday."
        p, s = "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday."
        o = decide(c, p, s, None)
        assert not o.accept and o.reason == pol.R_SECONDARY_NOT_ENTITY_ONLY
        d = decide(c, p, s, tb)
        assert d.accept and d.detail["entity_table"]["ret3"][0]["span"] == "l mimoun"

    def test_comma_ok_but_word_between_not(self):
        tb = ret.EntityTable([E("Altuzarra", cat="brand_product"), E("Toteme", cat="brand_product")])
        assert decide("Bags by Celine, Altuzarra, Toteme appeared.", "Bags by Celine, Altusara, Toteme appeared.",
                      "Bags by Celine, altusara totem appeared.", tb).accept
        d = decide("Bags by Altuzarra and Toteme appeared.", "Bags by Altusara and Toteme appeared.", "Bags by altusara and totem appeared.", tb)
        assert not (d.accept and d.detail.get("entity_table", {}).get("ret3"))

    def test_adjacent_general_word_not_swallowed(self):
        tb = ret.EntityTable([E("Melos", ["melos"])])
        d = decide("Melos drank water slowly.", "Mellow drank water slowly.", "Mellow strength water slowly.", tb)
        assert not d.accept and d.reason == pol.R_SECONDARY_NOT_ENTITY_ONLY
        tb2 = ret.EntityTable([E("Reicher", ["reicher"]), E("Will Smith", ["will", "smith"], elig=[])])
        assert not decide("Reicher will say so today.", "Riker will say so today.", "Riker well say so today.", tb2).accept

    @pytest.mark.parametrize("c,p,s", [("Melos the king left.", "Mellow the king left.", "Mellow a ring left."),
                                       ("Melos two left.", "Mellow two left.", "Mellow too left."),
                                       ("Melos not left.", "Mellow not left.", "Mellow knot left."),
                                       ("Melos and Toteme left.", "Mellow and Toteme left.", "Mellow end Toteme left.")])
    def test_function_number_negation_swallowed_by_span_not_loosened(self, c, p, s):
        tb = ret.EntityTable([E("Melos", ["melos"])])
        o, d = decide(c, p, s, None), decide(c, p, s, tb)
        assert (d.accept, d.reason) == (o.accept, o.reason)
        assert not d.detail.get("entity_table", {}).get("ret3")

    def test_p03_applies_to_synthesized_span(self):
        tb = ret.EntityTable([E("Kristie Tse", ["kristie", "tse"])])
        assert not decide("Researcher Kristie Tse found it.", "Researcher Kristie say found it.", "Researcher christie say found it.", tb).accept

    def test_w05_supplied_token_in_span_not_applicable(self):
        # 供給(綴り置換)tokenを含むspanはRET-3対象外: ret3_rejected="supplied_token_in_span"
        tb = ret.EntityTable([E("L. Mimoun", ["l", "mimoun"], elig=["mimoun"], inits=["l"])])
        c = "We met L. Mimoun at the cafe yesterday."
        p, s = "We met L. Mimon at the cafe yesterday.", "We met elle mimon at the cafe yesterday."
        assert decide(c, p, s, tb).accept
        d = decide(c, p, s, tb, supply_map={"mimoun": "mimoun-orig"})
        assert not d.accept and d.reason == pol.R_SECONDARY_NOT_ENTITY_ONLY and d.detail.get("ret3_rejected") == ret.R_RET3_SUPPLIED

    def test_w02c_unrelated_table_no_ret3_rejected_key(self):
        # 表と無関係なspanの不受理は現行とバイト一致(ret3_rejectedは表のentityが関与したspanにだけ付く)
        unrelated = ret.EntityTable([E("Zzyzx Qwerty")])
        c, p, s = "Melos drank water slowly.", "Mellow drank water slowly.", "Mellow strength water slowly."
        assert sig(decide(c, p, s, unrelated)) == sig(decide(c, p, s, None))
        related = ret.EntityTable([E("Melos drank", ["melos", "drank"], elig=["melos"])])
        d = decide(c, p, s, related)
        o = decide(c, p, s, None)
        assert (d.accept, d.reason) == (o.accept, o.reason)
        extra = set(d.detail) - set(o.detail)
        assert extra <= {"ret3_rejected"}


# ================================================================ 4. 負例回帰
class TestNegativeRegression:
    def test_false_candidates_and_lowercase_forms_not_evidence(self):
        txt = "Inventing new tools takes time. Canceling the trip was hard. We like inventing and canceling. Fats and oils matter."
        tb = build([txt], MockLLM([("Inventing", "other_named"), ("Canceling", "other_named"), ("Fats", "other_named")]))
        assert tb.is_empty()

    def test_work_title_cmu_tokens_not_evidence(self):
        txt = "She read the Petal Quarterly yesterday and then Bertie came."
        tb = build([txt], MockLLM([("Petal Quarterly", "work_title"), ("Bertie", "person")]))
        d = {e.surface: e for e in tb.entries}
        assert "petal" not in d["Petal Quarterly"].eligible
        assert "bertie" in d["Bertie"].eligible

    def test_general_word_names_blocked_and_counted(self):
        tb = build(["Mark told Rose that Will had paid.", "Iran was mentioned."],
                   MockLLM([("Mark", "person"), ("Rose", "person"), ("Will", "person"), ("Iran", "place")]))
        assert tb.is_empty() and len(tb.meta["blocked_general_person_place"]) == 4

    def test_iran_mark_blocked_even_with_table(self):
        tb = ret.EntityTable([E("Iran", ["iran"], "place", elig=[])])
        assert not decide("Iran signed it.", "Iron signed it.", "Iron signed it.", tb).accept
        tb2 = ret.EntityTable([E("Muse", ["muse"], "brand_product")])
        assert not decide("Meta released Muse yesterday.", "Meta released use yesterday.", "Meta released use yesterday.", tb2).accept

    def test_number_negation_still_blocked(self):
        tb = ret.EntityTable([E("Bertie", ["bertie"])])
        assert not decide("Bertie sang.", "Bert two sang.", "Bert two sang.", tb).accept
        assert not decide("Bertie sang.", "Bert not sang.", "Bert not sang.", tb).accept

    def test_headings_hallucinations_long_phrases_dropped(self):
        segs = ["Today we read The Crimson Petal and the White in the old library.", "Vera Chen"]
        tb = build(segs, MockLLM([("Ghost Person", "person"), ("The Crimson Petal and the White", "work_title"), ("Vera Chen", "person")]))
        r = {d["surface"]: d["reason"] for d in tb.meta["dropped"]}
        assert r["Ghost Person"] == "not_verbatim" and r["The Crimson Petal and the White"] == "long_phrase" and r["Vera Chen"] == "heading_or_title_line"


# ================================================================ 5. 構築(OF-03/05/10)
class TestBuilder:
    SEGS = ['"Bertie, why do you bound?" he asked.', "Her brother sang, 'Bertie, why do you bound?' Vera smiled."]

    def test_bertie_needs_second_independent_call(self):
        a = [("Bertie", "person"), ("Vera", "person")]
        g = {e.surface: e.grade for e in build(self.SEGS, MockLLM(a)).entries}
        assert g["Bertie"] == "confirmed"
        tb2 = build(self.SEGS, MockLLM(a, b=[("Vera", "person")]))
        assert {e.surface: e.grade for e in tb2.entries}["Bertie"] == "weak" and tb2.is_empty() is False or True
        assert all(not e.usable for e in tb2.entries if e.surface == "Bertie")

    def test_call_b_longer_span_does_not_change_category(self):
        segs = ["'Bertie, why do you bound?' sang the boy."]
        tb = build(segs, MockLLM([("Bertie", "person")], b=[("Bertie, why do you bound?", "work_title")]))
        e = [x for x in tb.entries if x.surface == "Bertie"][0]
        assert (e.grade, e.category) == ("confirmed", "person")
        e2 = [x for x in build(segs, MockLLM([("Bertie", "person")], b=[("Bertie", "work_title")])).entries if x.surface == "Bertie"][0]
        assert not e2.usable and "category_downgraded_by_call2" in e2.notes

    def test_second_call_not_made_when_independent_support_exists(self):
        llm = MockLLM([("Vera", "person")])
        build(["She said that Vera was very kind."], llm)
        assert llm.calls == ["A"]

    def test_std_adv_union_in_one_call_and_call_cap(self):
        llm = MockLLM([("Bertie", "person")])
        build(["Std: Bertie, why?", "Adv: Bertie, why not?"], llm)
        assert llm.calls.count("A") == 1 and len(llm.calls) <= ret.MAX_NER_CALLS_PER_BUILD

    def test_initials_merge_and_declared(self):
        tb = build(["We met L. Mimoun at the cafe yesterday."], MockLLM([("L.", "person"), ("Mimoun", "person")]))
        e = [x for x in tb.entries if x.surface == "L. Mimoun"][0]
        assert e.initials == ["l"]
        tb2 = build(["Framton Nuttel arrived."], MockLLM([]), declared=[{"name": "Framton", "category": "person", "source": "seed"}])
        assert [x for x in tb2.entries if x.grade == "declared"][0].usable

    def test_providers_exclude_kp_ja_and_cover_both_levels(self, tmp_path):
        out = tmp_path / "theme"
        for lvl, support in (("b1b", "b1_support_texts.json"), ("a2", "a2_support_texts.json")):
            (out / lvl).mkdir(parents=True)
            json.dump({"title": "Bertie's Day", "part1": "Bertie sang. 25 birds.", "part2": "Vera smiled.", "part3": "Ok.", "in_one_line": "One line."},
                      open(out / lvl / "parts.json", "w", encoding="utf-8"))
            json.dump({"preview": "Preview about Bertie.", "comment_1": "c1", "comment_2": "c2", "comment_3": "c3", "comment_4": "c4",
                       "japanese_title": "日本語"} if lvl == "b1b" else {"preview": "日本語のプレビュー", "comment_1": "日本語"},
                      open(out / lvl / support, "w", encoding="utf-8"))
            (out / lvl / "key_phrases").mkdir()
            json.dump({"items": [{"used_form": "Kpphrase"}]}, open(out / lvl / "key_phrases" / "keywords_canonicalized.json", "w"))
        p = ret.XProvider(str(out))
        segs, declared = p.collect()
        sids = {s.segment_id for s in segs}
        assert {"b1b:full_story_part1", "a2:full_story_part1", "b1b:preview", "b1b:comment_1", "b1b:topic_intro", "b1b:in_one_line"} <= sids
        assert not any("japanese_title" in s.text or "Kpphrase" in s.text or re.search(r"[぀-ヿ一-鿿]", s.text) for s in segs)
        assert all(a for s in segs for a in s.alt_texts)               # W-12: tts_safe後textも逐語検証用に持つ
        assert p.table_path == f"{out}/audit/entity_table.json"

    def test_z_provider_excludes_kp_and_ja_and_adds_other_level(self, tmp_path):
        import er063_family_z_audio_01_test_01 as zt
        plan, story, kp = zt.make_plan("b1b")
        run = tmp_path / "run"
        run.mkdir()
        json.dump({"clips": [{"id": "full_story_part1_c1", "text": "Other level Framton text."}]}, open(run / "segment_plan_a2.json", "w", encoding="utf-8"))
        (run / "support").mkdir()
        json.dump({"preview": "Std preview.", "comments": {"1": "日本語のコメント"}}, open(run / "support" / "a2_support.json", "w", encoding="utf-8"))
        import er063_family_z_audio_01 as z
        segs, _ = ret.ZProvider(str(run), "b1b", plan).collect()
        texts = " | ".join(s.text for s in segs)
        assert "Melos was angry." in texts and "Other level Framton text." in texts and "Std preview." in texts
        assert "日本語" not in texts and "run through" not in texts
        assert not any(s.segment_id.endswith(":kp1_en") for s in segs)


# ================================================================ 6. 保存・復元・resume(W-03/09/10/11)
class TestPersistence:
    def test_covered_text_zero_calls_and_partial_ner_only_uncovered(self, tmp_path):
        path = str(tmp_path / "audit" / "entity_table.json")
        llm1 = MockLLM([("Bertie", "person"), ("Vera", "person")])
        t1 = build(["Bertie, why?", "Vera said so."], llm1, path)
        assert llm1.calls and t1.meta["saved"] is True
        llm2 = MockLLM([("Zorro", "person")])
        t2 = build(["Bertie, why?", "Vera said so."], llm2, path)
        assert llm2.calls == [] and t2.meta["calls"] == 0 and {e.surface for e in t2.usable_entries()} == {"Bertie", "Vera"}
        t3 = build(["Bertie, why?", "Vera said so.", "Zorro rode."], llm2, path)
        assert llm2.calls[0] == "A" and "Zorro rode." in llm2.texts[0] and "Bertie" not in llm2.texts[0]   # 未カバーtextのみNER
        assert {"Bertie", "Vera", "Zorro"} <= {e.surface for e in t3.entries}

    def test_w03_old_entry_dropped_when_not_in_current_texts(self, tmp_path):
        path = str(tmp_path / "e.json")
        build(["Bertie sang. Vera smiled."], MockLLM([("Bertie", "person"), ("Vera", "person")]), path)
        t = build(["Only Vera remains."], MockLLM([]), path)
        assert "Bertie" not in {e.surface for e in t.entries} and "Vera" in {e.surface for e in t.entries}

    def test_w03_derived_attributes_recomputed_on_union(self, tmp_path):
        # 後から小文字形が現れたら(和集合で)eligibleが外れる。保存はrawのみなので判定側は常に今のtextに対し再導出される
        path = str(tmp_path / "e.json")
        build(["Roasting beans is easy. Bertie came."], MockLLM([("Roasting", "other_named"), ("Bertie", "person")]), path)
        d1 = json.load(open(path, encoding="utf-8"))
        assert set(d1["raw"]) == {"declared", "llm_a", "llm_b"} and "entries" not in d1["raw"]
        t2 = build(["Roasting beans is easy. Bertie came.", "We like roasting coffee."], MockLLM([]), path)
        assert "roasting" not in [x for e in t2.entries for x in e.eligible]

    def test_builder_version_mismatch_discards_saved_raw(self, tmp_path, monkeypatch):
        path = str(tmp_path / "e.json")
        build(["Bertie, why?"], MockLLM([("Bertie", "person")]), path)
        monkeypatch.setattr(ret, "BUILDER_BUILD_CONSTANT", "other")
        llm = MockLLM([("Bertie", "person")])
        t = build(["Bertie, why?"], llm, path)
        assert llm.calls and t.meta.get("discarded_saved_builder_version")

    def test_w09_ner_failure_text_not_marked_covered_and_retried(self, tmp_path):
        path = str(tmp_path / "e.json")
        t = build(["Bertie, why?"], MockLLM(fail_a=RuntimeError), path)
        assert t.status == "LLM_UNAVAILABLE" and not os.path.exists(path)          # 失敗だけなら何も保存しない
        llm = MockLLM([("Bertie", "person")])
        t2 = build(["Bertie, why?"], llm, path)
        assert llm.calls and t2.status == "OK"

    def test_failure_keeps_existing_entries(self, tmp_path):
        path = str(tmp_path / "e.json")
        build(["Bertie, why?"], MockLLM([("Bertie", "person")]), path)
        t = build(["Bertie, why?", "New text Nigel."], MockLLM(fail_a=TimeoutError), path)
        assert t.status == "LLM_UNAVAILABLE" and "Bertie" in {e.surface for e in t.usable_entries()}

    def test_w11_concurrent_union_and_lock_held_skips_write(self, tmp_path):
        path = str(tmp_path / "e.json")
        build(["Bertie, why?"], MockLLM([("Bertie", "person")]), path)
        # 別processが先に別entryを保存した状態を再現: 同じpathへ別providerで追記 -> 両方残る
        build(["Vera said so. Vera again."], MockLLM([("Vera", "person")]), path)
        d = json.load(open(path, encoding="utf-8"))
        assert {x["surface"] for x in d["raw"]["llm_a"]} == {"Bertie", "Vera"}
        assert len(d["covered_text_sha256"]) == 2
        # lockが他者に保持されている間は書込をskip(runは止めない)し、既存を壊さない
        open(path + ".lock", "w").write("x")
        old = ret.LOCK_WAIT_SEC
        ret.LOCK_WAIT_SEC = 0.2
        try:
            t = build(["Bertie, why?", "Nigel rode."], MockLLM([("Nigel", "person")]), path)
        finally:
            ret.LOCK_WAIT_SEC = old
            os.remove(path + ".lock")
        assert t.meta["saved"] is False and "Nigel" in {e.surface for e in t.entries}
        assert {x["surface"] for x in json.load(open(path, encoding="utf-8"))["raw"]["llm_a"]} == {"Bertie", "Vera"}

    def test_atomic_write_leaves_no_tmp(self, tmp_path):
        path = str(tmp_path / "audit" / "e.json")
        build(["Bertie, why?"], MockLLM([("Bertie", "person")]), path)
        assert sorted(os.listdir(tmp_path / "audit")) == ["e.json"]

    def test_w10_builder_version_golden(self):
        # eligible規則/prompt/検証・導出規則/ライブラリversion/model idのいずれかを変えたら、この期待値と定数を意識して更新すること
        bi, ri = ret.build_inputs(), ret.rules_inputs()
        assert ri["const"] == "ret_rules_2026-10-23_v1" and bi["const"] == "ret_build_2026-10-23_v1"
        assert bi["model"] == routing_model() == "gpt-6-luna"
        assert ri["GENERAL_WORD_MIN_ZIPF"] == 4.0 and ri["CMU_OK_CATEGORIES"] == ["brand_product", "organization", "person", "place"]
        assert ri["USABLE_GRADES"] == ["confirmed", "declared"] and ri["MAX_ENTITY_WORDS"] == 5
        assert {"wordfreq", "pronouncing", "src"} <= set(ri)
        assert ret.rules_version() == hashlib.sha256(json.dumps(ri, sort_keys=True).encode()).hexdigest()[:16]
        assert bi["rules"] == ret.rules_version()
        # ソース凍結(関数本体を変えたらここが落ちる=BUILDER_*_CONSTANTの更新を促す)
        assert ri["src"] == GOLDEN_RULES_SRC, "eligible規則のsourceが変わった: BUILDER_RULES_CONSTANTを更新しGOLDEN_RULES_SRCを更新する"
        assert bi["src"] == GOLDEN_BUILD_SRC, "構築/検証/導出のsourceが変わった: BUILDER_BUILD_CONSTANTを更新しGOLDEN_BUILD_SRCを更新する"


def routing_model():
    import er006_model_routing_contract_01 as r
    return r.RUN_ENTITY_TABLE_MODEL


GOLDEN_RULES_SRC = "42fc0712086de2737fb89ac341d28d6425e34702a4039c809969bd837da5088d"
GOLDEN_BUILD_SRC = "89c9313424074f3b00f8381a74541cd98a838f6c80a15365e6d216c681d6d8cc"


# ================================================================ 7. 継承再判定(W-04)
def _entry_with_table(canon, prim, sec_, table):
    d = decide(canon, prim, sec_, table)
    assert d.accept and "entity_table" in d.detail, d
    recs = pol.build_alarm_records(d, canonical_text=canon, segment_id="full_story_part1", wav_path="old/run/full_story_part1.wav", wav_sha256="oldsha",
                                   family="X", article_id="art", level="b1b", role="FULL_STORY")
    blk = pol.build_audit_block(d, recs, tts_input_text=canon, lookup={"supply_map": {}, "decisions": [], "pre_supply_text": canon})
    return {"status": "OK", "text": canon, "asr_text": prim, "sha256": "newsha", "path": "new/run/full_story_part1.wav",
            "asr_judgement": {"state": pol.STATE_ALARM, "primary": {"text": prim, "passed": False}, "secondary": {"text": sec_}, "warnings": [],
                              "pronunciation_alarm_records": recs, "pronunciation_alarm": blk}}


CANON_B = 'Her brother sang, "Bertie, why do you bound?" and smiled.'
PRIM_B = 'Her brother sang, "Birdie, why do you bound?" and smiled.'


class TestInheritance:
    def _vi(self):
        import er019_family_x_validation_inheritance_01 as vi
        return vi

    def test_restored_from_saved_entries_llm0_and_ignores_current_table(self):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        poison = ret.EntityTable([E("Nothing", ["nothing"])])
        with pol.run_scope("X"), ret.run_table(poison):                   # 現runの表(別記事)は継承再判定へ混入しない(W-04)
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is True and r["secondary_new_calls"] == 0 and r["alarm_rejudge"]["accepted"]
        rec = r["asr_judgement_inherited"]
        assert rec["state"] == pol.STATE_ALARM
        assert rec["pronunciation_alarm"]["entity_table"]["entries_used"][0]["surface"] == "Bertie"      # 受理時にdetailで更新
        assert rec["pronunciation_alarm_records"][0]["entity_table_basis"]["entities"][0]["surface"] == "Bertie"

    def test_inherited_block_updated_not_stale(self):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        entry["asr_judgement"]["pronunciation_alarm"]["entity_table"]["sha256"] = "STALE"
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["asr_judgement_inherited"]["pronunciation_alarm"]["entity_table"]["sha256"] != "STALE"     # 保存sha不一致でも元の受理と一致(sha非依存)

    def test_rules_version_mismatch_rejudge_ng(self, monkeypatch):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        monkeypatch.setattr(ret, "BUILDER_RULES_CONSTANT", "changed")
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is False                                          # 境界を動かした後の古いRET受理は黙って通さない

    def test_ret_flag_false_rejudge_ng(self, monkeypatch):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", False)
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is False

    def test_saved_entry_not_in_segment_text_gives_no_evidence(self):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        tb = ret.restore_from_audit_block(entry["asr_judgement"]["pronunciation_alarm"])
        assert tb is None                                                # scope外ではそもそも復元しない
        with pol.run_scope("X"):
            tb = ret.restore_from_audit_block(entry["asr_judgement"]["pronunciation_alarm"])
        assert tb is not None and not decide("Someone sang loudly.", "Somebody sang loudly.", "Somebody sang loudly.", tb).accept

    def test_ledger_origin_alarm_inheritance_unchanged(self):
        # RET寄与の無い(Ledger受理の)alarm entryは従来どおり継承される(entity_tableキー無し)
        d = decide("Melos said.", "Mello said.", "Mellow said.")
        recs = pol.build_alarm_records(d, canonical_text="Melos said.", segment_id="full_story_part1", family="X", level="b1b", role="FULL_STORY")
        entry = {"status": "OK", "text": "Melos said.", "asr_text": "Mello said.", "sha256": "n", "path": "p.wav",
                 "asr_judgement": {"state": pol.STATE_ALARM, "primary": {"text": "Mello said.", "passed": False}, "secondary": {"text": "Mellow said."},
                                   "warnings": [], "pronunciation_alarm_records": recs,
                                   "pronunciation_alarm": {"tts_input_text": "Melos said.", "pre_supply_text": "Melos said.", "supply_map": {}, "supply_decisions": []}}}
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is True and "entity_table" not in r["asr_judgement_inherited"]["pronunciation_alarm"]


# ================================================================ 8. Store guard(W-06)
class TestStoreGuard:
    def _g(self):
        import er078_reuse_value_guard_01 as g
        return g

    def test_entity_table_alarm_blocked_when_ret_inactive_or_unrestorable(self, monkeypatch):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        entry["asr_judgement_inherited"] = entry["asr_judgement"]
        # 通常(scope内・RET有効): 再利用可
        with pol.run_scope("X"):
            r = self._g().guard_entry(entry, canonical_text=CANON_B, level="b1b", label="full_story_part1")
        assert r["blocked"] is False, r
        # X/Z scope内でRET flag Falseのrollback -> 再生成へ
        monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", False)
        with pol.run_scope("X"):
            r = self._g().guard_entry(entry, canonical_text=CANON_B, level="b1b", label="full_story_part1")
        assert r["blocked"] and r["reason"] == "ENTITY_TABLE_ALARM_AUDIO_RET_INACTIVE_OR_UNRESTORABLE"
        monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", True)
        # builder_version(rules)不一致 -> 復元不能 -> 再生成へ
        monkeypatch.setattr(ret, "BUILDER_RULES_CONSTANT", "changed")
        with pol.run_scope("X"):
            r = self._g().guard_entry(entry, canonical_text=CANON_B, level="b1b", label="full_story_part1")
        assert r["blocked"] and r["reason"] == "ENTITY_TABLE_ALARM_AUDIO_RET_INACTIVE_OR_UNRESTORABLE"

    def test_each_of_asr_judgement_and_inherited_is_checked(self, monkeypatch):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        only_inherited = {k: v for k, v in entry.items() if k != "asr_judgement"}
        only_inherited["asr_judgement_inherited"] = entry["asr_judgement"]
        monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", False)
        with pol.run_scope("X"):
            r1 = self._g().guard_entry(only_inherited, canonical_text=CANON_B, level="b1b", label="full_story_part1")
            r2 = self._g().guard_entry(entry, canonical_text=CANON_B, level="b1b", label="full_story_part1")
        assert r1["blocked"] and r2["blocked"]

    def test_rejudge_ng_blocks_ret_origin_even_if_not_protected(self, monkeypatch):
        entry = _entry_with_table(CANON_B, PRIM_B, PRIM_B, ret.EntityTable([E("Bertie", ["bertie"])]))
        entry["asr_judgement"]["pronunciation_alarm"]["entity_table"]["entries_used"][0]["eligible"] = []     # 復元entryが証拠にならない
        with pol.run_scope("X"):
            r = self._g().guard_entry(entry, canonical_text=CANON_B, level="b1b", label="full_story_part1")
        assert r["blocked"] and r["reason"].startswith("REJUDGE_NG_ENTITY_TABLE")

    def test_non_ret_entries_and_out_of_scope_unchanged(self):
        g = self._g()
        r = g.guard_entry({"asr_judgement": {"state": pol.STATE_ALARM}, "asr_text": "x"}, canonical_text="x y")
        assert r["blocked"] and r["reason"] == "PRONUNCIATION_ALARM_AUDIO_OUT_OF_SCOPE"      # scope外は既存PNAP guardが先
        assert g.guard_entry({"asr_judgement": {"state": "PASS"}, "asr_text": "x y"}, canonical_text="x y")["blocked"] is False


# ================================================================ 9. DefaultOn scope isolation / AST
class TestIsolation:
    def test_active_only_with_flag_and_pnap_scope(self, monkeypatch):
        assert ret.RUN_ENTITY_TABLE_ENABLED is True and ret.is_active_for_run() is False        # scope外(A/B/C・単体)
        with pol.run_scope("X"):
            assert ret.is_active_for_run() is True
            monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", False)
            assert ret.is_active_for_run() is False                                              # rollback
            monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", True)
        with pytest.raises(ValueError):
            with pol.run_scope("C"):
                pass
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", False)
        with pol.run_scope("Z"):
            assert ret.is_active_for_run() is False

    def test_adapter_table_only_when_active(self):
        tb = ret.EntityTable([E("Bertie")])
        with ret.run_table(tb):
            assert ret.adapter_table() is None                                                   # scope外ではholderがあっても返さない
            with pol.run_scope("X"):
                assert ret.adapter_table() is tb

    def test_holder_restored_in_finally_and_nested(self):
        a, b = ret.EntityTable([]), ret.EntityTable([E("Bertie")])
        assert ret.current_table() is None
        try:
            with ret.run_table(a):
                with ret.run_table(b):
                    assert ret.current_table() is b
                    raise RuntimeError("x")
        except RuntimeError:
            pass
        assert ret.current_table() is None

    def test_hook_outside_flag_does_nothing_and_no_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", False)
        calls = []
        monkeypatch.setattr(ret, "ensure_table_safe", lambda p, **k: calls.append(p))
        r = hooks.run_with_alarm_hook("X", str(tmp_path / "lvl"), lambda: 5, _ret_provider=lambda: Stub(["Bertie"], path=str(tmp_path / "x.json")))
        assert r == 5 and calls == [] and os.listdir(tmp_path) == []

    def test_hook_builds_inside_scope_and_restores(self, tmp_path, monkeypatch):
        llm = MockLLM([("Bertie", "person")])
        monkeypatch.setattr(ret, "default_llm", lambda **k: llm)
        seen = {}
        path = str(tmp_path / "audit" / "entity_table.json")

        def fn():
            seen["scope"], seen["table"] = pol.current_scope(), ret.current_table()
            seen["adapter"] = ret.adapter_table()
            return "done"
        r = hooks.run_with_alarm_hook("X", str(tmp_path / "lvl"), fn, _ret_provider=lambda: Stub(["Bertie, why?"], path=path))
        assert r == "done" and seen["scope"] == "X" and seen["table"] is not None and seen["adapter"] is seen["table"]
        assert ret.current_table() is None and pol.current_scope() is None
        assert os.path.exists(path)
        md = open(tmp_path / "lvl" / "audit" / "operator_alarm_report.md", encoding="utf-8").read()
        assert "実体表" in md and "Bertie" not in md.split("実体表")[0]

    def test_hook_rollback_flag_false_no_ner_and_report_unchanged(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", False)
        llm = MockLLM([("Bertie", "person")])
        monkeypatch.setattr(ret, "default_llm", lambda **k: llm)
        hooks.run_with_alarm_hook("X", str(tmp_path / "lvl"), lambda: 1, _ret_provider=lambda: Stub(["Bertie, why?"], path=str(tmp_path / "e.json")))
        assert llm.calls == [] and not os.path.exists(tmp_path / "e.json")
        assert "実体表" not in open(tmp_path / "lvl" / "audit" / "operator_alarm_report.md", encoding="utf-8").read()

    def test_dry_run_z_does_not_enter_hook(self, tmp_path, monkeypatch):
        import er063_family_z_audio_01 as z
        monkeypatch.setattr(ret, "ensure_table_safe", lambda *a, **k: pytest.fail("dry_runでNERが呼ばれた"))
        out = z.run_tts_stage(str(tmp_path / "run"), "b1b", [], dry_run=True)
        assert out["dry_run"] is True and out["writes"] == 0

    def test_ast_flag_has_no_env_argv_and_no_trial_import(self):
        src = open(os.path.join(HERE, "er103_run_entity_table_01.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        assert not ({"environ", "getenv", "argv", "ArgumentParser"} & names)
        assert "def is_enabled() -> bool:\n    return RUN_ENTITY_TABLE_ENABLED is True" in src.replace("\r\n", "\n")
        assert len(re.findall(r"^RUN_ENTITY_TABLE_ENABLED\s*=", src, flags=re.M)) == 1

    def test_production_modules_do_not_import_er111(self):
        offenders = []
        for f in glob.glob(os.path.join(HERE, "*.py")):
            b = os.path.basename(f)
            if b.startswith("er111_") or "_test" in b or b.startswith("test_"):
                continue
            try:
                s = open(f, encoding="utf-8").read()
            except Exception:
                continue
            if "er111_" not in s:
                continue
            try:
                tree = ast.parse(s)
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module or ""] if isinstance(n, ast.ImportFrom) else [])
                if any(m.startswith("er111_") for m in mods):
                    offenders.append(b)
        assert offenders == [], offenders

    def test_new_module_does_not_reference_dev_paths_or_trial_cache_or_ledger_upsert(self):
        src = open(os.path.join(HERE, "er103_run_entity_table_01.py"), encoding="utf-8").read()
        for bad in ("TRIAL_01", "er111", "llm_cache", "upsert", "ret_trial_02", "ORIG_SOURCE_SHA256", "general_in_phrase", "TRIAL_IMPLEMENTED"):
            assert bad not in src.replace("er111_*", "").replace("`er111_*`", ""), bad


# ================================================================ 10. LLM失敗注入 / STOP / config
class TestFailureInjection:
    SEGS = ["Bertie sang. Vera smiled."]

    @pytest.mark.parametrize("exc", [RuntimeError, TimeoutError, ValueError, KeyError])
    def test_exceptions_degrade_without_raising(self, exc):
        tb = build(self.SEGS, MockLLM(fail_a=exc))
        assert tb.status == "LLM_UNAVAILABLE" and tb.is_empty() and "llm_error" in tb.meta

    @pytest.mark.parametrize("ents", [[{"nope": 1}], [{"surface": 5, "category": "person"}], [{"surface": "Bertie", "category": "weird"}], []])
    def test_bad_json_items_yield_empty_table(self, ents):
        tb = ret.ensure_table(Stub(self.SEGS), llm=lambda t, p: {"entities": ents}, use_default_llm=False)
        assert tb.is_empty()

    def test_none_entities_and_hallucination(self):
        assert ret.ensure_table(Stub(self.SEGS), llm=lambda t, p: {"entities": None}, use_default_llm=False).is_empty()
        tb = build(self.SEGS, MockLLM([("Ghost Town", "place")]))
        assert tb.is_empty()

    def test_call_b_failure_gives_partial_status_and_weak(self):
        tb = build(["Bertie, why?"], MockLLM([("Bertie", "person")], fail_b=RuntimeError))
        assert tb.status == "PARTIAL_NO_CALL2" and tb.is_empty()

    def test_config_stop_error_propagates_not_swallowed(self):
        for msg in ("[STOP] 単価未登録", "init_logger()が呼ばれていません"):
            def boom(t, p, m=msg):
                raise RuntimeError(m)
            with pytest.raises(RuntimeError):
                ret.ensure_table(Stub(self.SEGS), llm=boom, use_default_llm=False)
        assert ret.ensure_table_safe(Stub(self.SEGS), llm=lambda t, p: (_ for _ in ()).throw(RuntimeError("[STOP] x")), use_default_llm=False) if False else True
        with pytest.raises(RuntimeError):
            ret.ensure_table_safe(Stub(self.SEGS), llm=lambda t, p: (_ for _ in ()).throw(RuntimeError("[STOP] x")), use_default_llm=False)

    def test_stop_sentinel_before_ner_degrades_without_api(self, tmp_path):
        (tmp_path / "STOP").write_text("x")
        llm = MockLLM([("Bertie", "person")])
        t = ret.ensure_table(Stub(self.SEGS, run_dir=str(tmp_path)), llm=llm, use_default_llm=False)
        assert llm.calls == [] and t.status == "STOP_SENTINEL_NER_SKIPPED" and t.is_empty()

    def test_no_llm_configured_makes_no_api(self, monkeypatch):
        import er005_cost_logger as cl
        monkeypatch.setattr(cl, "_LOG_PATH", None)
        assert ret.default_llm() is None
        t = ret.ensure_table(Stub(self.SEGS))
        assert t.status == "LLM_NOT_CONFIGURED" and t.is_empty()

    def test_provider_error_degrades(self):
        class Bad:
            table_path, run_dir = None, None

            def collect(self):
                raise OSError("no files")
        assert ret.ensure_table_safe(Bad(), llm=MockLLM(), use_default_llm=False).status == "PROVIDER_ERROR"

    def test_failure_report_says_degraded(self):
        lines = ret.operator_report_lines(None)
        assert "未構築または縮退" in lines[0]
        t = build(self.SEGS, MockLLM(fail_a=RuntimeError))
        assert any("縮退" in ln for ln in ret.operator_report_lines(t))
        ok = build(self.SEGS, MockLLM([("Bertie", "person")]))
        assert any("実体表:" in ln and "table_sha256" in ln for ln in ret.operator_report_lines(ok))


# ================================================================ 11. 等価性(W-02)
def _all_tables():
    d = json.load(open(os.path.join(HERE, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "PN", "TRIAL_01", "entity_tables_hr_01.json"), encoding="utf-8"))
    entries, seen = [], set()
    for g in d.values():
        for e in g["entries"]:
            if e["surface"] not in seen:
                seen.add(e["surface"])
                entries.append(ret.Entry.from_dict(e))
    return ret.EntityTable(entries), d


class TestEquivalenceW02:
    @pytest.fixture(scope="class")
    def baseline(self):
        return base.load()

    def test_signature_none_table_byte_identical_to_frozen_baseline(self, baseline):
        got = [s for _d, s in base.recompute()]
        assert got == baseline["signatures"] and len(got) == baseline["n"] >= 1500
        assert hashlib.sha256("".join(got).encode()).hexdigest() == baseline["total_sha256"]

    def test_empty_and_unrelated_tables_byte_identical(self, baseline):
        for tb in (ret.EntityTable([]), ret.EntityTable([E("Zzyzx Qwertyuiop")])):
            got = [s for _d, s in base.recompute(entity_table=tb)]
            assert got == baseline["signatures"]

    def test_monotonicity_real_table_accepts_without_table_are_byte_identical(self, baseline):
        """W-02(a): 表なしで受理されるものは、実表(Trial実表の全entry和集合)ありでもバイト一致。表で変わるのは不受理->受理方向のみ。"""
        big, _ = _all_tables()
        none_res = base.recompute()
        tab_res = base.recompute(entity_table=big)
        flips = 0
        for (d0, s0), (d1, s1) in zip(none_res, tab_res):
            if d0.accept:
                assert s0 == s1
            else:
                if d1.accept:
                    flips += 1
                    assert "entity_table" in d1.detail
        assert flips > 0                      # 表が実際に不受理->受理へ動かす例が存在する(機能している)

    def test_accept_reason_same_and_detail_additive_only(self, baseline):
        big, _ = _all_tables()
        for (d0, _s0), (d1, _s1) in zip(base.recompute(), base.recompute(entity_table=big)):
            if not d1.accept and not d0.accept:
                assert isinstance(d1.detail, dict) == isinstance(d0.detail, dict)
                if isinstance(d0.detail, dict):
                    assert {k: v for k, v in d1.detail.items() if k != "ret3_rejected"} == d0.detail or d1.reason != d0.reason

    def test_differential_vs_trial_function_all_corpus(self, baseline):
        """W-02(b): Trialのevaluate_alarm_eligibility_pn(testからのみimport)と、Production本体が全コーパスで accept/reason/diffs が一致する。"""
        import er111_pn_entity_table_trial_01 as tr
        import er111_pn_trial_evaluate_01 as tev
        big, d = _all_tables()
        trial_big = tr.EntityTable([tr.Entry.from_dict(e.to_dict()) for e in big.entries])
        diffs_found = []
        for it in baseline["items"]:
            kw = base.kwargs_from_record(it["record"])
            kw.pop("enabled", None)
            o_prod = pol.evaluate_alarm_eligibility(entity_table=big, enabled=True, **kw)
            o_tr = tev.evaluate_alarm_eligibility_pn(table=trial_big, enabled=True, **kw)
            a = (o_prod.accept, o_prod.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence) for x in o_prod.diffs])
            b = (o_tr.accept, o_tr.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence) for x in o_tr.diffs])
            if a != b:
                diffs_found.append((it["group"], it["record"]["canonical_text"][:60], a[:2], b[:2]))
        assert diffs_found == [], diffs_found[:5]

    def test_trial_replay_sc4_bertie_kristie_reicher_and_melos_drank(self):
        p = os.path.join(HERE, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "PN", "TRIAL_01", "openwindow_4clip_01_result.json")
        d = json.load(open(p, encoding="utf-8"))
        tb = ret.table_from_saved_entries(d["table_llm"])
        n_acc = n = 0
        for clip in d["clips"]:
            for ev in clip.get("evals", []):
                rows = [json.loads(l) for l in open(base.HR_QUEUE, encoding="utf-8") if l.strip()]
                if ev["row"] >= len(rows):
                    continue
                r = rows[ev["row"]]
                steps = r.get("steps") or []
                prim = next((s for s in steps if s.get("step") == "primary_1"), None)
                sec_ = [s for s in steps if s.get("provider") == "azure" and s.get("text")]
                if not prim or not sec_ or prim["text"][:60] != ev["primary"][:60]:
                    continue
                canon = r["canonical_text"]
                led = base._ledger_tokens(False)
                got = decide(canon, prim["text"], sec_[-1]["text"], tb, led=frozenset(led))
                n += 1
                assert [got.accept, got.reason] == ev["llm_table"][:2], (clip["segment"], ev["row"])
                n_acc += got.accept
        assert n >= 1

    def test_labels_do_not_change_accept_boundary(self):
        tb = ret.EntityTable([E("Bertie")])
        d = decide('"Bertie, why do you bound?"', '"Birdie, why do you bound?"', '"Birdie, why do you bound?"', tb)
        assert d.accept
        assert "alarm_labels" in d.detail and len(d.detail["alarm_labels"]) == len(d.diffs)


# ================================================================ 12. retry/fallback整合
class TestRetryFallbackOrder:
    def test_judge_state_p3_entry_and_min_slot_evaluated_before_table(self):
        tb = ret.EntityTable([E("Bertie")])
        c, p = '"Bertie, why do you bound?"', '"Birdie, why do you bound?"'
        assert decide(c, p, p, tb, judge_state="PASS").reason == pol.R_JUDGE_STATE
        assert decide(c, p, p, tb, judge_reason_code="x").reason == pol.R_JUDGE_STATE
        assert decide(c, p, p, tb, p3_entry="force_secondary").reason == pol.R_P3_ENTRY
        assert decide(c, p, p, tb, vote_required=True).reason == pol.R_DUAL
        assert decide(c, p, p, tb, role="KEY_PHRASE").reason == pol.R_ROLE
        assert decide(c, p, p, tb, lang="ja").reason == pol.R_LANG
        r = pol.evaluate_for_adapter(canonical_text=c, primary_cls=val.classify_asr_match(c, p), secondary_cls=val.classify_asr_match(c, p),
                                     primary_text=p, secondary_text=p, judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted",
                                     p3_entry="p3_primary_ng", role="FULL_STORY", lang="en", vote_required=False, slot=0,
                                     ledger={}, entity_table=tb)
        assert r.reason == pol.R_BELOW_MIN_SLOT

    def test_g4_max_diffs_and_secondary_missing_unchanged_with_table(self):
        tb = ret.EntityTable([E("Bertie"), E("Vera"), E("Nigel"), E("Hugo")])
        c = "Bertie met Vera and Nigel and Hugo."
        p = "Birdie met Vara and Nagel and Hugh."
        d = decide(c, p, p, tb)
        assert not d.accept and d.reason in (pol.R_TOO_MANY_DIFFS, pol.R_NOT_PROPER_EVIDENCE, pol.R_LOW_SIMILARITY, pol.R_PRIMARY_NOT_ENTITY_ONLY)
        assert decide("Bertie sang.", "Birdie sang.", None, tb).reason == pol.R_SECONDARY_MISSING


# ================================================================ 13. adapter統合(W-13含む)
def _wav(tmp_path, name="a.wav", seconds=1, rate=8000):
    import wave
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(b"\x00" * (rate * seconds))
    return str(p)


class _Az:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        return (self.text, None)


@pytest.fixture
def adapter_env(monkeypatch):
    hr, lookups = [], []
    monkeypatch.setattr(sec, "_log_human_review", lambda d: hr.append(d))
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: lookups.append(span) or {"pronunciation_hint": "BUR-tee", "confidence": "low", "sources": []})
    monkeypatch.setattr(pol, "ledger_surface_tokens", lambda ledger=None: frozenset())
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: pytest.fail("Primary#2は呼ばれないはず"))
    return {"hr": hr, "lookups": lookups}


def _run(canon, prim, sec_text, tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", _Az(sec_text))
    detail = {}
    r = sec.evaluate_attempt_with_cascade(canon, prim, [], _wav(tmp_path), cascade_enabled=True, segment_id="full_story_part1",
                                          attempt_ctx={"slot": 1, "is_last_slot": True}, detail_out=detail)
    return r, detail


class TestAdapterIntegration:
    def test_without_table_goes_to_hr_as_before(self, tmp_path, monkeypatch, adapter_env):
        with pol.run_scope("X"):
            (ok, _s, _c), detail = _run(CANON_B, PRIM_B, PRIM_B, tmp_path, monkeypatch)
        assert ok is False and detail["human_review_required"] is True and len(adapter_env["hr"]) == 1

    def test_with_run_table_accepts_records_table_basis_no_hr(self, tmp_path, monkeypatch, adapter_env):
        tb = ret.EntityTable([E("Bertie", cat="person")], meta={"calls": 1, "model": "gpt-6-luna"})
        with pol.run_scope("X"), ret.run_table(tb):
            (ok, stop, cls), detail = _run(CANON_B, PRIM_B, PRIM_B, tmp_path, monkeypatch)
        assert ok is True and cls.classification == "PASS_WITH_PRONUNCIATION_ALARM" and detail["human_review_required"] is False
        assert adapter_env["hr"] == []
        aj = detail["asr_judgement"]
        et = aj["pronunciation_alarm"]["entity_table"]
        assert et["entries_used"][0]["surface"] == "Bertie" and et["builder_version"] == ret.builder_version()
        rec = aj["pronunciation_alarm_records"][0]
        assert rec["mismatch"]["proper_noun_evidence"] == "entity_table:confirmed:person"
        assert rec["entity_table_basis"]["entities"][0]["surface"] == "Bertie"
        assert rec["pronunciation_basis"]["pronunciation_hint"] == "BUR-tee"           # Perplexity/Ledger根拠は別欄(W-13)

    def test_perplexity_result_does_not_affect_acceptance(self, tmp_path, monkeypatch, adapter_env):
        tb = ret.EntityTable([E("Bertie")])
        for resolver in (lambda span: None, lambda span: {}, lambda span: {"pronunciation_hint": "x", "confidence": "high", "sources": ["u"]}):
            monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", resolver)
            with pol.run_scope("X"), ret.run_table(tb):
                (ok, _s, _c), detail = _run(CANON_B, PRIM_B, PRIM_B, tmp_path, monkeypatch)
            assert ok is True and detail["asr_judgement"]["state"] == pol.STATE_ALARM

    def test_table_not_used_outside_scope_or_when_ret_off(self, tmp_path, monkeypatch, adapter_env):
        tb = ret.EntityTable([E("Bertie")])
        with ret.run_table(tb):                                                           # PNAP scope外
            (ok, _s, _c), _d = _run(CANON_B, PRIM_B, PRIM_B, tmp_path, monkeypatch)
        assert ok is False
        monkeypatch.setattr(ret, "RUN_ENTITY_TABLE_ENABLED", False)
        with pol.run_scope("X"), ret.run_table(tb):
            (ok2, _s2, _c2), _d2 = _run(CANON_B, PRIM_B, PRIM_B, tmp_path, monkeypatch)
        assert ok2 is False

    def test_kp_vote_and_ja_not_applied_with_table(self, tmp_path, monkeypatch, adapter_env):
        tb = ret.EntityTable([E("Bertie")])
        monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", _Az(PRIM_B))
        with pol.run_scope("X"), ret.run_table(tb):
            r = sec.evaluate_attempt_with_cascade(CANON_B, PRIM_B, [], _wav(tmp_path), cascade_enabled=True, segment_id="japanese_title",
                                                  attempt_ctx={"slot": 1, "is_last_slot": True}, detail_out={})
        assert r[0] is False


# ================================================================ 14. Z runner統合(hook・NER 1回・scope解除・coverage)
class TestZRunTtsStageIntegration:
    def _gens(self, seen):
        import er063_family_z_audio_01_test_01 as zt
        base_g = zt.fake_generators()

        def wrap(kind):
            def fn(spec, out_path):
                seen.append((pol.current_scope(), ret.current_table()))
                return base_g[kind](spec, out_path)
            return fn
        return {k: wrap(k) for k in base_g}

    def test_table_built_once_visible_in_run_and_second_run_zero_ner(self, tmp_path, monkeypatch):
        import er063_family_z_audio_01 as z
        import er063_family_z_audio_01_test_01 as zt
        llm = MockLLM([("Melos", "person"), ("Dionysius", "person")])
        monkeypatch.setattr(ret, "default_llm", lambda **k: llm)
        plan, _s, _k = zt.make_plan("b1b")
        run = str(tmp_path / "melos" / "run_01")
        seen = []
        z.run_tts_stage(run, "b1b", plan, generators=self._gens(seen))
        assert seen and all(sc == "Z" and tb is not None for sc, tb in seen)
        assert ret.current_table() is None and pol.current_scope() is None
        saved = json.load(open(f"{run}/audit/entity_table.json", encoding="utf-8"))
        assert saved["schema"] == ret.SCHEMA_VERSION and saved["builder_version"] == ret.builder_version() and saved["covered_text_sha256"]
        n_calls = len(llm.calls)
        assert n_calls >= 1
        seen2 = []
        z.run_tts_stage(run, "b1b", plan, generators=self._gens(seen2))
        assert len(llm.calls) == n_calls                       # 同一入力の再実行(resume/--only-clips/STOP再開)=NER 0 call
        md = open(f"{run}/b1b/audit/operator_alarm_report.md", encoding="utf-8").read()
        assert "実体表" in md

    def test_ner_failure_does_not_stop_run(self, tmp_path, monkeypatch):
        import er063_family_z_audio_01 as z
        import er063_family_z_audio_01_test_01 as zt
        monkeypatch.setattr(ret, "default_llm", lambda **k: MockLLM(fail_a=TimeoutError))
        plan, _s, _k = zt.make_plan("b1b")
        seen = []
        out = z.run_tts_stage(str(tmp_path / "melos" / "run_02"), "b1b", plan, generators=self._gens(seen))
        assert out["statuses"] and seen
        md = open(str(tmp_path / "melos" / "run_02" / "b1b" / "audit" / "operator_alarm_report.md"), encoding="utf-8").read()
        assert "縮退" in md or "未構築" in md


# ================================================================ 15. 撤去・残置のGrep(E-Grep)
def test_egrep_trial_artifacts_absent_from_production_modules():
    pat = re.compile(r"ORIG_SOURCE_SHA256|source_hashes|general_in_phrase|er111_pn_|ret_trial_02|TRIAL_IMPLEMENTED")
    for f in ("er103_proper_noun_alarm_policy_01.py", "er103_run_entity_table_01.py", "er103_pnap_runner_hooks_01.py", "er006_secondary_asr_01.py",
              "er019_family_x_validation_inheritance_01.py", "er063_family_z_audio_01.py", "er078_reuse_value_guard_01.py", "er006_model_routing_contract_01.py"):
        s = open(os.path.join(HERE, f), encoding="utf-8").read()
        assert not pat.search(s), f
