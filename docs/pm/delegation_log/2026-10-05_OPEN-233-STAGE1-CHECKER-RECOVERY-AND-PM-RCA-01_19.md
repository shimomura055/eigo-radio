# 委任_19 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01(有料E2E本番)

## 管理ID
`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01`(委任_19、有料E2E本番)。並行タスクなし。

## Fable判断(委任_18の8論点への回答)
1. 計画: 20 run(SC 6x2+Std/Adv対2組4+負例4)で確定。B2_hormuz(HF-011監視)・neg4/neg6・er009 hold-outはE2E対象外とし、対象外であることをOPEN_ITEMS進捗・REPORTに明記(隠さない)。run数は増やさない。
2. 出口3'-R全文の再入は仕様どおり。出口全文由来の候補数・Stage 2再入費用・STAGE2_VERDICT_REUSE_NONBLOCKINGによる抑制数をrun別に集計する。
3. Recheck判定規則(prior issue解消のfail-closed、R5V prompt流用、新規候補はMAJOR相当で次cycle)は承認。Opus#18の論点に含める。
4. Waste検知はWorker実装どおり(検知時はE2E全体STOP)。Safety見逃し・STAGE4出口は止めず完走して集計。
5. Safety判定定義(重大見逃し=PASS系最終本文にgoldの逸脱が残存)を採用。Stage 1 M/Dは参考値。STAGE4/Human Review出口は別KPIとして件数。
6. total_calls>80は維持。超過時は内訳を報告。
7. OF-018は観測のみ(t_used_runs)。Tが使われてSTAGE4になった場合は別途報告。
8. 費用乖離の暫定基準: 平均純増が事前見込み+5.4円/セットに対し+-3円超(>+8.4または<+2.4)で「大幅」として原因確認。構造的Wasteは乖離の大小によらずSTOP。

## 性質/禁止事項
- 有料。Guardrail本委任合計90円(残98.29円、E2E見積mid66.5/high86.0)。スクリプトの--budget-jpy 86。1 run 6円超・call>80・API失敗>3・cycle>5は当該run停止(Waste→E2E全体STOP)。想定外の大量API発火(累計が見積highを超える勢い、または10 run時点で累計>50円)は中断して報告。
- 禁止: Production正式path変更禁止。コード変更は本番中に見つかった実行を妨げる不具合の最小修正のみ(判定・Checker・prompt・gold・fixture・Stage 2・Safety-critical定義には触れない。修正したら内容・影響・修正前後のrun扱いを報告)。frozen Stage 1/手動差替え/Trial artifactによる代替禁止。git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下。
- 出力先: er052_output/open233_e2e_acceptance_01/のみ(dry-run dirには触れない)。既存dirのgit status --porcelain空を前後で確認。
- 有料run起動手順: Get-CimInstance Win32_Processでer052_open233_e2e_acceptance_01.py/stageAのpythonプロセスなしを確認→Start-Processバックグラウンド+stdout/stderrログ→60秒ポーリング(run数・累計費用・最新run状態)→600秒無進捗は状況報告(殺さない)。skip existingで再開可能。同一run jsonが既に存在する場合は再実行しない(重複課金防止)。
- T-0: 委任ログ本ファイル全文保存(分割)、check PASS後commit。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業
Step 0(0円): プロセス確認、--stage estimate再確認、git status確認。
Step 1(本番): --stage main --yes-run-paid --budget-jpy 86をバックグラウンド起動。ポーリングで(a)累計費用、(b)完了run数、(c)Waste/STOPフラグ、(d)STAGE4出口数、(e)1 run 3円超を監視。10 run時点で累計>50円なら中断判断のため一時報告(run_logのcheckpointで停止できるならその手順、できなければ報告のみ)。
Step 2(集計): --stage agg。summary e2e_acceptance_summary_01.md: (i)Safety: gold 6 instance x2のE2E出口時点の残存、negでの誤BLOCKING、(ii)Human Review/STAGE4出口件数(理由別)、(iii)Rewrite率・cycle分布・Stage 2発動率・候補数(Stage 1初回/Recheck/出口全文由来別)、(iv)費用: Stage別・/記事・/セット(実測対と推計x2を列分離)・差し引き(0.76〜0.91円/セット、推計)後の純増・通常/上振れ・worst・3円超一覧・事前見込み+5.4との乖離判定、(v)runtime、(vi)waste_flags・t_used_runs、(vii)provenance監査(全run stage1_source=fresh、frozen/reuse/substitution=false、結果側との照合)。
Step 3(再発防止自己確認8項目): 1つずつ「確認方法/証跡パス/結果」で表に(fresh開始/upstream frozen・reuse・substitutionなし/Safety値がE2E値/Std・Adv双方/Human Review 0実測/Opus・Fable未解決Safety警告(OPUS_FINDINGS_LEDGERのOPEN残を列挙し解消・未解消を判定)/条件付き値とE2E値の混同なし/未解決項目のOpen Item化)。
Step 4(Opus#18 packet、0円): docs/pm/opus_packet_open233_e2e_acceptance_01.md。論点1 E2E結果の妥当性(Safety定義・provenance監査・Std/Adv扱い)、2 Recheck新仕様の判定規則、3 費用乖離・Waste所見、4 Opus台帳OPEN残の解消判定、5 VALIDATED表記の可否、6 Production採用提案前に残るSafety懸念(A4-0揺らぎ、OF-018、HF-011未測定)。読み先・Grep語を列挙。
Step 5(SSOT): REPORT §73(E2E結果、provenance=fresh/E2E、Status候補はFable/Opus照合待ちと明記、VALIDATEDと書かない)。OPEN_ITEMS本管理ID行進捗「E2E 20 run完了: 重大見逃し/Human Review/純増(実測対・推計)/worst/乖離/Waste、対象外: B2_hormuz/neg4/neg6/hold-out。Opus#18待ち」。REPORT_LEDGER.md 1行。ACTIVE_TASK.md(addしない)。費用累計を枠238円に対して記録。
Step 6: commit/push(明示add: run json全件・summary・estimate・packet・REPORT・OPEN_ITEMS・REPORT_LEDGER・委任ログ+check.json、コード修正があればそのファイル)。メッセージ: `OPEN-233 E2E-ACCEPTANCE-01: fresh E2E 20 run【重大見逃し n・Human Review n・純増x円/セット・worst y円・Waste 有/無】、再発防止自己確認8項目、Opus#18 packet(委任_19、円)`

## STOP条件(該当時はE2E全体を止めて報告)
Waste検知(構造的: 同一候補の反復Rewrite・出口全文の反復・cycle>5・call>80)/provenance違反(fresh以外・代替発生)/1 run 6円超/累計が見積high 86円超/想定外の大量API発火。Safety見逃し・STAGE4出口はSTOPせず完走・集計(その後Fableが分類)。

## 事前指定Read一覧
er052_open233_e2e_acceptance_01.py(CLI・集計欄・Waste判定部)、er052_output/open233_e2e_acceptance_01/estimate.json、docs/pm/e2e_plan_open233_stage1_loop2_01.md §追補、docs/pm/OPUS_FINDINGS_LEDGER.md(OPEN残の節)、docs/pm/opus_packet_open233_stage1_loop2_01.md(packet形式)、REPORT §72(形式)。

## 事前指定Grep一覧+追記位置・更新位置の手順
E2Eスクリプト: waste|STOP|provenance|budget|skip|checkpoint|vs_expected|set_cost|residual_at_pass|stage4。OPEN_ITEMS本管理ID行。REPORT末尾§72。REPORT_LEDGER末尾。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_19.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_19.md_check.json
プロセス確認: Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*er052_open233_e2e_acceptance_01.py*' -or $_.CommandLine -like '*er052_open233_stage1_stageA_01.py*' } | Select-Object ProcessId, CommandLine
見積: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01.py --stage estimate --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01 --estimate-out C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01\estimate.json
本番: Start-Process -FilePath C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -ArgumentList '-u','C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01.py','--stage','main','--yes-run-paid','--out-dir','C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01','--budget-jpy','86' -RedirectStandardOutput C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01\run_stdout.log -RedirectStandardError C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01\run_stderr.log -NoNewWindow
集計: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01.py --stage agg --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01
(CLI引数名が実装と異なる場合は--helpに合わせ、使用した全コマンドを委任ログに記録)
Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。

## 報告(短く)
(1)結論8行以内(重大見逃し/Human Review/純増円/セット[実測対・推計]/通常・上振れ/worst/乖離判定/Waste/費用合計・累計)、(2)表(Safety instance別、費用Stage別、provenance監査)、(3)自己確認8項目表、(4)STOP該当有無・コード修正有無、(5)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測、(6)Fableへの論点(Opus#18前の懸念、Status候補はFable判断に委ねる)。
