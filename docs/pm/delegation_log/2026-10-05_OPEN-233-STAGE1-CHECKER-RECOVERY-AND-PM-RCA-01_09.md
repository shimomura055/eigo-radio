# 委任_09(ループ1「KPI見込み確認」段、¥0)

管理ID: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。並行タスクなし。

## 性質/禁止事項
- 性質: ¥0・既存出力の分析のみ(有料APIなし、コード変更なし)。段階A(委任_07c、commit 194a4ded)はSafety側の採用基準3つに合格したが、NORMAL群の候補数が2経路∪で24.0/記事(r3 23.5、r5 13.8)=平均判定単位数20.4に匹敵し、ほぼ全文が候補化している。これをそのままStage 2へ渡すE2E(段階B、約40〜50円)は、Cost KPI(+2円/記事)とHuman Review 0・不要Rewriteの観点で見込みが立たない可能性が高い。ユーザー§13「KPI見込み確認→必要なら広いE2E」に従い、E2Eの前に¥0で見込みを確定し、見込みが立たない場合のループ2設計の論点(構造的、Prompt文言の小修正ではない)を整理する。
- 禁止: 有料API禁止。コード・Prompt変更禁止。gold・fixture変更禁止。SSOT編集はOPEN_ITEMS.md該当行の進捗欄・REPORT_LEDGER.md1行のみ。git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下。
- T-0: 本ログに全文保存(分割)、check実行・結果記録。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー指示(原文、該当部分)
9. Cost / Productivityも同時に見る
重大見逃し0だけを達成して、全記事を大量MAJOR扱いする方式も成功ではない。以下も測る。
- 正常/負例へのMAJOR誤検出
- Stage 2発動率
- Rewrite率
- cycle数
- Human Review / USER_DECISION_REQUIRED
- 平均追加費用
- worst run
- runtime
ただし、Safety KPIを過剰検出削減のために緩めない。
13. 費用・作業方針: ¥0分析 → 小規模Safety/normal確認 → KPI見込み確認 → 必要なら広いE2E

## 作業(出力: er052_output/open233_kpi_recovery_02_offline_01/stageA_candidate_composition_01.{py,json,md}、新規文書docs/pm/design_open233_stage1_loop2_prep_01.md)
1. 候補の内訳(段階A全42 run、er052_output/open233_stage1_stageA_01/の保存出力): run・instance群(SC/B群/NORMAL/hold-out)別に候補の発生源を分類: (a)r3 LLMがCANDIDATE、(b)r5 LLMがCANDIDATE、(c)決定論検査で戻した(negation_polarity_mismatch 149件・quote_not_in_ledger 4件・その他)、(d)coverage_gap。(a)(b)について、候補のflags(10種)の分布、issueの有無・長さ、related_fact_idの有無、claim_in_articleの有無。SUPPORTEDの割合(全単位中)。
2. NORMAL/負例群の候補の性質(各instance先頭5件): 「本当に逸脱か/自然な推論・言い換え(問題なし)/Checkerが迷って候補にしただけ」のラベル(推測と明記、gold変更ではない)。負例neg1〜3は本来0件が期待される群。
3. negation_polarity_mismatch 149件の検査: 発火した単位と引用factの否定語を列挙し、真の極性不一致か誤発火かを分類(確認/推測)。
4. Stage 2負荷・KPI見込みの推定(rep30実測fit: Stage 2費用約0.099+0.073x候補数、S1は割れたらBLOCKING): 候補24/記事の場合の(i)Stage 2費用/記事、(ii)期待BLOCKING件数(rep30のBLOCKING率を保守適用/NORMALで問題なしラベル割合をStage 2が正しく落とす場合の2通り)、(iii)Rewrite・cycle・Human Reviewへの波及、(iv)平均追加費用。結論: 段階BでKPI 3つ(Human Review 0/見逃し0/+2円)を満たす見込みをYes/No/不明で。
5. 見込みが立たない場合のループ2設計論点(設計はせず論点整理、構造): (A)Stage 1出力の2層化(discrepancy必須、具体化できないものはUNSUREとして安価な決定論/小batch triageへ)、(B)決定論検査の精度是正、(C)Stage 2のbatch化、(D)r5(13.8)とr3(23.5)の差の意味。各論点でSafety(SC 6件検出維持)を損なわないかを明記。Opus#17レビューの必要性。
6. SSOT: OPEN_ITEMS.md本管理ID行進捗、REPORT_LEDGER.md1行、ACTIVE_TASK.md(addしない)。
7. commit/push(明示add)。メッセージ: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: 段階A候補の内訳(LLM/決定論/NORMAL性質)とStage 2負荷・KPI見込み【Yes/No】、ループ2設計論点(委任_09、¥0)

## 事前指定Read
er052_open233_stage1_stageA_01.py、段階A出力(Pythonで一括、サンプル検査は個別Read)、er052_open233_stage1_coverage_checker_01.py(Grep)、rep30 summary_kpi_01.json、agg_cost_recalc_models_01.md。
## 事前指定Grep一覧+追記位置・更新位置の手順
OPEN_ITEMS.md本管理ID行(進捗欄のみ追記)。REPORT_LEDGER.md末尾に1行追記。
KPI provenance: 全て既存fresh出力(段階A 42 run、rep30)の再集計、¥0、E2Eではない。
Opus台帳更新: なし(Opus#17は必要性の論点整理のみ、OPUS_FINDINGS_LEDGER.md更新なし)。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_09.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_09.md_check.json
分析: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\stageA_candidate_composition_01.py
Git: git status --porcelain、明示add、commit、git push origin main、git log --oneline -1。

## 報告
RESULT_PACKET.mdには短い要約(20行程度)。詳細は上記出力ファイルへ。報告(短く): 結論8行以内、表、ループ2論点(A)〜(D)、SSOT・commit・push・raw URL、確認/推測、Fableへの論点。
