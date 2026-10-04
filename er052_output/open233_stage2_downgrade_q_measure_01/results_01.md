# results_01.md (委任_68 q測定: 修正版S1の2回目だけBLOCKINGになる率)

cost_jpy_total=4.3265 calls=30 errors=0 n=30

## q(2回目の最終materiality=BLOCKING率)

| 区分 | n | API失敗等 | 有効n | BLOCKING | q | Wilson95 |
|---|---|---|---|---|---|---|
| 全体 | 30 | 0 | 30 | 0 | 0.0 | [0, 0.114] |
| cycle1 | 24 | 0 | 24 | 0 | 0.0 | [0, 0.138] |
| cycle2plus | 6 | 0 | 6 | 0 | 0.0 | [0, 0.39] |
| route=body | 23 | 0 | 23 | 0 | 0.0 | [0, 0.143] |
| route=hook | 7 | 0 | 7 | 0 | 0.0 | [0, 0.354] |
| 1回目=ACCEPTABLE | 18 | 0 | 18 | 0 | 0.0 | [0, 0.176] |
| 1回目=QUALITY | 12 | 0 | 12 | 0 | 0.0 | [0, 0.243] |
| cycle1/body | 18 | 0 | 18 | 0 | 0.0 | [0, 0.176] |
| cycle1/hook | 6 | 0 | 6 | 0 | 0.0 | [0, 0.39] |
| cycle2plus/body | 5 | 0 | 5 | 0 | 0.0 | [0, 0.434] |
| cycle2plus/hook | 1 | 0 | 1 | 0 | 0.0 | [0, 0.793] |

STOP閾値(cycle1>30% / cycle2+>20%): {'cycle1_limit': 0.3, 'cycle2plus_limit': 0.2, 'cycle1_exceeds': False, 'cycle2plus_exceeds': False}
route不一致: ['t12'] / 2回目floor_reason異常: []
2回目のllm_materiality=BLOCKING 0件 / 最終BLOCKING 0件

## 2回目BLOCKINGの件(仮ラベル=実行層[Sonnet]の読み、正式確定ではない)

仮ラベル集計: {}


## S1追加費用の試算

- rep24_targets: {'cycle1': 62, 'cycle2plus': 6}
- rep24_s2_second_calls_batched: 30
- unit_cost_per_call_measured_single_claim: 0.1442
- extra_rewrites_total_rep24: 0
- extra_rewrites_per_instance_run(38): 0.0
- stage2_second_cost_per_instance_run(batched): 0.114
- stage2_second_cost_per_article(29): 0.149
- rewrite_cost_per_instance_run_range: [0.0, 0.0]
- total_extra_per_instance_run_range: [0.114, 0.114]
- note: 推定。Rewriteの再帰(Recheckで新MAJOR等)・STAGE4への移行は含まない。+2円枠はfloor_verify/L6/Recheck等の合計に対する上限(Opus#10)。
