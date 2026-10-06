# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 委任_L1d(簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03(委任_L1d: 改善パターンA/B/Cのprompt作成+B3転記規則の接頭辞対応、JPY0)。
## 性質/到達上限Status/禁止事項
prompt設計(新規ファイル)。禁止: 有料API/Production変更/SSOT編集/git/特定fact_id・5テーマ固有語のprompt混入/件数目安の記載。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
該当なし(JPY0)。T-0のみ(本ファイル+check_delegation_prompt.py)。
## 事前指定Read一覧
F0_failure_analysis.md、H1のprompt差込仕様、er052_open233_polysemy_nb_dev_01.pyの転記規則ブロック。
## 事前指定Grep一覧+追記位置・更新位置の手順
共通の操作的定義(i)〜(iv)を逐語で3パターンへ入れる。A=一体型、B=2段階、C=既存notes昇格+A fallback。nb_dev接頭辞はOPEN233_NOTE_PREFIX。衛生チェックはprompt_hygiene_p03.py。
## 実行コマンド全文
prompt_hygiene_p03.pyと、test_nb_dev_01.pyのpytest。
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
作成ファイル、共通定義、パターン差分、衛生チェック、nb_dev接頭辞とtest、T-0結果。
