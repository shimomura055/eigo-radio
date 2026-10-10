# Post-EN Risk Flagger Review Queue: X09 / b1b

- run_id: `rf20261010T083520Z-1e87`  status: **OK**
- article_sha256: `adf6f2fb422c27fe3e8a938a6470e06d5c0bc97ac770a0399205a26f174c0363`  ledger_sha256: `9bd6834e68e7e4378ba0ebccdd84c0128df2a5cd0aca7c1e84df612ae77ae1a6`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `STUB_FIXTURE_NOT_REAL`  run_label: `C1_STUB_E2E`
- sentences: 33  facts: 12  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.136 model=gpt-6-luna
- luna A4: OK flags=0 cost_jpy=0.136 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.52 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=1 cost_jpy=0.52 model=gemini-3.5-flash-lite

## Issues

### s3  (confidence max 0.3)
- issue_id: `X09__b1b__adf6f2fb__rf20261010T083520Z-1e87__s3`
- sentence: The next day, the plan was withdrawn.
- before: # The “20% Plan” Exits at Once, but High Oil Prices Still Won’t Go Away / A major policy plan appeared, and oil prices shot up.
- after: You might expect the market to say, “Sorry for the fuss,” and return to where it was—but that did not happen. / The lead actor left the stage, but the tension stayed behind.
- detected_by: gemini35fl-A3(0.3), gemini35fl-A4(0.3)
- reason [数量時系列]: STUB: 台帳と食い違うのではありませんか
- fact HF-001: 国際海事機関（IMO）理事会は、第137回会合で、ホルムズ海峡の通航は国際法およびIMO条約に従い、通航料・手数料を課されない状態を維持すべきだと再確認した。
  scope: 国際航行に使用されるホルムズ海峡を通航する全船舶
  conditions: 沿岸国間の取り決めは、全船舶の無差別かつ妨げられない通過通航権を保証する必要がある。
  numeric_value: 第137回理事会 (numeric_scope: IMO理事会の会合番号)
  date_or_period: 2026-07-06～2026-07-10（第137回理事会開催期間）、2026-07-13公表
  notes_for_writer: この決議と7月14日の発言撤回との因果関係は一次資料で確認できない。撤回の原因として記述しない。
