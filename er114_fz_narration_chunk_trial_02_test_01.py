# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er114_fz_narration_chunk_trial_02 as r


class T(unittest.TestCase):
    def test_f0_sine(self):
        t = np.arange(0, 1.0, 1 / r.SR24)
        x = 0.3 * np.sin(2 * np.pi * 200 * t)
        o = r.f0_and_centroid(x)
        self.assertTrue(190 <= o["f0_median_hz"] <= 210, o)

    def test_arm_sources_and_alt_reuses_b_r1_part1(self):
        self.assertEqual(r.ARM_SOURCE["B_alt"]["full_story_part1_c1"], "B_r1")
        self.assertEqual(set(r.ARM_SOURCE["A_r2"].values()), {"A_r2"})
        self.assertEqual(set(r.EST_JPY), {"A_r2", "B_r1", "B_fine", "B_alt"})

    def test_reserve_within_cap(self):
        self.assertLessEqual(sum(v * r.RESERVE_FACTOR for v in r.EST_JPY.values()), r.CAP_JPY)

    def test_audit_hook_blocks_write_outside_allowed_but_allows_inside(self):
        code = (
            "import sys, os, tempfile; sys.path.insert(0, %r); os.chdir(%r)\n"
            "import er114_fz_narration_chunk_trial_02 as r\n"
            "ok_dir = os.path.join(r.ROOT, r.OUT, 'audit_selftest'); os.makedirs(ok_dir, exist_ok=True)\n"
            "r.install_audit([r.OUT])\n"
            "open(os.path.join(ok_dir, 'a.txt'), 'w').write('x')\n"
            "bad = os.path.join(r.ROOT, 'er114_audit_selftest_must_not_exist.txt')\n"
            "try:\n"
            "    open(bad, 'w').write('x'); print('NOT_BLOCKED')\n"
            "except PermissionError as e:\n"
            "    print('BLOCKED')\n"
            "print(os.path.exists(bad)); print(len(r._AUDIT['violations']))\n"
            "os.remove(os.path.join(ok_dir, 'a.txt')); os.rmdir(ok_dir)\n" % (ROOT, ROOT))
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8").stdout.split()
        self.assertEqual(out[:3], ["BLOCKED", "False", "1"], out)

    def test_judge_boundary_and_speed_logic(self):
        meas = {"arms": {a: {"clips": {c: {"alignment": {"asr_words": 100, "ref_words": 100, "all_paragraphs_aligned": True, "match_ratio": 1.0}} for c in r.CLIP_IDS}}
                         for a in ("A", "A_r2")}}
        self.assertEqual(r.BOUNDARY_TOL_DB, 3.0)
        self.assertEqual(r.SPEED_ART300_RATIO_MAX, 0.97)
        self.assertEqual(r.ASR_RATIO_RANGE, (0.97, 1.03))


if __name__ == "__main__":
    unittest.main()
