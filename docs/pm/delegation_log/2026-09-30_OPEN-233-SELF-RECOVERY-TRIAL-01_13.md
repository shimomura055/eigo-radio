管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_13: Opus L2レビュー#3
所見の逐語保存+iteration 5 = R3''/R3'''較正+Stage2 2-of-2安定化+
cite-or-release+品質劣化検出v2+Rewrite品質制約+29 instance×n=2実測+
読み比べページ更新)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)

到達上限Status: `ITER5_DONE_TARGET_MET`または`ITER5_DONE_IMPROVEMENT_
NEEDED`(実測結果=後者、REPORT§14-9参照)。禁止事項: 削除・移動・rm・
git clean・git stash・rebase/reset/amend/force push禁止。
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`はcommit対象外。
`git add -A`禁止(パス指定add)。Production正式path(既存の量産経路)
への無断実装禁止(iteration5もTrial実装のみでProduction配線しない)。
既存iteration1〜4(`er052_output/open233_self_recovery_flow_runner_01/`
`_iter2/`/`_iter3/`/`_iter4/`)・委任_08〜_12証跡ファイルは変更しない。
item7(floor精度)は既存安全装置の弱め方向変更であり明示的にユーザー
判断待ちとして未実装、item8(fact_id複数箇所Rewrite)はPhase2設計
課題として未実装(いずれも独断で実装しない)。

## 1. 事前指定Read一覧

`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§12、`docs/pm/design_
open233_self_recovery_flow_01.md`§4-9/§7-0-iter4/§8-5/§9-1⑨、
`er052_open233_self_recovery_flow_runner_01.py`(+test)、`er052_
open233_self_recovery_stage2_calibration_01.py`(RUBRIC_R3_NATURAL_
INTERPRETATION/RUBRIC_R3_PRIME)、Opus L2レビュー#3全文(委任文に
verbatim添付)、`er052_output/open233_self_recovery_flow_runner_01_
iter4/instances/*.json`(STAGE4到達3件、negative群Rewrite発火4件)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: `RUBRIC_R3_PRIME`/`FLOOR_FLAGS`/`apply_floor`/
  `run_stage2`/`measure_rewrite_quality_degradation`/`run_recheck`
  (`er052_open233_self_recovery_flow_runner_01.py`)、
  `RUBRIC_R3_NATURAL_INTERPRETATION`(`er052_open233_self_recovery_
  stage2_calibration_01.py`)、`NORMAL_GROUP_INSTANCE_IDS`
  (全ファイル横断)。
- 追記位置: `er052_open233_self_recovery_stage2_calibration_01.py`
  (RUBRIC_R3_DOUBLE_PRIME/RUBRIC_R3_TRIPLE_PRIME新規追加)、
  `er052_open233_self_recovery_flow_runner_01.py`(品質劣化検出v2・
  Rewrite品質制約・cite-or-release・2-of-2安定化・n=2結合measures・
  Wilson CI・OUT_DIR iter5化、新規関数群多数)、`docs/pm/design_
  open233_self_recovery_flow_01.md`冒頭Status・§4-10[新設]・
  §4-11[新設]・§5-6[新設]・§6-3[新設]・§7-0-iter5[新設]・
  §8-6[新設]・§9-1⑩[新設]、`OPEN-233-SELF-RECOVERY-TRIAL-01_
  REPORT.md`§13[新規追加]・§14[新規追加]、`OPEN_ITEMS.md`OPEN-233行、
  `DECISION_LOG.md`末尾。

## 3. 実行内容

(a) `docs/pm/opus_l2_review_open233_self_recovery_03.md`へOpus L2
レビュー#3全文を逐語保存(作業A、¥0)。
(b) 較正harnessの正解ラベル是正(A2A3-1/A4-2→QUALITY)+Safety-critical
10claim名指しリストへの絞り込み(作業B項目1)。
(c) `er052_open233_self_recovery_stage2_calibration_01.py`へ
`RUBRIC_R3_DOUBLE_PRIME`(R3''、例示→原則書換)・`RUBRIC_R3_TRIPLE_
PRIME`(R3'''、項目1をさらに限定)を新設(作業B項目2)。
(d) `er052_open233_self_recovery_flow_runner_01.py`へStage2
2-of-2安定化(`apply_stage2_two_of_two`、作業B項目3)、cite-or-release
(`run_recheck_confirm`/`apply_cite_or_release`、Rewrite前後文ペア
付き、作業B項目4)、品質劣化検出v2(`measure_rewrite_quality_
degradation_v2`、重複段落/孤立逆接/語彙難化/hookフラグ、作業B項目5)、
Rewrite品質制約(`level_constraint_text`/`REGENERATION_EMPHASIS_
TEMPLATE`、Stage3 prompt注入+同一cycle内1回だけの再生成、作業B項目6・
Fable追加指示)を実装。
(e) regression test25件追加(既存67件+新規=92件、他4モジュール81件と
合わせ計173件PASS)。
(f) 新規`er052_open233_self_recovery_r3dprime_calibration_01.py`
(作業C)で既存13group・23claim評価セットをn=2実測。R3''(26call・
¥4.267)はB4-d未達のため委任文の条件付きパスに従い1回限りR3'''
(26call・+¥4.1773、累計¥8.4443)で全条件達成。
(g) `er052_open233_self_recovery_flow_runner_01.py --n_runs 2 --s1u`
で29 instance×n=2再実行(作業D、305call・¥62.3761・error0)。
sha256キャッシュでStage1 freshモードのsample間二重課金を回避。
n=2結合measures(`combine_n2_measures`、Wilson CI含む)を実装・実行。
(h) `user_test/open233_rewrite_compare_01/index.html`を
`index_iter4.html`へコピー保存(削除・移動せず保持)、新規
`er052_open233_self_recovery_rewrite_compare_page_iter5_01.py`
(作業E、API呼び出しなし)で`index.html`をiteration5版へ更新(収録
4記事、instances_s1読み直しのみ)。
(i) SSOT更新(design doc§4-10/§4-11/§5-6/§6-3/§7-0-iter5/§8-6/
§9-1⑩/冒頭Status、REPORT.md§13[訂正4点]・§14[iteration5結果]、
DECISION_LOG.md、OPEN_ITEMS.md)・delegation_log作成・
`python -m unittest`全PASS確認・`git diff --stat`でProduction・
既存証跡無変更を確認。

## 4. 実行コマンド全文

- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m py_compile er052_open233_self_recovery_flow_runner_01.py er052_open233_self_recovery_flow_runner_01_test_01.py er052_open233_self_recovery_stage2_calibration_01.py er052_open233_self_recovery_r3dprime_calibration_01.py er052_open233_self_recovery_rewrite_compare_page_iter5_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01 er052_open233_self_recovery_precheck_01_test_01 er052_open233_self_recovery_s1d_trial_01_test_01 er052_open233_self_recovery_stage2_production_01_test_01 er051_open233_checker_trial_variant_01_test_01`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_r3dprime_calibration_01.py --rubric r3dprime`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_r3dprime_calibration_01.py --rubric r3tripleprime`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --n_runs 2 --s1u`
- `cd /c/Users/tensh/eigo-radio && cp user_test/open233_rewrite_compare_01/index.html user_test/open233_rewrite_compare_01/index_iter4.html`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_rewrite_compare_page_iter5_01.py`
- `cd /c/Users/tensh/eigo-radio && git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er009_ledger_deviation_recalibration_02_test.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py er052_output/open233_self_recovery_flow_runner_01 er052_output/open233_self_recovery_flow_runner_01_iter2 er052_output/open233_self_recovery_flow_runner_01_iter3 er052_output/open233_self_recovery_flow_runner_01_iter4 er052_output/open233_self_recovery_stage2_calibration_01 er052_output/open233_self_recovery_stage3_rewrite_trial_01 er052_output/open233_self_recovery_s1u_alt_compare_01 er052_output/open233_self_recovery_r3_natural_calibration_01`

## 5. SSOT追記文

`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
iteration 5実測完了(Opus L2 #3是正+R3''/R3'''較正+2-of-2+
cite-or-release+品質劣化v2+n=2実測、委任_13、2026-09-30)」を追加。
`OPEN_ITEMS.md`OPEN-233行へ「2026-09-30追記(委任_13、iteration5
完了)」を追加しStatus列更新。`OPEN-233-SELF-RECOVERY-TRIAL-01_
REPORT.md`へ新規§13(Opus L2 #3と報告訂正)・§14(iteration5実測)を
追加。`docs/pm/design_open233_self_recovery_flow_01.md`冒頭Status・
§4-10[新設]・§4-11[新設]・§5-6[新設]・§6-3[新設]・§7-0-iter5[新設]・
§8-6[新設]・§9-1⑩[新設]を更新。`CURRENT_SPEC.md`は変更しない
(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)

明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、`DECISION_LOG.md`、
`OPEN_ITEMS.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`docs/pm/opus_l2_review_open233_self_recovery_03.md`、
`er052_open233_self_recovery_flow_runner_01.py`、
`er052_open233_self_recovery_flow_runner_01_test_01.py`、
`er052_open233_self_recovery_stage2_calibration_01.py`、
`er052_open233_self_recovery_r3dprime_calibration_01.py`、
`er052_open233_self_recovery_rewrite_compare_page_iter5_01.py`、
`er052_output/open233_self_recovery_flow_runner_01_iter5/`、
`er052_output/open233_self_recovery_r3dprime_calibration_01/`、
`user_test/open233_rewrite_compare_01/index.html`、
`user_test/open233_rewrite_compare_01/index_iter4.html`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_
13.md`。コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01:
iteration 5実測(Opus L2 #3是正・R3''/R3'''較正・2-of-2・
cite-or-release・品質劣化v2・n=2実測、委任_13)"。trailer:
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
ACTIVE_TASK*/RESULT_PACKET*/.envは add対象外。競合時は`git merge
origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`参照(作成できない場合はhandback本文に
含める)。
