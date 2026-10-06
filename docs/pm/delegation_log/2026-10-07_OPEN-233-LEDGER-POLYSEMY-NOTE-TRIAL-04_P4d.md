# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04 委任_P4d (簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04(P4d: 5記事Control条件Phase 2、EN生成+Checker DEV run、上限¥45)。
- 性質: Trial実行(有料、Control側のみ)。到達上限: 5 run完了+生成物確認(評価なし)。
- 禁止: N+B側実行/Production変更/SSOT編集/git/E2E state書込/Checkerスイッチ変更。
## 性質/到達上限Status/禁止事項
Trial限定。再実行はtimeout・APIエラー時1回のみ。P4a-2/P4e領域に触らない。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 上限¥45(EN/Checker各--budget 10)。D-1: 実費は runs/cost_control_p2.json。G-1: Trial限定。F-1: fail-closed。T-0: 本ファイル+check。T-2: TTSなし。T-3: 対象外。
## 事前指定Read一覧
phase2_readme.md / er052_open233_polysemy_nb_dev_01.py phase2処理 / control_p1_manifest.json。
## 事前指定Grep一覧+追記位置・更新位置の手順
dry-runでphase2がChecker込みと確認(二重実行しない)。5テーマ並列、ログ runs/_logs/<slug>.p2.log。実行後に生成物・provenance・Checker最終判定・E2E非混入を確認し control_p2_manifest.json へ保存。
## 実行コマンド全文
`.venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --theme <topic> --slug <slug> --ledger-txt <txt> --out-dir <rep1> --phase phase2 --yes-run-paid`(環境変数 OPEN233_B3_VARIANT=control)
`python docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <同名_check.json>`
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目、8行以内)
Checker込みか/5 run完了/実費/EN行数・Checker判定/switches一致/E2E非混入/T-0結果。
