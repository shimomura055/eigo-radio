# COST_VERIFICATION_01: ユーザー提示コスト表の再検証(Phase 1 read-only、費用0円)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_01。為替=USD/JPY 160固定(`er009_n1_routing_governance_10_actual_model_cost.py` L15-17、`pricing_snapshot.json`)。ログにはレート自体は記録されず、cost.jsonが160で計算されていることを下記の再計算一致で確認。

## 1. 登録単価(USD/100万token、入力/cached入力/出力)
| model | 入力 | cached | 出力 | 出典・状態 |
|---|---|---|---|---|
| gpt-6-luna | 0.10 | 0.01 | 0.50 | `er005_output/cost_baseline_01/pricing_snapshot.json`(PROJECT_INTERNAL_RECORD、DECISION_LOG GPT6-MODEL-COMPARISON-TRIAL-01由来)。`er009`のPRICING_USD_PER_Mにも登録 |
| gpt-6-astra | 10 | 1 | 50 | pricing_snapshot.json(OFFICIAL_PRICING_PAGE_FETCHED、2026-10-09、Standardのみ)。routing contract `FAMILY_X_FACTLOCK_REVISE`に登録 |
| gpt-6.1-sol | 2 | 0.1 | 10 | pricing_snapshot.json(OFFICIAL_PRICING_PAGE_FETCHED、2026-10-09、Short context Standardのみ。「登録=採用ではない、DEV/評価用」)。**routing contract(`er006`)には未登録**(DEV専用model id) |
| gpt-5.6-sol(旧世代) | 4 | 0.4 | 20 | 参考のみ。公式脚注でpromotional pricingが少なくとも2026-11-21まで。最新原則上は使わない |

注意(要確認): `er009`の`PRICING_USD_PER_M`は**luna(+旧5.6)のみ**で、astra/gpt-6.1-solは未登録(`cost_jpy_for_call`は未登録modelでUnknownModelPricingErrorを出す設計)。Trial driverは`pricing_snapshot.json`または既存Trial driverの単価定数を使う必要がある。Sol(gpt-6.1-sol)は「Sol相当」ではなく正式model idとして登録済み。gpt-6.1-solに5.6-solと同様のpromotional期限があるかは**未確認**。

## 2. 実測円の再集計(stage × run)
計算式: (input−cached)×入力単価+cached×cached単価+output×出力単価、×160。reasoning tokenはoutputに含まれる(ログのoutput_tokensがreasoning込み)。

| stage | model | META in/out | META 円(cost.json) | META 再計算 | coffee in/out | coffee 円(cost.json) | coffee 再計算 | 平均円 | ユーザー提示 | 差 |
|---|---|---|---|---|---|---|---|---|---|---|
| B3 | luna | 4,078/4,254 | 0.406 | 0.406 | 6,241/7,456 | 0.696 | 0.696 | 0.551 | 0.55 | 0 |
| R0 | luna | 1,772/3,567 | 0.314 | 0.314 | 2,437/6,296 | 0.543 | 0.543 | 0.4285 | 0.43 | 0 |
| R1 | astra | 475/2,236 | 18.648 | 18.648 | 696/2,131 | 18.162 | 18.162 | 18.405 | 18.41 | 0 |
| R2 | astra | 723/1,890 | 16.277 | 16.277 | 765/2,305 | 19.664 | 19.664 | 17.9705 | 17.97 | 0 |
| 合計 | | | 35.645 | | | 39.065 | | **37.355** | 37.36 | 0 |

**検証結果: ユーザー提示値(37.36円)は実測と一致**(META・coffeeの2 run平均、丸め差のみ)。cached tokenは全call 0。出力tokenが費用の約99%(Astra R1/R2が合計約95%)。

## 3. C/D/E案の概算再計算(A案実測tokenに単価を当てた値)
前提: tokenはA案実測(META+coffee平均)をそのまま使用。**モデルを変えると出力token数(特にreasoning)は変わる**ため、これは単価差だけの概算。同一入力でSolの出力tokenはLunaの0.6〜1.2倍(streaming_price 4,240→5,154、space_weapons 6,259→3,763)、処理時間は約1.3〜2倍という既存実測がある(`er052_output/writer_r0_model_impact_trial_01`、R0のみ3テーマ)。

### 3-1. stage×モデル別の単価換算(円/回、A案実測tokenベース)
| stage | META luna | META sol | META astra | coffee luna | coffee sol | coffee astra |
|---|---|---|---|---|---|---|
| B3 | 0.406 | 8.111 | 40.557 | 0.696 | 13.927 | 69.634 |
| R0 | 0.314 | 6.274 | 31.371 | 0.543 | 10.853 | 54.267 |
| R1 | 0.186 | 3.730 | 18.648 | 0.182 | 3.632 | 18.162 |
| R2 | 0.163 | 3.255 | 16.277 | 0.197 | 3.933 | 19.664 |

### 3-2. 配置別合計(META+coffee平均、円、4 stage)
| 構成(アーム定義は委任_02のDESIGN側が正本。ここは仮置き) | 計算結果 | ユーザー提示 | 乖離 |
|---|---|---|---|
| A: 現行(B3 luna / R0 luna / R1,R2 astra) | 37.36 | 約37(B案暫定) | 一致 |
| R0のみSol化 | 45.49 | C約44 | -1.5 |
| 〃(R0 Sol実測: RESULT_01 R0 3テーマ合計22.07円→平均7.36円/回で置換) | 44.3 | C約44 | **ほぼ一致**(C=R0 Sol化と推定) |
| B3のみSol化 | 47.82 | D約56 | **+8.2乖離(ユーザー値が高い)** |
| B3 Sol+R0 Sol(R1/R2 Astra) | 55.96 | D約56 | **一致**(D=B3+R0のSol化と推定。ただしこの定義でよいかはFable確認) |
| 全stage Sol(B3/R0/R1/R2) | 26.86 | E約54 | **ユーザー値が約2倍。未解明** |
| R0〜R2をSol、B3 luna | 16.39 | | |
| R0をAstra(参考) | 79.75 | | R0 Astra実測は127.08円/3テーマ=42.4円/回 |
| B3をAstra(参考) | 91.90 | | |

乖離の指摘:
- C(約44円)・D(約56円)は、それぞれ「R0のSol化」「B3+R0のSol化」と置くと再計算とよく一致する(推定。アーム定義は未確認)。
- **E「Sol統一」約54円は、全stageをSolにすると単価換算で約27円にしかならず、約2倍の乖離**。Eがreasoning増加・追加段(例: 修正段の追加)・Astra併用等を含む定義なのか、ユーザー概算が別前提なのか、本調査では判断できない(要確認)。仮にSol統一でR1/R2がAstraのままなら55.96円でDと同額になる。
- B案約37円(暫定)はA案同額。実測B案(既存META R2)は約35.1円(B3除く)で整合。

## 4. 5案合計見積と上限200円に対する余裕
| ケース | 内容 | 新規API費用 | 200円に対する余裕 |
|---|---|---|---|
| A,B既存再利用+C約44+D約56+E約54(ユーザー値) | 各1回(META 1記事) | 約154円 | 約46円(23%)。評価用のLLM judge/FC費・retryは別途 |
| 同上、E=再計算値26.9円 | | 約127円 | 約73円 |
| 同上、B3をA案出力で固定しC/D/Eで再利用 | B3新規call不要(約0.4〜0.7円/案を削減) | 約154円から約1円減 | 同上 |
| B案を新規再生成(R0〜R2のみ約35円)する場合 | A再利用+B新規+C/D/E | 約189円 | 約11円(**ほぼ余裕なし**) |
| A,Bとも再利用しC案のみ | | 約44円 | 約156円 |

注意: 上記は生成段のみ。評価(Luna FC、Risk Flagger、pairwise judge等)の費用は含まない(1本あたり約0.2〜数円規模の既存実績あり、本調査では集計せず)。Sol/Astraは出力token・処理時間が増える可能性があるため、5案×1記事でも上限200円に対し実測変動±30%を見込むと約154円は約200円に近づく。

## 5. 不明点・要確認
1. E案「Sol統一」約54円の前提が再計算(約27円)と約2倍乖離。
2. D案の定義(B3のみSol化か、B3+R0か)。B3のみなら再計算47.8円でユーザー値56円と乖離。
3. gpt-6.1-solはpricing_snapshot登録済(DEV/評価用)だが、routing contract(`er006`)・`er009` PRICING_USD_PER_Mには未登録。Trial driverでの単価注入方法が必要(委任_02側で確認)。
4. gpt-6.1-solのpromotional pricing期限は未確認(5.6-solは2026-11-21まで)。
5. Astra/Solの出力token数がLuna基準のA案実測と異なる可能性(上記概算の最大不確実性)。
