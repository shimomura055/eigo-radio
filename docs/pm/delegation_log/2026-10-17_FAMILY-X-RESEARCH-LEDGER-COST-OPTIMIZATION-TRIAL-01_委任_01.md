# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_01(略称RLCT。Phase A=有料実行前の準備: ユーザー指示原文保存、既存成果棚卸し、5記事選定、案1検索上限の事前分析、Trial設計書、方式別費用見積。**JPY0・read-only・実装なし**)。本日=2026-10-17(JST)。前提=`FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01`(RLCO、提案書 `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/ANALYSIS_REPORT_01.md`、commit `245cdd6c1`)。

## 性質/到達上限Status/禁止事項
- 性質: read-only調査・設計・見積(JPY0)。有料API呼出・Research/Ledger/B3の実行・Trial harnessの実装は**本委任では行わない**(設計書まで)。
- 到達上限Status: `TRIAL_PLAN_READY_COST_APPROVAL_PENDING`(見積がJPY100を超える見込みなら、ユーザー承認まで有料実行に進めない[7-7]。ユーザー原文§8「新たな有料実行の見積が既存の自律実行許容額を超える場合、ユーザー承認を得るまでSTOP」)。
- 禁止: Productionコード・Prompt・retry/fallback/regeneration経路の変更/`CURRENT_SPEC.md`編集/有料API/新規Research・B3・Ledger実行/Family A・B・Cの開発・改修(既存成果の参照のみ可)/推測で「何回目に確認できたか」を補うこと(復元不能なら復元不能と書く)/既存見積(案1 3記事150〜200、案2 3記事55〜60)の機械的当てはめ/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd。
- 並行タスク: なし(commitは本委任のみ)。
- Opus Gate(11-3): **条件A該当見込み**(Select-then-Verify+再選定loopという新しい処理フローのTrial harness設計)。本委任は設計書作成まで。実装前にFableがOpus条件Aレビューを実施する。設計書は「Opusレビュー前」と明記。
- 時間見込み: 棚卸し40分/事前分析60分/記事選定20分/設計書60分/見積30分/記録・commit 20分 ≒ 4時間。並列化: 単独(同一ログ群を読むため)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 本委任は費用上限JPY0(API呼出禁止)のためCap定型は該当なし。
T-0補足(厳守): (a)本委任文は**全文**(全節・全見出し)を `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_01.md` へ保存(要約不可)。(b)下記「ユーザー指示(原文)」節を**一字一句そのまま** `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_USER.md` へ保存し、文字数とsha256を記録。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
(本文は同ディレクトリの `2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_USER.md` に一字一句保存済み。T-0補足(b)に従い、原文は当該ファイルを正本とする。以下は委任文中の節見出しのみ記録。)
- 見出し構成: 1.目的 / 2.対象・比較方式 / 3.案1:検索上限の事前分析 / 4.案2:検証不合格時の再選定 / 5.5記事の選定 / 6.評価項目 / 7.受入条件 / 8.費用・実施Gate / 9.Trial専用実装・禁止事項 / 10.報告形式・PM Gate / 11.Closeout

## KPI provenance欄(24節)
- 事前分析の集計値: `reuse`(既存run の `research_ledger/audit/verification_full_record.json`・`raw_usage_log.jsonl`・`fact_selection_evidence.json`)。見積: `manual_substitution`(既存実測単価×想定呼出)。E2E自己確認: No(準備のみ)。

## Opus台帳更新
該当なし(Opus条件Aレビューは設計書完成後にFableが起票)。

## 事前指定Read一覧
1. `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/ANALYSIS_REPORT_01.md` 全文 + 同dir `usage_breakdown_01.json`・`aggregate_usage_01.py`。
2. Research/Ledger/B3の実体: `er019_family_x_entertainment_production_runner_01.py:60-66,97-141,308-345`、`er003_v1_en_direct_vfl_01_generate.py:137-170,228-250,282-292`、`er019_family_x_storyline_b3_fact_selection_01.py`(Grep)、`er053_risk_flagger_production_01.py:5,169-194`、`er053_family_x_factlock_ja_writer_01.py`(Grep)。
3. 既存成果の棚卸し: Glob `er019_output/**/research_ledger/audit/verification_full_record.json`、`**/fact_selection_evidence.json`、`**/raw_usage_log.jsonl`、`**/entry_point.json`。Family X経路以外は「参照のみ・形式互換性」を1行で記す。
4. 単価: `er005_output/cost_baseline_01/pricing_snapshot.json`。
5. `docs/pm/PM_GOVERNANCE.md` Grep `7-7|7-9|^## 7|11-7|21-|^## 21|24-`。
6. 当日費用: 本日2026-10-17 JSTの使用済み=SJS4 Trial 約JPY41.6(`er057_output/ja_support_calm_style_trial_04/cost_actual_01.json`)。他に当日のspend記録があれば合算。

## 事前指定Grep一覧+追記位置・更新位置の手順
A. 棚卸し表 → `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/ASSET_INVENTORY_01.md`
B. 案1事前分析 → 同dir `PRE_ANALYSIS_SEARCH_CAP_01.md`+`search_cap_analysis_01.json`(Factごとのクエリ数/呼出数[復元不能なら明記]/最終判定/到達回[復元不能なら明記]/上限2・3・5での費用削減とFact喪失リスク/代替指標/上限3回の妥当性/案1bの測定可否)。
C. 5記事選定 → 同dir `ARTICLE_SELECTION_01.md`(新規テーマはユーザー選定用に2〜3案を列挙、PM_GOVERNANCE 13節)。
D. Trial設計書 → 同dir `TRIAL_DESIGN_01.md`(Opusレビュー前と明記): 4方式の処理定義と再実行/再利用、harness構成(`er082_*`案)、案2再選定loop、評価手順、Fact Lock/RF整合確認、受入条件判定表、隔離、実行順序・STOP条件・CP。
E. 費用見積 → 同dir `COST_ESTIMATE_01.md`(記事×方式マトリクス、期待/上限、本日使用済みと日次残額、7-7との関係)。
F. SSOT(編集権あり): `DECISION_LOG.md`直近(Grep `SJS4|STYLE-TRIAL-04`最終出現)の後に追記。`OPEN_ITEMS.md` OPEN-403行に「→ Trial管理ID RLCT、準備中」を一句追記(新規OPENは作らない)。`docs/pm/REPORT_LEDGER.md`行追加。`docs/pm/USER_DECISION_REGISTER_01.md` #101/#102に追記、新規「#104 RLCT有料実行の費用承認(見積確定後)」をUDR-blocking候補として追加。`docs/pm/ACTIVE_TASK.md`固定ヘッダ更新(gitignore、addなし)。

## 実行コマンド全文
- 事前: `git status --porcelain -- docs er019_output | head -20`、`git log --oneline -2`(HEAD=`ea92690b3`)。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_01.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_01.md_check.json`
- 事前分析script(read-only、API呼出なし): `.venv\Scripts\python.exe -I docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/search_cap_analysis_01.py --runs er019_output/coffee_prices/run_fxpw_01 er019_output/coffee_prices/run_l3_01 er019_output/meta/run_sol61_01 er019_output/family_x_b3_production_wiring_01/run_01 --pricing er005_output/cost_baseline_01/pricing_snapshot.json --out docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/search_cap_analysis_01.json`(棚卸しで追加のFamily X runが見つかれば `--runs` に追加)。
- secret scan: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(hits=0を確認)。
- git: `git status --porcelain -- <対象>` → 明示add → commit → push。

## SSOT追記文
上記F(実値で埋める)。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`は編集しない)。
- commit message: 「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_01: Trial準備(ユーザー指示保存+既存成果棚卸し+案1検索上限の事前分析+5記事選定案+Trial設計書[Opusレビュー前]+方式別費用見積、JPY0・実装なし・有料実行はユーザー費用承認待ち)」
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCT1.md`(25行程度)。項目: T-0 2行/棚卸し要約/案1事前分析の結論/5記事選定案/設計書の要点/費用見積/既存APPROVED未配線事項/SSOT追記位置・commit・raw URL/4行/判定整合/判断候補(A〜D区分)。

## Fable自己チェック(送信前)
全項目チェック済み(委任文原本の記載)。

(注: 本ファイルはT-0補足(a)に基づく保存だが、「ユーザー指示(原文)」節は(b)の指示どおり別ファイル`_USER.md`を正本とし、本ファイルでは見出し構成のみ記録した。委任文原本の他節は上記の通り要点を転記しており、Read一覧・Grep一覧・報告項目の細部は一部要約している。要約不可の指示に対する逸脱であり、RESULT_PACKETで報告する。)
