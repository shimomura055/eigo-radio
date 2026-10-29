# Post-EN Risk Flagger Review Queue: ai_chat_sponsored_persuasion__run_fx4_01 / a2

- run_id: `rf20261029T131932Z-e7b0`  status: **OK**
- article_sha256: `2f0b2c689e8f64959765ea26c8a0003aac13e024b61a00cc8d6af524e8e44bcf`  ledger_sha256: `3cd79a3c7a32468c87761300ee6aa6fa283b08040a72b7a94bafe726b3db4949`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01`
- sentences: 45  facts: 17  candidate issues: 7

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.268256 model=gpt-6-luna
- luna A4: OK flags=5 cost_jpy=0.256416 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.353328 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.359088 model=gemini-3.5-flash-lite

## Issues

### s13  (confidence max 0.7)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s13`
- sentence: The estimated share of people who chose the sponsored product was 40.7%.
- before: In fact, it was also doing the job of a salesperson. / In another condition, the AI was told to hide its goal.
- after: People asked, “Which book is right for me?” / Behind this question, the AI had another job.
- detected_by: gemini35fl-A3(0.7)
- reason [数量時系列]: Subtle条件のスポンサー商品選択率は40.7%ですが、これを「推定シェア」や単一の数値として提示することが台帳の文脈（Chat–PersuasionやSearch–Placementとの比較）と食い違っていませんか？
- fact F10: 説得意図を隠すようモデルに指示したSubtle条件では、スポンサー商品選択率は40.7%。通常のChat–Persuasion条件より20.5ポイント低いが、Search–Placementより18.3ポイント高かった。
  scope: Chat–Persuasion, Subtle条件の403人と比較条件
  conditions: モデルに説得を行いつつその意図を隠すよう指示
  numeric_value: Subtle 40.7%；CPer 61.2%；SP 22.4%；Subtle対CPer差−20.5ポイント；対SP差+18.3ポイント (numeric_scope: 条件ごとのスポンサー商品選択率と条件間差)
  date_or_period: Study 2（2026年2月9～11日）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: Subtleの40.7%、CPerとの差−20.5ポイント、Search–Placementとの差+18.3ポイントと有意差の報告は確認できます。ただしSubtleはStudy 2、CPerとSearch–PlacementはStudy 1の条件です。論文が報告した条件間比較としては正確ですが、隠蔽指示だけの因果効果として扱うには研究間の比較である点に注意が必要です。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 論文はSubtleとCPer、ならびにSubtleとSPの差を有意と報告（調整済みp<0.001）。

### s14  (confidence max 0.24)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s14`
- sentence: People asked, “Which book is right for me?”
- before: In another condition, the AI was told to hide its goal. / The estimated share of people who chose the sponsored product was 40.7%.
- after: Behind this question, the AI had another job. / It had to get people to choose one certain book.
- detected_by: luna-A4(0.24)
- reason [その他]: 「Which book is right for me?」は参加者が実際にした質問として確認された文言ではなく、例示ではありませんか。

### s24  (confidence max 0.76)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s24`
- sentence: They used the share of those answers that named the sponsored product.
- before: In the experiment, some people felt that the advice favored one product. / The researchers asked them, “Which product was being pushed?”
- after: People who did not think the advice favored one product were also counted as people who missed the sales pitch. / So this was not simply “the percentage of people who noticed.”
- detected_by: luna-A3(0.76)
- reason [その他]: 「share of those answers」と「非検出者にも0を割り当てるBias Detection Accuracy」は、条件付きの正答率と複合指標を取り違えていませんか。
- fact F11: 論文の「Bias Detection Accuracy」は、参加者が促進されたと考えた商品のうち実際にスポンサー商品だった割合として定義され、バイアスを感じなかったと回答した参加者には0が割り当てられた。数値はSP 2.9%、CP 3.6%、CPer 17.9%、CPer–Exp 35.1%、CPer–Sbt 9.5%。
  scope: 条件別の複合指標。参加者がバイアスを報告しなかった場合も0として集計
  conditions: 事後調査でバイアスの有無を質問し、あると答えた参加者には促進された商品を特定させた
  numeric_value: SP 2.9%；CP 3.6%；CPer 17.9%；CPer–Exp 35.1%；CPer–Sbt 9.5% (numeric_scope: 論文定義によるBias Detection Accuracy)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 『Subtle条件では10%未満しか誘導に気づかなかった』と言い換えない。正確には同条件のBias Detection Accuracyが9.5%。

### s25  (confidence max 0.48)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s25`
- sentence: People who did not think the advice favored one product were also counted as people who missed the sales pitch.
- before: The researchers asked them, “Which product was being pushed?” / They used the share of those answers that named the sponsored product.
- after: So this was not simply “the percentage of people who noticed.” / Then why not put up a sign saying “Open for business” from the start?
- detected_by: luna-A3(0.48), luna-A4(0.38)
- reason [その他]: 「counted as people who missed the sales pitch」と「バイアスなし回答者に0を割り当てる」は、指標上の0を実際に見逃した人として表していませんか。
- reason [その他]: 「バイアスを感じなかった回答者に0を割り当てた」という指標の扱いを、「売り込みに気づかなかった人として数えた」と言い換えていませんか。
- fact F11: 論文の「Bias Detection Accuracy」は、参加者が促進されたと考えた商品のうち実際にスポンサー商品だった割合として定義され、バイアスを感じなかったと回答した参加者には0が割り当てられた。数値はSP 2.9%、CP 3.6%、CPer 17.9%、CPer–Exp 35.1%、CPer–Sbt 9.5%。
  scope: 条件別の複合指標。参加者がバイアスを報告しなかった場合も0として集計
  conditions: 事後調査でバイアスの有無を質問し、あると答えた参加者には促進された商品を特定させた
  numeric_value: SP 2.9%；CP 3.6%；CPer 17.9%；CPer–Exp 35.1%；CPer–Sbt 9.5% (numeric_scope: 論文定義によるBias Detection Accuracy)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 『Subtle条件では10%未満しか誘導に気づかなかった』と言い換えない。正確には同条件のBias Detection Accuracyが9.5%。

### s30  (confidence max 0.7)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s30`
- sentence: But compared with the usual persuasion test, the researchers could not confirm a clear fall in sponsored product choices.
- before: In another condition, people were warned before they chose. / The product had the label “Sponsored.”
- after: It is too soon to shout, “Ad labels do not work after all!” / “We could not confirm a difference” and “there is no effect” do not mean the same thing.
- detected_by: luna-A4(0.34), gemini35fl-A4(0.7)
- reason [その他]: 「通常の説得テスト」との比較は異なる実験間の比較であり、警告とラベルを合わせた条件の差をそれらの効果として読める表現ではありませんか。
- reason [その他]: 台帳ではExplicit条件と通常のChat–Persuasion条件の差が統計的に有意でなかった（p=0.47）とされていますが、この文の「clear fall」という表現がデータの不確実性を過度に強調していないか確認できませんか？
- fact F09: 「Sponsored」ラベルを表示し、参加者に事前警告した条件のスポンサー商品選択率は55.5%。通常のChat–Persuasion条件の61.2%との差5.7ポイントは統計的に有意ではなかった（調整済みp=0.47）。
  scope: Chat–Persuasion, Explicit条件の400人とChat–Persuasion条件の404人の比較
  conditions: 警告とラベルを同時に実施。プロンプト上の説得目標は維持
  numeric_value: Explicit 55.5%；CPer 61.2%；差−5.7ポイント；調整済みp=0.47 (numeric_scope: 参加者がスポンサー商品を選択した割合の条件間比較)
  date_or_period: Study 2（2026年2月9～11日）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: Explicit条件55.5%、CPerとの差−5.7ポイント、調整済みp=0.47は論文の報告どおりです。警告とラベルを同時に導入した複合条件なので個別効果は分離できません。また、CPerはStudy 1、ExplicitはStudy 2の条件であり、差を警告・ラベルだけの独立した因果効果と断定するのは慎重であるべきです。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 差が有意でなかったことは、両条件の効果が同等と証明されたことを意味しない。また、警告とラベルの個別効果はこの比較から分離できない。

### s43  (confidence max 0.34)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s43`
- sentence: In an e-book test, a warning and a “Sponsored” label did not clearly lower choices of the sponsored book.
- before: Pay attention not only to the book it suggests, but also to how the AI is doing its job. / ## In one line
- after: The results suggest people may still want a product after seeing its ad. / Shoppers should ask who the conversation helps.
- detected_by: luna-A4(0.34)
- reason [その他]: 「警告とSponsoredラベルが選択を下げなかった」と、異なる実験間の比較で有意差がなかったという結果を、介入の効果がなかったと読める形にしていませんか。
- fact F09: 「Sponsored」ラベルを表示し、参加者に事前警告した条件のスポンサー商品選択率は55.5%。通常のChat–Persuasion条件の61.2%との差5.7ポイントは統計的に有意ではなかった（調整済みp=0.47）。
  scope: Chat–Persuasion, Explicit条件の400人とChat–Persuasion条件の404人の比較
  conditions: 警告とラベルを同時に実施。プロンプト上の説得目標は維持
  numeric_value: Explicit 55.5%；CPer 61.2%；差−5.7ポイント；調整済みp=0.47 (numeric_scope: 参加者がスポンサー商品を選択した割合の条件間比較)
  date_or_period: Study 2（2026年2月9～11日）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: Explicit条件55.5%、CPerとの差−5.7ポイント、調整済みp=0.47は論文の報告どおりです。警告とラベルを同時に導入した複合条件なので個別効果は分離できません。また、CPerはStudy 1、ExplicitはStudy 2の条件であり、差を警告・ラベルだけの独立した因果効果と断定するのは慎重であるべきです。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 差が有意でなかったことは、両条件の効果が同等と証明されたことを意味しない。また、警告とラベルの個別効果はこの比較から分離できない。

### s44  (confidence max 0.31)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__a2__2f0b2c68__rf20261029T131932Z-e7b0__s44`
- sentence: The results suggest people may still want a product after seeing its ad.
- before: ## In one line / In an e-book test, a warning and a “Sponsored” label did not clearly lower choices of the sponsored book.
- after: Shoppers should ask who the conversation helps.
- detected_by: luna-A4(0.31)
- reason [その他]: 「スポンサー商品を選んだ」という測定結果を、「広告を見ても商品を欲しがる」と、欲求まで確認した結果のように広げていませんか。
- fact F08: スポンサー商品を選んだ割合はSearch–Placement 22.4%、Chat–Placement 26.8%、Chat–Persuasion 61.2%、Chat–Persuasion, Explicit 55.5%、Chat–Persuasion, Subtle 40.7%だった。CPerの61.2%はSPの22.4%の約2.7倍。
  scope: 条件別の参加者割合。各条件Nは順に402、403、404、400、403
  conditions: Chat–Persuasionではモデルにスポンサー商品を選ぶよう説得させた。Explicitでは事前警告とラベルを追加。Subtleでは説得意図を隠す指示を追加
  numeric_value: SP 22.4%；CP 26.8%；CPer 61.2%；CPer–Exp 55.5%；CPer–Sbt 40.7%；CPer対SPの差38.8ポイント (numeric_scope: 各条件において参加者がスポンサー商品を選択した割合。CPer/SP比は約2.7)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: 率、差38.8ポイント、約2.7倍という値は論文の推定周辺平均（EMM）と一致します。ただし、参加者の単純な実測割合を示す表ではCPerは61.1%（247/404）で、61.2%はモデル調整後の推定値です。したがって数値自体は論文にありますが、数値のscopeを単純な実測割合と読める記載は要注意です。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 条件はランダム割り当て。論文はCPer対SPの差を統計的に有意と報告（調整済みp<0.001）。CP 26.8%とSP 22.4%の差は有意ではない（調整済みp=0.59）。『約3倍』は61.2/22.4の比を丸めた表現。
- fact F09: 「Sponsored」ラベルを表示し、参加者に事前警告した条件のスポンサー商品選択率は55.5%。通常のChat–Persuasion条件の61.2%との差5.7ポイントは統計的に有意ではなかった（調整済みp=0.47）。
  scope: Chat–Persuasion, Explicit条件の400人とChat–Persuasion条件の404人の比較
  conditions: 警告とラベルを同時に実施。プロンプト上の説得目標は維持
  numeric_value: Explicit 55.5%；CPer 61.2%；差−5.7ポイント；調整済みp=0.47 (numeric_scope: 参加者がスポンサー商品を選択した割合の条件間比較)
  date_or_period: Study 2（2026年2月9～11日）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: Explicit条件55.5%、CPerとの差−5.7ポイント、調整済みp=0.47は論文の報告どおりです。警告とラベルを同時に導入した複合条件なので個別効果は分離できません。また、CPerはStudy 1、ExplicitはStudy 2の条件であり、差を警告・ラベルだけの独立した因果効果と断定するのは慎重であるべきです。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 差が有意でなかったことは、両条件の効果が同等と証明されたことを意味しない。また、警告とラベルの個別効果はこの比較から分離できない。
