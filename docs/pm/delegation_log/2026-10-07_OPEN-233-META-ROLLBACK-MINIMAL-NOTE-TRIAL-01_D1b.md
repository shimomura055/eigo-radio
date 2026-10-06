# 委任_D1b 簡略保存 (OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-01、上限JPY8)
## 管理ID
OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-01 委任_D1b。rep1停止の代替としてrep6を1本実行。
## 性質/到達上限Status/禁止事項
Trial実行(有料1 run)。Production/SSOT/git変更禁止、再実行はtimeout/APIエラーのみ1回、D2対象(rep1-5・eval)に触れない。
## 固定ブロック
E-1 上限JPY8。D-1 実費はcost.jsonへrep6追記。G-1 Trial限定。F-1 fail-closed。T-0簡略保存。T-2 TTSなし(7-5含む)。T-3 対象外。
## 事前指定Read一覧
runs/manifest.json(rep2のコマンド・env)。
## 事前指定Grep一覧+追記位置・更新位置の手順
rep2と同一env(OPEN233_RUNS_ROOT/OPEN233_B3_VARIANT=nb)・同一引数でout-dirをrep6に。完了後provenance・brief含有・行数確認、manifestへrep6追記。
## 実行コマンド全文
.venv python er052_open233_polysemy_nb_dev_01.py --phase phase1 --slug meta --ledger-txt .../ledger/nb/research_ledger/verified_fact_ledger.txt --out-dir .../runs/meta/nb/rep6 --budget-jpy 8 --yes-run-paid。check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-07_OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-01_D1b.md
## SSOT追記文
なし。
## Git
なし。
## 報告
RESULT_PACKET: 完了、実費JPY5.25、brief注意含有・行数10、R0/R1/R2=11/17/13、T-0。
