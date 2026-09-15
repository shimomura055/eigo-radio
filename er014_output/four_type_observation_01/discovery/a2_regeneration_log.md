# Discovery A2 Regeneration Log (USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY Part B)

## 方式選定理由
既存Discovery S2正式Production path(run_one_pattern_staged_discovery_focus、editorial_mode="discovery_focus_staged"相当、同一Ledger)で再生成する方式を採用した。604語版の圧縮編集(Local Rewriteの多段人手編集)はFact Safety(圧縮のたびに新たなLedger逸脱リスクが生じ、既存Local Rewrite安全装置[MAX_REWRITE_CYCLES=3]で吸収しきれない可能性がある)・コスト両面(圧縮編集の反復QAコストが再生成2回より高くなりうる)で再生成方式よりリスクが高いと判断し、不採用とした(委任文の指定どおり)。

## Attempt別結果
- attempt1: status=OK word_count_raw=510 word_count_final=530 jargon_before_hit=3 jargon_fix_applied=True jargon_after_hit=0 elapsed=382.21s
  final_qa_after_jargon_fix: {'fact_checker_status': 'FACT_CHECK_COMPLETED', 'fact_checker_verdict': 'REVIEW_REQUIRED', 'ledger_deviation_overall_status': 'LEDGER_COMPLIANT', 'ledger_deviation_major_count': 0, 'directional_fact_precheck_status': 'DIRECTION_REVIEW_REQUIRED'}
- attempt2: status=STOP_BUDGET_EXCEEDED_MIDRUN word_count_raw=None word_count_final=None jargon_before_hit=None jargon_fix_applied=False jargon_after_hit=None elapsed=333.61s

## 採用判断
{'adopted': True, 'chosen_attempt': 1, 'word_count_flag': 'WORD_COUNT_GE_500', 'word_counts_all_candidates': {1: 530}}

## 費用(実測、Part Bのみ、budget=¥120.00)
実測: ¥155.06
