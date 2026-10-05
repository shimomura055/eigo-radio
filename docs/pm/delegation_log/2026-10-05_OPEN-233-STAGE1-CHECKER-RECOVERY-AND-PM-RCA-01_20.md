# 委任_20 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01(E2E停止の原因分析、¥0)

## 管理ID
`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01`(委任_20、¥0: 停止原因分析+記録)。

## 性質・禁止事項
有料API禁止。コード変更禁止。E2E再開禁止(aborted jsonの削除も禁止)。SSOT編集はREPORT §73、`OPEN_ITEMS.md`本管理ID行、`REPORT_LEDGER.md`1行、`ACTIVE_TASK.md`(addしない)のみ。`git add -A`/`stash`/`amend`禁止。1回の書き込み2,500文字以下。KPI provenance: 本委任は既存E2E 2 run(fresh Stage 1、E2E途中)の再集計であり、VALIDATED判定・Production採用判定を行わない。

## 背景(Fable)
委任_19でE2Eが2 run目(s1/safety_A2A3)の1 run ¥6超Waste検知で全体停止(完了1 run bgroup_B3 ¥4.55、A2A3はabort時¥6.21、累計¥10.76)。実測約¥5.4/run vs 見積mid約¥3.3/run(約1.6倍)。ユーザー指示「実測コストが事前見込みから大幅に乖離した場合は原因を確認する。構造的Wasteなら別問題としてSTOP」「想定外の大量API発火が見えた場合は中断」に従い、再開前に¥0で原因を確定し、ユーザー判断材料を作る。¥6/runはFableが設けたWaste閾値であり、ユーザーKPIではない(ユーザー: 単発¥3超は報告のみ)。

## 作業
1. call単位の内訳: 2 run json・budget history・call_logから、call種別(r3初回/r5初回/Stage 2 body・hook・floor_verify・s1/Rewrite(HF別)/recheck r3・r5v/出口3'-R/その他)ごとに件数・tokens(input/output/reasoning)・費用。見積(estimate.json、cost_feasibility_open233_stage1_01.md §2の式: Stage 1 ¥1.23、Stage 2 ¥0.83〜1.69、Rewrite+Recheck ¥0.17〜0.35、出口 ¥0.22〜0.45)と項目別に対比し、乖離を(a)見積誤り(新Recheck仕様=r3+r5v 2 callが見積に未反映、出口3'-R全文の実費)、(b)SC fixtureの性質(意図的に重大逸脱を埋め込んだ記事はRewrite・cycle 2が仕様どおり発生=上振れ側の代表)、(c)構造的Waste(同一候補の反復Rewrite、不要call、無限retry、同じ判定の再実行)に分類。(c)の有無を証拠付きで判定(HF-009がc1で複数回試行された点を精査: 同一候補の再Rewriteか、別spanか)。
2. rep30同一instanceとの比較: rep30のB3/A2A3 run(Stage 1凍結)の後段費用・cycle・Rewrite回数と比較し、後段の増分が(i)候補数増(新Stage 1約22候補/記事→Stage 2費用)、(ii)新Recheck仕様、(iii)出口全文のどれに由来するかを分解。
3. 20 run費用の再予測: run種別(SC 12/対4/負例4)ごとに、実測2 run・G arm Stage 1実測・rep30後段実測から1 run費用のlow/mid/highを置き、合計と残予算(¥98.29−¥10.76=¥87.53)との差を算出。SCをn=1(6 run)に縮小した14 run案、対+負例のみ8 run案も併記(Safety evidenceへの影響を明記: SC n=1ではA4-0揺らぎ等を検出しにくい)。
4. 1 run閾値: ¥6→¥10に上げた場合に止まらなくなるrunの見込みと、残るWaste検知(cycle>5・call>80・API失敗>3・同一候補反復)で構造的Wasteを捕捉できるかを評価。
5. 純増の暫定値(参考、2 run・SCのみ、推測明記): B3 ¥4.55を「上振れ側1記事」として、セット換算・差し引き後の純増を示し、事前見込み+¥5.4/セット(通常)・上振れ+¥6.7との位置づけ。
6. 記録: REPORT §73「E2E停止(2 run目、¥6/run Waste閾値該当)、原因分類、再開はユーザー判断待ち」(provenance=fresh/E2E途中、VALIDATED不可と明記)。OPEN_ITEMS.md本管理ID行: Status `USER_DECISION_REQUIRED(E2E停止)`、要約。ACTIVE_TASK.md同旨。REPORT_LEDGER.md 1行。分析文書 docs/pm/e2e_stop_analysis_open233_01.md。
7. commit/push(明示add)。メッセージ: `OPEN-233 E2E-ACCEPTANCE-01: E2E停止(2 run目¥6超)の¥0原因分析【見積誤り/SC性質/構造的Waste 有無】、20 run費用再予測【¥(実測値)】、USER_DECISION_REQUIRED(委任_20、¥0)`

## 事前指定Read一覧
er052_output/open233_e2e_acceptance_01/runs/s1/bgroup_B3.json、同dir safety_A2A3.json(call_log・budget部分をPythonで抽出、全文Readしない)、er052_output/open233_e2e_acceptance_01/budget_state_e2e_acceptance_01.json、estimate.json、docs/pm/cost_feasibility_open233_stage1_01.md §2、rep30 instances_s1の bgroup_B3.json・safety_A2A3.json(call_log)。

## 事前指定Grep一覧+追記位置・更新位置の手順
er052_open233_e2e_acceptance_01.py: per_run_cost_gt|waste|HF-|recheck|exit。rep30出力dir名: er052_output/open233_self_recovery_flow_runner_01_rep30*。REPORT末尾§72(OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md)。OPEN_ITEMS本管理ID行。REPORT_LEDGER末尾(docs/pm/REPORT_LEDGER.md)。

## 実行コマンド全文
T-0: 委任ログ本ファイル全文保存、check PASS後commit。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_20.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_20.md_check.json
分析: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\e2e_stop_analysis_01.py(新規、出力json/md同dir)

## SSOT追記文
REPORT §73、OPEN_ITEMS本管理ID行、REPORT_LEDGER 1行、ACTIVE_TASK(addしない)に、作業6の内容を実測値で記述する(推測は推測と明記)。

## Git
git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。commit末尾にCo-Authored-Byを付ける。

## 報告(短く)
(1)結論8行以内(乖離の主因と分類a/b/c、構造的Wasteの有無と証拠、20 run再予測low/mid/high、残予算との差、14 run・8 run案の費用)、(2)表(call種別内訳×見積対比、rep30比較、再予測)、(3)SSOT・T-0・commit・push・raw URL、確認/推測、(4)Fableへの論点。
