# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_06(Stage 1aの人手判定・再現性分析: B3構成差3段階のブラインド判定、品質一対比較、中心FactのAMBIGUOUS断定判定、Verifier再現性の整理。**JPY0・有料API禁止**。Stage 1bは別日・未着手)。本日=2026-10-17(JST)。前委任=委任_05(commit `61e5ad3e1`/`6530a0ff5`、Stage 1a完了JPY212.80+任意A 10.88)。

## 性質/到達上限Status/禁止事項
- 性質: 保存済みTrial出力のread-only評価+評価記録の作成+SSOT追記+commit。
- 到達上限Status: `STAGE_1A_EVALUATED_PENDING_FABLE`。
- 禁止: 有料API/Trial run再実行/Production code・Prompt変更/`er082_*`のロジック変更(aggregateのキャプション「SYNTHETIC(stub)」固定文言の修正=実測/stubを出力元から判定して表示する最小修正のみ可)/Stage 1b・任意A(inbound/streaming)の開始/BAPE有料実行/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd。
- 並行タスク: なし(commitは本委任のみ)。
- Opus Gate: 非該当(評価作業)。重大判定・不一致が出た場合はFableがOpus要否を判断。
- 時間見込み: 2時間、単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1/D-1/G-1/F-1: 標準。T-0: 委任文を本pathへ全文保存しcheck_delegation_prompt.pyを実行しRESULT_PACKETへ1行記録。T-2: TTSなし。T-3: JPY0のためCap定型該当なし。pythonは`.venv\Scripts\python.exe`。

## ユーザー指示(原文)
保存済み: `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_APPROVAL_USER.md`(sha b04eb8e1…)§8「各記事・各方式について…最終B3構成の差/ストーリーの品質・一貫性…削減額と品質差を分けて評価」、原指示 `..._USER.md`(sha e6bc729b…)§6「B3の構成差は3段階…構成差の大きさと品質の良し悪しは別々に判定…自然な生成ばらつきと方式変更による差を混同しない」。

## KPI provenance欄(24節)
評価対象=`reuse`(Stage 1a実測出力)。判定=人手(Sonnet机上、ブラインド)。E2E自己確認: No。

## Opus台帳更新(11-5)
OF-RLCT-R-04/07/10/13: Stage 1a実測で検証できた部分を `EVIDENCED` へ。

## 事前指定Read一覧
1. docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1A_RESULTS_01.md 全文
2. TRIAL_DESIGN_02.md: Grep `4-4|ブラインド|一対比較|軽微|中程度|重大|事前登録|中心Fact`
3. er082_output/rlct_trial_01/<article>/<method>/ (article∈{coffee_prices, inbound_tourism}, method∈{M0,M0b,M0p,M1,M2,M3}): storyline_b3/selected_brief.md, fact_selection_evidence.json, research_ledger/verified_fact_ledger.txt, _inputs/。M0pはLedgerのみ。
4. PRE_ANALYSIS_SEARCH_CAP_01.md / ANALYSIS_REPORT_01.md の Coffee F12/F07/F16/F17、inbound F05/F12 (Grep)。

## 事前指定Grep一覧+追記位置・更新位置の手順
A. ブラインド判定準備: scratchpad rlct_eval/ に各記事のB3成果(M0/M0b/M1/M2/M3)をラベル(Coffee-α〜ε等、順序ランダム、blind_key.jsonは判定終了まで開かない)で並べる。推測可能な場合は記録(ブラインド限界)。
B. B3構成差3段階判定(M0基準、M0b含む): 軽微/中程度/重大。根拠1〜2行。事前登録ルール: 「M0とM0bの差が中程度以上の記事では、方式差が中程度以下なら方式効果と認めない」。
C. 品質一対比較(M0 vs 各ラベル、面白さ/一貫性/事実との整合、各 良い/同等/悪い+理由1行)。事実整合は選定Factのverdictとストーリー行の断定有無を主根拠に。
D. 中心FactのAMBIGUOUS断定判定(R-07): STAGE_1A_RESULTS_01 §5の対象(inbound M1/M2/M3のF05、F06ほか、Coffee側該当)について断定/留保あり/言及なしを原文引用付きで判定。M0/M0bも記録。
E. Verifier再現性の整理(事実整理): M0pとM1のverdict差、M0(10-08〜10-16)との差をFact別表に(Coffee F02/F12/F16/F17、inbound F05/F12必須)。inbound F12のREJECTED→VERIFIED昇格(M1)がM0pでも起きたかをverification_notes引用付きで明確化。推測で原因断定しない。
F. 判定終了後blind_key.jsonを開き復元→ docs/research/.../STAGE_1A_EVAL_01.md(§1手順と限界/§2構成差/§3品質/§4中心Fact/§5 Verifier再現性/§6受入条件暫定判定/§7 1b所見[判断はFable])。
G. aggregate固定キャプション最小修正(raw_usage_log行有無またはdry_runフラグでMEASURED/SYNTHETIC切替)、test1件追加、既存17件PASS維持、再集計で数値不変をdiff確認。
H. SSOT: DECISION_LOG.md末尾、OPEN_ITEMS.md OPEN-403、docs/pm/REPORT_LEDGER.md行、docs/pm/OPUS_FINDINGS_LEDGER.md R-04/07/10/13 EVIDENCED、docs/pm/ACTIVE_TASK.md(addなし)。

## 実行コマンド全文
- T-0: .venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json
- test: .venv\Scripts\python.exe run_project_regression.py --pattern "er082_rlct_trial_01_test_*.py"
- 再集計: .venv\Scripts\python.exe er082_rlct_trial_01_aggregate.py --out er082_output/rlct_trial_01 --title "Stage 1a (measured)"
- secret scan: .venv\Scripts\python.exe tools\secret_scan_01.py
- git: 明示add→commit→push(work/post-merge-01 → crbn git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main → 主dir git merge --ff-only origin/main)。

## Git
明示add: STAGE_1A_EVAL_01.md、er082_rlct_trial_01_aggregate.py、er082_rlct_trial_01_test_01.py、er082_output/rlct_trial_01/aggregate*.md|json、delegation_log本委任2件、SSOT4件。blind_key.json等はscratchpad。
commit message: 「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_06: Stage 1a人手評価(B3構成差3段階ブラインド・品質一対比較・中心FactのAMBIGUOUS断定・Verifier再現性整理)+aggregateキャプション修正+SSOT(JPY0、1bは別日)」

## 報告
docs/pm/RESULT_PACKET_RLCT6.md(20行程度): T-0/ブラインド実施状況と限界/構成差表要約/品質一対比較要約/中心Fact断定結果/Verifier再現性/受入条件暫定判定表/1b所見(判断はFable)/aggregate修正・test結果/SSOT位置/commit hash・push・raw URL/4行/判定整合行/判断候補。
