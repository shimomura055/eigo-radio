管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_09: Phase 1 ⑥ Self-Recovery
Flow 統合 dry-run=最初の実 Trial。Checkpoint B の Evidence 取得)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `PHASE1_DONE_IMPROVEMENT_NEEDED`(USER_DECISION_REQUIRED
には該当しない、7条件いずれも非該当)。禁止事項: 削除・移動・rm・git
clean・git stash・rebase/reset/amend/force push禁止。
`docs/pm/ACTIVE_TASK_C233M.md`/`RESULT_PACKET_C233M.md`はcommit対象外。
`git add -A`禁止(パス指定add)。Production正式path(既存の量産経路)への
無断実装禁止(統合dry-runはTrial実装のみでProduction配線しない)。

## 1. 事前指定Read一覧
`docs/pm/design_open233_self_recovery_flow_01.md`(§3/§4-8/§5-4-補2/§6-1/
§7/§8/§9-0/§9-1/§13)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§7、
`docs/pm/RESULT_PACKET_C233L.md`、`docs/pm/ACTIVE_TASK_C233L.md`、
`er052_open233_self_recovery_precheck_01.py`、
`er052_open233_self_recovery_stage2_production_01.py`、
`er052_open233_self_recovery_stage2_calibration_01.py`、
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`、
`er051_open233_checker_trial_variant_01.py`、
`er050_gpt6_checker_comparison_trial_01.py`、
`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`、
`er003_v1_en_direct_vfl_01_generate.py`(`run_deviation_check`/
`build_prior_issues_instruction`/`PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA`、
read-only)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `step1_fixtures\(\)`/`step2_fixtures\(\)`/`step3_
  fixtures\(\)`/`load_audit_fixture`(`er050_gpt6_checker_comparison_
  trial_01.py`)、`NEGATIVE_SOURCE_FILES`/`load_negative_fixture`
  (`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`)、
  `run_trial_deviation_check`/`build_trial_deviation_item_schema`/
  `classify_parsed_result_trial`(`er051_open233_checker_trial_
  variant_01.py`)、`RUBRIC_R2`/`run_stage2_batch_variant`(`er052_
  open233_self_recovery_stage2_calibration_01.py`)、`simple_llm_
  call`/`J1_DEVELOPER_MSG`/`extract_json_obj`(`er052_open233_self_
  recovery_stage3_rewrite_trial_01.py`)、`⑥ 統合dry-run`/`### 9-2`
  (design書見出し位置確認)、`OPEN-233`(`OPEN_ITEMS.md`該当行特定)。
- 追記位置: `docs/pm/design_open233_self_recovery_flow_01.md`冒頭
  Status行、§9-1⑥本文(実測結果で全面置換)・費用見積り末尾
  ([委任_09実測]行追加)、§9-2直後(改善優先順位を追記)。
  `OPEN_ITEMS.md`OPEN-233行(既存最終追記文の直後に追記、Status列更新)。
  `DECISION_LOG.md`末尾(新規`## OPEN-233-SELF-RECOVERY-TRIAL-01: Phase
  1 ⑥ 統合dry-run実測完了...`見出しで新規エントリ追加)。
  `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`末尾(新規§8追加)。

## 3. 実行内容
(a) 新規`er052_open233_self_recovery_flow_runner_01.py`(+test)を実装:
既存`er052_open233_self_recovery_{precheck,stage2_production,stage2_
calibration,stage3_rewrite_trial}_01.py`と`er051_open233_checker_
trial_variant_01.py`・`er050_gpt6_checker_comparison_trial_01.py`・
`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`を
importし、Stage1(既存V4A出力reuse/新規実行)→precheck floor→Stage2
(R2 rubric、batch、floor適用)→Stage3(claimのorigin+JA/EN pairing有無
でJ-1/E-2汎用実装を選択、guard抵触時は全文最小編集フォールバック)→
Stage1 Recheck(`prior_issues`付き、A1)のcycle上限2ループを実装した。
(b) 対象29 instance(Hormuz run_01/run_02 Advanced・run_03
Advanced/Standard、Meta run_03 Advanced/Standard、B群4、negative候補7、
Safety群12)を実行(92 call、¥16.7806、0 error、Guardrail¥45)。
(c) 実行中に発見した不具合(既存`s3rt.simple_llm_call`をそのまま呼ぶと
そのモジュール自身の`save_budget_state`が委任_08の証跡ファイル
`budget_state_c233l_b.json`を上書きする)を`git diff`で検出し、`git
checkout`で該当ファイルを復元、本runner独自の`simple_llm_call`実装へ
差し替え、再発防止regression testを追加した(判定ロジック自体への
影響なし)。(d) 実測結果を分析し、Stage1(V4A)recall miss(3 instance)・
Stage2出力`rewrite_hint`欠落・J-1汎用対象文特定失敗率63.6%・委任_08
negative群測定(87.5%)がplaceholder文字列に対する無効な測定だった
ことを発見・報告した(いずれも独断で修正せず報告のみ)。(e) SSOT更新
(design書§9-1⑥/§9-2/冒頭Status、DECISION_LOG/OPEN_ITEMS/REPORT§8)、
delegation_log本体作成、`python -m unittest`既存110件PASS確認
(regression、新規17件追加)、`git diff --stat`でProductionファイル・
既存Trial infraファイル無変更を確認。

## 4. 実行コマンド全文
- `cd /c/Users/tensh/eigo-radio && python -m py_compile er052_open233_self_recovery_flow_runner_01.py er052_open233_self_recovery_flow_runner_01_test_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01 -v`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest discover -p "er05*test*.py"`
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --groups safety,b_group,meta,hormuz,negative --resume`
- `cd /c/Users/tensh/eigo-radio && git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er009_ledger_deviation_recalibration_02_test.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py er050_gpt6_checker_comparison_trial_01.py er051_open233_checker_trial_variant_01.py er052_open233_self_recovery_stage2_production_01.py er052_open233_self_recovery_stage2_calibration_01.py er052_open233_self_recovery_stage3_rewrite_trial_01.py er052_open233_self_recovery_precheck_01.py er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`
- `cd /c/Users/tensh/eigo-radio && git checkout -- er052_output/open233_self_recovery_stage3_rewrite_trial_01/budget_state_c233l_b.json`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
Phase 1 ⑥ 統合dry-run実測完了(Self-Recovery Flow最初の実Trial、
negative群測定訂正+recall miss発見、委任_09、2026-09-30)」を追加。
`OPEN_ITEMS.md`OPEN-233行へ既存最終追記文の直後に「2026-09-30追記
(委任_09、Phase 1⑥統合dry-run完了...)」を追加しStatus列を
`PHASE1_DONE_IMPROVEMENT_NEEDED`へ更新。`OPEN-233-SELF-RECOVERY-
TRIAL-01_REPORT.md`へ新規§8を追加。`docs/pm/design_open233_self_
recovery_flow_01.md`冒頭Status・§9-1⑥[実測反映]・§9-2[改善優先順位
追記]を更新。`CURRENT_SPEC.md`は変更しない(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、
`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_flow_runner_01.py`、
`er052_open233_self_recovery_flow_runner_01_test_01.py`、
`er052_output/open233_self_recovery_flow_runner_01/`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_09.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_09_check.json`。
コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01: Phase 1 ⑥
統合dry-run実測(29 instance、negative群測定訂正+recall miss発見、
委任_09)"。trailer: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
ACTIVE_TASK*/RESULT_PACKET*/.envはadd対象外。競合時は`git merge
origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233M.md`参照。
