# er104_kp_three_asr_vote_01 の追加unit test(委任_02: Opus P-02/P-03/P-08/P-09/P-10/P-12)。API 0 / 費用0 / ネットワークなし。
# 実行: .venv\Scripts\python.exe -m unittest er104_kp_three_asr_vote_01_test_02 -v
import os
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

    def __call__(self, *a, **k):
        self.n += 1
        if self.exc:
            raise self.exc
        return self.voter


class RowsAndWarnings(unittest.TestCase):
    """P-03/P-10: どの行で合格したか。行4(P NG/S PASS/W PASS)はSECONDARY_CONFIRMED警告(事後試聴)、行2はPASS。"""

    def test_row2_p_plus_w_no_warning(self):
        d = m.decide(V("openai", True), Counter(V("azure", False)), Counter(V("whisper", True)))
        self.assertEqual((d.row, d.secondary_confirmed_warning, d.audit["row"]), (m.ROW_P_W, False, "P+W"))

    def test_row4_s_plus_w_confirmed_warning(self):
        d = m.decide(V("openai", False), Counter(V("azure", True)), Counter(V("whisper", True)))
        self.assertEqual((d.row, d.secondary_confirmed_warning, d.audit["row"]), (m.ROW_S_W, True, "S+W"))

    def test_row1_dual_row_and_ng_have_no_row(self):
        d = m.decide(V("openai", True), Counter(V("azure", True)), None)
        self.assertEqual((d.row, d.secondary_confirmed_warning), (m.ROW_DUAL, False))
        d2 = m.decide(V("openai", False), Counter(V("azure", True)), Counter(V("whisper", False)))
        self.assertEqual((d2.row, d2.verified), (None, False))


class TallyPurityAndEquivalence(unittest.TestCase):
    """P-09: tally()は純関数。decide()は同じtally()/whisper_needed()だけを使う。全組合せでdecideとtally直呼びが一致。"""

    def test_all_combinations_decide_equals_tally(self):
        import itertools
        voters_p = [V("openai", True), V("openai", False), V("openai", False, observed_protected_diff=True),
                    Voter("openai", None, False, available=False)]
        voters_s = [V("azure", True), V("azure", False), V("azure", False, observed_protected_diff=True), V("azure", True, observed_protected_diff=True),
                    Voter("azure", None, False, available=False), Voter("azure", "", False)]
        voters_w = [None, V("whisper", True), V("whisper", False), Voter("whisper", None, False, available=False, technical_failure=True),
                    Voter("whisper", "", False, available=False)]
        n_checked = 0
        for p, s, w, tb in itertools.product(voters_p, voters_s, voters_w, (True, False)):
            need = m.whisper_needed(p, s, tiebreak=tb)
            tr = m.tally(p, s, w if need else None, tiebreak=tb)
            wc = Counter(w) if w is not None else None
            d = m.decide(p, lambda s=s: s, wc, tiebreak=tb)
            if need and w is None:
                # whisper_fn未設定の割れ: decideはWhisper無し=技術STOP(tally(None)と同じ)
                self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE)
            else:
                self.assertEqual((d.state, d.reason, d.pass_count, d.row), (tr.state, tr.reason, tr.pass_count, tr.row), (p, s, w, tb))
            if not need:
                self.assertTrue(wc is None or wc.n == 0, "whisper must not be called when not needed")
            n_checked += 1
        self.assertGreater(n_checked, 200)

    def test_tally_has_no_side_effects(self):
        import inspect
        src = inspect.getsource(m.tally) + inspect.getsource(m.whisper_needed)
        for forbidden in ("open(", "requests", "subprocess", "time.", "whisper_transcribe", "print("):
            self.assertNotIn(forbidden, src)

    def test_hard_states_never_overridden_by_whisper(self):
        """除外確定状態(Primary失敗/Secondary障害)はWhisper PASSでも覆らない。"""
        w = V("whisper", True)
        for p, s in ((Voter("openai", None, False, available=False), V("azure", True)),
                     (V("openai", True), Voter("azure", None, False, available=False))):
            tr = m.tally(p, s, w)
            self.assertIn(tr.state, m.HARD_STATES)
            self.assertFalse(tr.verified)


class WhisperVoteRules(unittest.TestCase):
    def setUp(self):
        m.reset_whisper_state()
        self.addCleanup(m.reset_whisper_state)

    def test_length_applies_to_whisper_vote(self):
        """P-02: Whisper票にも呼出元と同じmax_len判定。長さ超過の転写はPASS票にしない。"""
        v = m.whisper_vote("take part", "w.wav", stored_text="Take part.", max_len=len("take part") + 10)
        self.assertTrue(v.passed)
        v2 = m.whisper_vote("take part", "w2.wav", stored_text="Take part. " + "and more words " * 3, max_len=len("take part") + 10)
        self.assertFalse(v2.passed)

    def test_ambiguous_value_is_not_a_pass_vote(self):
        """P-02: 値ガードAMBIGUOUS(根拠のない曖昧表層)はWhisperのPASS票にしない(ambiguous_blocks)。"""
        import er078_asr_unified_judge_01 as uj
        found = False
        for canon, text in (("ten minutes", "10 minutes."), ("10 minutes", "ten minutes."), ("ten", "10"), ("10", "ten"),
                            ("one", "1"), ("two apples", "2 apples"), ("three", "3")):
            vgr, neg = uj._protected(canon, text, "en")
            if vgr.kind == uj.vg.AMBIGUOUS:
                found = True
                self.assertFalse(m.make_voter("whisper", canon, text, ambiguous_blocks=True).passed, (canon, text))
        if not found:
            # AMBIGUOUSの発生条件が現行ガードに無い場合は契約(ambiguous_blocks時にAMBIGUOUSならFalse)をモックで確認
            orig = uj._protected
            class K:  # noqa
                kind = uj.vg.AMBIGUOUS
            uj._protected = lambda *a, **k: (K, False)
            try:
                self.assertFalse(m.make_voter("whisper", "take part", "Take part.", ambiguous_blocks=True).passed)
                self.assertTrue(m.make_voter("whisper", "take part", "Take part.", ambiguous_blocks=False).passed)
            finally:
                uj._protected = orig

    def test_exception_is_technical_and_counts_toward_circuit(self):
        def boom(_p):
            raise ImportError("no faster_whisper")
        for i in range(m.WHISPER_CIRCUIT_THRESHOLD - 1):
            v = m.whisper_vote("think up", f"w{i}.wav", transcribe_fn=boom)
            self.assertTrue(v.technical_failure and not v.passed)
            self.assertFalse(m.whisper_circuit_open())
        v = m.whisper_vote("think up", "wlast.wav", transcribe_fn=boom)
        self.assertTrue(v.technical_failure)
        self.assertTrue(m.whisper_circuit_open())
        called = []
        v = m.whisper_vote("think up", "wx.wav", transcribe_fn=lambda p: called.append(p) or "Think up.")
        self.assertEqual((v.technical_failure, called, v.error), (True, [], "whisper_circuit_open"))

    def test_timeout_opens_circuit_immediately_threshold_1(self):
        def slow(_p):
            raise m.WhisperTimeout("t")
        v = m.whisper_vote("think up", "w.wav", transcribe_fn=slow)
        self.assertTrue(v.technical_failure)
        self.assertTrue(m.whisper_circuit_open())
        self.assertEqual(m.WHISPER_STATE.events[-1]["type"], "WHISPER_CIRCUIT_OPEN")

    def test_real_timeout_conversion(self):
        import er008_disfluency_qa_18 as dq
        old = dq.transcribe_verbatim
        dq.transcribe_verbatim = lambda *a, **k: (time.sleep(0.4), [])[1]
        try:
            with self.assertRaises(m.WhisperTimeout):
                m.whisper_transcribe("dummy.wav", timeout=0.05)
        finally:
            dq.transcribe_verbatim = old

    def test_empty_transcript_is_ng_vote_not_failure(self):
        v = m.whisper_vote("think up", "w.wav", transcribe_fn=lambda p: "")
        self.assertFalse(v.technical_failure)
        self.assertFalse(v.passed)
        self.assertFalse(m.whisper_circuit_open())

    def test_memo_same_wav_one_transcription(self):
        n = []
        fn = lambda p: n.append(p) or "Think up."
        a = m.whisper_vote("think up", "w.wav", sha="abc", transcribe_fn=fn)
        b = m.whisper_vote("think up", "w.wav", sha="abc", transcribe_fn=fn)
        self.assertEqual((len(n), a.passed, b.passed, b.memo_hit), (1, True, True, True))

    def test_stored_text_no_transcription(self):
        fn = Counter(None, exc=AssertionError("must not run"))
        v = m.whisper_vote("think up", "w.wav", transcribe_fn=fn, stored_text="Think up.")
        self.assertEqual((v.passed, fn.n, v.memo_hit), (True, 0, True))

    def test_preflight_failure_opens_circuit(self):
        import er008_disfluency_qa_18 as dq
        old = dq._get_model

        def bad(*a, **k):
            raise ImportError("no module")
        dq._get_model = bad
        try:
            rec = m.whisper_preflight()
        finally:
            dq._get_model = old
        self.assertFalse(rec["ok"])
        self.assertTrue(m.whisper_circuit_open())

    def test_model_is_production_small_int8_shared_loader(self):
        import inspect
        import er008_disfluency_qa_18 as dq
        self.assertEqual((m.WHISPER_MODEL_SIZE, m.WHISPER_COMPUTE_TYPE), ("small", "int8"))
        self.assertIn('device="cpu", compute_type="int8"', inspect.getsource(dq._get_model))


class VoteCheckRecord(unittest.TestCase):
    def test_record_has_row_and_whisper_model(self):
        f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        f.write(b"RIFFfakewav")
        f.close()
        self.addCleanup(os.unlink, f.name)
        d = m.decide(V("openai", False, text="Blur."), Counter(V("azure", True, text="Blurt.")), Counter(V("whisper", True, text="Blurt")))
        rec = m.vote_check_from_audit(d.audit, f.name, "blurt", source="generation")
        self.assertEqual((rec["version"], rec["ok"], rec["row"], rec["vote_state"]), ("kp_vote_check_v1", True, "S+W", m.PASS_VOTE_2OF3))
        self.assertEqual((rec["whisper"]["model"], rec["whisper"]["compute_type"], rec["whisper"]["called"]), ("small", "int8", True))
        self.assertEqual(rec["wav_sha256"], m.sha256_file(f.name))
        self.assertEqual(rec["primary"]["text"], "Blur.")


if __name__ == "__main__":
    unittest.main()
