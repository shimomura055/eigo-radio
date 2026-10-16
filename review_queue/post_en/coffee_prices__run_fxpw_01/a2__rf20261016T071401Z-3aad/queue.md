# Post-EN Risk Flagger Review Queue: coffee_prices__run_fxpw_01 / a2

- run_id: `rf20261016T071401Z-3aad`  status: **OK**
- article_sha256: `b836713dd23a67a658078abfdcc486f8f0ff8664e45676b5ac44a684a2a89ba4`  ledger_sha256: `1e4c771ecb8d579d0ae45512fa3536ea1a7d13c2a001c38f55991e4dfa6946c9`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FXPW-COFFEE-E2E-01`
- sentences: 49  facts: 17  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.192992 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.218592 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.16297 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.13673 model=gemini-3.5-flash-lite

## Issues

### s18  (confidence max 0.36)
- issue_id: `coffee_prices__run_fxpw_01__a2__b836713d__rf20261016T071401Z-3aad__s18`
- sentence: People had also stopped hoping that the next harvest would be better.
- before: The investigation leads us to Brazil. / A drought was happening there.
- after: “Will there be enough beans?” / Before we think about how to brew them, we must ask if there will be any beans to brew at all.
- detected_by: luna-A3(0.36), luna-A4(0.34)
- reason [その他]: 「people had also stopped hoping」は、台帳の「次期作の回復見通しを弱め、供給懸念を強めた」より強い断定ではありませんか。
- reason [その他]: 「people had stopped hoping」と、Factの「次期作の回復見通しを弱めた」では、人々の期待についての断定の強さが異なるのではありませんか。
- fact F07: 2024年のブラジルの干ばつは次期作の回復見通しを弱め、ブラジル産コーヒーの供給懸念を強めたとReutersは報じた。Reuters記事は、ベトナムの生産や輸出見通しにも懸念があると伝えた。
  scope: ブラジル（主にアラビカ供給国）およびベトナム（ロブスタ主要生産国）
  conditions: 市場参加者・ディーラーの見通しを含む報道
  date_or_period: 2024年の天候と2025年作柄見通し
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: 天候が各品種の世界価格に与えた寄与率は示されていない。
  notes_for_writer: 気象要因を供給懸念の一要素として記述し、価格上昇の唯一の原因とはしない。

### s29  (confidence max 0.7)
- issue_id: `coffee_prices__run_fxpw_01__a2__b836713d__rf20261016T071401Z-3aad__s29`
- sentence: Reuters also reported that U.S. tariffs put in place during summer raised the price of the beans themselves.
- before: No. / That would be deciding too soon, too.
- after: They did play a part. / But we must put events in the right order.
- detected_by: gemini35fl-A3(0.7)
- reason [その他]: Reutersが報じたのは「輸入品に課した関税が原料豆価格を押し上げた」ことですが、「beans themselves」の価格を直接引き上げたとする点や文脈がFactと一致しているか確認できませんか？
- fact F09: Reutersは、2025年夏に米国がコーヒー生産国を含む輸入品に課した関税が原料豆価格を押し上げたと報じた。同社記事によると、米国の小売コーヒー価格上昇の大部分は、それ以前の供給不足と生豆価格上昇によるもので、関税の影響は当時まだ供給網を通じて消費者に十分反映されていなかった。
  scope: 米国の輸入コーヒーおよび米国消費者向け価格
  conditions: 2025年12月19日付Reuters報道時点の評価。関税の市場影響と小売への転嫁時期を区別
  date_or_period: 2025年夏～2025年12月の報道時点
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Reutersが報じた専門家・業界関係者の評価。関税を小売価格上昇の唯一または主因と断定しない。
