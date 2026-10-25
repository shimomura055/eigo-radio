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


if __name__ == "__main__":
    unittest.main()
