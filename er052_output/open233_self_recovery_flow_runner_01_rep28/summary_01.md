# summary_01.md (rep28、委任_04)

n instance-run=38 cost=JPY20.5012 worst=JPY2.1636
stage2_blocking=35 floor_only_blocking=5 by_flag={'s1_second_opinion_blocking': 1, 'deterministic_floor:changed_actor': 3, 'precheck_floor': 1}
unnecessary_rewrite(normal group)={'definition': 'NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)', 'n_normal_runs': 14, 'n_with_rewrite': 5, 'rate': 0.3571}
runs_with_rewrite_nonsafety={'n': 34, 'with_rewrite': 17} rewrite_executed=24
stage4=3 reasons={'ladder_exhausted_without_full_rewrite': 2, 'degenerate_rewrite_output': 1}
floor_verify={'n_floor_verify_records': 13, 'n_target': 0, 'n_confirmed': 0, 'n_verify_calls': 0, 'n_released': 0, 'blocking_fixed_by_reason': {}, 'target_reason_counts': {'out_of_scope_flag:changed_actor': 3, 'llm_materiality_blocking': 10}, 'out_of_scope_flag': {'changed_actor': 3}, 'cost_jpy': 0.0}
item8={'n_runs': 38, 'ja_changed': 0, 'ja_labelled_calls': 0, 'paired': 0, 'en_title_rewritten': 0, 'fired_cycles': 8, 'fired_and_recheck': 8, 'switches_distinct': ['{"CAUSAL_FLOOR": true, "FLOOR_VERIFY_MODE": "time_only", "HANDOFF_MODE": "violation_span", "JA_MODE": "english_only", "RECHECK_MERGE_UNRESOLVED": true, "STAGE2_SECOND_OPINION": true, "VS_EXPLAIN_SPLIT": true, "VS_MATCH_EXT": true, "VS_SENTENCE_RESTORE": true}']}
item9={'cycles_ge2': 5, 'cycles_ge3': 0, 'severity_wobble': 0, 'carry_forward_comparison': 9, 'carry_forward_covered': 9}
iter7 totals={"n_runs": 38, "stage2_blocking": 39, "floor_only_blocking": 4, "floor_only_by_flag": {"deterministic_floor:changed_actor": 3, "precheck_floor": 1}, "rewrite_executed": 39, "runs_with_rewrite": 23, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 14, "n_with_rewrite": 3, "rate": 0.2143}, "runs_with_rewrite_nonsafety": {"n": 34, "with_rewrite": 19}, "stage4_count": 7, "stage4_reasons": {"ja_deviation_unresolved": 6, "cycle_limit_exhausted_after_recheck": 1}, "cycles_ge2_runs": 8, "cycles_ge3_runs": 5, "cost_jpy_total": 39.5475, "cost_jpy_worst": 8.9545}
rep23 totals={"n_runs": 12, "stage2_blocking": 24, "floor_only_blocking": 2, "floor_only_by_flag": {"precheck_floor": 2}, "rewrite_executed": 13, "runs_with_rewrite": 8, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 2, "n_with_rewrite": 2, "rate": 1.0}, "runs_with_rewrite_nonsafety": {"n": 6, "with_rewrite": 2}, "stage4_count": 4, "stage4_reasons": {"violation_span_unverified": 3, "unconfirmed_after_reverify": 1}, "cycles_ge2_runs": 2, "cycles_ge3_runs": 1, "cost_jpy_total": 7.9137, "cost_jpy_worst": 2.6814}

## per run

- s1 safety_A2A3: RESOLVED_REWRITE s4=None JPY1.3698
- s1 bgroup_B3: RESOLVED_REWRITE s4=None JPY0.452
- s1 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2177
- s1 meta_run03_advanced: RESOLVED_REWRITE s4=None JPY1.1545
- s1 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2239
- s1 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1978
- s1 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.087
- s1 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY0.9186
- s1 bgroup_B1: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.3736
- s1 bgroup_B2_hormuz: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.211
- s1 bgroup_B4: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY2.1636
- s1 hormuz_run01_advanced: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.7183
- s1 hormuz_run02_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.208
- s1 neg4_smallbag_div_a2: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg5_hormuz_div_a2: RESOLVED_REWRITE s4=None JPY0.9752
- s1 neg6_smallbag_div_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg7_meta_prodrunner_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 safety_A4: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY1.8189
- s1 safety_A5: RESOLVED_REWRITE s4=None JPY0.9152
- s1 safety_er009_changed_actor: RESOLVED_REWRITE s4=None JPY0.3459
- s1 safety_er009_changed_causality: RESOLVED_REWRITE s4=None JPY0.3721
- s1 safety_er009_changed_certainty: RESOLVED_REWRITE s4=None JPY0.7309
- s1 safety_er009_changed_comparison: RESOLVED_REWRITE s4=None JPY0.3243
- s1 safety_er009_changed_negation: RESOLVED_REWRITE s4=None JPY0.365
- s1 safety_er009_changed_number: RESOLVED_REWRITE s4=None JPY0.3365
- s1 safety_er009_changed_scope: STAGE4_ESCALATION s4=ladder_exhausted_without_full_rewrite JPY1.4145
- s1 safety_er009_changed_time: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY0.6163
- s1 safety_er009_unsupported_new_claim: STAGE4_ESCALATION s4=degenerate_rewrite_output JPY0.1465
- s2 safety_A2A3: RESOLVED_REWRITE s4=None JPY1.0519
- s2 bgroup_B3: RESOLVED_REWRITE s4=None JPY0.3463
- s2 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1044
- s2 meta_run03_advanced: STAGE4_ESCALATION s4=ladder_exhausted_without_full_rewrite JPY1.1632
- s2 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1271
- s2 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s2 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1361
- s2 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0825
- s2 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY0.8326
