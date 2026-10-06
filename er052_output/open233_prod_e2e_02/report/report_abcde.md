# 報告A〜E集計(委任_02 / 比較基準値)

**旧仕様9 run(frozen)・比較基準値・新仕様のEvidenceではない**。ラベルは `--labels` の外部jsonのみ(推測ラベルの新規付与なし)。UNLABELEDは未ラベル件数。
対象run: 9 (bgroup_B3, hormuz_run03_advanced, hormuz_run03_standard, meta_run03_advanced, meta_run03_standard, neg1_meta_b3prod_a2, neg2_meta_refresh_a2, neg3_hormuz_prodrunner_b1b, neg7_meta_prodrunner_b1b)

## A. Checker(初回候補、重複はclaim単位=norm)
| 項目 | 値 |
|---|---|
| AI候補(claim) | 46 |
| 機械候補(claim) | 20 |
| AIのみ | 46 |
| 機械のみ | 20 |
| AIと機械の重複 | 0 |
| 重複除外前の延べ | 66 |
| 重複除外後のChecker総候補(=後段へ渡した件数) | 66 |
| AI候補 true_problem | {"Y": 0, "N": 0, "UNDECIDABLE": 0, "UNLABELED": 46} |
| 機械候補 true_problem | {"Y": 0, "N": 0, "UNDECIDABLE": 0, "UNLABELED": 20} |
| 機械候補の内訳 | {"negation_polarity_mismatch": 18, "deterministic": 20, "quote_not_in_ledger": 1} |
| 再分類前後フィールド | MISSING(旧仕様に無し) |

run別:
| run | AI | 機械 | AIのみ | 機械のみ | 重複 | 延べ | 除外後(後段へ) |
|---|---|---|---|---|---|---|---|
| bgroup_B3 | 1 | 1 | 1 | 1 | 0 | 2 | 2 |
| hormuz_run03_advanced | 7 | 1 | 7 | 1 | 0 | 8 | 8 |
| hormuz_run03_standard | 5 | 4 | 5 | 4 | 0 | 9 | 9 |
| meta_run03_advanced | 4 | 1 | 4 | 1 | 0 | 5 | 5 |
| meta_run03_standard | 8 | 3 | 8 | 3 | 0 | 11 | 11 |
| neg1_meta_b3prod_a2 | 10 | 4 | 10 | 4 | 0 | 14 | 14 |
| neg2_meta_refresh_a2 | 5 | 2 | 5 | 2 | 0 | 7 | 7 |
| neg3_hormuz_prodrunner_b1b | 3 | 2 | 3 | 2 | 0 | 5 | 5 |
| neg7_meta_prodrunner_b1b | 3 | 2 | 3 | 2 | 0 | 5 | 5 |

## B. 後段判定(cycle1)
| 項目 | 値 |
|---|---|
| n_claim_judgments | 89 |
| downstream_ai | {"重大(BLOCKING)": 4, "軽微(QUALITY)": 11, "問題なし(ACCEPTABLE)": 74} |
| downstream_ai_posteval | {"真に重大だった(AI重大&Y)": 0, "不要に重大判定(AI重大&N)": 0, "AI重大の判断不能": 0, "AI重大のUNLABELED": 4, "真に重大だったのに軽微/問題なし(Y&AI非重大)": 0} |
| downstream_machine_floor | {"発火件数": 3, "種別内訳": {"changed_number": 3}, "AI判定との重複(AIもBLOCKING)": 2, "機械のみで重大化": 1, "真に重大だった(Y)": 0, "不要に重大化(N)": 0, "判断不能": 0, "UNLABELED": 3} |

## B. 後段判定(全cycle合算)
| 項目 | 値 |
|---|---|
| n_claim_judgments | 123 |
| downstream_ai | {"重大(BLOCKING)": 4, "軽微(QUALITY)": 14, "問題なし(ACCEPTABLE)": 105} |
| downstream_ai_posteval | {"真に重大だった(AI重大&Y)": 0, "不要に重大判定(AI重大&N)": 0, "AI重大の判断不能": 0, "AI重大のUNLABELED": 4, "真に重大だったのに軽微/問題なし(Y&AI非重大)": 0} |
| downstream_machine_floor | {"発火件数": 4, "種別内訳": {"changed_number": 3, "s1_second_opinion_blocking": 1}, "AI判定との重複(AIもBLOCKING)": 2, "機械のみで重大化": 2, "真に重大だった(Y)": 0, "不要に重大化(N)": 0, "判断不能": 0, "UNLABELED": 4} |

## C. Rewrite
| 項目 | 値 |
|---|---|
| Rewrite発生件数(rewrite_records) | 6 |
| guard_ok件数 | 6 |
| Rewrite発生run数 | 4 |
| run総数 | 9 |
| 必要だった | 0 |
| 不要だった | 0 |
| 判断不能 | 0 |
| ラベルUNLABELED | 6 |
| Rewrite後に再修正が必要(同fact次cycleもBLOCKING) | 0 |
| 再修正判定不能(次cycleなし/ID無) | 0 |
| per_run | {"bgroup_B3": 1, "meta_run03_standard": 2, "neg2_meta_refresh_a2": 1, "neg3_hormuz_prodrunner_b1b": 2} |

## D. Human Review(目標0件)
到達run: []、出口BLOCKING claim 0件


## E. Safety・Cost
Safety: {"source": "MISSING(旧e2e_aggregate.json無し)"}

| run | total_cost_jpy | call_log合計 | Checker | 後段判定 | Rewrite関連 | other |
|---|---|---|---|---|---|---|
| bgroup_B3 | 3.9618 | 3.9618 | 1.6981 | 1.1705 | 1.0932 | 0 |
| hormuz_run03_advanced | 1.971 | 1.971 | 1.4185 | 0.5525 | 0 | 0 |
| hormuz_run03_standard | 2.6368 | 2.6368 | 2.0096 | 0.6272 | 0 | 0 |
| meta_run03_advanced | 2.4103 | 2.4103 | 1.8367 | 0.5736 | 0 | 0 |
| meta_run03_standard | 4.7278 | 4.7278 | 2.8038 | 0.6795 | 1.2445 | 0 |
| neg1_meta_b3prod_a2 | 3.07 | 3.07 | 2.281 | 0.789 | 0 | 0 |
| neg2_meta_refresh_a2 | 4.579 | 4.579 | 2.6422 | 0.7558 | 1.181 | 0 |
| neg3_hormuz_prodrunner_b1b | 5.6561 | 5.6561 | 2.4223 | 1.6638 | 1.57 | 0 |
| neg7_meta_prodrunner_b1b | 2.5062 | 2.5062 | 2.0249 | 0.4813 | 0 | 0 |

合計 31.519円 / 1run平均 3.502円
{"Checker関連(Stage1初回+再分類)": 19.1371, "後段判定関連(Stage2+S1+floor_verify)": 7.2932, "Rewrite関連(Rewrite+regen+Recheck+出口)": 5.0887, "分離不能(other)": 0}
