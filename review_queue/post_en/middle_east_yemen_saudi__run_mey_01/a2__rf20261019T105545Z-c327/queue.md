# Post-EN Risk Flagger Review Queue: middle_east_yemen_saudi__run_mey_01 / a2

- run_id: `rf20261019T105545Z-c327`  status: **OK**
- article_sha256: `2b1e9ef78e0561e85e642ec664041a22fb7341e754f2ee3ac95286bfa846856e`  ledger_sha256: `4f7d28b0bb7c280a34715215bc6c3d8b3c6b9127899a342c97cb1e6924cb8cf6`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `MEY-E2E-01`
- sentences: 45  facts: 11  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.164048 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.246688 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.236608 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.242368 model=gemini-3.5-flash-lite

## Issues

### s18  (confidence max 0.35)
- issue_id: `middle_east_yemen_saudi__run_mey_01__a2__2b1e9ef7__rf20261019T105545Z-c327__s18`
- sentence: They also make efforts to bring peace to Yemen even harder.
- before: The UN special envoy for Yemen condemned the continuing attacks on civilian sites in Saudi Arabia. / The envoy said these attacks put safety in the region at risk.
- after: Here, the camera of the news story pulls far back. / Until then, the news had focused on the harm at the airport.
- detected_by: luna-A3(0.35)
- reason [その他]: 台帳では和平努力を困難にするのは特使の評価ですが、「They also make」と断定している点は食い違うのではありませんか。
- fact F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃についてサウジ当局による死者12人・負傷者300人超との報告を示した。また、同週のリヤドおよびアブハ空港への攻撃でも民間人の死傷があったと述べ、攻撃は地域の安全保障を脅かし、イエメンの和平努力を一層困難にすると評価した。
  scope: サウジアラビアの民間インフラ、とくにリヤド・アブハの空港。和平への影響は特使による評価。
  conditions: 死傷者数は国連特使がサウジ当局の発表に基づくとして紹介したもの。和平努力への影響は特使自身の評価。
  numeric_value: リヤド空港攻撃：死亡12人、負傷300人超（サウジ当局発表として国連特使が引用）。 (numeric_scope: 2026年10月10日のリヤド空港攻撃)
  date_or_period: 2026-10-11。対象となる直近の攻撃は同週および2026-10-10。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「和平努力を困難にする」は国連特使の評価として記載し、独立に実証された因果関係として一般化しない。

### s28  (confidence max 0.58)
- issue_id: `middle_east_yemen_saudi__run_mey_01__a2__2b1e9ef7__rf20261019T105545Z-c327__s28`
- sentence: From this information alone, we cannot know for sure how much harder peace has become.
- before: The reported numbers of people killed and hurt are one kind of information. / The envoy’s view that the attacks “make peace efforts harder” is another.
- after: The numbers tell us about the harm. / The envoy’s words warn us about what may happen next.
- detected_by: luna-A3(0.32), luna-A4(0.58)
- reason [その他]: 台帳は和平努力への影響を特使の評価としている一方、「peace has become」では実際に和平が困難になったことを前提にしているのではありませんか。
- reason [その他]: 「peace has become harder」が和平努力への特使の評価を実際に起きた変化として前提にしており、台帳の評価としての記述より強く読めるのではありませんか。
- fact F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃についてサウジ当局による死者12人・負傷者300人超との報告を示した。また、同週のリヤドおよびアブハ空港への攻撃でも民間人の死傷があったと述べ、攻撃は地域の安全保障を脅かし、イエメンの和平努力を一層困難にすると評価した。
  scope: サウジアラビアの民間インフラ、とくにリヤド・アブハの空港。和平への影響は特使による評価。
  conditions: 死傷者数は国連特使がサウジ当局の発表に基づくとして紹介したもの。和平努力への影響は特使自身の評価。
  numeric_value: リヤド空港攻撃：死亡12人、負傷300人超（サウジ当局発表として国連特使が引用）。 (numeric_scope: 2026年10月10日のリヤド空港攻撃)
  date_or_period: 2026-10-11。対象となる直近の攻撃は同週および2026-10-10。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「和平努力を困難にする」は国連特使の評価として記載し、独立に実証された因果関係として一般化しない。
