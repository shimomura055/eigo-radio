# C2 test results (RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2, 2026-10-10, API 0 / cost JPY 0)

Command: `.venv/Scripts/python.exe -m pytest <files> -q -p no:cacheprovider` (branch `feature/factlock-rf-wiring-01`)

## 1. C2 targeted set (all PASS)
Files: er053_*_test_01.py (C1+C2) / er019_family_x_*test*.py / er019_writer_run_summary_reconstruction_01_test_01.py /
er012_e_family_entertainment_two_level_runner_test_01.py / er052_factlock_{sweep,writer_trial}_01_test_01.py /
er052_open243_m123_trial_test_01.py / er052_factlock_astra_e2e_runner_01_test.py / er006_model_routing*test*.py
Result: **610 passed, 14 skipped, 0 failed** (skipped 14 = legacy Trial tests whose target was physically removed:
er052_factlock_astra_e2e_runner_01_test StubDryRunTest 10 + er052_open243_m123_trial_test 4; reason strings in the files).

New C2 tests: er053_c2_old_checker_removal_test_01.py (15) / er053_c2_wiring_test_01.py (15) /
er019_family_x_entertainment_production_runner_01_test_01.py (20, rewritten) / er012_e..._test_01.py (U-2 + writer stage, 30 total) /
er019_family_x_ja_writer_o_r1_r2_01_test_01.py (7, rewritten) / er019_family_x_ja_recheck_retry_01_test_01.py (4, disabled->removal-fixation) /
W-1 test E5 golden (35 total).

## 2. Full repo suite (249 test files, `er*` only; excl. er015_standard_a2_6000_... [known collection RuntimeError, unrelated])
Branch HEAD (after commits 1-3): **37 failed, 5733 passed, 14 skipped, 362 subtests passed** (11m57s)

Baseline = same suite on a git worktree of pre-C2 commit f71dbb41 (worktree lacks untracked files, so its failure count is larger: 116 failed + 8 errors).

Classification of the 37 failures:
- 32: also fail at pre-C2 f71dbb41 (pre-existing, unrelated to C2): er003_test_p2j_investigate(4) / er006_asr_provider_routing(2) /
  er006_batch_tts_wiring(10) / er006_kp5_canonical_bug(4) / er007_ja_secondary_asr(4) / er008_n8_cost_compute_pricing_fix_24(2) /
  er011_open112_trend_synthesis(3) / er025_..._b1b_en_wiring FamilyXRunnerKwargWiringTests(1) / er040(1) / er043(1).
- 4: er006_secondary_asr_01_test (order-dependent): passes alone (29 passed); fails when run after er002_test_ja_free_markdown_restore*.py
  (bisected). Those test files import only er002_ja_free_markdown_restore*, i.e. independent of C2.
- 1: er053_review_queue_01_test_01::QueueTests::test_concurrent_appends_no_loss = flaky C1 latent bug: on Windows `_IndexLock.__enter__`
  (os.open O_CREAT|O_EXCL) can raise PermissionError (not FileExistsError) under thread contention (reproduced 3 of 25 trials of 12 threads).
  Not fixed in C2 (out of scope); Production impact is low because save_queue is non-blocking (falls back to out_dir with WARN).
  Suggested 1-line fix: `except (FileExistsError, PermissionError):`.
Test-run side effects on tracked files (er005_output/cost_baseline_01/cost_summary.json, er025_output/.../telemetry.jsonl) were restored with `git checkout --`.

## 3. Trial test handling (S3-4: Trial runners cannot run on HEAD after removal; reproduce via worktree of f71dbb41)
- er052_factlock_sweep_01_test_01 / er052_factlock_writer_trial_01_test_01: removed the obsolete `full_ledger_text=None` argument (3 call sites) -> pass.
- er052_open243_m123_trial_test_01: 4 tests skipped (functions removed: open243_majors_only_in_summary / open243_m1_summary_only_retry / open243_g3_record_translation_minor).
- er052_factlock_astra_e2e_runner_01_test: StubDryRunTest (10 tests, child-process runs of the Trial runner with old Checker arms) skipped.
