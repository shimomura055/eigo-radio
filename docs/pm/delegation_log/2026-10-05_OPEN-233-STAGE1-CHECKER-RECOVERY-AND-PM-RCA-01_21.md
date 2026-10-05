# 委任_21 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01(記録+有料E2E再開・完走)

## 管理ID
`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01`(委任_21、記録+有料E2E再開・完走)。並行タスクなし。

## ユーザー追加指示(原文はDECISION_LOGへ逐語記録。見出し: `## OPEN-233 E2E-ACCEPTANCE-01 追加指示(2026-10-05、ユーザー判断: 20 run再開・予算+¥35・1 run閾値¥20・独自停止条件の禁止・報告フォーマット固定)`)
要点: 20 run全再開可/追加予算+¥35/1 run停止閾値¥20/¥20以内でも構造的Waste(同一候補の不自然な反復Rewrite・call数急増・API失敗連発)はSTOP/単発¥3超の記録・報告継続/独自の過度に厳しい停止条件を追加しない/ユーザー向け報告は固定5節順(1結論 2ユーザー判断が必要なこと 3重要な問題・残作業 4完了・良好だったこと 5次の行動・費用)。

## 性質/禁止事項
- 有料。予算: 本管理ID枠¥238+¥35=¥273、使用済み累計¥150.47(¥139.71+E2E¥10.76)、残¥122.53。E2Eスクリプト`--budget-jpy 120`。1 run停止閾値=¥20(ユーザー承認値。これより厳しい独自閾値を設けない)。STOPは構造的Waste(同一候補の不自然な反復Rewrite、call>80/run、API失敗>3/run)のみ。¥3超は全件記録・報告。累計が残予算に達する見込みになった場合のみ中断して報告。
- 禁止: Production正式path変更禁止。コード変更は(1)閾値・予算・実行順・aborted再実行の設定変更、(2)実行を妨げる不具合の最小修正、(3)abort時の部分call_log保存(軽微)のみ。判定・Checker・prompt・gold・fixture・Stage 2・Safety-critical定義に触れない。frozen/手動差替え/artifact代替禁止。git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下。
- 有料run起動手順: プロセス確認→Start-Processバックグラウンド+ログ→60秒ポーリング→600秒無進捗は報告(殺さない)。skip existing。aborted s1/safety_A2A3.jsonはユーザー承認済み再実行対象: 削除ではなくruns/_aborted/へ移動してから再開(証跡保全)。
- T-0: 委任ログ全文保存、check PASS後commit。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり(T-3のCap記述は閾値¥20・枠¥273に合わせる)。

## 作業
Step 0(¥0、記録とPMルール反映): (1)DECISION_LOGへ原文逐語(転写スクリプト)。(2)docs/pm/PM_GOVERNANCE.md 9節「ユーザー向け報告フォーマット」を固定5節順(1結論/2ユーザー判断が必要なこと/3重要な問題・残作業/4完了・良好だったこと/5次の行動・費用)に置換(候補セクション制を廃止、各節の小項目をユーザー原文どおり列挙、「通常の技術作業を判断事項として上げない」「非エンジニアのPMが原文を読まずに判断できる要約」を明記、2026-10-05ユーザー指示)。T-3/10節/11節の該当箇所に「ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)」を追記。Closeout項目に「報告が5節順か」を追加。docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.mdの報告欄も5節順へ。(3)OPEN_ITEMS.md本管理ID行: 枠¥273・閾値¥20・Status IN_PROGRESS(E2E再開)。ACTIVE_TASK.md同旨(addしない)。
Step 1(設定変更+テスト): E2Eスクリプト: per_run_cost_gt閾値を¥20に(CLI --per-run-cap-jpy、既定20)、実行順を非SC(対4+負例4)→SCに、abort時に部分call_logをjsonへ保存。既存テストPASS。aborted jsonをruns/_aborted/へ移動。
Step 2(本番): --stage main --yes-run-paid --budget-jpy 120 --per-run-cap-jpy 20をバックグラウンド起動、完走までポーリング(累計費用・run数・¥3超・waste_flags・STAGE4出口を記録)。
Step 3(集計): --stage agg + e2e_acceptance_summary_01.md: (i)Safety: gold 6x2のE2E出口時点の残存件数(=重大見逃し)、negの誤BLOCKING、(ii)Human Review/STAGE4出口件数(理由別)、(iii)Rewrite率・cycle分布・Stage 2発動率・候補数(初回/Recheck/出口全文別)、(iv)費用: Stage別・/記事・/セット(実測対2組の合算と x2推計を列分離)・差し引き(¥0.76-0.91/セット、推計)後の純増・通常(非SC)と上振れ(SC・Rewrite発生)を分離・worst・¥3超一覧・事前見込み+¥5.4/セットとの比較、(v)runtime、(vi)waste_flags・t_used_runs、(vii)provenance監査(全run fresh、frozen/reuse/substitution=false、結果側と照合)。
Step 4(再発防止自己確認8項目): ユーザー指示の8項目を「確認方法/証跡/結果」で表に(Opus台帳OPEN残の本E2Eでの解消・未解消判定を含む)。
Step 5(Opus#18 packet): docs/pm/opus_packet_open233_e2e_acceptance_01.md: (1)E2E結果の妥当性(Safety定義・provenance・Std/Adv)、(2)Recheck新仕様(fail-closed/R5V流用[ループ2で能力10-12/18と判定したpromptの流用の是非]/新規候補MAJOR)、(3)費用(非SC/SC分離、乖離、Waste所見、Recheck r5v・floor_verify/s1二重確認)、(4)Opus台帳OPEN残の解消判定、(5)VALIDATED表記の可否、(6)Production採用提案前に残るSafety懸念(A4-0揺らぎ、OF-018、HF-011未測定)。読み先・Grep語列挙。
Step 6(SSOT): REPORT §74(E2E完走結果、provenance=fresh/E2E、Status候補はFable/Opus照合待ちと明記、VALIDATEDと書かない)。OPEN_ITEMS.md本管理ID行進捗。OPEN-233-COST-REDUCTION-01行にRecheck r5v・floor_verify/s1二重確認を候補追記。REPORT_LEDGER.md 1行。ACTIVE_TASK.md(addしない)。
Step 7: commit/push(明示add: run json全件(_aborted含む)・summary・packet・PM_GOVERNANCE・テンプレート・DECISION_LOG・OPEN_ITEMS・REPORT・REPORT_LEDGER・スクリプト・委任ログ+check.json)。Step 0の記録は本番起動前に先行commit可。メッセージ: `OPEN-233 E2E-ACCEPTANCE-01: ユーザー追加指示(予算+¥35・閾値¥20・独自停止条件禁止・報告5節固定)を記録しPM_GOVERNANCE反映、fresh E2E 20 run完走【重大見逃し n・Human Review n・純増 非SC¥x/SC¥y/セット・worst¥z・Waste 有/無】、自己確認8項目、Opus#18 packet(委任_21、¥…)`

## STOP条件(ユーザー承認値のみ)
構造的Waste(同一候補の不自然な反復Rewrite/1 run call>80/1 run API失敗>3)/provenance違反/1 run ¥20超/累計が残¥122.53に達する見込み。Safety見逃し・STAGE4出口はSTOPせず完走・集計。

## 事前指定Read一覧
er052_open233_e2e_acceptance_01.py(閾値・実行順・abort処理・集計部)、docs/pm/e2e_stop_analysis_open233_01.md(再予測)、docs/pm/PM_GOVERNANCE.md 9節(置換対象)、docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md(報告欄)、docs/pm/OPUS_FINDINGS_LEDGER.md(OPEN残)、docs/pm/opus_packet_open233_stage1_loop2_01.md(形式)、REPORT §73。

## 事前指定Grep一覧+追記位置・更新位置の手順
E2Eスクリプト: per_run_cost_gt|6\.0|order|aborted|call_log|waste|budget。PM_GOVERNANCE: ## 9|候補セクション|adaptive|T-3|Guardrail|Closeout Mandatory。OPEN_ITEMS本管理ID行・OPEN-233-COST-REDUCTION-01行。DECISION_LOG末尾。REPORT末尾。REPORT_LEDGER末尾。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_21.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_21.md_check.json
転写: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\append_decision_log_from_sources_01.py(引数はヘッダ参照)
テスト: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01_test_01.py
プロセス確認: Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*er052_open233_e2e_acceptance_01.py*' } | Select-Object ProcessId, CommandLine
本番: Start-Process -FilePath C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -ArgumentList '-u','C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01.py','--stage','main','--yes-run-paid','--out-dir','C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01','--budget-jpy','120','--per-run-cap-jpy','20' -RedirectStandardOutput ...\run_stdout_resume.log -RedirectStandardError ...\run_stderr_resume.log -NoNewWindow
集計: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01.py --stage agg --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01
(CLI引数名が実装と異なる場合は--helpに合わせ、使用した全コマンドを委任ログに記録)
Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。

## 報告(ユーザー指示の5節順で短く)
1.結論(完了/停止/Production反映状況[未反映]/次へ進める条件)、2.ユーザー判断が必要なこと(なければ「なし」)、3.重要な問題・残作業(作業ミス/仕様制約/未確認、各々 解決済み or blocking)、4.完了・良好だったこと、5.次の行動・費用(本委任費用・累計/枠¥273・残)。末尾に: 表(Safety instance別、費用 非SC/SC・/記事・/セット、provenance監査)、自己確認8項目表、SSOT・T-0・commit・push・raw URL、確認/推測、コード修正内容。

## KPI provenance
fresh Stage 1 E2E(frozen/reuse/代替なし)。本委任の集計はE2E実測。Status候補はFable/Opus照合待ちでVALIDATED/Production採用判定は行わない。Opus台帳: OPEN残の解消判定をpacketで行う。
