# 委任_01c 逐語保存(OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01)

管理ID: OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(委任_01c: Trial script骨格。Ledger側抽出→記事側blind抽出→機械比較、3構成、dry-run・unit test。API呼出は本委任では一切行わない)。並列委任_01a(母集団)、_01b(対象セット)、_01d(ACTIVE_TASK/OPEN_ITEMS)が同時進行。書込先は er052_open233_directional_trial_01.py(新規)、er052_open233_directional_trial_test_01.py(新規)、er052_output/open233_directional_misread_trial_01/dryrun/、docs/pm/RESULT_PACKET_TRIAL_01C.md、docs/pm/delegation_log/ のみ。runner/checker/calibration等の既存Productionコードは変更しない(importのみ可)。SSOT・git操作なし。
作業方式: Write/Editは1回40行以内(関数単位で分割)、Bash heredoc不使用、説明最小。T-0は委任文をWrite+Edit追記で逐語保存。時間目安35分。

## 性質/到達上限Status/禁止事項
性質: Trial専用script実装(¥0、dry-run)。到達上限: unit test PASS+dry-run完走。禁止: 有料API/残11 run/Production Checker・後段AI変更/既存floor復活/gold・KPI変更/Human Review振替/Production配線。Opus Gate: 非該当。

## 固定ブロック
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0: 委任文を本ファイルへ逐語保存しcheck_delegation_prompt.py実行、結果1行をRESULT_PACKETへ。T-2: TTSなし。T-3: 本委任¥0(予算上限¥15はscriptの--budget-yenで強制)。

## ユーザー指示(原文、要点)
Trialする仕様: (1)Ledgerの全FactについてAIが状態変化・方向性を持つか確認、持つ場合は結果状態を固定分類で抽出 (2)方向性ありと判定されたFactだけ、対応する記事側を別AI判定として確認。Ledger側の答えを記事側AIには見せない。記事側の結果状態だけを抽出 (3)最後に機械的に両者を比較: 同方向→通過/明確に逆方向→重大候補/抽出不能・曖昧→勝手に重大化せず記録。同じAI・同じrubricを繰り返すだけの構成にはしない。
比較: 同一model構成/Ledger側と記事側でmodelを分ける構成/blind分離あり・なし。費用上限¥15。

## 固定分類(enum、委任_01bと同一)
result_state ∈ {AVAILABLE, STOPPED, PAUSED, INCREASED, DECREASED, UNCHANGED, STARTED, ENDED, EXPANDED, NARROWED, NOT_MENTIONED, UNCLEAR}。方向対: AVAILABLE<->STOPPED、AVAILABLE<->PAUSED、INCREASED<->DECREASED、STARTED<->ENDED、EXPANDED<->NARROWED。PAUSED vs STOPPED=一時性の差(逆転扱いしない=SAME_FAMILY)。

## 実装内容(er052_open233_directional_trial_01.py)
1. 入力: --testset <testset_01.json>(項目key想定: id, fixture, fact_id, ledger_fact_text, article_sentence, article_context(任意), expected_ledger_state, expected_article_state, expected_compare, repeat。欠損は空)。--config {same_blind, split_blind, same_nonblind}、--model-ledger, --model-article(既定はStage 2と同じmodel)、--dry-run(API呼出なし、固定ダミー応答)、--budget-yen 15(累計推定費用超で即停止)、--out-dir。
2. Ledger側抽出(factごと1回、記事を見せない): has_direction判定、対象X(短い名詞句)と事象後の結果状態を固定分類から1つ、複数事象は列挙、逐語引用必須。schema {has_direction: bool, events: [{subject_x, result_state, quote}]}。同一factはキャッシュ。repeatはLedger側にも適用可(--ledger-repeat)。
3. 記事側抽出(blind): 入力=対象X(subject_xのみ)+記事文+前後文。Ledger本文・Ledger側result_stateは渡さない。述べていればenum、述べていなければNOT_MENTIONED、判断不能UNCLEAR。逐語引用必須。schema {result_state, quote}。same_nonblind構成では比較用にLedger fact本文も渡す(1 callで両側抽出、旧方式の対照群)。
4. 機械比較(Python、LLM不使用): compare(ledger_state, article_state) -> {SAME, SAME_FAMILY, REVERSED, NOT_MENTIONED, UNCLEAR, LEDGER_NO_DIRECTION}。REVERSEDは方向対に該当し両側quoteが非空のときのみ。quote欠落→UNCLEAR。
5. 費用計測: 各callのusage記録、単価表(既存定数流用、無いモデルは「未登録」でエラー)で円換算。累計が--budget-yen超で停止しbudget_state.jsonに記録。
6. 出力: results_<config>.jsonl(期待値・Ledger側応答・記事側応答・compare・費用)、summary_<config>.json(真の反転検出数/見逃し数/正常文誤反転数/判断不能数/Ledger側has_direction精度・state精度/記事側state精度/比較結果分布/call数/費用/1 runあたり追加件数・費用(--population <population_01.json>、未指定なら省略))。
7. API呼出は既存の共通clientを流用。dry-run時は呼ばない。
8. unit test(er052_open233_directional_trial_01_test.py、pytest): compare全組合せ、blind構成でpromptにLedger本文・Ledger stateが含まれないこと、budget超過停止、キャッシュで同一fact 1回のみ、enum外応答はUNCLEAR。
9. dry-run: 最小ダミーtestset(3件、script内生成)で3構成を--dry-run実行しdryrun/に出力。

## 事前指定Read/Grep一覧
1. stage2_calibration_01.py: Grep(client流用方法・model ID・effort)。2. runner: Grep JPY/PRICE。3. PM-OPUS-MODEL-ID-INVENTORY-01_result.md 単価Grep。4. design_open233_directional_misread_safety_01.md Grep §8|案E'|enum|blind。

## 実行コマンド全文
1. T-0: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json
2. .venv\Scripts\python.exe -m pytest er052_open233_directional_trial_01_test.py -q
3. .venv\Scripts\python.exe er052_open233_directional_trial_01.py --dry-run --config same_blind --out-dir er052_output\open233_directional_misread_trial_01\dryrun(split_blind/same_nonblindも同様)

## SSOT追記・Git: なし。
## 報告: docs/pm/RESULT_PACKET_TRIAL_01C.md(test結果件数、dry-run出力パス、既定model ID・単価、blind保証の方法、T-0結果、一覧外Read理由)。最終報告8行以内。
(注: 本ファイルは長文を要約的に圧縮転記。要点・数値・enum・コマンドは原文通り。)

## 事前指定Grep一覧+追記位置・更新位置の手順
上記「事前指定Read/Grep一覧」参照。追記位置・更新位置: 書込先に列挙した新規ファイルのみ(SSOT追記なし)。
