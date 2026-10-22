# -*- coding: utf-8 -*-
"""er108_kp_vote_noguard_01 のtest(API 0)。実行: .venv\\Scripts\\python.exe -m unittest er108_kp_vote_noguard_01_test_01 -v"""
from __future__ import annotations

import ast
import glob
import itertools
import os
import unittest

import er104_kp_three_asr_vote_01 as kp3v
import er108_kp_vote_noguard_01 as ng

ROOT = os.path.dirname(os.path.abspath(__file__))


def V(provider, passed, *, text="x", available=True, tech=False, pdiff=False, obs=False, rescued=False):
    return ng.NoGuardVoter(provider=provider, text=(text if available else None), passed=passed, available=available,
                           technical_failure=tech, protected_diff=pdiff, observed_protected_diff=obs, rescued=rescued)


class TruthTable(unittest.TestCase):
    def test_row_dual_pass_no_whisper(self):
        p, s = V("openai", True), V("azure", True)
        self.assertFalse(ng.whisper_needed_noguard(p, s))
        r = ng.tally_noguard(p, s, None)
        self.assertEqual((r.state, r.row, r.verified), (kp3v.PASS_DUAL, kp3v.ROW_DUAL, True))

    def test_row_p_pass_s_ng_needs_whisper_and_2of3(self):
        p, s = V("openai", True), V("azure", False)
        self.assertTrue(ng.whisper_needed_noguard(p, s))
        r = ng.tally_noguard(p, s, V("whisper", True))
        self.assertEqual((r.state, r.row, r.secondary_confirmed_warning), (kp3v.PASS_VOTE_2OF3, kp3v.ROW_P_W, False))
        r = ng.tally_noguard(p, s, V("whisper", False))
        self.assertEqual((r.state, r.verified), (kp3v.NG_VOTE_WHISPER_NG, False))

    def test_row_p_ng_s_pass_needs_whisper_and_warning(self):
        p, s = V("openai", False), V("azure", True)
        self.assertTrue(ng.whisper_needed_noguard(p, s))
        r = ng.tally_noguard(p, s, V("whisper", True))
        self.assertEqual((r.state, r.row, r.secondary_confirmed_warning), (kp3v.PASS_VOTE_2OF3, kp3v.ROW_S_W, True))   # P-03 PASS_WITH_WARNING維持
        self.assertFalse(ng.tally_noguard(p, s, V("whisper", False)).verified)

    def test_row_both_ng_no_whisper(self):
        p, s = V("openai", False), V("azure", False)
        self.assertFalse(ng.whisper_needed_noguard(p, s))
        r = ng.tally_noguard(p, s, None)
        self.assertEqual((r.state, r.verified), (kp3v.NG_BOTH, False))

    def test_equivalent_to_existing_tally_when_no_protected(self):
        """保護差が無い入力では、既存tallyと全状態・reason・row・warningが一致する(挙動の差は保護分岐だけ)。"""
        for pp, sp, wp in itertools.product((True, False), repeat=3):
            p, s, w = V("openai", pp), V("azure", sp), V("whisper", wp)
            need_new = ng.whisper_needed_noguard(p, s)
            need_old = kp3v.whisper_needed(p, s)
            self.assertEqual(need_new, need_old)
            a = ng.tally_noguard(p, s, w if need_new else None)
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
                need = ng.whisper_needed_noguard(p, s)
                r = ng.tally_noguard(p, s, w if need else None)
                key = (need, r.state, r.reason, r.row, r.secondary_confirmed_warning)
                base = base or key
                self.assertEqual(key, base)
                self.assertNotIn(r.state, ng.REMOVED_STATES)

    def test_split_with_protected_dissent_still_calls_whisper(self):
        p, s = V("openai", True), V("azure", False, pdiff=True, obs=True)
        self.assertTrue(ng.whisper_needed_noguard(p, s))
        called = []
        d = ng.decide_noguard(p, lambda: s, lambda: (called.append(1), V("whisper", True))[1])
        self.assertEqual((d.state, d.row, len(called), d.verified), (kp3v.PASS_VOTE_2OF3, "P+W", 1, True))

    def test_primary_protected_diff_does_not_short_circuit(self):
        p, s = V("openai", False, pdiff=True, obs=True), V("azure", True)
        sec_called = []
        d = ng.decide_noguard(p, lambda: (sec_called.append(1), s)[1], lambda: V("whisper", True))
        self.assertEqual((len(sec_called), d.state, d.row), (1, kp3v.PASS_VOTE_2OF3, "S+W"))
        self.assertTrue(d.secondary_confirmed_warning)

    def test_both_ng_with_protected_diff_still_ng_and_no_whisper(self):
        p, s = V("openai", False, obs=True), V("azure", False, obs=True)
        called = []
        d = ng.decide_noguard(p, lambda: s, lambda: (called.append(1), V("whisper", True))[1])
        self.assertEqual((d.state, len(called)), (kp3v.NG_BOTH, 0))


class FailClosed(unittest.TestCase):
    def test_whisper_failure_is_never_pass(self):
        p, s = V("openai", True), V("azure", False)
        r = ng.tally_noguard(p, s, V("whisper", False, available=False, tech=True))
        self.assertEqual((r.state, r.verified, r.technical_stop), (kp3v.NG_WHISPER_UNAVAILABLE, False, True))
        r = ng.tally_noguard(p, s, None)
        self.assertEqual(r.state, kp3v.NG_WHISPER_UNAVAILABLE)

    def test_whisper_exception_in_decide(self):
        d = ng.decide_noguard(V("openai", True), lambda: V("azure", False), lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        self.assertEqual((d.state, d.verified), (kp3v.NG_WHISPER_UNAVAILABLE, False))

    def test_whisper_empty_transcript_is_ng_vote(self):
        w = ng.make_voter_noguard("whisper", "pump one's fist", "  ")
        r = ng.tally_noguard(V("openai", True), V("azure", False), w)
        self.assertEqual(r.state, kp3v.NG_VOTE_WHISPER_NG)

    def test_secondary_unavailable_is_technical_stop_not_2of3(self):
        r = ng.tally_noguard(V("openai", True), V("azure", False, available=False, tech=True), V("whisper", True))
        self.assertEqual((r.state, r.technical_stop), (kp3v.NG_SECONDARY_UNAVAILABLE, True))

    def test_primary_failure(self):
        r = ng.tally_noguard(V("openai", False, available=False), V("azure", True), None)
        self.assertEqual(r.state, kp3v.NG_PRIMARY_ASR_FAILURE)

    def test_rescued_primary_is_not_a_pass_vote(self):
        v = ng.make_voter_noguard("openai", "take part", "Take part.", rescued=True)
        self.assertFalse(v.passed)

    def test_tiebreak_off_is_old_dual_rule(self):
        p, s = V("openai", True), V("azure", False)
        self.assertFalse(ng.whisper_needed_noguard(p, s, tiebreak=False))
        self.assertEqual(ng.tally_noguard(p, s, None, tiebreak=False).state, kp3v.NG_SPLIT_TIEBREAK_OFF)


class RealClassifierFixtures(unittest.TestCase):
    """保存evidence(coffee pump one's fist, docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01)の転写で、本物の分類器を通す。"""
    CANON = "pump one's fist"

    def test_azure_itn_one_s_to_1_s_is_observed_but_ineffective(self):
        s = ng.make_voter_noguard("azure", self.CANON, "Pump 1's fist.")
        self.assertTrue(s.observed_protected_diff)     # 値ガードは差を観測する(記録のみ)
        self.assertFalse(s.protected_diff)              # しかし票・短絡には使わない
        self.assertFalse(s.passed)                      # 本文一致分類ではNG(= 割れるだけ)

    def test_stored_evidence_pump_ones_fist_passes_via_whisper(self):
        """N1 attempt1 / N2 attempt4 相当: P=`Pump one's fist.`(PASS) S=`Pump 1's fist.`(NG) W=`Pump One's Fist`(保存音声のlocal Whisper転写) -> P+W。"""
        p = ng.make_voter_noguard("openai", self.CANON, "Pump one's fist.")
        s = ng.make_voter_noguard("azure", self.CANON, "Pump 1's fist.")
        self.assertTrue(p.passed)
        self.assertTrue(ng.whisper_needed_noguard(p, s))
        w = ng.make_voter_noguard("whisper", self.CANON, "Pump One's Fist", ambiguous_blocks=True)
        self.assertTrue(w.passed)
        r = ng.tally_noguard(p, s, w)
        self.assertEqual((r.state, r.row, r.verified), (kp3v.PASS_VOTE_2OF3, "P+W", True))
        a = ng.build_vote_audit_noguard(p, s, w, r, secondary_called=True, whisper_called=True)
        self.assertTrue(a["guard_lifted"] and a["observed_protected_diff"]["secondary"])
        self.assertEqual(a["state"], kp3v.PASS_VOTE_2OF3)

    def test_stored_evidence_primary_drops_s_is_both_ng(self):
        """N1 attempt2-4 / N2 attempt2: P=`Pump one fist.`(NG) S=`Pump 1's fist.`(NG) -> 両NG=NG(Whisper不呼出)。真理値表どおり。"""
        p = ng.make_voter_noguard("openai", self.CANON, "Pump one fist.")
        s = ng.make_voter_noguard("azure", self.CANON, "Pump 1's fist.")
        self.assertFalse(p.passed or s.passed)
        self.assertFalse(ng.whisper_needed_noguard(p, s))
        self.assertEqual(ng.tally_noguard(p, s, None).state, kp3v.NG_BOTH)

    def test_false_pass_guard_real_numeric_error_still_needs_two_votes(self):
        """保護解除後も、本物の数値誤読(2 days -> 3 days)は1票(P)しか立たなければPASSしない(Whisperも別転写なら)。"""
        p = ng.make_voter_noguard("openai", "two days", "Two days.")
        s = ng.make_voter_noguard("azure", "two days", "3 days.")
        w = ng.make_voter_noguard("whisper", "two days", "Three days.", ambiguous_blocks=True)
        self.assertTrue(p.passed)
        self.assertFalse(s.passed)
        self.assertFalse(w.passed)
        self.assertEqual(ng.tally_noguard(p, s, w).state, kp3v.NG_VOTE_WHISPER_NG)


class Isolation(unittest.TestCase):
    def test_no_production_module_imports_er108(self):
        offenders = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            base = os.path.basename(f)
            if base.startswith("er108_"):
                continue
            try:
                with open(f, encoding="utf-8") as fh:
                    tree = ast.parse(fh.read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                if any(n.startswith("er108_kp_vote_noguard_01") for n in names):
                    offenders.append(base)
        self.assertEqual(offenders, [], f"未配線moduleをimportするfile: {offenders}")


if __name__ == "__main__":
    unittest.main()
