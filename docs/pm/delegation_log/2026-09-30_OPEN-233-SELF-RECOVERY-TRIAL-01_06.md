管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_06: 棚卸し結果の設計統合[§5三分類]+棚卸し文書commit+deterministic pre-checkのTrial実装、Phase 1①pre-check FP率[¥0]②hormuz見逃し3attempt補完実験[少額])
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 性質(到達上限Status・禁止事項)
到達上限Status: `PHASE1_STEP2_DONE`(USER_DECISION_REQUIREDには該当
しない)。禁止事項: 削除・移動・rm・git clean・git stash・rebase/
reset/amend/force push禁止。`docs/pm/ACTIVE_TASK_C233I〜J.md`/
`RESULT_PACKET_C233I〜J.md`はcommit対象外。`git add -A`禁止(パス指定
add)。Production正式path(既存の量産経路)への無断実装禁止(E-1/E-2/
J-1/J-2はいずれも両論併記のみでProduction配線しない)。

## 1. 事前指定Read一覧
`docs/pm/design_open233_self_recovery_flow_01.md`(委任_04改訂版、
§5-1〜§5-4/§9-0/§9-1/§15)、`docs/pm/inventory_local_rewrite_
mechanisms_open233_01.md`(委任_05、未commit)、
`docs/pm/RESULT_PACKET_C233H.md`/`RESULT_PACKET_C233I.md`、
`er010_ledger_local_rewrite_09.py`(読むのみ)、
`er003_v1_n3_01_scaffold_generate.py::split_family_x_article_
text_v2`(読むのみ)、`er051_open233_checker_trial_variant_01.py`、
`er051_output/open233_checker_trial_01/trial_03_stability_n20/`
(hormuz V4A非検出3attemptのraw)、`docs/pm/negative_claim_candidates_
open233_01.md`、`er003_v1_en_direct_vfl_01_generate.py`(Ledger schema
確定用)、`er050_gpt6_checker_comparison_trial_01.py`(fixture再利用)。

## 2. 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: design書内`^## 14`/`^## 15`/`^## 13`(見出し位置確認)、
  `er019_output/**/deviation_checks/*.json`(LEDGER_COMPLIANT 28件抽出)、
  `step1_fixtures\(\)`/`step2_fixtures\(\)`/`step3_fixtures\(\)`
  (`er050_gpt6_checker_comparison_trial_01.py`内定義箇所)。
- 追記位置: `docs/pm/design_open233_self_recovery_flow_01.md`冒頭Status
  行、§5内(新設§5-0を§5-1直前へ、§5-2-補を§5-3直前へ、§5-4-補+§5-5を
  §6直前へ)、§9-1①②本文(実測結果追記)、§9-1費用見積り末尾(実測反映)。
  `OPEN_ITEMS.md`OPEN-233行(既存の最後の追記文の直後、Status列直前)。
  `DECISION_LOG.md`末尾(新規`## OPEN-233-SELF-RECOVERY-TRIAL-01: 既存
  Rewrite機構棚卸し統合...`見出しで新規エントリ追加)。
  `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`末尾(新規§5追加)。

## 3. 実行内容
(a) 設計書§5-0(既存Rewrite関連機構18件の三分類表、KPI/QCD理由付き)を
新設し、EN局所Rewriteを既存ベース案(E-1、er010拡張)と新方式案(E-2、
delete型決定論処理+replace/narrow_scope型最小Prompt)の両論併記
(§5-2/§5-2-補)、JA局所Rewriteを既存ベース案(J-1、er010骨格の日本語
移植)と代替案(J-2、既存JA must-fix全文+局所指示)の両論併記
(§5-4/§5-4-補)へ再構成し、継承guard/retry/再検証を§5-5へ統合した。
(b) 新規`er052_open233_self_recovery_precheck_01.py`(+test)で
deterministic pre-checkをTrial実装(Ledger text構造化フィールドと記事
本文の機械照合、FPを出しにくい正規化・除外ロジック)。unittest 23件
全PASS。(c) Phase 1①: 既存LEDGER_COMPLIANT記事28件中20件(8件は
JA retry版promptで既存逆展開ツール非対応のため対象外)へprecheck適用、
記事単位FP率0/20=0%。Safety群12件で単独検出率1/12(8.3%)。design書
§3-1の判断基準(FP率10%超で弱め分岐)に該当せずfloor扱いを維持。
(d) Phase 1②: hormuz_run03_standard/V4A非検出3attempt(8/13/14)を
特定し、precheck適用(非検出、既知の限界どおり)+新規`er052_open233_
self_recovery_stage2_01.py`によるStage1出力なし独立Stage2診断(gpt-6-
luna、3 call、¥0.6285)を適用し3/3(100%)がHF-009 changed_scopeを
`BLOCKING`として独立検出したことを実測した。(e) SSOT更新(DECISION_LOG/
OPEN_ITEMS/REPORT)、delegation_log本体作成、`python -m unittest`全
PASS確認、`git diff --stat`でProductionファイル無変更を確認。

## 4. 実行コマンド全文
- `./.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_precheck_01_test_01 -v`
- `./.venv/Scripts/python.exe er052_open233_self_recovery_precheck_phase1_measure_01.py`
- `./.venv/Scripts/python.exe er052_open233_self_recovery_phase1_hormuz_followup_01.py`
- `git diff --stat -- er003_v1_en_direct_vfl_01_generate.py er006_model_routing_contract_01.py er010_ledger_local_rewrite_09.py er012_e_family_entertainment_two_level_runner_01.py er019_family_x_ja_writer_o_r1_r2_01.py`

## 5. SSOT追記文
`DECISION_LOG.md`末尾へ新規エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01:
既存Rewrite機構棚卸し統合(§5三分類)+deterministic pre-check Trial
実装+Phase1①②実測(委任_05/_06、2026-09-30)」を追加(ユーザー逐語要旨
+委任_05棚卸し概要+委任_06三分類統合+precheck実装+Phase1①②実測結果+
費用+USER_DECISION_REQUIRED該当有無+Production安全性確認)。
`OPEN_ITEMS.md`OPEN-233行へ既存最終追記文の直後に「2026-09-30追記
(委任_06、既存Rewrite機構棚卸し統合+deterministic pre-check Trial
実装+Phase1①②実測完了)」を追加しStatus列を`PHASE1_STEP2_DONE`へ更新。
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`へ新規§5を追加。
`CURRENT_SPEC.md`は変更しない(Production配線なしのため)。

## 6. Git(明示add対象・コミットメッセージ・trailer)
明示add対象(パス指定、`git add -A`は使用しない):
`docs/pm/design_open233_self_recovery_flow_01.md`、
`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`、
`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、
`er052_open233_self_recovery_precheck_01.py`、
`er052_open233_self_recovery_precheck_01_test_01.py`、
`er052_open233_self_recovery_precheck_phase1_measure_01.py`、
`er052_open233_self_recovery_stage2_01.py`、
`er052_open233_self_recovery_phase1_hormuz_followup_01.py`、
`er052_output/open233_self_recovery_precheck_01/`、
`er052_output/open233_self_recovery_phase1_hormuz_followup_01/`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_05.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_05_check.json`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_06.md`、
`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_06_check.json`。
コミットメッセージ(想定): "OPEN-233-SELF-RECOVERY-TRIAL-01: 既存
Rewrite機構棚卸し統合(§5三分類)+deterministic pre-check実装+Phase1
①②実測(委任_05/_06)"。trailer:
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
ACTIVE_TASK*/RESULT_PACKET*/.envはadd対象外。競合時は`git merge
origin/main`のみ(force push/rebase/resetは使わない)。

## 7. 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_C233J.md`参照。
