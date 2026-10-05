# 委任_07 委任文(全文保存、2026-10-05)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_07、ループ1「限定Trial(段階A)」段)。並行タスクなし。

## 性質/到達Status/禁止事項

- 性質: 委任_06で実装した新Stage 1(coverage_union: 3'-R+5-lite、関係単位、決定論検査、F3、H1)を**fresh実行(Stage 1のみ)**し、事前固定の採用基準で段階Aの合否を判定する。有料。合格なら段階B(E2E)へ、不合格なら原因分析をFableへ(Prompt追加で追い込まない)。
- Fable判断(規模・予算): 委任_06の費用概算(低¥53/中¥72/高¥99、48 run)に対し、**NORMAL 6 instanceをn=2に縮小**(SC 6+B2_hormuz[監視]はn=3、er009合成9種hold-out n=1)=計42 run、`--budget-jpy 70`(Guardrail)。実行順はsample-major(途中停止でもnが揃う)。
- 到達Status: Trial、最大`VALIDATED`。段階Aは中間判定(Status変更なし)。
- 採用基準(事前固定、結果を見て変えない): (1)正式SC 6件(B3・A2A3-0・A4-0・A5-0・B4-a・B3-same@neg5、`SAFETY_CRITICAL_CLAIM_DEFS`)が2経路∪でn=3中**3/3**(経路別も報告)。(2)hold-out(er009合成9種)で新たな見逃し0(各種のgold claimが∪で1/1)。(3)欠落IDの再実行後残存≤5%(run比)。参考(採否基準ではない、記録): HF-011(監視)、NORMAL候補数/記事、決定論検査で戻した件数(理由別)、経路別検出率とr3×r5の2×2相関、費用/call・合計・worst run、runtime。
- 即時STOP(有料run中): 1 run費用>¥6/API連続失敗でTrialAbort/例外2 instance以上/想定外の大量call(1 runあたりcall数が設計[経路2+再実行最大2]を超える)。見逃し・候補過多は止めずに完走し集計。
- 禁止: コード変更は不具合修正に限る(Prompt文言・判定規則の調整禁止=結果を見てのチューニング禁止)。Production変更禁止。gold・fixture変更禁止。N増し・再実行(skip existing再開を除く)禁止。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`編集禁止。`git add -A`/`stash`/`amend`禁止。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込み2,500文字以下。
- 費用上限: ¥70(Guardrail。T-3: 到達=自動STOPではない。承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加が合理的/QCD便益明らか、なら超過を記録して継続。暴走疑い時のみSTOP)。本管理ID枠: Phase残約¥138+追加¥100=約¥238、本管理ID支出¥0(開始前)。有料実行前に`--stage estimate`の概算を出力し、実測と並記。
- T-0: 委任ログ本ファイルに全文保存、check実行・結果記録。KPI provenance欄: 本段階の測定は全て**fresh**(frozen/reuse/差替えなし)、Stage 1のみ(E2Eではない=条件付きの中間測定として明記)。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー指示(原文、該当部分)

````
13. 費用・作業方針
無駄な大規模Trialを先に行わない。各ループとも、¥0分析 → 小規模Safety/normal確認 → KPI見込み確認 → 必要なら広いE2E の順で進める。
既存Evidenceは積極的に再利用するが、E2E KPI確認時はfresh runを使う。単発¥3超は報告する。
````

## 作業(要約)

1. T-0。2. `--stage estimate`(42 run、NORMAL n=2)。3. 段階A実行`--stage main --yes-run-paid --budget-jpy 70`(NORMAL n=2引数追加可、10分中断時はskip existingで1回だけ再開)→`--stage agg`。4. 集計・判定(基準(1)〜(3)機械判定+参考指標。不合格はclaim別に経路別出力・決定論検査・欠落ID/判定誤り・原因候補を分離、Prompt修正なし)。5. (¥0)rep30後段スイッチ値一覧を`er052_output/open233_kpi_recovery_02_offline_01/rep30_switch_values_01.md`へ。6. SSOT: OPEN_ITEMS本管理ID行進捗、REPORT_LEDGER 1行、REPORT §66直後に§67。7. 明示addでcommit/push(ACTIVE_TASK/RESULT_PACKETはadd禁止)。

## 事前指定Read/実行コマンド/報告(要約)

Read: `er052_open233_stage1_stageA_01.py`、段階A出力(Python集計)、rep30 summary json switches、rep30_full_01.py(Grep)。
コマンド: check_delegation_prompt.py(本ファイル→`_check.json`)、`er052_open233_stage1_stageA_01.py --stage estimate|main --yes-run-paid --budget-jpy 70|agg`(NORMAL n=2指定)、git status/明示add/commit/push/log。
報告: (1)結論8行以内 (2)結果表・2×2相関・決定論検査理由別 (3)不合格時の原因分離(確認/推測) (4)rep30スイッチ表の所在 (5)SSOT・T-0・commit・push・raw URL・一覧外Read (6)Fableへの論点(段階B可否/再設計要否)。

## 事前指定Grep一覧+追記位置・更新位置の手順

OPEN_ITEMS本管理ID行。REPORT `^## §66`直後に§67。REPORT_LEDGER末尾。

## 実行コマンド全文

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_07.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_07.md_check.json
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage estimate --normal-n 2
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage main --yes-run-paid --budget-jpy 70 --normal-n 2
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage agg
