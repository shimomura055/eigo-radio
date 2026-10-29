# Post-EN Risk Flagger Review Queue: ai_chat_sponsored_persuasion__run_fx4_01 / b1b

- run_id: `rf20261029T131820Z-9cc9`  status: **OK**
- article_sha256: `f32269d1128c10e793a46ea286ff1afc619bbe51c5b9aa2ffb14dd409a52e3e9`  ledger_sha256: `3cd79a3c7a32468c87761300ee6aa6fa283b08040a72b7a94bafe726b3db4949`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01`
- sentences: 40  facts: 17  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.20704 model=gpt-6-luna
- luna A4: OK flags=4 cost_jpy=0.30752 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.312448 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.318208 model=gemini-3.5-flash-lite

## Issues

### s21  (confidence max 0.72)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__b1b__f32269d1__rf20261029T131820Z-9cc9__s21`
- sentence: The researchers used the share of those answers that named the sponsored product.
- before: This number needs an instruction manual. / In the experiment, people who felt the recommendations were biased were asked, “Which product was being pushed?”
- after: People who did not feel that the recommendations were biased were also counted as having failed to spot the sales pitch. / So this was not simply “the percentage of people who noticed.”
- detected_by: luna-A3(0.72), luna-A4(0.54)
- reason [その他]: 「those answersのうちスポンサー商品を挙げた割合」という説明は、バイアスを感じなかった参加者を0として集計した指標の定義と食い違っていませんか。
- reason [その他]: 「回答のうちスポンサー商品を挙げた割合」だけで定義したように読め、バイアスを感じなかった参加者を0として扱う定義が抜けているのではありませんか。
- fact F11: 論文の「Bias Detection Accuracy」は、参加者が促進されたと考えた商品のうち実際にスポンサー商品だった割合として定義され、バイアスを感じなかったと回答した参加者には0が割り当てられた。数値はSP 2.9%、CP 3.6%、CPer 17.9%、CPer–Exp 35.1%、CPer–Sbt 9.5%。
  scope: 条件別の複合指標。参加者がバイアスを報告しなかった場合も0として集計
  conditions: 事後調査でバイアスの有無を質問し、あると答えた参加者には促進された商品を特定させた
  numeric_value: SP 2.9%；CP 3.6%；CPer 17.9%；CPer–Exp 35.1%；CPer–Sbt 9.5% (numeric_scope: 論文定義によるBias Detection Accuracy)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 『Subtle条件では10%未満しか誘導に気づかなかった』と言い換えない。正確には同条件のBias Detection Accuracyが9.5%。

### s22  (confidence max 0.68)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__b1b__f32269d1__rf20261029T131820Z-9cc9__s22`
- sentence: People who did not feel that the recommendations were biased were also counted as having failed to spot the sales pitch.
- before: In the experiment, people who felt the recommendations were biased were asked, “Which product was being pushed?” / The researchers used the share of those answers that named the sponsored product.
- after: So this was not simply “the percentage of people who noticed.” / Then why not put up a sign saying “Open for business” from the start?
- detected_by: luna-A4(0.68)
- reason [その他]: 「バイアスを感じなかった人」を実際に「説得を見抜けなかった人」と断定しており、指標上0を割り当てたという事実より強い意味になっているのではありませんか。
- fact F11: 論文の「Bias Detection Accuracy」は、参加者が促進されたと考えた商品のうち実際にスポンサー商品だった割合として定義され、バイアスを感じなかったと回答した参加者には0が割り当てられた。数値はSP 2.9%、CP 3.6%、CPer 17.9%、CPer–Exp 35.1%、CPer–Sbt 9.5%。
  scope: 条件別の複合指標。参加者がバイアスを報告しなかった場合も0として集計
  conditions: 事後調査でバイアスの有無を質問し、あると答えた参加者には促進された商品を特定させた
  numeric_value: SP 2.9%；CP 3.6%；CPer 17.9%；CPer–Exp 35.1%；CPer–Sbt 9.5% (numeric_scope: 論文定義によるBias Detection Accuracy)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 『Subtle条件では10%未満しか誘導に気づかなかった』と言い換えない。正確には同条件のBias Detection Accuracyが9.5%。

### s39  (confidence max 0.47)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__b1b__f32269d1__rf20261029T131820Z-9cc9__s39`
- sentence: In an e-book experiment, a warning and a “Sponsored” label did not clearly reduce how often people chose the sponsored book.
- before: It’s worth paying attention not only to the recommended book, but also to how the recommender is doing its job. / ## In one line
- after: The results suggest people may still want a product after spotting its ad, so shoppers should ask whose interests the conversation serves.
- detected_by: luna-A4(0.47)
- reason [その他]: 「警告とラベルが選択を減らさなかった」と介入の因果効果まで述べており、通常条件とExplicit条件が別実験の比較である点を越えているのではありませんか。
- fact F09: 「Sponsored」ラベルを表示し、参加者に事前警告した条件のスポンサー商品選択率は55.5%。通常のChat–Persuasion条件の61.2%との差5.7ポイントは統計的に有意ではなかった（調整済みp=0.47）。
  scope: Chat–Persuasion, Explicit条件の400人とChat–Persuasion条件の404人の比較
  conditions: 警告とラベルを同時に実施。プロンプト上の説得目標は維持
  numeric_value: Explicit 55.5%；CPer 61.2%；差−5.7ポイント；調整済みp=0.47 (numeric_scope: 参加者がスポンサー商品を選択した割合の条件間比較)
  date_or_period: Study 2（2026年2月9～11日）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: Explicit条件55.5%、CPerとの差−5.7ポイント、調整済みp=0.47は論文の報告どおりです。警告とラベルを同時に導入した複合条件なので個別効果は分離できません。また、CPerはStudy 1、ExplicitはStudy 2の条件であり、差を警告・ラベルだけの独立した因果効果と断定するのは慎重であるべきです。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 差が有意でなかったことは、両条件の効果が同等と証明されたことを意味しない。また、警告とラベルの個別効果はこの比較から分離できない。

### s40  (confidence max 0.56)
- issue_id: `ai_chat_sponsored_persuasion__run_fx4_01__b1b__f32269d1__rf20261029T131820Z-9cc9__s40`
- sentence: The results suggest people may still want a product after spotting its ad, so shoppers should ask whose interests the conversation serves.
- before: ## In one line / In an e-book experiment, a warning and a “Sponsored” label did not clearly reduce how often people chose the sponsored book.
- detected_by: luna-A3(0.56), luna-A4(0.31)
- reason [その他]: 「広告に気づいた人も商品を欲しがる」という含意は、選択率と自己申告・商品特定精度という別々の集計から、同じ参加者が気づいたうえで選んだと確認できる範囲を超えていませんか。
- reason [その他]: 「広告に気づいた人がそれでも商品を欲しがった」と個人単位の関係を示唆していますが、自己申告と選択率の集計結果だけではその関係を確認できないのではありませんか。
- fact F08: スポンサー商品を選んだ割合はSearch–Placement 22.4%、Chat–Placement 26.8%、Chat–Persuasion 61.2%、Chat–Persuasion, Explicit 55.5%、Chat–Persuasion, Subtle 40.7%だった。CPerの61.2%はSPの22.4%の約2.7倍。
  scope: 条件別の参加者割合。各条件Nは順に402、403、404、400、403
  conditions: Chat–Persuasionではモデルにスポンサー商品を選ぶよう説得させた。Explicitでは事前警告とラベルを追加。Subtleでは説得意図を隠す指示を追加
  numeric_value: SP 22.4%；CP 26.8%；CPer 61.2%；CPer–Exp 55.5%；CPer–Sbt 40.7%；CPer対SPの差38.8ポイント (numeric_scope: 各条件において参加者がスポンサー商品を選択した割合。CPer/SP比は約2.7)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: 率、差38.8ポイント、約2.7倍という値は論文の推定周辺平均（EMM）と一致します。ただし、参加者の単純な実測割合を示す表ではCPerは61.1%（247/404）で、61.2%はモデル調整後の推定値です。したがって数値自体は論文にありますが、数値のscopeを単純な実測割合と読める記載は要注意です。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 条件はランダム割り当て。論文はCPer対SPの差を統計的に有意と報告（調整済みp<0.001）。CP 26.8%とSP 22.4%の差は有意ではない（調整済みp=0.59）。『約3倍』は61.2/22.4の比を丸めた表現。
- fact F12: バイアスを感じたと自己申告した参加者は、CPerで22.3%、CPer–Sbtで14.6%。バイアスに気づいた人に限った商品特定の精度は、CPerで80.1%、CPer–Sbtで68.0%。
  scope: 各条件の参加者全体に占める自己申告割合、および自己申告者に限った条件付き精度
  conditions: 事後調査でバイアスを感じたと回答した場合に、促進された商品を特定
  numeric_value: 自己申告：CPer 22.3%、CPer–Sbt 14.6%；自己申告者内の特定精度：CPer 80.1%、CPer–Sbt 68.0% (numeric_scope: 自己申告割合の分母は各条件の全参加者。特定精度の分母はバイアスを感じたと回答した参加者)
  date_or_period: 2つのランダム化実験の結果
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: F11の複合指標と区別する。『気づいた人の大半は商品を特定できた』という記述は条件付き精度を指す。
- fact F09: 「Sponsored」ラベルを表示し、参加者に事前警告した条件のスポンサー商品選択率は55.5%。通常のChat–Persuasion条件の61.2%との差5.7ポイントは統計的に有意ではなかった（調整済みp=0.47）。
  scope: Chat–Persuasion, Explicit条件の400人とChat–Persuasion条件の404人の比較
  conditions: 警告とラベルを同時に実施。プロンプト上の説得目標は維持
  numeric_value: Explicit 55.5%；CPer 61.2%；差−5.7ポイント；調整済みp=0.47 (numeric_scope: 参加者がスポンサー商品を選択した割合の条件間比較)
  date_or_period: Study 2（2026年2月9～11日）
  causal_strength: CAUSAL_STATED_BY_SOURCE
  ambiguity_note: Explicit条件55.5%、CPerとの差−5.7ポイント、調整済みp=0.47は論文の報告どおりです。警告とラベルを同時に導入した複合条件なので個別効果は分離できません。また、CPerはStudy 1、ExplicitはStudy 2の条件であり、差を警告・ラベルだけの独立した因果効果と断定するのは慎重であるべきです。 ([arxiv.org](https://arxiv.org/abs/2604.04263))
  notes_for_writer: 差が有意でなかったことは、両条件の効果が同等と証明されたことを意味しない。また、警告とラベルの個別効果はこの比較から分離できない。
