# 委任_05A runtime evidence: M3 cool-down通算判定 / M1 実在results写しarchive / M2 SCG費用計上。
# API課金0(全てmock/保存済みファイルの写し)。実行: python er058_output/asr_tts_prodfix_01/runtime_evidence_02.py
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import er058_asr_tts_prodfix_01_test_01 as t  # noqa: E402


def main():
    # M3: 通算3回目直前にだけcool-downが発火する(sleepはmock、600秒を待たない)
    for label, kw in [
        ("lap1(標準2+fallback1、通算3回目=fallback)", dict(max_attempts=3, standard_attempts=2, prior_generations=0, cooldown_total_budget=3)),
        ("lap2(1周目で1回消費、残り2=標準2回、通算3回目=標準2回目)", dict(max_attempts=2, standard_attempts=2, prior_generations=1, cooldown_total_budget=3)),
        ("lap3(2回消費、残り1=標準1回、通算3回目)", dict(max_attempts=1, standard_attempts=1, prior_generations=2, cooldown_total_budget=3)),
    ]:
        c = t.CooldownOverallAttemptTest("test_remaining_one_runs_no_fallback_for_real_inner")
        c.setUp()
        try:
            fb = c._run(**kw)
            print(label, "-> cooldown呼出(通算試行,総予算,gate,発火):", c.cool, "fallback呼出", fb.call_count)
        finally:
            c.tearDown()
    suite = unittest.TestSuite()
    for n in ("ScgAzureCostRecordTest", "ArchiveFailureIsolationTest"):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(t, n)))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
