# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_09(Stage 1b 記事1=streaming_price 有料実走+記事単位の集計・機械チェック。ユーザー承認#107(b)・2026-10-17指示DESIGN-FIX-1Bに基づく)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Trial専用harness(`er082_*`)の有料実行(Research/Ledger/B3のLLM+Web検索)。Production code・Prompt・Gateの変更0。
- 到達上限Status: `STAGE_1B_ARTICLE1_COMPLETE_PENDING_FABLE`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDには到達しない(Trial結果はProduction採用を意味しない)。
- 禁止: 記事2・3(openai_copyright/central_bank_mortgage)の実行(記事単位でFable確認を挟む=TRIAL_DESIGN_03 §4)/1b上限JPY493・Trial全体JPY1,040・日次JPY1,000の超過見込みでの続行/有料runの再起動(26節: 異常終了時は再起動せず状態報告)/Production runner・Prompt・Style・Verifierの変更/任意B・C・Stage 2/不要なResearch再生成/既存1a成果dir(`coffee_prices`・`inbound_tourism`)の変更(sha一致維持)/`run_summary.json`・`stop_check.json`等の既存集計の上書き(委任_08の再発防止: 新しい集計は別名で保存)。
- 固定ブロック: **E-1**(TRIAL_DESIGN_03 §4・§5・§8、STAGE_1A_CORRECTION_01、OPUS_REVIEW_B R-B1/B2/B5/B7/B9-1に整合。新仕様なし)/**D-1**(Trial専用経路のみ、Production到達経路なしを明記)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。commit直列)/**F-1**(費用は`er082_output/rlct_trial_01/raw_usage_log.jsonl`実測・`lib.cost_by_stage_tag`を出典に、実測/推定を区分。未確認の数字は出さない)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_09.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT9.md`、`docs/pm/ACTIVE_TASK.md`先頭へ新ヘッダをEdit/Writeで追記、旧ヘッダ保持、sed一括置換禁止)。
- 使用モデル: harness既定(1aと同一条件を維持するため変更しない)。報告に実model名を記載(25節: 1aとの比較条件維持が旧モデル使用の理由になる場合はその旨明記)。

## 承認・費用枠(Fable把握事実)
- ユーザー承認: #107(b)、原文`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md`(sha256 835f6972…2cdb)。上限: 1a 493/1b 493/任意A 54/全体 1,040。`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`。
- Trial累計(実測): 1a 212.80+任意A 10.88+1a補正 20.009=JPY243.7(出典 STAGE_1A_CORRECTION_01 / ACTIVE_TASK旧ヘッダ)。1b残枠=493。全体残=1,040−243.7=796.3。
- 当日(JST 2026-10-18)の1b以外の支出=**JPY0**(本日まだ有料実行なし。実行前に`raw_usage_log.jsonl`等で本日UTC/JST日付の行がないことを確認し、あれば実値を集計して`--other-spend-today-jpy`に渡す)。
- 記事1(streaming_price)の見積: 1aの記事単価(inbound M0 b3 8.465等、TRIAL_DESIGN_03 §5)から、M0/M0b/M0p/M1/M2/M3の合計を事前に算出して報告(期待値・最大値)。M0pはstreamingのみ(PLANどおり)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_DESIGN_03.md` §4・§5・§8(L42-76)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1A_CORRECTION_01.md`(実行手順・console保存の先例)
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT8.md`
- `C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py` L330-360(CLI引数)と`--plan`/`--article`の組合せ仕様(Grep `plan`)
- `C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\PLAN*.json`または同等のplan定義(1bの記事×方式一覧)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `OPEN-410`(確認パス)・`OPEN-409`(Verifier再現性)・`OPEN-411`(ラベル)→記事1の該当事実を各1行追記(新規起票はしない)。
- `DECISION_LOG.md`: 末尾に委任_09エントリ(事実のみ: 実行・費用・成立/未成立・STOP有無)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1B_RESULTS_01.md`: 新規作成(記事1節。記事2・3は後続委任で追記)。

## 作業(順序)
A. 事前(JPY0): T-0保存・check。dry-runで記事1のplan(方式一覧・stage)と費用ガード(`Budget`)の上限値(1b 493・全体1,040・日次1,000)が効いていることを確認(console保存)。1a成果dirのsha一覧を事前取得(`_sha_before_09.json`)。
B. 実走(有料、1回起動、foreground): 下記CLIを1回だけ起動し終了まで待つ。途中でBudgetガードSTOP・例外停止した場合は再起動せず、状態(方式・stage・費用)を報告。
C. 事後(JPY0): (1)記事1の方式別結果: 成立/UNRESOLVED(`unmet`内訳 REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMED)、`reselect_count`/`confirm_pass_count`/`b3_calls_after_initial`、確認パス`NOT_NEEDED_ALL_VERIFIED`の有無 (2)方式別費用(検索ツール呼出回数・クエリ数・LLM費用を別列、再選定/確認パス費用を分離、`cost_by_stage_tag`)と対M0/M0b/M0p削減率 (3)機械チェック: 選定FactにREJECTED混入0か、AMBIGUOUS選定があれば候補Ledgerで`[AMBIGUOUS…断定禁止]`が可視だったか、ラベル「【独立検証前の編集仮説】」の出現件数(方式別、記録のみ・Prompt不変) (4)Verifier判定の方式間差(同一FactのVERIFIED/AMBIGUOUS/REJECTED遷移表、M0p含む) (5)1a成果dirのsha再取得→`_sha_before_09.json`と一致(IDENTICAL)を確認 (6)aggregate再集計は既存出力を上書きせず`aggregate_1b_a1.md`等の別名で保存 (7)Trial累計・1b累計・当日累計を更新(全て出典付き)。人手品質評価(ブラインド等)は本委任ではしない(記事3完了後に別委任)。
D. 記録(commit): `er082_output/rlct_trial_01/streaming_price/`配下の追跡対象(1a先例に合わせる)、console、集計json/md、STAGE_1B_RESULTS_01.md、SSOT追記。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_09.md`
- dry-run: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --dry-run --plan 1b --article streaming_price --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --other-spend-today-jpy 0 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_09_dryrun_streaming.txt`(`--plan`と`--article`の併用可否はusageで確認し、不可なら実在する指定方法に置換して報告。dry-runは`raw_usage_log.jsonl`に追記しないことを確認)
- 実走: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --plan 1b --article streaming_price --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --other-spend-today-jpy 0 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_09_1b_streaming.txt`
- 集計: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er082_rlct_trial_01_aggregate.py --root C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\aggregate_1b_a1.md`(引数名はaggregateのusageに合わせ、実在する形に置換して報告。既存`aggregate.md`は上書きしない)
- 適合照合: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er082_rlct_trial_01_conform_check.py --root C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --article streaming_price --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\_conform_check_1b_a1.json`(同上)
- test: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er082_rlct_trial_01_test_01.py -q`
- secret scan: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在するscript名に置換)

## SSOT追記文(要点)
- OPEN-410: 「1b記事1(streaming_price): 確認パス発火 M2 x回/M3 y回、成立/未成立、費用JPY z(実測)」。
- OPEN-409/411: 記事1で観測されたVerifierばらつき・ラベル件数(事実のみ)。
- DECISION_LOG: 「2026-10-18 RLCT 委任_09: 1b記事1実走(実費JPY z、1b累計z/493、Trial累計243.7+z/1,040)。Production変更なし。判定はFable」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_09+_check.json、`er082_output/rlct_trial_01/streaming_price/**`(1a先例の追跡範囲)、console 2本、`aggregate_1b_a1.md`、`_conform_check_1b_a1.json`、`_sha_before_09.json`、STAGE_1B_RESULTS_01.md、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_09: Stage 1b 記事1(streaming_price)有料実走(M0/M0b/M0p/M1/M2/M3、確認パス込み、実費JPY z)+記事単位集計・適合照合+SSOT(1a成果sha IDENTICAL、Production変更なし)`
- `raw_usage_log.jsonl`等のappend-onlyログは既存の追跡方針に従う(1a先例と同じ扱い)。

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT9.md`)
4行: (1)整合(TRIAL_DESIGN_03 §4/§8との整合、plan一致)(2)Production到達経路=なし(er082のみ)(3)成果物とcommit sha、方式別 成立/未成立・費用・削減率・確認パス回数・ラベル件数・Verifier遷移、1b累計/493・Trial累計/1,040・当日累計/1,000、事前見積との差(4)撤去/残置(sha IDENTICAL結果、上書きなし)。`判定整合:` 重大NG有無。`判断候補:` [A]〜[D]またはなし。T-0 check結果。自己チェック: 1回起動/再起動なし/記事2・3未実行/上限内/Production・Prompt不変/既存集計未上書き。
