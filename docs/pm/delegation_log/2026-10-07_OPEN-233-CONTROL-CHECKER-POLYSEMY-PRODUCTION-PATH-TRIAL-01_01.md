# 2026-10-07 OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_01(SSOT裏取り+実行計画+事前登録+評価準備、¥0)

## 管理ID
Management-ID: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(委任_01)。並行タスクなし。API呼び出し禁止(¥0)、Production変更禁止、SSOT編集禁止、git操作は最後に1回(個別add)。

## ユーザー決定(2026-10-07、原文要旨)
- ベース仕様=「従来版(Control)」: 現行B3(Notes for writerを要約転写で渡す仕様、逐語でなくてよい)+Trial02(META-ALLFACT-NOTE-E2E-TRIAL-02)で試した複数Checker仕様のうちvalidatedとされた構成=`docs/pm/ledger_clarity_p_trial/00a_base_checker_config.md` の「ユーザー確認済みChecker構成」。
- これに多義語Note=META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02で使った「Metaのrollback factに対する固定最小Note」(0/12実績)を加える。他4テーマは多義語Noteなし(Control+Checkerの再確認)。
- 目的: (1) Rollback誤読のN増し(Meta +10本、累積0/22を目標) (2) 本番経路でのネガ(不良率増加・Gate STOP・不要Rewrite・原価)の有無。
- 予算上限¥500、並列4まで。Production経路(run_instance・承認スイッチ不変)で走らせるが公開はしない(OPEN-238 runtime evidenceと同方式)。
- 物差しを固定: 記事評価はB3 rubric(fact単位・盲検・保留区分)、Rollbackは正/曖/誤の3値ラベル、重大判定とRollback判定は人間確認パックを作る。

## 性質・到達上限Status・禁止事項
- 性質: Trial計画(DEV)。本委任では生成を実行しない。到達上限Status=`PLAN_READY`(Fable照合後に実行委任)。
- 禁止事項: Production変更、Checker仕様の新設・変更、Writer prompt変更、新テーマ追加(既存seedのmeta/hormuz/space_weapons/sewer/ai_controlのみ)、SSOT編集、`git add -A`。
- 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3):
  - E-1: 推測や未実行の想定でPASSと報告しない。実行した検証(dry-run・合成fixture)だけを結果として書く。
  - D-1: 不明・不一致は「要Fable判断」として列挙し、勝手に埋めない。
  - G-1: 本委任はAgent/Subagentを起動しない。無関係な既存差分をstageしない。
  - F-1: 報告は20行以内。詳細は plan_01.md / preregistration_01.md へ。
  - T-0: 本委任文を本ファイルへ保存し `python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`。FAILなら見出し補完し再検証。
  - T-1/T-2/T-3: 該当なし(KPI・Opus指摘関連の委任ではない)。

## 事前指定Read一覧
Grepで該当箇所のみ(全文読込禁止): `docs/pm/ledger_clarity_p_trial/00a_base_checker_config.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §91/§92/§94/§99-5/§100、`er052_output/open233_allfact_note_e2e_02/`(設定・provenance・cost.jsonのみ)、`er052_output/open238_precheck_fix_trial_01/runtime_evidence/{provenance.json,approved_switches_dump.json}`、META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02出力(`er052_output/open233_meta_rollback_minimal_note_01/`)の固定Note本文・台帳差込位置、`docs/pm/b3_trial_01/eval_rubric.md`、`er052_output/open233_b3_trial_01/eval/eval_pack_stage2/README_EVALUATOR.md`、`docs/pm/b3_trial_01/make_eval_pack.py`、`er052_output/open233_ng_root_cause_01/tools/make_rca_pack.py`、`er052_output/open233_b3_trial_01/tools/driver_stage2.py`。

## 事前指定Grep一覧と追記・更新位置の手順
- `CURRENT_SPEC.md` を「Notes for writer」「要約」「逐語」「notes」でGrepし、現行B3のnotes転写方式(要約/逐語)を事実として特定。
- 更新位置: `docs/pm/ACTIVE_TASK.md` の固定ヘッダ(管理ID追加=PLAN_READY)+本文末尾1行。`docs/pm/RESULT_PACKET.md` は上書き。

## 作業
1. 裏取り(事実のみ、出典付き): (a) E2E_02の従来版Controlの正確な構成(B3 notes転写方式、Writer経路、Checker構成が00aと一致するか、スイッチ一覧、1記事原価)、(b) 固定多義語Noteの本文と差し込み方法、META-ROLLBACK TRIAL-01/02のrunnerと本件Production経路の違い、(c) Production入口(run_instance)でControl+Checker+多義語Noteを通せるか・必要な既存Trialスイッチ、(d) 00aの構成がPRODUCTION_WIRED前であることの確認。不明・不一致は「要Fable判断」として列挙。
2. 実行計画 `docs/pm/control_checker_polysemy_trial_01/plan_01.md`(run構成表18本、スイッチ、並列4・guard、費用・時間見積、出力レイアウト、provenance)。
3. 事前登録 `docs/pm/control_checker_polysemy_trial_01/preregistration_01.md`(主要指標①②、副次③〜⑦、合否規則、人間確認が必要な件の定義)。
4. 評価準備: `tools/make_eval_pack_ccp.py`、Rollback 3値ラベルテンプレ、人間確認パックテンプレ。評価者割当は3本(18記事、テーマ混在・seed固定)。
5. `docs/pm/ACTIVE_TASK.md` 固定ヘッダ更新、`docs/pm/RESULT_PACKET.md` 上書き(12行以内)。
6. Git: 個別add(`docs/pm/control_checker_polysemy_trial_01/*`、tools、delegation_log本件)。commit「OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01: 計画・SSOT裏取り・事前登録・評価準備(¥0、Production変更なし)」+ trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。push origin main。

## 実行コマンド全文
- ¥0確認: `python`(runnerの承認スイッチ比較dry-run)、`python er052_open233_polysemy_nb_dev_01.py --phase phase1 ... --dry-run`(meta nb / hormuz control)、`python docs/pm/control_checker_polysemy_trial_01/tools/make_eval_pack_ccp.py --runs-root <合成fixture> --eval-root <scratch>`。有料API実行コマンドは本委任では実行しない(plan_01.md 5節に実行委任用の要旨を記載)。
- 本件T-0検証: `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-07_OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-10-07_OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01_01_check.json`

## SSOT追記文
なし(SSOT編集禁止。REPORT/DECISION_LOG/OPEN_ITEMSへの反映は実行・評価完了後の別委任)。

## Git
個別addのみ(`git add -A`禁止)。対象: `docs/pm/control_checker_polysemy_trial_01/`配下、本delegation_logとcheck.json、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET.md`。commit message末尾 trailer: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。push origin main。

## 報告
20行以内: 裏取り結果(a)〜(d)と「要Fable判断」一覧、run構成表、費用・時間見積、事前登録の主要指標と合否規則、評価準備の所在、実行委任に渡すべきコマンド要旨、commit hash・push結果、check結果、raw URL(plan_01.md、preregistration_01.md)。RESULT_PACKET項目は12行以内の要約。
