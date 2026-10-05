# 委任_07c(段階Aの再開2。委任_07はAPIエラー、07bは600秒無進捗でworker停止)

管理ID: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。並行タスクなし。
KPI provenance: 全てfresh、Stage 1のみ(E2Eではない=条件付き中間測定)。

## 最初にやること(¥0、重複課金の防止が最優先)
1. 実行中プロセス確認(er052_open233_stage1_stageA_01)。動いていれば起動しない。60秒ごとにポーリング(最大20分)。
2. 出力状態集計(run json件数・費用・budget state・--stage agg)。委任_07/07b委任ログ・未commit差分を引き継ぐ(revertしない)。
3. (¥0)rep30_switch_values_01.mdの有無確認、無ければ作成。

## 実行方法
有料実行はバックグラウンド起動しログへリダイレクト、ポーリング。skip existing(二重課金なし)。
即時STOP: 1 run>6円/API連続失敗TrialAbort/例外2 instance以上/設計超のcall数/1 run>10分進まない。

## 仕様(委任_07と同一、変更禁止)
- SC 6 instance+B2_hormuz(監視)n=3、NORMAL 6 instance n=2、er009合成9種hold-out n=1=計42 run。sample-major。--budget-jpy 70(Guardrail、T-3)。
- 採用基準(事前固定): (1)正式SC 6件が2経路∪でn=3中3/3(経路別も報告)。(2)hold-out新規見逃し0。(3)欠落ID再実行後残存5%以下。参考: HF-011(監視)、NORMAL候補数/記事、決定論検査で戻した件数(理由別)、経路別検出率とr3xr5相関、費用/call・合計・worst run、runtime。
- 禁止: Prompt・判定規則調整禁止(不具合修正のみ)、Production変更禁止、gold・fixture変更禁止、N増し禁止、CURRENT_SPEC.md/PM_GOVERNANCE.md編集禁止、git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下。
- 費用: 本管理ID枠約238円。委任_07/07b発生分を含め累計報告。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー指示(原文、該当部分)
13. 費用・作業方針
無駄な大規模Trialを先に行わない。…E2E KPI確認時はfresh runを使う。単発¥3超は報告する。

## 作業(順序)
T-0 → プロセス確認・待機 → 状態集計 → スイッチ値一覧 → 残run実行 → --stage agg → 判定 → SSOT(OPEN_ITEMS本管理ID行、REPORT_LEDGER 1行、REPORT §67) → commit/push(明示add)。
コミットメッセージ: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: ループ1 段階A(新Stage 1 fresh 42 run、2経路∪)【結果】、rep30スイッチ値一覧(委任_07〜07c)

## 事前指定Read: er052_open233_stage1_stageA_01.py、段階A出力、rep30 summary json・_rep30_full_01.py、scratchログtail。
## 報告: (1)結論8行以内(2)結果表・2x2相関・決定論検査理由別(3)不合格時の原因分離(4)スイッチ値表の所在(5)SSOT・T-0・commit・push・raw URL(6)Fableへの論点。

## 性質/到達Status/禁止事項
性質: Trial(DEV)・有料。到達Status: 段階A合否判定まで。Production変更禁止。禁止事項は上記「仕様」の禁止欄のとおり。

## 事前指定Read一覧
er052_open233_stage1_stageA_01.py(全文可)。段階A出力(Pythonで一括)。rep30 summary json・_rep30_full_01.py。scratchログtail。

## 事前指定Grep一覧+追記位置・更新位置の手順
OPEN_ITEMS本管理ID行。OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md末尾(§66直後)に§67。docs/pm/REPORT_LEDGER.md末尾。

## 実行コマンド全文
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_07c.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_07c.md_check.json
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage main --yes-run-paid --budget-jpy 70 --normal-n 2
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage agg
