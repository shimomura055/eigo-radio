# C3 test results (RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C3, 2026-10-10, API 0 / cost JPY 0)

Branch `feature/factlock-rf-wiring-01` (HEAD after C3 commits). Command: `.venv/Scripts/python.exe -m pytest <files> -q -p no:cacheprovider`

## 1. C3 targeted set + C2 set (same file list as C2 = regression check)
Files: er053_*_test_01.py (C1+C2+C3) / er019_family_x_*test*.py / er019_writer_run_summary_reconstruction_01_test_01.py /
er012_e_family_entertainment_two_level_runner_test_01.py / er052_factlock_{sweep,writer_trial}_01_test_01.py /
er052_open243_m123_trial_test_01.py / er052_factlock_astra_e2e_runner_01_test.py / er006_model_routing*test*.py (33 files)
Result: **644 passed, 14 skipped, 0 failed** (C2 baseline: 610 passed / 14 skipped; +34 = new C3 tests: 33 in er053_c3_audio_guard_test_01.py + 1 queue 12x25 test).
skipped 14 = same legacy Trial tests as C2 (reason strings in the files).

## 2. Full repo suite (er*test*.py 249 files, excl. er015_standard_a2_6000_... [known collection error, unrelated])
Result: **36 failed, 5781 passed, 14 skipped, 362 subtests passed** (11m41s).
C2 result was 37 failed / 5733 passed. Difference:
- 36 failures are exactly the set classified at C2 as unrelated: 32 pre-existing at f71dbb41 (er003_test_p2j_investigate 4 / er006_asr_provider_routing 2 /
  er006_batch_tts_wiring 10 / er006_kp5_canonical_bug 4 / er007_ja_secondary_asr 4 / er008_n8_cost_compute_pricing_fix_24 2 /
  er011_open112_trend_synthesis 3 / er025_..._b1b_en_wiring 1 / er040 1 / er043 1) + 4 order-dependent er006_secondary_asr_01_test (pass alone).
- The 1 C2-era flaky failure (er053_review_queue_01_test_01::test_concurrent_appends_no_loss, PermissionError) is gone (C3-5).
- No new failure. +48 passed vs C2 (new C3 tests + the C2->C3 test additions).
Test-run side effects on tracked files (er005_output/cost_baseline_01/cost_summary.json, er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl)
were restored with `git checkout --` (those two only).

## 3. C3-5 reproduction
Pre-fix module (HEAD copy) 12 threads x 25 appends: 1 of 6 runs raised PermissionError (299/300 rows). Post-fix: 15 of 15 runs 0 errors / 300 rows;
pytest `test_concurrent_appends_12_threads_x_25_rounds_zero_failures` PASS.

## 4. Pricing coverage prerequisite (G-4) : pricing_coverage_audio_c3.json
627 raw_usage_log.jsonl scanned; every (provider, model) that would need token pricing (no cost_usd) is registered for input/output
EXCEPT gpt-5.6-terra (6 records, historical er016 Trials, not on the Production audio/entertainment path).
