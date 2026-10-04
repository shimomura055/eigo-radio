# summary_01.md (rep27、委任_04)

n instance-run=38 cost=JPY17.4489 worst=JPY2.3655
stage2_blocking=32 floor_only_blocking=7 by_flag={'s1_second_opinion_blocking': 6, 'precheck_floor': 1}
unnecessary_rewrite(normal group)={'definition': 'NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)', 'n_normal_runs': 14, 'n_with_rewrite': 3, 'rate': 0.2143}
runs_with_rewrite_nonsafety={'n': 34, 'with_rewrite': 15} rewrite_executed=24
stage4=3 reasons={'unconfirmed_after_reverify': 1, 'ladder_exhausted_without_full_rewrite': 2}
floor_verify={'n_floor_verify_records': 9, 'n_target': 0, 'n_confirmed': 0, 'n_verify_calls': 0, 'n_released': 0, 'blocking_fixed_by_reason': {}, 'target_reason_counts': {'llm_materiality_blocking': 9}, 'out_of_scope_flag': {}, 'cost_jpy': 0.0}
item8={'n_runs': 38, 'ja_changed': 0, 'ja_labelled_calls': 0, 'paired': 0, 'en_title_rewritten': 0, 'fired_cycles': 5, 'fired_and_recheck': 5, 'switches_distinct': ['{"CAUSAL_FLOOR": true, "FLOOR_VERIFY_MODE": "time_only", "HANDOFF_MODE": "violation_span", "JA_MODE": "english_only", "STAGE2_SECOND_OPINION": true, "VS_EXPLAIN_SPLIT": true, "VS_MATCH_EXT": true, "VS_SENTENCE_RESTORE": true}']}
item9={'cycles_ge2': 2, 'cycles_ge3': 0, 'severity_wobble': 1, 'carry_forward_comparison': 5, 'carry_forward_covered': 5}
iter7 totals={"n_runs": 38, "stage2_blocking": 39, "floor_only_blocking": 4, "floor_only_by_flag": {"deterministic_floor:changed_actor": 3, "precheck_floor": 1}, "rewrite_executed": 39, "runs_with_rewrite": 23, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 14, "n_with_rewrite": 3, "rate": 0.2143}, "runs_with_rewrite_nonsafety": {"n": 34, "with_rewrite": 19}, "stage4_count": 7, "stage4_reasons": {"ja_deviation_unresolved": 6, "cycle_limit_exhausted_after_recheck": 1}, "cycles_ge2_runs": 8, "cycles_ge3_runs": 5, "cost_jpy_total": 39.5475, "cost_jpy_worst": 8.9545}
rep23 totals={"n_runs": 12, "stage2_blocking": 24, "floor_only_blocking": 2, "floor_only_by_flag": {"precheck_floor": 2}, "rewrite_executed": 13, "runs_with_rewrite": 8, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 2, "n_with_rewrite": 2, "rate": 1.0}, "runs_with_rewrite_nonsafety": {"n": 6, "with_rewrite": 2}, "stage4_count": 4, "stage4_reasons": {"violation_span_unverified": 3, "unconfirmed_after_reverify": 1}, "cycles_ge2_runs": 2, "cycles_ge3_runs": 1, "cost_jpy_total": 7.9137, "cost_jpy_worst": 2.6814}

## per run

- s1 safety_A2A3: RESOLVED_REWRITE s4=None JPY1.0694
- s1 bgroup_B3: RESOLVED_REWRITE s4=None JPY0.298
- s1 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2087
- s1 meta_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.2173
- s1 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2341
- s1 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2147
- s1 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2236
- s1 neg3_hormuz_prodrunner_b1b: STAGE4_ESCALATION s4=unconfirmed_after_reverify JPY0.9144
- s1 bgroup_B1: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.415
- s1 bgroup_B2_hormuz: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1928
- s1 bgroup_B4: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY2.3655
- s1 hormuz_run01_advanced: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.6302
- s1 hormuz_run02_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.2759
- s1 neg4_smallbag_div_a2: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg5_hormuz_div_a2: RESOLVED_REWRITE s4=None JPY0.4954
- s1 neg6_smallbag_div_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg7_meta_prodrunner_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 safety_A4: STAGE4_ESCALATION s4=ladder_exhausted_without_full_rewrite JPY1.4059
- s1 safety_A5: STAGE4_ESCALATION s4=ladder_exhausted_without_full_rewrite JPY0.6448
- s1 safety_er009_changed_actor: RESOLVED_REWRITE s4=None JPY0.3978
- s1 safety_er009_changed_causality: RESOLVED_REWRITE s4=None JPY0.3896
- s1 safety_er009_changed_certainty: RESOLVED_REWRITE s4=None JPY0.5677
- s1 safety_er009_changed_comparison: RESOLVED_REWRITE s4=None JPY0.3347
- s1 safety_er009_changed_negation: RESOLVED_REWRITE s4=None JPY0.4133
- s1 safety_er009_changed_number: RESOLVED_REWRITE s4=None JPY0.6078
- s1 safety_er009_changed_scope: RESOLVED_REWRITE s4=None JPY0.7955
- s1 safety_er009_changed_time: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY0.5845
- s1 safety_er009_unsupported_new_claim: RESOLVED_REWRITE s4=None JPY0.3433
- s2 safety_A2A3: RESOLVED_REWRITE s4=None JPY1.4447
- s2 bgroup_B3: RESOLVED_REWRITE s4=None JPY0.2611
- s2 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0848
- s2 meta_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s2 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0929
- s2 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s2 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.137
- s2 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0765
- s2 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY1.112
