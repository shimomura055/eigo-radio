# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01: er123_kp_rescue_dev_01 のDEV test(API 0。遮断harness下で実行)。

固定する性質(前回Opus M1/M6/R4 + 今回の設計の歯止め):
  - RulePatchは『Productionへ入れる場合の差分案』をin-memoryで当てるだけで、exit後にProductionの関数/表を完全に元へ戻す(Production不変)
  - 非提案語形を作らない(hoped->hop)。再導出の語は{display語, LLM提案語}のみ
  - 否定・程度語(too/not/never/no/only…)を落として被演算子を残す短縮をしない(意味反転の禁止)
  - 救済内のvalidator呼出は最終Gateと同一引数(allow_inflection_normalization=True, original_span, role_ok_poss)
  - lexical have/has/hadと完了形・慣用のauxを区別。法助動詞は区別しない(例外は辞書見出しの核のみ)
  - Human NGは復活しない / CMU未登録語は代替合格にしない / 主語で始まる完全文は慣用句例外にしない
  - X/Y/Z共通核(family非依存のvalidator)、A/B/Cは対象外
実行: $env:PYTHONPATH="netblock_harness_01"; py -m pytest er123_kp_rescue_dev_01_test_01.py -q
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er123_kp_rescue_dev_01 as m   # noqa: E402

kc, ft, cmu = m.kc, m.ft, m.cmu
EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02", "rescue_eval_07.json")


# ---------------------------------------------------------------- Production不変 / 既定OFF
def test_rule_patch_restores_production_state():
    before = (kc._contains_finite_auxiliary, ft._token_pair_ok, dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR),
              ft._GUARD_DET, ft._guard_ok)
    with m.RulePatch(**m.TIER2_PATCH):
        assert kc._contains_finite_auxiliary is not before[0]          # パッチ中は差し替わっている(効果の測定用)
        assert "rang" in ft._AMBIGUOUS_IRREGULAR or "rang" in ft._PAST_ONLY_IRREGULAR
    after = (kc._contains_finite_auxiliary, ft._token_pair_ok, dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR),
             ft._GUARD_DET, ft._guard_ok)
    assert before[0] is after[0] and before[1] is after[1] and before[2] == after[2] and before[3] == after[3]
    assert before[4] == after[4] and before[5] is after[5]


def test_default_off_current_production_behaviour_unchanged():
    # パッチ外(=Production現行)では従来どおり除外される(DefaultOffIsolation)
    assert kc._contains_finite_auxiliary("have a say") is True
    assert m.gate_check("study separately", "studied separately", "studied separately")["ok"] is False
    assert m.gate_check("ring through", "rang through", "rang through")["ok"] is False
    assert "rang" not in ft._PAST_ONLY_IRREGULAR and "rang" not in ft._AMBIGUOUS_IRREGULAR


def test_patch_flags_are_independent_and_minimal():
    with m.RulePatch(adverb=True):
        assert m.gate_check("study separately", "studied separately", "studied separately")["ok"] is True
        assert m.gate_check("ring through", "rang through", "rang through")["ok"] is False      # past未指定なら通らない
        assert kc._contains_finite_auxiliary("have a say") is True                              # aux未指定なら変わらない
    with m.RulePatch(past=True):
        assert m.gate_check("ring through", "rang through", "rang through")["ok"] is True
    with m.RulePatch(aux=True):
        assert kc._contains_finite_auxiliary("have a say") is False


# ---------------------------------------------------------------- M1: 非提案語形を作らない / 三重検査
def test_forward_inflection_rejects_wrong_lemma():
    assert m.inflects_to("hope", "hoped") and not m.inflects_to("hop", "hoped")
    assert m.inflects_to("study", "studied") and not m.inflects_to("stud", "studied")
    assert m.inflects_to("plan", "planned") and not m.inflects_to("plane", "planned")
    assert m.inflects_to("ring", "rang") and m.inflects_to("hold", "held")


def test_adverb_tier_rejects_wrong_lemma_even_if_cmu_registered():
    # `hop`はCMU実在語・_verb_base_candidates(hoped)にも含まれるが、前方生成一致で拒否(adverb tierの三重検査)
    with m.RulePatch(adverb=True, quant=True):
        assert m.gate_check("hop quietly", "hoped quietly", "hoped quietly")["ok"] is False
        assert m.gate_check("hope quietly", "hoped quietly", "hoped quietly")["ok"] is True


def test_rederive_m1_uses_only_display_or_llm_tokens():
    r = m.rederive_m1("hoped for", "hope for", "hoped for", m.NO_PATCH)
    toks = ft._norm_tokens(r["key"])
    assert all(t in ("hoped", "hope", "for") for t in toks)
    # LLMが『hop for』と誤提案しても、patch無しでは通らず、通る場合でもdisplay/LLM語のみ(新語形を作らない)
    r2 = m.rederive_m1("hoped for", "hop for", "hoped for", m.TIER1_PATCH)
    for t in ft._norm_tokens(r2.get("key") or "hoped for"):
        assert t in ("hoped", "hop", "for")


def test_rederive_truncates_llm_extension_to_display_window():
    r = m.rederive_m1("rose above", "rise above the other voices", "rose above", m.NO_PATCH)
    assert r["ok"] and r["key"] == "rise above" and r["truncated_tail"] == ["the", "other", "voices"]
    r = m.rederive_m1("held out", "hold out one's hands", "held out", m.NO_PATCH)
    assert r["ok"] and r["key"] == "hold out"


def test_participial_adjective_nouns_still_rejected_under_tier1():
    with m.RulePatch(**m.TIER1_PATCH):
        for key, disp in [("heat debate", "heated debate"), ("mix feelings", "mixed feelings"), ("limit time", "limited time"),
                          ("use cars", "used cars"), ("break record", "broken record"), ("close doors", "closed doors"),
                          ("new", "news"), ("bind to", "bound to")]:
            assert ft.find_inflection_window(key, disp) is None, (key, disp)


# ---------------------------------------------------------------- A: 意味反転の歯止め
@pytest.mark.parametrize("phrase", ["too soon to wave a flag", "could not bear another second", "no way to know", "never been to Paris", "hardly ever heard it"])
def test_subspans_never_drop_scope_operator_and_keep_operand(phrase):
    allr, ok = m.subspan_candidates(phrase, [], [])
    toks = [t.lower() for t in ft._norm_tokens(phrase)]
    for r in allr:
        if r.get("rejected"):
            continue
        i, j = r["span"]
        assert m._scope_violation(ft._norm_tokens(phrase), i, j) is None
        for s, w in enumerate(toks):
            if w in m.SCOPE_WORDS and not (i <= s < j):
                assert not (i <= s + 1 < j), (phrase, r["phrase"])


def test_soon_to_wave_a_flag_is_rejected_as_meaning_inversion():
    allr, _ = m.subspan_candidates("too soon to wave a flag", [], [])
    rej = {r["phrase"]: r.get("rejected") for r in allr}
    assert rej["soon to wave a flag"] and "演算子" in rej["soon to wave a flag"]


def test_slot_generalization_keeps_frame_and_flags_non_contiguous():
    res = m.slot_generalization_candidates("too soon to wave a flag", [], [])
    assert res and res[0]["phrase"] == "too soon to do" and res[0]["contiguous_in_text"] is False
    assert res[0]["checks"]["scope_words_kept_before_slot"] and res[0]["replaced_tail"] == "wave a flag"


# ---------------------------------------------------------------- M6: 最終Gateと同一引数
def test_gate_check_calls_validator_with_final_gate_arguments(monkeypatch):
    seen = {}
    real = kc.validate_canonicalization_item

    def spy(*a, **k):
        seen.update(k)
        seen["args"] = a
        return real(*a, **k)
    monkeypatch.setattr(kc, "validate_canonicalization_item", spy)
    m.gate_check("rise above", "rose above", "rose above", "rose above", frozenset({1}))
    assert seen["allow_inflection_normalization"] is True
    assert seen["original_span"] == "rose above"
    assert seen["role_ok_poss"] == frozenset({1})
    assert seen["normalization_reason"] in ("lemma_normalization", "none")


# ---------------------------------------------------------------- C: 助動詞の役割判定
@pytest.mark.parametrize("phrase,expected_roles", [
    ("have a say", ["lexical"]), ("had our eye on", ["lexical"]), ("has a point", ["lexical"]), ("have agency", ["lexical"]),
    ("have a big moment", ["lexical"]), ("have limited access", ["lexical"]),
    ("have gone", ["aux"]), ("has been", ["aux"]), ("have to go", ["aux"]), ("had better", ["aux"]), ("have limited the damage", ["aux"]),
    ("Have you seen it", ["aux"]), ("have taken", ["aux"]), ("had started", ["aux"]),
    ("Had users been", ["aux"]), ("Has Vera been", ["aux"]), ("Has the Moon", ["aux"]), ("have only put", ["aux"]), ("had also faded", ["aux"]),
    ("have expected", ["aux"]), ("have proven useful", ["aux"]), ("have become", ["aux"]), ("have in common", ["lexical"]), ("had no way", ["lexical"]), ("have seven levels", ["lexical"]),
])
def test_have_role_distinguishes_lexical_and_auxiliary(phrase, expected_roles):
    roles = [role for tok, role in m.finite_aux_roles(phrase) if tok in ("have", "has", "had")]
    assert roles == expected_roles


@pytest.mark.parametrize("phrase", ["could not bear", "will have a say", "must have a say", "the stakes are different", "were mocking me", "is going to"])
def test_modals_and_copula_remain_rejected_by_role_based_check(phrase):
    assert m.contains_finite_aux_role_based(phrase) is True


def test_idiom_exception_only_for_core_without_subject():
    with m.RulePatch(aux=True, idiom=True):
        assert kc._contains_finite_auxiliary("can’t be helped") is False          # 見出しの核(主語なし)
        assert kc._contains_finite_auxiliary("it can’t be helped") is True        # 主語で始まる完全文は例外にしない
        assert kc._contains_finite_auxiliary("could not bear") is True            # 辞書見出しに無い法助動詞は不変


# ---------------------------------------------------------------- D: 再アンカー / CMU / 構造違反のrevert
def _units(text):
    return m.units_for(text)


def test_reanchor_uses_existing_validator_in_reverse():
    text = "I do not think it is okay to let them use whatever catches their interest. Seeing that, I feel safer."
    anchors = m.reanchor("catch their interest", _units(text))
    assert [a["surface"] for a in anchors] == ["catches their interest"]
    # 本文に対応窓が無い(言い換え・創作)なら戻さない
    assert m.reanchor("grab their attention", _units(text)) == []


def test_cmu_derived_never_substitutes_pass():
    assert m.cmu_derived("redelivery") and cmu.reasons_for_phrase("redelivery fee")   # 分解はできるが、CMU gate自体は不通過のまま
    assert m.cmu_derived("minaudière") == []


def test_structural_revert_for_cmu_post_canon_style_violation():
    # LLM keyが未登録語を作った(synthetic)場合、displayへ戻せば既存validator+CMUを通る。戻した後も必ず再検査する
    r = m.rescue_structural_revert("fooqux above", "rose above", "rose above")
    assert r["before_ok"] is False and r["after_ok"] is True and r["reverted_key"] == "rose above"


# ---------------------------------------------------------------- inventory結果の不変条件(X/Y/Z・NG・CMU)
@pytest.mark.skipif(not os.path.exists(EVAL), reason="rescue_eval_07.json未生成")
def test_inventory_invariants():
    rows = json.load(open(EVAL, encoding="utf-8"))
    assert {r["family"] for r in rows} <= {"X", "Y", "Z"}                     # A/B/C(LEGACY)は対象外
    for r in rows:
        d = r["decision"]
        if r["class"] == "HUMAN_NG_EXCLUDED":
            assert d["rescuable"] is False and d["final_key"] is None          # NG復活禁止
        if r["class"] == "CMU_UNREGISTERED":
            assert d["rescuable"] is False and d["final_key"] is None          # 代替合格禁止
        fc = r.get("final_check")
        if d.get("rescuable") and fc:
            assert fc["validator_ok"] and fc["cmu_ok"]                         # 救済後も既存Gate(同一引数)を通過
            assert not fc["duplicate_with_existing"]                           # 既存候補と重複/包含しない
        if r.get("rescue_record"):
            rr = r["rescue_record"]
            if rr["flags"]["rescued"]:
                assert rr["auto_eligible"] is False                            # 救済フロー由来はAUTO不可
                assert rr["gates"]["canonicalization"] == "RESCUED_QA_NOT_REJUDGED"
