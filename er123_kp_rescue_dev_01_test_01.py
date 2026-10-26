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
EVAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02", "rescue_eval_08.json")


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
    # 委任_03(2026-10-26): 区分1(副詞前原形化・過去形表補完・have役割判定)はProductionへ適用済み(er105_kp_rule_compliance_test_01.pyが固定)。
    # パッチ外でも区分1の変換は通る。共有のA/B/C用kc._contains_finite_auxiliary(語形リスト判定)は不変で、区分2(慣用句の閉表等)はパッチ外では効かない。
    assert kc._contains_finite_auxiliary("have a say") is True
    assert m.gate_check("study separately", "studied separately", "studied separately")["ok"] is True
    assert m.gate_check("ring through", "rang through", "rang through")["ok"] is True
    assert "rang" in ft._PAST_ONLY_IRREGULAR
    assert kc._contains_finite_auxiliary("can of worms") is True          # 区分2(慣用句例外)は未配線


def test_patch_flags_are_independent_and_minimal():
    with m.RulePatch(adverb=True):
        assert m.gate_check("study separately", "studied separately", "studied separately")["ok"] is True
        assert m.gate_check("ring through", "rang through", "rang through")["ok"] is True       # 委任_03: past表補完はProduction適用済み
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
@pytest.mark.skipif(not os.path.exists(EVAL), reason="rescue_eval_08.json未生成")
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


# =====================================================================================================
# 委任_02: Opus M1〜M4 / R3〜R5 の固定(敵対的test)。adversarial_01.json と同じ事例を直接assertする
# =====================================================================================================
ADV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02", "adversarial_01.json")


def _adv():
    return json.load(open(ADV, encoding="utf-8"))


# ---------------------------------------------------------------- M1: -ly名詞/形容詞を副詞扱いしない
@pytest.mark.parametrize("noun", ["supply", "reply", "rally", "assembly", "jelly", "belly", "bully", "folly", "monopoly", "anomaly", "tally",
                                  "timely", "scholarly", "cowardly", "leisurely", "manly", "hourly", "nightly", "sickly", "burly", "unruly", "well", "still"])
def test_m1_is_manner_adverb_rejects_ly_nouns_adjectives_and_noun_homographs(noun):
    assert m.is_manner_adverb(noun) is False


@pytest.mark.parametrize("adv", ["separately", "quietly", "happily", "basically", "probably", "simply", "truly", "fully", "gently", "effectively"])
def test_m1_is_manner_adverb_accepts_real_ly_adverbs_via_stem_check(adv):
    assert m.is_manner_adverb(adv) is True


def test_m1_adversarial_conversions_from_json():
    bad = []
    for c in _adv()["conversions"]:
        with m.RulePatch(**m.TIER1_PATCH):
            t1 = ft.find_inflection_window(c["key"], c["display"]) is not None
        base = ft.find_inflection_window(c["key"], c["display"]) is not None
        if c["expect"] == "accept":
            ok = t1 is True
        elif c["expect"] == "reject":
            ok = t1 is False
        else:       # preexisting_accept: Production既存の挙動。パッチで変化しない
            ok = (t1 == base)
        if not ok:
            bad.append((c["display"], c["key"], c["expect"], t1))
    assert not bad, bad


def test_m1_increased_supply_is_not_lemmatized_under_tier1():
    with m.RulePatch(**m.TIER1_PATCH):
        for key, disp in [("increase supply", "increased supply"), ("fail rally", "failed rally"), ("cancel reply", "cancelled reply")]:
            assert ft.find_inflection_window(key, disp) is None, (key, disp)
        assert ft.find_inflection_window("study separately", "studied separately") is not None


# ---------------------------------------------------------------- M2: have_roleの3類型(迷えばaux)
@pytest.mark.parametrize("phrase", ["has spread", "have quit", "has cast", "has cost", "have burst", "has shed", "has split", "have upset", "have bet",
                                    "has forecast", "has broadcast", "have bid", "have fit", "have rid", "had wed", "had dwelt", "had leapt",
                                    "has wrung", "had strode", "has stunk"])
def test_m2_invariant_participles_are_aux(phrase):
    assert [r for _, r in m.finite_aux_roles(phrase)] == ["aux"]


@pytest.mark.parametrize("phrase", ["have all gone", "have both agreed", "has more than doubled", "have each tried", "have just been", "had already left",
                                    "have never seen"])
def test_m2_quantifier_or_adverb_between_aux_and_participle_is_aux(phrase):
    assert [r for _, r in m.finite_aux_roles(phrase)] == ["aux"]


@pytest.mark.parametrize("phrase", ["had the board known", "had the house painted", "had the big board known"])
def test_m2_det_noun_participle_is_aux_when_indistinguishable(phrase):
    assert [r for _, r in m.finite_aux_roles(phrase)] == ["aux"]


@pytest.mark.parametrize("phrase", ["have all the answers", "have many questions", "have more than five users", "have a say in", "have a limited budget",
                                    "have two hundred pounds"])
def test_m2_lexical_have_still_lexical(phrase):
    assert [r for _, r in m.finite_aux_roles(phrase)] == ["lexical"]


def test_m2_have_roles_from_json():
    bad = []
    for c in _adv()["have_roles"]:
        got = [r for t, r in m.finite_aux_roles(c["phrase"]) if t in ("has", "have", "had")]
        if got != c["expect"]:
            bad.append((c["phrase"], got, c["expect"]))
    assert not bad, bad


# ---------------------------------------------------------------- M3: 慣用句例外は先頭が助動詞のレビュー済み閉表だけ
@pytest.mark.parametrize("phrase", ["beggars can’t be choosers", "boys will be boys", "time is money", "the die is cast", "a leopard can’t change its spots",
                                    "it can’t be helped", "will be missed", "could not bear", "you can’t be serious"])
def test_m3_noun_subject_proverbs_and_full_clauses_stay_blocked(phrase):
    with m.RulePatch(aux=True, idiom=True):
        assert kc._contains_finite_auxiliary(phrase) is True


@pytest.mark.parametrize("phrase", ["can’t be helped", "can of worms", "might as well", "had better", "had our hands tied", "can’t wait"])
def test_m3_closed_table_phrases_are_allowed(phrase):
    with m.RulePatch(aux=True, idiom=True):
        assert kc._contains_finite_auxiliary(phrase) is False


def test_m3_closed_table_is_small_reviewed_and_integrity_checked():
    t = m.idiom_closed_table()
    assert 20 <= len(t) <= 40 and m._entries_sha(t) == m.IDIOM_TABLE_SHA256
    assert all(m._first_aux_word(e.split()) for e in t)            # 全件が先頭語=(法助動詞/助動詞)
    assert not any(e.split()[0] in ("it", "that", "there", "i", "you", "he", "she", "we", "they") for e in t)
    assert len(m.build_idiom_candidates()) >= len(t)


def test_m3_tampered_table_fails_closed(monkeypatch):
    monkeypatch.setattr(m, "IDIOM_TABLE_SHA256", "0" * 64)
    monkeypatch.setattr(m, "_IDIOM_TABLE", None)
    assert m.idiom_closed_table() == frozenset()
    with m.RulePatch(aux=True, idiom=True):
        assert kc._contains_finite_auxiliary("can’t be helped") is True       # 閉表が空なら例外なし(fail-closed)
    monkeypatch.setattr(m, "_IDIOM_TABLE", None)


def test_m3_idiom_is_not_used_without_flag():
    assert kc._contains_finite_auxiliary("can of worms") is True            # 既定OFF: Production現行どおり拒否


# ---------------------------------------------------------------- R3: 他動詞の原形/名詞と同形になる語を補完しない
def test_r3_past_table_completion_excludes_homographs():
    snap = (dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR))
    with m.RulePatch(past=True):
        for w in ("lay", "wound", "ground", "bore", "bound"):
            assert w not in ft._PAST_ONLY_IRREGULAR and w not in ft._AMBIGUOUS_IRREGULAR, w
        for w in ("rang", "sang", "swam"):
            assert w in ft._PAST_ONLY_IRREGULAR or w in ft._AMBIGUOUS_IRREGULAR, w
    assert (dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR)) == snap     # 復元済み(委任_03: Productionは補完済みの状態へ戻る)


# ---------------------------------------------------------------- R4: A1の演算子表拡張とHR旗
@pytest.mark.parametrize("dropped", ["little", "few", "unless", "rather", "instead", "fail", "except"])
def test_r4_new_operator_words_are_in_scope_table(dropped):
    assert dropped in m.SCOPE_WORDS


def test_r4_a1_candidates_carry_hr_flags_and_never_drop_operator():
    allr, ok = m.subspan_candidates("too soon to wave a flag", [], [])
    r = next(x for x in allr if x["phrase"] == "too soon")
    flags = m.a1_hr_flags(ft._norm_tokens("too soon to wave a flag"), r)
    assert any("意味縮小" in f for f in flags) and any("低価値" in f for f in flags)
    rej = {x["phrase"]: x.get("rejected") for x in allr}
    assert rej["soon to wave a flag"] and "演算子" in rej["soon to wave a flag"]


# ---------------------------------------------------------------- M4: A2は区分3で閉じず、区分2(非推奨・意見付き)
@pytest.mark.skipif(not os.path.exists(EVAL), reason="rescue_eval_08.json未生成")
def test_m4_a2_is_tier2_not_recommended_not_tier3():
    rows = json.load(open(EVAL, encoding="utf-8"))
    a2 = [r["decision"]["option_slot_generalization"] for r in rows if r["decision"].get("option_slot_generalization")]
    assert a2 and all(o["category"].startswith("区分2") and "非推奨" in o["category"] for o in a2)
    assert any(o["candidate"] == "too soon to do" for o in a2)


# ---------------------------------------------------------------- R5: 縮約形(測定。Gateは変えない)
def test_r5_current_gate_asymmetry_between_ascii_and_curly_contractions_is_recorded():
    assert kc._contains_finite_auxiliary("can't wait") is False          # ASCII: 1トークン(can't)でありすり抜け
    assert kc._contains_finite_auxiliary("can’t wait") is True           # 曲線: can|t に割れてcanで拒否
    assert kc._contains_finite_auxiliary("they’re ready") is False       # 're は are と認識されない
    assert kc._contains_finite_auxiliary("I’ll go") is False


# ---------------------------------------------------------------- 回帰: 結果の不変条件(委任_02)
@pytest.mark.skipif(not os.path.exists(EVAL), reason="rescue_eval_08.json未生成")
def test_inventory_hr_final_categories_unchanged_or_documented():
    rows = json.load(open(EVAL, encoding="utf-8"))
    hr = {(r["display"].lower()): str(r["decision"]["category"]).split("(")[0] for r in rows if str(r.get("era", "")).startswith("HR")}
    assert hr["studied separately"] == "区分1" and hr["had our eye on"] == "区分1" and hr["rang through"] == "区分1" and hr["have a say"] == "区分1"
    assert hr["too soon to wave a flag"] == "区分2" and hr["rose above"] == "区分2" and hr["held out"] == "区分2"
    assert hr["catch their interest"] == "区分2" and hr["it can’t be helped"] == "区分2" and hr["can’t be helped"] == "区分2"
    assert hr["redelivery fee"] == "区分2"
