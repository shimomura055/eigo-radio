# er104_kp_three_asr_vote_01 の単体test(API 0 / 費用0 / ネットワークなし)。
# 実行: .venv\Scripts\python.exe -m unittest er104_kp_three_asr_vote_01_test_01 -v
import glob
import os
import re
import tempfile
import time
import unittest

import er104_kp_three_asr_vote_01 as m
from er104_kp_three_asr_vote_01 import Voter


def V(provider, passed, text="x", **kw):
    return Voter(provider=provider, text=text, passed=passed, **kw)


class Counter:
    def __init__(self, voter=None, exc=None):
        self.n, self.voter, self.exc = 0, voter, exc

    def __call__(self):
        self.n += 1
        if self.exc:
            raise self.exc
        return self.voter


class TruthTable(unittest.TestCase):
    """ユーザー§2の6行を真理値表として固定(Whisper呼出回数込み)。"""

    def run_row(self, p, s, w):
        sec = Counter(V("azure", s))
        wh = Counter(V("whisper", w if w is not None else False))
        d = m.decide(V("openai", p), sec, wh)
        return d, sec.n, wh.n

    def test_row1_pass_pass_no_whisper(self):
        d, sn, wn = self.run_row(True, True, None)
        self.assertEqual((d.state, d.verified, sn, wn), (m.PASS_DUAL, True, 1, 0))

    def test_row2_pass_ng_whisper_pass(self):
        d, sn, wn = self.run_row(True, False, True)
        self.assertEqual((d.state, d.verified, sn, wn), (m.PASS_VOTE_2OF3, True, 1, 1))
        self.assertEqual(d.reason, "vote_2of3:primary+whisper")

    def test_row3_pass_ng_whisper_ng(self):
        d, sn, wn = self.run_row(True, False, False)
        self.assertEqual((d.state, d.verified, wn), (m.NG_VOTE_WHISPER_NG, False, 1))

    def test_row4_ng_pass_whisper_pass(self):
        d, sn, wn = self.run_row(False, True, True)
        self.assertEqual((d.state, d.verified, wn), (m.PASS_VOTE_2OF3, True, 1))
        self.assertEqual(d.reason, "vote_2of3:secondary+whisper")

    def test_row5_ng_pass_whisper_ng(self):
        d, sn, wn = self.run_row(False, True, False)
        self.assertEqual((d.state, d.verified, wn), (m.NG_VOTE_WHISPER_NG, False, 1))

    def test_row6_ng_ng_no_whisper(self):
        d, sn, wn = self.run_row(False, False, None)
        self.assertEqual((d.state, d.verified, sn, wn), (m.NG_BOTH, False, 1, 0))
        self.assertFalse(d.whisper_called)

    def test_pass_count_audit(self):
        d, _, _ = self.run_row(True, False, True)
        self.assertEqual(d.pass_count, 2)
        self.assertTrue(d.audit["whisper_called"])
        self.assertEqual(d.audit["whisper_model"]["model"], "small")
        d1, _, _ = self.run_row(True, True, None)
        self.assertIsNone(d1.audit["whisper"])
        self.assertIsNone(d1.audit["whisper_model"])


class FailClosed(unittest.TestCase):
    def test_whisper_exception_is_not_pass(self):
        d = m.decide(V("openai", True), Counter(V("azure", False)), Counter(exc=RuntimeError("model load failed")))
        self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE)
        self.assertFalse(d.verified)
        self.assertTrue(d.whisper_called)

    def test_whisper_none_or_technical_failure_is_technical_stop(self):
        for bad in (None, Voter("whisper", None, False, available=False, error="timeout", technical_failure=True)):
            d = m.decide(V("openai", False), Counter(V("azure", True)), Counter(bad))
            self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE, bad)
            self.assertFalse(d.verified)
            self.assertTrue(d.technical_stop)

    def test_whisper_empty_transcript_is_ng_vote_not_technical_stop(self):
        """P-08: 空転写 = NG票(通常の再生成)。技術STOPにしない。PASSにもしない。"""
        for bad in (m.make_voter("whisper", "think up", ""), m.make_voter("whisper", "think up", "  "), m.make_voter("whisper", "think up", None)):
            d = m.decide(V("openai", False), Counter(V("azure", True)), Counter(bad))
            self.assertEqual((d.state, d.verified, d.technical_stop), (m.NG_VOTE_WHISPER_NG, False, False), bad)
            self.assertEqual(d.reason, "whisper_empty_transcript_ng_vote")

    def test_whisper_not_configured_is_not_pass(self):
        d = m.decide(V("openai", True), Counter(V("azure", False)), None)
        self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE)
        self.assertFalse(d.verified)

    def test_secondary_unavailable_no_whisper_no_downgrade(self):
        """Azure障害でPrimary+Whisperの2/3へ降格しない(現行承認の「Primary単独PASSへ降格しない」と同方針)。Whisperは呼ばない。"""
        for sec in (Counter(exc=TimeoutError("azure")), Counter(Voter("azure", None, False, available=False, error="x")),
                    Counter(Voter("azure", "", False)), Counter(None)):
            wh = Counter(V("whisper", True))
            d = m.decide(V("openai", True), sec, wh)
            self.assertEqual(d.state, m.NG_SECONDARY_UNAVAILABLE)
            self.assertTrue(d.technical_stop)
            self.assertFalse(d.verified)
            self.assertEqual(wh.n, 0)

    def test_primary_asr_failure_no_calls(self):
        sec, wh = Counter(V("azure", True)), Counter(V("whisper", True))
        d = m.decide(Voter("openai", None, False, available=False), sec, wh)
        self.assertEqual((d.state, sec.n, wh.n), (m.NG_PRIMARY_ASR_FAILURE, 0, 0))

    def test_primary_observed_protected_diff_no_short_circuit(self):
        """2026-10-22保護解除: Primary NG+観測保護差でもSecondary/Whisperを呼ぶ(短絡しない)。"""
        sec, wh = Counter(V("azure", True)), Counter(V("whisper", True))
        d = m.decide(V("openai", False, observed_protected_diff=True), sec, wh)
        self.assertEqual((d.state, sec.n, wh.n, d.verified, d.row), (m.PASS_VOTE_2OF3, 1, 1, True, m.ROW_S_W))

    def test_dissent_observed_protected_diff_still_calls_whisper(self):
        """反対票側の観測保護差でWhisperを止めない(旧dissentブロックの撤去)。"""
        wh = Counter(V("whisper", True))
        d = m.decide(V("openai", True), Counter(V("azure", False, observed_protected_diff=True)), wh)
        self.assertEqual((d.state, wh.n, d.verified, d.row), (m.PASS_VOTE_2OF3, 1, True, m.ROW_P_W))
        self.assertTrue(d.audit["observed_protected_diff"]["secondary"] and d.audit["guard_lifted"])

    def test_rescued_primary_is_not_a_pass(self):
        """Azure転写依存で救済されたPrimary(rescued)はOpenAI自身のPASSではない: make_voterでpassed=False。"""
        v = m.make_voter("openai", "take part", "Take part.", rescued=True)
        self.assertFalse(v.passed)
        self.assertTrue(v.rescued)


class TiebreakOff(unittest.TestCase):
    def test_tiebreak_off_equals_old_dual_rule(self):
        """段階rollback: tie-break無効なら全8通りが旧「両方PASS必須」と一致し、Whisperは呼ばれない。"""
        for p in (True, False):
            for s in (True, False):
                wh = Counter(V("whisper", True))
                d = m.decide(V("openai", p), Counter(V("azure", s)), wh, tiebreak=False)
                self.assertEqual(d.verified, p and s)
                self.assertEqual(wh.n, 0)
        d = m.decide(V("openai", True), Counter(V("azure", False)), Counter(V("whisper", True)), tiebreak=False)
        self.assertEqual(d.state, m.NG_SPLIT_TIEBREAK_OFF)
        self.assertFalse(d.technical_stop)

    def test_default_constants(self):
        self.assertTrue(m.KP_WHISPER_TIEBREAK_ENABLED)
        self.assertTrue(m.vote_enabled())
        self.assertTrue(m.tiebreak_enabled())

    def test_no_primary_only_switch_exists(self):
        """P-04: Primary単独へ落とすスイッチは置かない(戻しスイッチは両方PASS必須への1本だけ)。"""
        names = [n for n in dir(m) if n.isupper()]
        self.assertEqual(sorted(n for n in names if n.startswith("KP_")), ["KP_THREE_ASR_VOTE_ENABLED", "KP_WHISPER_TIEBREAK_ENABLED"])
        self.assertFalse([n for n in dir(m) if "PRIMARY_ONLY" in n.upper()])


class RealClassifier(unittest.TestCase):
    """保存済み実転写を現行分類器(Production同一関数)に通した判定。ユーザー§3の4ケース。"""

    def vote(self, canon, p, s, w):
        wh = Counter(m.make_voter("whisper", canon, w))
        d = m.decide(m.make_voter("openai", canon, p), lambda: m.make_voter("azure", canon, s), wh)
        return d, wh.n

    def test_think_up(self):
        d, wn = self.vote("think up", "ThinkUp.", "Think.", "Think up.")
        self.assertEqual((d.state, wn), (m.PASS_VOTE_2OF3, 1))

    def test_blurt(self):
        d, wn = self.vote("blurt", "Blur.", "Blurt.", "Blurt")
        self.assertEqual((d.state, wn), (m.PASS_VOTE_2OF3, 1))

    def test_take_part_problem_audio_all_ng(self):
        d, wn = self.vote("take part", "Take tart.", "Take Tart.", "Take Tarte.")
        self.assertEqual((d.state, wn, d.verified), (m.NG_BOTH, 0, False))   # P/S両NGなのでWhisperは呼ばない
        # Primaryが言語priorで「part」に補正した試行(er088 trial1: Primary PASS/Azure NG)でも、WhisperがNGなら不合格
        d2, wn2 = self.vote("take part", "Take part.", "Take Tart.", "Take Tarte.")
        self.assertEqual((d2.state, wn2, d2.verified), (m.NG_VOTE_WHISPER_NG, 1, False))

    def test_take_part_good_audio_all_pass(self):
        d, wn = self.vote("take part", "Take part.", "Take part.", "Take part.")
        self.assertEqual((d.state, wn), (m.PASS_DUAL, 0))


