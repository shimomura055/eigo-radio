# REGRESSION_BASELINE_2026-10-24 (FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_27)
「既知3件」の定義を `docs/pm/PM_GOVERNANCE.md`・`docs/pm/REPORT_LEDGER.md` でGrepしたが、定義(件数3の既知失敗の一覧)は見つからなかった(REPORT_LEDGERに過去IDごとの「既知の無関係failure」の言及のみ)。以後「既知」は本baselineを参照する。

## 基準線
- コマンド: `.venv\Scripts\python.exe run_project_regression.py`(既定pattern `er0*_test_*.py`)および `--pattern "er1*_test_*.py"`(Opus W-04(3))。
- 既定: 327 files / collected 7071 / passed 7060 / failed 1 / skipped 10。失敗1件=`er064_kp_int_01_test_01.ProductionUnchanged.test_no_tracked_py_or_template_modified`(未commitのtracked .py変更があると必ず失敗する検査。clean tree=commit後は0)。他agentの作業中変更(例: Family Yの`er110_family_y_opinion_based_02*.py`)があれば、その帰属で失敗し得る。
- `er1*`: 32 files / collected 477 / passed 477 / failed 0。
- 出力に現れる `er003_test_bad ... test_case_0 FAIL` は runner自身のtestが作る意図的失敗fixtureの出力であり失敗に数えない。
- 「既知の恒常失敗」は0。一時状態(別agentの作業中の変更・並行runの出力dir)で出る失敗は、(a)単独実行で通る、(b)帰属agent/管理IDを記録、の2点を満たせば「他agent起因・一時」と分類してよい。それ以外は是正対象。
