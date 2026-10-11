# Post-EN Risk Flagger Review Queue: coffee_prices__run_e_tone_01 / a2

- run_id: `rf20261011T052458Z-19b1`  status: **OK**
- article_sha256: `a3cc7bb98af7526f55485b6a589354eeb36eb74a80bbd43a5e5be151915e4ff7`  ledger_sha256: `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `COFFEE_NEW_TONE_E2E_01`
- sentences: 41  facts: 19  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.2268 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.27256 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.188883 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.197843 model=gemini-3.5-flash-lite

## Issues

### s1  (confidence max 0.35)
- issue_id: `coffee_prices__run_e_tone_01__a2__a3cc7bb9__rf20261011T052458Z-19b1__s1`
- sentence: # Coffee Bean Prices Fall.
- after: Are Price Tags Still on a Journey? / “Beans cost less now!”
- detected_by: luna-A3(0.34), luna-A4(0.35)
- reason [主体対象入替]: 「Coffee Bean Prices Fall」は、特定の国際指標であるICO複合価格の下落を、コーヒー豆全般の価格下落に広げて述べているのではありませんか？
- reason [主体対象入替]: 「Coffee Bean Prices」は、台帳が示すICO複合価格指数の下落より広い範囲を指しているのではありませんか。
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

### s3  (confidence max 0.35)
- issue_id: `coffee_prices__run_e_tone_01__a2__a3cc7bb9__rf20261011T052458Z-19b1__s3`
- sentence: “Beans cost less now!”
- before: # Coffee Bean Prices Fall. / Are Price Tags Still on a Journey?
- after: When you hear that, your wallet pumps its fist. / You already imagine your usual cup costing less, too.
- detected_by: luna-A4(0.35)
- reason [主体対象入替]: 「Beans cost less now」は、台帳が示すICO複合価格指数の下落を、豆全般の価格低下へ広げているのではありませんか。
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

### s34  (confidence max 0.8)
- issue_id: `coffee_prices__run_e_tone_01__a2__a3cc7bb9__rf20261011T052458Z-19b1__s34`
- sentence: A person who runs a cafe in Chicago said three costs had pushed prices up.
- before: It is too soon to mark the date on your calendar. / A cafe cup also costs money for more than just beans.
- after: These were cups, workers’ pay, and buying beans. / Even if bean prices fall, other costs do not always fall with them.
- detected_by: gemini35fl-A3(0.8), gemini35fl-A4(0.8)
- reason [数量時系列]: シカゴのカフェ運営者が挙げた店舗数は、台帳では4店舗ですが、「3つ」になっていませんか？
- reason [数量時系列]: s34のシカゴのカフェ運営者が挙げた店舗数は、COFFEE-018の「4店舗」と食い違っていませんか？
- fact COFFEE-018: APが2025年10月に取材したシカゴのカフェ運営者は、4店舗でラテ、カプチーノなどの価格を約15%引き上げたと述べた。同運営者は、前年より豆の購入費が15%高くなり、カップやスリーブ、人件費も費用要因になったと説明した。
  scope: シカゴのMomentum Coffee 4店舗の事例
  conditions: 一事業者への取材事例。全米カフェの平均的な値上げ率ではない
  numeric_value: 飲料価格約+15%、運営者による豆購入費前年同期比+15% (numeric_scope: 同社のラテ、カプチーノ等の価格、および同社の仕入れ費用)
  date_or_period: 2025年10月の報道時点
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 豆価格だけが値上げを引き起こしたと断定しない。事業者の説明として限定して記載する。

### s36  (confidence max 0.28)
- issue_id: `coffee_prices__run_e_tone_01__a2__a3cc7bb9__rf20261011T052458Z-19b1__s36`
- sentence: Even if bean prices fall, other costs do not always fall with them.
- before: A person who runs a cafe in Chicago said three costs had pushed prices up. / These were cups, workers’ pay, and buying beans.
- after: If you are waiting for your usual cup to get cheaper, ask more than, “How much do beans cost now?” / Also ask, “When does the bean price reach here?”
- detected_by: luna-A4(0.28)
- reason [その他]: 「他の費用は豆価格と一緒には下がらないことがある」という点は、台帳の費用要因の説明だけでは確認できないのではありませんか。
- fact COFFEE-018: APが2025年10月に取材したシカゴのカフェ運営者は、4店舗でラテ、カプチーノなどの価格を約15%引き上げたと述べた。同運営者は、前年より豆の購入費が15%高くなり、カップやスリーブ、人件費も費用要因になったと説明した。
  scope: シカゴのMomentum Coffee 4店舗の事例
  conditions: 一事業者への取材事例。全米カフェの平均的な値上げ率ではない
  numeric_value: 飲料価格約+15%、運営者による豆購入費前年同期比+15% (numeric_scope: 同社のラテ、カプチーノ等の価格、および同社の仕入れ費用)
  date_or_period: 2025年10月の報道時点
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 豆価格だけが値上げを引き起こしたと断定しない。事業者の説明として限定して記載する。
