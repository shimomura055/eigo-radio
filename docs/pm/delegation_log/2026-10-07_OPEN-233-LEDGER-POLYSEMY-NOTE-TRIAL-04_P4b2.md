## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04(委任_P4b-2)。DEV runnerにenv出力先上書き追加+5記事Control Phase 1実行。
## 性質/到達上限Status/禁止事項
DEV改修1ファイル+Trial実行(Control側のみ)。禁止: N+B側/Production変更/SSOT編集/git/E2E state書込。上限JPY60。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1上限JPY60、D-1実費はruns/cost_control_p1.json、G-1 Trial限定、F-1 fail-closed、T-2 TTSなし、T-3対象外。
## ユーザー指示(原文、要点)
5記事Trial: Control vs 自動生成N+B。固定台帳。artifact競合・条件混在禁止。並列化。
## 事前指定Read一覧
runner L20-40/L160-175/引数、既存test、P0c_run_readme.md を読了。
## 事前指定Grep一覧+追記位置・更新位置の手順
RUNS_ROOTをenv OPEN233_RUNS_ROOT上書き化(既定不変)、test_k追加、dry-run5件、並列本実行、事後確認、manifest作成。
## 実行コマンド全文
pytest 11件PASS。5テーマを並列phase1本実行(--budget-jpy 12 --yes-run-paid)。ログはruns/_logs/。
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目、10行以内。評価はしない)
runner改修+test、5run完了(再開なし)、実費合計JPY24.656、provenance、行数、E2E非混入、manifest。
