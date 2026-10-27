# REGRESSION_M_01 全体回帰(委任_05M、API 0、2026-10-27)

## 実行
`.venv\Scripts\python.exe run_project_regression.py --pattern <P> --allow-non-test-pattern`(3 patternを並列起動。unittest discover)。
| pattern | collected | passed | failed | errors | skipped |
|---|---|---|---|---|---|
| `er0*_test_*.py`(er003/er019/er026/er053/er062/er063含む) | 7373 | 7352 | 6 | 2 | 10 |
| `er1*_test_*.py`(er119/er120/er121/er128含む) | 1949 | 1918 | 19 | 10 | 2 |
| `er_*test*.py`(er_learning_highlight*/er_page_audience*) | 40 | 40 | 0 | 0 | 0 |
個別: `er128_kp_confirmed_content_{test,slot23_test,02b_test}_01`、`er026_z_highlight_wiring_test_01`(47件)は全PASS。

## 初回(接続直後)の本変更起因失敗と対処
接続直後の初回回帰で、旧(マーク無し)記事を前提にする既存test 約50件が失敗(new_reviewがstd_part1を付与→a2が`--vocab`必須/Std Part 1あり/display_spec導出)。**期待値(旧挙動)は変えず**、`er119_test_support_01.legacy_unmarked_class/legacy_unmarked_flow`でマーク発行だけを無効化して旧reviewを再現(production不変)。対象: er003_kp_general_explanation_01_runner_integration(ZPart1Tests)、er003_test_kp_gloss_person_alignment(ZPersonGate)、er026_z_highlight_wiring(plain fixture)、er117_z_chunk_wiring、er119_kp_human_review_01(1件)、er119_kp_p7w5_e2e、er119_x_wiring、er119_z_wiring(TestZWait)、er120_part2_wiring_integration、er121_family_y_runner_01(StudyTextWiring)、er121_y_highlight_wiring(UnmarkedPipeline)、er128_kp_confirmed_content_{test,slot23,02b}。接続後の正例(マーク付き)はC/D/E班test+slot23_test(新規4件)で固定。

## 残失敗の分類(最終回帰、計38件)
比較基準: 4 production file(er119/er128/er121 Y runner/er026 Z runner)とtest 2本をHEADへ戻した状態で同一idを実行(24件が同様に失敗)。
| 分類 | 件数 | 内訳 |
|---|---|---|
| **本変更起因** | **0** | 初回の約50件は上記legacy再現で解消。残りに本変更で新たに生じた失敗なし |
| 既知(HEADでも失敗=既存OPEN-543系の静的/golden/隔離群) | 24 | er019_x_std_chunk_opus R4Hunk、er020 RegressionCorpus、er053_c2/er053_family_x_factlock、er054_z_story_pool、er064_kp_int ProductionUnchanged、er105/er108/er110×3/er112_trial01・06/er119_isolation/er119_grammar_review×2/er109_wiring_golden×3/er109_xz_isolation×2(静的scan・golden・隔離系が中心。個別原因は未精査、HEAD相当でも失敗することのみ確認)、er119_z_wiring `test_part1_items_follow_vocab_confirmed_five`、er003 ZPart1Tests `test_kp_expression_change…` |
| 作業ツリー依存(commit後に再確認) | 3 | er112_kp_gm_trial_03 `test_no_production_edit`、er124_kp_phrase_word{,5}_trial `test_production_files_not_modified_vs_head`(『productionファイルのHEAD差分が空』を見るtest。本commitでproduction file(er026 runner等)がdirtyの間のみ失敗)→commit 1684e19f5後に再実行しPASS確認済み |
| 並列実行時の共有state競合(単独実行PASS) | 9 | er117_z_chunk_wiring ZGateAndAssemblyTests×5、er120 ZPart2Integration×4(`unittest er117… er120… er003…`の逐次実行で68件中、既存の1件を除きPASS) |
| 環境/fixture | 2 | `er003_test_bad.FixtureTests.test_case_0`(実ファイルの無いdiscovery id)、`er003_test_kp_gloss_alignment_stop_paths.T3StopPaths.setUpClass`(HEADでも`KP_REVIEW_PENDING: Standard`で失敗する既存事象。本変更前後で同一) |
genai/faster_whisper等の未導入起因: 今回の失敗には該当なし。
