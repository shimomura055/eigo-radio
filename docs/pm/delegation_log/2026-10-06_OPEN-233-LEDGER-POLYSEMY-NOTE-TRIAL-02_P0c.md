# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02 委任_P0c(簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02(委任_P0c)
## 性質/到達上限Status/禁止事項
DEV実装(新規ファイルのみ)+評価表、JPY0。禁止: Production file変更/有料API/SSOT編集/git。P0a/P0b出力へ触らない。
## 固定ブロック
E-1 / D-1 / G-1 / F-1: 該当なし(JPY0)。T-0: 簡略保存+checker。T-2: TTSなし。T-3: 対象外。
## 事前指定Read一覧
er052_open233_ledger_clarity_pprime_dev_01.py、er019 B3/runner、run_checker_after_p01.py、FREEZE_T01_CONFIG.json、E_trial_plan.md
## 事前指定Grep一覧+追記位置・更新位置の手順
新規 er052_open233_polysemy_nb_dev_01.py、tests/test_nb_dev_01.py、tools/launch_batch_p02.py、docs/pm/polysemy_trial_02/P0c_eval_template.md、P0c_run_readme.md
## 実行コマンド全文
.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_02/tests/test_nb_dev_01.py -q
.venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --theme t --slug meta --ledger-txt er019_output/meta/run_03/ledger/verified_fact_ledger.txt --out-dir er052_output/open233_polysemy_trial_02/runs/meta/nb/rep1 --budget-jpy 12 --dry-run
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
作成ファイル/stop-after値/Researcher不実行保証/test/dry-run/Production無変更/1 run費用/T-0
