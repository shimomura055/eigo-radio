# Stage R 費用集計(委任_06+_07)
単価=`er019 compute_stage_cost_breakdown`(gpt-6-luna、登録単価x実測トークン+web_search call課金)。素データ=各`<slug>/raw_usage_log.jsonl`、集計=`cost_by_theme.json`。
| slug | research | ledger | storyline_b3 | 計(円) | 担当 |
|---|---|---|---|---|---|
| byd_recall | 7.425 | 5.545 | 0.563 | 13.533 | _06 |
| openai_copyright | 22.821 | 9.010 | 0.456 | 32.288 | research/ledger _06、B3 _07 |
| central_bank_mortgage | 14.947 | 7.385 | 0.566 | 22.898 | _06 |
| inbound_tourism | 28.561 | 28.257 | 0.602 | 57.420 | research/ledger _06、B3 _07 |
| streaming_price(v2 topic) | 21.677 | 12.783 | 0.510 | 34.970 | _07 |
| semiconductor_earnings(v2 topic) | 9.305 | 5.579 | 0.468 | 15.352 | _07 |
| meta | - | - | 0.419 | 0.419 | _06 |
| hormuz | - | - | 0.427 | 0.427 | _06 |
| space_weapons | - | - | 0.563 | 0.563 | _06 |
| small_bag | - | - | 0.377 | 0.377 | _06 |

委任_06 ¥126.87 + 委任_07 ¥51.38(B3 openai 0.456 + inbound 0.602 + streaming 34.97 + semiconductor 15.352)= **累計 ¥178.25**。委任_07上限¥80内(残¥28.6)。見積¥100に対し+¥78.2。
原因: (1) inbound_tourismがresearch+ledgerで¥56.8(検索16+検証16 call、トピックが月次・累計・国別・消費・収容力と広い)。(2) openai ¥31.8、central ¥22.9もweb_search call数(research 8〜13/ledger 4〜5)が見積より多い。(3) streaming(topic絞り後でも¥34.5、検索research 12+ledger 7 call。semiconductorは5+3 call)。見積は1テーマ約¥17の想定で、実測は¥14〜57(平均約¥29)。topic絞り(1社・1イベント)後はsemiconductor ¥14.9に対しstreaming ¥34.5と差が残った。
