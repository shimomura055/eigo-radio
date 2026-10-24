# REGRESSION_03(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-489修正の全回帰。API 0)

環境注記: 本環境(Python 3.14)には `google.genai` / `pykakasi` が無く、TEST-HYGIENE-02(REGRESSION_BASELINE_01.md、failed 0/errors 0)の前提環境とは異なる。このため絶対件数ではなく**『修正前モジュール(base_HEAD03の er006/er021)』と『修正後(working tree)』の同条件比較**で自分起因の失敗を判定した(base側は `sys.modules` へ修正前の2moduleを先に差し込む実行ラッパで、同じ test 母集団・同じ作業ツリー)。

| 群 | 修正後 | 修正前(同条件) | 失敗ID集合の差 |
|---|---|---|---|
| `run_project_regression.py`(unittest, 4,870件) | passed 4,556 / failed 60 / errors 233 / skipped 4 | passed 4,554 / failed 62 / errors 233 / skipped 4 | 修正後のみ失敗=1(`er020_tts_retry_local_rewrite_fullseg_test_01 ... test_recorded_candidates`: 単独再実行でPASS。他agentが更新中の `er011_output/local_rewrite_recovery/...` を読む記録corpus testで並行実行時の一時状態) / 修正前のみ失敗=3(OPEN-489の新規test case 2件[修正前は失敗=期待どおり]+並行依存の `er026 ... test_legacy_dry_run_flag_maps_to_dry_run`) |
| pytest群(er078*/er103/er104*/er105/er106/er108/er109 + er021/er006 時刻test) | 251 failed / 576 passed / 112 errors | 253 failed / 576 passed / 112 errors | **失敗・エラーID集合 317件が完全一致**(差0。全て環境依存=google.genai/pykakasi未導入・collection error) |
| 本件関連test(単独) | `er021_time_numeral_test_01`(+新規 AndSplitOpen489 4件)・`er006_time_numeral_test_01`・`er078_time_atom_test_01` = 19 passed / 80 subtests | — | — |

結論: 自分起因の新規失敗 0。OPEN-489の追加testは修正前で失敗(2件)・修正後で成功。
