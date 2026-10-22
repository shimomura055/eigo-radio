# -*- coding: utf-8 -*-
"""er109_xz_scope_01 + 共有経路(adapter / 統一judge / KP voter / 再評価 / Store guard / 試聴registry)の配線test(API 0・費用0)。
ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04(WIRING_DESIGN_03 §G、Opus M1〜M13)。
実行: .venv\\Scripts\\python.exe -m unittest er109_xz_scope_01_test_01 -v   (pytestでも同じ結果)
構成: G1 scope / G3 決定的ケース(adapter経由) / G4 span説明規則(M7〜M10) / KP票(M5,M11) / Store guard(M1) / rollback / ScopeLeak / 例外時fail-closed。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import wave
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er019_family_x_validation_inheritance_01 as vi
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import er078_pass_with_warning_registry_01 as pww
import er078_reuse_value_guard_01 as rvg
import er103_proper_noun_alarm_policy_01 as pol
import er104_kp_three_asr_vote_01 as kp3v
import er109_asr_orthographic_equivalence_01 as e109
import er109_xz_scope_01 as xz

_WAV = os.path.join(tempfile.gettempdir(), "er109_xz_scope_test_silence.wav")
with wave.open(_WAV, "wb") as _w:
    _w.setnchannels(1)
    _w.setsampwidth(1)
    _w.setframerate(8000)
    _w.writeframes(b"\x00" * 8000)


class Base(unittest.TestCase):
    """各test前後で scope が None であること(pytest autouse fixtureのunittest版: ScopeLeakの検出)。"""

    def setUp(self):
        self.assertIsNone(xz.current_scope(), "前のtestからscopeが漏れている")
        self._patches = [
            mock.patch.object(sec, "_resolve_unresolved_entity_for_review", lambda span: {"pronunciation_hint": "", "confidence": "unconfirmed", "sources": []}),
            mock.patch.object(sec, "_log_human_review", lambda d: None),
            mock.patch.object(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None),
            mock.patch.object(routing, "transcribe", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Primary#2 forbidden"))),
        ]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in reversed(self._patches)])

    def tearDown(self):
        self.assertIsNone(xz.current_scope(), "testがscopeを残した")

    # ---- adapter(本物)をmock Secondary/Whisperで駆動 ----
    def adapter(self, canon, primary, azure=None, *, scope="X", kp=False, whisper=None, seg="full_story_part1", actx_extra=None):
        az = azure if azure is not None else primary
        actx = {"slot": 1, "is_last_slot": True}
        if kp:
            actx["vote_required"] = True
            actx["vote_whisper_fn"] = lambda: kp3v.make_voter("whisper", canon, whisper if whisper is not None else primary, lang="en")
        actx.update(actx_extra or {})
        with mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", lambda w, language="en-US", phrases=None, **kw: (az, None)):
            sec.reset_secondary_cache()

            def go():
                return sec.evaluate_attempt_with_cascade_detail(canon, primary, [], _WAV, language="en-US", cascade_enabled=True,
                                                                segment_id=(None if kp else seg), attempt_ctx=actx)
            if scope in ("X", "Z"):
                with pol.run_scope(scope), xz.run_scope(scope):
                    return go()
            return go()


# ============================================================ G1 scope
class ScopeTests(Base):
    def test_public_surface_only_run_scope_and_family_scope(self):
        public = {n for n in dir(xz) if not n.startswith("_")}
        self.assertIn("run_scope", public)
        self.assertIn("family_scope", public)
        self.assertNotIn("enter_scope", public)         # M3
        self.assertNotIn("leave_scope", public)
        self.assertTrue(hasattr(xz, "_enter_scope"))

    def test_unsupported_family_rejected(self):
        for bad in ("A", "B", "C", "Y", "x", "z", "", None, "XZ"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    with xz.run_scope(bad):
                        pass
                with self.assertRaises(ValueError):
                    xz.family_scope(bad)
        self.assertIsNone(xz.current_scope())

    def test_run_scope_nested_and_restore(self):
        with xz.run_scope("X"):
            self.assertEqual(xz.current_scope(), "X")
            with xz.run_scope("Z"):               # 入れ子は外側scopeを維持
                self.assertEqual(xz.current_scope(), "X")
            self.assertEqual(xz.current_scope(), "X")
        self.assertIsNone(xz.current_scope())

    def test_family_scope_decorator(self):
        seen = []

        @xz.family_scope("Z")
        def stage(a, b=2):
            seen.append(xz.current_scope())
            return a + b
        self.assertEqual(stage(1, b=3), 4)
        self.assertEqual(seen, ["Z"])
        self.assertEqual(stage.__er109_scoped__, "Z")
        self.assertEqual(stage.__name__, "stage")
        self.assertIsNone(xz.current_scope())

    def test_scope_restored_on_exception_stop_and_keyboard_interrupt(self):
        for exc in (RuntimeError("boom"), SystemExit(3), KeyboardInterrupt()):
            with self.subTest(exc=type(exc).__name__):
                @xz.family_scope("X")
                def stage():
                    raise exc
                with self.assertRaises(type(exc)):
                    stage()
                self.assertIsNone(xz.current_scope())

    def test_flag_false_means_inactive_even_in_scope(self):
        with xz.run_scope("X"):
            self.assertTrue(xz.is_active_for_run())
            with mock.patch.object(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False):
                self.assertFalse(xz.is_active_for_run())
                self.assertIsNone(xz.decision("Pump one's fist.", "Pump 1's fist."))      # M4: flag確認はメモ外=即座に効く
            self.assertIsNotNone(xz.decision("Pump one's fist.", "Pump 1's fist."))

    def test_scope_unset_means_inactive(self):
        self.assertFalse(xz.is_active_for_run())
        self.assertIsNone(xz.decision("Pump one's fist.", "Pump 1's fist."))

    def test_memo_is_evaluate_only_scope_not_memoized(self):
        xz._evaluate_cached.cache_clear()
        with xz.run_scope("X"):
            xz.decision("Pump one's fist.", "Pump 1's fist.")
        self.assertIsNone(xz.decision("Pump one's fist.", "Pump 1's fist."))               # メモ済みでもscope外はNone
        self.assertEqual(xz._evaluate_cached.cache_info().hits + xz._evaluate_cached.cache_info().misses, 1)

    def test_decision_is_english_only(self):
        with xz.run_scope("X"):
            self.assertIsNone(xz.decision("Pump one's fist.", "Pump 1's fist.", lang="ja"))
            self.assertIsNone(xz.decision("", "x"))
            self.assertIsNone(xz.decision("Pump one's fist.", None))
            self.assertIsNone(xz.decision("Pump one's fist.", "   "))

    def test_decision_exception_is_fail_closed_and_recorded(self):
        sink = {}
        with xz.run_scope("X"):
            with mock.patch.object(xz, "_evaluate_cached", side_effect=RuntimeError("er109 boom")):
                self.assertIsNone(xz.decision("Pump one's fist.", "Pump 1's fist.", sink=sink))
        self.assertIn("er109 boom", sink["orthographic_equivalence_errors"][0])


# ============================================================ G3 決定的ケース(adapter経由)
class DeterministicCases(Base):
    def aj(self, d):
        return d["asr_judgement"]

    def test_one_s_vs_1_s_passes_without_warning(self):
        d = self.adapter("Pump one's fist.", "Pump 1's fist.")
        aj = self.aj(d)
        self.assertTrue(d["verified"])
        self.assertEqual((aj["state"], aj["warnings"]), ("PASS", []))
        self.assertEqual(d["final_status"], xz.ORTHO_LABEL)
        self.assertTrue(aj["orthographic_equivalence"]["applied"])
        self.assertTrue(aj["final_gate"]["span_unlock"]["explained"])
        self.assertEqual(aj["primary"]["equivalence_basis"], xz.ORTHO_BASIS)
        self.assertNotIn(xz.ORTHO_BASIS, uj.APPROVED_EQUIVALENCE_BASES)                  # 最終ゲートを丸ごとskipしない
        self.assertIn("orthographic_er109", aj["adapter"]["layers"])

    def test_same_input_scope_unset_is_the_old_ng(self):
        d = self.adapter("Pump one's fist.", "Pump 1's fist.", scope=None)
        self.assertFalse(d["verified"])
        self.assertEqual(self.aj(d)["reason_code"], "p1_value_diff")
        self.assertNotIn("orthographic_equivalence", self.aj(d))

    def test_no_vs_know_is_pass_with_warning_and_recorded(self):
        d = self.adapter("I said no.", "I said know.")
        aj = self.aj(d)
        self.assertTrue(d["verified"])
        self.assertEqual(aj["state"], "PASS_WITH_WARNING")
        self.assertIn(xz.W_ORTHO_NEGATION, aj["warnings"])                              # M7: 否定差を解除したら必ずPASS_WITH_WARNING
        self.assertTrue(aj["final_gate"]["span_unlock"]["detail"]["negation_spans"])
        spans = aj["orthographic_equivalence"]["sites"][0]["er109"]["spans"]
        self.assertEqual(spans[0]["warnings"], ["negation_word_homophone"])

    def test_negatives_stay_ng(self):
        cases = [("We have two cats.", "We have one cats."),                 # 実数値差
                 ("I did not go.", "I did go."),                            # not脱落
                 ("I can't go.", "I can go."),                              # can't <-> can
                 ("I don't know.", "I do know."),                           # don't <-> do
                 ("Take part in it.", "Take apart in it."),
                 ("Pump one's fist twice, 3 times.", "Pump 1's fist twice, 4 times."),      # one's->1's + 別の実数値差
                 ("I said no and did not go.", "I said know and did go.")]  # 否定語がspan内外にまたがる
        for c, a in cases:
            with self.subTest(c=c, a=a):
                d = self.adapter(c, a)
                self.assertFalse(d["verified"])

    def test_er109_level_negatives(self):
        with xz.run_scope("X"):
            for c, a in [("He is lead.", "He is led."), ("Take part", "Take apart"), ("Visit St. John.", "Visit Street John."),
                         ("We have two cats.", "We have one cats."), ("I can't go.", "I can go."), ("I don't know.", "I do know.")]:
                with self.subTest(c=c, a=a):
                    self.assertIsNone(xz.decision(c, a))

    def test_point_to_vs_point_2_is_ambiguous_ng_in_body_and_secondary(self):
        d = self.adapter("Point to the map.", "Point 2. the map.")                       # Primary/Secondaryとも'Point 2.'
        aj = self.aj(d)
        self.assertFalse(d["verified"])
        self.assertEqual(aj["reason_code"], "secondary_ambiguous_value_not_same_surface")   # 本文はP3降格、SecondaryでもNG
        self.assertEqual(aj["value_guard"]["primary"]["kind"], "AMBIGUOUS")

    def test_secondary_ortho_acceptance_gets_secondary_confirmed_and_ortho_warning(self):
        d = self.adapter("I said no.", "I sed no.", azure="I said know.")
        aj = self.aj(d)
        self.assertTrue(d["verified"])
        self.assertEqual(aj["state"], "PASS_WITH_WARNING")
        self.assertEqual(aj["reason_code"], "secondary_confirmed")
        self.assertIn(uj.W_SECONDARY_CONFIRMED, aj["warnings"])
        self.assertIn(xz.W_ORTHO_NEGATION, aj["warnings"])
        self.assertEqual(aj["secondary"]["label"], xz.ORTHO_LABEL)
        self.assertEqual(d["final_status"], xz.ORTHO_LABEL)
        self.assertEqual([s["site"] for s in aj["orthographic_equivalence"]["sites"]], ["secondary"])
        self.assertTrue(aj["final_gate"]["span_unlock"]["explained"])

    def test_secondary_value_unlock_one_s(self):
        d = self.adapter("Pump one's fist.", "Pump a fist.", azure="Pump 1's fist.")
        aj = self.aj(d)
        self.assertTrue(d["verified"])
        self.assertEqual(aj["secondary"]["label"], xz.ORTHO_LABEL)
        self.assertEqual(aj["warnings"], [uj.W_SECONDARY_CONFIRMED])
        self.assertEqual(self.adapter("Pump one's fist.", "Pump a fist.", azure="Pump 1's fist.", scope=None)["asr_judgement"]["reason_code"],
                         "secondary_value_diff")

    def test_secondary_real_value_diff_not_unlocked(self):
        d = self.adapter("We have two cats.", "We have tu cats.", azure="We have one cats.")
        self.assertFalse(d["verified"])
        self.assertEqual(self.aj(d)["reason_code"], "secondary_value_diff")

    def test_existing_labels_win_p1_order(self):
        # 既存層で合格するものにはorthoは発火しない(層順P1: 既存ラベル・警告の勝敗は不変)
        d = self.adapter("Visit St. John.", "Visit Street John.")
        self.assertTrue(d["verified"])
        self.assertNotEqual(d["final_status"], xz.ORTHO_LABEL)
        self.assertNotIn("orthographic_equivalence", self.aj(d))

    def test_listening_list_html_shows_spans_only_for_ortho_entries(self):
        d = self.adapter("I said no.", "I said know.")
        node = {"segments": {"s1": {"status": "OK", "text": "I said no.", "path": "x.wav", "sha256": "abc", "role": "r",
                                    "asr_judgement": d["asr_judgement"]},
                             "s2": {"status": "OK", "text": "plain", "path": "y.wav", "sha256": "def", "role": "r",
                                    "asr_judgement": {"state": "PASS_WITH_WARNING", "warnings": ["SECONDARY_CONFIRMED"], "reason_code": "secondary_confirmed"}}}}
        html = pww.render_html_section(pww.derive_listening_list(node))
        self.assertIn("er109: no -&gt; know", html.replace("no. -&gt; know.", "no -&gt; know").replace("no.", "no"))
        self.assertEqual(html.count("er109:"), 1)

    def test_listening_list_entry_additive_key(self):
        d = self.adapter("I said no.", "I said know.")
        node = {"segments": {"full_story_part1": {"status": "OK", "text": "I said no.", "path": "x.wav", "sha256": "abc",
                                                   "asr_judgement": d["asr_judgement"]}}}
        lst = pww.derive_listening_list(node)
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0]["orthographic_equivalence"]["warnings"], [xz.W_ORTHO_NEGATION])
        self.assertIn("negation_word_homophone", json.dumps(lst[0]["orthographic_equivalence"]))
        # ortho不使用のPASS_WITH_WARNINGにはキー自体が無い
        plain = {"segments": {"s": {"status": "OK", "asr_judgement": {"state": "PASS_WITH_WARNING", "warnings": ["SECONDARY_CONFIRMED"]}}}}
        self.assertNotIn("orthographic_equivalence", pww.derive_listening_list(plain)[0])


# ============================================================ G4 span説明規則(M7〜M10)
def _dec(canon, text, spans, warnings=()):
    eq = e109.EquivalenceResult(True, "all_diff_spans_phoneme_equal", spans=spans, version=e109.LAYER_VERSION)
    return xz.OrthoDecision(canon, text, eq, tuple(warnings), "X")


def _span(c, a, warnings=()):
    return e109.SpanRecord(list(c), list(a), True, "number_spoken_form", "phoneme_equal", warnings=list(warnings))


def _vgr(*pairs):
    return vg.ValueGuardResult(vg.DIFF, tuple(vg.PairResult(s, h, vg.DIFF, "t") for s, h in pairs))


class ExplainProtectedTests(Base):
    def test_token_boundary(self):
        for unit, ok in [("1's", True), ("21's", False), ("1.5", False), ("1,000", False), ("3:1", False), ("a1", False), ("1", True)]:
            with self.subTest(unit=unit):
                d = _dec("one", unit, [_span(["one"], [unit])])
                ex = xz.explain_protected(d, _vgr((None, "1")), False, "one", unit)
                self.assertEqual(ex.explained, ok, ex.reason)

    def test_one_to_one_assignment(self):
        d = _dec("one's one's", "1's", [_span(["one's"], ["1's"])])
        self.assertFalse(xz.explain_protected(d, _vgr((None, "1"), (None, "1")), False, "one's one's", "1's").explained)
        d2 = _dec("one's one's", "1's 1's", [_span(["one's"], ["1's"]), _span(["one's"], ["1's"])])
        ex = xz.explain_protected(d2, _vgr((None, "1"), (None, "1")), False, "one's one's", "1's 1's")
        self.assertTrue(ex.explained)
        self.assertEqual([m["span_index"] for m in ex.detail["value_pairs"]], [0, 1])          # M8d: 対応表を記録

    def test_src_and_hyp_must_be_in_same_span(self):
        d = _dec("a b", "x y", [_span(["two"], ["x"]), _span(["three"], ["y"])])
        self.assertFalse(xz.explain_protected(d, _vgr(("2", "3")), False, "a b", "x y").explained)
        d2 = _dec("a b", "x y", [_span(["2"], ["3"])])
        self.assertTrue(xz.explain_protected(d2, _vgr(("2", "3")), False, "a b", "x y").explained)

    def test_unexplained_pair_blocks_all(self):
        d = _dec("c", "t", [_span(["one's"], ["1's"])])
        self.assertFalse(xz.explain_protected(d, _vgr((None, "1"), ("2", "3")), False, "c", "t").explained)

    def test_target_mismatch_m9(self):
        d = _dec("c", "1's", [_span(["one's"], ["1's"])])
        self.assertTrue(xz.explain_protected(d, _vgr((None, "1")), False, "c", "1's").explained)
        self.assertFalse(xz.explain_protected(d, _vgr((None, "1")), False, "c", "1's ").explained)
        self.assertFalse(xz.explain_protected(d, _vgr((None, "1")), False, "c2", "1's").explained)
        self.assertFalse(xz.explain_protected(None, _vgr((None, "1")), False, "c", "1's").explained)

    def test_version_mismatch(self):
        eq = e109.EquivalenceResult(True, "x", spans=[_span(["one's"], ["1's"])], version="old_version")
        d = xz.OrthoDecision("c", "1's", eq, (), "X")
        self.assertFalse(xz.explain_protected(d, _vgr((None, "1")), False, "c", "1's").explained)

    def test_ambiguous_pair_never_unlocked(self):
        pairs = (vg.PairResult(None, "2", vg.AMBIGUOUS, "number_vs_homophone_word"), vg.PairResult(None, "1", vg.DIFF, "t"))
        d = _dec("c", "t", [_span(["one's"], ["1's"])])
        self.assertFalse(xz.explain_protected(d, vg.ValueGuardResult(vg.DIFF, pairs), False, "c", "t").explained)

    def test_negation_requires_homophone_warning_on_every_differing_span(self):
        d = _dec("I said no.", "I said know.", [_span(["no."], ["know."])])
        self.assertFalse(xz.explain_protected(d, vg.ValueGuardResult(vg.NO_VALUES), True, "I said no.", "I said know.").explained)
        d2 = _dec("I said no.", "I said know.", [_span(["no"], ["know"], ["negation_word_homophone"])])
        ex = xz.explain_protected(d2, vg.ValueGuardResult(vg.NO_VALUES), True, "I said no.", "I said know.")
        self.assertTrue(ex.explained)
        self.assertEqual(ex.warning_labels, (xz.W_ORTHO_NEGATION,))

    def test_negation_outside_spans_must_match(self):
        d = _dec("no and not", "know and", [_span(["no"], ["know"], ["negation_word_homophone"])])
        self.assertFalse(xz.explain_protected(d, vg.ValueGuardResult(vg.NO_VALUES), True, "no and not", "know and").explained)

    def test_negation_span_count_cannot_exceed_total(self):
        d = _dec("no", "know", [_span(["no", "no"], ["know"], ["negation_word_homophone"])])
        self.assertFalse(xz.explain_protected(d, vg.ValueGuardResult(vg.NO_VALUES), True, "no", "know").explained)

    def test_nothing_to_unlock(self):
        d = _dec("c", "t", [_span(["a"], ["b"])])
        self.assertFalse(xz.explain_protected(d, vg.ValueGuardResult(vg.NO_VALUES), False, "c", "t").explained)


# ============================================================ judge直(M9/M10)
class JudgeLevelTests(Base):
    def _ctx(self, canon):
        return uj.AttemptCtx(canonical_text=canon, wav_sha256="sha-test", segment_key="s", length_ok=True)

    def _secondary_case(self, accepted_preset, accept_label, stext="Pump 1's fist."):
        canon = "Pump one's fist."
        pr = uj.PrimaryResult(passed=False, text="Pump a fist.", label="TRUE_CONTENT_MISMATCH")
        out = uj.SecondaryOutcome(stext, accepted=accepted_preset, label=("PRESET" if accepted_preset is not None else ""))

        def accept(c, s):
            return True, accept_label
        with xz.run_scope("X"):
            return uj.unified_judge(self._ctx(canon), pr, lambda c: out, lang="en", role=None, secondary_accept_fn=accept)

    def test_m10_ortho_label_unlocks(self):
        jr = self._secondary_case(None, xz.ORTHO_LABEL)
        self.assertTrue(jr.verified)
        self.assertEqual(jr.state, "PASS_WITH_WARNING")

    def test_m10_provider_preset_accepted_stays_ng(self):
        jr = self._secondary_case(True, xz.ORTHO_LABEL)
        self.assertEqual((jr.state, jr.reason_code), ("NG_BOTH", "secondary_value_diff"))

    def test_m10_non_ortho_acceptance_stays_ng(self):
        for label in ("HOMOPHONE_EQUIVALENT", "M1_MULTI_CANDIDATE", "SECONDARY_ASR_CORROBORATED_MATCH"):
            with self.subTest(label=label):
                jr = self._secondary_case(None, label)
                self.assertEqual((jr.state, jr.reason_code), ("NG_BOTH", "secondary_value_diff"))

    def test_m10_unlock_needs_scope(self):
        pr = uj.PrimaryResult(passed=False, text="Pump a fist.", label="x")
        jr = uj.unified_judge(self._ctx("Pump one's fist."), pr, lambda c: uj.SecondaryOutcome("Pump 1's fist."), lang="en", role=None,
                              secondary_accept_fn=lambda c, s: (True, xz.ORTHO_LABEL))
        self.assertEqual((jr.state, jr.reason_code), ("NG_BOTH", "secondary_value_diff"))

    def test_m10_secondary_ambiguous_is_ng(self):
        canon = "Point to the map."
        pr = uj.PrimaryResult(passed=False, text="Pint to the map.", label="x")
        with xz.run_scope("X"):
            jr = uj.unified_judge(self._ctx(canon), pr, lambda c: uj.SecondaryOutcome("Point 2. the map."), lang="en", role=None,
                                  secondary_accept_fn=lambda c, s: (True, xz.ORTHO_LABEL))
        self.assertFalse(jr.verified)

    def test_m9_primary_gate_uses_decision_target_only(self):
        canon, t = "Pump one's fist.", "Pump 1's fist."
        with xz.run_scope("X"):
            dec = xz.decision(canon, t)
            ok = uj.unified_judge(self._ctx(canon), uj.PrimaryResult(True, t, xz.ORTHO_LABEL, xz.ORTHO_BASIS, signals={"er109_decision": dec}),
                                  lambda c: None, lang="en", role=None)
            self.assertEqual(ok.state, "PASS")
            # adopted_text(別転写)に対してはdecisionを流用して解除しない
            bad = uj.unified_judge(self._ctx(canon), uj.PrimaryResult(True, t, xz.ORTHO_LABEL, xz.ORTHO_BASIS, signals={"er109_decision": dec},
                                                                       adopted_text=t + " "), lambda c: None, lang="en", role=None)
            self.assertEqual((bad.state, bad.reason_code), ("NG_PROTECTED", "final_gate_value_diff"))

    def test_primary_not_ortho_basis_never_unlocks(self):
        canon, t = "Pump one's fist.", "Pump 1's fist."
        with xz.run_scope("X"):
            jr = uj.unified_judge(self._ctx(canon), uj.PrimaryResult(True, t, "SOMETHING", None), lambda c: None, lang="en", role=None)
        self.assertEqual(jr.reason_code, "final_gate_value_diff")


# ============================================================ KP票(M5, M11)
class VoteTests(Base):
    def test_make_voter_ortho_only_in_scope_and_english(self):
        v0 = kp3v.make_voter("whisper", "I said no", "I said know", lang="en")
        self.assertFalse(v0.passed)
        self.assertNotIn("ortho_applied", v0.audit())
        with xz.run_scope("X"):
            v = kp3v.make_voter("whisper", "I said no", "I said know", lang="en")
            self.assertTrue(v.passed)
            self.assertEqual(v.label, xz.ORTHO_LABEL)
            self.assertTrue(v.audit()["ortho_applied"])
            self.assertEqual(v.audit()["ortho_warnings"], [xz.W_ORTHO_NEGATION])
            vj = kp3v.make_voter("whisper", "I said no", "I said know", lang="ja")                # M5: en以外はer109を呼ばない
            self.assertFalse(vj.passed)

    def test_kp_p_ortho_and_s_pass_dual_with_warning(self):
        d = self.adapter("I said no", "I said know", azure="I said no", kp=True, whisper="I said no")
        aj = d["asr_judgement"]
        self.assertTrue(d["verified"])
        self.assertEqual((aj["state"], aj["vote"]["row"]), ("PASS_WITH_WARNING", "P+S"))
        self.assertIn(xz.W_ORTHO_NEGATION, aj["warnings"])
        self.assertEqual(aj["vote"]["version"], "kp_vote_check_v1")                            # version据え置き
        self.assertEqual(aj["vote"]["ortho_layer_version"], e109.LAYER_VERSION)                # M11
        self.assertEqual(aj["vote"]["ortho_scope"], "X")
        self.assertTrue(aj["vote"]["primary"]["ortho_applied"])
        self.assertNotIn("ortho_applied", aj["vote"]["secondary"])

    def test_kp_s_ortho_pass_adds_warning_from_s_transcript(self):
        d = self.adapter("I said no", "I said no", azure="I said know", kp=True, whisper="I said no")
        aj = d["asr_judgement"]
        self.assertTrue(d["verified"])
        self.assertIn(xz.W_ORTHO_NEGATION, aj["warnings"])
        self.assertTrue(aj["vote"]["secondary"]["ortho_applied"])
        self.assertEqual(aj["vote"]["secondary"]["label"], xz.ORTHO_LABEL)

    def test_kp_w_ortho_vote_adds_warning(self):
        # P NG(別語) / S PASS(完全一致) / W ortho -> row S+W。PASS票(S,W)からのORTHO警告合成
        d = self.adapter("I said no", "I sed no", azure="I said no", kp=True, whisper="I said know")
        aj = d["asr_judgement"]
        self.assertTrue(d["verified"], aj["reason_code"])
        self.assertEqual(aj["vote"]["row"], "S+W")
        self.assertIn(uj.W_SECONDARY_CONFIRMED, aj["warnings"])
        self.assertIn(xz.W_ORTHO_NEGATION, aj["warnings"])
        self.assertTrue(aj["vote"]["whisper"]["ortho_applied"])

    def test_voter_ortho_exception_is_fail_closed_and_recorded(self):
        with xz.run_scope("X"):
            with mock.patch.object(xz, "_evaluate_cached", side_effect=RuntimeError("er109 boom")):
                v = kp3v.make_voter("whisper", "I said no", "I said know", lang="en")
        self.assertFalse(v.passed)                                   # 従来の厳しい判定(同値ではない)
        self.assertIn("er109 boom", v.audit()["ortho_error"])

    def test_adapter_records_ortho_exception_and_keeps_old_ng(self):
        with mock.patch.object(xz, "_evaluate_cached", side_effect=RuntimeError("er109 boom")):
            d = self.adapter("I said no.", "I said know.")
        self.assertFalse(d["verified"])
        self.assertIn("er109 boom", d["asr_judgement"]["orthographic_equivalence_errors"][0])
        self.assertEqual(d["asr_judgement"]["reason_code"], "p1_negation_diff")        # runは止まらず従来のNG理由

    def test_kp_scope_unset_vote_audit_has_no_ortho_keys(self):
        d = self.adapter("I said no", "I said no", azure="I said no", kp=True, scope=None)
        self.assertNotIn("ortho_layer_version", d["asr_judgement"]["vote"])
        self.assertNotIn("ortho_scope", d["asr_judgement"]["vote"])


# ============================================================ Store guard(M1) + rollback
class StoreGuardTests(Base):
    LAYERS = {
        "orthographic_equivalence.applied": {"orthographic_equivalence": {"applied": True}},
        "primary.label": {"primary": {"label": xz.ORTHO_LABEL}},
        "secondary.label": {"secondary": {"label": xz.ORTHO_LABEL}},
        "vote.primary.label": {"vote": {"primary": {"label": xz.ORTHO_LABEL}}},
        "vote.secondary.label": {"vote": {"secondary": {"label": xz.ORTHO_LABEL}}},
        "vote.whisper.label": {"vote": {"whisper": {"label": xz.ORTHO_LABEL}}},
        "warning.negation": {"warnings": [xz.W_ORTHO_NEGATION]},
        "warning.nonrep": {"warnings": [xz.W_ORTHO_NONREP]},
    }

    def _entry(self, key, mark):
        aj = {"state": "PASS", "warnings": []}
        aj.update(mark)
        return {"text": "I said no.", "asr_text": "I said know.", key: aj}

    def test_blocked_out_of_scope_for_every_layer_and_both_keys(self):
        for lname, mark in self.LAYERS.items():
            for key in ("asr_judgement", "asr_judgement_inherited"):
                for follows in (False, True):
                    with self.subTest(layer=lname, key=key, vote_gate_follows=follows):
                        g = rvg.guard_entry(self._entry(key, mark), label="t", canonical_text="I said no.", kp_vote_gate_follows=follows)
                        self.assertTrue(g["blocked"])
                        self.assertEqual(g["reason"], xz.OUT_OF_SCOPE_BLOCK_REASON)       # kp_vote_gate_follows skipより前

    def test_not_blocked_in_scope(self):
        for key in ("asr_judgement", "asr_judgement_inherited"):
            with xz.run_scope("X"):
                g = rvg.guard_entry(self._entry(key, self.LAYERS["orthographic_equivalence.applied"]), label="t", canonical_text="I said no.")
            self.assertNotEqual(g.get("reason"), xz.OUT_OF_SCOPE_BLOCK_REASON)
            self.assertFalse(g["blocked"], g)
            with xz.run_scope("Z"):
                g = rvg.guard_entry(self._entry(key, self.LAYERS["orthographic_equivalence.applied"]), label="t", canonical_text="I said no.")
            self.assertFalse(g["blocked"], g)

    def test_entries_without_ortho_mark_are_unaffected(self):
        for mark in ({}, {"primary": {"label": "EXACT_MATCH"}}, {"warnings": ["SECONDARY_CONFIRMED"]}, {"vote": {"primary": {"label": "x"}}}):
            e = self._entry("asr_judgement", mark)
            g = rvg.guard_entry(e, label="t", canonical_text="I said no.")
            self.assertNotEqual(g.get("reason"), xz.OUT_OF_SCOPE_BLOCK_REASON)

    def test_rollback_flag_false_blocks_ortho_entries_even_in_scope(self):
        e = self._entry("asr_judgement", self.LAYERS["orthographic_equivalence.applied"])
        with mock.patch.object(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False):
            with xz.run_scope("X"):
                g = rvg.guard_entry(e, label="t", canonical_text="I said no.")
        self.assertTrue(g["blocked"])
        self.assertEqual(g["reason"], xz.OUT_OF_SCOPE_BLOCK_REASON)

    def test_rollback_flag_false_gives_old_results_in_scope(self):
        cases = [("Pump one's fist.", "Pump 1's fist."), ("I said no.", "I said know."), ("I said no.", "I sed no.", "I said know.")]
        for c in cases:
            with self.subTest(c=c):
                with mock.patch.object(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False):
                    off = self.adapter(*c)
                none = self.adapter(*c, scope=None)
                self.assertEqual((off["verified"], off["asr_judgement"]["state"], off["asr_judgement"]["reason_code"], off["final_status"]),
                                 (none["verified"], none["asr_judgement"]["state"], none["asr_judgement"]["reason_code"], none["final_status"]))
                self.assertNotIn("orthographic_equivalence", off["asr_judgement"])

    def test_store_end_to_end_ortho_entry_reuse_in_scope_and_regenerate_out_of_scope(self):
        import er006_master_audio_store_01 as store
        d = self.adapter("I said no.", "I said know.")
        aj = d["asr_judgement"]
        self.assertTrue(xz.ortho_contributed(aj))
        tmp = tempfile.mkdtemp()
        with mock.patch.object(store, "STORE_DIR", f"{tmp}/store"), mock.patch.object(store, "AUDIO_DIR", f"{tmp}/store/audio"), \
                mock.patch.object(store, "MANIFEST_PATH", f"{tmp}/store/manifest.json"), mock.patch.object(store, "TELEMETRY_PATH", f"{tmp}/store/t.jsonl"):
            os.makedirs(f"{tmp}/store", exist_ok=True)
            key = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id="m", canonical_text="I said no.")
            calls = []

            def gen(out):
                calls.append(out)
                with open(out, "wb") as f:
                    f.write(b"RIFFxxxx")
                return {"status": "OK", "sha256": "s", "asr_verified": True, "asr_text": "I said know.", "asr_judgement": aj}
            with xz.run_scope("X"):
                r1 = store.get_or_generate(key, f"{tmp}/o1.wav", gen)
                r2 = store.get_or_generate(key, f"{tmp}/o2.wav", gen)
            self.assertEqual((len(calls), r1["reused"], r2["reused"]), (1, False, True))            # X内: 再利用される
            r3 = store.get_or_generate(key, f"{tmp}/o3.wav", gen)                                    # A/B/C相当(scope外): ブロック -> 再生成
            self.assertEqual((len(calls), r3["reused"], r3["cache_miss_reason"]), (2, False, "reuse_value_guard_blocked"))


# ============================================================ 再評価(rejudge)
class RejudgeTests(Base):
    def test_rejudge_primary_and_accept_fn_in_scope(self):
        e = {"text": "I said no.", "asr_text": "I said know.", "sha256": "z"}
        r0 = vi.rejudge_with_current_judge(dict(e), "b1b", "full_story_part1", force_lang="en")
        self.assertFalse(r0["ok"])
        self.assertNotIn("orthographic_equivalence", r0["asr_judgement_inherited"])
        with xz.run_scope("X"):
            r = vi.rejudge_with_current_judge(dict(e), "b1b", "full_story_part1", force_lang="en")
        self.assertTrue(r["ok"])
        self.assertEqual(r["unified_state"], "PASS_WITH_WARNING")
        self.assertTrue(r["asr_judgement_inherited"]["orthographic_equivalence"]["applied"])
        self.assertIn(xz.W_ORTHO_NEGATION, r["asr_judgement_inherited"]["warnings"])
        # 保存Secondary転写がortho同値(accept_fn側)
        e2 = {"text": "I said no.", "asr_text": "I sed no.", "sha256": "z2", "scg_info": {"secondary_transcript": "I said know."}}
        with xz.run_scope("Z"):
            r2 = vi.rejudge_with_current_judge(dict(e2), "b1b", "full_story_part1", force_lang="en")
        self.assertTrue(r2["ok"], r2)
        self.assertTrue(xz.ortho_contributed(r2["asr_judgement_inherited"]))

    def test_rejudge_inherited_record_keeps_ortho_mark_when_original_had_judgement(self):
        e = {"text": "I said no.", "asr_text": "I said know.", "sha256": "z",
             "asr_judgement": {"state": "PASS", "warnings": [], "primary": {"text": "I said know.", "passed": True}, "secondary": {}}}
        with xz.run_scope("X"):
            r = vi.rejudge_with_current_judge(dict(e), "b1b", "full_story_part1", force_lang="en")
        self.assertTrue(r["ok"], r)
        self.assertTrue(xz.ortho_contributed(r["asr_judgement_inherited"]))

    def test_guard_entry_end_to_end_reuse_only_in_scope(self):
        e = {"text": "Pump one's fist.", "asr_text": "Pump 1's fist."}
        g_none = rvg.guard_entry(dict(e), label="t", canonical_text="Pump one's fist.")
        self.assertTrue(g_none["blocked"])                       # 従来: p1_value_diff -> 再生成
        with xz.run_scope("X"):
            g_x = rvg.guard_entry(dict(e), label="t", canonical_text="Pump one's fist.")
        self.assertFalse(g_x["blocked"], g_x)


if __name__ == "__main__":
    unittest.main()
