# HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02: 隔離helperの検証test
from __future__ import annotations

import hashlib
import os
import re
import unittest

import test_state_isolation_01 as iso
import er011_human_review_lock_01 as lock

PROD = ("er011_output/attempt_history.jsonl",
        "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
        "er007_output/ja_asr_cascade_01/human_review_queue.jsonl")

# 実測(2026-10-22、全_test*.pyを1fileずつ実行しattempt_history.jsonlのサイズ変化で特定)で
# Productionの監査ログへ追記していた15 test file。全て隔離importを持つこと。
KNOWN_WRITER_TESTS = (
    "er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01.py",
    "er007_ja_scg_test_01.py",
    "er007_ja_tts_retry_path_fix_test_01.py",
    "er011_ending_clarity_fallback_01_test.py",
    "er011_human_review_lock_01_test_01.py",
    "er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py",
    "er011_tts_attempt_audio_retention_wiring_01_test.py",
    "er012_editorial_b_family_production_phase1_test_01.py",
    "er019_family_x_fx_20261016_wiring_01_test_01.py",
    "er019_family_x_variable_role_style_wiring_01_test_01.py",
    "er019_test_family_x_completion_02_integration.py",
    "er020_tts_retry_local_rewrite_01_test_01.py",
    "er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py",
    "er063_family_z_audio_01_pd06_run_style_test_01.py",
    "er063_family_z_audio_01_test_01.py",
)


def _snap(p):
    if not os.path.exists(p):
        return None
    b = open(p, "rb").read()
    return (b.count(b"\n"), hashlib.sha256(b).hexdigest())


class StateIsolationTests(unittest.TestCase):
    def test_attempt_history_path_redirected(self):
        self.assertNotEqual(os.path.abspath(lock.ATTEMPT_HISTORY_PATH), os.path.abspath(PROD[0]))
        self.assertEqual(lock.ATTEMPT_HISTORY_PATH, iso.ISOLATED_ATTEMPT_HISTORY)

    def test_write_goes_to_tmp_and_production_unchanged(self):
        before = [_snap(p) for p in PROD]
        lock.append_attempt_history_event("isolation_probe.mp3", "isolation_probe", {"note": "tmp only"})
        self.assertTrue(os.path.exists(iso.ISOLATED_ATTEMPT_HISTORY))
        self.assertEqual([_snap(p) for p in PROD], before)

    def test_known_writer_tests_import_isolation(self):
        for f in KNOWN_WRITER_TESTS:
            src = open(f, encoding="utf-8").read()
            self.assertRegex(src, re.compile(r"^import test_state_isolation_01\b", re.M), f)


if __name__ == "__main__":
    unittest.main()
