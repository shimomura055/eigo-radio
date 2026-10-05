# 委任_07b(委任_07の再開。07のworkerはネットワークAPIエラーで途中終了)

管理ID: OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。並行タスクなし。
KPI provenance: 全てfresh、Stage 1のみ(E2Eではない=条件付き中間測定)。

## 最初にやること(状態確認、¥0)
1. 委任_07ログの存在確認(あれば仕様の正本)。
2. 段階A出力ディレクトリの既存run json・費用記録を確認し、生成済みrun件数(instance×sample別)と記録済み費用合計を報告。二重課金回避のため再実行はskip existing。
3. git status --porcelainで委任_07の未commit変更を確認、引き継ぐ(revertしない)。

## 仕様(委任_07と同一)
- 新Stage 1(coverage_union: 3'-R+5-lite、関係単位、決定論検査、F3、H1)をfresh実行(Stage 1のみ)、事前固定の採用基準で段階A合否判定。有料。
- 規模: SC 6 instance+B2_hormuz(監視)n=3、NORMAL 6 instance n=2、er009合成9種hold-out n=1=計42 run。sample-major順。--budget-jpy 70(Guardrail)。
- 採用基準(事前固定、変更禁止): (1)正式SC 6件(B3・A2A3-0・A4-0・A5-0・B4-a・B3-same@neg5)が2経路∪でn=3中3/3(経路別も報告)。(2)hold-out新規見逃し0。(3)欠落ID再実行後残存5%以下。参考: HF-011(監視)、NORMAL候補数/記事、決定論検査で戻した件数(理由別)、経路別検出率とr3xr5相関、費用/call・合計・worst run、runtime。
- 即時STOP(有料中): 1 run>6円/API連続失敗TrialAbort/例外2 instance以上/設計超のcall数。見逃し・候補過多は完走して集計。
- 禁止: コード変更は不具合修正のみ(Prompt・判定規則調整禁止)。Production変更禁止。gold・fixture変更禁止。N増し・再実行(skip existing再開除く)禁止。CURRENT_SPEC.md/PM_GOVERNANCE.md編集禁止。git add -A/stash/amend禁止。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込み2,500文字以下。
- 費用上限: 70円(Guardrail、T-3: 到達=自動STOPではない、暴走疑い時のみSTOP)。本管理ID枠約238円。有料前に--stage estimate概算、実測と並記(委任_07分含め累計)。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー指示(原文、該当部分)
13. 費用・作業方針
無駄な大規模Trialを先に行わない。各ループとも、¥0分析 → 小規模Safety/normal確認 → KPI見込み確認 → 必要なら広いE2E の順で進める。
既存Evidenceは積極的に再利用するが、E2E KPI確認時はfresh runを使う。単発¥3超は報告する。

## 作業
1. T-0: 本委任文を本ファイルに保存、check実行・結果記録。
2. 状態確認→--stage estimate(残run分)。
3. 段階A実行(skip existing再開)→--stage agg。
4. 集計・判定(基準(1)〜(3)機械判定+参考指標)。不合格なら見逃claimごとに経路別出力(単位ID判定・引用・flags)・決定論検査結果・欠落IDか判定誤りかを逐語記録、原因候補(判定方針/関係単位粒度/5-liteのfact対応/引用検査の厳しさ/非決定性)を分離(Prompt修正なし)。
5. (¥0)rep30スイッチ値一覧 er052_output/open233_kpi_recovery_02_offline_01/rep30_switch_values_01.md(07で作成済みなら確認、無ければ作成。CAUSAL_FLOOR/CAUSAL_FLOOR_VOCAB/STAGE2_SECOND_OPINION/enable_s1u/FLOOR_VERIFY_MODE/STAGE2_NORMAL_TWO_OF_TWO/STAGE2_DOWNGRADE_VERIFY/TIER0_G_L_ENABLED/RECHECK_BEFORE_AFTER_PAIRS/RECHECK_MERGE_UNRESOLVED/STAGE4_ALLOWLIST/LADDER_LOCATION_CARRY/REWRITE_REVERT_GUARD/SPAN_FALLBACK_CHAIN/JUDGE_ONLY_CYCLE_AFTER_CAP/LAST_RESORT_DELETE/MATERIALITY_BLOCKING_PIN/STAGE2_VERDICT_REUSE_NONBLOCKING/STAGE2_SIBLING_LOCATIONS_CYCLE1/ACTOR_GUARD_MODE/HANDOFF_MODE/JA_MODE/VS_SENTENCE_RESTORE/MODEL。なければ「記録なし」)。
6. SSOT: OPEN_ITEMS.md本管理ID行進捗、REPORT_LEDGER.md 1行、REPORT s67、ACTIVE_TASK.md(addしない)。
7. commit/push(明示add)。

## 性質/到達Status/禁止事項
性質: Trial(DEV)・有料。到達Status: 段階A合否判定まで。Production変更禁止。禁止事項は上記「仕様」の禁止欄のとおり。

## 事前指定Read一覧
er052_open233_stage1_stageA_01.py(全文可)。段階A出力(Pythonで一括集計、不合格claimの該当runのみ個別Read)。rep30 summary json(switches部分)・_rep30_full_01.py(Grep apply_kpi_trial_switches|runner\.|--reuse|--sibling)。

## 事前指定Grep一覧+追記位置・更新位置の手順
OPEN_ITEMS本管理ID行。REPORT `^## §66`直後に§67。REPORT_LEDGER末尾。

## 実行コマンド全文
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_07b.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_07b.md_check.json
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage estimate --normal-n 2
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage main --yes-run-paid --budget-jpy 70 --normal-n 2
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_stageA_01.py --stage agg

## 報告
結論8行以内、結果表、不合格時原因分離、rep30スイッチ表の所在、SSOT・commit・push・raw URL、Fableへの論点。
