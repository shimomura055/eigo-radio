# -*- coding: utf-8 -*-
"""HR-SELECTION-FLOW 委任_03A: ニュアンス解説経路の仕様②(選定後の重複=アラームのみ・非停止)の発火証拠(API 0・全てmock)。
test(er134_nuance_runner_wiring_test_01 / er128_nuance_hr_test_01)を実行し、各testの一時dir(確定sidecar・nuance_redundancy_alarm.json・nuance_result.json)を
evidence配下へ複製して残す(shutil.rmtreeを一時的に差し替え、削除前にコピー)。実LLMは呼ばない。"""
import os, shutil, sys, unittest, json

ROOT = "C:/Users/tensh/eigo-radio"
sys.path.insert(0, ROOT); os.chdir(ROOT)
OUT = "C:/Users/tensh/eigo-radio-evidence/hrq3a/nuance_mock"
os.makedirs(OUT, exist_ok=True)
_real = shutil.rmtree
_n = [0]


def keep_then_rm(path, *a, **k):
    p = str(path)
    if os.path.isdir(p) and "nuance_redundancy_alarm.json" in "".join(fs for _, _, f in os.walk(p) for fs in [" ".join(f)]):
        _n[0] += 1
        shutil.copytree(p, f"{OUT}/case_{_n[0]:02d}", dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.wav", "*.mp3"))
    return _real(path, *a, **k)


shutil.rmtree = keep_then_rm
import er134_nuance_runner_wiring_test_01 as W
import er128_nuance_hr_test_01 as H
names = ["test_pool_conflict_chosen_at_hr_is_alarm_only_adoption_proceeds_spec2", "test_no_pool_conflict_records_empty_alarm_file_and_pass_spec2",
         "test_kp_set_changed_after_nuance_confirm_is_alarm_not_stale_stop_spec2"]
suite = unittest.TestSuite()
for n in names:
    suite.addTest(W.T3_Overlap(n))
suite.addTest(H.T2_CoverageAndConflicts("test_pool_conflict_is_alarm_only_when_that_item_is_chosen_spec2"))
res = unittest.TextTestRunner(verbosity=2).run(suite)
shutil.rmtree = _real
summ = {"tests_run": res.testsRun, "failures": len(res.failures), "errors": len(res.errors), "kept_cases": _n[0]}
json.dump(summ, open(f"{OUT}/summary.json", "w"), indent=1)
print(summ)
sys.exit(0 if res.wasSuccessful() else 1)
