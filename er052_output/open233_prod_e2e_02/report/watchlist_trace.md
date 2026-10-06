# watchlist_trace(委任_05b、run jsonからの抜粋、¥0、ラベル無し)

対象: watchlist_floor_only_gold.json。safety_A4 actorは9 runに含まれない(未観測)。neg3 time(`neg3_hormuz_prodrunner_b1b`)のみ該当。

## neg3 time gold(旧: changed_timeのfloorのみで重大化)
- claim: "The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned."(HF-009、in_one_line)
- Stage 1: cycle0に候補あり(detected_by=stage1_llm)。reclassify(初回)=ok、n_targets 7、除外4。当該claimは除外されず後段へ。
- Stage 2(cycle0): llm_materiality=BLOCKING / final=BLOCKING / floor_reason=None / basis=ledger_conditions / rewrite_kind=narrow_scope。floor非関与でLLMのみで重大判定(数字のみfloor下でも拾われた)。
- Rewrite: cycle0でrewrite_records発生。cycle1の同fact(HF-009、書き換え後"...the prices themselves quickly returned.")=ACCEPTABLE。
- 出口: exit_check done=True、final_state=RESOLVED_REWRITE_THEN_DOWNGRADE、Human Review無し。

## neg3 追加観測(watch外、記録のみ)
- cycle2: "On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement."(HF-003): llm=ACCEPTABLE→final=BLOCKING、floor_reason=s1_second_opinion_blocking(S1 BLOCKING化)、cap_terminal_last_resort/last_resort_delete=True。旧No.22(changed_actor、旧floor+LLM BLOCKING)と同文。cycle3でjudge_only後に終端(RESOLVED_REWRITE_THEN_DOWNGRADE)。

## 旧「正当6件」のうち本9 runで観測
- meta_run03_standard cycle1: No.9/No.10相当2件=deterministic_floor:changed_number + llm BLOCKING(数字floor維持)。
- neg2_meta_refresh_a2 cycle1: No.21相当1件=deterministic_floor:changed_number、llm=QUALITY(floorのみで重大化)。
- meta_run03_advanced(No.5 actor): 本runはcycle数1、changed_actor floorは非適用(承認構成)。重大化なし。
