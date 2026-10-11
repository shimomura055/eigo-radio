# Post-EN Risk Flagger Review Queue: coffee_prices__run_e_tone_01 / b1b

- run_id: `rf20261011T052407Z-71d5`  status: **OK**
- article_sha256: `d9b77190905d9060d578b2b21d634d48193decfd4c4eb90f1ae9bdb7da028e67`  ledger_sha256: `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `COFFEE_NEW_TONE_E2E_01`
- sentences: 33  facts: 19  candidate issues: 5

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=3 cost_jpy=0.239744 model=gpt-6-luna
- luna A4: OK flags=2 cost_jpy=0.261344 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.328384 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.372144 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.34)
- issue_id: `coffee_prices__run_e_tone_01__b1b__d9b77190__rf20261011T052407Z-71d5__s1`
- sentence: # Coffee Bean Prices Fall.
- after: Are Price Tags Still on a Journey? / “Beans have gotten cheaper!”
- detected_by: luna-A3(0.32), luna-A4(0.34)
- reason [その他]: 「Coffee Bean Prices」と「ICO複合指標価格」では対象範囲が異なるのではありませんか。
- reason [主体対象入替]: 「Coffee Bean Prices」の下落は、ICO複合指標など特定の価格指標の下落をコーヒー豆価格全般の下落に広げていませんか。
- fact COFFEE-001: ICO Composite Indicator Price（I-CIP）は2026年9月に平均262.18米セント／ポンドとなり、2026年8月比で8.7%下落した。ICOは、ブラジルの収穫物の供給増加と潤沢な供給見通しが価格を押し下げた一方、認証済みアラビカ在庫の少なさとエルニーニョをめぐる不確実性が下支えしたと報告した。
  scope: 国際的なICO Composite Indicator Price。コーヒー4グループの指標を含む
  conditions: ICOの2026年9月市場報告。値下がり要因と下支え要因の双方を記録
  numeric_value: 平均262.18米セント／ポンド、前月比-8.7% (numeric_scope: 世界のコーヒー指標価格の月平均。特定の小売商品価格ではない)
  date_or_period: 2026年9月（8月比）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: ICOの報告する市場要因。これだけで消費者価格が同月に下がったとは言えない。報告ページは2026年10月9日時点で9月報告を掲載。
- fact COFFEE-009: USDAはICOの月次複合価格指数を指標として、コーヒー価格が2026年7月までの7か月間に25%下落したと報告した。同報告は、追加供給の入手可能性を下落と結び付けている。
  scope: ICO月次複合価格指数を用いた世界市場価格
  conditions: USDAが2026年7月報告で記載した観察期間
  numeric_value: 7か月で-25% (numeric_scope: ICO月次複合価格指数。個別品種または小売価格ではない)
  date_or_period: 2025年末頃から2026年7月までの7か月間
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 価格が2026年中に下落局面へ移ったことを示す。小売価格も同じ速度で下がったとは言えない。

### s3  (confidence max 0.32)
- issue_id: `coffee_prices__run_e_tone_01__b1b__d9b77190__rf20261011T052407Z-71d5__s3`
- sentence: “Beans have gotten cheaper!”
- before: # Coffee Bean Prices Fall. / Are Price Tags Still on a Journey?
- after: At that news, your wallet pumps its fist. / In your mind, the price of your usual cup has already come down, too.
- detected_by: luna-A3(0.32)
- reason [その他]: 「Beans have gotten cheaper」と「ICO複合指標価格が下落した」では対象範囲が異なるのではありませんか。
- fact COFFEE-001: ICO Composite Indicator Price（I-CIP）は2026年9月に平均262.18米セント／ポンドとなり、2026年8月比で8.7%下落した。ICOは、ブラジルの収穫物の供給増加と潤沢な供給見通しが価格を押し下げた一方、認証済みアラビカ在庫の少なさとエルニーニョをめぐる不確実性が下支えしたと報告した。
  scope: 国際的なICO Composite Indicator Price。コーヒー4グループの指標を含む
  conditions: ICOの2026年9月市場報告。値下がり要因と下支え要因の双方を記録
  numeric_value: 平均262.18米セント／ポンド、前月比-8.7% (numeric_scope: 世界のコーヒー指標価格の月平均。特定の小売商品価格ではない)
  date_or_period: 2026年9月（8月比）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: ICOの報告する市場要因。これだけで消費者価格が同月に下がったとは言えない。報告ページは2026年10月9日時点で9月報告を掲載。

### s8  (confidence max 0.4)
- issue_id: `coffee_prices__run_e_tone_01__b1b__d9b77190__rf20261011T052407Z-71d5__s8`
- sentence: The price measure reported by the International Coffee Organization fell 8.7% from the previous month.
- before: But the price tag in a shop may not change right away. / When you see a price tag that makes you want to say, “Haven’t you heard the news?”, it seems there is a time lag.
- after: The reason, it said, was that more beans harvested in Brazil had entered the market, and a good supply was expected to continue. / The US Department of Agriculture said that earlier high prices came from several factors happening at once: bad weather in Brazil and Vietnam, fewer beans available for sale, and strong demand.
- detected_by: gemini35fl-A4(0.4)
- reason [数量時系列]: s8の「8.7%下落した」という数値はICOの指標価格についてのものですが、文中で時期や対象（指標価格であること）が十分に明示されていないため、生豆の価格が直接下がったと読者に誤解を与えませんか？
- fact COFFEE-001: ICO Composite Indicator Price（I-CIP）は2026年9月に平均262.18米セント／ポンドとなり、2026年8月比で8.7%下落した。ICOは、ブラジルの収穫物の供給増加と潤沢な供給見通しが価格を押し下げた一方、認証済みアラビカ在庫の少なさとエルニーニョをめぐる不確実性が下支えしたと報告した。
  scope: 国際的なICO Composite Indicator Price。コーヒー4グループの指標を含む
  conditions: ICOの2026年9月市場報告。値下がり要因と下支え要因の双方を記録
  numeric_value: 平均262.18米セント／ポンド、前月比-8.7% (numeric_scope: 世界のコーヒー指標価格の月平均。特定の小売商品価格ではない)
  date_or_period: 2026年9月（8月比）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: ICOの報告する市場要因。これだけで消費者価格が同月に下がったとは言えない。報告ページは2026年10月9日時点で9月報告を掲載。

### s11  (confidence max 0.38)
- issue_id: `coffee_prices__run_e_tone_01__b1b__d9b77190__rf20261011T052407Z-71d5__s11`
- sentence: Meanwhile, US consumer price data showed that the price of coffee was 6.1% higher than in the same month a year earlier.
- before: The reason, it said, was that more beans harvested in Brazil had entered the market, and a good supply was expected to continue. / The US Department of Agriculture said that earlier high prices came from several factors happening at once: bad weather in Brazil and Vietnam, fewer beans available for sale, and strong demand.
- after: It may leave you wondering, “Did prices go down or up?” / But the data covers a different month from the bean price measure.
- detected_by: luna-A3(0.38)
- reason [その他]: 「the price of coffee」と「米CPIの『Coffee』項目の指数」では示している対象が異なるのではありませんか。
- fact COFFEE-015: BLSの2026年8月CPIでは、米国の「Coffee」項目の指数は前年同月比6.1%上昇だった。
  scope: 米都市消費者（CPI-U）におけるコーヒー項目
  conditions: BLSの前年同月比指数。特定ブランドの価格やカフェの一杯の価格ではない
  numeric_value: 前年同月比+6.1% (numeric_scope: 米国CPI-Uの「Coffee」項目の価格指数)
  date_or_period: 2026年8月のCPI。公表日は2026年9月11日
  notes_for_writer: 2026年8月時点では前年より高い一方、過去のピーク時の上昇率と同一視しない。

### s28  (confidence max 0.29)
- issue_id: `coffee_prices__run_e_tone_01__b1b__d9b77190__rf20261011T052407Z-71d5__s28`
- sentence: Even if bean prices fall, other costs do not always fall along with them.
- before: And a cup at a cafe comes with costs besides the beans. / One cafe operator in Chicago said that the cost of cups and labor, as well as the cost of buying beans, had been behind price increases.
- after: If you are waiting for the price of your usual cup to come down, think not only, “How much do beans cost now?” / but also, “When does the price of the beans reach here?”
- detected_by: luna-A4(0.29)
- reason [その他]: 「other costs do not always fall along with them」は、台帳の費用要因の記述だけでは、他の費用が豆価格と連動して下がらないことまで確認できないのではありませんか。
- fact COFFEE-018: APが2025年10月に取材したシカゴのカフェ運営者は、4店舗でラテ、カプチーノなどの価格を約15%引き上げたと述べた。同運営者は、前年より豆の購入費が15%高くなり、カップやスリーブ、人件費も費用要因になったと説明した。
  scope: シカゴのMomentum Coffee 4店舗の事例
  conditions: 一事業者への取材事例。全米カフェの平均的な値上げ率ではない
  numeric_value: 飲料価格約+15%、運営者による豆購入費前年同期比+15% (numeric_scope: 同社のラテ、カプチーノ等の価格、および同社の仕入れ費用)
  date_or_period: 2025年10月の報道時点
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 豆価格だけが値上げを引き起こしたと断定しない。事業者の説明として限定して記載する。
