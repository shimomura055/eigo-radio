# summary_01.md (rep24、委任_63)

n instance-run=38 cost=JPY16.7238 worst=JPY1.7625
stage2_blocking=35 floor_only_blocking=4 by_flag={'precheck_floor': 1, 'deterministic_floor:changed_actor': 3}
unnecessary_rewrite(normal group)={'definition': 'NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)', 'n_normal_runs': 14, 'n_with_rewrite': 3, 'rate': 0.2143}
runs_with_rewrite_nonsafety={'n': 34, 'with_rewrite': 15} rewrite_executed=24
stage4=2 reasons={'violation_span_unverified': 2}
floor_verify={'n_floor_verify_records': 12, 'n_target': 0, 'n_confirmed': 0, 'n_verify_calls': 0, 'n_released': 0, 'blocking_fixed_by_reason': {}, 'target_reason_counts': {'llm_materiality_blocking': 9, 'out_of_scope_flag:changed_actor': 3}, 'out_of_scope_flag': {'changed_actor': 3}, 'cost_jpy': 0.0}
item8={'n_runs': 38, 'ja_changed': 0, 'ja_labelled_calls': 0, 'paired': 0, 'en_title_rewritten': 0, 'fired_cycles': 8, 'fired_and_recheck': 8, 'switches_distinct': ['{"FLOOR_VERIFY_MODE": "time_only", "HANDOFF_MODE": "violation_span", "JA_MODE": "english_only", "VS_EXPLAIN_SPLIT": true, "VS_MATCH_EXT": true}']}
item9={'cycles_ge2': 7, 'cycles_ge3': 0, 'severity_wobble': 1, 'carry_forward_comparison': 9, 'carry_forward_covered': 9}
iter7 totals={"n_runs": 38, "stage2_blocking": 39, "floor_only_blocking": 4, "floor_only_by_flag": {"deterministic_floor:changed_actor": 3, "precheck_floor": 1}, "rewrite_executed": 39, "runs_with_rewrite": 23, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 14, "n_with_rewrite": 3, "rate": 0.2143}, "runs_with_rewrite_nonsafety": {"n": 34, "with_rewrite": 19}, "stage4_count": 7, "stage4_reasons": {"ja_deviation_unresolved": 6, "cycle_limit_exhausted_after_recheck": 1}, "cycles_ge2_runs": 8, "cycles_ge3_runs": 5, "cost_jpy_total": 39.5475, "cost_jpy_worst": 8.9545}
rep23 totals={"n_runs": 12, "stage2_blocking": 24, "floor_only_blocking": 2, "floor_only_by_flag": {"precheck_floor": 2}, "rewrite_executed": 13, "runs_with_rewrite": 8, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 2, "n_with_rewrite": 2, "rate": 1.0}, "runs_with_rewrite_nonsafety": {"n": 6, "with_rewrite": 2}, "stage4_count": 4, "stage4_reasons": {"violation_span_unverified": 3, "unconfirmed_after_reverify": 1}, "cycles_ge2_runs": 2, "cycles_ge3_runs": 1, "cost_jpy_total": 7.9137, "cost_jpy_worst": 2.6814}

## per run

- s1 safety_A2A3: RESOLVED_REWRITE s4=None JPY0.9227
- s1 bgroup_B3: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY0.7671
- s1 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.043
- s1 meta_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.2108
- s1 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0566
- s1 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1498
- s1 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1612
- s1 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY0.7884
- s1 bgroup_B1: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2536
- s1 bgroup_B2_hormuz: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1566
- s1 bgroup_B4: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY1.5691
- s1 hormuz_run01_advanced: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.4881
- s1 hormuz_run02_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.1616
- s1 neg4_smallbag_div_a2: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg5_hormuz_div_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.3077
- s1 neg6_smallbag_div_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg7_meta_prodrunner_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 safety_A4: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY1.0075
- s1 safety_A5: RESOLVED_REWRITE s4=None JPY0.7864
- s1 safety_er009_changed_actor: RESOLVED_REWRITE s4=None JPY0.357
- s1 safety_er009_changed_causality: RESOLVED_REWRITE s4=None JPY0.4246
- s1 safety_er009_changed_certainty: RESOLVED_REWRITE s4=None JPY0.4495
- s1 safety_er009_changed_comparison: RESOLVED_REWRITE s4=None JPY0.3198
- s1 safety_er009_changed_negation: RESOLVED_REWRITE s4=None JPY0.3442
- s1 safety_er009_changed_number: RESOLVED_REWRITE s4=None JPY0.1551
- s1 safety_er009_changed_scope: RESOLVED_REWRITE s4=None JPY0.8424
- s1 safety_er009_changed_time: RESOLVED_REWRITE s4=None JPY0.3373
- s1 safety_er009_unsupported_new_claim: RESOLVED_REWRITE s4=None JPY0.3497
- s2 safety_A2A3: STAGE4_ESCALATION s4=violation_span_unverified JPY1.0597
- s2 bgroup_B3: STAGE4_ESCALATION s4=violation_span_unverified JPY0.7374
- s2 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.047
- s2 meta_run03_advanced: RESOLVED_REWRITE s4=None JPY1.7625
- s2 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0894
- s2 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s2 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0587
- s2 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0562
- s2 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY1.5031
