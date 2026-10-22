# -*- coding: utf-8 -*-
"""PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_02: Opus条件Aレビュー反映(P-01〜P-15)+X/Z配線のtest。
全てmock/tempfile。API呼出0・費用JPY0。共有ログ/HR queue/Ledger/Storeの実ファイルには書かない(OPEN-447/449の混入再発防止)。
実行: .venv\\Scripts\\python.exe -m pytest er103_pnap_wiring_test_01.py"""
import json
import os
import re
import shutil
import sys
import wave

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er103_pnap_runner_hooks_01 as hooks
import er103_proper_noun_alarm_policy_01 as pol
import er103_pronunciation_tts_supply_01 as sup

ELIG = dict(judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY", lang="en", enabled=True,
            p3_entry="p3_primary_ng")


def decide(canon, prim, sec_, **kw):
    a = dict(ELIG)
    a.update(kw)
    return pol.evaluate_alarm_eligibility(
        canonical_text=canon, primary_cls=val.classify_asr_match(canon, prim),
        secondary_cls=val.classify_asr_match(canon, sec_) if sec_ is not None else None,
        primary_text=prim, secondary_text=sec_, **a)


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    """flag/scope/registryを各testで初期化(既定OFF)。"""
    monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", False)
    monkeypatch.setattr(sup, "TTS_SUPPLY_ENABLED", False)
    monkeypatch.setattr(pol, "_RUN_SCOPE", None)
    sup.clear_registry()
    sec.reset_secondary_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    yield
    sup.clear_registry()
    sec.reset_secondary_cache()


# ============================================================ P-01
class TestP01Entry:
    def test_force_secondary_entry_not_accepted(self):
        d = decide("Melos said.", "Mello said.", "Mellow said.", p3_entry="force_secondary")
        assert not d.accept and d.reason == pol.R_P3_ENTRY

    @pytest.mark.parametrize("entry", ["primary_length_ng", "primary_pass_demoted_ambiguous_value", None, "dual_required"])
    def test_other_p3_entries_not_accepted(self, entry):
        d = decide("Melos said.", "Mello said.", "Mellow said.", p3_entry=entry)
        assert not d.accept and d.reason == pol.R_P3_ENTRY

    def test_primary_ng_entry_accepted(self):
        assert decide("Melos said.", "Mello said.", "Mellow said.").accept

    def test_real_judge_force_secondary_sets_p3_entry_force_secondary(self):
        import er078_asr_unified_judge_01 as uj
        canon = "Melos said."
        primary = uj.PrimaryResult(passed=True, text=canon, label="EXACT_MATCH")
        ctx = uj.AttemptCtx(canonical_text=canon, wav_path="x.wav", wav_sha256="s", audio_seconds=3.0, segment_key="full_story_part1",
                            script_version="v0", slot=1, force_secondary=True, engine="azure", cache=uj.SecondaryCache(), run_state=uj.RunState())
        jr = uj.unified_judge(ctx, primary, lambda _c: uj.SecondaryOutcome("Mellow said."), lang="en", role="FULL_STORY",
                              secondary_accept_fn=lambda c, t: (False, "ASR_VALIDATION_UNCERTAIN"))
        assert jr.audit_record["p3_entry"] == "force_secondary"
        d = pol.evaluate_alarm_eligibility(
            canonical_text=canon, primary_cls=val.classify_asr_match(canon, "Mello said."), secondary_cls=val.classify_asr_match(canon, "Mellow said."),
            primary_text="Mello said.", secondary_text="Mellow said.", judge_state=jr.state, judge_reason_code=jr.reason_code,
            role="FULL_STORY", enabled=True, p3_entry=jr.audit_record["p3_entry"])
        assert not d.accept and d.reason in (pol.R_P3_ENTRY, pol.R_JUDGE_STATE)


# ============================================================ P-02
class TestP02TitleCase:
    CMU = staticmethod(lambda t: t not in {"khaite", "toteme", "meink", "melos"})

    def test_title_case_run_of_general_words_not_evidence(self):
        ok, _ = pol.proper_noun_evidence("sales", "The report said Retail Sales Fell sharply.", cmu_has=self.CMU)
        assert not ok

    def test_topic_intro_title_general_word_not_evidence(self):
        ok, _ = pol.proper_noun_evidence("coffee", "Today's topic is Coffee Prices Fall.", cmu_has=self.CMU, role="TOPIC_INTRO")
        assert not ok

    def test_after_colon_or_quote_not_evidence(self):
        for text in ("The headline read: Kite prices rose.", 'He said "Kite" twice.'):
            ok, _ = pol.proper_noun_evidence("kite", text, cmu_has=self.CMU)
            assert not ok, text

    def test_person_name_run_with_oov_part_is_evidence(self):
        ok, ev = pol.proper_noun_evidence("stephen", "A study by Stephen Reicher was published.", cmu_has=lambda t: t != "reicher")
        assert ok and ev == "capitalized_midsentence"

    def test_midsentence_single_capital_cmu_word_still_evidence(self):
        ok, _ = pol.proper_noun_evidence("kite", "The model wore a Kite bag.", cmu_has=self.CMU)
        assert ok

    def test_title_general_word_diff_not_accepted(self):
        zipf = lambda t: 5.0   # 全語を一般語に
        d = decide("Today's topic is Retail Sales Fell.", "Today's topic is Real Tailor Sales Fell.",
                   "Today's topic is Real Tailor Sales Fell.", role="TOPIC_INTRO", cmu_has=lambda t: True, zipf=zipf)
        assert not d.accept


# ============================================================ P-03
class TestP03GeneralWords:
    def test_muse_to_use_both_sides_not_accepted(self):
        d = decide("Some Muse calls were handed over to human workers.", "Some use calls were handed over to human workers.",
                   "Some use calls were handed over to human workers.")
        assert not d.accept and d.reason in (pol.R_ASR_BOTH_GENERAL_WORDS, pol.R_NOT_PROPER_EVIDENCE, pol.R_GENERAL_WORD, pol.R_LOW_SIMILARITY)

    def test_low_frequency_collapse_still_accepted(self):
        for canon, p, s in (("Its examples included Khaite's bags.", "Its examples included Kite's bags.", "Its examples included Kites bags."),
                            ("Toteme and Altuzarra said hello.", "Totem and Altuzarra said hello.", "Totem and Altuzarra said hello.")):
            assert decide(canon, p, s).accept, canon

    def test_short_spelling_general_collapse_needs_similarity(self):
        # 原稿綴り4文字以下 + ASR側が一般語 -> 類似度0.5未満は不受理
        d = decide("Met Zoe today.", "Met so today.", "Met so today.", cmu_has=lambda t: t != "zoe", ledger_surfaces=frozenset({"zoe"}))
        assert not d.accept

    def test_asr_more_words_than_canonical_when_general_not_accepted(self):
        d = decide("Then Nara walked.", "Then in our a walked.", "Then in our a walked.",
                   cmu_has=lambda t: t != "nara", zipf=lambda t: 5.0 if t != "nara" else 1.0)
        assert not d.accept

    def test_one_side_general_other_side_proper_still_accepted(self):
        d = decide("Its examples included Khaite's bags.", "Its examples included Kate's bags.", "Its examples included Kites bags.")
        assert d.accept, d


# ============================================================ P-04
class TestP04SecondaryNoise:
    def test_up_to_two_non_proper_noise_ok_three_rejected(self):
        canon = "Melos met a tall guard near the old gate and then a small boy ran past the red door."
        prim = canon.replace("Melos", "Mello")
        sec2 = prim.replace("tall", "short").replace("old", "new")
        assert decide(canon, prim, sec2).accept
        sec3 = sec2.replace("small", "big")
        d = decide(canon, prim, sec3)
        assert not d.accept and d.reason == pol.R_SECONDARY_NOISE_LIMIT

    def test_two_consecutive_content_words_dropped_rejected(self):
        canon = "Melos met the tall strong guard near the gate."
        prim = canon.replace("Melos", "Mello")
        d = decide(canon, prim, prim.replace("tall strong ", ""))
        assert not d.accept and d.reason == pol.R_SECONDARY_NOISE_LIMIT


# ============================================================ P-05 (i)(ii)(iii)
def _alarm_entry(canon="Melos said.", prim="Mello said.", sec_="Mellow said.", *, tts_input=None, pre=None, smap=None):
    d = decide(canon, prim, sec_)
    assert d.accept
    recs = pol.build_alarm_records(d, canonical_text=canon, segment_id="full_story_part1", wav_path="old/run/full_story_part1.wav",
                                   wav_sha256="oldsha", family="X", article_id="art", level="b1b", role="FULL_STORY")
    return {"status": "OK", "text": canon, "asr_text": prim, "sha256": "newsha", "path": "new/run/full_story_part1.wav",
            "asr_judgement": {"state": pol.STATE_ALARM, "primary": {"text": prim, "passed": False},
                              "secondary": {"text": sec_}, "warnings": [], "pronunciation_alarm_records": recs,
                              "pronunciation_alarm": {"tts_input_text": tts_input or canon, "pre_supply_text": pre or canon,
                                                      "supply_map": smap or {}, "supply_decisions": []}}}


class TestP05Inheritance:
    def _vi(self):
        import er019_family_x_validation_inheritance_01 as vi
        return vi

    def test_alarm_entry_reevaluated_and_inherited_in_scope(self, monkeypatch):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        entry = _alarm_entry()
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is True and r["secondary_new_calls"] == 0
        rec = r["asr_judgement_inherited"]
        assert rec["state"] == pol.STATE_ALARM
        # 現runのlocation/segmentで再構築される
        assert rec["pronunciation_alarm_records"][0]["location"]["wav_path"] == "new/run/full_story_part1.wav"
        assert rec["pronunciation_alarm_records"][0]["location"]["wav_sha256"] == "newsha"
        assert rec["pronunciation_alarm_records"][0]["level"] == "b1b"

    def test_not_inherited_outside_scope_or_flag_off(self, monkeypatch):
        entry = _alarm_entry()
        assert self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")["ok"] is False   # flag OFF/scope無し
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        assert self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")["ok"] is False   # scope無し

    def test_stricter_current_boundary_rejects_old_acceptance(self, monkeypatch):
        """古い受理(例: Muse->use)は、現行定数(P-03)での再評価で継承されない。"""
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        canon, prim, s = "Some Muse calls were handed over.", "Some use calls were handed over.", "Some use calls were handed over."
        entry = {"status": "OK", "text": canon, "asr_text": prim, "sha256": "x", "path": "p.wav",
                 "asr_judgement": {"state": pol.STATE_ALARM, "primary": {"text": prim, "passed": False}, "secondary": {"text": s},
                                   "warnings": [], "pronunciation_alarm_records": [], "pronunciation_alarm": {}}}
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is False and r["alarm_rejudge"]["accepted"] is False

    def test_value_diff_in_stored_transcript_still_blocks(self, monkeypatch):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        entry = _alarm_entry("Melos ran 3 miles.", "Mello ran 3 miles.", "Mellow ran 3 miles.")
        entry["asr_text"] = "Mello ran 5 miles."
        entry["asr_judgement"]["primary"]["text"] = "Mello ran 5 miles."
        with pol.run_scope("X"):
            assert self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")["ok"] is False

    def test_supplied_tts_input_used_for_rejudge(self, monkeypatch):
        """P-05(iii): 供給後(Khaite->Kate)のTTS入力で受理した音声は、保存したtts_input_text/supply_mapで再判定される。"""
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        import er003_v1_n3_01_tts_generate as n3
        orig = "Its examples included Khaite bags."
        shaped = n3.tts_safe_news_en(orig)
        supplied = shaped.replace("Khaite", "Kate")
        prim, s = "Its examples included Kait bags.", "Its examples included Kate bags."
        d = decide(supplied, prim, s, supply_map={"kate": "khaite"})
        assert d.accept, d
        recs = pol.build_alarm_records(d, canonical_text=supplied, segment_id="full_story_part1", supply_map={"kate": "khaite"}, family="X")
        entry = {"status": "OK", "text": orig, "asr_text": prim, "sha256": "x", "path": "p.wav",
                 "asr_judgement": {"state": pol.STATE_ALARM, "primary": {"text": prim, "passed": False}, "secondary": {"text": s}, "warnings": [],
                                   "pronunciation_alarm_records": recs,
                                   "pronunciation_alarm": {"tts_input_text": supplied, "pre_supply_text": shaped, "supply_map": {"kate": "khaite"},
                                                           "supply_decisions": []}}}
        with pol.run_scope("X"):
            r = self._vi().rejudge_with_current_judge(entry, "b1b", "full_story_part1")
        assert r["ok"] is True, r


class TestP05StoreScope:
    def _store(self, tmp_path, monkeypatch):
        import er006_master_audio_store_01 as st
        monkeypatch.setattr(st, "STORE_DIR", str(tmp_path / "store"))
        monkeypatch.setattr(st, "AUDIO_DIR", str(tmp_path / "store" / "audio"))
        monkeypatch.setattr(st, "MANIFEST_PATH", str(tmp_path / "store" / "manifest.json"))
        monkeypatch.setattr(st, "TELEMETRY_PATH", str(tmp_path / "store" / "t.jsonl"))
        return st

    def test_alarm_audio_reused_only_in_scope(self, tmp_path, monkeypatch):
        st = self._store(tmp_path, monkeypatch)
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        key = st.MasterAudioKey("en", "v", "m", "Melos said.")
        gen_calls = []
        entry = _alarm_entry()

        def gen(out_path):
            gen_calls.append(out_path)
            with open(out_path, "wb") as f:
                f.write(b"RIFFxxxx")
            return {"status": "OK", "sha256": "s", "asr_verified": True, "asr_text": "Mello said.",
                    "asr_judgement": entry["asr_judgement"]}
        with pol.run_scope("X"):
            st.get_or_generate(key, str(tmp_path / "o1.wav"), gen)
            r_in = st.get_or_generate(key, str(tmp_path / "o2.wav"), gen)
        assert r_in["reused"] is True and len(gen_calls) == 1          # 承認範囲内は再利用
        r_out = st.get_or_generate(key, str(tmp_path / "o3.wav"), gen)  # scope外(A/B/C相当)
        assert r_out["reused"] is False and len(gen_calls) == 2         # 再利用せず再生成
        assert r_out["cache_miss_reason"] == "reuse_value_guard_blocked"

    def test_guard_entry_alarm_blocked_when_flag_off(self):
        import er078_reuse_value_guard_01 as g
        r = g.guard_entry({"asr_judgement": {"state": pol.STATE_ALARM}, "asr_text": "x"}, canonical_text="x y")
        assert r["blocked"] and r["reason"] == "PRONUNCIATION_ALARM_AUDIO_OUT_OF_SCOPE"


# ============================================================ P-06 / P-07
def _led(**kw):
    e = {"surface": "Khaite", "entity_type": "brand", "pronunciation_hint": "kate", "sources": ["https://www.nylon.com/x"],
         "evidence_tier": "QUOTE_VERIFIED"}
    e.update(kw)
    return {"k": e}


class TestP06CaseSensitive:
    def test_lowercase_common_word_not_replaced(self):
        led = {"n": {"surface": "Nice", "entity_type": "brand", "pronunciation_hint": "niece", "human_approved": True,
                     "evidence_tier": "QUOTE_VERIFIED", "sources": ["https://x.com/a"]}}
        text = "Nice weather. It was a nice day, and nice people met Nice in France."
        decs = sup.plan_supply(text, led, enabled=True)
        out, _ = sup.apply_supply(text, decs)
        assert "a nice day" in out and "and nice people" in out   # 小文字は不変
        assert out.startswith("Nice weather")                       # 文頭の大文字(一般語の可能性)は不変
        assert "met Niece in France" in out                          # 文中の大文字始まりのみ置換

    def test_rare_name_replaced_case_exact(self):
        decs = sup.plan_supply("Khaite and khaite and KHAITE", _led(human_approved=True), enabled=True)
        out, _ = sup.apply_supply("Khaite and khaite and KHAITE", decs)
        assert out == "Kate and khaite and KHAITE"


class TestP07TierRules:
    def _tier(self, entry):
        return sup.classify_supply_tier(entry)[0]

    def test_official_host_label_exact_not_substring(self):
        assert sup._is_official_host("www.khaite.com", "Khaite")
        assert not sup._is_official_host("khaite-fan-blog.example.com", "Khaite")
        assert not sup._is_official_host("notkhaite.com", "Khaite")

    def test_a_tier_needs_consistency_with_quote(self):
        base = dict(sources=["https://www.khaite.com/about"], evidence_tier="QUOTE_VERIFIED")
        # 引用が無い -> A不可(B扱い=人承認が必要)
        assert self._tier(_led(**base)["k"]) == "B"
        d = sup.plan_supply("Khaite bags.", _led(**base), enabled=True)[0]
        assert not d.supplied
        # 引用にrespelling(kate)が現れる -> A
        ok = _led(**base, evidence=[{"url": "https://www.khaite.com/about", "quote": "Khaite (pronounced Kate) is a brand"}])
        assert self._tier(ok["k"]) == "A"
        assert sup.plan_supply("Khaite bags.", ok, enabled=True)[0].supplied
        # 引用が別の発音を言っている -> A不可
        bad = _led(**base, evidence=[{"url": "https://www.khaite.com/about", "quote": "Khaite (pronounced kite) is a brand"}])
        assert self._tier(bad["k"]) == "B"

    def test_wikipedia_a_only_when_consistent(self):
        base = dict(sources=["https://en.wikipedia.org/wiki/Khaite"], evidence_tier="QUOTE_VERIFIED")
        assert self._tier(_led(**base)["k"]) == "B"
        ok = _led(**base, evidence=[{"url": "https://en.wikipedia.org/wiki/Khaite", "quote": "Khaite, pronounced Kate"}])
        assert self._tier(ok["k"]) == "A"

    def test_media_host_never_a_even_with_quote(self):
        e = _led(evidence=[{"url": "https://www.nylon.com/x", "quote": "pronounced Kate"}])["k"]
        assert self._tier(e) == "B"
        assert not sup.plan_supply("Khaite bags.", {"k": e}, enabled=True)[0].supplied   # 人承認なし

    def test_human_tts_respelling_on_official_host_is_a(self):
        e = _led(sources=["https://www.khaite.com/"], tts_respelling="Kate")["k"]
        assert self._tier(e) == "A"


# ============================================================ P-08 / P-11 / P-13 / report
def _write_results(level_dir, results):
    os.makedirs(os.path.join(level_dir, "audit"), exist_ok=True)
    with open(os.path.join(level_dir, "audit", "tts_generation_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)


class TestP08Report:
    def test_report_embeds_supply_list_and_hr_split_and_ja_note(self, tmp_path):
        e = _alarm_entry()
        _write_results(str(tmp_path / "b1b"), {"segments": {"full_story_part1": e}})
        sl = [{"original": "Khaite", "respelling": "Kate", "tier": "B", "evidence_tier": "QUOTE_VERIFIED", "human_approved": True, "ledger_id": "L1"}]
        r = pol.write_run_alarms(str(tmp_path / "b1b"), supply_list=sl)
        md = open(r["md"], encoding="utf-8").read()
        assert "発音供給の適用一覧" in md and "`Khaite` -> `Kate`" in md and "日本語音声" in md and "Human Review残" in md
        assert r["consistency"] == {"alarm_state_records": 1, "reported": 1, "match": True}

    def test_zero_alarm_still_has_section_and_supply_zero(self, tmp_path):
        _write_results(str(tmp_path / "a2"), {"segments": {}})
        r = pol.write_run_alarms(str(tmp_path / "a2"))
        md = open(r["md"], encoding="utf-8").read()
        assert "0件" in md and "供給対象なし" in md

    def test_missing_results_gives_explicit_failure_not_zero(self, tmp_path):
        rep = pol.write_run_alarms_safe(str(tmp_path / "b1b"))
        assert rep["error"]
        md = open(rep["md"], encoding="utf-8").read()
        assert "アラーム集計失敗" in md and "0件" not in md

    def test_count_mismatch_is_flagged(self):
        md = pol.render_operator_report([], consistency={"alarm_state_records": 2, "reported": 0, "match": False})
        assert "集計不一致" in md

    def test_same_wav_reused_in_two_segments_reports_both(self):
        e1 = _alarm_entry()
        aj = e1["asr_judgement"]
        res = {"segments": {"full_story_part1": e1, "full_story_part2": {"status": "OK", "asr_judgement_inherited": aj, "path": "n/p2.wav", "sha256": "z"}}}
        out = pol.derive_run_alarms(res)
        assert len(out) == 2 and pol.count_alarm_states(res) == 2
        assert {o["segment_id"] for o in out} == {"full_story_part1", "full_story_part2"}

    def test_noun_aggregation_in_report(self):
        e = _alarm_entry()
        recs = e["asr_judgement"]["pronunciation_alarm_records"]
        res = {"segments": {f"full_story_part1_c{i}": {"status": "OK", "asr_judgement": e["asr_judgement"], "path": f"p{i}.wav"} for i in (1, 2, 3)}}
        md = pol.render_operator_report(pol.derive_run_alarms(res))
        assert "× 3箇所" in md and recs[0]["proper_noun"] in md

    def test_hr_residual_distinguishes_proper_noun_only(self):
        res = {"segments": {"s1": {"status": "STOPPED", "text": "Melos ran home.", "attempts_log": [
            {"audio_classification": "ASR_VALIDATION_UNCERTAIN", "asr_text": "Mello ran home."}]},
                            "s2": {"status": "STOPPED", "text": "Melos ran home.", "attempts_log": [
                                {"audio_classification": "TRUE_CONTENT_MISMATCH", "asr_text": "x"}]}}}
        h = pol.hr_residual_summary(res)
        assert h["hr_asr_uncertain_segments"] == 1 and h["of_which_proper_noun_only_outside_alarm_boundary"] == 1

    def test_article_aggregate_x(self, tmp_path):
        e = _alarm_entry()
        for lv in ("b1b", "a2"):
            _write_results(str(tmp_path / lv), {"segments": {"full_story_part1": e}})
            pol.write_run_alarms(str(tmp_path / lv))
        r = hooks.aggregate_article_alarms(str(tmp_path), [str(tmp_path / "b1b"), str(tmp_path / "a2")])
        assert r["count"] == 2 and r["error"] is None
        assert os.path.exists(tmp_path / "audit" / "operator_alarm_report_article.md")
        r2 = hooks.aggregate_article_alarms(str(tmp_path), [str(tmp_path / "b1b"), str(tmp_path / "nope")])
        assert "集計失敗" in r2["md"]

    def test_outputs_only_under_audit(self, tmp_path):
        _write_results(str(tmp_path / "b1b"), {"segments": {"full_story_part1": _alarm_entry()}})
        before = {p for p, _d, fs in os.walk(tmp_path) for f in fs for p in [os.path.join(p, f)]}
        pol.write_run_alarms(str(tmp_path / "b1b"))
        after = {p for p, _d, fs in os.walk(tmp_path) for f in fs for p in [os.path.join(p, f)]}
        for new in after - before:
            assert os.sep + "audit" + os.sep in new
        assert not any(f.endswith(".html") for p in after for f in [os.path.basename(p)])


# ============================================================ P-10 scope / hooks
class TestP10Scope:
    def test_context_manager_releases_on_exception(self):
        with pytest.raises(RuntimeError):
            with pol.run_scope("X"):
                assert pol.current_scope() == "X"
                raise RuntimeError("boom")
        assert pol.current_scope() is None

    def test_nested_scope_restores_previous(self):
        with pol.run_scope("X"):
            with pol.run_scope("Z"):
                assert pol.current_scope() == "Z"
            assert pol.current_scope() == "X"
        assert pol.current_scope() is None

    def test_hook_flag_off_is_passthrough_no_files(self, tmp_path):
        calls = []
        r = hooks.run_with_alarm_hook("X", str(tmp_path / "b1b"), lambda: calls.append(pol.current_scope()) or "ret")
        assert r == "ret" and calls == [None] and not os.path.exists(tmp_path / "b1b")

    def test_hook_flag_on_runs_in_scope_and_reports_in_finally(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        seen = []

        def fn():
            seen.append(pol.current_scope())
            _write_results(str(tmp_path / "b1b"), {"segments": {"full_story_part1": _alarm_entry()}})
            raise RuntimeError("STOP mid-run")
        with pytest.raises(RuntimeError):
            hooks.run_with_alarm_hook("X", str(tmp_path / "b1b"), fn)
        assert seen == ["X"] and pol.current_scope() is None
        assert os.path.exists(tmp_path / "b1b" / "audit" / "operator_alarm_report.md")   # 途中失敗でも出る
        assert "固有名詞発音アラーム" in capsys.readouterr().out

    def test_hook_when_results_never_written_reports_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)

        def fn():
            raise RuntimeError("early")
        with pytest.raises(RuntimeError):
            hooks.run_with_alarm_hook("Z", str(tmp_path / "a2"), fn)
        assert "アラーム集計失敗" in open(tmp_path / "a2" / "audit" / "operator_alarm_report.md", encoding="utf-8").read()


# ============================================================ P-11 supply wiring
class TestP11SupplyWiring:
    def test_supply_for_tts_identity_when_flags_off_or_no_scope(self):
        led = _led(human_approved=True)
        assert sup.supply_for_tts("Khaite bags.", "Khaite bags.", ledger=led) == "Khaite bags."          # flag OFF
        sup.TTS_SUPPLY_ENABLED = True
        try:
            assert sup.supply_for_tts("Khaite bags.", "Khaite bags.", ledger=led) == "Khaite bags."      # scope無し
        finally:
            sup.TTS_SUPPLY_ENABLED = False

    def test_supply_in_scope_registers_and_reports_static_reicher(self, monkeypatch):
        monkeypatch.setattr(sup, "TTS_SUPPLY_ENABLED", True)
        import er003_v1_n3_01_tts_generate as n3
        orig = "Khaite and Stephen Reicher spoke."
        shaped = n3.tts_safe_news_en(orig)
        assert "Riker" in shaped
        with pol.run_scope("X"):
            out = sup.supply_for_tts(orig, shaped, ledger=_led(human_approved=True),
                                     static_overrides=n3._EN_NAME_PRONUNCIATION_OVERRIDES)
        assert out == shaped.replace("Khaite", "Kate")
        lk = sup.lookup_supply(out)
        assert lk["supply_map"].get("riker") == "reicher" and lk["supply_map"].get("kate") == "khaite"
        assert lk["pre_supply_text"] == shaped
        names = {(d["original"], d["respelling"]) for d in sup.applied_supplies()}
        assert ("Reicher", "Riker") in names and ("Khaite", "Kate") in names

    def test_supply_failure_is_identity(self, monkeypatch):
        monkeypatch.setattr(sup, "TTS_SUPPLY_ENABLED", True)
        monkeypatch.setattr(sup, "plan_supply", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
        with pol.run_scope("Z"):
            assert sup.supply_for_tts("a", "a b", ledger={}) == "a b"


# ============================================================ P-12/P-15 role resolution for Z clip IDs
def test_z_clip_ids_resolve_to_narrative_roles():
    import er020_tts_retry_local_rewrite_01 as rg
    assert rg.resolve_narrative_role("full_story_part1_c7") == "FULL_STORY"
    assert rg.resolve_narrative_role("full_story_part3_c11") == "FULL_STORY"
    assert rg.resolve_narrative_role("comment_2") == "COMMENT"
    assert rg.resolve_narrative_role("preview") == "PREVIEW"


# ============================================================ approval CLI / Ledger additive keys
class TestApprovalCliAndLedger:
    def test_cli_dry_run_then_apply_with_temp_ledger_and_log(self, tmp_path):
        import er103_pronunciation_approve_cli_01 as cli
        ledger = {"id1": {"surface": "Khaite", "entity_type": "brand"}, "id2": {"surface": "Other"}}
        saved = {}
        r = cli.approve("khaite", "Kate", "tester", apply=False, ledger_loader=lambda: ledger, ledger_saver=lambda l: saved.update(l),
                        log_path=str(tmp_path / "log.jsonl"))
        assert r["ok"] and not r["applied"] and not saved and not os.path.exists(tmp_path / "log.jsonl")
        r = cli.approve("khaite", "Kate", "tester", apply=True, ledger_loader=lambda: ledger, ledger_saver=lambda l: saved.update(l),
                        log_path=str(tmp_path / "log.jsonl"))
        assert saved["id1"]["human_approved"] is True and saved["id1"]["tts_respelling"] == "Kate" and "human_approved" not in saved["id2"]
        assert json.loads(open(tmp_path / "log.jsonl", encoding="utf-8").read().splitlines()[0])["approved_by"] == "tester"
        # 承認済みB階層は供給対象に、未承認は対象外
        assert sup.plan_supply("Khaite bags.", {"id1": {**saved["id1"], "pronunciation_hint": "kate", "evidence_tier": "QUOTE_VERIFIED",
                                                         "sources": ["https://www.nylon.com/x"]}}, enabled=True)[0].supplied

    def test_ledger_upsert_keeps_human_approval_and_old_entries_have_no_new_keys(self, tmp_path, monkeypatch):
        import er006_pronunciation_ledger_01 as pl
        monkeypatch.setattr(pl, "LEDGER_PATH", str(tmp_path / "ledger.json"))
        key = pl.LedgerKey("Khaite", "brand", "en") if hasattr(pl, "LedgerKey") else None
        if key is None:
            pytest.skip("LedgerKey unavailable")
        lid = pl.upsert(key, {"canonical_spelling": "Khaite", "pronunciation_hint": "kate", "confidence": "medium", "sources": []})
        assert "human_approved" not in pl._load()[lid]                     # 旧呼出はキーを書かない(バイト一致)
        pl.upsert(key, {"canonical_spelling": "Khaite", "pronunciation_hint": "kate", "confidence": "medium", "sources": [],
                        "human_approved": True, "tts_respelling": "Kate"})
        pl.upsert(key, {"canonical_spelling": "Khaite", "pronunciation_hint": "kate", "confidence": "low", "sources": []})   # 無関係な再upsert
        e = pl._load()[lid]
        assert e["human_approved"] is True and e["tts_respelling"] == "Kate"


# ============================================================ adapter wiring (mock Primary/Secondary、HR queue spy)
def _wav(tmp_path, name="a.wav", seconds=1, rate=8000, fill=b"\x00"):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(fill * (rate * seconds))
    return str(p)


class _Az:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        return (self.text, None)


@pytest.fixture
def adapter_env(monkeypatch):
    hr = []
    monkeypatch.setattr(sec, "_log_human_review", lambda d: hr.append(d))
    lookups = []
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review",
                        lambda span: lookups.append(span) or {"pronunciation_hint": "KAYT", "confidence": "low", "sources": []})
    monkeypatch.setattr(pol, "ledger_surface_tokens", lambda ledger=None: frozenset({"khaite"}))
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: pytest.fail("Primary#2は呼ばれないはず"))
    return {"hr": hr, "lookups": lookups}


def _run(canon, prim, sec_text, tmp_path, monkeypatch, *, segment_id="full_story_part1", slot=1, last=True, dual=False, **kw):
    az = _Az(sec_text)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    ctx = {"slot": slot, "is_last_slot": last}
    if dual:
        ctx["dual_required"] = True
    return sec.evaluate_attempt_with_cascade(canon, prim, [], _wav(tmp_path), cascade_enabled=True, segment_id=segment_id,
                                             attempt_ctx=ctx, detail_out=kw.setdefault("detail_out", {}), **{k: v for k, v in kw.items() if k != "detail_out"}), az


CANON = "Its examples included Khaite's palm-sized bags."        # 実HR queue由来の型(Khaite->Kite/Kites)
PRIM = "Its examples included Kite's palm-sized bags."
SEC = "Its examples included Kites palm-sized bags."


class TestAdapterWiring:
    def test_default_off_unchanged_goes_to_human_review(self, tmp_path, monkeypatch, adapter_env):
        detail = {}
        (ok, stop, cls), az = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, detail_out=detail)
        assert ok is False and detail["human_review_required"] is True and len(adapter_env["hr"]) == 1
        assert "pronunciation_alarm" not in detail["asr_judgement"]

    def test_flag_on_without_scope_unchanged(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        detail = {}
        (ok, _s, _c), _az = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, detail_out=detail)
        assert ok is False and detail["human_review_required"] is True

    @pytest.mark.parametrize("scope", ["X", "Z"])
    def test_scope_on_accepts_alarm_no_hr(self, tmp_path, monkeypatch, adapter_env, scope):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        detail = {}
        with pol.run_scope(scope):
            (ok, stop, cls), az = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, detail_out=detail)
        assert ok is True and stop is False and cls.classification == "PASS_WITH_PRONUNCIATION_ALARM" and cls.should_pass
        assert detail["human_review_required"] is False and adapter_env["hr"] == []        # HR queue不追記
        aj = detail["asr_judgement"]
        assert aj["state"] == pol.STATE_ALARM and aj["pronunciation_alarm"]["alarm_ids"]
        rec = aj["pronunciation_alarm_records"][0]
        assert rec["proper_noun"] == "khaite" and rec["family"] == scope and rec["models"]["primary_asr"]["model"]
        assert rec["pronunciation_basis"]["pronunciation_hint"] == "KAYT"
        assert aj["pronunciation_alarm"]["tts_input_text"] == CANON                            # P-05(iii)
        assert adapter_env["lookups"] == ["khaite"]                                             # Stage 1調査は1語1回(HR packageの代替)
        assert az.calls == 1                                                                   # 追加API 0(Secondaryは従来の1回)

    def test_first_slot_accepted_with_min_slot_1_and_not_with_2(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        monkeypatch.setattr(pol, "ALARM_ACCEPT_MIN_SLOT", 2)
        with pol.run_scope("X"):
            (ok1, _s, _c), _ = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, slot=1, last=False)
            (ok2, _s2, _c2), _ = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, slot=2, last=False)
        assert ok1 is False and ok2 is True

    def test_kp_dual_required_not_applied(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        detail = {}
        with pol.run_scope("X"):
            (ok, _s, _c), _ = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, dual=True, detail_out=detail, segment_id="kp1_en")
        assert ok is False and "pronunciation_alarm" not in detail["asr_judgement"]

    def test_heading_and_ja_roles_not_applied(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        with pol.run_scope("X"):
            (ok, _s, _c), _ = _run(CANON, PRIM, SEC, tmp_path, monkeypatch, segment_id="japanese_title")
        assert ok is False

    def test_number_or_negation_diff_not_applied(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        with pol.run_scope("X"):
            (ok, _s, _c), _ = _run("Melos ran 3 miles.", "Mello ran 5 miles.", "Mello ran 5 miles.", tmp_path, monkeypatch)
        assert ok is False

    def test_secondary_outage_still_technical_stop(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list",
                            lambda *a, **k: (_ for _ in ()).throw(RuntimeError("azure down")))
        detail = {}
        with pol.run_scope("X"):
            r = sec.evaluate_attempt_with_cascade(CANON, PRIM, [], _wav(tmp_path), cascade_enabled=True, segment_id="full_story_part1",
                                                  attempt_ctx={"slot": 1, "is_last_slot": True}, detail_out=detail)
        assert r[0] is False and detail.get("technical_stop") and detail["human_review_required"] is False
        assert "pronunciation_alarm" not in detail["asr_judgement"]

    def test_registry_not_in_pass_with_warning_listening_list(self, tmp_path, monkeypatch, adapter_env):
        import er078_pass_with_warning_registry_01 as reg
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        detail = {}
        with pol.run_scope("X"):
            _run(CANON, PRIM, SEC, tmp_path, monkeypatch, detail_out=detail)
        res = {"segments": {"full_story_part1": {"status": "OK", "asr_judgement": detail["asr_judgement"], "path": "x.wav"}}}
        assert reg.derive_listening_list(res) == []

    def test_audit_block_has_adapter_and_actual_model(self, tmp_path, monkeypatch, adapter_env):
        monkeypatch.setattr(pol, "PROPER_NOUN_ALARM_POLICY_ENABLED", True)
        detail = {}
        with pol.run_scope("Z"):
            _run(CANON, PRIM, SEC, tmp_path, monkeypatch, detail_out=detail)
        assert detail["asr_judgement"]["adapter"]["layers"] is not None
        assert detail["asr_judgement"]["pronunciation_alarm_records"][0]["models"]["secondary_asr"] == "azure-speech-stt"


# ============================================================ 非露出(公開ページ生成moduleが参照しない)
def test_public_page_builders_do_not_reference_alarm_modules():
    import glob
    banned = re.compile(r"pronunciation_alarm|operator_alarm|PASS_WITH_PRONUNCIATION_ALARM|er103_")
    # 公開ページ(index.html/standard.html/advanced.html)を生成するmodule(X/Z/共通)のソースにアラーム語が現れない
    for pat in ("er063_family_z_page*.py", "er0*_user_test*page*.py", "er026_family_z_*page*.py"):
        for p in glob.glob(pat):
            if p.endswith("_test_01.py") or "_test" in p:
                continue
            assert not banned.search(open(p, encoding="utf-8").read()), p


def test_page_builder_functions_do_not_reference_alarm_terms():
    """公開ページ生成(Z: er063.build_pages / X: build_player_html[運営用player.html]) の関数ソースにアラーム語が現れない(OF-PNAP-P-15)。"""
    import inspect
    import er063_family_z_audio_01 as z
    import er019_family_x_audio_production_runner_01 as x
    banned = re.compile(r"pronunciation_alarm|operator_alarm|PASS_WITH_PRONUNCIATION_ALARM|アラーム付き|er103_")
    for fn in (z.build_pages, x.build_player_html):
        assert not banned.search(inspect.getsource(fn)), fn.__name__


def test_generated_public_pages_do_not_contain_alarm_terms():
    import glob
    banned = ("PASS_WITH_PRONUNCIATION_ALARM", "アラーム付き完成", "pronunciation_alarm", "operator_alarm")
    for p in glob.glob("user_test/**/*.html", recursive=True):
        txt = open(p, encoding="utf-8", errors="ignore").read()
        assert not any(b in txt for b in banned), p
