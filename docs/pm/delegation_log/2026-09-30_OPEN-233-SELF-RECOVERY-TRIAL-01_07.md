管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_07: Phase 1 ③ Stage 1 variantの実測確定[V0/V4-A/独立materiality判定S1-D]+④ Stage 2実単価・batch化・prompt caching実測)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `PHASE1_STEP4_DONE`(USER_DECISION_REQUIREDには該当
しない)。禁止事項: 削除・移動・rm・git clean・git stash・rebase/
reset/amend/force push禁止。`docs/pm/ACTIVE_TASK_C233K.md`/
`RESULT_PACKET_C233K.md`はcommit対象外。`git add -A`禁止(パス指定
add)。Production正式path(既存の量産経路)への無断実装禁止(S1-Dは
Trial実装のみでProduction配線しない、Stage2較正リスクの発見も
rubric文言を勝手に変更せず報告のみ行う)。

## 1. 事前指定Read一覧
`docs/pm/design_open233_self_recovery_flow_01.md`(§9-1/§13/§14全体)、
`docs/pm/negative_claim_candidates_open233_01.md`、
`er051_open233_checker_trial_variant_01.py`、
`er052_open233_self_recovery_stage2_01.py`、
`er052_open233_self_recovery_precheck_01.py`、
`er050_gpt6_checker_comparison_trial_01.py`(fixture再利用)、
`er051_open233_checker_trial_02_run.py`(harness pattern参照)、
`er003_v1_en_direct_vfl_01_generate.py`(DEVIATION_FLAG_KEYS等、
read-only参照)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§5、
`docs/pm/RESULT_PACKET_C233J.md`。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `step1_fixtures\(\)`/`step2_fixtures\(\)`/`step3_
  fixtures\(\)`/`filter_fixtures_by_id`(`er050_gpt6_checker_
  comparison_trial_01.py`内定義箇所)、`^## 14`/`^### 14-2`/`^### 13-4`
  (design書見出し位置確認)、`OPEN-233`(`OPEN_ITEMS.md`該当行特定)。
- 追記位置: `docs/pm/design_open233_self_recovery_flow_01.md`冒頭
  Status行、§4内(新設§4-7を§5直前へ)、§9-1③④本文(実測結果で
  置換)、§9-1費用見積り末尾([委任_07実測]行追加)、§13-4末尾
  (実単価確定の追記)、§14内(新設§14-5を§15直前へ)。`OPEN_ITEMS.md`
  OPEN-233行(既存の最後の追記文の直後、Status列を`PHASE1_STEP4_DONE`
  へ更新)。`DECISION_LOG.md`末尾(新規`## OPEN-233-SELF-RECOVERY-
  TRIAL-01: Phase 1 ③④実測+Stage 1最終確定...`見出しで新規エントリ
  追加)。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`末尾(新規§6
  追加)。

## 3. 実行内容
(a) 新規`er052_open233_self_recovery_s1d_trial_01.py`(+test、11件
PASS)でS1-D(検出+materiality一体型、10 flags+materiality+basis+
rewrite_kind出力、explanationなし)をTrial実装。(b) 新規`er052_
open233_self_recovery_phase1_step3_stage1_compare_01.py`でV0/V4-A/
S1-D比較harness(a)〜(e)5作業を実装・実行(76 call、¥13.5234、
0 error)。既存V0/V4-A出力(er050_output/er051_output)を最大限
再利用し新規callをS1-D分+n=15追加分に限定。(c) 新規`er052_open233_
self_recovery_stage2_production_01.py`(+test、8件PASS)で§4-4確定
入力どおりのper-claim/batch Stage2実装(段落±1抽出+引用符正規化を
追加改善)。(d) 新規`er052_open233_self_recovery_phase1_step4_stage2_
unitcost_01.py`でper-claim vs batch(9 call)+prompt caching(4 call)
実測(計12 call、¥1.1364、0 error)。(e) 実測結果に基づきStage 1を
V4-A確定(S1-D不採用)、Stage2較正リスク(Real-but-fixable群の
QUALITY誤降格)を新規発見・報告。(f) SSOT更新(design書§4-7/§9-1/
§13-4/§14-5、DECISION_LOG/OPEN_ITEMS/REPORT§6)、delegation_log本体
作成、`python -m unittest`全PASS確認(新規19件+既存回帰51件=70件)、
`git diff --stat`でProductionファイル無変更を確認。

## 4. 実行コマンド全文
- `./.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_s1d_trial_01_test_01 er052_open233_self_recovery_stage2_production_01_test_01 -v`
- `./.venv/Scripts/python.exe er052_open233_self_recovery_phase1_step3_stage1_compare_01.py --tasks a,b,c,d,e`
- `./.venv/Scripts/python.exe er052_open233_self_recovery_phase1_step4_stage2_unitcost_01.py --tasks unitcost,caching`
- `git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
Phase 1 ③④実測+Stage 1最終確定(V4-A確定・S1-D不採用、委任_07、
2026-09-30)」を追加(実測結果・Stage1最終確定根拠・Stage2較正リスク
発見・費用・USER_DECISION_REQUIRED該当有無・Production安全性確認)。
`OPEN_ITEMS.md`OPEN-233行へ既存最終追記文の直後に「2026-09-30追記
(委任_07、Phase 1 ③④実測+Stage 1最終確定)」を追加しStatus列を
`PHASE1_STEP4_DONE`へ更新。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`
へ新規§6を追加。`docs/pm/design_open233_self_recovery_flow_01.md`
冒頭Status・§4-7[新設]・§9-1③④・§13-4・§14-5[新設]を追記。
`CURRENT_SPEC.md`は変更しない(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、
`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_s1d_trial_01.py`、
`er052_open233_self_recovery_s1d_trial_01_test_01.py`、
`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`、
`er052_open233_self_recovery_stage2_production_01.py`、
`er052_open233_self_recovery_stage2_production_01_test_01.py`、
`er052_open233_self_recovery_phase1_step4_stage2_unitcost_01.py`、
`er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/`、
`er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_07.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_07_check.json`。
コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01: Phase 1
③④実測+Stage 1最終確定(V4-A確定・S1-D不採用、委任_07)"。trailer:
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
ACTIVE_TASK*/RESULT_PACKET*/.envはadd対象外。競合時は`git merge
origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233K.md`参照。
