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
        self.assertEqual(d.audit["whisper_model"], "small")
        d1, _, _ = self.run_row(True, True, None)
        self.assertIsNone(d1.audit["whisper"])
        self.assertIsNone(d1.audit["whisper_model"])


class FailClosed(unittest.TestCase):
    def test_whisper_exception_is_not_pass(self):
        d = m.decide(V("openai", True), Counter(V("azure", False)), Counter(exc=RuntimeError("model load failed")))
        self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE)
        self.assertFalse(d.verified)
        self.assertTrue(d.whisper_called)

    def test_whisper_none_or_empty_or_unavailable(self):
        for bad in (None, Voter("whisper", "", False), Voter("whisper", None, False, available=False, error="timeout"),
                    Voter("whisper", "  ", True)):
            d = m.decide(V("openai", False), Counter(V("azure", True)), Counter(bad))
            self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE, bad)
            self.assertFalse(d.verified)

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

    def test_primary_protected_diff_short_circuit_no_calls(self):
        sec, wh = Counter(V("azure", True)), Counter(V("whisper", True))
        d = m.decide(V("openai", False, protected_diff=True), sec, wh)
        self.assertEqual((d.state, sec.n, wh.n, d.verified), (m.NG_PROTECTED, 0, 0, False))

    def test_dissent_protected_diff_blocks_2of3(self):
        wh = Counter(V("whisper", True))
        d = m.decide(V("openai", True), Counter(V("azure", False, protected_diff=True)), wh)
        self.assertEqual((d.state, wh.n, d.verified), (m.NG_PROTECTED_DISSENT, 0, False))
        # 反対票側がPrimary(NG+保護差)でもP1短絡(NG_PROTECTED)
        d2 = m.decide(V("openai", False, protected_diff=True), Counter(V("azure", True)), wh)
        self.assertEqual(d2.state, m.NG_PROTECTED)
        # opt-out時は表どおり(Whisper呼出)
        d3 = m.decide(V("openai", True), Counter(V("azure", False, protected_diff=True)), Counter(V("whisper", True)),
                      protected_dissent_blocks=False)
        self.assertEqual(d3.state, m.PASS_VOTE_2OF3)

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
                d = m.decide(V("openai", p), Counter(V("azure", s)), wh, tiebreak_enabled=False)
                self.assertEqual(d.verified, p and s)
                self.assertEqual(wh.n, 0)
        d = m.decide(V("openai", True), Counter(V("azure", False)), Counter(V("whisper", True)), tiebreak_enabled=False)
        self.assertEqual(d.state, m.NG_SPLIT_TIEBREAK_OFF)
        self.assertFalse(d.technical_stop)

    def test_default_constants(self):
        self.assertTrue(m.KP_WHISPER_TIEBREAK_ENABLED)
        self.assertTrue(m.vote_enabled())


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


class StoredRejudge(unittest.TestCase):
    def _wav(self):
        f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        f.write(b"RIFFfakewav")
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_old_dual_check_think_up_becomes_pass_with_local_whisper_only(self):
        wav = self._wav()
        chk = {"version": "kp_dual_check_v1", "ok": False, "canonical_text": "think up", "wav_sha256": m._sha256_file(wav),
               "primary": {"text": "ThinkUp.", "pass": True, "rescued_by_secondary": False}, "secondary": {"text": "Think.", "pass": False}}
        wh = Counter(m.make_voter("whisper", "think up", "Think up."))
        d = m.rejudge_stored(chk, wav, "think up", whisper_fn=wh)
        self.assertEqual((d.state, wh.n), (m.PASS_VOTE_2OF3, 1))
        rec = m.vote_check_from_decision(d, wav, "think up", source="stored_rejudged")
        self.assertEqual((rec["version"], rec["ok"], rec["whisper"]["called"]), ("kp_vote_check_v1", True, True))
        # 保存済みWhisper転写(同sha)があれば再転写しない
        wh2 = Counter(m.make_voter("whisper", "think up", "SHOULD NOT RUN"))
        d2 = m.rejudge_stored(rec, wav, "think up", whisper_fn=wh2)
        self.assertEqual((d2.state, wh2.n), (m.PASS_VOTE_2OF3, 0))

    def test_sha_or_canonical_mismatch_or_missing_text_returns_none(self):
        wav = self._wav()
        base = {"version": "kp_dual_check_v1", "canonical_text": "think up", "wav_sha256": m._sha256_file(wav),
                "primary": {"text": "ThinkUp."}, "secondary": {"text": "Think."}}
        self.assertIsNone(m.rejudge_stored({**base, "wav_sha256": "0" * 64}, wav, "think up", whisper_fn=None))
        self.assertIsNone(m.rejudge_stored(base, wav, "blurt", whisper_fn=None))
        self.assertIsNone(m.rejudge_stored({**base, "secondary": {"text": ""}}, wav, "think up", whisper_fn=None))
        self.assertIsNone(m.rejudge_stored({**base, "primary": {}}, wav, "think up", whisper_fn=None))

    def test_rescued_primary_in_stored_check_counts_ng(self):
        wav = self._wav()
        chk = {"version": "kp_dual_check_v1", "canonical_text": "take part", "wav_sha256": m._sha256_file(wav),
               "primary": {"text": "Take part.", "rescued_by_secondary": True}, "secondary": {"text": "Take part."}}
        wh = Counter(m.make_voter("whisper", "take part", "Take part."))
        d = m.rejudge_stored(chk, wav, "take part", whisper_fn=wh)
        self.assertEqual((d.state, wh.n), (m.PASS_VOTE_2OF3, 1))   # P(NG:救済)/S PASS/W PASS = 2/3
        self.assertEqual(d.reason, "vote_2of3:secondary+whisper")


class WhisperRunner(unittest.TestCase):
    def test_timeout_converts_to_unavailable(self):
        def slow(_p):
            time.sleep(0.5)
            return "x"
        orig = m.whisper_transcribe

        def wt(path, *, timeout=0.05):
            import concurrent.futures
            ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            try:
                return ex.submit(slow, path).result(timeout=timeout)
            finally:
                ex.shutdown(wait=False, cancel_futures=True)
        fn = m.make_whisper_fn("think up", "dummy.wav", transcribe_fn=wt)
        d = m.decide(V("openai", True), Counter(V("azure", False)), fn)
        self.assertEqual(d.state, m.NG_WHISPER_UNAVAILABLE)
        self.assertIs(m.whisper_transcribe, orig)

    def test_model_is_production_small_int8_shared_loader(self):
        import inspect
        import er008_disfluency_qa_18 as dq
        self.assertEqual(m.WHISPER_MODEL_SIZE, "small")
        src = inspect.getsource(dq._get_model)
        self.assertIn('device="cpu", compute_type="int8"', src)


class Isolation(unittest.TestCase):
    """未配線の固定: Production .pyはer104_*をimportしない(配線は次委任で本testを更新する)。"""

    def test_no_production_module_imports_er104(self):
        pat = re.compile(r"^\s*(import|from)\s+er104_", re.M)
        hits = []
        for p in glob.glob("*.py") + glob.glob("tools/*.py"):
            if os.path.basename(p).startswith("er104_"):
                continue
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    if pat.search(fh.read()):
                        hits.append(p)
            except OSError:
                pass
        self.assertEqual(hits, [])

    def test_er096_dual_still_present_and_unchanged_default(self):
        import er096_kp_dual_pass_01 as d2
        self.assertTrue(d2.KP_EN_PHRASE_DUAL_REQUIRED)   # 現行(両方PASS)は本委任で無変更


if __name__ == "__main__":
    unittest.main()
