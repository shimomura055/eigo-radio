# -*- coding: utf-8 -*-
"""er121_e1_hr_adopt_r0_01(E-1 Human Review承認後のR0 attempt採用)のoffline test(API 0)。tempdirの擬似run dirのみ使う。"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
import wave

import er121_e1_hr_adopt_r0_01 as ad


def _wav(path, n=2400, val=0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes((val.to_bytes(2, "little", signed=True)) * n)


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _w(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)


class AdoptTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = self.tmp.name.replace("\\", "/") + "/run"
        L = f"{self.run}/b1b"
        self.att_wav = f"{L}/narration/attempts/y_voice_1_attempt6_englishstyleprefixwidemargin.wav"
        _wav(self.att_wav, val=100)
        _w(self.att_wav[:-4] + ".json", {"sha256": _sha(self.att_wav), "asr_text": "r0 asr"})
        _wav(f"{L}/narration/y_voice_1.wav", val=-100)          # 書換え版
        self.canon = "I want fewer redeliveries."
        _w(f"{L}/audit/tts_generation_results.json", {"segments": {"y_voice_1": {
            "status": "OK", "text": "I want fewer repeat deliveries.", "canonical_text": self.canon, "attempts_log": [{"attempt": 1}],
            "local_rewrite_recovery": {"status": "RESOLVED_BY_LOCAL_REWRITE"}, "sha256": "old"}}})
        _w(f"{L}/audit/review_lock_state.json", {"y_voice_1": {"state": "RESOLVED", "final_status": "OK"}})
        self.stmt = self.tmp.name + "/stmt.md"
        open(self.stmt, "w", encoding="utf-8").write("対象: b1b y_voice_1\nユーザー発言(テスト用の擬似)")

    def tearDown(self):
        self.tmp.cleanup()

    def _main(self, *extra):
        return ad.main(["--run-dir", self.run, "--level", "b1b", "--segment", "y_voice_1", *extra])

    def test_dry_run_writes_nothing(self):
        before = _sha(f"{self.run}/b1b/narration/y_voice_1.wav")
        self.assertEqual(self._main(), 0)
        self.assertEqual(_sha(f"{self.run}/b1b/narration/y_voice_1.wav"), before)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/audit/human_approved_segments.json"))

    def test_apply_without_statement_refused_and_writes_nothing(self):
        self.assertEqual(self._main("--apply"), 2)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/audit/human_approved_segments.json"))
        self.assertEqual(self._main("--apply", "--user-statement-ref", self.tmp.name + "/missing.md"), 2)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/audit/human_approved_segments.json"))

    def test_statement_must_name_the_segment(self):
        open(self.stmt, "w", encoding="utf-8").write("a2 preview だけ承認")
        self.assertEqual(self._main("--apply", "--user-statement-ref", self.stmt), 2)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/audit/human_approved_segments.json"))

    def test_not_a_target_segment_refused(self):
        with self.assertRaises(SystemExit):
            ad.plan(self.run, "b1b", "y_voice_2")

    def test_attempt_sha_mismatch_refused(self):
        _w(self.att_wav[:-4] + ".json", {"sha256": "0" * 64, "asr_text": "x"})
        self.assertEqual(self._main("--apply", "--user-statement-ref", self.stmt), 2)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/audit/human_approved_segments.json"))

    def test_apply_records_existing_mechanism_and_keeps_ng_records(self):
        rewritten_sha = _sha(f"{self.run}/b1b/narration/y_voice_1.wav")
        self.assertEqual(self._main("--apply", "--user-statement-ref", self.stmt), 0)
        L = f"{self.run}/b1b"
        self.assertEqual(_sha(f"{L}/narration/y_voice_1.wav"), _sha(self.att_wav))          # R0 attempt採用
        self.assertEqual(_sha(f"{L}/narration/y_voice_1.pre_ypl7_adopt.wav"), rewritten_sha)  # 書換え版は証跡として保全
        ap = json.load(open(f"{L}/audit/human_approved_segments.json", encoding="utf-8"))["y_voice_1"]
        self.assertEqual(ap["approved_by"], "user")
        self.assertEqual(ap["canonical_text_sha256"], hashlib.sha256(self.canon.encode("utf-8")).hexdigest())
        lock = json.load(open(f"{L}/audit/review_lock_state.json", encoding="utf-8"))["y_voice_1"]
        self.assertEqual((lock["state"], lock["final_status"]), ("RESOLVED", "HUMAN_APPROVED"))
        ent = json.load(open(f"{L}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["y_voice_1"]
        self.assertEqual(ent["text"], self.canon)
        self.assertEqual(ent["text_before_adoption"], "I want fewer repeat deliveries.")
        self.assertEqual(ent["sha256"], _sha(self.att_wav))
        self.assertEqual(ent["attempts_log"], [{"attempt": 1}])                         # NG記録は消さない
        self.assertTrue(ent["local_rewrite_recovery"] and ent["local_rewrite_audio_superseded_by_human_approval"])
        self.assertTrue(os.path.exists(f"{L}/audit/tts_generation_results.pre_ypl7_adopt_backup.json"))
        self.assertTrue(os.path.exists(f"{L}/audit/ypl7_user_approval_record_y_voice_1.json"))


class A2SlowdownRecheckGateTest(unittest.TestCase):
    """a2 y_voice_1: 減速後ASR再検証の実測PASSがあるときだけ採用可(NOT_RUN代替なし)。ffmpegで実際に減速する(API 0)。"""

    def setUp(self):
        import er008_a2_postprocess_slowdown_01 as slow
        self.tmp = tempfile.TemporaryDirectory()
        self.run = self.tmp.name.replace("\\", "/") + "/run"
        L = f"{self.run}/a2"
        self.att_wav = f"{L}/narration/attempts/y_voice_1_attempt5_custom53fd514d.wav"
        _wav(self.att_wav, n=48000, val=1000)
        _w(self.att_wav[:-4] + ".json", {"sha256": _sha(self.att_wav), "asr_text": "r0 asr"})
        _wav(f"{L}/narration/y_voice_1.wav", val=-100)
        self.canon = "I want fewer redeliveries."
        _w(f"{L}/audit/tts_generation_results.json", {"segments": {"y_voice_1": {
            "status": "OK", "text": self.canon, "canonical_text": self.canon, "sha256": "old"}}})
        _w(f"{L}/audit/review_lock_state.json", {"y_voice_1": {"state": "HUMAN_REVIEW_REQUIRED", "final_status": "NG"}})
        self.stmt = self.tmp.name + "/stmt.md"
        open(self.stmt, "w", encoding="utf-8").write("対象: a2 y_voice_1 テスト用の擬似")
        exp = self.tmp.name + "/exp.wav"
        slow.apply_a2_slowdown(self.att_wav, exp)
        self.slowed_sha = _sha(exp)

    def tearDown(self):
        self.tmp.cleanup()

    def _recheck(self, **kw):
        d = {"recheck_pass": True, "asr_verified": True, "status": "OK", "post_slowdown_final_classification": "NORMALIZED_MATCH",
             "source_attempt_sha256": _sha(self.att_wav), "slowed_wav_sha256": self.slowed_sha, "asr_model_id": "m"}
        d.update(kw)
        _w(f"{self.run}/a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json", d)

    def _main(self):
        return ad.main(["--run-dir", self.run, "--level", "a2", "--segment", "y_voice_1", "--apply", "--user-statement-ref", self.stmt])

    def _untouched(self):
        self.assertFalse(os.path.exists(f"{self.run}/a2/audit/human_approved_segments.json"))

    def test_pass_allows_adoption_and_records_reference(self):
        self._recheck()
        self.assertEqual(self._main(), 0)
        ent = json.load(open(f"{self.run}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["y_voice_1"]
        ref = ent["post_slowdown_asr_recheck"]
        self.assertIsInstance(ref, dict)
        self.assertEqual(ref["judgement"], "NORMALIZED_MATCH")
        self.assertTrue(ref["path"].endswith("y_voice_1_slowed_asr_recheck.json"))
        self.assertNotIn("NOT_RUN", json.dumps(ent, ensure_ascii=False))
        self.assertEqual(_sha(f"{self.run}/a2/narration/y_voice_1.wav"), self.slowed_sha)

    def test_missing_recheck_refused(self):
        self.assertEqual(self._main(), 2)
        self._untouched()

    def test_non_pass_recheck_refused(self):
        self._recheck(recheck_pass=False, asr_verified=False, status="STOPPED", post_slowdown_final_classification="MISMATCH")
        self.assertEqual(self._main(), 2)
        self._untouched()

    def test_recheck_for_other_audio_refused(self):
        self._recheck(slowed_wav_sha256="0" * 64)
        self.assertEqual(self._main(), 2)
        self._untouched()
        self._recheck(source_attempt_sha256="1" * 64)
        self.assertEqual(self._main(), 2)
        self._untouched()


if __name__ == "__main__":
    unittest.main()
