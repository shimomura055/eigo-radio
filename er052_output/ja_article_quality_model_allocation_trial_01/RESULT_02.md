# RESULT_02: JA記事品質 工程別モデル配置Trial(委任_05、Phase 3 coffee_prices / hormuz)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_05 / 2026-10-11 / DEV/Trial専用(Production code・Prompt・Routing・CURRENT_SPEC不変、Research/Ledger再実行なし、英訳・RF・TTS・Audioなし)
Status案: **MEASURED(N=1)**。hormuz=A/C/D/E 4案すべて完了。coffee_prices=A(既存再利用)/C/E完了、**D=R2記号QA STOP(R2再実行1回後も括弧残存、仕様どおり停止)**。B案は保留(対象外)。VALIDATED/採用はユーザーBlind評価後。
モデル: 全案 gpt-6-luna / gpt-6-astra / gpt-6.1-sol(各世代の現行。effort high)。

## 1. 比較表(再掲、B案は保留・今回対象外)
| 案 | B3 | R0 | R1 | R2 |
|---|---|---|---|---|
| A | Luna(coffeeは既存run_l3_01再利用¥0、hormuzは新規) | Luna | Astra | Astra |
| B | 保留(旧仕様再現不可。本Phase対象外) | - | - | - |
| C | A再利用 | Astra | Luna | Luna |
| D | Astra | Luna | Luna | Luna |
| E | Sol 6.1 | Sol | Sol | Sol |
決定論producer・契約・Prompt・effort high・developerはR0のみ・R2入力=R1 raw・記号QA(R2再実行1回)はMETA Phase 2と同一(無課金stub検査で両slug ALL_PASS、5ケースのrequest列/出力ファイル完全一致)。

## 2. 入力
- coffee_prices: Ledger=er019_output/coffee_prices/run_l3_01/research_ledger/verified_fact_ledger.txt(sha e94a50c1…、18件)。B3 topic=run_l3_01 full_ledger.jsonの英語theme(A既存と同一)。
- hormuz: Ledger=er019_output/family_x_refresh_e2e_01/hormuz/run_03/research_ledger/verified_fact_ledger.txt(sha 9bd6834e…、12件、2026-09-26取得。**事実鮮度は当時**)。B3 topic「ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応」=旧run_03 full_ledger.json記録と一致、かつProduction runnerは`--theme`でtopicを自由文字列指定する方式(er019_family_x_entertainment_production_runner_01.py L30/L386)でrun_03の記録topicと同じ文字列(ER-002 ADD03以来の正式topic)。不一致なし。

## 3. 実測円(記事×案×stage、円=USD×160、pricing_snapshot単価)
| 記事 | 案 | B3 | R0 | R1 | R2 | R2再実行 | 新規実測 | 点見積 | 保守cap | 状態 |
|---|---|---|---|---|---|---|---|---|---|---|
| coffee | A | 0.696(既存) | 0.543(既存) | 18.162(既存) | 19.664(既存) | - | 0(既存実測39.065) | 0 | - | 既存再利用 |
| coffee | C | 0(A再利用) | 42.499 | 0.080 | 0.080 | - | 42.659 | 64.72 | 97 | OK |
| coffee | D | 75.514 | 0.681 | 0.101 | 0.106 | 0.106 | 76.508 | 86.08 | 129 | **STOP(R2記号QA)** |
| coffee | E | 11.533 | 6.741 | 4.184 | 4.482 | - | 26.940 | 33.40 | 50 | OK |
| hormuz | A(新規) | 0.410 | 0.325 | 15.270 | 13.939 | - | 29.945 | 37.36 | 56 | OK |
| hormuz | C | 0(A再利用) | 46.126 | 0.092 | 0.104 | - | 46.323 | 50.58 | 76 | OK |
| hormuz | D | 51.731 | 0.496 | 0.087 | 0.088 | - | 52.403 | 64.80 | 97 | OK |
| hormuz | E | 7.209 | 7.332 | 2.284 | 2.590 | - | 19.415 | 26.66 | 40 | OK |
見積との差: 全案で点見積以下(点見積-実測: coffee C -22.1、D -9.6、E -6.5、hormuz A -7.4、C -4.3、D -12.4、E -7.2。点見積はMETA比出力・A実測由来のため全体にやや過大)。capを超えた案なし。
**Phase 3 新規課金合計 JPY294.19**(coffee 146.11[C42.66+D76.51+E26.94]+hormuz 148.09[A29.94+C46.32+D52.40+E19.42])。**Trial累計 JPY403.30 / 上限550(残146.70)**。全体残予算ゲート(既消費109.11+Phase3累計+他process予約+当該call見積≤550)は全callで通過。

## 4. 実行結果(actual model_id、受理)
- 全call: 返却model_idが要求モデルで始まる(gpt-6-luna / gpt-6-astra / gpt-6.1-sol)。モデル/effort/json_schemaの非受理(400系)なし。
- coffee D: R0/R1/R2は完了。R2(Luna、`w1_astra_r2`)出力に全角括弧「USDA（米農務省）」が残り、R2再実行1回(同一R1 raw入力)でも括弧が残存→`JASymbolCheckStopError`で停止(既存の記号QA機構どおり、上限回数を変更・回避せず)。rejected本文は`runs_02/coffee_prices/D/ja_writer/audit/rejected_w1_r2_symbol.md`(Blindページには使用しない)。各案1回のみの方針のため再生成していない。coffee DのR2は未受理=Blind比較に含められない。
- 他の6案(coffee A/C/E、hormuz A/C/D/E)は記号QA 初回/再実行とも発火なし(R0再生成・R2再実行ゼロ)。
- hormuz C は hormuz A のB3(Luna)をバイト再利用(注記済みB3/writer_constraintsの一致assert通過)。

## 5. 補助QA(人間判断の代替ではない。詳細 `AUX_METRICS_02_<slug>.md/.json`)
- 制約文混入grep・タグ残存・記号QA findings・R0 echo: 全受理記事で検出なし。
- 数値・英字固有名詞のLedger外: 全受理記事で「Ledger外の数値/英字」なし(カタカナ語は翻字ゆれ・比喩語で目視対象のみ、fact上の問題とは判断していない)。
- Fact忠実性の重大問題: **なし**(hormuz 4本・coffee A/C/E を Ledger の notes_for_writer と照合: 「提案した」表現、7/13と7/14の時系列、Brent 83.30/約2.6%/85ドル超、約9か月の見積り帰属、CPI 6.1%/8.7%の対象の区別は維持)。軽微: hormuz C本文・題に「通行料」「料金」(Ledgerは償還料/通航料。提案段階の表現として許容範囲)、coffee C本文に「、？」の句読点崩れ(postprocess由来の可能性、要目視)、E題冒頭の「！、」(同)。
- 選択Fact: hormuz A/C=HF-002,006,007,009、D/E=HF-002,007,009(Dは3件)。coffee A/C=COFFEE-003,009,010,014,015、E=COFFEE-001,010,014,015,018。D(STOP)=COFFEE-009,010,014,015,019。

## 6. Blind比較ページ
- hormuz: `user_test/ja_quality_model_allocation_02/hormuz/index.html`(4タブ、記事ごと独立seed=int(sha256("MAQ02:hormuz")[:8],16)=4088314252、対応表 `BLIND_MAP_02_hormuz.json`、漏洩検査OK、Pages 200+Playwright tab4/全文表示/leakなし/audioなし: `pages_playwright_evidence_02_hormuz.json`)。
- coffee: **未作成**(D欠落のため。選択肢: (i)A/C/Eの3本で作成、(ii)Dの扱いをFable/ユーザー判断)。seedは`int(sha256("MAQ02:coffee_prices")[:8],16)`=3330374777(4本でも3本でも同一seed、割当は本数で変わる)。

## 7. 未解決・判断事項
1. coffee D: 再生成(追加課金約76円)かD欠落(3本評価)かの判断。Luna R2が出典括弧を出しやすい傾向の可能性(N=1、断定しない)。
2. hormuz Ledgerは2026-09-26取得(鮮度は当時、比較目的には影響なし)。
3. B案は保留のまま。
