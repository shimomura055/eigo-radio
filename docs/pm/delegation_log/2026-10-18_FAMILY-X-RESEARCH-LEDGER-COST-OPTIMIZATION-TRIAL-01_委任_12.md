# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_12(任意A=故障注入の未実施分(inbound_tourism / streaming_price)を承認枠内で実行+委任_11のcommit 2確認+集計。有料、任意A上限JPY54の残枠内)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Trial専用harness(`er082_*`)の有料実行(任意A: 誤Fact注入時の検出漏れ確認、{上限なし, 上限付き})。Production・Prompt・Gate・harnessコードの変更0。
- 到達上限Status: `OPTIONAL_A_COMPLETE_PENDING_FABLE`。VALIDATED等には到達しない。
- 禁止: 任意A上限JPY54(既使用Coffee 10.882→残43.118)・Trial全体1,040・日次1,000の超過見込みでの続行(Budgetガードに任せず事前見積で超過見込みならSTOP)/任意B・C・Stage 2/有料runの再起動(26節)/`er082_*.py`変更/既存成果dir(1a・1b・任意A Coffee)の変更/既存集計の上書き(バックアップ→改名保存→復元)/Productionや元データ(Research Ledger原本)の変更/人手品質評価(次委任)。
- 固定ブロック: **E-1**(任意Aの設計=TRIAL_DESIGN_02の任意A節・STAGE_1A_RESULTS_01 §任意A(L152付近)・lib PLAN/STAGE_CAPS("optA")に整合。Coffee実施済み分は再利用し再実行しない)/**D-1**(Trial専用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**ユーザー指示「commitを伴う作業は同時に1件のみ」**: 現在他のcommit作業は走っていない。commit直前に`git status --porcelain`で他のstagedがないことを確認)/**F-1**(`raw_usage_log.jsonl`実測・`lib.cost_by_stage_tag`)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_12.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行、要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT12.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記、sed禁止)。
- 使用モデル: harness既定(B3=gpt-6.1-sol、Verifier=gpt-6-luna、同一条件維持)。

## 承認・費用枠(Fable把握事実)
- ユーザー承認#107(b)+任意A維持(原文§7: 「実施済みCoffeeの結果は再利用/未実施の範囲は承認済み設計・費用枠内で実行/誤Factの検出漏れを確認/Productionや元データを変更しない」)。`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`。
- 実測累計(委任_11): 1b 212.123/493(完了)、任意A 10.882/54、Trial 455.814/1,040。当日 約291.8〜348.4/1,000(重複計上の可能性あり。実行前に`daily_dev_cost_01.py`で再集計し、RLCT以外の実値を`--other-spend-today-jpy`に渡す)。
- 任意A残枠=JPY43.118。Coffee実績(10.882=3件×{上限なし,上限付き})から、inbound+streamingの2記事分見込み≈22(最大約30)。2記事分が残枠に収まらない見込みなら、inboundのみ実行し理由を記録。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1A_RESULTS_01.md` L145-165(任意A Coffeeの実施内容・結果形式)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_DESIGN_02.md` 任意A節(Grep `故障注入`)
- `C:\Users\tensh\eigo-radio\er082_rlct_trial_01_lib.py` L36-80(STAGE_CAPS_JPY・PLAN・optA定義)と`er082_rlct_trial_01_run.py` L330-400(`--stage optA`の起動方法)
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT11.md`(commit 2の状態確認)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `git log --oneline -5` と `git status --porcelain -- docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1B_RESULTS_01.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md` で委任_11 commit 2(SSOT+結果節)が済んでいるか確認。未commitなら本委任のcommit 1として先に委任_11分をcommit(msg: `… 委任_11: Stage 1b 3記事合計+新設計列5記事暫定合計+SSOT(1b累計JPY212.123/493、Trial累計455.814/1,040、Production変更なし)`)。
- `OPEN_ITEMS.md`: Grep `OPEN-410`→任意A結果1行。
- `DECISION_LOG.md`: 末尾に委任_12エントリ。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/OPTIONAL_A_RESULTS_01.md`: 新規(Coffee再利用+inbound+streamingの故障注入結果表: 注入Fact/方式(上限なし・上限付き)/検出(REJECTED化)有無/検出漏れ/費用)。

## 作業(順序)
A. T-0。委任_11 commit 2確認(未なら先にcommit)。`_sha_before_12.json`(1a・1b・任意A Coffee)。当日費用再集計。dry-run(`_dryrun_12`、raw_usage_log sha不変)。事前見積と残枠43.118の照合。
B. 任意A実走(inbound_tourism→streaming_price、各1回起動、foreground。2記事を1起動で回せる実装ならそれでよい)。Budgetガード・rc・integrity(rc=5がMEY review_queue由来のみなら委任_11と同じ読み替え、それ以外の差分があればSTOP)。
C. 集計: 注入Factごとの検出結果(上限なし vs 上限付き)、検出漏れ件数、費用(`cost_by_stage_tag`)、Coffeeと合わせた任意A合計/54。固定名出力の改名保存+復元。`_sha_after_12.json` IDENTICAL。
D. OPTIONAL_A_RESULTS_01.md・SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_12.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_12.md_check.json`
- dry-run: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --dry-run --stage optA --article inbound_tourism --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\_dryrun_12 --other-spend-today-jpy 350 2>&1 | tee C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_12_dryrun_optA.txt`(任意Aの実引数(`--stage optA`/`--method`等)はrun.py usage・Coffee実施時のconsole(`er082_output/rlct_trial_01/console_*optA*`等)に合わせて置換し、置換内容を報告)
- 実走: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --stage optA --article inbound_tourism --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --other-spend-today-jpy <当日非RLCT実値> 2>&1 | tee C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_12_optA_inbound.txt`、同様に `--article streaming_price`(console `console_12_optA_streaming.txt`)
- test: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er082_rlct_trial_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-410: 「任意A(inbound/streaming)実施: 注入n件、検出漏れm件、費用JPY x、任意A合計y/54。Trial累計z/1,040」。
- DECISION_LOG: 「2026-10-18 RLCT 委任_12: 任意A完了(結果要旨)。残=人手品質評価・最終分類(次委任)。Production変更なし」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_12+_check.json、`er082_output/rlct_trial_01/<任意A成果dir>/**`(Coffee任意Aと同じ追跡範囲)、console、`_sha_{before,after}_12.json`、OPTIONAL_A_RESULTS_01.md、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_12: 任意A(故障注入)inbound/streaming実走(実費JPY x、任意A合計y/54)+結果表+SSOT(Production変更なし)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT12.md`)
4行: (1)整合(任意A設計との一致、Coffee再利用)(2)Production到達経路=なし(3)成果物とcommit sha、注入Fact別の検出結果(上限なし/上限付き)、検出漏れ、費用、任意A合計/54・Trial累計/1,040・当日/1,000(4)撤去/残置(sha IDENTICAL)。`判定整合:`・`判断候補:`・T-0 check・自己チェック(1回起動/再起動なし/残枠内/harness不変/既存集計未上書き/他commit作業なし)。
