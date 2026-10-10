# Post-EN Risk Flagger Review Queue: coffee_prices__run_l3_01 / b1b

- run_id: `rf20261010T125626Z-f4c2`  status: **OK**
- article_sha256: `5e8979dfaf1be6e63ffc29cf6d8670b1bf8c119d63daec39bdbc9c65d73d1e23`  ledger_sha256: `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `L3_PRODUCTION_E2E_01`
- sentences: 38  facts: 19  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.254336 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.230576 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.335008 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.340768 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.28)
- issue_id: `coffee_prices__run_l3_01__b1b__5e8979df__rf20261010T125626Z-f4c2__s1`
- sentence: # Market Prices Fall, Price Tags Stay Put: Coffee Prices’ “Jet Lag”
- after: “Coffee prices are falling!” / Great, maybe spring will finally come to my wallet too.
- detected_by: luna-A3(0.28)
- reason [不在断定]: 「Price Tags Stay Put」という断定は、台帳に小売価格が動いていないとの記載がなく、米国のコーヒーCPIは前年同月比で上昇していた点と食い違うのではありませんか。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。

### s2  (confidence max 0.35)
- issue_id: `coffee_prices__run_l3_01__b1b__5e8979df__rf20261010T125626Z-f4c2__s2`
- sentence: “Coffee prices are falling!”
- before: # Market Prices Fall, Price Tags Stay Put: Coffee Prices’ “Jet Lag”
- after: Great, maybe spring will finally come to my wallet too. / But on supermarket shelves, the price tags do not move at all.
- detected_by: luna-A4(0.35)
- reason [その他]: 「Coffee prices are falling」と全般のコーヒー価格が下落しているように読めますが、台帳では世界市場の指標は下落した一方、米国のCPI項目は前年同月比で上昇しており、範囲が広すぎるのではありませんか。
- fact COFFEE-009: USDAはICOの月次複合価格指数を指標として、コーヒー価格が2026年7月までの7か月間に25%下落したと報告した。同報告は、追加供給の入手可能性を下落と結び付けている。
  scope: ICO月次複合価格指数を用いた世界市場価格
  conditions: USDAが2026年7月報告で記載した観察期間
  numeric_value: 7か月で-25% (numeric_scope: ICO月次複合価格指数。個別品種または小売価格ではない)
  date_or_period: 2025年末頃から2026年7月までの7か月間
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 価格が2026年中に下落局面へ移ったことを示す。小売価格も同じ速度で下がったとは言えない。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。

### s4  (confidence max 0.32)
- issue_id: `coffee_prices__run_l3_01__b1b__5e8979df__rf20261010T125626Z-f4c2__s4`
- sentence: But on supermarket shelves, the price tags do not move at all.
- before: “Coffee prices are falling!” / Great, maybe spring will finally come to my wallet too.
- after: They look perfectly calm, as if to say, “News? / Never heard of it.”
- detected_by: luna-A3(0.32), luna-A4(0.32)
- reason [不在断定]: 「do not move at all」という断定は、台帳にスーパーの価格表示がまったく動いていないとの記載がなく、米国のコーヒーCPIは前年同月比で上昇していた点と食い違うのではありませんか。
- reason [不在断定]: 「price tags do not move at all」とスーパーの価格表示がまったく変動しないと断定していますが、台帳にはそのような不変の事実はなく、CPI項目は前年同月比で上昇しているのではありませんか。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。

### s38  (confidence max 0.38)
- issue_id: `coffee_prices__run_l3_01__b1b__5e8979df__rf20261010T125626Z-f4c2__s38`
- sentence: Falling coffee market prices don’t quickly lower supermarket prices because the changes take months to reach shelves.
- before: The next time you see a headline about falling prices, ask the price tag: “By the way, how many months ago did you get here?” / ## In one line
- detected_by: luna-A4(0.38)
- reason [その他]: 「changes take months to reach shelves」と一律の仕組みのように述べていますが、台帳では約9か月という見積もりは業界関係者の推定で全企業共通ではないとされており、断定が強すぎるのではありませんか。
- fact COFFEE-014: Reutersが2025年12月に取材した市場関係者・専門家は、生豆価格が小売に反映されるまで少なくとも約9か月かかるとの見積もりを示した。記事は、米国ロースターが平均で生豆在庫を約2～3か月分保有し、その後の焙煎・包装にも約2～3か月かかり、小売業者との価格交渉は四半期ごとに行われることが多いと報じた。
  scope: 米国のロースターと小売価格への価格転嫁
  conditions: 市場関係者・専門家の推定およびReutersの取材報告であり、すべての企業の標準期間を示すものではない
  numeric_value: 転嫁まで少なくとも約9か月との見積もり。在庫約2～3か月分、焙煎・包装約2～3か月 (numeric_scope: 米国のロースターの平均的な在庫・製造過程についての記事内説明)
  date_or_period: 2025年12月時点の業界関係者の説明
  causal_strength: CORRELATIONAL
  notes_for_writer: 相場下落や関税撤廃の後も消費者価格がすぐ下がらない理由の一つとして、推定・報道の帰属を付けて記載する。
