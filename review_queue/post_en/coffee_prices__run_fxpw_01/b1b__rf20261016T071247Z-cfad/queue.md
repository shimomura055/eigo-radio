# Post-EN Risk Flagger Review Queue: coffee_prices__run_fxpw_01 / b1b

- run_id: `rf20261016T071247Z-cfad`  status: **OK**
- article_sha256: `4f13cbba34ccf6b68df6ce0c3136af2a137636e3afc61c6812afe146dc8eae99`  ledger_sha256: `1e4c771ecb8d579d0ae45512fa3536ea1a7d13c2a001c38f55991e4dfa6946c9`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FXPW-COFFEE-E2E-01`
- sentences: 41  facts: 17  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.175888 model=gpt-6-luna
- luna A4: OK flags=0 cost_jpy=0.152048 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.336048 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.341808 model=gemini-3.5-flash-lite

## Issues

### s18  (confidence max 0.32)
- issue_id: `coffee_prices__run_fxpw_01__b1b__4f13cbba__rf20261016T071247Z-cfad__s18`
- sentence: Before thinking about how to brew them, the question was whether there would be beans to brew at all.
- before: Hopes that the next harvest would recover had also faded. / “Will there be enough beans?”
- after: Turn the pages of the record, and we find that in February, before summer, the futures price for Arabica coffee in New York reached an all-time high. / This was not the price of ground coffee in stores, but the market price for trading coffee beans.
- detected_by: luna-A3(0.32)
- reason [不在断定]: “whether there would be beans to brew at all” は、台帳の供給懸念を超えて豆がまったく得られない可能性を示す表現ではありませんか。
- fact F07: 2024年のブラジルの干ばつは次期作の回復見通しを弱め、ブラジル産コーヒーの供給懸念を強めたとReutersは報じた。Reuters記事は、ベトナムの生産や輸出見通しにも懸念があると伝えた。
  scope: ブラジル（主にアラビカ供給国）およびベトナム（ロブスタ主要生産国）
  conditions: 市場参加者・ディーラーの見通しを含む報道
  date_or_period: 2024年の天候と2025年作柄見通し
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: 天候が各品種の世界価格に与えた寄与率は示されていない。
  notes_for_writer: 気象要因を供給懸念の一要素として記述し、価格上昇の唯一の原因とはしない。

### s19  (confidence max 0.3)
- issue_id: `coffee_prices__run_fxpw_01__b1b__4f13cbba__rf20261016T071247Z-cfad__s19`
- sentence: Turn the pages of the record, and we find that in February, before summer, the futures price for Arabica coffee in New York reached an all-time high.
- before: “Will there be enough beans?” / Before thinking about how to brew them, the question was whether there would be beans to brew at all.
- after: This was not the price of ground coffee in stores, but the market price for trading coffee beans. / The market alarm had already sounded.
- detected_by: gemini35fl-A3(0.3), gemini35fl-A4(0.3)
- reason [数量時系列]: F02では「2025年2月10日」とされているニューヨークのアラビカ先物の史上最高値の記録時期について、s19では「2月に、夏前に」と表現されていますが、時期の認識に齟齬はありませんか。
- reason [数量時系列]: F02では2025年2月にニューヨークのアラビカ先物が史上最高値を記録したとありますが、s19の「before summer」という表現は時期の順序として正確ですか？
- fact F02: 2025年2月、ニューヨークのアラビカ先物は1ポンド当たり4.30米ドルを超える史上最高値を記録した。
  scope: ICEニューヨーク市場のアラビカ先物
  conditions: 先物価格の高値。小売価格ではない
  numeric_value: 4.30米ドル/ポンド超 (numeric_scope: 2025年2月10日のニューヨーク市場アラビカ先物)
  date_or_period: 2025年2月10日
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「4.30米ドル超」は先物価格。記事は供給の限られた状況や市場参加者の見方も報じているが、この価格記録自体から単一原因を断定しない。
