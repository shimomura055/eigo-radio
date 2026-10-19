# Post-EN Risk Flagger Review Queue: middle_east_yemen_saudi__run_mey_01 / b1b

- run_id: `rf20261019T105456Z-07e4`  status: **OK**
- article_sha256: `500da2e404d78ebc1816c12ae3a847605b9ba6299357bdc9f34fa44a6ab6689f`  ledger_sha256: `4f7d28b0bb7c280a34715215bc6c3d8b3c6b9127899a342c97cb1e6924cb8cf6`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `MEY-E2E-01`
- sentences: 39  facts: 11  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.151168 model=gpt-6-luna
- luna A4: OK flags=0 cost_jpy=0.126448 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.23104 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.2368 model=gemini-3.5-flash-lite

## Issues

### s39  (confidence max 0.32)
- issue_id: `middle_east_yemen_saudi__run_mey_01__b1b__500da2e4__rf20261019T105456Z-07e4__s39`
- sentence: A UN envoy warned that attacks on civilian sites threaten regional safety and make peace efforts in Yemen harder, though the report cannot show by how much.
- before: ## In one line / An attack on Riyadh’s airport killed 12 people and injured 309.
- detected_by: luna-A3(0.32)
- reason [主体対象入替]: 「attacks on civilian sites」は、台帳が述べる「サウジアラビアの民間インフラへの攻撃」より対象範囲を広げているのではありませんか。
- fact F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃についてサウジ当局による死者12人・負傷者300人超との報告を示した。また、同週のリヤドおよびアブハ空港への攻撃でも民間人の死傷があったと述べ、攻撃は地域の安全保障を脅かし、イエメンの和平努力を一層困難にすると評価した。
  scope: サウジアラビアの民間インフラ、とくにリヤド・アブハの空港。和平への影響は特使による評価。
  conditions: 死傷者数は国連特使がサウジ当局の発表に基づくとして紹介したもの。和平努力への影響は特使自身の評価。
  numeric_value: リヤド空港攻撃：死亡12人、負傷300人超（サウジ当局発表として国連特使が引用）。 (numeric_scope: 2026年10月10日のリヤド空港攻撃)
  date_or_period: 2026-10-11。対象となる直近の攻撃は同週および2026-10-10。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「和平努力を困難にする」は国連特使の評価として記載し、独立に実証された因果関係として一般化しない。
