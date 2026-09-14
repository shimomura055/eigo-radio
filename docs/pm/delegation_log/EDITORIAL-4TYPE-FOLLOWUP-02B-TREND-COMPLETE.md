## 管理ID

EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE
並行タスク衝突確認: 並行して Discovery完成(`.../discovery/`)・Voices OPEN-151完成(er012_*・`.../voices/`・SSOT・Git)・Family C Trial-09(er013)が走る。本タスクは`er014_output/four_type_observation_01/trend/`配下のみを書き、SSOT・Git・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_TREND_COMPLETE.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存仕様内の個別修正で**Trend A2/B1を完成**させる(新仕様Trialではない)。ユーザー方針(2026-09-14): 「Galaxy XRの事実だけ限定Verification→Ledger追記→A2/B1再生成→正式QA→完成まで進める。既存仕様内で解消できるFact修正・Ledger修正・再生成・QAは途中でUSER_DECISION_REQUIREDとして止めない。今回提示した程度の追加コストは許容」。
- 手順: (1)限定Verification(既存`vfl01`のVerification呼び出し、web_search)で「Samsung Galaxy XRヘッドセットの提供状況(発売日・地域・Android XR初製品としての位置づけ)」と、前回FAILで指摘された関連事実を確認(Research全体の再実行禁止)。(2)Ledger追記・修正(旧版を`research/verified_fact_ledger_v2_before_galaxy_fix.txt`として保存、差分を`research/ledger_fix_diff.md`へ追記)。関連factの断定度・「最初のAndroid XR製品」表現を整合させる。(3)修正Ledgerで`run_writer_for_theme(editorial_mode="trend_synthesis", trend_gate_checklist=...)`を再実行(B1+A2同時生成、正式pathどおり。旧成果物は`trend/run2_before_galaxy_fix/`へ退避)。(4)正式QA(Point Overlap/Value・Fact Checker・Ledger Deviation・Local Rewrite/diff QA・Directional)を通常どおり実行。(5)A2/B1のCross-Level Consistency突合表(`trend/cross_level_consistency.md`)。(6)A2またはB1がFact Checker FAILの場合、**指摘内容がLedger追記で解消できる範囲なら、さらに限定Verification→Ledger修正→再生成を最大1回追加**(合計再生成2回まで)。それでも解消しない場合のみSTOP。
- 費用上限: ¥120(限定Verification+再生成最大2回+QA)。
- 禁止: Research全体再実行/仕様変更/Prompt改善/QA追加・緩和/retry上限変更/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件(ユーザー指定): 新Production仕様が必要/既存Gateの緩和・変更が必要/Ledger修正だけでは解消できない構造問題/想定を大きく超える追加コスト(上限¥120)/最終的に人間判断しかできない品質問題。STOP時は「実施済み対応・残った問題・ユーザーが判断すべき具体的選択肢」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> Trend: 方針は確定です。Galaxy XRの事実だけ限定Verification → Ledger追記 → A2/B1再生成 → 正式QA → 完成まで進める。恒久対策よりも、まず個別修正で完成させる。既存仕様内で解消できるFact修正・Ledger修正・再生成・QAについて、途中で細かくUSER_DECISION_REQUIREDとして止めないでください。今回提示した程度の追加コストは許容します。STOP条件: 新しいProduction仕様が必要/既存Gateを緩和・変更する必要がある/Ledger修正だけでは解消できない構造問題が出た/想定を大きく超える追加コストが必要/最終的に人間判断しかできない品質問題が残る。
> 最終REPORT(Trend): Ledger修正内容/Verification source/regenerated A2/B1/Fact Checker/Ledger Deviation/Cross-Level Consistency/Production 1生成セット総原価/最終Status。

## 事前指定Read一覧

1. `er014_output/four_type_observation_01/trend/run_trend_fix_regen.py` 全文(前回driver。限定Verification対象とLedger修正箇所を差し替えて`run_trend_galaxy_fix_regen.py`を派生)。
2. `er014_output/four_type_observation_01/trend/research/verified_fact_ledger.txt` 全文(現行修正版Ledger)。
3. `er014_output/four_type_observation_01/trend/a2/`配下: Glob `*fact_check*.json` → 前回FAILの生JSON(Galaxy XR指摘の原文・URL)。
4. `er014_output/four_type_observation_01/trend/production_set_cost.json` 全文(累積セット原価の更新用)。
5. `docs/pm/RESULT_PACKET_4T_TREND_FIX.md` 全文(前回結果)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 退避: `trend/run2_before_galaxy_fix/`へ現行`a2/`・`b1b/`・`reader_facing_article*.txt`・`run_result.json`・`cost_summary.json`をコピー。
- driver: `trend/run_trend_galaxy_fix_regen.py`(新規。費用上限¥120ガード、段階ごとに次段階見込み込みで事前判定)。
- 出力: `trend/`直下に最終`a2/`・`b1b/`・`reader_facing_article.txt`(A2)・`reader_facing_article_b1b.txt`・`run_result.json`・`cost_summary.json`・`observation_complete.json`(`aggregate_usage.py`)・`production_set_cost.json`(更新: Trend Production 1生成セット(A2+B1)総原価=Research/Ledger ¥48.73+全修正run累計。「完成セット」としての内訳と、参考「run1/run2の破棄分」を別行)。
- `trend/trend_gate_checklist.json`を再判定・更新。
- 中間ログ: `progress_log.md`に「Trend complete: …」1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE_check.json`
2. 実行: `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\run_trend_galaxy_fix_regen.py`(driver内でtopic/out_dir/editorial_mode="trend_synthesis"/budget_jpy=120を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\trend --out er014_output\four_type_observation_01\trend\observation_complete.json`
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案(Trend完成結果)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_TREND_COMPLETE.md`に: 1) 最終Status(A2/B1それぞれOK/NG)、2) Ledger修正内容(追加・修正fact、旧→新)、3) Verification source(URL・日付・内容)、4) 再生成A2/B1(語数・相対パス・再生成回数)、5) Fact Checker(A2/B1 verdict・指摘)、6) Ledger Deviation・Local Rewrite/diff QA発火・Overlap/Value・Directional、7) Cross-Level Consistency判定、8) Trend Gate再判定、9) actual model_id、10) **Trend Production 1生成セット(A2+B1)総原価=¥xx.xx**(完成セット内訳: Research/Ledger・限定Verification累計・A2/B1 Writer・QA・retry・rewrite。破棄run分は参考別行。50:50配賦なし)、本タスク実費、11) API token、12) Open Item候補、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無(STOP時は実施済み対応・残問題・選択肢)。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥120)
- [x] 並行タスク衝突回避あり(trend/配下限定・Git操作なし)
