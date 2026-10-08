# Phase 0 probe サマリ(PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_02)

互換のみ確認、品質は未検証。モデル=gpt-6-luna(override理由付き、メモリ上差し替え)。
累計費用: ¥10.70 / 予算 ¥30.0(6-luna 0.10/0.01/0.50 $/1M、USD/JPY=160、web_search概算$0.01/call)

| 工程 | 結果 | API call数 | 実使用model_id | schema適合 | effort(要求→応答) | web_search_call | 出力長/切れ | 秒 | 費用¥ |
|---|---|---|---|---|---|---|---|---|---|
| SHARED_POINT_BLUEPRINT | OK | 1 | gpt-6-luna | True | medium->medium | 0 | 1042字/completed | 20.0 | 0.23 |
| PROPER_NOUN_EXTRACTION | OK | 1 | gpt-6-luna | True | None->medium | 0 | 180字/completed | 4.6 | 0.04 |
| STANDARD_A2_ADAPTATION | OK | 1 | gpt-6-luna | None | high->high | 0 | 2205字/completed | 29.5 | 0.3 |
| EVIDENCE_PACK+VFL | OK | 2 | gpt-6-luna | True | medium->medium | 0 | 3402字/completed,4329字/completed | 31.9 | 0.41 |
| RESEARCH_COVERAGE_GATE | OK | 1 | gpt-6-luna | True | medium->medium | 0 | 533字/completed | 10.9 | 0.16 |
| B1_SUPPORT(KP selection) | OK | 1 | gpt-6-luna | True | high->high | 0 | 4035字/completed | 46.2 | 0.44 |
| KEY_PHRASE_ADVANCED_EXPLANATION | OK | 1 | gpt-6-luna | True | medium->medium | 0 | 539字/completed | 3.4 | 0.03 |
| QUERY_PLANNING/TOPIC_SELECTION(topic_adapter web_search) | OK | 1 | gpt-6-luna | None | None->medium | 5 | 10393字/completed | 54.7 | 9.07 |

## NG/SKIPPED の症状
- なし

## Production file sha256(probe前後)
| file | 不変 |
|---|---|
| er006_model_routing_contract_01.py | OK |
| er008_shared_point_blueprint_01.py | OK |
| er006_proper_noun_extraction_01.py | OK |
| er003_v1_n3_01_standard_a2_generate.py | OK |
| er006_pool_pilot_01_research.py | OK |
| er006_research_coverage_gate_01.py | OK |
| er003_v1_n3_01_scaffold_generate.py | OK |
| er019_family_x_kp_explanation_01.py | OK |
| er002_topic_adapter.py | OK |
| gather_topic.py | OK |
| er003_v1_en_direct_vfl_01_generate.py | OK |
| er005_output/cost_baseline_01/pricing_snapshot.json | OK |

## require_model差し替え記録(全件override理由付き)
- 件数: 5
- 全件理由付き: True
