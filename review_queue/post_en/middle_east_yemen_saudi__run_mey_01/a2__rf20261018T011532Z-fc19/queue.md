# Post-EN Risk Flagger Review Queue: middle_east_yemen_saudi__run_mey_01 / a2

- run_id: `rf20261018T011532Z-fc19`  status: **OK**
- article_sha256: `1f6e42d75c64d295e56e9f6085953b5b613108302aba9f1c4e949e2361b01461`  ledger_sha256: `4f7d28b0bb7c280a34715215bc6c3d8b3c6b9127899a342c97cb1e6924cb8cf6`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `MEY-E2E-01`
- sentences: 47  facts: 11  candidate issues: 3

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.124096 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.213536 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.24136 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.515614 model=gemini-3.5-flash-lite

## Issues

### s3  (confidence max 0.3)
- issue_id: `middle_east_yemen_saudi__run_mey_01__a2__1f6e42d7__rf20261018T011532Z-fc19__s3`
- sentence: As I followed the news, I saw a surprising phrase on an airport departure board: “Peace in Yemen.”
- before: # Why Does “Peace” Appear in Airport News? / An airport was attacked.
- after: Wait, wasn’t this happening in Saudi Arabia? / I had read it correctly.
- detected_by: luna-A4(0.3)
- reason [その他]: 空港の出発案内板に「Peace in Yemen」と表示されていたという記述は、台帳で確認できない事実ではありませんか。

### s31  (confidence max 0.3)
- issue_id: `middle_east_yemen_saudi__run_mey_01__a2__1f6e42d7__rf20261018T011532Z-fc19__s31`
- sentence: The official’s view is that the attack makes work to bring peace harder.
- before: An attack on that place is linked to yet another issue. / But we should not let our imagination run at full speed here.
- after: If we say, “This will surely push peace farther away,” we are saying more than the official did. / The more clearly we see the link, the more careful we must be.
- detected_by: luna-A4(0.3)
- reason [主体対象入替]: 「the attack」が指す特定の攻撃と、台帳が和平努力を困難にするとした「攻撃」全般では、対象の範囲が異なるのではありませんか。
- fact F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃についてサウジ当局による死者12人・負傷者300人超との報告を示した。また、同週のリヤドおよびアブハ空港への攻撃でも民間人の死傷があったと述べ、攻撃は地域の安全保障を脅かし、イエメンの和平努力を一層困難にすると評価した。
  scope: サウジアラビアの民間インフラ、とくにリヤド・アブハの空港。和平への影響は特使による評価。
  conditions: 死傷者数は国連特使がサウジ当局の発表に基づくとして紹介したもの。和平努力への影響は特使自身の評価。
  numeric_value: リヤド空港攻撃：死亡12人、負傷300人超（サウジ当局発表として国連特使が引用）。 (numeric_scope: 2026年10月10日のリヤド空港攻撃)
  date_or_period: 2026-10-11。対象となる直近の攻撃は同週および2026-10-10。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「和平努力を困難にする」は国連特使の評価として記載し、独立に実証された因果関係として一般化しない。

### s46  (confidence max 0.7)
- issue_id: `middle_east_yemen_saudi__run_mey_01__a2__1f6e42d7__rf20261018T011532Z-fc19__s46`
- sentence: The UN official for Yemen said the Riyadh airport attack could make peace efforts harder.
- before: Beyond it, another map opens up. / ## In one line
- after: Saudi officials gave the death and injury numbers, while the official described the effect on peace.
- detected_by: luna-A4(0.3), gemini35fl-A4(0.7)
- reason [主体対象入替]: 「the Riyadh airport attack」と特定する表現は、台帳が和平努力への影響を述べた「攻撃」全般より範囲を狭めているのではありませんか。
- reason [その他]: 国連特使の発言について、台帳(F11)では「和平努力を一層困難にする」と評価しているのに対し、s46では「could make peace efforts harder」と表現していますが、ニュアンスや時制が台帳の趣旨からずれていませんか？
- fact F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃についてサウジ当局による死者12人・負傷者300人超との報告を示した。また、同週のリヤドおよびアブハ空港への攻撃でも民間人の死傷があったと述べ、攻撃は地域の安全保障を脅かし、イエメンの和平努力を一層困難にすると評価した。
  scope: サウジアラビアの民間インフラ、とくにリヤド・アブハの空港。和平への影響は特使による評価。
  conditions: 死傷者数は国連特使がサウジ当局の発表に基づくとして紹介したもの。和平努力への影響は特使自身の評価。
  numeric_value: リヤド空港攻撃：死亡12人、負傷300人超（サウジ当局発表として国連特使が引用）。 (numeric_scope: 2026年10月10日のリヤド空港攻撃)
  date_or_period: 2026-10-11。対象となる直近の攻撃は同週および2026-10-10。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「和平努力を困難にする」は国連特使の評価として記載し、独立に実証された因果関係として一般化しない。
