# 委任_01a-2(簡略保存、T-0簡略版: 逐語ではなく要約。Fable指示により長文逐語Writeが安全分類器で停止したため簡略化)

## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_01a-2: P' DEVスクリプト実装+unit test+Checker DEVラッパ+手順書、Phase 1準備、費用0円)。

## 性質/到達上限Status/禁止事項
DEV実装(新規ファイルのみ)+test。到達上限は実装・test PASS報告で、有料実行はしない。
禁止: 既存Production file(er003 vfl01/er012/er019/er052 runner/e2e_run_02.py)の変更、有料API、SSOT編集、git。
tools/*(既存)と00d_eval_template.mdには触らない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1は該当なし(0円)。T-0は本ファイルの簡略保存、checkerは実行しFAILでも続行。
T-2/T-2追記(7-5)はTTSなし、T-3は対象外。

## ユーザー指示(原文、要点)
P'=Researcherの構造化・記述部分の改善。Research方法不変、原資料にないFact追加禁止、台帳生成処理(決定論)不変。
上限100円。Opus条件A判定(B)の必須修正M-a/M-b/M-cを反映。

## 事前指定Read一覧
00b_pprime_design.md、vfl01のbuild_researcher_prompt/build_verification_prompt、er019の引数定義部と再利用判定部(L92-97, L338, L360)、
e2e_run_02.pyのprepare_instances()とrunner.OUT_DIR/BUDGET_STATE_PATH上書き部、Before researcher_full_record.json。

## 事前指定Grep一覧+追記位置・更新位置の手順
(1) 新規er052_open233_ledger_clarity_pprime_dev_01.py: env OPEN233_RESEARCHER_VARIANT、contextmanagerでvfl01の2関数のみ差替え・復元、追記ブロック(Researcher10規則/Verification3観点)、provenance、out_dir不在確認、台帳段gate40円。
(2) unit test test_pprime_dev_01.py(a〜f、API非呼出)。(3) Checker DEVラッパ tools/run_checker_after_p01.py(新規、実行しない)。
(4) 手順書 docs/pm/ledger_clarity_p_trial/01a_run_procedure.md(40行以内)。(5) ACTIVE_TASK.mdの3行更新(上限100円/Opus(B)M-a〜M-e反映/現工程)。

## 実行コマンド全文
pytest test_pprime_dev_01.py -q / Production file 5本のgit status --porcelain(空であること) / check_delegation_prompt.py(本ファイル、json-out=..._01a_check.json)。

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目、10行以内)
(1)作成ファイル・行数 (2)test件数とPASS/FAIL (3)Production無変更確認 (4)台帳段/全連鎖/Checkerの各コマンド全文 (5)見込み費用 (6)T-0結果 (7)未解決・懸念。
