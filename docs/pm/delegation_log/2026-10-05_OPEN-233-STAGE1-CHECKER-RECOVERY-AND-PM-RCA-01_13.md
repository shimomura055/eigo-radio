# 委任_13 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 ループ2実装是正+限定Trial再測定(有料)

## 管理ID
OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(委任_13、並行タスクなし)

## 性質/禁止事項
- 有料。Guardrail本委任合計¥50(本管理ID累計¥80.13/枠¥238)。ステップ境界で見積+30%超なら次へ進まず報告。1 run ¥6超停止、¥3超全件記録。
- 禁止: Production正式path変更/prompt定数・gold・fixture・Safety-critical定義・Stage 2変更/git add -A・stash・amend/ACTIVE_TASK・RESULT_PACKET add。コード変更は本委任の是正(対象選定・raw保存)と不具合修正に限る。1回書込2,500字以下。
- 出力先: 新規dirのみ(er052_output/open233_stage1_loop2_r5v_fix_01/、..._r5v_cap_01/、..._garm_01/)。既存dir(open233_stage1_stageA_01、loop2_r5v_01、loop2_r5v_medium_01)は読取のみ、開始前後にgit status --porcelainが空であること。
- 有料run手順: Get-CimInstanceでstageAプロセス無し確認、Start-Process背景+ログ、60秒ポーリング、600秒無進捗は報告(killしない)、skip existing。
- T-0: 本ログ全文保存→check PASS確認後にcommit。委任_12ログのT-0 FAIL(placeholder 1件)も是正し再check。

## Fable判断(委任_12の照合結果)
委任_12のSTOPはr5-V対象選定の実装がOpus#17設計意図と異なっていたため。設計意図=r3のモデル判定がSUPPORTEDの単位+関係単位。実装はD適用後の最終状態==SUPPORTEDを対象にしたため、(a)Dで戻された単位(A4-0 S2.1 s1/s2)が検証されず、(b)保存r3が旧否定検査で保存されているため否定案aが反映されず交絡。Fableの基準「r5-V M>=17/18」は誤り(r5-VはCANDIDATE単位を対象にしないため構造上0になる)。正しい採否基準=(1)∪M 18/18 (2)r3 M見逃し単位(A4-0 s1/s2)をr5-V Mが検出 (3)hold-out 9/9 (4)neg5 ∪M 3/3 (5)r5-V検出能力(gold強制対象時のM検出)がhigh時r5 full 17/18と同等。設計変更ではなく実装是正でループ数2のまま。Opus再レビュー不要(内容不変)。

## 作業
Step 0(¥0): r5v_target_units是正(r3モデル判定SUPPORTED+関係単位、D後CANDIDATE化も含む)、model_verdict保存+保存r3からstatus文字列で復元、--reuse-r3-from時に否定案aを保存r3へ再適用、単体テスト追加、委任_12ログ是正、残留python(PID 36076)停止再試行。
Step 1(再測定、約¥6): r5-V low、保存r3(stageA 42 run)再利用、否定案a再適用、--out-dir ..._r5v_fix_01。集計: ∪M、A4-0 s1/s2のr5-V M、hold-out、neg5 ∪M、r5-V対象数/記事、NORMAL候補∪/記事、費用。基準(1)〜(4)。未達ならmedium(約¥10)で1回のみ。
Step 1b(能力テスト、約¥3〜5): SC 18 instance-run+hold-out 9でgold単位を強制対象に含めたr5-V low(新オプション--r5v-force-targets gold、Trial専用・測定用)、--out-dir ..._r5v_cap_01。基準(5): M検出>=17/18。未達ならmedium1回。lowもmediumも未達ならStep 2へ進まず報告。
Step 2(G arm、見積約¥26〜31): Step 1/1b合格のeffortで--plan g_arm 33 run fresh(r3 medium+r5-V+否定案a)、--out-dir ..._garm_01。集計: r3 M(対16/18)、r5-V M(救済数)、∪M、hold-out、neg5、HF-011、欠落ID率、NORMAL候補∪/記事(対24.0)、Stage 1費用/run(対¥1.51)、worst、runs_over_3jpy、API失敗。KPI見込み(推測明記): (iii)差し引き0主表示(感度¥0.12〜0.55)、Stage 2 fit ¥0.064+固定、Rewrite ¥0.31/回、BLOCKING率0.10/0.289併記、+¥2見込みYes/No/不明。Human Review 0はE2Eのみ判定可。
Step 3: summary(loop2_trial_summary_02.md)、REPORT §69追記(provenance=fresh Stage 1限定・E2Eではない)、OPEN_ITEMS本管理ID行、REPORT_LEDGER 1行、ACTIVE_TASK(addしない)、commit/push(明示add)。

## STOP条件
Step 1 mediumでも∪M<18/18、A4-0救済<2/2、hold-out見逃し、Step 1b mediumでもM<17/18、欠落ID 5%超、1 run ¥6超、見積+30%超、API失敗3 run超、想定外の大量API発火。

## 事前指定Read一覧
loop2_trial_summary_01.md(全文)、er052_open233_stage1_coverage_checker_01.py(Grep範囲)、loop2_r5v_01のA4-0 s1 run json、estimate_loop2_summary_01.md、kpi_cost_baseline_open233_stage1_01.md(定義のみ)、REPORT §68(形式)。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は委任元記載の通り。

## 事前指定Grep一覧+追記位置・更新位置の手順
checker: r5v_target_units|verify_supported|negation_mode|sources|model_verdict|SUPPORTED|apply_deterministic|r3_precomputed。stageA: reuse_r3|plan|g_arm|negation|force。テスト: r5v|verify_supported。追記位置: REPORT末尾§68の後に§69、OPEN_ITEMS本管理ID行、REPORT_LEDGER末尾。

## 実行コマンド全文(実行時追記)
T-0 check: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json
テスト: .venv\Scripts\python.exe -m unittest er052_open233_stage1_coverage_checker_01_test_01.py(72件PASS)
プロセス確認: Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*er052_open233_stage1_stageA_01.py*' }
Step 1 見積: python er052_open233_stage1_stageA_01.py --stage estimate --plan stageA --normal-n 2 --reuse-r3-from er052_output/open233_stage1_stageA_01 --r5-mode verify_supported --r5-reasoning low --negation-mode a --out-dir er052_output/open233_stage1_loop2_r5v_fix_01 --estimate-out er052_output/open233_stage1_loop2_r5v_fix_01/estimate.json --budget-jpy 15(--normal-n 2は保存r3の42 runに合わせる)
Step 1 本番: Start-Process python -u 上記の--stage main --yes-run-paid --budget-jpy 15(ログへリダイレクト)、集計は--stage agg
Step 1b: --plan cap --r5v-force-targets gold --reuse-r3-from(stageA) --r5-reasoning low --negation-mode a --out-dir er052_output/open233_stage1_loop2_r5v_cap_01 --budget-jpy 10
Step 2: --plan g_arm --r3-reasoning medium --r5-mode verify_supported --r5-reasoning {採用値} --negation-mode a --out-dir er052_output/open233_stage1_loop2_garm_01 --budget-jpy 40

## SSOT追記文
REPORT §69(Step 0是正内容・Step 1/1b/2の表・M/D区分・費用・見込み)、OPEN_ITEMS本管理ID行に進捗(委任_13 ...)、REPORT_LEDGER 1行。

## Git
git status --porcelain→明示add(今回変更ファイルのみ、ACTIVE_TASK/RESULT_PACKETは除外)→commit(trailer Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>)→git push origin main→git log --oneline -1。メッセージ: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: ループ2実装是正(r5-V対象=r3モデル判定SUPPORTED+関係単位・否定案a再適用)、再測定【...】(委任_13、¥...)

## 報告(RESULT_PACKET項目)
(1)結論8行以内 (2)表(Step 1/1b/2) (3)STOP有無 (4)SSOT・T-0・commit・push・raw URL・一覧外Read・確認/推測・コード修正要点 (5)Fableへの論点(E2Eへ進めるか/ループ3要否/構造的両立不能)。
KPI provenance: 本委任はfresh Stage 1限定の測定でE2Eではない。Opus台帳: 新規Opus指摘なし(OPUS_FINDINGS_LEDGER.md更新なし)。固定ブロックE-1/D-1/G-1/F-1は委任元記載の通り。

## 実行結果(実行時追記)
Step 1 low/medium、1b low/medium実施(出力dir: ..._r5v_fix_01、..._r5v_fix_medium_01、..._r5v_cap_01、..._r5v_cap_medium_01)。1bは両effortで基準未達のためStep 2未実施(STOP)。費用¥31.78。1b用の実装名は--r5v-force-targets gold(--help記載)。残留python PID 36076は停止成功。コード修正: r5v_target_units是正、reapply_negation_a、角括弧ID正規化、is_model_cand集計整合、--plan cap/--r5v-force-targets。
