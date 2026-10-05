# 委任_12 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 ループ2限定Trial(有料)

## 性質/禁止事項
- 委任_11(749da374)のスイッチを使う有料限定Trial(2ステップ)。Guardrail本委任合計¥60(本管理ID残≈¥174)。ステップ境界で見積と実績を照合、見積+30%超なら次へ進まず報告。1 run ¥6超停止、¥3超全件記録。
- 禁止: Production path変更/prompt定数・gold・fixture・Safety-critical定義変更/Stage 2変更/git add -A・stash・amend/ACTIVE_TASK・RESULT_PACKET add。コード変更は不具合修正最小限(報告明記)。1回書込2,500字以下。
- 出力先事故防止: 新規--out-dir(er052_output/open233_stage1_loop2_r5v_01/, ..._garm_01/)と--estimate-out明示。開始前後にgit status --porcelain er052_output/open233_stage1_stageA_01が空であること。
- 有料run手順: 起動前にGet-CimInstanceで重複プロセス確認、Start-Process背景+ログ、60秒ポーリング、600秒無進捗は報告(killしない)、skip existing。
## Fable判断
- ループ2主構成=Opus#17別案1(r3網羅+r5-V+否定案a)、Gは先行実験。採否基準=各経路M検出がhigh時(r3 M 16/18、r5 M 17/18、∪M 18/18、hold-out 9/9)より減らない。D検出はSafety合格数に入れない。
- KPI基準点(iii)。主表示は差し引き0、感度¥0.12〜0.55併記。安価な方から。
## 作業
Step 0(¥0): 見積確認、プロセス確認、stageA dir差分なし確認。
Step 1: r5-V on 保存r3(42 run、--reuse-r3-from stageA_01、--r5-mode verify_supported、--r5-reasoning low、--negation-mode a、mid≈¥14.5)。集計: 経路別M検出(SC 18 instance-run、hold-out 9、neg5)、∪M、A4-0のr5-V M(必須)、NORMAL候補∪、r5-V候補/記事、費用、worst、API失敗。判定: low M>=17/18かつhold-out 9/9かつA4-0 3/3 → low採用でStep 2。未達→medium再実行(≈¥20.8)。mediumも未達→Step 2へ進まず報告(構造/効果の切り分け所見)。
Step 2: G arm(--plan g_arm 33 run、fresh、--r3-reasoning medium、--r5-mode verify_supported、--r5-reasoning {採用値}、--negation-mode a、mid≈¥26〜31)。集計: r3 M(対16/18)、r5-V M、∪M、hold-out、neg5、HF-011、欠落ID率、NORMAL候補∪/記事(対24.0)、Stage 1費用/run(対¥1.51)、worst、API失敗、runs_over_3jpy。KPI見込み(推測明記): Stage 2 fit 1件¥0.064+固定、Rewrite ¥0.31/回、BLOCKING率0.10(n=2/20過小疑い)/0.289併記、(iii)差し引き0の平均追加費用(NORMAL/記事33 mix)再計算、+¥2以内Yes/No/不明。Human Review 0はE2Eでしか判定不能と明記。
Step 3: loop2_trial_summary_01.md(er052_output/open233_stage1_loop2_garm_01/)、REPORT §68(provenance=fresh Stage 1限定、E2Eではない)、OPEN_ITEMS本管理ID行、REPORT_LEDGER 1行、ACTIVE_TASK(add不可)。累計を枠¥238(既使用¥64.20)に対し記録。明示addでcommit/push。
## STOP条件
SC M低下(medium未達含む)/hold-out M見逃し/A4-0 r5-V M 3/3未達/欠落ID5%超/1 run ¥6超/見積+30%超/API失敗3 run超/想定外大量API発火。
## 事前指定Read一覧
(固定ブロックE-1/D-1/G-1/F-1/T-0/T-2/T-3は委任元記載の通り。)
## 事前指定Grep一覧+追記位置・更新位置の手順
estimate_loop2_summary_01.md、スクリプト--help、stageA_aggregate.json、kpi_cost_baseline_open233_stage1_01.md、design_open233_stage1_loop2_01.md §9、REPORT §67。Grep: plan|g_arm|reuse_r3|estimate_out|model_vs_deterministic|runs_over_3jpy|skip。
## 報告形式
(1)結論8行以内 (2)表 (3)STOP有無 (4)SSOT・T-0・commit・push・raw URL・一覧外Read・確認/推測・コード修正有無 (5)Fableへの論点(E2Eへ進めるか/ループ3要否/構造的両立不能)。
## 実行コマンド全文(実行時追記)
KPI provenance: 本委任はfresh Stage 1限定の測定でE2Eではない(provenance明記)。Opus台帳: 新規Opus指摘なし(OPUS_FINDINGS_LEDGER.md更新なし)。
T-0 check: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json
プロセス確認: Get-CimInstance Win32_Process | Where-Object CommandLine -like '*er052_open233_stage1_stageA_01.py*'
Step 1 見積: python er052_open233_stage1_stageA_01.py --stage estimate --plan stageA --reuse-r3-from er052_output/open233_stage1_stageA_01 --r5-mode verify_supported --r5-reasoning low --negation-mode a --out-dir er052_output/open233_stage1_loop2_r5v_01 --estimate-out er052_output/open233_stage1_loop2_r5v_01/estimate.json
Step 1 本番: Start-Process python -u er052_open233_stage1_stageA_01.py --stage main --yes-run-paid --plan stageA --reuse-r3-from er052_output/open233_stage1_stageA_01 --r5-mode verify_supported --r5-reasoning low --negation-mode a --out-dir er052_output/open233_stage1_loop2_r5v_01 --budget-jpy 25(stdout/stderr log付き)→ 集計: --stage agg(同引数)
medium再実行: 同上 --r5-reasoning medium --out-dir er052_output/open233_stage1_loop2_r5v_medium_01(見積→main→agg)
結果: low M 1/18・medium 0/18・A4-0 0/3 → Step 2未実施(STOP)。費用¥5.741+¥10.187。stageA_01 dirのgit差分: 開始前・終了後とも空。コード変更なし。
