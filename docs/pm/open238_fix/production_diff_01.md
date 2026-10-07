# OPEN-238 Production配線 diff要約(委任_01、未commit、全文は`git diff`)

## 変更ファイル
1. `er052_open233_self_recovery_precheck_01.py`(+57/-1)
   - L159-207付近: `extract_percentages_strict(text)` 新設(DEV版と同一ロジック、定数 `_OPEN238_*`、docstring相当コメントにOPEN-238・規則を明記)。現行 `extract_percentages`・`FRACTION_WORD_TO_PERCENT`・`PERCENT_RE` は無変更。
   - `check_number_mismatch` L311付近: `foreign_observed` 計算のみ、percent種別なら `extract_percentages_strict(article_text)` を使用(count種別は従来の `observed`)。`expected`・`observed`・`_any_close`/natural rounding判定・`all_ledger_pct` は現行のまま。
2. `er052_open233_self_recovery_flow_runner_01.py`(+2/-1)
   - `resolve_precheck_target_sentence` L8093-8094: 数値抽出を `precheck.extract_percentages_strict(s)` へ(counts側は現行)。
3. `er052_open238_precheck_fix_dev_01.py`: docstring先頭1行追記のみ(Trial記録用)。
4. 新規テスト `er052_open233_open238_precheck_strict_test_01.py`(12件、Production直接)。
5. 新規証跡 `er052_output/open238_precheck_fix_trial_01/production_regression/`。

## 他の呼び出し(変更なし)
precheck L322/L666、runner L1535/L2585/L2838/L3090、coverage_checker L475は現行 `extract_percentages` のまま。Stage 2・再分類・floor発火後Stage 2スキップ・`PRECHECK_MODE`・`OPEN233_APPROVED_FLOW_SWITCHES` 無変更。

## 検証
- 新規12件 PASS。既存: precheck 23 / flow_runner 720 / checker_floor_prod_wiring 59 / stage1_coverage_checker 75 / recheck_coverage 17 / stage2_production 10 / e2e_acceptance 7 = 全PASS(失敗0)。変更前も同じ件数で全PASSを確認済み。環境にdotenv等が無いためimport stub(precheck_baseline.install_stub)経由で実行。
- Regression: PRODUCTION_REGRESSION.md(26 run: 2->0、他25 run不変、他経路bit単位不変、9 run判定変化なし)。

## Opus条件Cレビュー論点(3点)
1. 変更が最小差分(foreign計算1箇所+対象文特定1箇所+新関数)に収まっているか。
2. 他呼び出し経路(L322/L666/runner/coverage_checker)の不変(o2_bitwise_check.jsonで確認)。
3. テスト・Regressionの十分性(26 run以外の実データ・残存FP("seeking a third."、"half the time")は仕様上許容と記録済み)。
