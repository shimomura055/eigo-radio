# TRIAL_01 検証結果 集計 (自動生成 er111_ukus_trial_eval_01.py --summary)

| V | 基準 | 判定 |
|---|---|---|
| V1 | pairs>=50 (both directions) all equivalent except intentional AMB reverse; V1_FORMS all equivalent | PASS |
| V2 | pairs>=30 (both dirs): new PASS (base NG -> trial PASS) = 0 except same-word variant (legit) / intentional AMB uk>us; extra cases all as expected | PASS |
| V3 | cases>=25: proper nouns not equalized by this layer / spelling diff + real misreading stays NG / omission & addition NG / base PASS kept | PASS |
| V4 | PASS->NG = 0; NG->PASS all items eyeballed & classified (cause = ukus pair only); er109-PASS rows reason change = 0 | PASS |
| V5 | rule precision: false-equivalence candidates over all SCOWL British-only words = 0 ; hold-out reproduction & breame (independent dictionary) coverage reported ; real generalization = V5b | PASS |
| V5b | coverage of British-spelled tokens (SCOWL british-only oracle) by the active table + list of mis-mapping candidates | (info) |
| V5c | both forms high-frequency independent words -> human review for semantic overlap (decisions recorded in 'review_decision') | (info) |
| V6 | c12 (Primary/Azure/KP vote/Store guard/rejudge): OFF=NG, ON=PASS, rules=ukus_spelling_variant, retry 0 / LR 0 / HR 0 (mock); neg rows stay NG; PASS->NG 0 | PASS |
| V7 | dictionary load <= 0.5 s (once per process); extra per judgment <= 1 ms (p95, NG path) ; API 0 | PASS |
| V8 | existing tests + isolation AST + golden unchanged; new regressions 0 | PASS |
| V9 | (info) 保存canonical文のUK綴り語を表の直接対のUS形へ置換=『ASRが米綴りで書いた』合成。改善前後のNG件数 | (info) |
