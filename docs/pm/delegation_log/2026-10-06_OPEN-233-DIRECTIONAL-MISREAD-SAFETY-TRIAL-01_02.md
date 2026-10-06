## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(委任_02: schema整合→費用見積→¥15判定→限定Trial実行→一次集計)。**書込先: `er052_open233_directional_trial_01.py`(整合修正のみ)、同test、`er052_output/open233_directional_misread_trial_01/`配下(`estimate_01.md`、`run_<config>/`、`trial_summary_01.{json,md}`)、`docs/pm/RESULT_PACKET_TRIAL_02.md`、`docs/pm/delegation_log/`。Production code(runner/checker/calibration)・SSOT・gold・git操作なし。**
作業方式: Edit 1回40行以内、Bash heredoc不使用、説明最小。長時間実行はBashをbackground化しログをファイルへ。T-0は委任文をWrite+Edit追記で逐語保存。時間目安40分。

## 性質/到達上限Status/禁止事項
性質: 有料限定Trial(上限¥15、ユーザー承認済み「¥0再集計後の見積が¥15以内なら追加承認なしで実行可、超えるならSTOP」)。到達上限: 一次集計まで(Status分類はFable)。禁止: 残11 run/Production Checker・後段AI変更/既存floor復活/gold・KPI変更/Human Review振替/Production配線/¥15超過(scriptの`--budget-yen`で強制、累計管理)。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_02.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3(有料): 見積(low/mid/high)を`estimate_01.md`に記録→mid≤¥15なら実行。実行中に累計が¥15に達したら即停止し、完了分のみ集計。実費はcall_log/usageから算出し領収(¥)をRESULT_PACKETへ。

## ユーザー指示(原文、要点)
> 費用: 限定Trial費用上限は¥15。¥0再集計後に、見積が¥15を超える場合のみSTOPして報告する。¥15以内なら追加承認を待たずTrialまで進めてよい。
> 比較: 同一model構成/Ledger側と記事側でmodelを分ける構成/blind分離あり・なし。モデル変更自体をProduction採用する判断は今回行わない。
> 評価項目: 真の方向反転検出数/見逃し数/正常文の誤反転数/判断不能数/Ledger側方向性判定の精度/記事側方向抽出の精度/最終機械比較の結果/追加処理件数/1 runあたり追加費用見込み。特に誤検出で不要Rewriteが再び増えないかを重視。

## Fableの実行方針(固定)
- effort: **medium**(前回の再分類Trialと同じ。Stage 2のhighはTrialでは不要、費用優先)。scriptの既定がhighなら`--effort`引数を追加しmediumを指定(Production codeは触らない)。
- 実行順と再利用: (1)`same_blind`(Ledger側10 fact×`--ledger-repeat 3`=30 call+記事側75 call)→(2)`same_nonblind`(1 callで両側、75 call)→(3)`split_blind`: 記事側は(1)と同一入力・同一modelのため**(1)の記事側結果を再利用**(scriptに`--reuse-article-from <run_same_blind dir>`を追加)、Ledger側のみ別model(10 fact×3 repeat=30 call)。
- 別model(split用): `docs/pm/delegation_log/2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01_result.md`(Grep `model|単価|\$`)から、**単価が記録されていてgpt-6-lunaより上位または別系統**のmodel IDを1つ選び、PRICE_TABLEへ登録(出典行を注記)。候補が`gpt-5.6-sol`($5/$30)しか無い場合は、Ledger側30 callの見積が合計¥15内に収まる範囲で`--ledger-repeat`を1〜3に調整(最低1)。収まらなければsplit_blindは**Ledger側5 fact(方向性あり5件)のみ**に縮小し、その旨記録。
- 累計予算: 各構成の`--budget-yen`は「15−それまでの実費」を渡す。
- Ledger側の2モデル一致率(same vs split)はsummaryで算出。

## 作業内容
A. **schema整合**: `testset_01.json`(items配列、keys: id/fixture/fact_id/ledger_fact_text/article_sentence/article_context/expected_ledger_state/expected_article_state/expected_compare/acceptable_compare/repeat/label 等。実keyはGrep `"items"|"expected_` で確認)と`population_01.json`(n_runs/total_facts/facts_per_run 等)を、scriptの想定keyへ整合(script側を修正。`acceptable_compare`があれば評価で許容扱い)。dry-runで63項目を通し、unit test再実行(PASS)。
B. **見積**: dry-runのprompt token数(tiktoken相当または文字数/3.5近似)×単価(01aの逆算値: 入力約¥10.7/1M・出力約¥81.7/1M、effort=mediumの推論token≒出力300〜1000 tokと仮定)で構成別・合計のlow/mid/highを`estimate_01.md`へ。**mid>¥15ならSTOP(実行せず報告)**。
C. **実行**(mid≤¥15): 上記順で実行。各runの`results_*.jsonl`/`summary_*.json`/`budget_state_*.json`/call_logを`run_<config>/`へ。失敗callは1回retry、なお失敗ならUNCLEAR記録(重大化しない)。
D. **一次集計** `trial_summary_01.{json,md}`(構成別+比較表): 真の反転検出数(gold 3のうち、repeat 3回中の検出回数も)/見逃し数/正常文(忠実38+非該当5)の誤反転数と率/判断不能数/Ledger側has_direction精度・state精度(事前登録10 factとの一致、repeat間の揺れ)/記事側state精度(expected_article_stateとの一致)/機械比較分布(SAME/SAME_FAMILY/REVERSED/NOT_MENTIONED/UNCLEAR)/人工反転14件の検出率(厳密6・許容8別)/曖昧3件の挙動/same vs split のLedger側一致率/blind vs nonblind のHC-012検出差/call数・実費・1 callあたり¥/**1 runあたり追加処理件数と費用**(population_01.jsonの3水準: 下限3.33・近似7.46・上限30.56単位/run+Ledger側13.67 fact/run)/**不要Rewrite増加見込み/run**=正常文誤反転率×単位数(3水準)、比較基準=現行Rewrite 0.67件/run。
E. `docs/pm/RESULT_PACKET_TRIAL_02.md`: 見積・実費・実行構成・集計要点10行・T-0結果・逸脱・一覧外Read理由。

## 事前指定Read/Grep一覧
1. `er052_open233_directional_trial_01.py`: Grep `argparse|add_argument|PRICE_TABLE|effort|def load_testset|def load_population|def main` →範囲Read。
2. `testset_01.json`: Grep `"items"|"expected_|"acceptable_|"repeat"` 先頭20行のみRead。`population_01.json`: 全文(短い)。
3. `docs/pm/delegation_log/2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01_result.md`: Grep `model|単価|\$|per`。
4. `docs/pm/RESULT_PACKET_TRIAL_01C.md`: 全文(短い)。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_02.md_check.json`
2. `.venv\Scripts\python.exe -m unittest er052_open233_directional_trial_01_test`
3. dry-run: `.venv\Scripts\python.exe er052_open233_directional_trial_01.py --dry-run --config same_blind --testset er052_output\open233_directional_misread_trial_01\testset_01.json --population er052_output\open233_directional_misread_trial_01\population_01.json --out-dir er052_output\open233_directional_misread_trial_01\dryrun_full`
4. 本実行(例): `.venv\Scripts\python.exe er052_open233_directional_trial_01.py --config same_blind --effort medium --ledger-repeat 3 --budget-yen 15 --testset ... --population ... --out-dir er052_output\open233_directional_misread_trial_01\run_same_blind > er052_output\open233_directional_misread_trial_01\run_same_blind.log 2>&1`(他構成も同様、budgetは残額)。

## SSOT追記文
なし(Fableが後続委任で反映)。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL_02.md`。最終報告10行以内(見積mid、STOP有無、実費、HC-012検出(3/3?)、gold、正常文誤反転率、UNCLEAR数、Ledger側一致率、不要Rewrite見込み/run、追加費用/run)。


---
(追記注記: check_delegation_prompt必須節「事前指定Grep一覧+追記位置・更新位置の手順」は上記「事前指定Read/Grep一覧」+「実行コマンド全文」で充足。追記位置=docs/pm/RESULT_PACKET_TRIAL_02.md新規、更新位置=er052_open233_directional_trial_01.py(整合のみ)。)
