# Post-EN Risk Flagger Review Queue: middle_east_yemen_saudi__run_mey_01 / b1b

- run_id: `rf20261018T011412Z-9426`  status: **OK**
- article_sha256: `1737fecb3b1075c0e40438ffe5fd8f019be7242172ca3f37f780c414fd56e3e7`  ledger_sha256: `4f7d28b0bb7c280a34715215bc6c3d8b3c6b9127899a342c97cb1e6924cb8cf6`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `MEY-E2E-01`
- sentences: 41  facts: 11  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.142496 model=gpt-6-luna
- luna A4: OK flags=2 cost_jpy=0.173296 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.235408 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.241168 model=gemini-3.5-flash-lite

## Issues

### s3  (confidence max 0.3)
- issue_id: `middle_east_yemen_saudi__run_mey_01__b1b__1737fecb__rf20261018T011412Z-9426__s3`
- sentence: As I followed the news, an unexpected phrase appeared on an airport departure board: “Peace in Yemen.”
- before: # Why Does “Peace” Appear in Airport News? / An airport was attacked.
- after: Wait, wasn’t this happening in Saudi Arabia? / I hadn’t misread it.
- detected_by: luna-A4(0.3)
- reason [その他]: 「空港の出発案内板に『Peace in Yemen』が表示された」という出来事は、台帳Factで確認できない内容ではありませんか。

### s5  (confidence max 0.2)
- issue_id: `middle_east_yemen_saudi__run_mey_01__b1b__1737fecb__rf20261018T011412Z-9426__s5`
- sentence: I hadn’t misread it.
- before: As I followed the news, an unexpected phrase appeared on an airport departure board: “Peace in Yemen.” / Wait, wasn’t this happening in Saudi Arabia?
- after: This news has a connection that goes beyond the name of just one country. / First, let’s check the reports of damage.
- detected_by: luna-A4(0.2)
- reason [その他]: 「I hadn’t misread it」という確認は、台帳Factで確認できない出発案内板の表示を事実として裏付けるものではありませんか。
