# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_03(方式Bの検索込み追加検証[Production同一経路、mey、2 sample]+CTRL低下・Fact増の原因分析+Closeout v02更新+SSOT更新)。2026-10-20。
並行タスク衝突確認: 並行委任なし(委任_02完了 9c22750b3)。SSOT編集権: あり(`OPEN_ITEMS.md` OPEN-427行、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md` #127行、`docs/pm/REPORT_LEDGER.md`)。

## Fableの照合結果と決定(前提)
- 委任_02結果: 検索なし36 cellでBのみmey背景12/12保持(E0 0.75)だが、mey CTRL 0.5(E0 1.0)・muse Δfacts +2.5・coffee +0.083で基準未達=NOT_VALIDATED_CRITERIA_UNMET。A/C/D/E=REJECTED。検索込み(E0/A/D)は主体6/6保持(Production 0/6は再現せず)、背景はE0 0/10・A 2/10・D 2/7で安定して脱落。検索回数はA/Dで増えず。創作UNSUPPORTED 1件(地理付加「ダンマーム近郊」、A/D mey s2)。
- **Fable決定**: (1)Bの検索込み追加検証を実施(承認済みTrial範囲内の比較完了、約JPY35〜55、案件合算≈205〜225≤300、承認区分C)。(2)併せてBの**CTRL低下(mey 0.5)とFact増(muse +2.5)の原因**を検索なし結果の出力から分析(構造化欄がCTRL項目を押し出したのか、同一事実の分割か、粒度変化か)。これは採否判断の必須材料。(3)地理付加1件は「軽微・主体/動機/因果の創作ではない」として最終ラベルでは**REJECTED根拠にはしないが、Bを含む全方式で同種の付加が検索込みで再発するかを計数**し、採用時の検証観点として記録。(4)判定基準は不変(v02)。結果を見てから変更しない。
- 禁止: Production変更。追加Web検索はProduction経路内のもののみ。`git add -A/-u/-f`・amend・rebase・force push・stash。有料runの再起動は費用重複なしを確認できる場合1回まで(開示)。

## 性質/到達上限Status/禁止事項
- 性質: Trial追加検証+Closeout更新。
- 到達上限Status: `XRFR_TRIAL_CLOSEOUT_V02_PENDING_FABLE`。方式Bの最終ラベルはFable。Production採用はユーザーのみ。
- 費用/日次: 当日実費累計JPY480.41(修正後ツール値)/本委任見積JPY35〜55/承認区分C。
- T-3: 上限¥60(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。1 runの検索回数がProduction実績(20)の2倍超でSTOP。
- 時間見込み: 1.5〜2.5h(T-0 5分/B検索込み2 run 25分/出典取得・採点40分/CTRL・Fact増分析30分/Closeout・SSOT・報告30分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。保存はsession JSONLから抽出(管理ID行に`FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_03`を含む最初のAgent prompt)→`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_03.md`。
T-2: 本委任はTTSを伴わない。
T-3: 定型文は上記に記載済み。

## ユーザー指示(原文、該当部抜粋。全文=`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_USER.md`)
> 異なる改善アプローチを比較し、**1回のTrialで採否判断に足る結果を取得できるよう設計すること。** … **品質が同等なら、追加検索・追加LLM呼出が少なく、安価で速い方式を優先する。** … 全Factに一律の項目を強制したり、不要なFactを大量生成したりしない。… 改善候補はTrial終了時に `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` へ分類する。

## 作業
W1. B検索込み: `er085_research_fact_retention_trial_01_search_arm.py --variants B --topic mey --samples 2 --budget-jpy 55`(委任_02と同一採点規則・出典取得規則[拡張後]を適用)。検索回数・token・費用・時間、主体・背景の保持、CTRL、Fact数、創作フラグ→逐語照合(地理付加の再発計数を含む)。
W2. 原因分析(API 0): 検索なしBのmey CTRL 0.5・muse Δfacts +2.5について、出力claimを並べて(a)CTRL項目がどこへ消えたか(統合/省略/言い換えで採点漏れ)、(b)増えたFactが「同一事実の分割」「新規だが必要」「不要(周辺)」のどれか、を分類。採点規則の限界があれば区別して記す(規則は変えない)。
W3. Closeout v02: `TRIAL_CLOSEOUT_01.md`へ「§v02追記」節(B検索込み結果、原因分析、方式Bの候補Status再評価[基準v02に対し]、推奨の更新[推奨方式なし/B条件付き/Bを別Trialへ 等を根拠付きで]、Production採用に必要なユーザー判断の更新)。本文の履歴は残す。
W4. SSOT: OPEN-427行末・DECISION_LOG末尾・REGISTER #127行末・REPORT_LEDGER更新。ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `docs/research/FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/TRIAL_CLOSEOUT_01.md`・`SEARCH_ARM_RESULT_01.md`・`COMPARISON_RESULT_01.md`(全体)、`adjudication_02.json`: Grep `UNSUPPORTED|ダンマーム`
- `docs/pm/RESULT_PACKET_XRFR2.md`(全体)
- `er085_research_fact_retention_trial_01_search_arm.py`・`_eval.py`: Grep `def |argparse|variants`
- `er085_output/research_fact_retention_trial_01/`配下のB mey/muse出力json(Grep `-l '"variant": "B"'`→該当ファイル)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `^- OPEN-427`→行末追記。REGISTER: Grep `^- #127`→行末追記。DECISION_LOG末尾。REPORT_LEDGER: Grep `FAMILY-X-RESEARCH-FACT-RETENTION`→更新。`docs/pm/ACTIVE_TASK.md`先頭ヘッダ4行。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(index走査) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_03.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_03.md_check.json`
- B検索込み: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_search_arm.py --variants B --topic mey --samples 2 --out er085_output\research_fact_retention_trial_01\search_arm --budget-jpy 55`(先に`--dry-run`)
- eval: `.venv\Scripts\python.exe er085_research_fact_retention_trial_01_eval.py --out er085_output\research_fact_retention_trial_01 --report docs\research\FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01\COMPARISON_RESULT_02.md`
- 出典取得: `curl.exe -L -s -A "Mozilla/5.0" -o C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\xrfr3\src_01.html "<URL>"`
- 費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(origin/main HEADへff-only、到達確認)

## SSOT追記文
W4のとおり(実値)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: B検索込み結果+eval+原因分析+Closeout v02+委任文。msg: `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_03: 方式B検索込み2 run(実費JPY<v>)+CTRL低下/Fact増の原因分析+Closeout v02(B=<Status>)`
- commit 2: SSOT。msg: `… 委任_03: SSOT(OPEN-427/DECISION_LOG/REGISTER #127/REPORT_LEDGER)`
- trailer: `Delegation: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/委任_03`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XRFR3.md`: (1)T-0 (2)B検索込み結果表(検索回数・token・費用・時間・主体/背景保持・CTRL・Fact数・創作) (3)原因分析(CTRL/Fact増の分類) (4)方式Bの候補Status再評価と推奨更新(根拠) (5)Before/After具体Fact(検索込みB vs E0) (6)費用(本委任・案件合算・当日累計) (7)SSOT差分 (8)Git (9)判断候補(ラベル無し) (10)再開の有無 (11)一覧外Read理由。判定整合行1行。