# Post-EN Risk Flagger Review Queue: paycheck_personality__run_pp_02 / b1b

- run_id: `rf20261022T005353Z-f00e`  status: **OK**
- article_sha256: `5052ff7c21a25d5cef081feb170765c7aae884f663434fa9efe969574edcab75`  ledger_sha256: `a31992b53082d2f143f9b32949dbb926d353c1034a04e2fad666cceca21b0980`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `B3RD8 writer after rejudge`
- sentences: 35  facts: 19  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.178416 model=gpt-6-luna
- luna A4: OK flags=0 cost_jpy=0.182976 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.318768 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.278128 model=gemini-3.5-flash-lite

## Issues

### s15  (confidence max 0.3)
- issue_id: `paycheck_personality__run_pp_02__b1b__5052ff7c__rf20261022T005353Z-f00e__s15`
- sentence: The personality trait they focused on was conscientiousness: the tendency to work seriously and steadily.
- before: They moved from ranking people by yearly income to tracking one person over time. / It’s a different contest altogether.
- after: Their analysis found that, within the same person, higher income was linked to higher conscientiousness later on. / Wait—we thought this was about personality affecting income, but income got a part too!
- detected_by: gemini35fl-A3(0.3)
- reason [その他]: s15で「The personality trait they focused on was conscientiousness」と記述されていますが、台帳F08やF13にある通り一次研究はBig Fiveの他の特性（情緒安定性、外向性、協調性、開放性）も対象としており、勤勉性のみに焦点を当てていたわけではありません。この表現は適切ですか？
- fact F08: 最大標準化交差遅延効果では、収入から勤勉性への関連は+0.0630、勤勉性から後の収入への関連は+0.0589で、いずれも約1.30年の間隔で最大だった。
  scope: 11研究の統合個人内モデル。特性別解析のNは異なる。
  conditions: 報告値は複数の測定間隔にわたる最大の標準化離散時間交差遅延効果。
  numeric_value: 収入→勤勉性 +0.0630; 勤勉性→収入 +0.0589 (numeric_scope: それぞれの方向の最大標準化交差遅延効果。単位は標準化されたモデル係数。)
  date_or_period: 最も大きい推定効果は約1.30年の時間間隔
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 観察された縦断的関連であり、因果効果として表現しない。最大値は該当する時間間隔での推定値。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。
