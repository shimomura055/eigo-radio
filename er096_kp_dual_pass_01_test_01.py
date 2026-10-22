"""er096_kp_dual_pass_01(旧KPDUAL「Primary・Secondary両方PASS必須」、OPEN-440)は **履歴script** です。
Production判定は KP-THREE-ASR-MAJORITY-PRODUCTION-01(OPEN-451、2026-10-22ユーザー承認)で3-ASR多数決(er104_*)へ置換済みです。
本testは「履歴として残す」ことを機械的に固定するだけです(旧dual判定のtestは er104_kp_vote_wiring_test_01.py へ移設・3-ASR版に更新):
  - Production .py が er096_* をimportしない(量産経路は er104 のみ)
  - judge に旧識別子(dual_required / NG_DUAL_PRIMARY_NOT_PASS)が残っていない(撤去済み)
  - er096 module自体は履歴として存在し、importできる(er096_kp_dual_runtime_evidence_01 / er099 が読む)
実行: .venv/Scripts/python.exe -m unittest er096_kp_dual_pass_01_test_01 -v"""
import dataclasses
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


class HistoricalOnly(unittest.TestCase):
    def test_er096_exists_and_is_marked_superseded(self):
        import er096_kp_dual_pass_01 as kd
        self.assertEqual(kd.SUPERSEDED_BY, "er104_kp_vote_reuse_01")
        with self.assertRaises(RuntimeError):
            kd.evaluate_dual("take part", "Take part.", "nonexistent.wav")

    def test_production_modules_do_not_import_er096(self):
        pat = re.compile(r"^\s*(?:import|from)\s+er096_", re.M)
        offenders = []
        for f in sorted(os.listdir(ROOT)):
            if not f.endswith(".py") or f.startswith("er096_"):
                continue
            txt = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
            if pat.search(txt) and not ("_test" in f or f.startswith("er099_") or "_trial" in f):
                offenders.append(f)
        self.assertEqual(offenders, [])

    def test_old_judge_identifiers_are_removed(self):
        import er078_asr_unified_judge_01 as uj
        self.assertNotIn("dual_required", {f.name for f in dataclasses.fields(uj.AttemptCtx)})
        self.assertFalse(hasattr(uj, "NG_DUAL_PRIMARY_NOT_PASS"))
        self.assertIn("vote_required", {f.name for f in dataclasses.fields(uj.AttemptCtx)})


if __name__ == "__main__":
    unittest.main()
