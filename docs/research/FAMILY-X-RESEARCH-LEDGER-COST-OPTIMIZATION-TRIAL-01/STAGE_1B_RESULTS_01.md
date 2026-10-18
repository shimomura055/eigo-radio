# Stage 1b 結果 01(FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01)

性質: Trial専用(`er082_*`)。Production code・Prompt・Gate変更0。Production到達経路なし。Trial結果はProduction採用を意味しない(到達上限Status=`STAGE_1B_COMPLETE_PENDING_FABLE`)。
記事2・3は下記へ追記済み(1b完了)。人手品質評価(ブラインド・R-07)は別委任。

## 記事1: streaming_price(委任_09、2026-10-18 JST)

### 実行
- 使用モデル(raw_usage_log実測): B3=`gpt-6.1-sol`、Verifier/Ledger検証=`gpt-6-luna`(M0基準と一致、`verifier_model_matches_m0=true`)。harness既定のまま変更なし(1aと同一条件維持)。
- 起動: 1回、rc=0、再起動なし。`console_09_1b_streaming.txt`(EXIT=0)。stop_scope_check rc=0(`_stop_scope_check_09.json`)。
- コマンドの置換(報告事項): `--plan 1b`は`--article`を無視して1b全3記事(計16job)を実行する実装(`jobs_from_args` L319-320)のため、記事2・3の誤実行を避け、同一6jobを`--article streaming_price --method M0,M0b,M0p,M1,M2,M3`(stage既定=ARTICLES.stage="1b"、順序はPLAN["1b"]の記事1部分と同一)で実行した。dry-runも同様に別out `_dryrun_09`(real outへの汚染防止)で実行、`raw_usage_log.jsonl`のsha256は前後不変(real_usage_log_rows=0)。
- 事前見積(TRIAL_DESIGN_03 §5の1a単価から): M0 B3 約8.5 + M0b 約8.3〜12.7 + M0p 約18〜25 + M1(Ledger約20〜23+B3約10)約30〜34 + M2(初回B3約10.5+選定検証約7〜9+確認B3約11、再選定発生で+約19) 約29〜50 + M3 約19〜45 = **期待約120、最大約185**。実測は下記のとおり86.128で、見積より小さい(streamingは検証対象Factが少なく、B3単価が5.7〜7.0円と1a(8.3〜10.5)より低かった)。

### 方式別結果(実測、`aggregate_1b_a1.md`/`_analysis_1b_a1.json`)
| 方式 | status | 選定Fact | 再選定/確認パス/後続B3 | unmet | ラベル件数 | 契約 |
|---|---|---|---|---|---|---|
| M0 | COMPLETED | F02,F03,F04,F07 | -/-/- | - | 0 | PASS |
| M0b | COMPLETED | F01,F02,F03,F04,F07 | -/-/- | - | 0 | PASS |
| M0p | COMPLETED(Ledger検証のみ、B3なし) | - | -/-/- | - | - | - |
| M1 | COMPLETED | F02,F03,F04,F06,F07 | -/-/- | - | 0 | PASS |
| M2 | COMPLETED | F02,F03,F04,F07 | 0/1/1 | null(`final_confirm_pass`=NOT_NEEDED_AMBIGUOUS_ALREADY_VISIBLE) | 0 | PASS |
| M3 | COMPLETED | F02,F03,F04 | 1/0/1 | null(`final_confirm_pass`=NOT_NEEDED_ALL_VERIFIED) | 0 | PASS |

- UNRESOLVED 0(REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMEDとも該当なし)。「確定条件のもとでの成立率」は案2系(M2/M3)のみの指標でM0/M0b/M0p/M1と同列比較しない(R-B2)。
- M2: 初回B3がF01/F04(AMBIGUOUS)を判定未提示で選定→確認パス1回→確認B3はF01を外しF04をAMBIGUOUS付きで選定。M3: 初回B3のF07がREJECTED→再選定1回(M2の初回B3を共有)→F02,F03,F04全てVERIFIED。
- 注: M3の再選定は`RESELECT_REJECTED+CONFIRM_AMBIGUOUS`トリガー。M2とM3の差はB3出力の揺らぎ標本を含み、案1上限の効果とは断定しない(R-B5)。

### 方式別費用(実測JPY、検索は別列。出典=`raw_usage_log.jsonl`、`lib.cost_by_stage_tag`)
| 方式 | LLM | 検索ツール | 合計 | 検索呼出(種別) | クエリ | step別 | 本番換算 | 対M0削減 |
|---|---|---|---|---|---|---|---|---|
| M0 | 5.735 | 0 | 5.735 | 0 | 0 | b3 5.735 | 40.195 | 基準 |
| M0b | 6.487 | 0 | 6.487 | 0 | 0 | b3 6.487 | 40.947 | -1.9%(増) |
| M0p | 1.263 | 9.6 | 10.863 | 6(search5/open_page1) | 18 | ledger 10.863 | 対象外 | 対象外 |
| M1 | 7.728 | 8.0 | 15.728 | 5(search3/open1/find1) | 12 | ledger 9.346, b3 6.382 | 37.405 | +6.9% |
| M2 | 15.831 | 14.4 | 30.231 | 9(search6/open3) | 21 | b3_initial 6.969, verify_sel_r0 16.073, 確認B3 7.189 | 51.908 | -29.1%(増) |
| M3 | 7.484 | 9.6 | 17.084 | 6(search4/open1/find1) | 23 | verify_sel_r0 11.278, 再選定B3 5.806 | 45.730 | -13.8%(増) |
- 対M0p(同日・上限なし再検証、検索6回/クエリ18)との検索比較: M1 5回/12(-17%/-33%)、M2 9回/21(+50%/+17%)、M3 6回/23(同数/+28%)。**検索削減を案1の3回上限の効果とは断定しない**(ソフト上限超過の記録は全方式0件=`soft_cap_exceeded_requests`空、M0pはB3を含まない限界あり、R-B7)。
- 本番換算は`aggregate`算出値(M0基準40.195の内訳[Ledger費用+M0 B3 5.735の差分34.46]は本委任では個別確認していない)。streaming(7Fact)では案2系の確認パス・選定後検証が全Fact検証(M0p)に対し割安にならず、本記事単独ではM2/M3は費用増。1記事の標本のため一般化せず、記事2・3完了後に5記事集計で判定(R-B7)。

### 機械チェック
- 選定FactへのREJECTED混入: 全方式0(`rejected_in_sel`空)。
- AMBIGUOUS選定: M2のF04は最終sel生成B3(confirm1)の候補Ledgerに`[AMBIGUOUS…]F04:`で可視(`_conform_check_1b_a1.json`、promptで裏取り、agrees_with_rounds=true)。M3は選定全VERIFIED。D1適合: M2=PASS、M3=PASS。M0/M0b/M0p/M1はN/A。M0はF07(AMBIGUOUS)、M0bはF01・F07(AMBIGUOUS)、M1はF04(AMBIGUOUS)を、いずれも全Fact検証済みLedger(判定タグ付き)から選定。
- 「【独立検証前の編集仮説】」ラベル出現件数: M0 0/M0b 0/M1 0/M2 0/M3 0(記録のみ、Prompt不変)。
- 中心Fact(R-07の機械検出分)で断定リスク候補: M0 F01(AMBIGUOUS)、M0b F01、M2 F01、M3 F01。人手判定は別委任。

### Verifier判定の方式間差(同一Fact、`_analysis_1b_a1.json` verdict_table。「-」=その方式では検証せず)
| Fact | M0 | M0b | M0p | M1 | M2 | M3 |
|---|---|---|---|---|---|---|
| F01 | AMBIGUOUS | AMBIGUOUS | REJECTED | REJECTED | AMBIGUOUS | AMBIGUOUS |
| F02 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED |
| F03 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED |
| F04 | VERIFIED | VERIFIED | AMBIGUOUS | AMBIGUOUS | AMBIGUOUS | VERIFIED |
| F05 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | - | - |
| F06 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | - | - |
| F07 | AMBIGUOUS | AMBIGUOUS | VERIFIED | VERIFIED | VERIFIED | REJECTED |
- M0/M0b=stage_r既存Ledger判定を再利用。M0pは全Fact同日再検証でもF01 REJECTED/F04 AMBIGUOUS/F07 VERIFIEDと既存から遷移し、Verifier自体の判定ばらつきが方式差に混入している(OPEN-409、改修なし)。既知欠陥F07は、M1・M2が選定しVERIFIED(`b_selected_missed_NG`)、M0はAMBIGUOUSで選定(`a_selected_detected`)、M3はREJECTEDで除外(`c_not_selected`)。M3のF07 REJECTEDと同日M0p/M1/M2のVERIFIEDは同一Factの方式間の矛盾で、M3固有の差かばらつきかは本標本では分離不能。

### 累計(実測、出典付き)
- 1b累計: JPY86.128 / 493(`cost_by_stage_tag` 1b|streaming_price|*の合計)。
- Trial累計: 243.7(1a 212.80+任意A 10.88+1a補正 20.009、STAGE_1A_CORRECTION_01)+86.128=**329.8 / 1,040**(raw_usage_log全行`cost_by_stage_tag`合計329.819と一致)。
- 当日(JST 2026-10-18): 本実行前の他支出0(raw_usage_log最終行=2026-10-17T06:22Z、JST日付境界2026-10-17T15:00Z以降の行なし)+86.128=**86.128 / 1,000**。
- 事前見積(期待約120・最大約185)に対し実測86.128(見積内)。

### 完全性
- 1a成果dir(`coffee_prices`・`inbound_tourism`)のsha256: 実行前後でIDENTICAL(161ファイル、`_sha_before_09.json`/`_sha_after_09.json`)。
- 既存集計の非上書き: run本体が`run_summary.json`/`stop_check.json`/`integrity_{before,after,check}.json`を固定名で書く実装のため、実行直後に新ファイルを`*_09_1b_a1.json`へ改名し、元のファイルを事前バックアップから復元(`aggregate.md`は未接触でsha不変)。aggregateは`--out`がroot兼出力先(`--root`なし、既存`aggregate.md/json`を上書きする実装)のため、streaming_priceのみを一時rootにコピーして実行し`aggregate_1b_a1.md/json`として保存。適合照合は`ARTICLES_1A`固定のため`check_method`を直接呼出して`_conform_check_1b_a1.json`に保存(コード不変)。
- test: `er082_rlct_trial_01_test_01.py` 25 passed。

## 記事2: openai_copyright(委任_10、2026-10-18 JST)

### 実行
- 使用モデル(raw_usage_log実測): B3=`gpt-6.1-sol`、Verifier/Ledger検証=`gpt-6-luna`(全方式で`verifier_model_matches_m0=true`)。harness既定のまま(1a・記事1と同一条件、旧モデル使用なし)。
- 起動: 1回、再起動なし。5job(M0,M0b,M1,M2,M3=PLAN["1b"]の記事2部分、M0pは実施せず)全てCOMPLETED。コマンドは委任_09と同じ置換(`--article openai_copyright --method M0,M0b,M1,M2,M3`)。dry-runは別out `_dryrun_10`で5jobを確認し`raw_usage_log.jsonl` sha256不変(331b4b93…)。
- **プロセスrc=5**(`[STOP] integrity mismatch`、実行完了後のpost-run integrity検査)。差分は全て`shared_review_queue_tree`配下の`review_queue/post_en/index.jsonl`と`review_queue/post_en/middle_east_yemen_saudi__run_mey_01/**`(並行中のFamily X新記事MEYの書込、`integrity_check_10_1b_a2.json`にdiff16件、いずれもMEY配下かindex.jsonl)のみ。RLCT側の保護対象(1a・streaming成果dir)は変化なし(sha IDENTICAL)。BudgetガードSTOPはなし(`stop_check`は`stop=false`)。記事間Gate G1が「rc=0」を要求するため機械的にFAIL(`_gate_1b_a2_to_a3_10.json`)。記事3は未実行。
- 事前見積(記事1の最大185に対し)実測74.738で範囲内。

### 方式別結果(実測、`aggregate_1b_a2.md`/`_analysis_1b_a2.json`)
| 方式 | status | 選定Fact | 再選定/確認パス/後続B3 | unmet | ラベル件数 | 契約 |
|---|---|---|---|---|---|---|
| M0 | COMPLETED | F2,F4,F6,F7,F8 | -/-/- | - | 0 | PASS |
| M0b | COMPLETED | F2,F4,F6,F7,F8 | -/-/- | - | 0 | PASS |
| M1 | COMPLETED | F2,F4,F6,F7,F8 | -/-/- | - | 0 | PASS |
| M2 | COMPLETED | F2,F4,F6,F7,F8 | 0/1/1 | null(`final_confirm_pass`=NOT_NEEDED_AMBIGUOUS_ALREADY_VISIBLE) | 0 | PASS |
| M3 | COMPLETED | F2,F4,F6,F7,F8 | 0/0/0(初回B3はM2と共有) | null(`final_confirm_pass`=NOT_NEEDED_ALL_VERIFIED) | 0 | PASS |
- UNRESOLVED 0。全5方式の選定Factが同一(Jaccard 1.0)。既知欠陥登録なし(`known_defects=[]`)。
- M2: 初回B3がF8を判定未提示で選定→選定検証でF8がVERIFIED→AMBIGUOUSに降格→確認パス1回→確認B3は同じ5Factを選定(F8はAMBIGUOUS付きで可視)。M3: 初回B3(M2と共有)の選定5FactをM3検証して全VERIFIED(F8もVERIFIED)→再選定・確認パスとも0回。

### 方式別費用(実測JPY。出典=`raw_usage_log.jsonl`、`lib.cost_by_stage_tag`)
| 方式 | LLM | 検索ツール | 合計 | 検索呼出(種別) | クエリ | step別 | 本番換算 | 対M0削減 |
|---|---|---|---|---|---|---|---|---|
| M0 | 6.389 | 0 | 6.389 | 0 | 0 | b3 6.389 | 38.22 | 基準 |
| M0b | 7.296 | 0 | 7.296 | 0 | 0 | b3 7.296 | 39.127 | -2.4%(増) |
| M1 | 8.634 | 9.6 | 18.234 | 6(search3/open_page2/unknown1) | 12 | ledger 10.81, b3 7.424 | 41.055 | -7.4%(増) |
| M2 | 15.713 | 11.2 | 26.913 | 7(search4/open_page2/find_in_page1) | 15 | b3_initial 7.337, verify_sel_r0 12.477, 確認B3 7.099 | 49.734 | -30.1%(増) |
| M3 | 1.506 | 14.4 | 15.906 | 9(search3/open_page5/find_in_page1) | 12 | verify_sel_r0 15.906(B3はM2のb3_initial共有) | 46.064 | -20.5%(増) |
- 記事2合計(実測): **JPY74.738**。本記事ではM1/M2/M3とも本番換算でM0より高い(M1 +2.8、M2 +11.5、M3 +7.8 JPY相当、`aggregate_1b_a2.md`削減JPY列)。要因は未分析(1標本)。ソフト上限超過の記録は全方式0件。本標本1記事のみで一般化せず、記事3完了後に5記事集計で判定(R-B7)。

### 機械チェック
- 選定FactへのREJECTED混入: 全方式0。AMBIGUOUS選定: M1のF8とM2のF8(M3は全VERIFIED)。D1適合: M2=PASS(AMBIGUOUS選定F8は確認B3 promptで可視)、M3=PASS。M0/M0b/M1はN/A(`_conform_check_1b_a2.json`)。
- 「【独立検証前の編集仮説】」ラベル出現件数: M0 0/M0b 0/M1 0/M2 0/M3 0(記録のみ)。
- 中心Factの断定リスク候補(機械抽出): M1のみF8(AMBIGUOUS)1件、他方式0件。人手判定は別委任。

### Verifier判定の方式間差(`_analysis_1b_a2.json` verdict_table。「-」=その方式では検証せず)
| Fact | M0 | M0b | M1 | M2 | M3 |
|---|---|---|---|---|---|
| F1 | VERIFIED | VERIFIED | VERIFIED | - | - |
| F2 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED |
| F3 | VERIFIED | VERIFIED | VERIFIED | - | - |
| F4 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED |
| F5 | VERIFIED | VERIFIED | VERIFIED | - | - |
| F6 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED |
| F7 | VERIFIED | VERIFIED | VERIFIED | VERIFIED | VERIFIED |
| F8 | VERIFIED | VERIFIED | AMBIGUOUS | AMBIGUOUS | VERIFIED |
- F8のみ方式間で揺れる(M1/M2=AMBIGUOUS、M0/M0b/M3=VERIFIED)。M2のF8降格とM3のF8 VERIFIEDは同一選定・同一初回B3に対する異なる検証呼出の結果で、Verifierばらつきと方式固有の差は分離不能(OPEN-409の観測と同種、改修なし)。

### 累計(実測、出典付き)
- 1b累計: 86.128+74.738=**160.866 / 493**(`cost_by_stage_tag` 1b|*の合計)。Trial累計: 329.819+74.738=**404.557 / 1,040**(全行集計と一致)。
- 当日(JST 2026-10-18): RLCT 160.866+非RLCT(Family X MEY進行中、`daily_dev_cost_01.py`のrun_mey_01ログ集計)56.53=**217.40 / 1,000**(記事2実走直後に集計)。記事2実走時に渡した`--other-spend-today-jpy`は保守値180。

### 完全性
- 1a成果dir・streaming_price: 実行前後でsha256 IDENTICAL(241ファイル、`_sha_before_10.json`と再計算値が一致、`_sha_after_10.json`)。
- 既存集計の非上書き: 固定名出力(run_summary/stop_check/integrity_*)を`*_10_1b_a2.json`へ改名保存し、事前バックアップから復元(復元後のsha256=実行前と一致、`aggregate.md`未接触)。aggregateは一時rootで実行し`aggregate_1b_a2.md/json`として保存、適合照合は`check_method`直接呼出(コード不変)。
- 記事3(central_bank_mortgage)は記事間Gate G1 FAIL(rc=5)により未実行。

## 記事3: central_bank_mortgage(委任_11、2026-10-18 JST)

### 実行
- 使用モデル(raw_usage_log実測): B3=`gpt-6.1-sol`、Verifier/Ledger検証=`gpt-6-luna`(M1/M2/M3で`verifier_model_matches_m0=true`)。harness既定のまま(旧モデルなし)。
- 起動: 1回、再起動なし。5job(M0,M0b,M1,M2,M3)全てCOMPLETED。`--other-spend-today-jpy 120`(daily_dev_cost_01.py再集計の非RLCT=MEY run_mey_01 63.21+_before_regen_01 56.53の保守合算)。dry-runは別out `_dryrun_11`、`raw_usage_log.jsonl`のsha256は前後不変。stop_scope_check rc=0(実走前)。
- **プロセスrc=5**(`[STOP] integrity mismatch`)。差分17件は全て`shared_review_queue_tree`の`review_queue/post_en/index.jsonl`と`review_queue/post_en/middle_east_yemen_saudi__run_mey_01/**`(並行MEYの書込。`integrity_check_11_1b_a3.json`)。review_queue配下以外の差分は0件。
- **Gate(Fable読替え版、`_gate_1b_a3_11.json`)=ALL_PASS**: 1回起動・再起動なし・BudgetガードSTOPなし(`stop_check_11_1b_a3.json` stop=false)・全job COMPLETED・RLCT保護対象(1a 2記事+streaming_price+openai_copyright、316ファイル)sha IDENTICAL(`_sha_before_11.json`/`_sha_after_11.json`)。
- 事前見積(期待約70〜90、最大185)に対し実測51.257(見積内、見積より小さい)。

### 方式別結果(実測、`aggregate_1b_a3.md`/`_analysis_1b_a3.json`)
| 方式 | status | 選定Fact | 再選定/確認パス/後続B3 | unmet | ラベル件数 | 契約 |
|---|---|---|---|---|---|---|
| M0 | COMPLETED | F002,F003,F006,F008,F010 | -/-/- | - | 0 | PASS |
| M0b | COMPLETED | F002,F003,F007,F008,F010 | -/-/- | - | 0 | PASS |
| M1 | COMPLETED | F001,F002,F003,F006,F008 | -/-/- | - | 0 | PASS |
| M2 | COMPLETED | F002,F003,F006,F008,F010 | 0/0/0 | null(`final_confirm_pass`=NOT_NEEDED_ALL_VERIFIED) | 0 | PASS |
| M3 | COMPLETED | F002,F003,F006,F008,F010 | 0/0/0(初回B3はM2と共有) | null(`final_confirm_pass`=NOT_NEEDED_ALL_VERIFIED) | 0 | PASS |
- UNRESOLVED 0。M2/M3とM0の選定は一致(Jaccard 1.0)、M0b・M1はJaccard 0.667。M2/M3は初回B3の選定5Factが全てVERIFIEDで、確認パス・再選定とも不要。

### 方式別費用(実測JPY。出典=`raw_usage_log.jsonl`、`lib.cost_by_stage_tag`)
| 方式 | LLM | 検索ツール | 合計 | 検索呼出(種別) | クエリ | step別 | 本番換算 | 対M0削減 |
|---|---|---|---|---|---|---|---|---|
| M0 | 8.060 | 0 | 8.060 | 0 | 0 | b3 8.060 | 30.392 | 基準 |
| M0b | 8.564 | 0 | 8.564 | 0 | 0 | b3 8.564 | 30.896 | -1.7%(増) |
| M1 | 11.402 | 6.4 | 17.802 | 4(search1/open_page2/find_in_page1) | 10 | ledger 7.463, b3 10.339 | 32.749 | -7.8%(増) |
| M2 | 8.266 | 4.8 | 13.066 | 3(search1/open_page2) | 4 | b3_initial 7.581, verify_sel_r0 5.485 | 28.013 | +7.8% |
| M3 | 0.565 | 3.2 | 3.765 | 2(search1/open_page1) | 4 | verify_sel_r0 3.765(B3はM2のb3_initial共有) | 26.293 | +13.5% |
- 記事3合計(実測): **JPY51.257**。本記事のみM2/M3が本番換算でM0より安い(+2.379/+4.099 JPY相当)。要因は選定5Factが全てVERIFIEDで確認パス・再選定が0回だったこと(1標本、一般化しない。R-B7)。ソフト上限超過の記録は全方式0件。

### 機械チェック
- 選定FactへのREJECTED混入: 全方式0。AMBIGUOUS選定: 全方式0(全Fact VERIFIED)。D1適合: M2=PASS、M3=PASS、M0/M0b/M1はN/A(`_conform_check_1b_a3.json`)。
- 「【独立検証前の編集仮説】」ラベル出現件数: M0 0/M0b 0/M1 0/M2 0/M3 0(記録のみ)。
- 中心Fact断定リスク候補(機械抽出のAMBIGUOUS): 全方式0件。人手判定は別委任。

### Verifier判定の方式間差(`_analysis_1b_a3.json` verdict_table)
- 全方式・全検証Factで VERIFIED(F001〜F011。M0/M0b/M1は11Fact、M2/M3は選定5Factのみ検証)。方式間の判定揺れなし(記事1・2で見られたOPEN-409型のばらつきは本記事では未観測)。

### 累計(実測、出典付き)
- 1b累計: 160.866+51.257=**212.123 / 493**(`cost_by_stage_tag` 1b|*の合計)。Trial累計: 404.557+51.257=**455.814 / 1,040**(全行集計と一致)。
- 当日(JST 2026-10-18): `daily_dev_cost_01.py`採用値**348.36 / 1,000**(RLCT 212.12+MEY run_mey_01 79.71+MEY _before_regen_01 56.53)。`_before_regen_01`は再生成前の退避ログで重複計上の可能性があり、実質は約291.8〜348.4。いずれも上限内。

### 完全性
- 1a成果dir・streaming_price・openai_copyright: 実行前後でsha256 IDENTICAL(316ファイル)。
- 既存集計の非上書き: 固定名出力(run_summary/stop_check/integrity_*)を`*_11_1b_a3.json`へ改名保存し、事前バックアップ(`_backup_11`)から復元(cmp一致、`aggregate.md/json`は未接触)。aggregateは一時rootで実行し`aggregate_1b_a3.*`として保存(`-I`ではlib importが失敗するため`-I`なしで実行。コード不変)。適合照合は`check_method`直接呼出。
- 委任_10のG1相当(rc=5)は、Fable判定どおりMEYのreview_queue書込によるfalse-positive。integrity検査のreview_queue除外はコード変更せずTrial後の改善候補(OPEN-410)。
- test: `er082_rlct_trial_01_test_01.py` 25 passed。

## 1b合計(3記事、`aggregate_1b_all.md`/`.json`、実測)
| 方式 | Trial費用JPY(3記事計) | 検索呼出/クエリ | 本番換算(3記事計) | 対M0削減JPY | 対M0削減% |
|---|---|---|---|---|---|
| M0 | 20.184 | 0/0 | 108.807 | 基準 | 基準 |
| M0b | 22.347 | 0/0 | 110.970 | -2.163 | -2.0%(増) |
| M1 | 51.764 | 15/34 | 111.209 | -2.402 | -2.2%(増) |
| M2 | 70.210 | 19/40 | 129.655 | -20.848 | -19.2%(増) |
| M3 | 36.755 | 17/39 | 118.087 | -9.280 | -8.5%(増) |
(M0pはstreaming_priceのみ実施: 10.863・検索6回/18q、対象外。)
- 1b実費合計 JPY212.123(記事1 86.128+記事2 74.738+記事3 51.257)/ 493。
- 確認パス/再選定回数(3記事): M2 確認パス2回(streaming 1・openai 1・central 0)、再選定0回。M3 再選定1回(streaming)、確認パス0回。
- ラベル件数: 全方式・全3記事で0件(15job)。
- unmet内訳: 全方式null(UNRESOLVED 0、REJECTED_SELECTED/AMBIGUOUS_NOT_CONFIRMEDとも0)。「確定条件のもとでの成立率」はM2/M3のみの指標(R-B2): 1b 6/6成立。
- Verifier遷移: 記事1=F01/F04/F07がM0p・M1・M2・M3で揺れ(M3のF07 REJECTED)、記事2=F8のみ揺れ(M1/M2=AMBIGUOUS)、記事3=遷移0。
- 1b単独では、M2/M3は3記事合計で本番換算がM0より高い(記事1・2で増、記事3のみ削減)。1b 3標本に基づく暫定値で、5記事暫定合計と人手品質評価で判定する。

## 新設計列の5記事暫定合計(R-B7、M0基準の本番換算、`aggregate.json`+`aggregate_1b_all.json`)
Coffee M2/M3(確認パス不要のため新設計と同一経路)+inbound M2c/M3c+1b 3記事(M2/M3)。旧inbound M2/M3(修正前)は参考行で母数に入れない。
| 記事 | M2列 削減JPY | M3列 削減JPY |
|---|---|---|
| coffee_prices(M2/M3) | +4.291 | +6.269 |
| inbound_tourism(M2c/M3c) | +9.224 | +6.965 |
| streaming_price | -11.713 | -5.535 |
| openai_copyright | -11.514 | -7.844 |
| central_bank_mortgage | +2.379 | +4.099 |
| **合計** | **-7.333**(M0計230.009に対し -3.2%、微増) | **+3.954**(+1.7%、微減) |
- 本番換算(5記事計): M0 230.009 / M2 237.342 / M3 226.055。
- 記事ごとに符号が分かれ(M2:+,+,-,-,+/M3:+,+,-,-,+)、5標本で明確な削減は確認されない。案1の上限効果との分離は不可(R-B5)。人手品質評価(ブラインド・R-07)と最終分類は別委任。到達上限Status=`STAGE_1B_COMPLETE_PENDING_FABLE`。
