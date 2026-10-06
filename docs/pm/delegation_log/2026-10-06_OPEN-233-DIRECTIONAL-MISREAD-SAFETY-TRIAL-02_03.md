## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任_03: 集計script・合格基準自動判定・前回比regression・report templateの事前準備)。並列委任_01(script)、_02(testset_02)、_04(SSOT)が同時進行。**書込先: `er052_output/open233_directional_misread_trial_02/aggregate_trial_02.py`、同`regression_vs_trial01.py`、同`report_template_02.md`、同`selftest/`、`docs/pm/RESULT_PACKET_TRIAL02_03.md`、`docs/pm/delegation_log/`。他ファイル・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0集計準備。禁止: 有料API/SSOT編集/Status判定の自動化(判定はFable。scriptは基準充足の事実のみ出力)。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_03.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 合格基準(事前登録): HC-012 3/3検出、A5-0 3/3検出、正常文の誤重大判定2%以下、不要Rewrite見込み現行0.67件/runの半分以下、前回誤爆3件解消、新しい重大見逃しを発生させない。
> Closeout: HC-012結果/A5-0結果/前回誤爆3件の結果/正常文誤爆率/不要Rewrite見込み/AI揺れ/1 runあたり追加処理件数/追加コスト/前回Trialとの差/Trial Status/Production採否のユーザー判断要否/残11 E2E再開可否/並列化内容と所要時間短縮/未解決事項/APPROVED_FOR_PRODUCTION未配線項目への影響/Dangling Reference有無。

## 入力契約(委任_01のscript出力、未完成のためこの契約で実装し、selftestはTRIAL-01結果を変換して行う)
results jsonl record: `id, fact_id, label, origin, expected_compare, acceptable_compare, expected_event_subject(任意), repeats: [{rep, ledger_events_subjects: [...], selected_subject, ledger_state, article_state, compare, ledger_quote, article_quote}], final_compare_rep0, final_compares, cost_jpy`。summary: `n_items, n_calls, cost_jpy, by_label, gold_detail`。`ledger_cache.json`: `{fact_id: {rep1: [events], ...}}`(events=[{subject_x, result_state, quote}])。正解: `ledger_truth_02.json`(委任_02、`{fact_id: {has_direction, events: [{event_key, aliases, result_state, quote}]}}`)、`testset_02.json`。母集団: `er052_output/open233_directional_misread_trial_01/population_01.json`(記事側3水準3.33/7.46/30.56単位/run、Ledger 13.67 fact/run)。

## 作業内容
A. `aggregate_trial_02.py --results <merged jsonl> --ledger-cache <json> --truth <ledger_truth_02.json> --testset <testset_02.json> --population <population_01.json> --prev <trial_summary_01.json> --out <dir>`: 出力`trial_summary_02.json/.md`。指標: (1)gold別検出(HC-012=G-01、A5-0=G-02、D61=G-03: rep0検出・k/3)(2)前回誤爆3件(F-09/F-10/F-19)のrep0 compareと3反復の内訳、「解消」=3反復ともREVERSEDでない(3)正常文(label 忠実・非該当、43件相当)の誤重大判定率=rep0でREVERSEDの件数/件数、全repeat率も併記(4)UNCLEAR/NOT_MENTIONED件数(5)曖昧3件の最終REVERSED有無(6)人工反転14件の検出(厳密/許容)(7)Ledger側: 事象対応付け(event_key/aliases部分一致)→方向性精度・state精度・余剰event数・repeat間一致率(8)記事側: 選択event正解率(expected_event_subject vs selected_subject、aliases許容)・state精度(9)AI揺れ: repeat 3の項目で3反復のcompareが全一致した割合(10)1 runあたり追加call・追加¥(3水準)・不要Rewrite見込み=誤重大判定率×単位数(3水準)、基準0.67・半分0.335(11)**合格基準チェック表**: 6基準それぞれ「充足/未達」+根拠数値(「新しい重大見逃し」=前回検出していたgold/人工反転で今回見逃したもの、`--prev`と突合)(12)前回比(regression_vs_trial01: gold検出・誤爆・UNCLEAR・費用/run・不要Rewriteの差分表)。
B. `report_template_02.md`: Closeout 16項目の見出しと、summaryから埋める箇所を`{{key}}`で明示(Fableが最終判断文を入れる欄は空欄)。
C. selftest: TRIAL-01の`run_same_blind/results_same_blind.jsonl`を入力契約へ変換するadapter(`selftest/adapt_trial01.py`)を書き、aggregateが完走すること(数値はTRIAL-01値と整合: 誤反転3件、gold 8/9等)。`ledger_truth_02.json`未完成の場合は最小ダミーtruthで通し、その旨記録。
D. `docs/pm/RESULT_PACKET_TRIAL02_03.md`: 使い方(コマンド)、selftest結果、T-0結果、一覧外Read理由。

## 事前指定Read/Grep一覧
1. `er052_output/open233_directional_misread_trial_01/aggregate_trial_01.py`: 全文(流用元)。
2. `er052_output/open233_directional_misread_trial_01/trial_summary_01.json`: Grep `"` 先頭40行(構造)。
3. `run_same_blind/results_same_blind.jsonl`: 1行目のみ(keys確認、Pythonで)。
4. `population_01.json`: 全文(短い)。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_03.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_03.md_check.json`
2. selftest: `.venv\Scripts\python.exe er052_output\open233_directional_misread_trial_02\selftest\adapt_trial01.py` → `.venv\Scripts\python.exe er052_output\open233_directional_misread_trial_02\aggregate_trial_02.py --results ... --out er052_output\open233_directional_misread_trial_02\selftest\out`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL02_03.md`。最終報告6行以内。
