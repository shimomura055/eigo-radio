管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_10: iteration 2=
rewrite_hint実装+J-1ロケータ改善+negative群R2再較正+Stage1 recall
対策variant実測+統合dry-run再実行)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `ITER2_DONE_TARGET_MET`(USER_DECISION_REQUIREDには
該当しない、7条件いずれも非該当)。禁止事項: 削除・移動・rm・git
clean・git stash・rebase/reset/amend/force push禁止。
`docs/pm/ACTIVE_TASK_C233N.md`/`RESULT_PACKET_C233N.md`はcommit対象外。
`git add -A`禁止(パス指定add)。Production正式path(既存の量産経路)への
無断実装禁止(iteration2もTrial実装のみでProduction配線しない)。既存
委任_08/_09の証跡ファイル(`budget_state_c233l_*.json`/
`er052_output/open233_self_recovery_flow_runner_01/`)は変更しない。

## 1. 事前指定Read一覧
`docs/pm/RESULT_PACKET_C233M.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_
REPORT.md`§8、`docs/pm/design_open233_self_recovery_flow_01.md`
§9-1⑥/§9-2(改善優先順位)、`er052_open233_self_recovery_flow_runner_
01.py`(+test)、`er052_output/open233_self_recovery_flow_runner_01/`
(29 instanceの結果・Stage4到達理由)、`er052_open233_self_recovery_
stage2_production_01.py`、`er052_open233_self_recovery_stage2_
calibration_01.py`、`er052_open233_self_recovery_stage3_rewrite_
trial_01.py`、`er052_open233_self_recovery_s1d_trial_01.py`、
`er010_ledger_local_rewrite_09.py`(`locate_target_sentence`、
read-only)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `_ITEM_PROPS`/`PER_CLAIM_JSON_SCHEMA`/`BATCH_JSON_SCHEMA`
  (`er052_open233_self_recovery_stage2_production_01.py`)、
  `RUBRIC_R2`/`run_stage2_batch_variant`(`er052_open233_self_
  recovery_stage2_calibration_01.py`)、`locate_best_sentence`/
  `claim_identity`/`single_text_rewrite`/`paired_rewrite`/
  `run_instance`(`er052_open233_self_recovery_flow_runner_01.py`)、
  `run_s1d_check`(`er052_open233_self_recovery_s1d_trial_01.py`)、
  `locate_target_sentence`/`split_sentences`(`er010_ledger_local_
  rewrite_09.py`)。
- 追記位置: `docs/pm/design_open233_self_recovery_flow_01.md`冒頭
  Status行、§3-1(S1-U variant新設)、§4-5(rewrite_hint実装反映)、
  §4-8(R2'較正・不採用)、§5-4(J-1ロケータ改善)、§9-1⑦(iteration2新設)、
  §9-2(改善優先順位1〜4の対応状況追記)、§13-11直後(worst case実測
  更新)。`OPEN_ITEMS.md`OPEN-233行(既存最終追記文の直後に追記、
  Status列更新)。`DECISION_LOG.md`末尾(新規エントリ追加)。
  `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`末尾(新規§9追加)。

## 3. 実行内容
(a) `er052_open233_self_recovery_stage2_production_01.py`の
Stage2出力schemaへ`rewrite_hint`(BLOCKING時必須、逐語引用+修正指示+
fact_id)を追加(`REWRITE_HINT_INSTRUCTION`、PER_CLAIM/BATCH双方の
schema・prompt template更新)。既存regression test 2件追加、
`er052_open233_self_recovery_stage2_calibration_01.py::run_stage2_
batch_variant`も同時対応。
(b) `er052_open233_self_recovery_flow_runner_01.py`へclaim identity
正規化(`normalize_claim_text`)、rewrite_hint引用抽出
(`extract_quoted_fragment`)、統合ロケータ(`locate_target`、
rewrite_hint引用→locate_best_sentence[ambiguous時は全文フォール
バックへ]→er010.locate_target_sentence)、JA側位置比マッピング
(`locate_ja_counterpart_by_position`、数値トークン一致優先)、
delete型のfuzzy再出現確認、S1-U variant(`stage1_union_screen`、
CLI `--s1u`、`s1u_eligible`instanceのみ)を実装。新規regression test
19件追加(既存含め131件PASS)。
(c) 新規`er052_open233_self_recovery_r2prime_recalibration_01.py`
(作業B): B1/B3/B4/A2A3/A4/A5+negative実claim4件(委任_09統合dry-run
instance jsonから抽出した実際のclaim_text)を対象に、段階的判定手順+
例示追加のRUBRIC_R2_PRIME(n=2)を実測(20 call・¥3.3977)。Safety側
誤降格1件(A4-0)+Productivity改善0件のため不採用と判定。
(d) OUT_DIRを`er052_output/open233_self_recovery_flow_runner_01_
iter2/`(既存委任_09の`_flow_runner_01/`とは別ディレクトリ)へ変更し、
Guardrail¥35で29 instanceを`--s1u`有効で再実行(126 call・¥26.0302、
0 error)。全群(negative→b_group/meta/hormuz→safety)を3回のコマンド
実行に分割し、`--resume`で既存キャッシュ結果を再利用(重複課金防止)。
(e) 実測結果を分析し、S1-U variantが委任_09の3件の重大recall miss
(B2_hormuz・B3・hormuz_run02_advanced)を全件捕捉しRewriteで解消した
ことを確認(hormuz_run02_advancedはcycle1で`LEDGER_COMPLIANT`かつ
`all_prior_issues_resolved=True`)。J-1 locate成功率36.4%→81.8%、
claim単位Rewrite成功率60.6%→81.0%、Escalation9→7件を実測。副作用
(meta_run03_advancedが新規Escalation)を報告。
(f) SSOT更新(design書§3-1/§4-5/§4-8/§5-4/§9-1⑦/§9-2/§13-11/冒頭
Status、DECISION_LOG/OPEN_ITEMS/REPORT§9)、delegation_log本体作成、
`python -m unittest discover`131件PASS確認、`git diff --stat`で
Productionファイル・既存委任_08/_09 Trial証跡ファイル無変更を確認。

## 4. 実行コマンド全文
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m py_compile er052_open233_self_recovery_flow_runner_01.py er052_open233_self_recovery_flow_runner_01_test_01.py er052_open233_self_recovery_stage2_production_01.py er052_open233_self_recovery_stage2_calibration_01.py er052_open233_self_recovery_r2prime_recalibration_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest discover -p "er05*test*.py"`
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_r2prime_recalibration_01.py`
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --groups negative --s1u`
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --groups b_group,meta,hormuz --s1u --resume`
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --groups safety --s1u --resume`
- `cd /c/Users/tensh/eigo-radio && git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er009_ledger_deviation_recalibration_02_test.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py er052_output/open233_self_recovery_flow_runner_01 er052_output/open233_self_recovery_stage2_calibration_01 er052_output/open233_self_recovery_stage3_rewrite_trial_01`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
iteration 2実測完了(rewrite_hint実装+J-1ロケータ改善+negative群R2
再較正+S1-U variant実測、委任_10、2026-09-30)」を追加。`OPEN_ITEMS.md`
OPEN-233行へ既存最終追記文の直後に「2026-09-30追記(委任_10、
iteration 2完了)」を追加しStatus列を`ITER2_DONE_TARGET_MET`へ更新。
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`へ新規§9を追加。
`docs/pm/design_open233_self_recovery_flow_01.md`冒頭Status・
§3-1[S1-U新設]・§4-5[rewrite_hint実装反映]・§4-8[R2'不採用]・
§5-4[J-1改善]・§9-1⑦[iteration2新設]・§9-2[改善優先順位対応状況]・
§13-11直後[worst case実測更新]を更新。`CURRENT_SPEC.md`は変更しない
(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、
`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_stage2_production_01.py`、
`er052_open233_self_recovery_stage2_production_01_test_01.py`、
`er052_open233_self_recovery_stage2_calibration_01.py`、
`er052_open233_self_recovery_flow_runner_01.py`、
`er052_open233_self_recovery_flow_runner_01_test_01.py`、
`er052_open233_self_recovery_r2prime_recalibration_01.py`、
`er052_output/open233_self_recovery_flow_runner_01_iter2/`、
`er052_output/open233_self_recovery_r2prime_recalibration_01/`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_10.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_10_check.json`。
コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01: iteration 2
実測(rewrite_hint実装+J-1改善+S1-U variantで重大recall miss3件解消、
委任_10)"。trailer: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
ACTIVE_TASK*/RESULT_PACKET*/.envはadd対象外。競合時は`git merge
origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233N.md`参照。
