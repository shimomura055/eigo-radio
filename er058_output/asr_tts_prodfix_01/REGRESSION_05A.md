# REGRESSION_05A(委任_05A、2026-10-12)
関連suite 168ファイル(er003/006/007/008/011/012/019/020/025/033/053系、pytest、commit d40cfbc7後)。
- main(e6f33c4f、worktree eigo-radio-prodfix-base): 94 failed / 8 errors / 3149 passed(既存fail集合)。
- feature(d40cfbc7): 93 failed / 8 errors / 3150 passed。
- 集合差分: 新規failure **0**。main側のみfailの1件(er053_c3_audio_guard MainStageTests::test_rf_unavailable_still_reaches_tts_via_main)はmain側のflaky/未commit差分起因でfeatureではPASS。
- 修正前(M1〜M3適用直後)に出た新規7件はtest側の追従で解消済み: er007 AzureStrictCancelTests 4件(cl.record未初期化→mock)、er012_b NarratorHeadingRetryPolicyAlignmentTests 1件(fake引数追従)、er020 ProductionModuleUnchangedTest 2件(commit後にPASS)。
- 新規test `er058_asr_tts_prodfix_01_test_01.py` 27件PASS。
