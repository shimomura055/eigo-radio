# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_10(Stage 1b 記事2=openai_copyright → 記事3=central_bank_mortgage の有料実走+記事単位集計・機械チェック。記事間はFable事前指定の機械Gateで自動継続)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Trial専用harness(`er082_*`)の有料実行。Production code・Prompt・Gateの変更0。
- 到達上限Status: `STAGE_1B_COMPLETE_PENDING_FABLE`(3記事完了)。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDには到達しない。
- 禁止: 1b上限JPY493・Trial全体JPY1,040・日次JPY1,000の超過見込みでの続行/有料runの再起動(26節)/Production runner・Prompt・Style・Verifierの変更/harnessコード(`er082_*.py`)の変更(委任_09の置換方式を踏襲し、コード修正はしない)/任意B・C・Stage 2/既存1a・記事1成果dirの変更(sha一致維持)/既存集計(`aggregate.md`・`run_summary.json`・`stop_check.json`・`integrity_*`)の上書き(委任_09と同じく事前バックアップ→改名保存→復元)/人手品質評価(別委任)。
- 固定ブロック: **E-1**(TRIAL_DESIGN_03 §4・§5・§8、STAGE_1B_RESULTS_01 記事1節、RESULT_PACKET_RLCT9の置換(a)(b)(c)に整合)/**D-1**(Trial専用、Production到達経路なし)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`)/**F-1**(`raw_usage_log.jsonl`実測・`lib.cost_by_stage_tag`を出典。未確認の数字は出さない)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_10.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT10.md`、ACTIVE_TASK.md先頭へ新ヘッダをEdit/Writeで追記、旧ヘッダ保持、sed禁止)。
- **並行作業注意**: 別agentがFamily X新記事(`er019_output/middle_east_yemen_saudi`、`er019_mey_*`)とFamily Z試聴ページ(`user_test/family_z_melos_02`、`er063_*`、`tools/user_test_page_*`)を並行中。ACTIVE_TASK.mdは編集直前に再読し自分のブロックのみ先頭追記。gitは自分のファイルのみadd、`.git/index.lock`は最大5分待ち再試行、commit直前に他のstagedがないことを確認、pushがnon-ffなら`git pull --ff-only`後に再試行(force禁止)、conflictはSTOP報告。
- 使用モデル: harness既定(B3=gpt-6.1-sol、Verifier=gpt-6-luna、1a/記事1と同一条件維持のため変更しない)。

## 承認・費用枠(Fable把握事実)
- ユーザー承認#107(b)、`--paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040`。上限: 1b 493/全体 1,040。
- 実測累計(委任_09報告、出典 STAGE_1B_RESULTS_01): 1b 86.128/493、Trial 329.8/1,040。記事1実費86.128(期待120・最大185の範囲内)。
- 当日(10/18 JST)の他支出: RLCT以外にFamily X新記事(上限180)が並行中。実行直前に`er019_output/middle_east_yemen_saudi/run_mey_01/cost.json`等から当日の非RLCT実績を集計し、`--other-spend-today-jpy <実値>`に渡す(未取得なら保守的に180を渡す)。日次1,000内であることを確認。
- 記事2・3の方式: PLAN["1b"]どおり(M0,M0b,M1,M2,M3。M0pはstreamingのみ=記事2・3では実行しない)。

## Fable決定(記事間Gate。全て満たせば記事3へ自動継続、1つでも満たさなければ記事3を実行せずSTOP報告)
G1 記事2が1回起動・rc=0・BudgetガードSTOPなし・再起動なし。
G2 記事2の全方式がCOMPLETED(UNRESOLVEDがあっても`unmet`が記録され確定ファイル無しで安全側なら可。ただしUNRESOLVEDが2方式以上なら STOP)。
G3 記事2実費 ≤ JPY185(記事1の最大見積)。かつ 1b累計(86.128+記事2) + 記事3最大見積185 ≤ 493。
G4 REJECTED選定混入0、D1適合PASS(M2/M3)。
G5 1a・記事1成果dirのsha IDENTICAL。
G6 当日累計(RLCT+非RLCT実績)+記事3最大185 ≤ 1,000。
Gate判定結果は`_gate_1b_a2_to_a3_10.json`に記録してからcommitし、その後に記事3を起動する。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT9.md`(置換(a)(b)(c)の実手順を踏襲)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\STAGE_1B_RESULTS_01.md`(記事1節の書式に合わせて記事2・3節を追記)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_DESIGN_03.md` §4・§5・§8(L42-76)
- `C:\Users\tensh\eigo-radio\er082_rlct_trial_01_lib.py` L70-85(PLAN["1b"])

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `OPEN-410`・`OPEN-409`・`OPEN-411`→記事2・3の事実を各1行追記。
- `DECISION_LOG.md`: 末尾に委任_10エントリ(記事2・3の実行・費用・成立/未成立・Gate判定・STOP有無)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `STAGE_1B_RESULTS_01.md`: 記事2節・記事3節・1b合計節(3記事の方式別費用表・削減率・確認パス回数・ラベル件数・Verifier遷移・unmet内訳)。

## 作業(順序)
A. T-0。事前: `_sha_before_10.json`(1a 2記事+streaming_price)。当日非RLCT実績集計。dry-run(記事2、別out `_dryrun_10`)で6→5 job(M0,M0b,M1,M2,M3)とBudget上限を確認、`raw_usage_log.jsonl` sha不変を確認。
B. 記事2 実走(1回起動、foreground)→記事単位集計(委任_09と同じ: aggregate別名`aggregate_1b_a2.*`、`check_method`直接呼出で`_conform_check_1b_a2.json`、`_analysis_1b_a2.json`、固定名出力の改名保存+復元)→機械チェック→Gate G1〜G6判定→`_gate_1b_a2_to_a3_10.json`→commit 1→push。
C. Gate全PASSなら記事3 実走(同手順、`*_a3.*`)→集計→commit 2→push。Gate不成立ならSTOP報告(記事3未実行)。
D. 1b合計節(3記事)作成、`_sha_after_10.json` IDENTICAL確認、SSOT追記→commit 3→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_10.md`
- dry-run記事2: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --dry-run --article openai_copyright --method M0,M0b,M1,M2,M3 --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\_dryrun_10 --other-spend-today-jpy 180 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_10_dryrun_openai.txt`
- 記事2実走: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --article openai_copyright --method M0,M0b,M1,M2,M3 --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --other-spend-today-jpy <当日非RLCT実値> 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_10_1b_openai.txt`
- 記事3実走(Gate PASS後): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er082_rlct_trial_01_run.py --paid-confirm USER_APPROVED_B_OPTA_2026-10-17_CAP1040 --article central_bank_mortgage --method M0,M0b,M1,M2,M3 --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01 --other-spend-today-jpy <当日非RLCT実値> 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\console_10_1b_central.txt`
- 集計(委任_09方式): 一時rootへ当該記事dirをコピーし `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er082_rlct_trial_01_aggregate.py --out C:\Users\tensh\eigo-radio\er082_output\rlct_trial_01\aggregate_1b_a2.md`(aggregateの実引数は委任_09の実手順に合わせる)
- test: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er082_rlct_trial_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-410: 「1b記事2/3: 確認パス発火回数、成立/未成立(unmet内訳)、費用(実測)。1b合計 x/493」。
- OPEN-409/411: 記事2・3で観測したVerifier遷移・ラベル件数(事実のみ)。
- DECISION_LOG: 「2026-10-18 RLCT 委任_10: 1b記事2・3実走(実費、Gate G1〜G6判定、1b累計/493、Trial累計/1,040)。Production変更なし。判定はFable」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 委任_10+_check.json、`er082_output/rlct_trial_01/openai_copyright/**`(記事1と同じ追跡範囲)、console、`aggregate_1b_a2.*`、`_conform_check_1b_a2.json`、`_analysis_1b_a2.json`、`_gate_1b_a2_to_a3_10.json`、`_sha_before_10.json`、`*_10_1b_a2.json`。msg: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_10: Stage 1b 記事2(openai_copyright)有料実走(M0/M0b/M1/M2/M3、実費JPY x)+集計・適合照合+記事間Gate判定`
- commit 2: 記事3同様。msg: `… 委任_10: Stage 1b 記事3(central_bank_mortgage)有料実走(実費JPY y)+集計・適合照合`
- commit 3: STAGE_1B_RESULTS_01.md(記事2・3・合計節)、`_sha_after_10.json`、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `… 委任_10: Stage 1b 3記事合計集計+SSOT(1b累計JPY z/493、Trial累計/1,040、Production変更なし)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_RLCT10.md`)
4行: (1)整合(PLAN一致、置換(a)(b)(c)の踏襲)(2)Production到達経路=なし(3)成果物とcommit sha、記事2・3それぞれの方式別 成立/未成立・費用・削減率・検索呼出・確認パス/再選定回数・ラベル件数・Verifier遷移、Gate G1〜G6の判定値、1b累計/493・Trial累計/1,040・当日累計/1,000(非RLCT実績の出典付き)、3記事+1a(新設計列=Coffee M2/M3+inbound M2c/M3c+1b M2/M3、旧inbound M2/M3は参考行)の暫定合計表(4)撤去/残置(sha IDENTICAL、上書きなし)。`判定整合:` 重大NG有無。`判断候補:` [A]〜[D]またはなし。T-0 check。自己チェック: 各記事1回起動/再起動なし/Gate判定記録後に記事3/上限内/Production・harness不変/既存集計未上書き。
