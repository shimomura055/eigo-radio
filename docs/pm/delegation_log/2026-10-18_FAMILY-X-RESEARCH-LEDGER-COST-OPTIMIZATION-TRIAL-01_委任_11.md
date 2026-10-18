# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_11(Stage 1b 記事3=central_bank_mortgage 有料実走+記事単位集計+1b 3記事合計集計。Fable判定: 委任_10のG1 rc=5は並行MEYのreview_queue書込による整合性検査の誤検知=false-positive)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Trial専用harness(`er082_*`)の有料実行。Production code・Prompt・Gate・harnessコードの変更0。
- 到達上限Status: `STAGE_1B_COMPLETE_PENDING_FABLE`。VALIDATED等には到達しない。
- 禁止: 1b上限JPY493・Trial全体1,040・日次1,000の超過見込みでの続行/有料runの再起動(26節)/`er082_*.py`の変更(integrity対象からreview_queueを除外するコード修正もしない=Fable決定、記録のみ)/任意B・C・Stage 2/既存1a・記事1・記事2成果dirの変更/既存集計の上書き(委任_09/_10方式: 事前バックアップ→改名保存→復元)/人手品質評価(別委任)。
- 固定ブロック: **E-1**(TRIAL_DESIGN_03 §4・§5・§8、STAGE_1B_RESULTS_01 記事1・2節、RESULT_PACKET_RLCT9/10の置換(a)(b)(c))/**D-1**(Trial専用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agent(Family X MEY: `er019_output/middle_east_yemen_saudi`・`review_queue/post_en/middle_east_yemen_saudi__run_mey_01`、Family Z: `user_test/family_z_melos_02`・`er063_*`・`tools/user_test_page_*`)あり: `.git/index.lock`待ち再試行、自分のファイルのみadd(SSOTは委任_10と同じく自分の変更分のみstaged blobでcommit)、non-ffは`pull --ff-only`後再試行、conflictはSTOP)/**F-1**(`raw_usage_log.jsonl`実測・`lib.cost_by_stage_tag`)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_11.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT11.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記、sed禁止)。
- 使用モデル: harness既定(B3=gpt-6.1-sol、Verifier=gpt-6-luna、1a/記事1・2と同一条件)。

## Fable決定(記録用。再質問しない)
- 委任_10 G1(rc=5 `[STOP] integrity mismatch`)の判定: 差分16件が全て並行MEYの`review_queue/post_en/middle_east_yemen_saudi__run_mey_01/**`と`index.jsonl`であり、RLCT保護対象(1a+streaming_price)のsha IDENTICAL(241ファイル)、BudgetガードSTOPなし、全job COMPLETED、`stop_check` stop=false → **false-positive。記事2の結果は有効**。
- 記事3のGate(実走後の有効性判定)は次に読み替える: 「1回起動・再起動なし・BudgetガードSTOPなし・全job COMPLETED・RLCT保護対象(1a+記事1+記事2)のsha IDENTICAL」。rc=5が出た場合は、integrity差分の全件が`review_queue/**`配下(MEY由来)または`index.jsonl`であることを`integrity_*`出力で確認し、それ以外の差分が1件でもあればSTOP報告。確認結果を`_gate_1b_a3_11.json`に記録。
- harnessコードは変更しない(integrity検査の対象見直しはOPEN-410へ「Trial後の改善候補」として1行記録のみ)。

## 承認・費用枠(Fable把握事実)
- ユーザー承認#107(b)、`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`。上限1b 493/全体1,040。
- 実測累計(委任_10): 1b 160.866/493、Trial 404.557/1,040。当日217.40/1,000(RLCT 160.866+非RLCT 56.53)。
- 記事3見積: 期待約70〜90、最大185。1b累計見込み ≤ 345.9 ≤ 493。
- `--other-spend-today-jpy`: 実行直前に`daily_dev_cost_01.py`(委任_10と同じ方法)で当日の非RLCT実績を再集計して渡す(MEYが再生成中のため増えている可能性あり。未取得なら保守的に180)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT10.md`
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1B_RESULTS_01.md`
- `C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\_gate_1b_a2_to_a3_10.json`
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_DESIGN_03.md` §4・§8(L42-76)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `OPEN-410`→記事3事実+「integrity検査のreview_queue誤検知(委任_10)=Trial後の改善候補」1行。Grep `OPEN-409`・`OPEN-411`→記事3の事実。
- `DECISION_LOG.md`: 末尾に委任_11エントリ(Fable判定false-positive、記事3結果、1b合計)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `STAGE_1B_RESULTS_01.md`: 記事3節+「1b合計(3記事)」節(方式別費用・対M0削減率・検索呼出・確認パス/再選定回数・ラベル件数・unmet内訳・Verifier遷移)+「新設計列の5記事暫定合計」(Coffee M2/M3+inbound M2c/M3c+1b 3記事、旧inbound M2/M3は参考行、R-B7)。

## 作業(順序)
A. T-0。`_sha_before_11.json`(1a 2記事+streaming_price+openai_copyright)。当日非RLCT実績の再集計。dry-run(記事3、`_dryrun_11`、`raw_usage_log.jsonl` sha不変確認)。
B. 記事3実走(1回起動、foreground)→Gate(読み替え版)判定→`_gate_1b_a3_11.json`→記事単位集計(`aggregate_1b_a3.*`、`_conform_check_1b_a3.json`、`_analysis_1b_a3.json`、固定名出力の改名保存+復元)→commit 1→push。
C. 1b合計節・5記事暫定合計・`_sha_after_11.json` IDENTICAL確認→SSOT→commit 2→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_11.md`
- dry-run: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --dry-run --article central_bank_mortgage --method M0,M0b,M1,M2,M3 --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\_dryrun_11 --other-spend-today-jpy 180 2>&1 | tee C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_11_dryrun_central.txt`
- 実走: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --article central_bank_mortgage --method M0,M0b,M1,M2,M3 --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --other-spend-today-jpy <当日非RLCT実値> 2>&1 | tee C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_11_1b_central.txt`
- 集計: 委任_09/_10と同じ一時rootコピー方式で `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er082_rlct_trial_01_aggregate.py --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\aggregate_1b_a3.md`(実引数は先例に合わせる)。3記事合計は`streaming_price`+`openai_copyright`+`central_bank_mortgage`を一時rootへコピーして`aggregate_1b_all.md`。
- test: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er082_rlct_trial_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-410: 「1b記事3: …(費用・成立・確認パス)。1b合計 x/493。integrity検査のreview_queue誤検知はTrial後の改善候補(コード不変)」。
- DECISION_LOG: 「2026-10-18 RLCT 委任_11: 委任_10 G1 rc=5をfalse-positiveと判定(根拠)。記事3実走(実費)。1b完了、Trial累計/1,040。人手評価・最終分類は次委任。Production変更なし」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 委任_11+_check.json、`er082_output/rlct_trial_01/central_bank_mortgage/**`(先例の追跡範囲)、console、`aggregate_1b_a3.*`、`_conform_check_1b_a3.json`、`_analysis_1b_a3.json`、`_gate_1b_a3_11.json`、`_sha_before_11.json`、`*_11_1b_a3.json`。msg: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_11: Stage 1b 記事3(central_bank_mortgage)有料実走(実費JPY x)+集計・適合照合+Gate判定(委任_10 G1=review_queue誤検知)`
- commit 2: STAGE_1B_RESULTS_01.md、`aggregate_1b_all.*`、`_sha_after_11.json`、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `… 委任_11: Stage 1b 3記事合計+新設計列5記事暫定合計+SSOT(1b累計JPY y/493、Trial累計z/1,040、Production変更なし)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT11.md`)
4行: (1)整合(2)Production到達経路=なし(3)成果物とcommit sha、記事3の方式別結果、Gate判定値(rc、integrity差分の内訳)、1b合計表、5記事暫定合計(新設計列)、1b累計/493・Trial累計/1,040・当日累計/1,000(4)撤去/残置(sha IDENTICAL)。`判定整合:` 重大NG有無。`判断候補:` [A]〜[D]またはなし。T-0 check。自己チェック: 1回起動/再起動なし/上限内/harness不変/既存集計未上書き。
