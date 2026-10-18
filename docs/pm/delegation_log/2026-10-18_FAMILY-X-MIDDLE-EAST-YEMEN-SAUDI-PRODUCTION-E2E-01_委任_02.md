# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_02(Fable CP-C判定=NG → 既存機構`--regenerate-stage storyline_b3`によるB3再選定+下流(Writer R0-R2/Adv/Std/Risk Flagger)再生成1回+費用記録+音声plan再確認。有料、E2E上限JPY180内)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 正式Production経路の既存retry機構(stage再生成)による1回限りの再生成。Prompt・Gate・Style変更0。
- 到達上限Status: `TEXT_STAGES_REGENERATED_PENDING_FABLE_CP2`。音声有料工程はFable CP2後(委任_03)。
- 禁止: Prompt改変/B3・Writerへの手動ヒント注入/Ledger・Factの手動編集/Research再実行(Ledgerは現状のF01〜F11を使う)/再生成の2回目(1回でCP2へ。2回目が必要ならSTOP報告)/RLCT方式混入/有料TTS起動/累計JPY180超過見込みでの続行/review_lock・Fact Lock・Risk Flagger契約・HRの迂回/`er082_*`・`er026_output`・`user_test/family_z_*`・`er063_*`への接触。
- 固定ブロック: **E-1**(E2E_PLAN_01 §4工程表・§5仕様照合表・BAPE先例の`--regenerate-stage`の扱い=CURRENT_SPEC/runner usageで「stage再生成が下流をstale化し再生成する」既存仕様であることを確認して記録)/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agent(RLCT/Family Z)あり: `.git/index.lock`待ち再試行、自分のファイルのみadd、non-ffは`pull --ff-only`後再試行、conflictはSTOP)/**F-1**(`cost.json`/`raw_usage_log.jsonl`実測。再生成分を初回分と分離して記録)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_委任_02.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY2.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記、sed禁止)。

## Fable CP-C判定(2026-10-18、記録用)
- 判定: **NG(音声工程へ進めない)**。根拠: (1)冒頭の「空港の出発案内板に“Peace in Yemen”が表示された」場面はLedgerに存在しない創作で、死傷者を扱うニュース記事における事実でない具体描写(Risk Flagger luna A4がb1b/a2のs3を「台帳で確認できない事実」として候補化)。(2)B3がF11の1件のみを選定し、F01〜F10(10/6〜10/16の空港・アラムコ・マリブ・アデンへの一連の攻撃)が全て`excluded`のため、ユーザーの狙い「なぜイエメン周辺の紛争がサウジや地域全体に影響するのか」を事実で語れておらず、「ニュースの読み方」のメタ記事になっている。(3)数字の時点明示・帰属・In One Lineの因果非誇張は良好(維持したい点)。
- Fact Ledger自体(V11/A0/R0、帰属・時点・主体未特定の保持)は受入可。出典が公的発表・当事者系に限られ独立報道(Reuters/AP)0件・1Fact1URLである点は最終報告でユーザーへ限界として明示する(Research再実行はしない)。
- 対応: 既存機構によるB3再選定1回(案B)。2回目は行わず、結果が再びNG(単一Fact・創作場面・狙い未達)ならSTOPしてユーザー判断(Production経路の限界として選択肢提示)。
- 費用見込み: B3約6+Writer R0-R2約12+Adv/Std約1+RF約2 ≒ JPY21(初回実測比例)。text累計≒78、E2E残≒102(音声見込み約25〜30)。180内。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY1.md`
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01\E2E_PLAN_01.md` §4・§12・§13
- `C:\Users\tensh\eigo-radio\er019_family_x_entertainment_production_runner_01.py` の`--regenerate-stage`/stale化の実装(Grep `regenerate|stale`)
- `C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\storyline_b3\fact_selection_evidence.json`(初回選定の記録。再生成前に`_before_regen/`へコピー保全)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `OPEN-416`→Fable CP-C NG理由・B3再選定1回・結果・費用を追記、Status更新。
- `DECISION_LOG.md`: 末尾に委任_02エントリ(CP-C判定・再生成1回の根拠=既存retry機構・結果)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `E2E_PLAN_01.md`: 「## §14 Fable CP-C判定と再生成記録(委任_02)」追記(初回と再生成後のタイトル/In One Line/選定Fact/RF候補/費用の対照表)。

## 作業(順序)
1. T-0。初回成果の保全(`run_mey_01/_before_regen_01/`へ storyline_b3/ b1b/ a2/ writer系・RF・audit・cost.jsonをコピー。git追跡はBAPE先例の範囲)。
2. `--regenerate-stage storyline_b3`で再生成(1回起動。runnerが下流を自動再生成するか確認し、しない場合は`--stage writer`→`advanced`→`standard`を順に実行。各stage後に費用記録)。Budget `--budget-jpy 110`は継続(text累計110内)。
3. 再生成後チェック(機械+記録): 選定Fact一覧(件数・ID)、In One Line全文、タイトル、Risk Flagger候補(s番号・理由)、HR/Lock発火有無、Ledger外の具体描写の有無(RF候補とは別に、本文の固有名詞・場面・数字をLedgerと突合した表)、数字の時点明示、帰属表現。
4. S6音声plan再実行(`--stage plan`、fx_20261017 sha一致再確認、JPY0)。
5. 費用集計(`er019_mey_cost_01.py`→`audit/cost_by_stage_text_02.json`: 初回/再生成を分離、text累計/110、E2E累計/180、当日累計/1,000)。
6. §14・SSOT→commit→push。Fable CP2用に新`article.md`(a2/b1b)の絶対pathを報告。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`、bashの`tee`・`PYTHONIOENCODING=utf-8`は委任_01の置換を踏襲可)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_委任_02.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er019_family_x_entertainment_production_runner_01.py --theme "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く" --slug middle_east_yemen_saudi --out-dir C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01 --run-label MEY-E2E-01 --budget-jpy 110 --regenerate-stage storyline_b3 2>&1 | tee C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\console_regen_b3_02.txt`(`--regenerate-stage`の正確な引数名・併用必須引数はrunner usageで確認し、実在形に置換して報告。下流が自動再生成されない場合は `--stage writer` / `--stage advanced` / `--stage standard` を同引数で順次実行、console `console_regen_s3_02.txt`〜`_s5_02.txt`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_01 --level both --stage plan 2>&1 | tee C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\console_s6_plan_02.txt`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er019_mey_cost_01.py --run-dir C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01 --out C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\audit\cost_by_stage_text_02.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-416: 「2026-10-18 Fable CP-C=NG(創作導入場面・単一Fact選定・狙い未達)。既存機構でB3再選定1回(費用JPY x)。再生成後: 選定Fact …、RF候補 …件。Status=TEXT_STAGES_REGENERATED_PENDING_FABLE_CP2」。
- DECISION_LOG: 同旨+「2回目の再生成は行わずSTOP→ユーザー判断の方針」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_02+_check.json、`run_mey_01/_before_regen_01/**`(追跡対象のみ)、再生成後の`storyline_b3/`・`b1b/`・`a2/`・RF・audit・console、`cost_by_stage_text_02.json`、E2E_PLAN_01.md、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_02: Fable CP-C=NG(Ledger外の創作導入・B3単一Fact選定)→既存機構でB3再選定1回+下流再生成(実費JPY x、text累計y/110、E2E累計z/180)+初回成果保全+音声plan再確認(音声工程はFable CP2後)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY2.md`)
4行: (1)整合(`--regenerate-stage`が既存仕様であることの出典行、下流再生成の経路)(2)Production到達経路=既存のみ(3)成果物とcommit sha、再生成後のタイトル・In One Line全文・選定Fact ID一覧・Ledger外具体描写の突合表(件数)・RF候補(s番号+理由)・HR/Lock有無・費用(初回/再生成/累計、E2E累計/180、当日/1,000)・S6 sha一致・新article.md絶対path(4)撤去/残置(初回成果の保全先)。`判定整合:` 重大NG有無。`判断候補:` [A]〜[D]またはなし。T-0 check。自己チェック: 再生成1回のみ/Prompt・Ledger不変/有料TTS未起動/累計≤180/並行作業不干渉。
