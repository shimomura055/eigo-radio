# 委任_18 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01(記録+実装+dry-run、¥0。有料E2Eは次の委任_19)

## 管理ID
`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01`(委任_18、¥0: 記録+実装+dry-run。有料E2Eは次の委任_19)。並行タスクなし。

## 性質/禁止事項
- 有料API禁止(dry-runはfixture・mock・保存出力のみ)。Production正式path(`er003*`/`er009*`/`er010*`/`er012*`/`er019*`)変更禁止。編集可は`er052_open233_*`と文書。既存prompt定数・gold・fixture・Safety-critical定義・Stage 2(承認済み構成)変更禁止。`git add -A`/`stash`/`amend`禁止。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込み2,500文字以下、長文はファイル間転写スクリプト。T-0: 委任ログ本ファイル全文保存(分割)、check PASS後commit。固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。
- 禁止(ユーザー指示): frozen Stage 1出力/過去判定の手動差替え/gold変更/Safety-critical候補の除外/Checker甘化/E2Eの一部をTrial artifactで代替して「E2E」と呼ぶこと。

## ユーザー決定(原文はDECISION_LOGへ一字一句逐語記録)
見出し: `## OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01(2026-10-05、ユーザー決定: Cost KPI例外承認・fresh E2E最終確認・到達最大VALIDATED)`
要旨(原文はDECISION_LOG): Cost KPI(+¥2/セット)のみ今回のOPEN-233について例外承認(理由1〜5)。Safety(重大Fact見逃し0)・Human Review/USER_DECISION_REQUIRED 0は不変。Cost未達は「将来の量産原価低減」としてOpen Itemに残す。これ以上のCost最適化Trialは行わず、現在のSafety優先構成でfresh E2E(fresh Stage 1→Stage 2→Rewrite/Recheck/Self-Recovery→最終出口)を原則20 run。Costは合否Gateにしないが実測必須(平均追加費用、Standard+Advanced 1セット換算、Rewrite/Recheck上振れ、worst run)。Waste(異常API発火・無限的retry・不要Rewrite)があればSTOP。到達最大=VALIDATED、Production未配線、ユーザーの正式採用判断を受ける。再発防止の自己確認8項目(fresh Stage 1/frozen・reuse・substitution無/Safety値=E2E値/Std+Adv両方/Human Review 0実測/Opus・Fable未解決警告/条件付き値とE2E値の混同無/Open Item漏れ無)。費用: 現管理ID残予算約¥98.29、E2E 20 runは約¥62見込み。ループ3は開始しない。

## Fable判断(前提)
- E2E構成: Stage 1=`coverage_union`(r3 medium+r5 high(full)+否定案a、F3常時、H1 fail-closed)。後段=rep30有効構成(`STAGE2_VERDICT_REUSE_NONBLOCKING`/`STAGE2_SIBLING_LOCATIONS_CYCLE1`/`STAGE4_ALLOWLIST`等をE2Eスクリプトで明示的にrep30値へ設定、`rep30_switch_values_01.md`突合済み)。Recheck=新Stage 1仕様(変更単位+前後1単位、Rewrite発生記事は出口前に3'-R全文1回; Opus#16レビュー済み設計)。shadow V4Aは省略(差し引き額は既存Productionログの実tokens×6-luna単価換算¥0.76〜0.91/セットを推計として使用。予算¥62枠を守るため)。
- 1セット単位: 20 run内にStandard/Advancedの両レベルが揃うinstance対を必ず含める(例: hormuz_run03_standard/advanced、meta_run03 std/adv等)。対が揃うinstanceは実測合算、揃わないinstanceは「1記事×2(推計)」と明示列分離。
- 到達最大=VALIDATED。Production変更なし。E2E後、Fable→Opus#18(条件C: Production採用提案前の独立レビュー)→ユーザー。

## 作業
A. 記録(¥0): (1)DECISION_LOGへ原文逐語(転写スクリプト)。(2)CURRENT_SPEC.md OPEN-233節へ最小追記(Cost KPIは2026-10-05ユーザー例外承認[本管理ID限定]、Safety/Human Review KPI不変、Stage 1プレースホルダ→Trial E2E最終確認中・Production未反映。既存記述を消さない)。(3)OPEN_ITEMS.md: 新規`OPEN-233-COST-REDUCTION-01`(Status OPEN、着手条件=ユーザー指示)、本管理ID行Status`IN_PROGRESS(E2E-ACCEPTANCE-01)`・Cost例外記録・分母=セット、独立Open ID化2件`OPEN-233-OF018-SUBREASON-01`と`OPEN-233-SPEC-STAGE1-PLACEHOLDER-01`。(4)ACTIVE_TASK.md(addしない)。
B. Recheck新仕様の実装(Trial runner、既定挙動不変、スイッチ`RECHECK_MODE`∈{legacy_v4a,coverage_union}): Rewrite後Recheck=変更単位(rewritten_regions)+前後1単位を3'-R+5-liteの対象にし、Rewrite発生記事は最終出口前に3'-R全文1回(欠落ID再実行・決定論検査・∪は同じ)。H1 fail-closed適用。単体テスト8〜10件。全テストPASS。
C. E2Eスクリプト`er052_open233_e2e_acceptance_01.py`(`--stage estimate|main --yes-run-paid|agg`、`--budget-jpy`、`--out-dir er052_output/open233_e2e_acceptance_01/`、skip existing、1 run ¥6超で停止、合計Guardrail、Waste検知: cycle上限超過/同一候補の再Rewrite/API retry連続3回超→当該run停止・waste_flags記録)。run jsonにprovenance(stage1_source=fresh、frozen=false、reuse=false、substitution=false、スイッチ全値、model/effort/prompt sha)を必ず記録。集計: Safety(gold 6+hold-out、M/D区分、E2E出口時点の見逃し)、Human Review/STAGE4出口数、Rewrite率、誤BLOCKING率、Stage 2発動率、cycle分布、費用(Stage別・/記事・/セット[実測対/推計×2列分離]・差し引き後純増・通常/上振れ・worst・¥3超一覧)、runtime、waste_flags。instance計画はe2e_plan §instanceの20 runを基本にStandard/Advanced対を含むよう調整し、計画表をe2e_plan_open233_stage1_loop2_01.md§追補に記録。
D. dry-run(¥0): fixture/mockで全20 runの経路が最終出口まで通ること、provenance欄・集計欄が埋まることを確認。`--stage estimate`で費用見積(mid/high)。
E. SSOT: REPORT_LEDGER.md1行、REPORT §72(E2E準備、未実行と明記)。commit/push(明示add)。

## 事前指定Read一覧
docs/pm/e2e_plan_open233_stage1_loop2_01.md(全文)、docs/pm/design_open233_stage1_coverage_impl_01.md(Recheck節)、docs/pm/opus_l2_review_open233_stage1_redesign_16.md(Grep Recheck|出口|全文)、er052_open233_stage1_stageA_01.py(estimate/main/agg構造の流用元)、er052_output/open233_kpi_recovery_02_offline_01/rep30_switch_values_01.md、docs/pm/cost_feasibility_open233_stage1_01.md §2。

## 事前指定Grep一覧+追記位置・更新位置の手順
runner: run_recheck|rewritten_regions|STAGE1_MODE|stage1_coverage_fresh|h1_rerun_stage1|F3_PRECHECK_ALWAYS|STAGE4_ALLOWLIST|STAGE2_VERDICT_REUSE_NONBLOCKING|STAGE2_SIBLING_LOCATIONS_CYCLE1|def run_instance|cycle。checker: def run_coverage|r3_precomputed|negation_mode|reasoning。CURRENT_SPEC.md: OPEN-233|Stage 1はA構成|プレースホルダ|Self-Recovery Production Flow。OPEN_ITEMS.md: 本管理ID行・OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01行・末尾の採番形式。DECISION_LOG末尾。REPORT末尾§71。

## 実行コマンド全文
T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_18.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_18.md_check.json
転写: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\append_decision_log_from_sources_01.py(引数はヘッダ参照)
テスト: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest C:\Users\tensh\eigo-radio\er052_open233_stage1_coverage_checker_01_test_01.py(+新規テストファイル)
dry-run: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_e2e_acceptance_01.py --stage dryrun --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01_dryrun
見積: 同 --stage estimate --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_e2e_acceptance_01 --estimate-out ...\estimate.json
Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。

## 報告(短く)
(1)結論8行以内、(2)表(instance計画: instance/レベル/群/n/セット対有無)、(3)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測、(4)Fableへの論点(E2E本番起動前の懸念)。
