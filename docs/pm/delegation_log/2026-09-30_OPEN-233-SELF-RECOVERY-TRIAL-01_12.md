管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_12: iteration 4 = Checker
許容線の再設計[自然な解釈はOK/事実の発明はNG]+不要Rewrite削減+追加測定
7項目+読み比べページ+29 instance再実行)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `ITER4_DONE_TARGET_MET`または`ITER4_DONE_IMPROVEMENT_
NEEDED`(実測結果=後者、§12-7参照)。禁止事項: 削除・移動・rm・git
clean・git stash・rebase/reset/amend/force push禁止。`docs/pm/
ACTIVE_TASK_C233P.md`/`RESULT_PACKET_C233P.md`はcommit対象外。
`git add -A`禁止(パス指定add)。Production正式path(既存の量産経路)
への無断実装禁止(iteration4もTrial実装のみでProduction配線しない)。
既存iteration1〜3(`er052_output/open233_self_recovery_flow_runner_01/`
`_iter2/`/`_iter3/`)・委任_08〜_11証跡ファイルは変更しない。

## 1. 事前指定Read一覧
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§10/§11、`docs/pm/design_
open233_self_recovery_flow_01.md`§4-2/§4-3/§4-8/§7-0/§9-1⑧、
`er052_open233_self_recovery_flow_runner_01.py`(+test)、`er052_
open233_self_recovery_stage2_calibration_01.py`(RUBRIC_R2/R2_PRIME)、
`er052_open233_self_recovery_stage2_production_01.py`、
`er052_output/open233_self_recovery_flow_runner_01_iter3/instances/
*.json`(STAGE4到達5件)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `RUBRIC_R2`/`FLOOR_FLAGS`/`apply_floor`/`run_stage2`
  (`er052_open233_self_recovery_flow_runner_01.py`)、
  `MATERIALITY_RUBRIC`/`RUBRIC_R2_PRIME`/`apply_r3_floor`
  (`er052_open233_self_recovery_stage2_calibration_01.py`)、
  `changed_certainty`(全ファイル横断)。
- 追記位置: `er052_open233_self_recovery_stage2_calibration_01.py`
  (RUBRIC_R3_NATURAL_INTERPRETATION/RUBRIC_R3_PRIME新規追加)、
  `er052_open233_self_recovery_flow_runner_01.py`(FLOOR_FLAGS改訂・
  run_stage2のrubric切替・追加測定7項目・S1-U反実仮想、新規関数群)、
  `docs/pm/design_open233_self_recovery_flow_01.md`冒頭Status・§4-9
  [新設]・§7-0-iter4[新設]・§8-5[新設]・§9-1⑨[新設]・§13[追記]、
  `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§12[新規追加]、
  `OPEN_ITEMS.md`OPEN-233行、`DECISION_LOG.md`末尾。

## 3. 実行内容
(a) `er052_open233_self_recovery_stage2_calibration_01.py`へ
`RUBRIC_R3_NATURAL_INTERPRETATION`(自然な解釈基準、tie-break反転)を
新設。
(b) `er052_open233_self_recovery_flow_runner_01.py`の`FLOOR_FLAGS`から
`changed_certainty`を除外、`run_stage2`のrubricを`s2c.RUBRIC_R2`から
新rubricへ切替、OUT_DIRをiteration4用へ変更。
(c) 新規`er052_open233_self_recovery_r3_natural_calibration_01.py`
(作業B)で既存13group・23claim評価セットをn=2実測(26 call)。Safety側
誤降格5件を検出し受入条件未達のため、`RUBRIC_R3_PRIME`(fail-closed
明確化2点追加)で1回限りの再較正(26 call)を実施、誤降格2件へ縮小。
`run_stage2`をR3_PRIMEへ切替確定。
(d) regression test追加(既存67件PASS)。
(e) `_iter4_additional_measures`/`measure_rewrite_quality_
degradation`/`compute_s1u_counterfactual`を新規実装し追加測定7項目+
S1-U反実仮想比較(0 call)を`aggregate_measurements`/`main`へ配線。
(f) `er052_open233_self_recovery_flow_runner_01.py --s1u`で29
instance再実行(作業C、139 call・¥28.5644)。実行完了後、Windows
console(cp932)へのensure_ascii=False printでUnicodeEncodeErrorが
発生し2回目のprint文でプロセスが異常終了する実害を発見(証跡json自体は
save_json済みで無事)、print文のみensure_ascii=Trueへ修正。
(g) 新規`er052_open233_self_recovery_rewrite_compare_page_01.py`
(作業D、API呼び出しなし)でRewrite前後比較ページを生成、
`user_test/open233_rewrite_compare_01/index.html`として保存。
(h) SSOT更新・delegation_log作成・`python -m unittest`全PASS確認・
`git diff --stat`でProduction・既存証跡無変更を確認。

## 4. 実行コマンド全文
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m py_compile er052_open233_self_recovery_flow_runner_01.py er052_open233_self_recovery_flow_runner_01_test_01.py er052_open233_self_recovery_stage2_calibration_01.py er052_open233_self_recovery_r3_natural_calibration_01.py er052_open233_self_recovery_rewrite_compare_page_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01 er052_open233_self_recovery_precheck_01_test_01 er052_open233_self_recovery_s1d_trial_01_test_01 er052_open233_self_recovery_stage2_production_01_test_01 er051_open233_checker_trial_variant_01_test_01`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_r3_natural_calibration_01.py --rubric r3`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_r3_natural_calibration_01.py --rubric r3prime`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --s1u`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_rewrite_compare_page_01.py`
- `cd /c/Users/tensh/eigo-radio && git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er009_ledger_deviation_recalibration_02_test.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py er052_output/open233_self_recovery_flow_runner_01 er052_output/open233_self_recovery_flow_runner_01_iter2 er052_output/open233_self_recovery_flow_runner_01_iter3 er052_output/open233_self_recovery_stage2_calibration_01 er052_output/open233_self_recovery_stage3_rewrite_trial_01 er052_output/open233_self_recovery_s1u_alt_compare_01`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
iteration 4実測完了(許容線の再設計+Stage2 rubric R3+追加測定7項目+
読み比べページ、委任_12、2026-09-30)」を追加。`OPEN_ITEMS.md`OPEN-233
行へ「2026-09-30追記(委任_12、iteration4完了)」を追加しStatus列更新。
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`へ新規§12(iteration4実測)
を追加。`docs/pm/design_open233_self_recovery_flow_01.md`冒頭Status・
§4-9[新設]・§7-0-iter4[新設]・§8-5[新設]・§9-1⑨[新設]・§13[追記]
を更新。`CURRENT_SPEC.md`は変更しない(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、`DECISION_LOG.md`、
`OPEN_ITEMS.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_flow_runner_01.py`、
`er052_open233_self_recovery_flow_runner_01_test_01.py`、
`er052_open233_self_recovery_stage2_calibration_01.py`、
`er052_open233_self_recovery_r3_natural_calibration_01.py`、
`er052_open233_self_recovery_rewrite_compare_page_01.py`、
`er052_output/open233_self_recovery_flow_runner_01_iter4/`、
`er052_output/open233_self_recovery_r3_natural_calibration_01/`、
`user_test/open233_rewrite_compare_01/index.html`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_12.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_12_check.json`
(存在する場合)。コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-
TRIAL-01: iteration 4実測(許容線の再設計・Stage2 rubric R3・追加測定
7項目・読み比べページ、委任_12)"。trailer: `Co-Authored-By: Claude
Sonnet 5 <noreply@anthropic.com>`。ACTIVE_TASK*/RESULT_PACKET*/.envは
add対象外。競合時は`git merge origin/main`のみ(force push/rebase/
resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233P.md`参照(作成できない場合はhandback本文に
含める)。
