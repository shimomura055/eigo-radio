# Post-EN Risk Flagger Review Queue: semiconductor_earnings__run_devconfirm_01 / a2

- run_id: `rf20261010T122643Z-f5e7`  status: **OK**
- article_sha256: `386153caa5f32429b747f6acfc270cf23400657ab55aa0e0a1cbaf5dd4f07630`  ledger_sha256: `36b2c87dbc570a776c65cb335a516e33a497451f1bb9446fbc7a5bcd2aec3c97`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `W1_DOWNSTREAM_DEV_CONFIRM`
- sentences: 47  facts: 6  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.096032 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.108752 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.174832 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.180592 model=gemini-3.5-flash-lite

## Issues

### s37  (confidence max 0.88)
- issue_id: `semiconductor_earnings__run_devconfirm_01__a2__386153ca__rf20261010T122643Z-f5e7__s37`
- sentence: The company says demand for AI is strong.
- before: The forecast of about $34.8 billion is for the whole company’s revenue too. / It is not only a forecast for AI semiconductors.
- after: But that does not mean all the numbers are AI numbers. / If we treat them that way, we start a different movie.
- detected_by: luna-A3(0.35), luna-A4(0.88)
- reason [その他]: 「demand for AI is strong」は、台帳の「カスタムAIアクセラレーターとネットワーキングへの需要が非常に強い」より対象範囲を広げていませんか。
- reason [その他]: “demand for AI”は、Factの“custom AI accelerators and networkingへの需要”より範囲を広げた表現ではありませんか。
- fact F6: BroadcomのCEOは、カスタムAIアクセラレーターとネットワーキングへの需要が引き続き非常に強いと述べた。
  scope: 同社のカスタムAIアクセラレーターおよびネットワーキングに対する需要についてのCEOの説明
  conditions: 経営陣による定性的な評価。
  date_or_period: 2026年9月2日発表の2026年度第3四半期決算リリース
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 会社CEOの評価として帰属を明記し、独立に確認された市場全体の需要事実として一般化しない。
