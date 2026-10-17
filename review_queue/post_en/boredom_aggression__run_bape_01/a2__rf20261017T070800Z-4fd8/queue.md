# Post-EN Risk Flagger Review Queue: boredom_aggression__run_bape_01 / a2

- run_id: `rf20261017T070800Z-4fd8`  status: **OK**
- article_sha256: `d9552126bde988c668c549a2c3301aa50ba2bda52f774c7100c9decc49a0b87f`  ledger_sha256: `701612d85b9a2a4eee67728abe4de3e85f0acabe28874826066b4df2d917b0ac`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `BAPE-E2E-01`
- sentences: 47  facts: 11  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.205712 model=gpt-6-luna
- luna A4: OK flags=2 cost_jpy=0.237152 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.160197 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.170314 model=gemini-3.5-flash-lite

## Issues

### s18  (confidence max 0.32)
- issue_id: `boredom_aggression__run_bape_01__a2__d9552126__rf20261017T070800Z-4fd8__s18`
- sentence: People who strongly liked seeing others suffer were more likely to make the other person’s reward smaller after watching the stone video than after watching the magician video.
- before: The stone on the screen stayed quiet, while the viewers were given “a little power.” / So, did boredom become fuel for being mean?
- after: For people who felt this less strongly, there was no clear difference. / You may want to say, “So, it really depends on personality.”
- detected_by: luna-A3(0.32)
- reason [数量時系列]: 文中の “after watching” は、Factの「動画を見ている間に選択した」と時点が食い違うのではありませんか。
- fact F05: Study 7では、参加者が動画を見ている間、別の参加者の報酬を減らす、増やす、または何もしない選択をできるようにした。著者らの分析では、退屈条件による報酬破壊の増加は、特性サディズムが高い参加者で認められ、低い参加者では認められなかった。
  scope: 米国MTurk参加者N=634、平均年齢31.3歳、女性50.5%。
  conditions: オンライン実験。退屈条件では、何も起きない石の5分動画を視聴しながら、別の参加者の報酬を10セント刻みで最大50セント減らすか増やすか選べた。対照条件では、マジシャンの5分動画を視聴。無作為割付。
  numeric_value: N=634；退屈条件n=299；対照条件n=335；動画各5分；報酬変更は10セント刻み、最大50セント (numeric_scope: Study 7の全参加者、条件別人数、動画時間、選択肢の金額範囲。)
  date_or_period: 論文公刊：2021年
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 結果は、特定のオンライン金銭選択課題における効果であり、日常生活全般の攻撃行動への直接的な一般化は避けること。著者らの報告では、低特性サディズム群では退屈条件と対照条件の差は有意でなかった。

### s26  (confidence max 0.32)
- issue_id: `boredom_aggression__run_bape_01__a2__d9552126__rf20261017T070800Z-4fd8__s26`
- sentence: People who watched the stone video were more likely to make another person’s reward smaller than people in the other groups.
- before: They could only make it smaller. / This time, it did not matter how strongly people liked seeing others suffer.
- after: If we look only at personality, we may miss something. / We need to ask not only what kind of person someone is, but also what they can do in that situation.
- detected_by: luna-A4(0.32)
- reason [その他]: 「the other groups」は石の動画条件が両方の対照群それぞれより高かったという意味ではありませんか。台帳で確認できる比較範囲を超えていないか、人間に確認してもらえますか。
- fact F06: Study 8では、別の参加者の報酬を減らす選択肢のみを設けた実験で、著者らは退屈条件の参加者が対照条件より報酬を減らす可能性が高かったと報告した。著者らの分析では、この条件では特性サディズムの高低にかかわらず退屈条件で報酬破壊が増加した。
  scope: 米国MTurk参加者N=1,332、平均年齢31.0歳、女性47.2%。
  conditions: オンライン実験、3条件に無作為割付。退屈条件は石の5分動画、第一対照条件はマジシャンの5分動画、第二対照条件は動画視聴前に選択を行う条件。参加者は別の参加者への報酬を10セント刻みで最大50セント減らせ、増額という向社会的選択肢はなかった。
  numeric_value: N=1,332；退屈条件n=421；第一対照条件n=469；第二対照条件n=442；動画条件各5分 (numeric_scope: Study 8の全参加者と3条件別人数。)
  date_or_period: 論文公刊：2021年
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 実験での報酬減額行動に限定した因果的主張。Study 7と異なり、向社会的な報酬増額の代替選択肢はなかった。著者らは、実験的誘発は短時間の退屈を扱うため、長時間・継続的な退屈の効果は推定できないと述べている。

### s33  (confidence max 0.7)
- issue_id: `boredom_aggression__run_bape_01__a2__d9552126__rf20261017T070800Z-4fd8__s33`
- sentence: We cannot say the choices alone caused the different results.
- before: But it is too soon to say, “Add a button to make rewards bigger and bring world peace!” / The two were separate experiments.
- after: We do not know if giving people a choice to make rewards bigger can stop meanness. / The experiment looked only at brief boredom.
- detected_by: gemini35fl-A3(0.3), gemini35fl-A4(0.7)
- reason [その他]: Study 7とStudy 8の設計の違いについて、選択肢の有無が結果の違いの直接の原因とは言えないという主張は台帳のFactに記載されていないのではないでしょうか？
- reason [主体対象入替]: Study 7とStudy 8は異なる実験ですが、「選択肢の違いが結果の違いを引き起こしたとは言えない」という記述は、台帳にある各実験の設計の違い（報酬増額選択肢の有無）や著者らの解釈と食い違っていませんか？
- fact F05: Study 7では、参加者が動画を見ている間、別の参加者の報酬を減らす、増やす、または何もしない選択をできるようにした。著者らの分析では、退屈条件による報酬破壊の増加は、特性サディズムが高い参加者で認められ、低い参加者では認められなかった。
  scope: 米国MTurk参加者N=634、平均年齢31.3歳、女性50.5%。
  conditions: オンライン実験。退屈条件では、何も起きない石の5分動画を視聴しながら、別の参加者の報酬を10セント刻みで最大50セント減らすか増やすか選べた。対照条件では、マジシャンの5分動画を視聴。無作為割付。
  numeric_value: N=634；退屈条件n=299；対照条件n=335；動画各5分；報酬変更は10セント刻み、最大50セント (numeric_scope: Study 7の全参加者、条件別人数、動画時間、選択肢の金額範囲。)
  date_or_period: 論文公刊：2021年
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 結果は、特定のオンライン金銭選択課題における効果であり、日常生活全般の攻撃行動への直接的な一般化は避けること。著者らの報告では、低特性サディズム群では退屈条件と対照条件の差は有意でなかった。
- fact F06: Study 8では、別の参加者の報酬を減らす選択肢のみを設けた実験で、著者らは退屈条件の参加者が対照条件より報酬を減らす可能性が高かったと報告した。著者らの分析では、この条件では特性サディズムの高低にかかわらず退屈条件で報酬破壊が増加した。
  scope: 米国MTurk参加者N=1,332、平均年齢31.0歳、女性47.2%。
  conditions: オンライン実験、3条件に無作為割付。退屈条件は石の5分動画、第一対照条件はマジシャンの5分動画、第二対照条件は動画視聴前に選択を行う条件。参加者は別の参加者への報酬を10セント刻みで最大50セント減らせ、増額という向社会的選択肢はなかった。
  numeric_value: N=1,332；退屈条件n=421；第一対照条件n=469；第二対照条件n=442；動画条件各5分 (numeric_scope: Study 8の全参加者と3条件別人数。)
  date_or_period: 論文公刊：2021年
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 実験での報酬減額行動に限定した因果的主張。Study 7と異なり、向社会的な報酬増額の代替選択肢はなかった。著者らは、実験的誘発は短時間の退屈を扱うため、長時間・継続的な退屈の効果は推定できないと述べている。

### s36  (confidence max 0.84)
- issue_id: `boredom_aggression__run_bape_01__a2__d9552126__rf20261017T070800Z-4fd8__s36`
- sentence: It also looked only at actions that made another person’s reward smaller.
- before: We do not know if giving people a choice to make rewards bigger can stop meanness. / The experiment looked only at brief boredom.
- after: We cannot use its results directly to explain everyday meanness or boredom that lasts a long time. / Even so, we see boring moments a little differently now.
- detected_by: luna-A4(0.84)
- reason [その他]: 「only at actions that made another person’s reward smaller」は実験で減額行動だけを扱ったという意味ではありませんか。Study 7では報酬を増やす選択肢もあったことと食い違わないか、確認してもらえますか。
- fact F05: Study 7では、参加者が動画を見ている間、別の参加者の報酬を減らす、増やす、または何もしない選択をできるようにした。著者らの分析では、退屈条件による報酬破壊の増加は、特性サディズムが高い参加者で認められ、低い参加者では認められなかった。
  scope: 米国MTurk参加者N=634、平均年齢31.3歳、女性50.5%。
  conditions: オンライン実験。退屈条件では、何も起きない石の5分動画を視聴しながら、別の参加者の報酬を10セント刻みで最大50セント減らすか増やすか選べた。対照条件では、マジシャンの5分動画を視聴。無作為割付。
  numeric_value: N=634；退屈条件n=299；対照条件n=335；動画各5分；報酬変更は10セント刻み、最大50セント (numeric_scope: Study 7の全参加者、条件別人数、動画時間、選択肢の金額範囲。)
  date_or_period: 論文公刊：2021年
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 結果は、特定のオンライン金銭選択課題における効果であり、日常生活全般の攻撃行動への直接的な一般化は避けること。著者らの報告では、低特性サディズム群では退屈条件と対照条件の差は有意でなかった。
- fact F06: Study 8では、別の参加者の報酬を減らす選択肢のみを設けた実験で、著者らは退屈条件の参加者が対照条件より報酬を減らす可能性が高かったと報告した。著者らの分析では、この条件では特性サディズムの高低にかかわらず退屈条件で報酬破壊が増加した。
  scope: 米国MTurk参加者N=1,332、平均年齢31.0歳、女性47.2%。
  conditions: オンライン実験、3条件に無作為割付。退屈条件は石の5分動画、第一対照条件はマジシャンの5分動画、第二対照条件は動画視聴前に選択を行う条件。参加者は別の参加者への報酬を10セント刻みで最大50セント減らせ、増額という向社会的選択肢はなかった。
  numeric_value: N=1,332；退屈条件n=421；第一対照条件n=469；第二対照条件n=442；動画条件各5分 (numeric_scope: Study 8の全参加者と3条件別人数。)
  date_or_period: 論文公刊：2021年
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 実験での報酬減額行動に限定した因果的主張。Study 7と異なり、向社会的な報酬増額の代替選択肢はなかった。著者らは、実験的誘発は短時間の退屈を扱うため、長時間・継続的な退屈の効果は推定できないと述べている。
