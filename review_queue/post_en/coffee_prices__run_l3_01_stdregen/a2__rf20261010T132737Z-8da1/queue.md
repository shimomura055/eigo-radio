# Post-EN Risk Flagger Review Queue: coffee_prices__run_l3_01_stdregen / a2

- run_id: `rf20261010T132737Z-8da1`  status: **OK**
- article_sha256: `c582868e603366f87da0eacfcb7b0ceaafde3041b73c4cb9921a68afcae2d212`  ledger_sha256: `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `L3_STDREGEN_EVIDENCE`
- sentences: 46  facts: 19  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.231248 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.266688 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.380384 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.395344 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.35)
- issue_id: `coffee_prices__run_l3_01_stdregen__a2__c582868e__rf20261010T132737Z-8da1__s1`
- sentence: # Market Prices Fall, But Coffee Price Tags Stay Put: Coffee’s “Jet Lag”
- after: “Coffee prices are falling!” / Great!
- detected_by: luna-A4(0.35)
- reason [不在断定]: 「Market Prices Fall」とは別に「Price Tags Stay Put」と断定していますが、台帳のCPIや過去の平均小売価格の数値だけでは値札が動いていないとは確認できないのではありませんか。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。
- fact COFFEE-016: APが報じたBLS政府統計によると、米国の挽いたコーヒー1ポンドの平均価格は2025年9月に9.14米ドルとなり、同年8月の8.87米ドルから3%上昇、2024年9月比で41%上昇した。
  scope: 米国で販売された挽いたコーヒーの1ポンド当たり平均価格
  conditions: APがBLSの政府統計として報道した値。豆、銘柄、販売店を限定しない平均
  numeric_value: 9.14米ドル／ポンド。前月比+3%、前年同月比+41% (numeric_scope: 挽いたコーヒー1ポンドの米国平均小売価格)
  date_or_period: 2025年9月（2025年8月および2024年9月との比較）
  notes_for_writer: BLSデータの報道値として出典をAPと明記。家庭用小売価格であり、カフェの一杯の価格とは区別する。

### s5  (confidence max 0.4)
- issue_id: `coffee_prices__run_l3_01_stdregen__a2__c582868e__rf20261010T132737Z-8da1__s5`
- sentence: But in supermarkets, price tags do not move.
- before: Great! / Maybe spring will finally bring relief to my wallet, too.
- after: They look calm, as if saying, “News? / I’ve never heard of it.”
- detected_by: luna-A3(0.32), luna-A4(0.4)
- reason [不在断定]: 「price tags do not move」という一律の断定は、コーヒー項目の前年同月比上昇や挽いたコーヒーの平均小売価格上昇の記録と範囲が食い違うのではありませんか。
- reason [不在断定]: 「price tags do not move」というスーパー全体の断定は、台帳にあるCPIや過去の平均小売価格のデータだけでは確認できないのではありませんか。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。
- fact COFFEE-016: APが報じたBLS政府統計によると、米国の挽いたコーヒー1ポンドの平均価格は2025年9月に9.14米ドルとなり、同年8月の8.87米ドルから3%上昇、2024年9月比で41%上昇した。
  scope: 米国で販売された挽いたコーヒーの1ポンド当たり平均価格
  conditions: APがBLSの政府統計として報道した値。豆、銘柄、販売店を限定しない平均
  numeric_value: 9.14米ドル／ポンド。前月比+3%、前年同月比+41% (numeric_scope: 挽いたコーヒー1ポンドの米国平均小売価格)
  date_or_period: 2025年9月（2025年8月および2024年9月との比較）
  notes_for_writer: BLSデータの報道値として出典をAPと明記。家庭用小売価格であり、カフェの一杯の価格とは区別する。

### s14  (confidence max 0.9)
- issue_id: `coffee_prices__run_l3_01_stdregen__a2__c582868e__rf20261010T132737Z-8da1__s14`
- sentence: At the time, ICE’s arabica coffee futures reached a record high.
- before: Then demand around the world was strong. / This was a hard mix for prices to settle down.
- after: But futures prices are not the prices of green beans for sale right away. / They are not store prices, either.
- detected_by: gemini35fl-A3(0.7), gemini35fl-A4(0.9)
- reason [その他]: s14で『ICEのアラビカ先物が過去最高値を記録した』とありますが、COFFEE-003の「2025年1月29日に当時の過去最高値」という限定が抜けて、現在までの最高値であるかのように読めるのではないでしょうか？
- reason [数量時系列]: COFFEE-003では「ICEのアラビカ先物は2025年1月29日に一時369.45米セント／ポンドの当時の過去最高値を記録した」とありますが、s14の「reached a record high」という表現は「当時の過去最高値」という限定が落ちて全期間の最高値に読めませんか？
- fact COFFEE-003: ICEのアラビカ先物は2025年1月29日に一時369.45米セント／ポンドの当時の過去最高値を記録し、同日終値は366.55米セント／ポンドだった。Reutersは、ブラジルの販売可能な豆の減少と次期収穫への懸念を背景として報じた。
  scope: ICEのアラビカ先物契約。当日の取引価格
  conditions: Reuters記事時点での過去最高値。先物価格であり、生豆の個別現物取引価格や小売価格とは異なる
  numeric_value: 一時369.45米セント／ポンド、終値366.55米セント／ポンド (numeric_scope: ICEアラビカ先物1ポンド当たりの米ドル建て価格)
  date_or_period: 2025年1月29日
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「当時の過去最高値」とする。現在までの最高値とは言い換えない。

### s46  (confidence max 0.35)
- issue_id: `coffee_prices__run_l3_01_stdregen__a2__c582868e__rf20261010T132737Z-8da1__s46`
- sentence: Falling coffee market prices do not quickly lower supermarket prices because changes take months to reach shelves.
- before: Next time you see a headline about falling prices, ask the price tag: “By the way, how many months ago did you get here?” / ## In one line
- detected_by: luna-A4(0.35)
- reason [その他]: 「do not quickly lower」と「because changes take months」は、関係者による推定で全企業共通ではないという台帳の条件より強い断定になっているのではありませんか。
- fact COFFEE-014: Reutersが2025年12月に取材した市場関係者・専門家は、生豆価格が小売に反映されるまで少なくとも約9か月かかるとの見積もりを示した。記事は、米国ロースターが平均で生豆在庫を約2～3か月分保有し、その後の焙煎・包装にも約2～3か月かかり、小売業者との価格交渉は四半期ごとに行われることが多いと報じた。
  scope: 米国のロースターと小売価格への価格転嫁
  conditions: 市場関係者・専門家の推定およびReutersの取材報告であり、すべての企業の標準期間を示すものではない
  numeric_value: 転嫁まで少なくとも約9か月との見積もり。在庫約2～3か月分、焙煎・包装約2～3か月 (numeric_scope: 米国のロースターの平均的な在庫・製造過程についての記事内説明)
  date_or_period: 2025年12月時点の業界関係者の説明
  causal_strength: CORRELATIONAL
  notes_for_writer: 相場下落や関税撤廃の後も消費者価格がすぐ下がらない理由の一つとして、推定・報道の帰属を付けて記載する。
