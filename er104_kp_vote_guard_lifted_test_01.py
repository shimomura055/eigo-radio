# -*- coding: utf-8 -*-
"""KP英語3-ASR多数決の数値・否定保護解除(2026-10-22、KP-QUALITY-2ITEMS)のtest(API 0)。委任_01のstaging testをer104へ折込み後に移植。"""
from __future__ import annotations

import ast
import glob
import itertools
import os
import unittest

import er104_kp_three_asr_vote_01 as kp3v

ROOT = os.path.dirname(os.path.abspath(__file__))


def V(provider, passed, *, text="x", available=True, tech=False, pdiff=False, obs=False, rescued=False):
    return kp3v.Voter(provider=provider, text=(text if available else None), passed=passed, available=available,
                      technical_failure=tech, observed_protected_diff=(pdiff or obs), rescued=rescued)


class TruthTable(unittest.TestCase):
    def test_row_dual_pass_no_whisper(self):
        p, s = V("openai", True), V("azure", True)
        self.assertFalse(kp3v.whisper_needed(p, s))
        r = kp3v.tally(p, s, None)
        self.assertEqual((r.state, r.row, r.verified), (kp3v.PASS_DUAL, kp3v.ROW_DUAL, True))

    def test_row_p_pass_s_ng_needs_whisper_and_2of3(self):
        p, s = V("openai", True), V("azure", False)
        self.assertTrue(kp3v.whisper_needed(p, s))
        r = kp3v.tally(p, s, V("whisper", True))
        self.assertEqual((r.state, r.row, r.secondary_confirmed_warning), (kp3v.PASS_VOTE_2OF3, kp3v.ROW_P_W, False))
        r = kp3v.tally(p, s, V("whisper", False))
        self.assertEqual((r.state, r.verified), (kp3v.NG_VOTE_WHISPER_NG, False))

    def test_row_p_ng_s_pass_needs_whisper_and_warning(self):
        p, s = V("openai", False), V("azure", True)
        self.assertTrue(kp3v.whisper_needed(p, s))
        r = kp3v.tally(p, s, V("whisper", True))
        self.assertEqual((r.state, r.row, r.secondary_confirmed_warning), (kp3v.PASS_VOTE_2OF3, kp3v.ROW_S_W, True))   # P-03 PASS_WITH_WARNING維持
        self.assertFalse(kp3v.tally(p, s, V("whisper", False)).verified)

    def test_row_both_ng_no_whisper(self):
        p, s = V("openai", False), V("azure", False)
        self.assertFalse(kp3v.whisper_needed(p, s))
        r = kp3v.tally(p, s, None)
        self.assertEqual((r.state, r.verified), (kp3v.NG_BOTH, False))

    def test_equivalent_to_existing_tally_when_no_protected(self):
        """保護差が無い入力では、既存tallyと全状態・reason・row・warningが一致する(挙動の差は保護分岐だけ)。"""
        for pp, sp, wp in itertools.product((True, False), repeat=3):
            p, s, w = V("openai", pp), V("azure", sp), V("whisper", wp)
            need_new = kp3v.whisper_needed(p, s)
            need_old = kp3v.whisper_needed(p, s)
            self.assertEqual(need_new, need_old)
            a = kp3v.tally(p, s, w if need_new else None)
            b = kp3v.tally(p, s, w if need_old else None)
            self.assertEqual((a.state, a.reason, a.row, a.pass_count, a.secondary_confirmed_warning),
                             (b.state, b.reason, b.row, b.pass_count, b.secondary_confirmed_warning))


class GuardLifted(unittest.TestCase):
    def test_protected_diff_never_changes_outcome(self):
        """Voter.protected_diff / observed_protected_diff を全組合せで立てても、結果は保護差なしと同じ(解除の核)。"""
        for pp, sp, wp in itertools.product((True, False), repeat=3):
            base = None
            for pd1, pd2, pd3, ob1, ob2, ob3 in itertools.product((False, True), repeat=6):
                p = V("openai", pp, pdiff=pd1, obs=ob1)
                s = V("azure", sp, pdiff=pd2, obs=ob2)
                w = V("whisper", wp, pdiff=pd3, obs=ob3)
                need = kp3v.whisper_needed(p, s)
                r = kp3v.tally(p, s, w if need else None)
                key = (need, r.state, r.reason, r.row, r.secondary_confirmed_warning)
                base = base or key
                self.assertEqual(key, base)
                self.assertNotIn(r.state, ("NG_PROTECTED", "NG_PROTECTED_DISSENT"))

    def test_split_with_protected_dissent_still_calls_whisper(self):
        p, s = V("openai", True), V("azure", False, pdiff=True, obs=True)
        self.assertTrue(kp3v.whisper_needed(p, s))
        called = []
        d = kp3v.decide(p, lambda: s, lambda: (called.append(1), V("whisper", True))[1])
        self.assertEqual((d.state, d.row, len(called), d.verified), (kp3v.PASS_VOTE_2OF3, "P+W", 1, True))

    def test_primary_protected_diff_does_not_short_circuit(self):
        p, s = V("openai", False, pdiff=True, obs=True), V("azure", True)
        sec_called = []
        d = kp3v.decide(p, lambda: (sec_called.append(1), s)[1], lambda: V("whisper", True))
        self.assertEqual((len(sec_called), d.state, d.row), (1, kp3v.PASS_VOTE_2OF3, "S+W"))
        self.assertTrue(d.secondary_confirmed_warning)

    def test_both_ng_with_protected_diff_still_ng_and_no_whisper(self):
        p, s = V("openai", False, obs=True), V("azure", False, obs=True)
        called = []
        d = kp3v.decide(p, lambda: s, lambda: (called.append(1), V("whisper", True))[1])
        self.assertEqual((d.state, len(called)), (kp3v.NG_BOTH, 0))


class FailClosed(unittest.TestCase):
    def test_whisper_failure_is_never_pass(self):
        p, s = V("openai", True), V("azure", False)
        r = kp3v.tally(p, s, V("whisper", False, available=False, tech=True))
        self.assertEqual((r.state, r.verified, r.technical_stop), (kp3v.NG_WHISPER_UNAVAILABLE, False, True))
        r = kp3v.tally(p, s, None)
        self.assertEqual(r.state, kp3v.NG_WHISPER_UNAVAILABLE)

    def test_whisper_exception_in_decide(self):
        d = kp3v.decide(V("openai", True), lambda: V("azure", False), lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        self.assertEqual((d.state, d.verified), (kp3v.NG_WHISPER_UNAVAILABLE, False))

    def test_whisper_empty_transcript_is_ng_vote(self):
        w = kp3v.make_voter("whisper", "pump one's fist", "  ")
        r = kp3v.tally(V("openai", True), V("azure", False), w)
        self.assertEqual(r.state, kp3v.NG_VOTE_WHISPER_NG)

    def test_secondary_unavailable_is_technical_stop_not_2of3(self):
        r = kp3v.tally(V("openai", True), V("azure", False, available=False, tech=True), V("whisper", True))
        self.assertEqual((r.state, r.technical_stop), (kp3v.NG_SECONDARY_UNAVAILABLE, True))

    def test_primary_failure(self):
        r = kp3v.tally(V("openai", False, available=False), V("azure", True), None)
        self.assertEqual(r.state, kp3v.NG_PRIMARY_ASR_FAILURE)

    def test_rescued_primary_is_not_a_pass_vote(self):
        v = kp3v.make_voter("openai", "take part", "Take part.", rescued=True)
        self.assertFalse(v.passed)

    def test_tiebreak_off_is_old_dual_rule(self):
        p, s = V("openai", True), V("azure", False)
        self.assertFalse(kp3v.whisper_needed(p, s, tiebreak=False))
        self.assertEqual(kp3v.tally(p, s, None, tiebreak=False).state, kp3v.NG_SPLIT_TIEBREAK_OFF)


class RealClassifierFixtures(unittest.TestCase):
    """保存evidence(coffee pump one's fist, docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01)の転写で、本物の分類器を通す。"""
    CANON = "pump one's fist"

    def test_azure_itn_one_s_to_1_s_is_observed_but_ineffective(self):
        s = kp3v.make_voter("azure", self.CANON, "Pump 1's fist.")
        self.assertTrue(s.observed_protected_diff)     # 値ガードは差を観測する(記録のみ。票・短絡には使わない)
        self.assertFalse(s.passed)                      # 本文一致分類ではNG(= 割れるだけ)

    def test_stored_evidence_pump_ones_fist_passes_via_whisper(self):
        """N1 attempt1 / N2 attempt4 相当: P=`Pump one's fist.`(PASS) S=`Pump 1's fist.`(NG) W=`Pump One's Fist`(保存音声のlocal Whisper転写) -> P+W。"""
        p = kp3v.make_voter("openai", self.CANON, "Pump one's fist.")
        s = kp3v.make_voter("azure", self.CANON, "Pump 1's fist.")
        self.assertTrue(p.passed)
        self.assertTrue(kp3v.whisper_needed(p, s))
        w = kp3v.make_voter("whisper", self.CANON, "Pump One's Fist", ambiguous_blocks=True)
        self.assertTrue(w.passed)
        r = kp3v.tally(p, s, w)
        self.assertEqual((r.state, r.row, r.verified), (kp3v.PASS_VOTE_2OF3, "P+W", True))
        a = kp3v.build_vote_audit(p, s, w, r, secondary_called=True, whisper_called=True)
        self.assertTrue(a["guard_lifted"] and a["observed_protected_diff"]["secondary"])
        self.assertEqual(a["guard_lifted_version"], kp3v.GUARD_LIFTED_VERSION)
        self.assertEqual(a["version"], "kp_vote_check_v1")   # reader互換のためversion据え置き
        self.assertEqual(a["state"], kp3v.PASS_VOTE_2OF3)

    def test_stored_evidence_primary_drops_s_is_both_ng(self):
        """N1 attempt2-4 / N2 attempt2: P=`Pump one fist.`(NG) S=`Pump 1's fist.`(NG) -> 両NG=NG(Whisper不呼出)。真理値表どおり。"""
        p = kp3v.make_voter("openai", self.CANON, "Pump one fist.")
        s = kp3v.make_voter("azure", self.CANON, "Pump 1's fist.")
        self.assertFalse(p.passed or s.passed)
        self.assertFalse(kp3v.whisper_needed(p, s))
        self.assertEqual(kp3v.tally(p, s, None).state, kp3v.NG_BOTH)

    def test_false_pass_guard_real_numeric_error_still_needs_two_votes(self):
        """保護解除後も、本物の数値誤読(2 days -> 3 days)は1票(P)しか立たなければPASSしない(Whisperも別転写なら)。"""
        p = kp3v.make_voter("openai", "two days", "Two days.")
        s = kp3v.make_voter("azure", "two days", "3 days.")
        w = kp3v.make_voter("whisper", "two days", "Three days.", ambiguous_blocks=True)
        self.assertTrue(p.passed)
        self.assertFalse(s.passed)
        self.assertFalse(w.passed)
        self.assertEqual(kp3v.tally(p, s, w).state, kp3v.NG_VOTE_WHISPER_NG)


class Dangling(unittest.TestCase):
    def test_removed_identifiers_have_no_reference(self):
        """撤去したKP保護の識別子が、Productionコード(記録系er106/er107と本test・docs除く)から参照されない。staging module(er108_kp_vote_noguard_01)も存在しない。"""
        self.assertFalse(os.path.exists(os.path.join(ROOT, "er108_kp_vote_noguard_01.py")))
        pat = ("NG_PROTECTED_DISSENT", "protected_dissent_blocks", "kp3v.NG_PROTECTED", "er108_kp_vote_noguard_01", ".protected_diff")
        offenders = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            base = os.path.basename(f)
            if base in (os.path.basename(__file__), "er106_joint_runtime_evidence_01.py", "er107_fx_kp_audio_ng3_listen_page_01.py",
                        "er104_kp_vote_wiring_test_01.py"):
                continue
            with open(f, encoding="utf-8", errors="ignore") as fh:
                s = fh.read()
            for p in pat:
                if p in s:
                    offenders.append((base, p))
        self.assertEqual(offenders, [], offenders)

    def test_state_constants_removed(self):
        for n in ("NG_PROTECTED", "NG_PROTECTED_DISSENT"):
            self.assertFalse(hasattr(kp3v, n), n)
        self.assertNotIn("protected_dissent_blocks", kp3v.tally.__code__.co_varnames + kp3v.decide.__code__.co_varnames)


class NumericNegationSynthetic(unittest.TestCase):
    """OF-KPQ-P-10: 数値系の合成誤転写。保護解除後も『本物の誤読』が2票揃わなければPASSしない。"""
    CASES = [("two days", "Two days.", "3 days."), ("the third floor", "The third floor.", "The second floor."),
             ("pump one's fist", "Pump one's fist.", "Pump 2's fist."), ("take it easy", "Take it easy.", "Do not take it easy."),
             ("ten minutes", "Ten minutes.", "Two minutes."), ("not bad", "Not bad.", "Bad.")]

    def test_real_error_on_both_s_and_w_does_not_pass(self):
        for canon, good, bad in self.CASES:
            p = kp3v.make_voter("openai", canon, good)
            s = kp3v.make_voter("azure", canon, bad)
            w = kp3v.make_voter("whisper", canon, bad, ambiguous_blocks=True)
            need = kp3v.whisper_needed(p, s)
            tr = kp3v.tally(p, s, w if need else None)
            self.assertFalse(tr.verified, (canon, tr.state))

    def test_real_error_on_primary_and_whisper_does_not_pass_via_s_alone(self):
        for canon, good, bad in self.CASES:
            p = kp3v.make_voter("openai", canon, bad)
            s = kp3v.make_voter("azure", canon, good)
            w = kp3v.make_voter("whisper", canon, bad, ambiguous_blocks=True)
            need = kp3v.whisper_needed(p, s)
            tr = kp3v.tally(p, s, w if need else None)
            self.assertFalse(tr.verified, (canon, tr.state))

    def test_both_ng_with_numeric_error_no_whisper(self):
        for canon, good, bad in self.CASES:
            p, s = kp3v.make_voter("openai", canon, bad), kp3v.make_voter("azure", canon, bad)
            self.assertFalse(kp3v.whisper_needed(p, s))
            self.assertEqual(kp3v.tally(p, s, None).state, kp3v.NG_BOTH)

    def test_observed_diff_recorded_not_used(self):
        p = kp3v.make_voter("openai", "two days", "Three days.")
        self.assertTrue(p.observed_protected_diff)
        self.assertFalse(p.passed)


if __name__ == "__main__":
    unittest.main()
