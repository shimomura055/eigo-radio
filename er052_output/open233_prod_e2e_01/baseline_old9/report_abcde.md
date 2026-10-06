# 報告A〜E集計(委任_02 / 比較基準値)

**旧仕様9 run(frozen)・比較基準値・新仕様のEvidenceではない**。ラベルは `--labels` の外部jsonのみ(推測ラベルの新規付与なし)。UNLABELEDは未ラベル件数。
対象run: 9 (bgroup_B3, hormuz_run03_advanced, hormuz_run03_standard, meta_run03_advanced, meta_run03_standard, neg1_meta_b3prod_a2, neg2_meta_refresh_a2, neg3_hormuz_prodrunner_b1b, neg7_meta_prodrunner_b1b)

## A. Checker(初回候補、重複はclaim単位=norm)
| 項目 | 値 |
|---|---|
| AI候補(claim) | 130 |
| 機械候補(claim) | 21 |
| AIのみ | 130 |
| 機械のみ | 21 |
| AIと機械の重複 | 0 |
| 重複除外前の延べ | 151 |
| 重複除外後のChecker総候補(=後段へ渡した件数) | 151 |
| AI候補 true_problem | {"Y": 0, "N": 0, "UNDECIDABLE": 0, "UNLABELED": 130} |
| 機械候補 true_problem | {"Y": 0, "N": 0, "UNDECIDABLE": 0, "UNLABELED": 21} |
| 機械候補の内訳 | {"negation_polarity_mismatch": 18, "deterministic": 21, "quote_not_in_ledger": 3} |
| 再分類前後フィールド | MISSING(旧仕様に無し) |

run別:
| run | AI | 機械 | AIのみ | 機械のみ | 重複 | 延べ | 除外後(後段へ) |
|---|---|---|---|---|---|---|---|
| bgroup_B3 | 6 | 2 | 6 | 2 | 0 | 8 | 8 |
| hormuz_run03_advanced | 8 | 1 | 8 | 1 | 0 | 9 | 9 |
| hormuz_run03_standard | 7 | 3 | 7 | 3 | 0 | 10 | 10 |
| meta_run03_advanced | 15 | 1 | 15 | 1 | 0 | 16 | 16 |
| meta_run03_standard | 20 | 3 | 20 | 3 | 0 | 23 | 23 |
| neg1_meta_b3prod_a2 | 27 | 5 | 27 | 5 | 0 | 32 | 32 |
| neg2_meta_refresh_a2 | 15 | 1 | 15 | 1 | 0 | 16 | 16 |
| neg3_hormuz_prodrunner_b1b | 10 | 3 | 10 | 3 | 0 | 13 | 13 |
| neg7_meta_prodrunner_b1b | 22 | 2 | 22 | 2 | 0 | 24 | 24 |

## B. 後段判定(cycle1)
| 項目 | 値 |
|---|---|
| n_claim_judgments | 178 |
| downstream_ai | {"重大(BLOCKING)": 5, "軽微(QUALITY)": 17, "問題なし(ACCEPTABLE)": 156} |
| downstream_ai_posteval | {"真に重大だった(AI重大&Y)": 4, "不要に重大判定(AI重大&N)": 0, "AI重大の判断不能": 0, "AI重大のUNLABELED": 1, "真に重大だったのに軽微/問題なし(Y&AI非重大)": 1} |
| downstream_machine_floor | {"発火件数": 31, "種別内訳": {"changed_time": 8, "changed_actor": 6, "changed_negation": 5, "changed_comparison": 12, "changed_number": 4}, "AI判定との重複(AIもBLOCKING)": 4, "機械のみで重大化": 27, "真に重大だった(Y)": 5, "不要に重大化(N)": 20, "判断不能": 4, "UNLABELED": 2} |

## B. 後段判定(全cycle合算)
| 項目 | 値 |
|---|---|
| n_claim_judgments | 326 |
| downstream_ai | {"重大(BLOCKING)": 5, "軽微(QUALITY)": 31, "問題なし(ACCEPTABLE)": 290} |
| downstream_ai_posteval | {"真に重大だった(AI重大&Y)": 4, "不要に重大判定(AI重大&N)": 0, "AI重大の判断不能": 0, "AI重大のUNLABELED": 1, "真に重大だったのに軽微/問題なし(Y&AI非重大)": 2} |
| downstream_machine_floor | {"発火件数": 37, "種別内訳": {"changed_time": 10, "changed_actor": 7, "changed_negation": 5, "changed_comparison": 14, "changed_number": 4, "changed_causality_floor": 1, "tier0:aux:issue_actor": 1}, "AI判定との重複(AIもBLOCKING)": 4, "機械のみで重大化": 33, "真に重大だった(Y)": 6, "不要に重大化(N)": 24, "判断不能": 5, "UNLABELED": 2} |

## C. Rewrite
| 項目 | 値 |
|---|---|
| Rewrite発生件数(rewrite_records) | 40 |
| guard_ok件数 | 37 |
| Rewrite発生run数 | 8 |
| run総数 | 9 |
| 必要だった | 0 |
| 不要だった | 0 |
| 判断不能 | 0 |
| ラベルUNLABELED | 40 |
| Rewrite後に再修正が必要(同fact次cycleもBLOCKING) | 8 |
| 再修正判定不能(次cycleなし/ID無) | 9 |
| per_run | {"bgroup_B3": 3, "hormuz_run03_advanced": 1, "meta_run03_advanced": 4, "meta_run03_standard": 5, "neg1_meta_b3prod_a2": 9, "neg2_meta_refresh_a2": 2, "neg3_hormuz_prodrunner_b1b": 2, "neg7_meta_prodrunner_b1b": 14} |

## D. Human Review(目標0件)
到達run: ['neg7_meta_prodrunner_b1b']、出口BLOCKING claim 3件

- [neg7_meta_prodrunner_b1b] `So it sounds like a simple story: you make a request, and someone takes care of the call.` fact=MUSE-HC-004 | Checker AI=MISSING / 機械=MISSING | 後段AI=ACCEPTABLE / 機械=changed_causality_floor | Rewrite={"method": "e2_generic_rewrite(violation_span(EN,L0))", "guard_ok": true, "ladder": "3_sentence"} | Recheck={"overall": "MISSING", "all_prior_resolved": "MISSING", "resolved_by_index": "MISSING"} | 直接原因=blocking_structural_after_ladder
- [neg7_meta_prodrunner_b1b] `The issue was not just that humans handled calls.` fact=MUSE-HC-010 | Checker AI=MISSING / 機械=MISSING | 後段AI=ACCEPTABLE / 機械=deterministic_floor:changed_comparison | Rewrite={"method": "violation_span_unverified", "guard_ok": false, "ladder": null} | Recheck={"overall": "MISSING", "all_prior_resolved": "MISSING", "resolved_by_index": "MISSING"} | 直接原因=blocking_structural_after_ladder
- [neg7_meta_prodrunner_b1b] `Users might not know who was doing the work they had asked AI to do—and their personal inf` fact=MUSE-HC-010 | Checker AI=MISSING / 機械=MISSING | 後段AI=ACCEPTABLE / 機械=tier0:aux:issue_actor | Rewrite={"method": "violation_span_unverified", "guard_ok": false, "ladder": null} | Recheck={"overall": "MISSING", "all_prior_resolved": "MISSING", "resolved_by_index": "MISSING"} | 直接原因=blocking_structural_after_ladder

## E. Safety・Cost
Safety: {"source": "er052_output/open233_e2e_acceptance_01\\e2e_aggregate.json", "真の重大Fact見逃し件数(出口)": 0, "重大Fact検出件数(Stage1 M)": "1/1", "n_gold_checks": 1, "note": "gold(既知重大)行のみ。gold以外の真重大はラベル無しのため算出不能"}

| run | total_cost_jpy | call_log合計 | Checker | 後段判定 | Rewrite関連 | other |
|---|---|---|---|---|---|---|
| bgroup_B3 | 4.5494 | 4.5494 | 1.4949 | 1.1762 | 1.8783 | 0 |
| hormuz_run03_advanced | 3.4427 | 3.4427 | 1.1544 | 1.2172 | 1.0711 | 0 |
| hormuz_run03_standard | 2.1737 | 2.1737 | 1.4684 | 0.7053 | 0 | 0 |
| meta_run03_advanced | 5.4284 | 5.4284 | 1.4773 | 1.6069 | 2.3442 | 0 |
| meta_run03_standard | 5.1642 | 5.1642 | 1.6825 | 1.3044 | 2.1773 | 0 |
| neg1_meta_b3prod_a2 | 8.8186 | 8.8186 | 1.3022 | 2.7276 | 4.7888 | 0 |
| neg2_meta_refresh_a2 | 3.7869 | 3.7869 | 1.2682 | 1.2904 | 1.2283 | 0 |
| neg3_hormuz_prodrunner_b1b | 3.9982 | 3.9982 | 1.0901 | 1.4154 | 1.4927 | 0 |
| neg7_meta_prodrunner_b1b | 6.5503 | 6.5503 | 1.6703 | 1.5528 | 3.3272 | 0 |

合計 43.912円 / 1run平均 4.879円
{"Checker関連(Stage1初回+再分類)": 12.6083, "後段判定関連(Stage2+S1+floor_verify)": 12.9962, "Rewrite関連(Rewrite+regen+Recheck+出口)": 18.3079, "分離不能(other)": 0}
