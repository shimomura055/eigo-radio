# -*- coding: utf-8 -*-
"""PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01: 未配線module(er103_*)の単体テスト。
Production .pyは編集しない。Production判定器(er006_preprod_hardening_01_validation)はimportして読取のみ使う。API 0。
実ファイル(HR queue/Ledger/共有ログ)には書かない(書込系は全て tempfile)。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er006_preprod_hardening_01_validation as val
import er103_proper_noun_alarm_policy_01 as pol
import er103_pronunciation_tts_supply_01 as sup

ELIGIBLE = dict(judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY", lang="en", enabled=True,
                p3_entry="p3_primary_ng")


def decide(canon, prim, sec, **kw):
    args = dict(ELIGIBLE)
    args.update(kw)
    return pol.evaluate_alarm_eligibility(
        canonical_text=canon, primary_cls=val.classify_asr_match(canon, prim),
        secondary_cls=val.classify_asr_match(canon, sec) if sec is not None else None,
        primary_text=prim, secondary_text=sec, **args)


class DefaultOffIsolationTest(unittest.TestCase):
    def test_flags_default_on_but_inactive_without_runner_scope(self):
        # 委任_02: ユーザー承認(APPROVED_FOR_PRODUCTION)により既定ON(配線済み)。ただしFamily X/Z runnerのrun scope外
        # (A/B/C・単体呼出)では不活性=従来どおり。起動script/.envでの暗黙ONはしない(単一定数のみ)。
        self.assertIs(pol.PROPER_NOUN_ALARM_POLICY_ENABLED, True)
        self.assertIs(sup.TTS_SUPPLY_ENABLED, True)
        self.assertIsNone(pol.current_scope())
        self.assertIs(pol.is_active_for_run(), False)

    def test_disabled_never_accepts_and_does_no_io(self):
        before = set(os.listdir("."))
        d = pol.evaluate_alarm_eligibility(
            canonical_text="Melos said.", primary_cls=val.classify_asr_match("Melos said.", "Mello said."),
            secondary_cls=val.classify_asr_match("Melos said.", "Mellow said."), primary_text="Mello said.",
            secondary_text="Mellow said.", judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY")
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_DISABLED)
        self.assertEqual(before, set(os.listdir(".")))

    def test_supply_disabled_returns_unchanged_text(self):
        led = {"x": {"surface": "Khaite", "entity_type": "brand", "evidence_tier": "QUOTE_VERIFIED", "human_approved": True,
                     "pronunciation_hint": "kate", "sources": ["https://www.nylon.com/x"]}}
        decs = sup.plan_supply("Khaite showed bags.", led, enabled=False)
        text, smap = sup.apply_supply("Khaite showed bags.", decs)
        self.assertEqual(text, "Khaite showed bags.")
        self.assertEqual(smap, {})
        self.assertEqual(decs[0].reason, sup.R_DISABLED_FLAG)


class AcceptBoundaryTest(unittest.TestCase):
    def test_melos_mello_accepted(self):
        d = decide("Melos said.", "Mello said.", "Mellow said.")
        self.assertTrue(d.accept, d)
        self.assertEqual(d.diffs[0].canonical, "melos")

    def test_melos_primary_only_mismatch_secondary_noise_ignored(self):
        # Azureが別の位置で数字表記ゆれ等のnoiseを返しても、Primaryが一致している位置は受理判断に使わない
        canon = "The guards went still when Melos spoke. Two men stepped back."
        d = decide(canon, "The guards went still when Mello spoke. Two men stepped back.",
                   "The guards went still when Mellow spoke. 2 men stepped back.")
        self.assertTrue(d.accept, d)

    def test_mellow_strength_adjacent_word_changed_rejected(self):
        # 実データ(HR queue): Secondaryが「Melos drank」を「mellow strength」と聞いた=隣接語まで別語
        canon = "Then Melos drank the water and ran."
        d = decide(canon, "Then Mello drank the water and ran.", "Then mellow strength the water and ran.")
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_SECONDARY_NOT_ENTITY_ONLY)

    def test_khaite_kite_midsentence_capital_accepted(self):
        canon = "Its examples included Khaite's palm-sized bags."
        d = decide(canon, "Its examples included Kite's palm-sized bags.", "Its examples included Kites palm-sized bags.")
        self.assertTrue(d.accept, d)

    def test_general_word_not_accepted(self):
        canon = "Many bags were small. Mini bags were popular."
        d = decide(canon, "Many bags were small. Many bags were popular.", "Many bags were small. Many bags were popular.")
        self.assertFalse(d.accept)  # mini->many: 一般語

    def test_sentence_initial_capital_cmu_word_without_ledger_rejected(self):
        cmu = lambda t: t in {"retailer", "sales", "fell"}
        zipf = lambda t: 3.0  # 一般語基準未満でも、文頭大文字だけでは固有名詞の根拠にしない
        d = decide("Retailer sales fell.", "Real tailor sales fell.", "Real tailor sales fell.", cmu_has=cmu, zipf=zipf)
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_NOT_PROPER_EVIDENCE)

    def test_sentence_initial_capital_with_ledger_accepted(self):
        cmu = lambda t: t in {"retailer", "sales", "fell"}
        zipf = lambda t: 3.0
        d = decide("Retailer sales fell.", "Real tailor sales fell.", "Real tailor sales fell.", cmu_has=cmu, zipf=zipf,
                   ledger_surfaces=frozenset({"retailer"}))
        self.assertTrue(d.accept, d)

    def test_initials_do_not_count_as_sentence_start(self):
        ok, ev = pol.proper_noun_evidence("gruen", "A study by L. Mimoun and A. Gruen was published.", cmu_has=lambda t: True)
        self.assertTrue(ok)
        self.assertEqual(ev, "capitalized_midsentence")

    def test_allcaps_brand_evidence(self):
        ok, ev = pol.proper_noun_evidence("elle", "ELLE included mini bags.", cmu_has=lambda t: True)
        self.assertTrue(ok)
        self.assertEqual(ev, "allcaps")

    def test_word_deletion_rejected(self):
        d = decide("Toteme and Khaite showed bags.", "Toteme showed bags.", "Toteme showed bags.")
        self.assertFalse(d.accept)

    def test_number_mismatch_not_accepted(self):
        d = decide("Melos ran 3 miles.", "Mello ran 5 miles.", "Mello ran 5 miles.")
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_PRIMARY_NOT_ENTITY_ONLY)

    def test_negation_mismatch_not_accepted(self):
        d = decide("Melos did not run.", "Mello did run.", "Mello did run.")
        self.assertFalse(d.accept)

    def test_other_content_word_error_not_accepted(self):
        d = decide("Melos began to increase speed.", "Mello began to decrease speed.", "Mello began to decrease speed.")
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_PRIMARY_NOT_ENTITY_ONLY)

    def test_tts_failure_not_accepted(self):
        d = decide("Melos said hello to everyone at the gate today.", "ok", "ok")
        self.assertFalse(d.accept)

    def test_low_similarity_rejected(self):
        d = decide("Space news mentioned Meink today.", "Space news mentioned mc today.", "Space news mentioned mc today.")
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_LOW_SIMILARITY)

    def test_too_many_diffs_rejected(self):
        canon = "Melos met Toteme and Khaite near Altuzarra."
        d = decide(canon, "Mello met Totem and Kite near Altazara.", "Mello met Totem and Kite near Altazara.", max_diffs=2)
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_TOO_MANY_DIFFS)

    def test_secondary_missing_rejected(self):
        d = decide("Melos said.", "Mello said.", None)
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_SECONDARY_MISSING)


class ScopeGateTest(unittest.TestCase):
    def test_kp_dual_required_rejected(self):
        d = decide("Melos said.", "Mello said.", "Mellow said.", dual_required=True)
        self.assertFalse(d.accept)
        self.assertEqual(d.reason, pol.R_DUAL)

    def test_key_phrase_and_heading_roles_rejected(self):
        for role in ("KEY_PHRASE", "HEADING_READOUT", None):
            d = decide("Melos said.", "Mello said.", "Mellow said.", role=role)
            self.assertFalse(d.accept, role)
            self.assertEqual(d.reason, pol.R_ROLE)

    def test_five_english_roles_applicable(self):
        for role in ("FULL_STORY", "COMMENT", "PREVIEW", "TOPIC_INTRO", "IN_ONE_LINE"):
            self.assertTrue(decide("Melos said.", "Mello said.", "Mellow said.", role=role).accept, role)

    def test_japanese_rejected(self):
        d = decide("Melos said.", "Mello said.", "Mellow said.", lang="ja")
        self.assertEqual(d.reason, pol.R_LANG)

    def test_other_judge_states_rejected(self):
        for st, rc in (("NG_PROTECTED", "p1_value_diff"), ("NG_EXCLUDED", "p2_exclusion:length"),
                       ("NG_SECONDARY_UNAVAILABLE", "secondary_unavailable"), ("NG_BOTH", "secondary_value_diff"),
                       ("NG_PRIMARY_ASR_FAILURE", "primary_asr_failure")):
            d = decide("Melos said.", "Mello said.", "Mellow said.", judge_state=st, judge_reason_code=rc)
            self.assertFalse(d.accept, st)
            self.assertEqual(d.reason, pol.R_JUDGE_STATE)


class SupplyMapAlarmTest(unittest.TestCase):
    def test_supplied_respelling_token_treated_as_proper_noun(self):
        canon = "Its examples included Kate's palm-sized bags."  # Khaite->Kate供給後のTTS入力
        prim = "Its examples included Khaite's palm-sized bags."  # ASRは原綴りを書いた
        sec = "Its examples included Khaite's palm-sized bags."
        self.assertFalse(decide(canon, prim, sec).accept)   # 供給情報なし: Kateは一般語
        d = decide(canon, prim, sec, supply_map={"kate": "khaite"})
        self.assertTrue(d.accept, d)
        self.assertEqual(d.diffs[0].evidence, "supplied_respelling")
        recs = pol.build_alarm_records(d, canonical_text=canon, segment_id="full_story_part1", supply_map={"kate": "khaite"})
        self.assertEqual(recs[0]["proper_noun"], "khaite")
        self.assertEqual(recs[0]["tts_input_token"], "kate")


class AlarmRecordAndRegistryTest(unittest.TestCase):
    def _records(self):
        canon = "The guards went still when Melos spoke."
        d = decide(canon, "The guards went still when Mello spoke.", "The guards went still when Mellow spoke.")
        return d, pol.build_alarm_records(
            d, canonical_text=canon, segment_id="full_story_part1_c3", wav_path="x/narration/full_story_part1_c3.wav",
            wav_sha256="abc", family="Z", article_id="melos", level="a2", role="FULL_STORY", audio_seconds=5.0,
            primary_text="The guards went still when Mello spoke.", secondary_text="The guards went still when Mellow spoke.",
            supply_info={"supplied": False, "reason": sup.R_UNVERIFIED}, ledger_info={"confidence": "low", "pronunciation_hint": "MEE-lahs"})

    def test_required_fields_present(self):
        d, recs = self._records()
        self.assertEqual(len(recs), 1)
        r = recs[0]
        for k in ("proper_noun", "location", "mismatch", "pronunciation_basis", "tts_supply_result", "final_state", "final_state_ja",
                  "alarm_id", "operator_only"):
            self.assertIn(k, r)
        self.assertEqual(r["final_state"], "PASS_WITH_PRONUNCIATION_ALARM")
        self.assertEqual(r["final_state_ja"], "アラーム付き完成")
        self.assertTrue(r["operator_only"])
        self.assertEqual(r["mismatch"]["asr_primary"], "mello")
        self.assertIsNotNone(r["location"]["approx_seconds"])
        self.assertTrue(r["pronunciation_basis"]["has_basis"])
        self.assertEqual(recs[0]["alarm_id"], self._records()[1][0]["alarm_id"])  # 決定的

    def test_not_accepted_gives_no_records(self):
        d = decide("Melos ran 3 miles.", "Mello ran 5 miles.", "Mello ran 5 miles.")
        self.assertEqual(pol.build_alarm_records(d, canonical_text="x"), [])

    def test_derive_from_results_only_adopted_ok_segments(self):
        d, recs = self._records()
        aj = {"state": pol.STATE_ALARM, "pronunciation_alarm_records": recs}
        results = {"segments": {
            "full_story_part1_c3": {"status": "OK", "segment_id": "x", "asr_judgement": aj},
            "full_story_part1_c4": {"status": "STOPPED", "asr_judgement": aj},                      # 未採用
            "full_story_part1_c5": {"status": "OK", "asr_judgement_inherited": aj, "path": "cur/c5.wav"},  # 継承(別segment=別箇所。P-08)
            "full_story_part1_c6": {"status": "OK", "asr_judgement": {"state": "PASS_WITH_WARNING"}},
            "attempts": {"attempts_log": [{"asr_judgement": aj}]},                                  # attempt logは走査しない
        }}
        out = pol.derive_run_alarms(results)
        self.assertEqual(len(out), 2)   # c3(原本) + c5(継承。現runのsegment/wavで表示)
        self.assertEqual(out[0]["proper_noun"], "melos")
        inh = [o for o in out if o["inherited"]][0]
        self.assertEqual(inh["segment_id"], "full_story_part1_c5")
        self.assertEqual(inh["location"]["wav_path"], "cur/c5.wav")
        self.assertEqual(inh["inherited_from"]["segment_id"], "full_story_part1_c3")
        self.assertEqual(pol.count_alarm_states(results), 2)

    def test_registry_does_not_leak_to_pass_with_warning_listening_list(self):
        import er078_pass_with_warning_registry_01 as pww
        d, recs = self._records()
        results = {"segments": {"s": {"status": "OK", "asr_judgement": {"state": pol.STATE_ALARM, "pronunciation_alarm_records": recs}}}}
        self.assertEqual(pww.derive_listening_list(results), [])  # 一般向けページの『事後試聴リスト』にアラーム状態は載らない

    def test_write_run_alarms_writes_only_under_audit_and_is_idempotent(self):
        d, recs = self._records()
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "audit"))
            with open(os.path.join(td, "audit", "tts_generation_results.json"), "w", encoding="utf-8") as f:
                json.dump({"segments": {"s": {"status": "OK", "asr_judgement": {"state": pol.STATE_ALARM, "pronunciation_alarm_records": recs}}}}, f)
            r1 = pol.write_run_alarms(td)
            snap1 = open(r1["json"], encoding="utf-8").read()
            r2 = pol.write_run_alarms(td)
            self.assertEqual(snap1, open(r2["json"], encoding="utf-8").read())
            self.assertEqual(r1["count"], 1)
            files = sorted(os.path.relpath(os.path.join(dp, fn), td) for dp, _, fns in os.walk(td) for fn in fns)
            self.assertTrue(all(f.replace("\\", "/").startswith("audit/") for f in files), files)  # pages等へは書かない
            md = open(r1["md"], encoding="utf-8").read()
            self.assertIn("運営責任者向け", md)
            self.assertIn("アラーム付き完成", md)
            self.assertIn("melos", md)

    def test_write_run_alarms_safe_never_raises(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "audit"))
            with open(os.path.join(td, "audit", "tts_generation_results.json"), "w", encoding="utf-8") as f:
                f.write("{broken json")
            rep = pol.write_run_alarms_safe(td)
            self.assertIsNotNone(rep["error"])
            # results未作成(途中失敗)は『0件』ではなく集計失敗を明示する(OF-PNAP-P-08)
            r2 = pol.write_run_alarms_safe(os.path.join(td, "empty_run"))
            self.assertIsNotNone(r2["error"])
            self.assertIn("アラーム集計失敗", open(r2["md"], encoding="utf-8").read())


    def test_zero_alarm_section_is_still_rendered(self):
        self.assertIn("0件", pol.render_operator_report([]))

    def test_append_alarm_log_idempotent(self):
        d, recs = self._records()
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x", "pronunciation_alarms.jsonl")
            self.assertEqual(pol.append_alarm_log(p, recs), 1)
            self.assertEqual(pol.append_alarm_log(p, recs), 0)
            self.assertEqual(len(open(p, encoding="utf-8").read().strip().splitlines()), 1)
        self.assertEqual(pol.append_alarm_log("nonexistent_never_written/x.jsonl", []), 0)
        self.assertFalse(os.path.exists("nonexistent_never_written"))


def _entry(**kw):
    e = {"surface": "Khaite", "entity_type": "cascade_unresolved_entity", "pronunciation_hint": "kate",
         "expected_pronunciation_ipa": "keɪt", "confidence": "medium", "sources": ["https://www.nylon.com/fashion-designer-pronunciation-guide"],
         "evidence_tier": "QUOTE_VERIFIED"}
    e.update(kw)
    return e


class TtsSupplyTest(unittest.TestCase):
    def plan(self, led, text="Its examples included Khaite's bags.", **kw):
        return sup.plan_supply(text, led, enabled=True, **kw)

    def test_a_tier_auto_supplied_b_tier_requires_approval(self):
        a = _entry(surface="Meink", pronunciation_hint="mink", sources=["https://en.wikipedia.org/wiki/Meink"],
                   evidence=[{"url": "https://en.wikipedia.org/wiki/Meink", "quote": "Meink (pronounced mink) is a brand"}])
        d = self.plan({"a": a}, "Meink spoke.")[0]
        self.assertTrue(d.supplied)
        self.assertEqual(d.tier, "A")
        b = _entry()  # nylon.com media
        d = self.plan({"b": b})[0]
        self.assertFalse(d.supplied)
        self.assertEqual(d.reason, sup.R_B_NOT_APPROVED)
        d = self.plan({"b": _entry(human_approved=True)})[0]
        self.assertTrue(d.supplied)
        self.assertEqual((d.tier, d.respelling), ("B", "Kate"))

    def test_estimated_never_supplied(self):
        for kw in ({"evidence_tier": "UNVERIFIED_AI_OUTPUT"}, {"evidence_tier": None}, {"evidence_tier": "NAME_IN_CITED_PAGE"},
                   {"evidence_tier": "NO_SOURCE", "sources": []}):
            d = self.plan({"x": _entry(**kw)})[0]
            self.assertFalse(d.supplied, kw)
            self.assertEqual(d.reason, sup.R_UNVERIFIED)

    def test_real_ledger_khaite_hint_KAYT_has_no_respelling(self):
        # 実Ledger(2026-10-22時点): khaite hint='KAYT'(非語)。機械変換では供給できず、人が`tts_respelling`を承認登録した場合のみ供給
        d = self.plan({"k": _entry(pronunciation_hint="KAYT", human_approved=True)})[0]
        self.assertFalse(d.supplied)
        self.assertEqual(d.reason, sup.R_NO_RESPELLING)
        d = self.plan({"k": _entry(pronunciation_hint="KAYT", human_approved=True, tts_respelling="Kate")})[0]
        self.assertTrue(d.supplied)

    def test_syllabic_hint_not_used(self):
        for h in ("al-tuh-ZAIR-ah", "ahl-too-ZAH-rah", "MAY-ngk", "one two three four"):
            self.assertIsNone(sup.derive_respelling(_entry(surface="Altuzarra", pronunciation_hint=h)), h)

    def test_disabled_and_excluded_entries_not_supplied(self):
        for kw in ({"ledger_disabled": True}, {"tts_injection_disabled": True}, {"entity_type": "ja_reading_katakana"}):
            d = self.plan({"x": _entry(human_approved=True, **kw)})[0]
            self.assertFalse(d.supplied, kw)

    def test_conflicting_entries_not_supplied(self):
        led = {"a": _entry(human_approved=True, pronunciation_hint="kate"),
               "b": _entry(human_approved=True, pronunciation_hint="kite", entity_type="brand")}
        d = self.plan(led)[0]
        self.assertFalse(d.supplied)
        self.assertEqual(d.reason, sup.R_CONFLICT)

    def test_static_override_surface_not_double_applied(self):
        led = {"r": _entry(surface="Reicher", pronunciation_hint="riker", human_approved=True)}
        d = self.plan(led, "Stephen Reicher explains.", static_overrides={"Reicher": "Riker"})[0]
        self.assertFalse(d.supplied)
        self.assertEqual(d.reason, sup.R_ALREADY_STATIC)

    def test_apply_supply_word_boundary_and_possessive(self):
        decs = self.plan({"k": _entry(human_approved=True)}, "Khaite's bag, khaite and Khaiteful.")
        text, smap = sup.apply_supply("Khaite's bag, khaite and Khaiteful.", decs)
        # OF-PNAP-P-06: 大文字小文字を区別(登録どおりの綴りのみ置換。小文字khaiteは置換しない)
        self.assertEqual(text, "Kate's bag, khaite and Khaiteful.")
        self.assertEqual(smap, {"kate": "khaite"})

    def test_respelling_must_differ_and_be_words(self):
        self.assertIsNone(sup.derive_respelling(_entry(surface="Kate", pronunciation_hint="kate")))
        self.assertIsNone(sup.derive_respelling(_entry(tts_respelling="K8")))

    def test_audit_block_has_basis_fields(self):
        d = self.plan({"k": _entry(human_approved=True)})[0]
        a = d.to_audit()
        for k in ("supplied", "tier", "original", "respelling", "evidence_tier", "human_approved", "source_urls", "reason"):
            self.assertIn(k, a)


class SupplyRegistryTest(unittest.TestCase):
    def tearDown(self):
        sup.clear_registry()

    def test_register_lookup_and_info(self):
        led = {"k": _entry(human_approved=True)}
        text = "Khaite showed bags."
        decs = sup.plan_supply(text, led, enabled=True)
        out, smap = sup.apply_supply(text, decs)
        sup.register_supply(out, decs, smap)
        lk = sup.lookup_supply(out)
        self.assertEqual(lk["supply_map"], {"kate": "khaite"})
        self.assertTrue(sup.supply_info_for("Khaite", lk)["supplied"])
        self.assertEqual(sup.lookup_supply("other text"), {"supply_map": {}, "decisions": []})
        self.assertEqual(sup.supply_info_for("Zzz", lk)["reason"], "no_ledger_entry_or_not_planned")


class RunScopeTest(unittest.TestCase):
    def tearDown(self):
        pol.leave_scope()
        pol.PROPER_NOUN_ALARM_POLICY_ENABLED = False

    def _call(self):
        c = "Melos said."
        return pol.evaluate_alarm_eligibility(
            canonical_text=c, primary_cls=val.classify_asr_match(c, "Mello said."), secondary_cls=val.classify_asr_match(c, "Mellow said."),
            primary_text="Mello said.", secondary_text="Mellow said.", judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted",
            role="FULL_STORY", p3_entry="p3_primary_ng")

    def test_flag_on_but_no_scope_is_inactive_family_abc_unchanged(self):
        pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
        self.assertFalse(pol.is_active_for_run())
        self.assertEqual(self._call().reason, pol.R_DISABLED)

    def test_scope_x_and_z_active_only_with_flag(self):
        for fam in ("X", "Z"):
            pol.enter_scope(fam)
            self.assertFalse(pol.is_active_for_run())  # flag OFF
            pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
            self.assertTrue(pol.is_active_for_run())
            self.assertTrue(self._call().accept)
            pol.PROPER_NOUN_ALARM_POLICY_ENABLED = False
            pol.leave_scope()

    def test_unsupported_scope_rejected(self):
        for fam in ("A", "B", "C", "", None):
            with self.assertRaises(ValueError):
                pol.enter_scope(fam)
        self.assertIsNone(pol.current_scope())


class RealUnifiedJudgeEntryConditionTest(unittest.TestCase):
    """設計の前提(G1)を実judge(er078)で確認する: Primary=固有名詞のみ不一致、Secondary(注入)も不許容のとき、
    judgeは NG_BOTH / secondary_not_accepted を返す(=アラーム受理の入口)。値差のとき・Secondary障害のときは別状態。"""

    def _judge(self, canon, prim, sec, *, sec_ok=True):
        import er078_asr_unified_judge_01 as uj
        cp = val.classify_asr_match(canon, prim)
        primary = uj.PrimaryResult(passed=bool(cp.should_pass), text=prim, label=cp.classification)
        ctx = uj.AttemptCtx(canonical_text=canon, wav_path="x.wav", wav_sha256="sha-test", audio_seconds=3.0, segment_key="full_story_part1",
                            script_version="v0", slot=1, is_last_slot=False, engine="azure", cache=uj.SecondaryCache(), run_state=uj.RunState())

        def sec_fn(_ctx):
            if not sec_ok:
                raise RuntimeError("azure down")
            return sec

        def accept(c, t):
            r = val.classify_asr_match(c, t)
            return bool(r.should_pass), r.classification
        return uj.unified_judge(ctx, primary, sec_fn, lang="en", role="FULL_STORY", secondary_accept_fn=accept), cp

    def test_entity_only_both_engines_gives_ng_both_secondary_not_accepted(self):
        jr, cp = self._judge("Melos said.", "Mello said.", "Mellow said.")
        self.assertFalse(jr.verified)
        self.assertEqual((jr.state, jr.reason_code), (pol.JUDGE_STATE_ELIGIBLE, pol.JUDGE_REASON_ELIGIBLE))
        d = pol.evaluate_alarm_eligibility(
            canonical_text="Melos said.", primary_cls=cp, secondary_cls=val.classify_asr_match("Melos said.", "Mellow said."),
            primary_text="Mello said.", secondary_text="Mellow said.", judge_state=jr.state, judge_reason_code=jr.reason_code,
            role="FULL_STORY", enabled=True, p3_entry=jr.audit_record.get("p3_entry"))
        self.assertTrue(d.accept)
        self.assertEqual(jr.audit_record.get("p3_entry"), "p3_primary_ng")

    def test_secondary_outage_is_not_eligible(self):
        jr, cp = self._judge("Melos said.", "Mello said.", None, sec_ok=False)
        self.assertEqual(jr.state, "NG_SECONDARY_UNAVAILABLE")
        self.assertNotEqual(jr.reason_code, pol.JUDGE_REASON_ELIGIBLE)

    def test_value_diff_is_protected_not_eligible(self):
        jr, cp = self._judge("Melos ran 3 miles.", "Mello ran 5 miles.", "Mello ran 5 miles.")
        self.assertEqual(jr.state, "NG_PROTECTED")

    def test_secondary_confirms_canonical_is_pass_with_warning_no_alarm(self):
        jr, cp = self._judge("Melos said.", "Mello said.", "Melos said.")
        self.assertTrue(jr.verified)
        self.assertEqual(jr.state, "PASS_WITH_WARNING")  # 既存救済が先(SECONDARY_CONFIRMED)。アラーム経路は走らない


if __name__ == "__main__":
    unittest.main()
