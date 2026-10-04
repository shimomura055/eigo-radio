# recount_01.md (委任_68、費用0円の再集計)

走査: instance JSON 474件(27ディレクトリ、smoke/fixtures/carry-forward修正前は除外)。Checker MAJOR claim(Stage 2通過)延べ1143件、うち最終非BLOCKING(降格)=534件。
降格の経路: {'llm_direct': 471, 'two_of_two': 14, 'det_downgrade_other': 49}

## all_downgrades

- 全体: {'n': 534, 'basis_none': 218, 'basis_none_rate': 0.408, 'basis_dist': {'none': 218, 'ledger_conditions': 52, 'ledger_claim': 73, 'unsupported_relationship': 165, 'ledger_scope': 24, 'ledger_numeric_value': 1, 'notes_for_writer': 1}}
- ACCEPTABLE: n=227 basis=none 184件(0.811) basis分布={'none': 184, 'ledger_claim': 30, 'ledger_conditions': 8, 'ledger_scope': 1, 'ledger_numeric_value': 1, 'unsupported_relationship': 2, 'notes_for_writer': 1}
- QUALITY: n=307 basis=none 34件(0.111) basis分布={'ledger_conditions': 44, 'ledger_claim': 43, 'unsupported_relationship': 163, 'none': 34, 'ledger_scope': 23}

| rubric | n | basis=none | 率 | ACCEPTABLE n(none) | QUALITY n(none) |
|---|---|---|---|---|---|
| R3''' | 281 | 85 | 0.302 | 109(79) | 172(6) |
| V4 | 32 | 13 | 0.406 | 9(6) | 23(7) |
| V5 | 55 | 16 | 0.291 | 13(8) | 42(8) |
| V6 | 62 | 29 | 0.468 | 27(26) | 35(3) |
| V7b | 104 | 75 | 0.721 | 69(65) | 35(10) |

| cycle | n | basis=none | 率 |
|---|---|---|---|
| cycle1 | 339 | 153 | 0.451 |
| cycle2plus | 195 | 65 | 0.333 |

## llm_direct(S1_target)

- 全体: {'n': 471, 'basis_none': 218, 'basis_none_rate': 0.463, 'basis_dist': {'none': 218, 'ledger_conditions': 40, 'ledger_claim': 53, 'unsupported_relationship': 138, 'ledger_scope': 20, 'ledger_numeric_value': 1, 'notes_for_writer': 1}}
- ACCEPTABLE: n=223 basis=none 184件(0.825) basis分布={'none': 184, 'ledger_claim': 29, 'ledger_conditions': 8, 'ledger_numeric_value': 1, 'notes_for_writer': 1}
- QUALITY: n=248 basis=none 34件(0.137) basis分布={'ledger_conditions': 32, 'ledger_claim': 24, 'unsupported_relationship': 138, 'none': 34, 'ledger_scope': 20}

| rubric | n | basis=none | 率 | ACCEPTABLE n(none) | QUALITY n(none) |
|---|---|---|---|---|---|
| R3''' | 246 | 85 | 0.346 | 105(79) | 141(6) |
| V4 | 28 | 13 | 0.464 | 9(6) | 19(7) |
| V5 | 48 | 16 | 0.333 | 13(8) | 35(8) |
| V6 | 45 | 29 | 0.644 | 27(26) | 18(3) |
| V7b | 104 | 75 | 0.721 | 69(65) | 35(10) |

| cycle | n | basis=none | 率 |
|---|---|---|---|
| cycle1 | 299 | 153 | 0.512 |
| cycle2plus | 172 | 65 | 0.378 |

- rep24のllm_direct: {'n': 68, 'basis_none': 47, 'basis_none_rate': 0.691, 'basis_dist': {'none': 47, 'ledger_claim': 12, 'unsupported_relationship': 3, 'ledger_conditions': 6}}
- V7b全体のllm_direct(ACCEPTABLE/QUALITY別): {'ACCEPTABLE': {'n': 69, 'basis_none': 65, 'basis_none_rate': 0.942, 'basis_dist': {'none': 65, 'ledger_conditions': 3, 'ledger_claim': 1}}, 'QUALITY': {'n': 35, 'basis_none': 10, 'basis_none_rate': 0.286, 'basis_dist': {'ledger_conditions': 9, 'ledger_claim': 13, 'none': 10, 'unsupported_relationship': 3}}}

## 既存2-of-2(NORMAL群)

- log_entries_total(1回目BLOCKINGで2回目を呼んだclaim数): 46
- results: {'BLOCKING(both agree)': 32, 'DOWNGRADED(1/2 non-blocking)': 14}
- downgraded_by_two_of_two: 14
- downgraded_by_dir_instance: {'_iter5|neg7_meta_prodrunner_b1b': 5, '_iter5|neg1_meta_b3prod_a2': 1, '_iter7|neg1_meta_b3prod_a2': 1, '_rep11|neg1_meta_b3prod_a2': 2, '_rep12|neg1_meta_b3prod_a2': 1, '_rep7|neg1_meta_b3prod_a2': 2, '_rep8|neg1_meta_b3prod_a2': 1, '_rep9|neg1_meta_b3prod_a2': 1}
- downgraded_final_materiality: {'ACCEPTABLE': 4, 'QUALITY': 10}
- orig_basis_dist(1回目BLOCKINGのbasis): {'ledger_scope': 4, 'ledger_claim': 2, 'unsupported_relationship': 6, 'ledger_conditions': 2}
- note: 2-of-2無しの場合、この件数のclaimは1回目のBLOCKINGのまま残り、Rewrite対象になる=NORMAL群の過剰Major見かけ上の改善幅
- instances_with_downgrade: 8
- instance_cycles_with_log: 20

rubric版はdir名から推定(iter1-7・rep7-15=R3''' / rep16=V4 / iter8・rep17=V5 / rep18-22=V6 / rep23-25=V7b)。委任_67設計書§2と同じ。
