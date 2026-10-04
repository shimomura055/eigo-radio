# summary_01.md (rep29、委任_08)

n instance-run=38 cost=JPY21.7866 worst=JPY4.1427
stage2_blocking=38 floor_only_blocking=5 by_flag={'s1_second_opinion_blocking': 3, 'changed_causality_floor': 1, 'precheck_floor': 1}
unnecessary_rewrite(normal group)={'definition': 'NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)', 'n_normal_runs': 14, 'n_with_rewrite': 3, 'rate': 0.2143}
runs_with_rewrite_nonsafety={'n': 34, 'with_rewrite': 16} rewrite_executed=26
stage4=0 reasons={}
floor_verify={'n_floor_verify_records': 10, 'n_target': 0, 'n_confirmed': 0, 'n_verify_calls': 0, 'n_released': 0, 'blocking_fixed_by_reason': {}, 'target_reason_counts': {'llm_materiality_blocking': 10}, 'out_of_scope_flag': {}, 'cost_jpy': 0.0}
item8={'n_runs': 38, 'ja_changed': 0, 'ja_labelled_calls': 0, 'paired': 0, 'en_title_rewritten': 1, 'fired_cycles': 8, 'fired_and_recheck': 8, 'switches_distinct': ['{"ACTOR_GUARD_MODE": "ag1_strict", "CAUSAL_FLOOR": true, "FLOOR_VERIFY_MODE": "time_only", "HANDOFF_MODE": "violation_span", "JA_MODE": "english_only", "JUDGE_ONLY_CYCLE_AFTER_CAP": true, "LADDER_LOCATION_CARRY": true, "LAST_RESORT_DELETE": true, "MATERIALITY_BLOCKING_PIN": true, "RECHECK_MERGE_UNRESOLVED": true, "REWRITE_REVERT_GUARD": true, "SPAN_FALLBACK_CHAIN": true, "STAGE2_SECOND_OPINION": true, "STAGE2_SIBLING_LOCATIONS_CYCLE1": true, "STAGE2_VERDICT_REUSE_NONBLOCKING": true, "STAGE4_ALLOWLIST": true, "STRUCTURAL_ELEMENT_REWRITE": true, "STRUCTURAL_PAIRS_TO_RECHECK": true, "VS_EXPLAIN_SPLIT": true, "VS_MATCH_EXT": true, "VS_SENTENCE_RESTORE": true}']}
item9={'cycles_ge2': 4, 'cycles_ge3': 1, 'severity_wobble': 0, 'carry_forward_comparison': 12, 'carry_forward_covered': 12}
iter7 totals={"n_runs": 38, "stage2_blocking": 39, "floor_only_blocking": 4, "floor_only_by_flag": {"deterministic_floor:changed_actor": 3, "precheck_floor": 1}, "rewrite_executed": 39, "runs_with_rewrite": 23, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 14, "n_with_rewrite": 3, "rate": 0.2143}, "runs_with_rewrite_nonsafety": {"n": 34, "with_rewrite": 19}, "stage4_count": 7, "stage4_reasons": {"ja_deviation_unresolved": 6, "cycle_limit_exhausted_after_recheck": 1}, "cycles_ge2_runs": 8, "cycles_ge3_runs": 5, "cost_jpy_total": 39.5475, "cost_jpy_worst": 8.9545}
rep23 totals={"n_runs": 12, "stage2_blocking": 24, "floor_only_blocking": 2, "floor_only_by_flag": {"precheck_floor": 2}, "rewrite_executed": 13, "runs_with_rewrite": 8, "unnecessary_rewrite_def_normal_group": {"definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)", "n_normal_runs": 2, "n_with_rewrite": 2, "rate": 1.0}, "runs_with_rewrite_nonsafety": {"n": 6, "with_rewrite": 2}, "stage4_count": 4, "stage4_reasons": {"violation_span_unverified": 3, "unconfirmed_after_reverify": 1}, "cycles_ge2_runs": 2, "cycles_ge3_runs": 1, "cost_jpy_total": 7.9137, "cost_jpy_worst": 2.6814}

## per run

- s1 safety_A2A3: RESOLVED_REWRITE s4=None JPY1.4287
- s1 bgroup_B3: RESOLVED_REWRITE s4=None JPY0.8283
- s1 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2184
- s1 meta_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.1395
- s1 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.4119
- s1 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2339
- s1 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.204
- s1 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY0.9211
- s1 bgroup_B1: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.3642
- s1 bgroup_B2_hormuz: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.2035
- s1 bgroup_B4: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY1.7912
- s1 hormuz_run01_advanced: RESOLVED_REWRITE s4=None JPY1.0909
- s1 hormuz_run02_advanced: ACCEPTABLE_STAGE1 s4=None JPY0.2756
- s1 neg4_smallbag_div_a2: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg5_hormuz_div_a2: RESOLVED_REWRITE s4=None JPY0.9407
- s1 neg6_smallbag_div_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 neg7_meta_prodrunner_b1b: ACCEPTABLE_STAGE1 s4=None JPY0
- s1 safety_A4: RESOLVED_REWRITE s4=None JPY4.1427
- s1 safety_A5: RESOLVED_REWRITE s4=None JPY1.0797
- s1 safety_er009_changed_actor: RESOLVED_REWRITE s4=None JPY0.3777
- s1 safety_er009_changed_causality: RESOLVED_REWRITE s4=None JPY0.4075
- s1 safety_er009_changed_certainty: RESOLVED_REWRITE s4=None JPY0.5642
- s1 safety_er009_changed_comparison: RESOLVED_REWRITE s4=None JPY0.3288
- s1 safety_er009_changed_negation: RESOLVED_REWRITE s4=None JPY0.3454
- s1 safety_er009_changed_number: RESOLVED_REWRITE s4=None JPY0.3293
- s1 safety_er009_changed_scope: RESOLVED_REWRITE s4=None JPY1.0273
- s1 safety_er009_changed_time: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY0.6397
- s1 safety_er009_unsupported_new_claim: RESOLVED_REWRITE s4=None JPY0.4217
- s2 safety_A2A3: RESOLVED_REWRITE_THEN_DOWNGRADE s4=None JPY1.339
- s2 bgroup_B3: RESOLVED_REWRITE s4=None JPY0.5028
- s2 meta_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0861
- s2 meta_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s2 hormuz_run03_standard: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1939
- s2 hormuz_run03_advanced: ACCEPTABLE_STAGE1 s4=None JPY0
- s2 neg1_meta_b3prod_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.1541
- s2 neg2_meta_refresh_a2: RESOLVED_STAGE2_DOWNGRADE s4=None JPY0.0857
- s2 neg3_hormuz_prodrunner_b1b: RESOLVED_REWRITE s4=None JPY0.7091
