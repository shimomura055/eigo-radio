# precheck baseline (pre-fix, number_only, JPY 0)

runs analyzed=26 skipped=1

- SKIPPED allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2_stop1: b1b/article.md or research_ledger missing

## per-run

| run_id | sentences | extracted values | fires | QTY-expr sentences (extracted) |
|---|---|---|---|---|
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1 | 29 | 0 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2 | 32 | 1 | 2 | 1 (1) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep1 | 26 | 3 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2 | 30 | 3 | 0 | 1 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/meta/nb/p2/rep1 | 28 | 0 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2 | 29 | 0 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep1 | 28 | 3 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/sewer/nb/p2/rep2 | 31 | 0 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep1 | 37 | 0 | 0 | 0 (0) |
| allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2 | 37 | 0 | 0 | 0 (0) |
| polysemy04_control:open233_polysemy_trial_04/runs/ai_control/control/rep1 | 24 | 0 | 0 | 0 (0) |
| polysemy04_control:open233_polysemy_trial_04/runs/hormuz/control/rep1 | 29 | 6 | 0 | 0 (0) |
| polysemy04_control:open233_polysemy_trial_04/runs/meta/control/rep1 | 26 | 0 | 0 | 0 (0) |
| polysemy04_control:open233_polysemy_trial_04/runs/sewer/control/rep1 | 30 | 3 | 0 | 0 (0) |
| polysemy04_control:open233_polysemy_trial_04/runs/space_weapons/control/rep1 | 39 | 0 | 0 | 1 (0) |
| meta_ent01:open233_meta_allfact_note_ent_01/runs/meta/nb/p1/rep1 | 30 | 0 | 0 | 0 (0) |
| meta_ent01:open233_meta_allfact_note_ent_01/runs/meta/nb/p2/rep1 | 24 | 0 | 0 | 0 (0) |
| prod_e2e02:bgroup_B3 | 24 | 8 | 0 | 0 (0) |
| prod_e2e02:hormuz_run03_advanced | 24 | 5 | 0 | 0 (0) |
| prod_e2e02:hormuz_run03_standard | 33 | 5 | 0 | 0 (0) |
| prod_e2e02:meta_run03_advanced | 27 | 0 | 0 | 0 (0) |
| prod_e2e02:meta_run03_standard | 36 | 0 | 0 | 0 (0) |
| prod_e2e02:neg1_meta_b3prod_a2 | 35 | 0 | 0 | 0 (0) |
| prod_e2e02:neg2_meta_refresh_a2 | 32 | 0 | 0 | 0 (0) |
| prod_e2e02:neg3_hormuz_prodrunner_b1b | 18 | 3 | 0 | 0 (0) |
| prod_e2e02:neg7_meta_prodrunner_b1b | 30 | 0 | 0 | 0 (0) |

fires total = 2

## all fires

- allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2 | EVID-006 | foreign=[33.3] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.
- allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2 | CONTROL-004 | foreign=[33.3] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.

## quantity-expression sentences (half/third/quarter/fifth/tenth/double/triple/twice); extracted = precheck fraction dict hit

- allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2 #6 terms=['third'] extracted=True [('a third', 33.3)] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.
- allfact_e2e02_p2:open233_allfact_note_e2e_02/runs/hormuz/nb/p2/rep2 #18 terms=['third'] extracted=False  | But in the third act, the reaction from the oil market was much calmer.
- polysemy04_control:open233_polysemy_trial_04/runs/space_weapons/control/rep1 #31 terms=['third'] extracted=False  | The third is the ground equipment that sends instructions to satellites.
