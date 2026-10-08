# Stage R 費用集計(委任_06)

単価=`er019 compute_stage_cost_breakdown`(登録単価gpt-6-luna×実測トークン+web_search call課金、USD_JPY込み)。素データ=各`<slug>/raw_usage_log.jsonl`、集計=`cost_by_theme.json`(`cost_tool.py`)。

| slug | research | ledger | storyline_b3 | 計(円) | web_search call(research/ledger) |
|---|---|---|---|---|---|
| byd_recall | 7.425 | 5.545 | 0.563 | 13.533 | 4/3 |
| openai_copyright | 22.821 | 9.01 | - | 31.832 | 13/5 |
| central_bank_mortgage | 14.947 | 7.385 | 0.566 | 22.898 | 8/4 |
| inbound_tourism | 28.561 | 28.257 | - | 56.819 | 16/16 |
| meta | - | - | 0.419 | 0.419 | -/- |
| hormuz | - | - | 0.427 | 0.427 | -/- |
| space_weapons | - | - | 0.563 | 0.563 | -/- |
| small_bag | - | - | 0.377 | 0.377 | -/- |

**合計 ¥126.868**(上限¥130、残り¥3.13)。

注: streaming_price / semiconductor_earnings は未実行(費用0)。openai_copyright・inbound_tourismは1テーマ¥30超(31.83 / 56.82)のためB3段の前でBUDGET_GUARD停止(B3未生成)。ガードは`--budget-jpy 30`のtoken+web_search込みresearch_ledger後判定。
