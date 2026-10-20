# Post-EN Risk Flagger Review Queue: middle_east_yemen_saudi__run_mey_02 / a2

- run_id: `rf20261020T124010Z-0975`  status: **OK**
- article_sha256: `d948d2c6570e6e5db57bb87bb00b799fba77ea2d6adf6aba76e822558d22e421`  ledger_sha256: `ae7611d033858e0738b27b2357313cc088aea76ce4df2a0d837639a476b9e665`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `MEY-E2E-02-T1`
- sentences: 44  facts: 8  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.142368 model=gpt-6-luna
- luna A4: OK flags=0 cost_jpy=0.132848 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.195344 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.200704 model=gemini-3.5-flash-lite

## Issues

### s11  (confidence max 0.3)
- issue_id: `middle_east_yemen_saudi__run_mey_02__a2__d948d2c6__rf20261020T124010Z-0975__s11`
- sentence: The Houthis had fired it toward Riyadh.
- before: First, let’s look at the announcement. / A spokesperson for the Saudi-led coalition forces in Yemen said they had stopped and destroyed one ballistic missile.
- after: In this case, the UK Ministry of Defence announced an air-defense mission for Royal Air Force Typhoon fighter jets. / They will protect Saudi cities and important sites from air attacks.
- detected_by: luna-A3(0.3)
- reason [その他]: 「The Houthis had fired it」と事実として述べる表現は、台帳の「連合軍報道官がそう発表した」という情報源の限定を外しているのではありませんか。
- fact YSA-20261020-01: サウジ主導のイエメン連合軍報道官は、フーシ派がリヤドに向けて発射した弾道ミサイル1発を迎撃・破壊したと発表した。
  scope: サウジアラビアのリヤドに向けて発射されたミサイル1発
  numeric_value: 1発 (numeric_scope: 連合軍報道官が迎撃・破壊したと発表した弾道ミサイル)
  date_or_period: 2026年10月20日
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: サウジ国営通信SPA掲載の連合軍報道官発表。独立した第三者による検証とは区別する。
