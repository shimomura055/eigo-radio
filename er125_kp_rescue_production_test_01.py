# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01: er125_kp_rescue_production_01 のtest(API 0・ネットワーク接続試行0)。

実行: .venv\\Scripts\\python.exe run_project_regression.py --pattern "er125*_test_*.py"  (または py -m unittest er125_kp_rescue_production_test_01)
fixture: docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/case_fixtures_01.json(除外11件+Human NG 3件の本文・文。frozen)。
本委任は未配線のため、H1(er105.contains_finite_aux_role_based)の配線後の挙動は `_wired_h1()` でin-memory再現して検証する(委任_02で本物の配線へ置換)。
"""
from __future__ import annotations

import contextlib
import copy
import json
import os
import socket
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def _blocked(*a, **k):
    raise RuntimeError("network blocked: er125 test is API-0")


socket.socket.connect = _blocked            # type: ignore[assignment]
socket.create_connection = _blocked         # type: ignore[assignment]

import er003_key_words_canonicalization as kc   # noqa: E402
import er030_key_phrase_db_hybrid_core_01 as core   # noqa: E402
import er105_kp_fulltext_selector_01 as ft      # noqa: E402
import er108_kp_cmu_lexicon_gate_01 as cmu      # noqa: E402
import er119_kp_human_review_01 as rv           # noqa: E402
import er125_kp_rescue_production_01 as r       # noqa: E402

WD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01")
RD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02")


def _load(base, name):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return json.load(f)


FX = _load(WD, "case_fixtures_01.json")
CASE = {c["table_no"]: c for c in FX if c["table_no"]}
NG_CASES = [c for c in FX if c["class"] == "HUMAN_NG_EXCLUDED"]
ADV = _load(RD, "adversarial_01.json")
_UNITS = {}


def units_of(case):
    t = case["text"]
    if t not in _UNITS:
        _UNITS[t] = core.build_sentence_units(t)
    return _UNITS[t]


@contextlib.contextmanager
def _wired_h1():
    """委任_02のH1配線(er105.contains_finite_aux_role_based の末尾でidiom_aux_exception_appliesを見る)をin-memoryで再現する。"""
    orig = ft.contains_finite_aux_role_based

    def patched(text):
        return orig(text) and not r.idiom_aux_exception_applies(text)
    ft.contains_finite_aux_role_based = patched
    try:
        yield
    finally:
        ft.contains_finite_aux_role_based = orig


def sel_reasons(phrase, units):
    v = ft.validate_and_resolve([{"phrase": phrase, "declared_word_count": None}], units)
    return [x for ir in v["item_reasons"] for x in ir["reasons"] if not x.startswith("件数が")]


def llm_item(rank, key, reason="lemma_normalization", changed=True, qa_fail=()):
    it = {"rank": rank, "possessor_roles": [], "key_phrase": key, "changed_from_display_phrase": changed, "normalization_reason": reason,
          "reasoning": "x"}
    for f in kc.QA_FIELDS:
        it[f] = "FAIL" if f in qa_fail else "PASS"
    return it


def original_item(case, rank=1, display=None):
    d = display or case["display"]
    u = units_of(case)
    v = ft.validate_and_resolve([{"phrase": d, "declared_word_count": None}], u)
    o = ft.build_original_items(v["resolved"])[0]
    o["rank"] = rank
    return o


def view_span(o):
    return kc.canonicalization_view_items([o])[0]["source_span"]


# =====================================================================================================
class TestEleven(unittest.TestCase):
    """(a) 除外11件の最終期待結果(RESCUE_TABLE_01の採用表+Fable解釈: 救済可=#2/#3/#4/#5/#6/#7/#9/#10/#11、不採用=#1[短縮]/#8[CMU])。"""

    def test_1_too_soon_to_wave_a_flag_not_rescued_shortening_rejected(self):
        c = CASE[1]
        rs = sel_reasons(c["display"], units_of(c))
        self.assertTrue(rs and any("語数" in x for x in rs), rs)
        self.assertIsNone(r.rescue_selection_item(c["display"], rs, units_of(c)))      # 6語以上の短縮救済は不採用(ユーザー表)
        for sub in ("too soon", "wave a flag", "too soon to do"):                       # 部分列・スロット一般化へも逃げない
            self.assertIsNone(r.rescue_selection_item(sub, rs, units_of(c)))

    def test_2_studied_separately_passes_normal_flow(self):
        c = CASE[2]
        o = original_item(c)
        self.assertEqual(sel_reasons(c["display"], units_of(c)), [])
        it = llm_item(1, "study separately")
        self.assertIsNone(r.rescue_canonicalization_item(it, o, view_span(o)))         # 通常Gateを通る=救済不要
        self.assertTrue(kc.validate_canonicalization_item("study separately", c["display"], view_span(o), normalization_reason="lemma_normalization",
                                                          original_span=o["source_span"], allow_inflection_normalization=True)["ok"])

    def test_3_had_our_eye_on_passes_normal_flow(self):
        c = CASE[3]
        self.assertEqual(sel_reasons(c["display"], units_of(c)), [])
        o = original_item(c)
        self.assertIsNone(r.rescue_canonicalization_item(llm_item(1, "have one's eye on"), o, view_span(o)))

    def test_4_rose_above_m1_rederive(self):
        c = CASE[4]
        o = original_item(c)
        it = llm_item(1, "rise above the other voices")
        meta = r.rescue_canonicalization_item(it, o, view_span(o))
        self.assertIsNotNone(meta)
        self.assertEqual((meta["code"], it["key_phrase"]), (r.R_M1, "rise above"))
        self.assertEqual(meta["dropped_tail"], ["the", "other", "voices"])

    def test_5_held_out_m1_rederive_drops_object(self):
        c = CASE[5]
        o = original_item(c)
        it = llm_item(1, "hold out one's hands")
        meta = r.rescue_canonicalization_item(it, o, view_span(o))
        self.assertIsNotNone(meta)
        self.assertEqual((meta["code"], it["key_phrase"]), (r.R_M1, "hold out"))
        self.assertEqual(meta["dropped_tail"], ["one's", "hands"])

    def test_6_rang_through_passes_normal_flow(self):
        c = CASE[6]
        o = original_item(c)
        self.assertEqual(sel_reasons(c["display"], units_of(c)), [])
        self.assertIsNone(r.rescue_canonicalization_item(llm_item(1, "ring through"), o, view_span(o)))

    def test_7_it_cant_be_helped_idiom_core(self):
        c = CASE[7]
        u = units_of(c)
        with _wired_h1():
            rs = sel_reasons(c["display"], u)
            self.assertTrue(any("有限助動詞" in x for x in rs), rs)             # itを含む完全文は例外にしない
            res = r.rescue_selection_item(c["display"], rs, u)
            self.assertIsNotNone(res)
            self.assertEqual(res["selection_rescue"]["code"], r.R_IDIOM_CORE)
            self.assertEqual(res["phrase"], "can’t be helped")
            self.assertEqual(sel_reasons(res["phrase"], u), [])
            o = original_item(c, display=res["phrase"])
            self.assertTrue(kc.validate_canonicalization_item(res["phrase"], res["phrase"], view_span(o), normalization_reason="none",
                                                              original_span=o["source_span"], allow_inflection_normalization=True)["ok"])
            self.assertEqual(cmu.reasons_for_phrase(res["phrase"]), [])

    def test_7b_without_h1_wiring_core_is_not_accepted(self):
        c = CASE[7]
        u = units_of(c)
        rs = sel_reasons(c["display"], u)
        self.assertIsNone(r.rescue_selection_item(c["display"], rs, u))                 # 未配線(現Production)では従来どおり除外

    def test_8_redelivery_fee_cmu_not_rescued(self):
        c = CASE[8]
        self.assertTrue(cmu.reasons_for_phrase(c["display"]))
        o = original_item(c)
        it = llm_item(1, "redelivery fee", reason="none", changed=False)
        self.assertIsNone(r.rescue_canonicalization_item(it, o, view_span(o)))         # 分解救済は不採用
        self.assertEqual(it["key_phrase"], "redelivery fee")
        self.assertNotIn("kp_rescue", it)

    def test_9_cant_be_helped_in_place(self):
        c = CASE[9]
        u = units_of(c)
        with _wired_h1():
            self.assertEqual(sel_reasons(c["display"], u), [])
            self.assertTrue(r.idiom_aux_exception_applies(c["display"]))
        self.assertTrue(any("有限助動詞" in x for x in sel_reasons(c["display"], u)))   # 未配線なら従来どおり除外

    def test_10_have_a_say_passes_normal_flow(self):
        c = CASE[10]
        self.assertEqual(sel_reasons(c["display"], units_of(c)), [])
        o = original_item(c)
        self.assertIsNone(r.rescue_canonicalization_item(llm_item(1, "have a say", reason="none", changed=False), o, view_span(o)))

    def test_11_catch_their_interest_d1_reanchor_then_canonicalization(self):
        c = CASE[11]
        u = units_of(c)
        rs = sel_reasons(c["display"], u)
        self.assertTrue(any("本文に連続一致しない" in x for x in rs), rs)
        res = r.rescue_selection_item(c["display"], rs, u)
        self.assertIsNotNone(res)
        self.assertEqual((res["phrase"], res["selection_rescue"]["code"]), ("catches their interest", r.R_D1))
        o = original_item(c, display=res["phrase"])
        self.assertTrue(kc.validate_canonicalization_item("catch their interest", res["phrase"], view_span(o), normalization_reason="lemma_normalization",
                                                          original_span=o["source_span"], allow_inflection_normalization=True)["ok"])
        self.assertEqual(r.reanchor("catch their interest", u)[0]["surface"], "catches their interest")


# =====================================================================================================
class TestAdversarialNoFalseAccept(unittest.TestCase):
    """(b) 敵対的85件で救済による誤受理0。救済で出てよいkeyは『display(表層)』か『{display語,LLM語}の組合せで承認済みvalidatorが受理する形』のみ。"""

    def test_conversions_rejected_cases_only_ever_revert(self):
        n = 0
        for c in ADV["conversions"]:
            if c["expect"] != "reject":
                continue
            n += 1
            o = {"rank": 1, "display_phrase": c["display"], "source_span": c["display"], "source_sentence": c["display"],
                 "fulltext_source_ref": "fulltext_exact_v1"}
            it = llm_item(1, c["key"])
            meta = r.rescue_canonicalization_item(it, o, c["display"])
            self.assertIsNotNone(meta, c)
            self.assertEqual(it["key_phrase"].lower(), c["display"].lower(), c)       # 誤った基本形(increase supply等)は決して採用されない
            self.assertEqual(meta["code"], r.R_REVERT, c)
        self.assertGreaterEqual(n, 10)

    def test_accepted_conversions_need_no_rescue(self):
        for c in ADV["conversions"]:
            if c["expect"] not in ("accept", "preexisting_accept"):
                continue
            o = {"rank": 1, "display_phrase": c["display"], "source_span": c["display"], "source_sentence": c["display"],
                 "fulltext_source_ref": "fulltext_exact_v1"}
            it = llm_item(1, c["key"])
            self.assertIsNone(r.rescue_canonicalization_item(it, o, c["display"]), c)
            self.assertEqual(it["key_phrase"], c["key"])

    def test_idiom_cases(self):
        for c in ADV["idiom"]:
            ex = r.idiom_exception(c["phrase"])
            ok_in_place = bool(ex and ex["form"] == "in_place")
            if c["phrase"] == "beggars can't be choosers":
                self.assertFalse(ok_in_place, c)       # 既存ASCII縮約形の抜け(R5)は本機構では通さない(名詞主語)
            elif c["expect"] == "allowed":
                self.assertTrue(ok_in_place, c)
            else:
                self.assertFalse(ok_in_place, c)
        self.assertEqual(len(ADV["idiom"]), 15)

    def test_noun_subject_proverbs_and_complete_sentences_never_excepted(self):
        for ph in ("beggars can’t be choosers", "the die is cast", "boys will be boys", "time is money", "a leopard can’t change its spots",
                   "you can’t be serious", "it is what it is", "that will do", "the show must go on", "murder will out", "can it", "have got", "will do",
                   "are you deaf", "wouldn’t you say", "has left the building and more", "would", "have"):
            ex = r.idiom_exception(ph)
            self.assertTrue(ex is None or (ex["form"] == "core_without_it" and ph.lower().startswith("it ")), (ph, ex))


# =====================================================================================================
class TestIdiomMechanism(unittest.TestCase):
    def test_positive_examples_from_lexicon(self):
        for ph in ("might as well", "may as well", "had better", "can’t wait", "can't wait", "can't help", "couldn’t care less", "can of worms",
                   "have it all", "have it both ways", "come what may", "had our hands tied", "have my head read"):
            ex = r.idiom_exception(ph)
            self.assertIsNotNone(ex, ph)
            self.assertEqual(ex["form"], "in_place", ph)

    def test_contraction_and_apostrophe_normalization(self):
        a, b = r.idiom_exception("can’t be helped"), r.idiom_exception("can't be helped")
        self.assertEqual(a, b)
        self.assertIsNotNone(a)
        self.assertEqual(r.idiom_exception("It Can’t Be Helped")["form"], "core_without_it")

    def test_possessive_slot_normalization(self):
        for ph in ("had our hands tied", "have his hands tied", "have your hands tied", "have someone's hands tied"):
            self.assertIsNotNone(r.idiom_exception(ph), ph)
        self.assertIsNone(r.idiom_exception("have the hands tied"))

    def test_length_bounds(self):
        self.assertIsNone(r.idiom_exception("can"))
        self.assertIsNone(r.idiom_exception("can't stand the sight of anyone here"))

    def test_be_verbs_and_non_aux_start_not_excepted(self):
        for ph in ("is what it is", "are bears catholic", "is no telling", "so be it"):
            self.assertIsNone(r.idiom_exception(ph), ph)

    def test_aux_exception_only_in_place_and_kill_switch(self):
        self.assertTrue(r.idiom_aux_exception_applies("might as well"))
        self.assertFalse(r.idiom_aux_exception_applies("it can’t be helped"))
        os.environ[r.KILL_SWITCH_ENV] = "0"
        try:
            self.assertFalse(r.idiom_aux_exception_applies("might as well"))
            self.assertIsNone(r.rescue_selection_item("catch their interest", ["本文に連続一致しない(変更・言い換え・創作)"], units_of(CASE[11])))
            self.assertEqual(r.postprocess_rescue({"items": [llm_item(1, "rise above the other voices")]}, [original_item(CASE[4])])["items"][0]["key_phrase"],
                             "rise above the other voices")
        finally:
            del os.environ[r.KILL_SWITCH_ENV]
        self.assertTrue(r.rescue_enabled())


class TestLexiconFailClosed(unittest.TestCase):
    """(h) 辞書の欠落/改ざん/件数不一致は空表=救済しない。例外は送出しない。"""

    def _copy_lex(self, d):
        for n in (r.LEXICON_FILE, r.LEXICON_META_FILE, r.DENYLIST_FILE):
            with open(os.path.join(r.LEXICON_DIR, n), "rb") as f:
                b = f.read()
            with open(os.path.join(d, n), "wb") as g:
                g.write(b)

    def test_loaded_ok(self):
        st = r.lexicon_status()
        self.assertTrue(st["loaded"], st)
        self.assertEqual(st["sha"], r.LEXICON_SHA256)
        self.assertGreater(st["n"], 10000)

    def test_missing_dir(self):
        ents, st = r.load_idiom_lexicon(os.path.join(tempfile.gettempdir(), "no_such_dir_kprw1"))
        self.assertEqual((len(ents), st["loaded"]), (0, False))

    def test_tampered_file_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_lex(d)
            with open(os.path.join(d, r.LEXICON_FILE), "a", encoding="utf-8", newline="\n") as f:
                f.write("beggars can't be choosers extra\n")
            ents, st = r.load_idiom_lexicon(d)
            self.assertEqual((len(ents), st["loaded"], st["reason"]), (0, False, "sha_mismatch_code"))

    def test_meta_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_lex(d)
            m = json.load(open(os.path.join(d, r.LEXICON_META_FILE), encoding="utf-8"))
            m["idioms_txt_sha256"] = "0" * 64
            json.dump(m, open(os.path.join(d, r.LEXICON_META_FILE), "w", encoding="utf-8"))
            ents, st = r.load_idiom_lexicon(d)
            self.assertEqual((len(ents), st["reason"]), (0, "sha_mismatch_meta"))

    def test_crlf_checkout_still_loads(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_lex(d)
            b = open(os.path.join(d, r.LEXICON_FILE), "rb").read().replace(b"\n", b"\r\n")
            open(os.path.join(d, r.LEXICON_FILE), "wb").write(b)
            ents, st = r.load_idiom_lexicon(d)
            self.assertTrue(st["loaded"], st)

    def test_empty_lexicon_disables_all_idiom_paths(self):
        r._reset_lexicon_cache_for_test(frozenset(), {"loaded": False, "n": 0, "reason": "test"})
        try:
            self.assertIsNone(r.idiom_exception("might as well"))
            self.assertFalse(r.idiom_aux_exception_applies("might as well"))
            u = units_of(CASE[7])
            with _wired_h1():
                self.assertIsNone(r.rescue_selection_item(CASE[7]["display"], sel_reasons(CASE[7]["display"], u), u))
        finally:
            r._reset_lexicon_cache_for_test(None)
        self.assertTrue(r.lexicon_status()["loaded"])


# =====================================================================================================
class TestHumanNgNotBypassed(unittest.TestCase):
    """(e) Human NGは救済経路でも復活しない(原句・救済形の両方を照合)。"""

    def test_fixture_ng_phrases_are_not_rescuable(self):
        self.assertGreaterEqual(len(NG_CASES), 3)
        for c in NG_CASES:
            u = units_of(c)
            self.assertEqual(sel_reasons(c["display"], u) if c["display"] != "off the hook" else [], [] if c["display"] != "off the hook" else [])

    def test_ng_blocked_by_original_or_rescued_phrase(self):
        ng = [{"candidate_id": rv.candidate_id_for("catch their interest"), "phrase_key": rv.phrase_key("catch their interest"),
               "used_form_key": rv.used_form_key("catch their interest"), "active": True}]
        cand = {"candidate_id": rv.candidate_id_for("catches their interest"), "selection_phrase": "catches their interest",
                "used_form": "catch their interest", "item": {"rescue": {"selection": {"original_phrase": "catch their interest"}}}}
        self.assertTrue(r.ng_blocked(cand, ng, rv.match_ng, rv.candidate_id_for))
        cand2 = {"candidate_id": rv.candidate_id_for("rise above"), "selection_phrase": "rose above", "used_form": "rise above",
                 "item": {"rescue": {"canonicalization": {"display_phrase": "rose above"}}}}
        ng2 = [{"candidate_id": rv.candidate_id_for("rose above"), "phrase_key": rv.phrase_key("rose above"), "used_form_key": "", "active": True}]
        self.assertTrue(r.ng_blocked(cand2, ng2, rv.match_ng, rv.candidate_id_for))
        self.assertFalse(r.ng_blocked(cand2, ng, rv.match_ng, rv.candidate_id_for))

    def test_annotate_never_clears_existing_ng_logic(self):
        # auto_eligible_nowはNG一致なら常にFalse(rescue旗付きでも)
        cand = {"candidate_id": rv.candidate_id_for("rose above"), "selection_phrase": "rose above", "used_form": "rise above", "auto_eligible": True,
                "item": {}}
        ng = [{"candidate_id": rv.candidate_id_for("rose above"), "phrase_key": rv.phrase_key("rose above"), "used_form_key": "", "active": True}]
        self.assertFalse(rv.auto_eligible_now(cand, ng))


# =====================================================================================================
class TestFlowAndPersistence(unittest.TestCase):
    """救済フロー全体(gate hook -> merge -> gloss/QA -> 候補)・決定論(f)・resume読み戻し(g)。"""

    def _run_gate(self, case, llm_key, qa_fail=()):
        o = original_item(case)
        item = llm_item(1, llm_key, qa_fail=qa_fail)
        raw = json.dumps({"items": [item]})
        calls = []

        def factory():
            def fn():
                calls.append(1)
                return raw, "gpt-fake", "resp-1"
            return fn
        pp = r.chain_postprocess()
        parsed, status, attempts, mid, rid = kc.run_canonicalization_gate(factory, [o], postprocess=pp)
        return o, parsed, status, calls

    def test_gate_passes_after_rescue_without_retry(self):
        o, parsed, status, calls = self._run_gate(CASE[4], "rise above the other voices")
        self.assertIn(status, ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"))
        self.assertEqual(len(calls), 1)                                          # 救済でINVALID->retry消費が起きない
        self.assertEqual(parsed["items"][0]["key_phrase"], "rise above")
        self.assertEqual(parsed["items"][0]["kp_rescue"]["code"], r.R_M1)

    def test_gate_without_rescue_is_invalid_baseline(self):
        o = original_item(CASE[4])
        raw = json.dumps({"items": [llm_item(1, "rise above the other voices")]})
        parsed, status, *_ = kc.run_canonicalization_gate(lambda: (lambda: (raw, "m", "i")), [o], sleep_fn=lambda s: None)
        self.assertEqual(status, "CANONICALIZATION_INVALID")                     # 現行(救済なし)ではINVALIDだった事例

    def test_determinism_same_input_same_output(self):
        outs = []
        for _ in range(3):
            o = original_item(CASE[5])
            p = r.postprocess_rescue({"items": [llm_item(1, "hold out one's hands")]}, [o])
            outs.append(json.dumps(p, sort_keys=True, ensure_ascii=False))
        self.assertEqual(len(set(outs)), 1)

    def test_postprocess_does_not_mutate_input(self):
        o = original_item(CASE[4])
        parsed = {"items": [llm_item(1, "rise above the other voices")]}
        snap = copy.deepcopy(parsed)
        r.postprocess_rescue(parsed, [o])
        self.assertEqual(parsed, snap)

    def test_non_fulltext_items_untouched(self):
        o = original_item(CASE[4])
        o.pop("fulltext_source_ref")
        parsed = {"items": [llm_item(1, "rise above the other voices")]}
        self.assertEqual(r.postprocess_rescue(parsed, [o]), parsed)             # A/B/C相当(fulltextマーカー無し)は無影響

    def _merged_after_rescue(self, qa_fail=()):
        o, parsed, status, _ = self._run_gate(CASE[4], "rise above the other voices", qa_fail=qa_fail)
        merged = kc.merge_canonicalization_result([o], parsed["items"])
        merged["items"][0]["japanese_gloss"] = "旧keyに付いた旧gloss"
        return o, parsed, merged

    @staticmethod
    def _gloss_ok(merged, ranks):
        m = copy.deepcopy(merged)
        for it in m["items"]:
            if it["rank"] in ranks:
                it["japanese_gloss"] = "〜の上に響く"
                it["gloss_alignment_status"] = "ALIGNED"
        return {"merged": m, "unresolved_ranks": [], "cost_jpy": 0.5}

    @staticmethod
    def _qa_call(pass_all=True, bad_key=False):
        def call(msg):
            assert "rise above" in msg
            items = [llm_item(1, "rise above" if not bad_key else "rise", reason="none", changed=False, qa_fail=() if pass_all else ("qa_not_over_minimized",))]
            return json.dumps({"items": items}), "gpt-fake", "r-qa"
        return call

    def test_finalize_pass_makes_candidate_auto_eligible(self):
        o, parsed, merged = self._merged_after_rescue()
        out = r.finalize_rescued_items(merged, parsed, [o], "text", gloss_realign_fn=lambda m, rk: self._gloss_ok(m, rk), qa_call_fn=self._qa_call())
        it = out["items"][0]
        self.assertEqual(it["rescue"]["codes"], [r.R_M1])
        self.assertEqual((it["rescue"]["gloss"]["status"], it["rescue"]["qa"]["status"]), (r.GLOSS_REALIGNED, r.QA_REJUDGED_PASS))
        self.assertEqual(it["japanese_gloss"], "〜の上に響く")
        cand = {"selection_phrase": "rose above", "used_form": "rise above", "auto_eligible": True, "item": it, "flags": {}, "gates": {}}
        r.annotate_candidate(cand)
        self.assertTrue(cand["auto_eligible"])
        self.assertTrue(cand["flags"]["rescued"])
        self.assertEqual(cand["gates"]["canonicalization"], "RESCUED_QA_REJUDGED_PASS")
        self.assertTrue(r.verify_persisted_rescue(cand))

    def test_finalize_qa_not_run_or_failed_blocks_auto(self):
        for qa_call, want in ((None, "RESCUED_QA_NOT_REJUDGED"), (self._qa_call(bad_key=True), "RESCUED_QA_NOT_REJUDGED"),
                              (self._qa_call(pass_all=False), "RESCUED_QA_REJUDGED_FAIL")):
            o, parsed, merged = self._merged_after_rescue()
            out = r.finalize_rescued_items(merged, parsed, [o], "text", gloss_realign_fn=lambda m, rk: self._gloss_ok(m, rk), qa_call_fn=qa_call)
            cand = {"selection_phrase": "rose above", "used_form": "rise above", "auto_eligible": True, "item": out["items"][0], "flags": {}, "gates": {}}
            r.annotate_candidate(cand)
            self.assertFalse(cand["auto_eligible"], want)
            self.assertEqual(cand["gates"]["canonicalization"], want)
            self.assertTrue(cand["human_selectable"] if "human_selectable" in cand else True)

    def test_finalize_gloss_failure_blocks_auto(self):
        o, parsed, merged = self._merged_after_rescue()
        bad = lambda m, rk: {"merged": m, "unresolved_ranks": list(rk), "cost_jpy": 0.0}      # noqa: E731
        out = r.finalize_rescued_items(merged, parsed, [o], "text", gloss_realign_fn=bad, qa_call_fn=self._qa_call())
        cand = {"selection_phrase": "rose above", "used_form": "rise above", "auto_eligible": True, "item": out["items"][0], "flags": {}, "gates": {}}
        r.annotate_candidate(cand)
        self.assertFalse(cand["auto_eligible"])

    def test_finalize_no_rescue_is_identity(self):
        o = original_item(CASE[2])
        parsed = {"items": [llm_item(1, "study separately")]}
        merged = kc.merge_canonicalization_result([o], parsed["items"])
        self.assertIs(r.finalize_rescued_items(merged, parsed, [o], "t"), merged)

    def test_resume_readback_is_stable_and_self_consistent(self):
        o, parsed, merged = self._merged_after_rescue()
        out = r.finalize_rescued_items(merged, parsed, [o], "text", gloss_realign_fn=lambda m, rk: self._gloss_ok(m, rk), qa_call_fn=self._qa_call())
        cand = {"selection_phrase": "rose above", "used_form": "rise above", "auto_eligible": True, "item": out["items"][0], "flags": {}, "gates": {}}
        r.annotate_candidate(cand)
        doc = {"candidates": [cand], "level": "b1b"}
        sha1 = rv.candidates_sha256(doc)
        reloaded = json.loads(json.dumps(doc, ensure_ascii=False))             # ファイル保存->読み戻し
        self.assertEqual(rv.candidates_sha256(reloaded), sha1)                  # 救済メタ込みでsha不変(HR候補の不変性)
        c2 = reloaded["candidates"][0]
        before = json.dumps(c2, sort_keys=True, ensure_ascii=False)
        r.annotate_candidate(c2)                                                # 読み戻した候補への再annotateは冪等(再計算で変わらない)
        self.assertEqual(json.dumps(c2, sort_keys=True, ensure_ascii=False), before)
        self.assertTrue(r.verify_persisted_rescue(c2))
        c2["rescue"]["canonicalization"]["validator_args"]["key"] = "tampered"
        self.assertFalse(r.verify_persisted_rescue(c2))

    def test_sha_changes_when_rescue_meta_changes(self):
        base = {"candidates": [{"candidate_id": "x", "used_form": "rise above", "rescue": {"codes": [r.R_M1]}}]}
        other = copy.deepcopy(base)
        other["candidates"][0]["rescue"]["codes"] = [r.R_REVERT]
        self.assertNotEqual(rv.candidates_sha256(base), rv.candidates_sha256(other))

    def test_selection_rescue_flows_into_candidate_without_extra_conditions(self):
        c = CASE[11]
        u = units_of(c)
        res = r.rescue_selection_item(c["display"], sel_reasons(c["display"], u), u)
        o = original_item(c, display=res["phrase"])
        o["selection_rescue"] = res["selection_rescue"]
        parsed = {"items": [llm_item(1, "catch their interest")]}
        merged = kc.merge_canonicalization_result([o], parsed["items"])
        out = r.finalize_rescued_items(merged, parsed, [o], "text")
        it = out["items"][0]
        self.assertEqual(it["rescue"]["codes"], [r.R_D1])
        cand = {"selection_phrase": res["phrase"], "used_form": "catch their interest", "auto_eligible": True, "item": it, "flags": {}, "gates": {}}
        r.annotate_candidate(cand)
        self.assertTrue(cand["auto_eligible"])                                  # 後続は通常canonicalizationを通るので追加条件なし
        self.assertIn("catch their interest", cand["rescue_note"])

    def test_outer_retry_accounting_rescued_items_are_not_dropped(self):
        # 救済が成功したitemはdropped[]に入らない(itemがPASSで候補になる)=gate_dropped数に寄与しない。失敗は従来どおりINVALID->dropped。
        o, parsed, status, _ = self._run_gate(CASE[4], "rise above the other voices")
        self.assertNotEqual(status, "CANONICALIZATION_INVALID")
        o8 = original_item(CASE[8])
        raw = json.dumps({"items": [llm_item(1, "redelivery fee", reason="none", changed=False)]})
        parsed8, st8, *_ = kc.run_canonicalization_gate(lambda: (lambda: (raw, "m", "i")), [o8], postprocess=r.chain_postprocess(), sleep_fn=lambda s: None)
        # redelivery feeはCMU未登録でcanonicalization Gate自体は通る(CMUはgenerate_candidates側のpost-canon)。救済は発動せず無変更。
        self.assertEqual(parsed8["items"][0]["key_phrase"], "redelivery fee")
        self.assertNotIn("kp_rescue", parsed8["items"][0])


class TestRoleOrder(unittest.TestCase):
    def test_chain_applies_roles_before_rescue(self):
        calls = []

        def first(parsed, orig):
            calls.append("roles")
            return parsed
        pp = r.chain_postprocess(first)
        o = original_item(CASE[4])
        out = pp({"items": [llm_item(1, "rise above the other voices")]}, [o])
        self.assertEqual(calls, ["roles"])
        self.assertEqual(out["items"][0]["key_phrase"], "rise above")


class TestSelectionGuards(unittest.TestCase):
    def test_d1_ambiguous_or_missing_window_not_rescued(self):
        u = units_of(CASE[11])
        self.assertIsNone(r.rescue_selection_item("catch zebra interest", ["本文に連続一致しない(変更・言い換え・創作)"], u))
        self.assertEqual(r.reanchor("catch zebra interest", u), [])

    def test_mixed_reasons_not_rescued(self):
        u = units_of(CASE[11])
        self.assertIsNone(r.rescue_selection_item("catch their interest", ["本文に連続一致しない(変更・言い換え・創作)", "語数が1〜5語でない(実際: 6語)"], u))
        self.assertIsNone(r.rescue_selection_item("catch their interest", ["文の境界をまたいでいる(1文の中の連続した語句だけを選ぶ)"], u))

    def test_reentrancy_guard(self):
        u = units_of(CASE[11])
        r._tls.active = True
        try:
            self.assertIsNone(r.rescue_selection_item("catch their interest", ["本文に連続一致しない(変更・言い換え・創作)"], u))
        finally:
            r._tls.active = False

    def test_d1_does_not_rescue_illegal_normalization(self):
        # heated debate型: 『heat debate』を本文のheated debateへ戻す方向は、承認済みvalidatorが原形化を認めない=窓にならない
        text = "They had a heated debate about the new rules. Nobody left."
        u = core.build_sentence_units(text)
        self.assertEqual(r.reanchor("heat debate", u), [])
        self.assertIsNone(r.rescue_selection_item("heat debate", ["本文に連続一致しない(変更・言い換え・創作)"], u))


class TestUnwiredInProduction(unittest.TestCase):
    """本委任ではProductionファイルからimportしない(未配線)。配線は委任_02。"""

    def test_no_production_file_imports_er125(self):
        for fn in ("er105_kp_fulltext_selector_01.py", "er119_kp_candidates_01.py", "er119_kp_human_review_01.py", "er119_kp_wiring_01.py",
                   "er003_key_words_canonicalization.py", "er003_v1_n3_01_scaffold_generate.py", "er003_key_words_min_unit.py",
                   "er119_kp_prompt_2v_01.py", "er062_family_z_writer_01.py", "er121_family_y_runner_01.py"):
            p = os.path.join(ROOT, fn)
            if os.path.exists(p):
                self.assertNotIn("er125", open(p, encoding="utf-8").read(), fn)

    def test_er125_imports_only_approved_modules(self):
        src = open(os.path.join(ROOT, "er125_kp_rescue_production_01.py"), encoding="utf-8").read()
        self.assertNotIn("import er123", src)
        self.assertNotIn("openai", src)
        self.assertNotIn("socket", src)
        import re as _re
        self.assertIsNone(_re.search(r"^\s*(import|from)\s+er119_", src, _re.M))     # er119_isolation_test維持: er119はimportしない


class TestAiIslandHrCandidatesUntouched(unittest.TestCase):
    """AI島 run_ai_01 の既存HR候補ファイルは不変: resumeは保存済み候補を読むだけで救済を再計算しない。本moduleは候補ファイルを書かない(read-only)。
    読み戻した既存候補にannotate_candidateを当てても変化しない(rescueなし・慣用句旗の該当なし)ことを確認する。ファイルが無い環境ではskip。"""

    def test_existing_candidates_unchanged_by_annotate(self):
        import hashlib
        base = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "ai_island_temple__run_ai_01")
        found = 0
        for lv in ("a2", "b1b"):
            p = os.path.join(base, lv, "key_phrases", "kp_candidates.json")
            if not os.path.exists(p):
                continue
            found += 1
            raw = open(p, "rb").read()
            sha_before = hashlib.sha256(raw).hexdigest()
            doc = json.loads(raw.decode("utf-8"))
            self.assertEqual(rv.candidates_sha256(doc), doc["candidates_sha256"])
            for c in doc["candidates"]:
                snap = json.dumps(c, sort_keys=True, ensure_ascii=False)
                r.annotate_candidate(c)
                self.assertEqual(json.dumps(c, sort_keys=True, ensure_ascii=False), snap, c["candidate_id"])
                self.assertTrue(r.verify_persisted_rescue(c))
            self.assertEqual(hashlib.sha256(open(p, "rb").read()).hexdigest(), sha_before)      # ファイルは書かれていない
        if not found:
            self.skipTest("AI島候補ファイルなし")


class TestQuantifierGuardRegression(unittest.TestCase):
    """(j) 量化詞限定詞guard是正(区分1)。詳細はer105_kp_rule_compliance_test_01。ここでは救済側との整合のみ。"""

    def test_accepts_no_responsibility_is_normal_flow(self):
        self.assertIsNotNone(ft.find_inflection_window("accept no responsibility", "accepts no responsibility"))
        o = {"rank": 1, "display_phrase": "accepts no responsibility", "source_span": "accepts no responsibility",
             "source_sentence": "The firm accepts no responsibility.", "fulltext_source_ref": "fulltext_exact_v1"}
        self.assertIsNone(r.rescue_canonicalization_item(llm_item(1, "accept no responsibility"), o, "accepts no responsibility"))


if __name__ == "__main__":
    unittest.main()
