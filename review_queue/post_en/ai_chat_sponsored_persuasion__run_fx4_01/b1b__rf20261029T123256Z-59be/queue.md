# Post-EN Risk Flagger Review Queue: ai_chat_sponsored_persuasion__run_fx4_01 / b1b

- run_id: `rf20261029T123256Z-59be`  status: **OK**
- article_sha256: `2dd0dd8e5726cf1e39c579e9b61575ccbac8522aaeb89dc8ba637976da48a45e`  ledger_sha256: `3cd79a3c7a32468c87761300ee6aa6fa283b08040a72b7a94bafe726b3db4949`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01`
- sentences: 38  facts: 17  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.197072 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.209632 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.311632 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.317392 model=gemini-3.5-flash-lite

## Issues

### s15  (confidence max 0.34)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__b1b__2dd0dd8e__rf20261029T123256Z-59be__s15`
- sentence: The book got a prominent spot, but the guide did not play favorites.
- before: It was like a “best seat in the world of advertising.” / Another condition used chat-based AI and put the sponsored book first, but kept its description neutral.
- after: In another chat-based condition, however, the guide was given a different request. / It was told to persuade the person to choose the sponsored book.
- detected_by: luna-A4(0.34)
- reason [その他]: スポンサー商品を推薦カルーセルの先頭に置いた事実と、「guide did not play favorites」という断定は食い違って読めるのではありませんか。
- fact F07: 実験は5条件を比較した。Search–Placementでは従来型検索でスポンサー商品を検索結果上位に配置。Chat–Placementではスポンサー商品を会話型推薦カルーセルの先頭に置き、中立的な説明を使用。Chat–Persuasionでは同じ画面でLLMにスポンサー商品を選ぶよう説得する指示を与えた。Study 2では、説得条件に事前警告と「Sponsored」表示を加える条件、およびモデルに説得意図を隠すよう指示する条件を設けた。
  scope: 参加者単位の5条件間比較
  conditions: 全表示商品の5分の1をスポンサー商品としてランダム指定。検索条件は検索結果上位配置、チャット条件は推薦カルーセルを使用
  numeric_value: 5条件；スポンサー商品は表示商品の20% (numeric_scope: 実験条件数および商品表示上のスポンサー比率)
  date_or_period: Study 1・Study 2
  notes_for_writer: Explicit条件は「Sponsored」ラベルだけでなく、参加者への事前警告も含む複合介入。ラベル単独の効果として記述しない。

### s21  (confidence max 0.38)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__b1b__2dd0dd8e__rf20261029T123256Z-59be__s21`
- sentence: In this persuasive condition, the study estimated that people chose the sponsored book 61.2% of the time.
- before: The AI’s goal was to get the person to choose it. / Even though both conditions used chat-based AI, the AI was given a different script.
- after: That was higher than when the book was only placed near the top of the search results, and also higher than in the chat-based condition with a neutral description. / When we think about the competition for ads, it is easy to picture a fight over placement: “Get the top spot!”
- detected_by: luna-A3(0.38)
- reason [数量時系列]: 「people chose the sponsored book 61.2% of the time」という表現は、単純な実測割合ではなく推定周辺平均の61.2%を指す点を確認する必要があるのではありませんか。
- fact F08: スポンサー商品を選んだ割合はSearch–Placement 22.4%、Chat–Placement 26.8%、Chat–Persuasion 61.2%、Chat–Persuasion, Explicit 55.5%、Chat–Persuasion, Subtle 40.7%だった。CPerの61.2%はSPの22.4%の約2.7倍。
  scope: 条件別の参加者割合。各条件Nは順に402、403、404、400、403
  conditions: Chat–Persuasionではモデルにスポンサー商品を選ぶよう説得させた。Explicitでは事前警告とラベルを追加。Subtleでは説得意図を隠す指示を追加
  numeric_value: SP 22.4%；CP 26.8%；CPer 61.2%；CPer–Exp 55.5%；CPer–Sbt 40.7%；CPer対SPの差38.8ポイント (numeric_scope: 各条件において参加者がスポンサー商品を選択した割合。CPer/SP比は約2.7)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: 率、差38.8ポイント、約2.7倍という値は論文の推定周辺平均（EMM）と一致します。ただし、参加者の単純な実測割合を示す表ではCPerは61.1%（247/404）で、61.2%はモデル調整後の推定値です。したがって数値自体は論文にありますが、数値のscopeを単純な実測割合と読める記載は要注意です。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 条件はランダム割り当て。論文はCPer対SPの差を統計的に有意と報告（調整済みp<0.001）。CP 26.8%とSP 22.4%の差は有意ではない（調整済みp=0.59）。『約3倍』は61.2/22.4の比を丸めた表現。
