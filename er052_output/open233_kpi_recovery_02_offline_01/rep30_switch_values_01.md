# rep30 後段スイッチ値一覧(段階BのE2E構成の正本、委任_07、¥0 read-only)

出典: `er052_output/open233_self_recovery_flow_runner_01_rep30/run_log_main.json`(`switches`、実行時の実値)、`summary_kpi_01.json`の`switches`/`models`、`er052_open233_self_recovery_flow_runner_01_rep30_full_01.py`の`apply_switches`(assert)と`run_instance(... enable_s1u=False ...)`、`er052_open233_self_recovery_flow_runner_01.py`のモジュール既定。

| スイッチ | rep30値 | 根拠 |
|---|---|---|
| CAUSAL_FLOOR | True | run_log switches / assert |
| CAUSAL_FLOOR_VOCAB | "known6" | run_log switches / assert |
| STAGE2_SECOND_OPINION | True | run_log switches / assert |
| enable_s1u | False | rep30_full_01.py `run_instance(..., enable_s1u=False)` |
| FLOOR_VERIFY_MODE | "time_only" | run_log switches |
| STAGE2_NORMAL_TWO_OF_TWO | False | run_log switches / assert |
| STAGE2_DOWNGRADE_VERIFY | False | rep30_full_01.py assert(runner既定 L3098も False)。run_log switchesには記録なし |
| TIER0_G_L_ENABLED | False | rep30_full_01.py assert(runner既定 L3106も False)。run_log switchesには記録なし |
| RECHECK_BEFORE_AFTER_PAIRS | False | run_log switches(N3'はOFF、委任_06 A/B不採用) |
| RECHECK_MERGE_UNRESOLVED | True | run_log switches / assert |
| STAGE4_ALLOWLIST | True | run_log switches / assert |
| LADDER_LOCATION_CARRY | True | run_log switches / assert |
| REWRITE_REVERT_GUARD | True | run_log switches / assert |
| SPAN_FALLBACK_CHAIN | True | run_log switches / assert |
| JUDGE_ONLY_CYCLE_AFTER_CAP | True | run_log switches / assert |
| LAST_RESORT_DELETE | True | run_log switches / assert |
| MATERIALITY_BLOCKING_PIN | True | run_log switches / assert |
| STAGE2_VERDICT_REUSE_NONBLOCKING | True | run_log switches(CLI `--reuse`既定on) |
| STAGE2_SIBLING_LOCATIONS_CYCLE1 | True | run_log switches(CLI `--sibling`既定on) |
| ACTOR_GUARD_MODE | "ag1_strict" | run_log switches / assert |
| HANDOFF_MODE | "violation_span" | run_log switches |
| JA_MODE | "english_only" | run_log switches |
| VS_SENTENCE_RESTORE | True | run_log switches / assert |
| MODEL | "gpt-6-luna" | summary_kpi_01 models.runner_MODEL |

追加(参考、同じ出典): VS_MATCH_EXT=True、VS_EXPLAIN_SPLIT=True、STRUCTURAL_ELEMENT_REWRITE=True、STRUCTURAL_PAIRS_TO_RECHECK=True、MAX_CYCLES=2、HARD_MAX_CYCLES=3、BODY_RUBRIC_DEFAULT=V7b(RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B)。
段階B注意: rep30のStage 1は旧Stage 1(legacy)。段階Bでは`STAGE1_MODE=STAGE1_MODE_COVERAGE_UNION`、`STAGE1_ROUTES=both`を上記に追加する(段階Aと同じ)。
