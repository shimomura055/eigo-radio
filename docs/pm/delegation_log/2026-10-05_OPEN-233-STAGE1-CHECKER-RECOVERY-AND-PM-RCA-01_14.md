# 委任_14 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 ループ2/3 限定Trial(G arm)→E2E準備(有料)

## 管理ID
OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(委任_14、並行タスクなし)

## 性質/禁止事項
- 有料。Guardrail本委任合計¥40(累計¥111.91/枠¥238)。見積+30%超なら進まず報告。1 run ¥6超停止、¥3超全件記録。
- 禁止: Production正式path変更/既存prompt定数・gold・fixture・Safety-critical定義・Stage 2変更/git add -A・stash・amend/ACTIVE_TASK・RESULT_PACKET add。E2Eスクリプト新規作成可(既存runner既定挙動不変)。1回書込2,500字以下。
- 出力先: 新規dir er052_output/open233_stage1_loop2_garm_01/(必要なら..._garm_r5low_01/)。既存dirは読取のみ、前後にgit status --porcelain空を確認。
- 有料run手順: プロセス確認、Start-Process背景+ログ、60秒ポーリング、600秒無進捗は報告(killしない)、skip existing。

## Fable判断(委任_13照合)
r5-V構成は不採用(gold強制でもM検出10〜12/18)。残る手段=(G)reasoning effort引下げをr5は5-lite full維持のまま経路別適用(Opus#17 §4レビュー済み範囲、ループ数2維持、Opus再レビュー不要)。採否基準(経路別M): r3 M>=16/18、r5 M>=17/18、union M 18/18、hold-out 9/9、neg5 union M 3/3、欠落ID<=5%。未達経路はhighへ戻す(フォールバック=r3 high+r5 high+否定案a)。E2E実行は委任_15。

## 作業
Step 1: G arm 33 run(--plan g_arm --r3-reasoning medium --r5-mode full --r5-reasoning medium --negation-mode a)。見積→本番(--budget-jpy 35)→集計(経路別M、hold-out、neg5、HF-011、欠落ID率、NORMAL候補、Stage 1費用、reasoning tokens、worst、runs_over_3jpy、API失敗)。判定規則: 両合格=r3 medium+r5 medium、r5のみ未達=r5 high、r3のみ未達=r3 high、両方未達=フォールバック。任意でr5 lowのSC 18のみ追加(予算内5円以内)。
Step 2(0円): docs/pm/e2e_plan_open233_stage1_loop2_01.md作成(構成、rep30スイッチ突合、Recheck実装有無、instance最小構成と費用、shadow V4A費用測定、測定項目、STOP条件)。実装なし。
Step 3: summary loop2_trial_summary_03.md、REPORT §70、OPEN_ITEMS行進捗、REPORT_LEDGER 1行、ACTIVE_TASK(addしない)、commit/push。

## STOP条件
欠落ID 5%超/1 run ¥6超/見積+30%超/API失敗3 run超/想定外の大量API発火/hold-outでのunion M見逃し(フォールバックで説明不能な場合)。

## 事前指定Read一覧
loop2_trial_summary_02.md、stageA_aggregate.json、rep30_switch_values_01.md(全文)、opus_l2_review_open233_stage1_redesign_16.md(E2E|段階B|instanceのみ)、kpi_cost_baseline_open233_stage1_01.md(定義)、rep30_stage1_provenance_01.md §7、REPORT §69。

## 事前指定Grep一覧+追記位置・更新位置の手順
stageA: g_arm|r5_mode|reasoning|only|budget。runner: recheck|STAGE1_MODE|stage1_coverage_fresh|rewritten_regions|run_trial_deviation_check|STAGE4_ALLOWLIST|STAGE2_VERDICT_REUSE_NONBLOCKING|STAGE2_SIBLING_LOCATIONS_CYCLE1。rep30出力: switches|budget_state。追記位置: REPORT末尾§69の後に§70、OPEN_ITEMS本管理ID行、REPORT_LEDGER末尾。

## 実行コマンド全文
T-0 check: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file 本ログ --json-out 本ログ.md_check.json
プロセス確認: Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*er052_open233_stage1_stageA_01.py*' }
見積: python er052_open233_stage1_stageA_01.py --stage estimate --plan g_arm --r3-reasoning medium --r5-mode full --r5-reasoning medium --negation-mode a --out-dir er052_output\open233_stage1_loop2_garm_01 --estimate-out ...\estimate.json
本番: Start-Process python -u 同スクリプト --stage main --yes-run-paid --plan g_arm --r3-reasoning medium --r5-mode full --r5-reasoning medium --negation-mode a --out-dir ...garm_01 --budget-jpy 35(stdout/stderrをログへ)
集計: --stage agg --out-dir ...garm_01。テスト: python -m unittest er052_open233_stage1_coverage_checker_01_test_01.py
Git: git status --porcelain、明示add、commit、git push origin main、git log --oneline -1。

## SSOT追記先
REPORT §70、OPEN_ITEMS.md本管理ID行、REPORT_LEDGER.md末尾、loop2_trial_summary_03.md、e2e_plan_open233_stage1_loop2_01.md。

## Git(明示add対象・コミットメッセージ・trailer)
今回変更ファイルのみ明示add(ACTIVE_TASK/RESULT_PACKETは除外)。メッセージ: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: r5-V不採用、G arm 33 run(...)、E2E計画書(委任_14、¥...)。trailer: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>

## 報告(RESULT_PACKETの項目)
(1)結論8行以内 (2)表 (3)STOP有無 (4)SSOT・T-0・commit・push・raw URL・一覧外Read・確認/推測 (5)Fableへの論点(E2E起動可否、懸念)。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は委任元記載の通り。
