# -*- coding: utf-8 -*-
"""委任_08 Trial_03(DEV)のAPI 0 test: 集合の独立性・盲検表のarm非露出・Production module非編集。"""
import json
import re
import subprocess
import unittest
from pathlib import Path

import er112_kp_gm_trial_03 as X

ROOT = Path(__file__).resolve().parent


class TestTrial03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A = X.kpall()

    def test_counts_and_independence(self):
        hard = [k for k, v in self.A.items() if v["tier"] == "hard"]
        normal = [k for k, v in self.A.items() if v["tier"] == "normal"]
        self.assertEqual((len(hard), len(normal)), (20, 40))
        t2 = set(X.T.kpset())
        self.assertFalse(set(normal) & (t2 - set(hard)), "normalがTrial_02集合と重複")
        fam = [self.A[k]["family"] for k in normal]
        self.assertEqual((fam.count("X"), fam.count("Z")), (30, 10))

    def test_blind_table_hides_arms(self):
        if not (X.OUT / "fable_blind_std_03.md").exists():
            self.skipTest("blind表未生成")
        t = (X.OUT / "fable_blind_std_03.md").read_text(encoding="utf-8")
        body = t.split("| # |", 1)[1]
        self.assertIsNone(re.search(r"\bG[023]\b|rep[12]", body))
        key = json.load(open(X.OUT / "fable_blind_std_03_key.json", encoding="utf-8"))
        self.assertEqual(len(key), 60)
        for k, m in key.items():
            self.assertEqual(sorted(m.values()), sorted("%s/rep%d" % (a, r) for a in X.ARMS for r in (1, 2)))

    def test_no_production_edit(self):
        out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "er003_key_words_gloss_alignment.py", "er019_family_x_kp_explanation_01.py",
                              "er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
                              "er003_v1_n3_01_scaffold_generate.py"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
