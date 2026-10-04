# summary_ab_01.md (rep28a、委任_06 A/B)

totals={"A": {"n_runs": 4, "missing_runs(例外相当)": 0, "n_rechecks": 2, "n_self_contradiction": 2, "self_contradiction_rate": 1.0, "reverify_calls": 2, "formal_resolution_items": 0, "stage4_unified": 0, "stage4_reasons": {}, "unnecessary_rewrite_runs(NORMAL群)": 2, "n_merges": 0, "cycles_ge2": 0, "cost_total": 2.7119, "cost_worst": 1.3646, "residual_unflagged": 0}, "B": {"n_runs": 4, "missing_runs(例外相当)": 0, "n_rechecks": 2, "n_self_contradiction": 2, "self_contradiction_rate": 1.0, "reverify_calls": 2, "formal_resolution_items": 0, "stage4_unified": 0, "stage4_reasons": {}, "unnecessary_rewrite_runs(NORMAL群)": 2, "n_merges": 0, "cycles_ge2": 0, "cost_total": 2.1287, "cost_worst": 1.024, "residual_unflagged": 0}}
criteria={"lower_self_contradiction": false, "a_formal_resolution_zero_in_B": true, "b_stage4_not_increased": true, "b_miss_not_increased": true, "complete_8_runs": true, "N3_adopt": false}

- A s1 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None cycles=1 recheck=1 selfcontra=1 reverify=1 merges=0 rewrite=1 JPY1.3646
    reverify(c1) status=LEDGER_COMPLIANT all_prior=True deviations=[]
- A s1 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None cycles=1 recheck=0 selfcontra=0 reverify=0 merges=0 rewrite=0 JPY0.1967
- A s2 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None cycles=1 recheck=1 selfcontra=1 reverify=1 merges=0 rewrite=1 JPY1.0804
    reverify(c1) status=LEDGER_COMPLIANT all_prior=True deviations=[]
- A s2 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None cycles=1 recheck=0 selfcontra=0 reverify=0 merges=0 rewrite=0 JPY0.0702
- B s1 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None cycles=1 recheck=1 selfcontra=1 reverify=1 merges=0 rewrite=1 JPY0.94
    reverify(c1) status=LEDGER_COMPLIANT all_prior=True deviations=[]
- B s1 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None cycles=1 recheck=0 selfcontra=0 reverify=0 merges=0 rewrite=0 JPY0.082
- B s2 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None cycles=1 recheck=1 selfcontra=1 reverify=1 merges=0 rewrite=1 JPY1.024
    reverify(c1) status=LEDGER_COMPLIANT all_prior=True deviations=[]
- B s2 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None cycles=1 recheck=0 selfcontra=0 reverify=0 merges=0 rewrite=0 JPY0.0827
