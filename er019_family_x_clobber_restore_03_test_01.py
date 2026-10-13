# -*- coding: utf-8 -*-
"""委任_03: (1) runnerが新規生成OK entryへsha256を記録する (2) 上書きされた検証済みentryの明示復元CLIの条件。API呼出なし。"""
import json
import os
import struct
import tempfile
import time
import unittest
import wave

import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_clobber_restore_03 as restore
import er019_family_x_validation_inheritance_01 as vi


def _wav(path, seconds=1.0, rate=8000):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<h", 100) * int(rate * seconds))


class RecordedShaTests(unittest.TestCase):
    def test_new_ok_entry_gets_sha256(self):
        d = tempfile.mkdtemp()
        p = f"{d}/a.wav"
        _wav(p)

        def gen():
            return {"status": "OK", "path": p}
        r = runner._generate_or_reuse(None, "x", p, gen)
        self.assertEqual(r["sha256"], vi.sha256_file(p))

    def test_not_ok_or_existing_sha_unchanged(self):
        d = tempfile.mkdtemp()
        p = f"{d}/a.wav"
        _wav(p)
        self.assertNotIn("sha256", runner._generate_or_reuse(None, "x", p, lambda: {"status": "STOPPED", "path": p}))
        self.assertEqual(runner._generate_or_reuse(None, "x", p, lambda: {"status": "OK", "path": p, "sha256": "abc"})["sha256"], "abc")

    def test_only_segments_skip_path_is_unchanged(self):
        runner._ONLY_SEGMENTS = {"other"}
        try:
            r = runner._generate_or_reuse(None, "x", "nope.wav", lambda: {"status": "OK", "path": "nope.wav"})
            self.assertEqual(r["status"], "SKIPPED_NOT_SELECTED")
        finally:
            runner._ONLY_SEGMENTS = None


class RestoreTests(unittest.TestCase):
    def _setup(self, *, dur_recorded=1.0, status="OK", asr_verified=True, mtime_after=False, text_ok=True):
        d = tempfile.mkdtemp()
        os.makedirs(f"{d}/audit")
        os.makedirs(f"{d}/narration")
        wav = f"{d}/narration/full_story_part1.wav"
        _wav(wav, 1.0)
        os.utime(wav, (time.time() - 3600, time.time() - 3600))
        json.dump({"part1": "Hello world."}, open(f"{d}/parts.json", "w"))
        entry = {"status": status, "asr_verified": asr_verified, "text": "Hello world.", "canonical_text": "Hello world.",
                 "asr_text": "Hello world.", "path": wav, "trim_info": {"trimmed_duration_seconds": dur_recorded}}
        ts = time.strftime("%Y%m%dT%H%M%S")
        bak = f"{d}/audit/tts_generation_results.pre_x_{ts}.json"
        json.dump({"style_version": "v3", "segments": {"full_story_part1": entry}}, open(bak, "w"))
        json.dump({"style_version": "v3", "segments": {"full_story_part1": {"status": "SKIPPED_NOT_SELECTED"}}},
                  open(f"{d}/audit/tts_generation_results.json", "w"))
        if mtime_after:
            t = time.time() + 5
            os.utime(wav, (t, t))
        return d, bak

    def _run(self, d, bak, apply=False, text="Hello world."):
        return restore.plan_and_apply(d, "b1b", bak, ["full_story_part1"], apply, expected_texts={"full_story_part1": text})

    def test_restore_ok_apply_and_dry_run(self):
        d, bak = self._setup()
        rep = self._run(d, bak, apply=False)
        self.assertTrue(rep["labels"]["full_story_part1"]["ok"])
        cur = json.load(open(f"{d}/audit/tts_generation_results.json"))
        self.assertEqual(cur["segments"]["full_story_part1"]["status"], "SKIPPED_NOT_SELECTED")  # dry-runは書かない
        rep = self._run(d, bak, apply=True)
        cur = json.load(open(f"{d}/audit/tts_generation_results.json"))
        e = cur["segments"]["full_story_part1"]
        self.assertEqual(e["status"], "OK")
        self.assertEqual(e["validation_inheritance"]["label"], "REUSED_VALIDATED")
        self.assertEqual(e["sha256"], vi.sha256_file(f"{d}/narration/full_story_part1.wav"))
        self.assertTrue(os.path.exists(rep["backup_of_current"]))

    def test_rejections(self):
        for kw, reason in (({"dur_recorded": 9.0}, "DURATION_WITNESS_MISMATCH"), ({"status": "STOPPED"}, "BACKUP_ENTRY_NOT_VALIDATED_OK"),
                           ({"asr_verified": False}, "BACKUP_ENTRY_NOT_VALIDATED_OK"), ({"mtime_after": True}, "WAV_MODIFIED_AFTER_BACKUP")):
            d, bak = self._setup(**kw)
            rep = self._run(d, bak, apply=True)
            self.assertFalse(rep["labels"]["full_story_part1"]["ok"], kw)
            self.assertEqual(rep["labels"]["full_story_part1"]["reason"], reason, kw)
            cur = json.load(open(f"{d}/audit/tts_generation_results.json"))
            self.assertEqual(cur["segments"]["full_story_part1"]["status"], "SKIPPED_NOT_SELECTED", kw)  # 書かれない
        d, bak = self._setup()
        rep = self._run(d, bak, apply=True, text="Different text.")
        self.assertEqual(rep["labels"]["full_story_part1"]["reason"], "CANONICAL_TEXT_MISMATCH_OR_NO_EXPECTED")

    def test_not_restored_over_existing_ok_entry(self):
        d, bak = self._setup()
        cur = json.load(open(f"{d}/audit/tts_generation_results.json"))
        cur["segments"]["full_story_part1"] = {"status": "OK", "asr_verified": True}
        json.dump(cur, open(f"{d}/audit/tts_generation_results.json", "w"))
        rep = self._run(d, bak, apply=True)
        self.assertTrue(rep["labels"]["full_story_part1"]["reason"].startswith("CURRENT_ENTRY_NOT_OVERWRITABLE"))


if __name__ == "__main__":
    unittest.main()
