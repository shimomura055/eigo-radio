管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_11: Opus L2 #2所見の
逐語保存+iteration 3=バグ修正・停止判定是正・段落単位Rewrite・測定
是正・Rewrite由来逸脱検出・S1-U安価代替比較・29 instance再実行)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `ITER3_DONE_TARGET_MET`または`ITER3_DONE_
IMPROVEMENT_NEEDED`(USER_DECISION_REQUIRED該当有無は§9-1⑧参照)。
禁止事項: 削除・移動・rm・git clean・git stash・rebase/reset/amend/
force push禁止。`docs/pm/ACTIVE_TASK_C233O.md`/`RESULT_PACKET_C233O.md`
はcommit対象外。`git add -A`禁止(パス指定add)。Production正式path
(既存の量産経路)への無断実装禁止(iteration3もTrial実装のみでProduction
配線しない)。既存iteration1(`er052_output/open233_self_recovery_
flow_runner_01/`)・iteration2(`er052_output/open233_self_recovery_
flow_runner_01_iter2/`)・委任_08証跡ファイルは変更しない。

## 1. 事前指定Read一覧
`docs/pm/RESULT_PACKET_C233N.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_
REPORT.md`§9、`docs/pm/design_open233_self_recovery_flow_01.md`
§3-1/§3-3/§4/§5-4/§5-5/§9-1⑦/§13、`er052_open233_self_recovery_
flow_runner_01.py`(+test)、`er052_output/open233_self_recovery_
flow_runner_01_iter2/instances/*.json`(Stage4到達7件+未検査5件)、
`er052_open233_self_recovery_s1d_trial_01.py`、`er003_ja_to_en_
translation.py`(翻訳忠実性QA資産)、`er052_open233_self_recovery_
precheck_01.py`。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `claim_identity`/`locate_target`/`paired_rewrite`/
  `single_text_rewrite`/`run_instance`/`aggregate_measurements`
  (`er052_open233_self_recovery_flow_runner_01.py`)、
  `split_family_x_article_text_v2`(構造Gate参照)、
  `build_fidelity_qa_prompt`/`FIDELITY_QA_JSON_SCHEMA`/
  `parse_and_validate_fidelity_qa_output`(`er003_ja_to_en_
  translation.py`、read-only借用)、`run_precheck`
  (`er052_open233_self_recovery_precheck_01.py`)。
- 追記位置: `docs/pm/opus_l2_review_open233_self_recovery_02.md`
  (新規作成、Opus L2 #2逐語保存)。`docs/pm/design_open233_self_
  recovery_flow_01.md`冒頭Status、§9-1⑧(iteration3新設)、
  §16(Opus L2レビュー#2への対応、新設)。`OPEN-233-SELF-RECOVERY-
  TRIAL-01_REPORT.md`§10(Opus L2 #2と報告訂正)・§11(iteration3)を
  新規追加。`OPEN_ITEMS.md`OPEN-233行へ追記。`DECISION_LOG.md`末尾へ
  新規エントリ追加。

## 3. 実行内容
(a) `docs/pm/opus_l2_review_open233_self_recovery_02.md`を新規作成し、
Opus L2レビュー#2全文を逐語保存(¥0)。
(b) `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§10で委任_10報告の
訂正2点(meta_run03_advancedのStage4はS1-U由来ではなくV4-A本体の
run間変動/誤PASS候補0はRESOLVED_REWRITE限定でRESOLVED_REWRITE_THEN_
DOWNGRADE5 instanceが未検査だった)を記録。
(c) `er052_open233_self_recovery_flow_runner_01.py`へ以下を実装:
  (1) `paired_rewrite`のバグ修正2件(`j1_pair_not_located`を全文
  fallbackへ配線/JA全文fallback後にEN側も必ず1 call編集)。
  (2) `find_matching_prior_record`による停止判定是正(fact_id+正規化
  claim本文近似一致、別claimはblocking件数厳密減少条件でcycle3を
  1回だけ許可、`HARD_MAX_CYCLES=3`)。
  (3) `locate_paragraph_block`+`E2_PARAGRAPH_PROMPT_TEMPLATE`/
  `J1_PARAGRAPH_PROMPT_TEMPLATE`による段落単位Rewriteへの拡張
  (見出し/タイトル行を含む)。
  (4) `aggregate_measurements`の測定是正(`RESOLVED_*`全体への分母
  拡張、群別Escalation率`group_escalation_rates`、実run6 instance
  限定`real_run`、記事単位`article_level`、`s1u_additional_block`
  への改名+正解ラベル真偽列)。
  (5) `run_ja_en_equivalence_check`(既存Production翻訳忠実性QA資産
  read-only借用)+`detect_rewrite_new_precheck_findings`(決定論
  precheck再実行)によるRewrite由来新規逸脱検出。
  (6) `en_ambiguous`自己矛盾応答時の追加1 call再確認
  (`_recheck_confirm`、解消未確認ならfail-closedで`unconfirmed_
  after_reverify`)。
新規regression test 19件追加(既存含め55件PASS)。
(d) iter2の未検査5 instance(`safety_er009_unsupported_new_claim`/
`hormuz_run01_advanced`/`hormuz_run03_standard`/`neg2_meta_refresh_
a2`/`neg3_hormuz_prodrunner_b1b`)を既存json読み直しのみで遡及監査
(¥0、iter2出力は無変更)。
(e) 新規`er052_open233_self_recovery_s1u_alt_compare_01.py`(作業C)
で、iter2でS1-U適用済みの7 instance対象に2×V4-A union/S1-D effort=
medium/lowを実測比較(21 call・¥5.136、Guardrail¥5)。
(f) OUT_DIRを`er052_output/open233_self_recovery_flow_runner_01_
iter3/`(既存iter1/iter2とは別ディレクトリ)へ変更し、`--s1u`有効で
29 instance再実行(作業D)。実行中に実run6 instanceのうち
stage1_mode="fresh"の3件(hormuz_run01_advanced/hormuz_run02_
advanced/meta_run03_advanced)がn=1のみで、委任文の明示要求
「実run6 instanceはn=2で実行」を満たしていないことを自ら発見した
ため、新規`er052_open233_self_recovery_flow_runner_01_n2_realrun_01.py`
を追加作成し、同一budget_stateを共有した状態で当該3件を`_n2`として
追加実行した(23 call・¥5.8944、累計¥42.8526、¥45 Guardrail内)。
(g) SSOT更新・delegation_log作成・`python -m unittest discover`
全PASS確認・`git diff --stat`でProductionファイル・既存iter1/iter2
証跡無変更を確認。

## 4. 実行コマンド全文
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m py_compile er052_open233_self_recovery_flow_runner_01.py er052_open233_self_recovery_flow_runner_01_test_01.py er052_open233_self_recovery_s1u_alt_compare_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01 er052_open233_self_recovery_precheck_01_test_01 er052_open233_self_recovery_s1d_trial_01_test_01 er052_open233_self_recovery_stage2_production_01_test_01 er051_open233_checker_trial_variant_01_test_01`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_s1u_alt_compare_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01.py --s1u`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe er052_open233_self_recovery_flow_runner_01_n2_realrun_01.py`
- `cd /c/Users/tensh/eigo-radio && git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er009_ledger_deviation_recalibration_02_test.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py er052_output/open233_self_recovery_flow_runner_01 er052_output/open233_self_recovery_flow_runner_01_iter2 er052_output/open233_self_recovery_stage2_calibration_01 er052_output/open233_self_recovery_stage3_rewrite_trial_01`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
iteration 3実測完了(Opus L2 #2バグ修正+停止判定是正+段落単位Rewrite+
測定是正、委任_11、2026-09-30)」を追加。`OPEN_ITEMS.md`OPEN-233行へ
「2026-09-30追記(委任_11、iteration 3完了)」を追加しStatus列更新。
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`へ新規§10(Opus L2 #2と
報告訂正)・§11(iteration3実測)を追加。`docs/pm/design_open233_self_
recovery_flow_01.md`冒頭Status・§9-1⑧[iteration3新設]・§16[Opus L2
レビュー#2への対応、新設]を更新。`CURRENT_SPEC.md`は変更しない
(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/opus_l2_review_open233_self_recovery_02.md`、
`docs/pm/design_open233_self_recovery_flow_01.md`、
`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_flow_runner_01.py`、
`er052_open233_self_recovery_flow_runner_01_test_01.py`、
`er052_open233_self_recovery_s1u_alt_compare_01.py`、
`er052_open233_self_recovery_flow_runner_01_n2_realrun_01.py`、
`er052_output/open233_self_recovery_flow_runner_01_iter3/`、
`er052_output/open233_self_recovery_s1u_alt_compare_01/`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_11.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_11_check.json`。
コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01: iteration 3
実測(Opus L2 #2バグ修正・停止判定是正・段落単位Rewrite・測定是正・
S1-U代替比較、委任_11)"。trailer: `Co-Authored-By: Claude Sonnet 5
<noreply@anthropic.com>`。ACTIVE_TASK*/RESULT_PACKET*/.envはadd対象外。
競合時は`git merge origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233O.md`参照。
