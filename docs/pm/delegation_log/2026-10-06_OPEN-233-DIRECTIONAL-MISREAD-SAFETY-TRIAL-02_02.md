## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(委任_02: testset_02と正解データ(複数事象対応)の作成)。並列委任_01(script)、_03(集計)、_04(SSOT)が同時進行。**書込先: `er052_output/open233_directional_misread_trial_02/testset_02.{json,md}`、同`ledger_truth_02.{json,md}`、`docs/pm/RESULT_PACKET_TRIAL02_02.md`、`docs/pm/delegation_log/`。他ファイル・gold定義・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0データ準備(事前登録)。禁止: 有料API/gold定義変更/KPI変更/人工文のLLM生成。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_02.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 前回と同じ主要テスト群を使う。最低限: HC-012/A5-0/D61・HF-009系の方向反転/正常文43件相当/曖昧例/前回誤爆した3件を含める。重要例は3回反復する。
> 合格基準(事前登録): HC-012 3/3検出、A5-0 3/3検出、正常文の誤重大判定2%以下、不要Rewrite見込み現行0.67件/runの半分以下、前回誤爆3件解消、新しい重大見逃しを発生させない。

## 作業内容
A. `testset_02.json`: TRIAL-01の`testset_01.json`(63項目)をコピーし、(1)`repeat`を次の項目で3に設定: G-01(HC-012 restored)、G-02(A5-0)、G-03(D61/HF-009)、F-09・F-10・F-19(前回誤爆3件)、G-04/G-05/G-06(曖昧3件)。他は1。(2)各項目に`expected_event_subject`(記事文が述べているLedger側事象の対象ラベル。下記Bのevent_keyを参照。述べていなければ"NONE")と`expected_compare`/`acceptable_compare`を複数事象前提で見直す(例: F-09/F-10「Brent fell/eased」は事象「上げ幅」に対応しSAME、F-19「pulled back the feature」は事象「機能」に対応しSAME/SAME_FAMILY)。(3)`trial02_reason`に見直し理由を1行。件数内訳をmdに。
B. `ledger_truth_02.json`(正解データの複数事象対応): 対象10 fact(testset_01の全fact_id)について、Ledger本文の逐語根拠付きで**事象リスト**を事前登録: `{fact_id: {has_direction: bool, events: [{event_key: 短いラベル(例 "機能", "電話テスト", "上げ幅", "水準"), aliases: [許容ラベル候補…], result_state: enum, quote: 逐語}]}}`。参考としてTRIAL-01のLedger側抽出結果(`er052_output/open233_directional_misread_trial_01/run_same_blind/results_same_blind.jsonl`の`ledger`/`repeat_events`。Grep `"fact_id": "MUSE-HC-012"`等で1行だけ確認)を見てよいが、**正解はLedger本文から独立に決める**(AI出力の追認にしない)。enum: AVAILABLE/STOPPED/PAUSED/INCREASED/DECREASED/UNCHANGED/STARTED/ENDED/EXPANDED/NARROWED/NOT_MENTIONED/UNCLEAR。HC-012=「電話テスト STARTED」+「機能 PAUSED(STOPPED許容)」、HF-009=「上げ幅 DECREASED(NARROWED許容)」+「水準 INCREASED」等、Ledger本文に即して登録。
C. Ledger側精度の採点規則(mdに記載、集計scriptが使う): 抽出eventsと正解eventsを`event_key`/`aliases`の部分一致で対応付け、対応したeventのstate一致率=state精度、has_direction一致率=方向性精度。対応しない余剰eventは「余剰」として件数のみ記録(誤りと断定しない)。
D. `testset_02.md`: 内訳表(gold/曖昧/忠実/非該当/人工、repeat、call見込み=Σrepeat)、前回誤爆3件の期待値、変更点一覧。
E. `docs/pm/RESULT_PACKET_TRIAL02_02.md`: 要約8行+T-0結果+一覧外Read理由。

## 事前指定Read/Grep一覧
1. `er052_output/open233_directional_misread_trial_01/testset_01.json`: 全文(scriptでコピー、Readは先頭30行で構造確認)。`testset_01.md`: 全文。
2. Ledger本文: `er019_output/meta/run_03/ledger/verified_fact_ledger.txt`、`er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt`: Grep `<fact_id>` →該当block範囲Read(10 fact分)。
3. TRIAL-01結果: 上記B参照(行単位Grepのみ)。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_02.md_check.json`
2. jsonの妥当性: `.venv\Scripts\python.exe -c "import json;json.load(open('er052_output/open233_directional_misread_trial_02/testset_02.json',encoding='utf-8'));json.load(open('er052_output/open233_directional_misread_trial_02/ledger_truth_02.json',encoding='utf-8'));print('ok')"`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL02_02.md`。最終報告6行以内(内訳、call見込み、前回誤爆3件の期待値)。
