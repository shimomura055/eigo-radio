# TEST_PLAN_02 — offline test(Phase 1、API 0)

実行環境: `$env:PYTHONPATH="docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/env_stub"; $env:NETBLOCK_LOG=<log>; py -m pytest <files> -q -p no:cacheprovider`(外部接続遮断+空stub。DESIGN_02 §K)。`.venv`は使わない。

## 新規test(全てoffline・mock/fake backend、実API 0)
| file | 件数(PASS) | 対象 |
|---|---|---|
| er122_fz_ctx_policy_test_01.py | policy/state機械/resume/cooldown/M-1,2,4/hook=None golden一致 | M-1,M-2,M-3,M-4,M-9 |
| er122_fz_ctx_notes_test_01.py | Trial逐語移植・53 clip style sha一致・chunk畳み戻し・LLM失敗STOP・story key解決 | M-5〜M-7,TEST-01,11 |
| er063_fz_ctx_wiring_test_01.py | stage経由の配線・reuse_key・policy固定・X/Y/narrator不変・旧規則残存 | M-5,M-8,R-2,W1〜W16 |
| er122_fzcw_runtime_evidence_test_01.py | Phase 2 driver(NG方向のみ・kill・ledger差分・argv)mock | M-10,R-1 |
合計 93 passed(新規4ファイルを一括実行)。

## 既存test回帰(変更前=HEAD基準 vs 変更後、同一stub環境)
`baseline_regression/`: base3_failed_* と after2_failed_*(er026のみbase3b/after3)の失敗test ID集合を比較。
| suite | base failed | after failed | 差分 |
|---|---|---|---|
| er078 | 53 | 53 | なし |
| er012 | 0 | 0 | なし(242 passed) |
| er063 | 9 | 9 | なし(新wiring test含め131 passed) |
| er109 | 44 | 44 | なし |
| er118 | 3 | 3 | なし |
| er117 | 5 | 5 | なし |
| er103 | 101 | 101 | なし |
| er026(posthoc除く) | 27 | 26 | 減1(`test_dry_run_each_single_stage`、並行実行由来のflake。新規failは0) |
既存failは全て変更前から存在(stub環境でのimport/環境依存)。新規failureは0。

## hook=None同一性
`golden/golden_hook_none_01.json`(基準commit `ab111631c`の変更前コードで凍結、MANIFESTにsource/golden sha)と全8+6シナリオでバイト一致。
