管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_08: Stage 2 rubric 較正
Trial + Phase 1 ⑤ Stage 3 Rewrite 型別成功率実測[E-1 vs E-2、J-1 vs J-2])
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `PHASE1_STEP5_DONE`(USER_DECISION_REQUIREDには該当
しない)。禁止事項: 削除・移動・rm・git clean・git stash・rebase/
reset/amend/force push禁止。`docs/pm/ACTIVE_TASK_C233L.md`/
`RESULT_PACKET_C233L.md`はcommit対象外。`git add -A`禁止(パス指定
add)。Production正式path(既存の量産経路)への無断実装禁止(Stage2
rubric較正・Rewrite採用案[E-2/J-1]はいずれもTrial実装のみでProduction
配線しない)。

## 1. 事前指定Read一覧
`docs/pm/design_open233_self_recovery_flow_01.md`(§4/§5-0〜§5-5/
§7-0/§9-1/§13/§14-5)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§6、
`docs/pm/RESULT_PACKET_C233K.md`、
`er052_open233_self_recovery_stage2_production_01.py`、
`er052_open233_self_recovery_phase1_step4_stage2_unitcost_01.py`、
`er010_ledger_local_rewrite_09.py`、
`er003_v1_n3_01_scaffold_generate.py`(`split_family_x_article_text_v2`、
read-only)、`er019_family_x_ja_writer_o_r1_r2_01.py`(must-fix入口、
read-only)、`er003_v1_en_direct_vfl_01_generate.py`
(`run_deviation_check`/`DEVIATION_FLAG_KEYS`、read-only)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `step1_fixtures\(\)`/`step2_fixtures\(\)`/`step3_
  fixtures\(\)`(`er050_gpt6_checker_comparison_trial_01.py`)、
  `NEGATIVE_SOURCE_FILES`/`load_negative_fixture`(`er052_open233_
  self_recovery_phase1_step3_stage1_compare_01.py`)、`^### 4-7`/
  `^### 5-4-補`/`^### 5-5`/`^### 9-1`/`^### 13-10`(design書見出し位置
  確認)、`OPEN-233`(`OPEN_ITEMS.md`該当行特定)。
- 追記位置: `docs/pm/design_open233_self_recovery_flow_01.md`冒頭
  Status行、§4内(新設§4-8を§5直前へ)、§5-4-補直後(新設§5-4-補2を
  §5-5直前へ)、§9-1⑤本文(実測結果で置換)、§9-1費用見積り末尾
  ([委任_08実測]行追加)、§13-10直後(新設§13-11を§14直前へ)。
  `OPEN_ITEMS.md`OPEN-233行(既存の最後の追記文の直後、Status列を
  `PHASE1_STEP5_DONE`へ更新)。`DECISION_LOG.md`末尾(新規`##
  OPEN-233-SELF-RECOVERY-TRIAL-01: Stage 2 rubric較正+Phase 1 ⑤実測
  ...`見出しで新規エントリ追加)。`OPEN-233-SELF-RECOVERY-TRIAL-01_
  REPORT.md`末尾(新規§7追加)。

## 3. 実行内容
(a) 新規`er052_open233_self_recovery_stage2_calibration_01.py`で
Stage2 rubric較正Trial(R1既存出力再利用/R2較正rubric batch実測/R3
post-hoc floor)を13グループ・23claim・n=2=26 callで実行(¥3.1717、
0 error)。既存fixture(`er050_gpt6_checker_comparison_trial_01`の
step1/step2/step3_fixtures、`er052_open233_self_recovery_phase1_
step3_stage1_compare_01`のNEGATIVE_SOURCE_FILES)を最大限再利用し
新規callをR2のみに限定。Safety群14/14維持・既知miscalib claim
(B1-c/B4-a/B4-d)6/6解消・R3不採用の判断を実測に基づき確定。(b) 新規
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`でPhase 1 ⑤
(delete型baseline/replace型E-1 vs E-2/narrow_scope型J-1 vs J-2)を
18 callで実行(¥3.0363、0 error)。J-1(新規paired local rewrite
実装)がhormuz narrow_scope claimを完全解消、J-2(JA全文regen代替案)は
未解消かつdrift 1件検出。採用案(narrow_scope=J-1、replace=E-2第一
候補)を実測に基づき確定。(c) SSOT更新(design書§4-8/§5-4-補2/§9-1/
§13-11/冒頭Status、DECISION_LOG/OPEN_ITEMS/REPORT§7)、delegation_log
本体作成、`python -m unittest`既存42件PASS確認(regression、新規追加
testなし)、`git diff --stat`でProductionファイル無変更を確認。

## 4. 実行コマンド全文
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_stage2_calibration_01.py --n_runs 2`
- `cd /c/Users/tensh/eigo-radio && set -a; source .env; set +a; .venv/Scripts/python.exe er052_open233_self_recovery_stage3_rewrite_trial_01.py`
- `cd /c/Users/tensh/eigo-radio && .venv/Scripts/python.exe -m unittest er052_open233_self_recovery_s1d_trial_01_test_01 er052_open233_self_recovery_stage2_production_01_test_01 er052_open233_self_recovery_precheck_01_test_01 -v`
- `cd /c/Users/tensh/eigo-radio && git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er009_ledger_deviation_recalibration_02_test.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
Stage 2 rubric較正+Phase 1 ⑤実測(Stage3型別Rewrite成功率、
E-1/E-2/J-1/J-2、委任_08、2026-09-30)」を追加(R1/R2/R3実測結果・
R2確定/R3不採用の根拠・Rewrite型別実測結果・narrow_scope=J-1採用案・
費用・USER_DECISION_REQUIRED該当有無・Production安全性確認)。
`OPEN_ITEMS.md`OPEN-233行へ既存最終追記文の直後に「2026-09-30追記
(委任_08、Stage2 rubric較正Trial+Phase 1 ⑤実測完了)」を追加し
Status列を`PHASE1_STEP5_DONE`へ更新。`OPEN-233-SELF-RECOVERY-TRIAL-01_
REPORT.md`へ新規§7を追加。`docs/pm/design_open233_self_recovery_
flow_01.md`冒頭Status・§4-8[新設]・§5-4-補2[新設]・§9-1⑤・
§13-11[新設]を追記。`CURRENT_SPEC.md`は変更しない(Production配線
なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、
`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_stage2_calibration_01.py`、
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`、
`er052_output/open233_self_recovery_stage2_calibration_01/`、
`er052_output/open233_self_recovery_stage3_rewrite_trial_01/`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_08.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_08_check.json`。
コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01: Stage 2
rubric較正+Phase 1 ⑤実測(narrow_scope=J-1採用、委任_08)"。trailer:
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
ACTIVE_TASK*/RESULT_PACKET*/.envはadd対象外。競合時は`git merge
origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233L.md`参照。
