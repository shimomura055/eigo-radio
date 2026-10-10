# Post-EN Risk Flagger Review Queue: coffee_prices__run_l3_01 / a2

- run_id: `rf20261010T125728Z-ea2b`  status: **OK**
- article_sha256: `6f5e8e5301963ad650a9538a453a3e5dd493ac61e76fd5ab5cdd6514aa618236`  ledger_sha256: `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `L3_PRODUCTION_E2E_01`
- sentences: 47  facts: 19  candidate issues: 5

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=3 cost_jpy=0.227376 model=gpt-6-luna
- luna A4: OK flags=5 cost_jpy=0.270016 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.205171 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.205288 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.48)
- issue_id: `coffee_prices__run_l3_01__a2__6f5e8e53__rf20261010T125728Z-ea2b__s1`
- sentence: # Coffee Prices Fall, but Store Prices Stay: Coffee’s “Jet Lag”
- after: “Coffee prices are falling!” / Great!
- detected_by: luna-A4(0.48)
- reason [その他]: 「Coffee Prices Fall」と「Store Prices Stay」は、世界市場の指標価格と米国のCPI項目という異なる範囲を、コーヒー全般と店舗価格全般の動きとして述べているのではありませんか。
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

### s5  (confidence max 0.35)
- issue_id: `coffee_prices__run_l3_01__a2__6f5e8e53__rf20261010T125728Z-ea2b__s5`
- sentence: But supermarket prices do not change.
- before: Great! / Maybe spring will finally come to my wallet, too.
- after: They look calm, as if saying, “News? / I haven’t heard any.”
- detected_by: luna-A3(0.35), luna-A4(0.31)
- reason [不在断定]: “do not change”というスーパー価格がまったく変動しないとの断定は、価格転嫁に時間がかかるとの推定や米国CPIの前年同月比上昇を超える意味ではありませんか。
- reason [否定反転]: 「supermarket prices do not change」は、米国のコーヒーCPIが前年同月比で上昇したというFactと食い違うのではありませんか。
- fact COFFEE-014: Reutersが2025年12月に取材した市場関係者・専門家は、生豆価格が小売に反映されるまで少なくとも約9か月かかるとの見積もりを示した。記事は、米国ロースターが平均で生豆在庫を約2～3か月分保有し、その後の焙煎・包装にも約2～3か月かかり、小売業者との価格交渉は四半期ごとに行われることが多いと報じた。
  scope: 米国のロースターと小売価格への価格転嫁
  conditions: 市場関係者・専門家の推定およびReutersの取材報告であり、すべての企業の標準期間を示すものではない
  numeric_value: 転嫁まで少なくとも約9か月との見積もり。在庫約2～3か月分、焙煎・包装約2～3か月 (numeric_scope: 米国のロースターの平均的な在庫・製造過程についての記事内説明)
  date_or_period: 2025年12月時点の業界関係者の説明
  causal_strength: CORRELATIONAL
  notes_for_writer: 相場下落や関税撤廃の後も消費者価格がすぐ下がらない理由の一つとして、推定・報道の帰属を付けて記載する。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。

### s14  (confidence max 0.9)
- issue_id: `coffee_prices__run_l3_01__a2__6f5e8e53__rf20261010T125728Z-ea2b__s14`
- sentence: At about the same time, ICE’s future prices for arabica coffee reached a record high.
- before: Then demand around the world was strong. / It was a hard mix for prices to settle down.
- after: But future prices are not prices for green beans sold right away. / They are not store prices, either.
- detected_by: luna-A3(0.31), luna-A4(0.55), gemini35fl-A3(0.9), gemini35fl-A4(0.7)
- reason [数量時系列]: “a record high”という表現は、台帳の「2025年1月29日時点での当時の過去最高値」を現在までの最高値と読める形にしていませんか。
- reason [数量時系列]: 「reached a record high」は「当時の過去最高値」を現在までの最高値とも読める形で述べているのではありませんか。
- reason [数量時系列]: s14の「ICE’s future prices for arabica coffee reached a record high」について、COFFEE-003の「当時の過去最高値(at the time record high)」が「現在までの最高値(record high)」に読めるようになっていませんか？
- reason [数量時系列]: s14の「ICE’s future prices for arabica coffee reached a record high」は、COFFEE-003の「当時の過去最高値」という条件と食い違っていませんか？
- fact COFFEE-003: ICEのアラビカ先物は2025年1月29日に一時369.45米セント／ポンドの当時の過去最高値を記録し、同日終値は366.55米セント／ポンドだった。Reutersは、ブラジルの販売可能な豆の減少と次期収穫への懸念を背景として報じた。
  scope: ICEのアラビカ先物契約。当日の取引価格
  conditions: Reuters記事時点での過去最高値。先物価格であり、生豆の個別現物取引価格や小売価格とは異なる
  numeric_value: 一時369.45米セント／ポンド、終値366.55米セント／ポンド (numeric_scope: ICEアラビカ先物1ポンド当たりの米ドル建て価格)
  date_or_period: 2025年1月29日
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「当時の過去最高値」とする。現在までの最高値とは言い換えない。

### s31  (confidence max 0.28)
- issue_id: `coffee_prices__run_l3_01__a2__6f5e8e53__rf20261010T125728Z-ea2b__s31`
- sentence: That is how long green-bean prices take to show up in store prices.
- before: Reuters spoke with market experts and others. / They estimated that it takes around nine months or longer.
- after: If market prices are a breaking news alert, price tags are patient letters. / US roasters keep green beans in stock.
- detected_by: luna-A4(0.28)
- reason [その他]: 「store prices」は、米国ロースターについての市場関係者らの推定を、店舗価格全般に当てはまるよう広げているのではありませんか。
- fact COFFEE-014: Reutersが2025年12月に取材した市場関係者・専門家は、生豆価格が小売に反映されるまで少なくとも約9か月かかるとの見積もりを示した。記事は、米国ロースターが平均で生豆在庫を約2～3か月分保有し、その後の焙煎・包装にも約2～3か月かかり、小売業者との価格交渉は四半期ごとに行われることが多いと報じた。
  scope: 米国のロースターと小売価格への価格転嫁
  conditions: 市場関係者・専門家の推定およびReutersの取材報告であり、すべての企業の標準期間を示すものではない
  numeric_value: 転嫁まで少なくとも約9か月との見積もり。在庫約2～3か月分、焙煎・包装約2～3か月 (numeric_scope: 米国のロースターの平均的な在庫・製造過程についての記事内説明)
  date_or_period: 2025年12月時点の業界関係者の説明
  causal_strength: CORRELATIONAL
  notes_for_writer: 相場下落や関税撤廃の後も消費者価格がすぐ下がらない理由の一つとして、推定・報道の帰属を付けて記載する。

### s47  (confidence max 0.82)
- issue_id: `coffee_prices__run_l3_01__a2__6f5e8e53__rf20261010T125728Z-ea2b__s47`
- sentence: Falling coffee market prices take months to lower supermarket prices.
- before: Say, “By the way, how many months ago did you get here?” / ## In one line
- detected_by: luna-A3(0.36), luna-A4(0.82)
- reason [その他]: “take months to lower supermarket prices”という断定は、米国の市場関係者らによる約9か月以上との推定を、スーパー価格が必ず数か月後に下がるという一般則に広げていませんか。
- reason [その他]: 「take months to lower supermarket prices」は、市場価格の下落後に小売価格が必ず下がると読め、約9か月という推定であって値下がりを保証しないという注意書きと食い違うのではありませんか。
- fact COFFEE-014: Reutersが2025年12月に取材した市場関係者・専門家は、生豆価格が小売に反映されるまで少なくとも約9か月かかるとの見積もりを示した。記事は、米国ロースターが平均で生豆在庫を約2～3か月分保有し、その後の焙煎・包装にも約2～3か月かかり、小売業者との価格交渉は四半期ごとに行われることが多いと報じた。
  scope: 米国のロースターと小売価格への価格転嫁
  conditions: 市場関係者・専門家の推定およびReutersの取材報告であり、すべての企業の標準期間を示すものではない
  numeric_value: 転嫁まで少なくとも約9か月との見積もり。在庫約2～3か月分、焙煎・包装約2～3か月 (numeric_scope: 米国のロースターの平均的な在庫・製造過程についての記事内説明)
  date_or_period: 2025年12月時点の業界関係者の説明
  causal_strength: CORRELATIONAL
  notes_for_writer: 相場下落や関税撤廃の後も消費者価格がすぐ下がらない理由の一つとして、推定・報道の帰属を付けて記載する。
