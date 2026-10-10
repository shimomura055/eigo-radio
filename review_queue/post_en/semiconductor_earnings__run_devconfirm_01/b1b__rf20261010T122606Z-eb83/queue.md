# Post-EN Risk Flagger Review Queue: semiconductor_earnings__run_devconfirm_01 / b1b

- run_id: `rf20261010T122606Z-eb83`  status: **OK**
- article_sha256: `c87bf5c9a10a7dc96f00ef882e2c255e9e25bcf5f974eb0280093dbdb719f6fa`  ledger_sha256: `36b2c87dbc570a776c65cb335a516e33a497451f1bb9446fbc7a5bcd2aec3c97`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `W1_DOWNSTREAM_DEV_CONFIRM`
- sentences: 39  facts: 6  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.07552 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.13504 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.167536 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.173296 model=gemini-3.5-flash-lite

## Issues

### s32  (confidence max 0.3)
- issue_id: `semiconductor_earnings__run_devconfirm_01__b1b__c87bf5c9__rf20261010T122606Z-eb83__s32`
- sentence: If we take the talk of strong demand for AI and turn it straight into “all the figures are AI figures,” we end up starting a different movie.
- before: One more thing to check before you leave. / The outlook for about $34.8 billion is also for the whole company’s revenue, not just a forecast for AI semiconductors.
- after: The highlights this time are how three things connect: the results for AI semiconductors, the CEO’s view of demand, and the outlook for the whole company’s revenue next quarter. / An earnings report doesn’t have to end with judging the past.
- detected_by: luna-A4(0.3)
- reason [その他]: 「AIへの強い需要」と「カスタムAIアクセラレーターおよびネットワーキングへの強い需要」は範囲が異なるのではありませんか
- fact F6: BroadcomのCEOは、カスタムAIアクセラレーターとネットワーキングへの需要が引き続き非常に強いと述べた。
  scope: 同社のカスタムAIアクセラレーターおよびネットワーキングに対する需要についてのCEOの説明
  conditions: 経営陣による定性的な評価。
  date_or_period: 2026年9月2日発表の2026年度第3四半期決算リリース
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 会社CEOの評価として帰属を明記し、独立に確認された市場全体の需要事実として一般化しない。
