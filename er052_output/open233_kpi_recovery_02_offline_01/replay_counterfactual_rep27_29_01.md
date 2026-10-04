# 反実仮想replay rep27〜29(¥0、決定論部分、委任_11)

- 対象: rep27/28/29の全run 114件(各38 run)。legacy STAGE4=9件(rep27=3/rep28=3/rep29=3)
- **許可リスト外STAGE4(決定論部分で確定した終端が許可リスト外): 0件**
- 決定論で終端が確定: 3件 / LLM call必要: 6件
- 非STAGE4の周回でも新ロジックが介入しうる箇所(記録からの決定論カウント): {"bprime_location_carry": 4, "a2_revert_would_reject": 1}

## legacy STAGE4 9件の新経路

| rep | sample | instance | legacy reason | 新経路 | 終端(決定論部分) | 必要call |
|---|---|---|---|---|---|---|
| 27 | s1 | neg3_hormuz_prodrunner_b1b | unconfirmed_after_reverify | unconfirmed_after_reverify(出口廃止) -> 次cycleのStage 2(funnel)へ合流 | call必要(Stage 2+S1) | stage2+s1 x1(次cycle) |
| 27 | s1 | safety_A4 | ladder_exhausted_without_full_rewrite | exhausted -> T(決定論削除) -> 全文Recheck 1回 | call必要(Recheck 1回→RESOLVED_REWRITE/judge-only cycle/post_T_new_blocking) | full_recheck x1 |
| 27 | s1 | safety_A5 | ladder_exhausted_without_full_rewrite | exhausted -> T(決定論削除) -> 全文Recheck 1回 | call必要(Recheck 1回→RESOLVED_REWRITE/judge-only cycle/post_T_new_blocking) | full_recheck x1 |
| 28 | s1 | safety_er009_changed_scope | ladder_exhausted_without_full_rewrite | exhausted -> T(構造要素/削除不可) -> blocking_structural_after_ladder | STAGE4:blocking_structural_after_ladder | - |
| 28 | s1 | safety_er009_unsupported_new_claim | degenerate_rewrite_output | degenerate_rewrite_output -> blocking_structural_after_ladder | STAGE4:blocking_structural_after_ladder | - |
| 28 | s2 | meta_run03_advanced | ladder_exhausted_without_full_rewrite | exhausted -> T(構造要素/削除不可) -> blocking_structural_after_ladder | STAGE4:blocking_structural_after_ladder | - |
| 29 | s1 | meta_run03_advanced | same_claim_fact_id_reblocked | same_claim_fact_id_reblocked(出口廃止) -> ladderへ(B′で前levelより上位から昇段、枯渇ならT) | call必要(Rewrite L3/L4→Recheck) | rewrite(上位level) x1以上, full_recheck x1 |
| 29 | s1 | safety_A4 | cycle_limit_exhausted_after_recheck | cycle_limit_exhausted_after_recheck(出口廃止) -> 判定だけのcycle(Stage 2+S1、Rewriteなし) | call必要(Stage 2+S1 x1 claim。非BLOCKING→RESOLVED_REWRITE_THEN_DOWNGRADE、BLOCKING→T/位置不明なら blocking_confirmed_unlocatable_after_cap) | stage2+s1 x1(判定だけのcycle) |
| 29 | s2 | meta_run03_advanced | violation_span_unverified | violation_span_unverified(出口廃止) -> D(i)緩和で位置を確定 -> Rewrite | call必要(Rewrite→Recheck) | rewrite x1以上, full_recheck x1 |

## 新ロジックが介入しうる周回(B′/A2/BLOCKING固定、記録からの決定論カウント)

- rep28 s1 safety_er009_changed_scope: [{"cycle": 2, "kind": "B'", "claim": "The taxi study's results have now been directly confirmed in New York City taxis", "prior_levels": ["1_word_connective"]}]
- rep29 s1 meta_run03_advanced: [{"cycle": 2, "kind": "B'", "claim": "users had no way to know whether AI or a person was making the call\na human on t", "prior_levels": ["1_word_connective"]}]
- rep29 s2 meta_run03_advanced: [{"cycle": 2, "kind": "B'", "claim": "And if this was not properly explained, businesses had no way to know whether th", "prior_levels": ["1_word_connective"]}, {"cycle": 2, "kind": "B'", "claim": "And if this was not properly explained, businesses had no way to know whether th", "prior_levels": ["1_word_connective"]}, {"cycle": 2, "kind": "A2", "target": "And if this was not properly explained, businesses had no way to know whether th", "revised": "And if this was not properly explained, users had no way to know whether they we"}]
