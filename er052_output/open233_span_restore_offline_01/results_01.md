# L6 完結文復元 決定論replay結果(委任_65、¥0)

## 集計

- claim_runs: 591
- unique_claim_article: 182
- resolved_unique: 165
- unresolved_unique: 17
- unresolved_runs: 41
- unresolved_unique_non_japanese: 12
- restored_unique: 5
- restored_unique_non_japanese: 5
- resolved_results_changed_by_L6: 0
- resolved_with_mid_number_edge: 1
- rep24_recorded_vs_replay_base_status_mismatch: {'checked': 35, 'mismatch': 0}
- type別(unique): {"g_japanese_claim(旧Checker言語)": 5, "h_precheck_descriptor(非Checker出力、数値差分の説明文)": 2, "e_substituted_word": 2, "c_ellipsis_mid": 2, "d_explanatory_mixed": 5, "b_ellipsis_edge": 1}
- type別(runs): {"c_ellipsis_mid": 2, "d_explanatory_mixed": 5, "h_precheck_descriptor(非Checker出力、数値差分の説明文)": 24, "e_substituted_word": 2, "g_japanese_claim(旧Checker言語)": 7, "b_ellipsis_edge": 1}
- L6判定別(unresolved unique): {"not_applicable": 5, "cand0": 3, "restored": 5, "not_fired": 4}
- L6判定別(日本語claim除く): {"cand0": 3, "restored": 5, "not_fired": 4}
- type別×L6判定: {"b_ellipsis_edge": {"restored": 1}, "c_ellipsis_mid": {"restored": 2}, "d_explanatory_mixed": {"cand0": 1, "not_fired": 4}, "e_substituted_word": {"restored": 2}, "g_japanese_claim(旧Checker言語)": {"not_applicable": 5}, "h_precheck_descriptor(非Checker出力、数値差分の説明文)": {"cand0": 2}}
- 復元文長(chars): [116, 116, 134, 161, 275]
- n-gram一意率(全記事28本): {"2": {"total_ngrams": 6730, "unique_ngrams": 5705, "unique_rate": 0.8477}, "3": {"total_ngrams": 6702, "unique_ngrams": 6402, "unique_rate": 0.9552}, "4": {"total_ngrams": 6674, "unique_ngrams": 6563, "unique_rate": 0.9834}, "5": {"total_ngrams": 6646, "unique_ngrams": 6592, "unique_rate": 0.9919}, "6": {"total_ngrams": 6618, "unique_ngrams": 6588, "unique_rate": 0.9955}}
- 未確定runsの内訳(時代/検出元): {"iter/初期/stage1_llm": 17, "iter/初期/precheck": 24}
- precheck由来claim: 全37 runs中、base確定13 runs
- 説明文混入型(d)のP-strict-closed拒否理由: [{"claim": "“Their job is visual. They add a special feeling. They say, ‘This is today’s mood.’” Also: “Large bags are the luggage crew. They carry what we need. Mini bags ", "P_reason": "explain_split_rejected:fragment_not_in_article", "fragments": ["Their job is visual. They add a special feeling. They say, ‘This is today’s mood.’", "Large bags are the luggage crew. They carry what we need. Mini bags are the stage crew. They catch the eye and set the mood. In 2026, the runway proudly shows this split in their work."], "dropped_remainders": []}, {"claim": "“That was what people thought as they spoke.” The opening also presents the call as one people believed was from an AI.", "P_reason": "explain_split_rejected:remainder_too_long", "fragments": ["That was what people thought as they spoke."], "dropped_remainders": [{"seg": "The opening also presents the call as one people believed was from an AI", "verdict": "remainder_too_long"}]}, {"claim": "“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also state this more broadly as a claim about oil prices generally.", "P_reason": "explain_split_rejected:dangling_position:headline,one_line", "fragments": ["Oil prices moved briefly, then returned to a high level."], "dropped_remainders": [{"seg": "The headline and one-line summary also state this more broadly as a claim about oil prices generally", "verdict": "dangling_position:headline,one_line"}]}, {"claim": "“The human backup plan” and “that backup plan” characterize the human-staff calls as a backup arrangement.", "P_reason": "explain_split_rejected:remainder_too_long", "fragments": ["The human backup plan", "that backup plan"], "dropped_remainders": [{"seg": "and", "verdict": "connective"}, {"seg": "characterize the human-staff calls as a backup arrangement", "verdict": "remainder_too_long"}]}, {"claim": "“Oil prices moved briefly, then returned to a high level”; “oil prices stayed high” (also reflected in the headline).", "P_reason": "explain_split_rejected:dangling_position:headline", "fragments": ["Oil prices moved briefly, then returned to a high level", "oil prices stayed high"], "dropped_remainders": [{"seg": "also reflected in the headline", "verdict": "dangling_position:headline"}]}]
- 文長(fixture 28本、見出し除く): {"n_sentences": 526, "median": 60.0, "p95": 140, "p99": 185, "max": 575, "pair_n": 339, "pair_median": 123, "pair_p95": 218, "pair_max": 289}
- コスト基礎: {"n_instance_runs": 38, "mean_instance_run_cost_jpy": 0.4401, "rewrite_call_cost_jpy": {"e1": {"n": 20, "mean": 0.1219, "max": 0.3528}, "paragraph": {"n": 5, "mean": 0.0797, "max": 0.0849}, "other": {"n": 3, "mean": 0.0748, "max": 0.0825}}}

## 必須確認(rep24の実例)

### A2A3_s2_c2
- claim: `“the trade and investment deals that the Gulf states were working on with the United States”`
- Checker issue: The article adds that the deals were already being worked on; HF-007 verifies the replacement with trade and investment deals but does not establish that status.
- base: unverified / mismatch / None; base範囲: []
- L6: {"status": "restored", "reason": null, "restore_reason": ["anchor_with_substituted_words"], "fired_by": ["anchor_with_substituted_words(unmatched=1)"], "restored": "On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States.", "n_sentences": 1}

### B3_s2_c2
- claim: `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage...`
- Checker issue: The word “so” presents the continuing concerns as a cause of the plan’s withdrawal. The Ledger says Trump cited productive discussions with Middle Eastern leaders, but does not establish that the continuing concerns caused the withdrawal.
- base: unverified / mismatch / None; base範囲: []
- L6: {"status": "restored", "reason": null, "restore_reason": ["anchor_with_substituted_words", "ellipsis_tail"], "fired_by": ["ellipsis_tail", "anchor_with_substituted_words(unmatched=1)"], "restored": "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.", "n_sentences": 1}

### A2A3_s1_c1_6percent
- claim: `6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.`
- Checker issue: The article asserts that the danger around the strait affects gasoline prices and the cost of moving goods through crude oil; the Ledger does not verify these downstream effects.
- base: resolved / None / L0; base範囲: ['6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.']
- L6: {"status": "restored", "reason": null, "restore_reason": ["truncated_head"], "fired_by": ["truncated_head"], "restored": "After the announcement, the rise in Brent crude futures briefly narrowed, but prices soon returned to nearly the high level seen before it; at the time of reporting, they were above $85 a barrel, up about 2.6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.", "n_sentences": 1}

### A2A3_s2_c1_6percent
- claim: `6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.`
- Checker issue: The article asserts that the danger around the strait affects gasoline prices and the cost of moving goods through crude oil; the Ledger does not verify these downstream effects.
- base: resolved / None / L0; base範囲: ['6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.']
- L6: {"status": "restored", "reason": null, "restore_reason": ["truncated_head"], "fired_by": ["truncated_head"], "restored": "After the announcement, the rise in Brent crude futures briefly narrowed, but prices soon returned to nearly the high level seen before it; at the time of reporting, they were above $85 a barrel, up about 2.6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.", "n_sentences": 1}

## 合成テスト

| 名前 | 期待 | 結果 | 一致 | reason/fired_by | 復元文 |
|---|---|---|---|---|---|
| S1 先頭切断(語の途中から) | restored | restored | OK | None ['truncated_head'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S2 末尾切断(語の途中まで) | restored | restored | OK | None ['truncated_tail'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S3 末尾...省略 | restored | restored | OK | None ['ellipsis_tail'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S3b 末尾…省略(Unicode) | restored | restored | OK | None ['ellipsis_tail'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S4 中間...省略 | restored | restored | OK | None ['ellipsis_mid'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S5 短すぎる断片(語の途中で切断+2語) | guard_rejected | guard_rejected | OK | fragment_too_short [] |  |
| S6 同じ断片が2か所に出現(候補複数) | cand_multi | cand_multi | OK | 2_candidate_sentence_groups ['ellipsis_tail'] |  |
| S7 引用符内の発話を含む文 | restored | restored | OK | None ['truncated_tail'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S8 2文またがり(Brent...) | restored | restored | OK | None ['truncated_tail'] | At the time of reporting, Brent was up about 3%, above $85 a barrel. Its final settlement price was about $85, up about 2% from the day before. |
| S9 3文以上またがり | cand0 | cand0 | OK | spans_more_than_2_sentences ['truncated_tail'] |  |
| S10 記事に逐語アンカーなし(言い換え) | cand0 | cand0 | OK | no_verbatim_anchor_in_article [] |  |
| S11 語の置換1語(実例B3型) | restored | restored | OK | None ['ellipsis_tail', 'anchor_with_substituted_words(unmatched=1)'] | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled ba |
| S12 先頭に余分な語1つ(実例A2A3型) | restored | restored | OK | None ['anchor_with_substituted_words(unmatched=1)'] | On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States |
| S13 置換が多すぎる(7語置換) | cand0 | cand0 | OK | unmatched_run_too_long(10>6) [] |  |

## 誤復元ストレステスト(確定済みclaimを壊してL6に通し、正解の文群と比較)

- 対象件数(確定済みclaimの一意(記事,範囲)): 127
- V1_head_midword_cut: {"restored_exact_truth": 98, "skipped(variant_not_applicable)": 29}
- V2_tail_midword_cut: {"restored_exact_truth": 115, "skipped(variant_not_applicable)": 12}
- V3_tail_ellipsis: {"base_resolved(L6_not_invoked)": 127}
- V4_mid_ellipsis: {"restored_exact_truth": 125, "safe_fail:not_fired:explanatory_mixed_left_to_P": 1, "safe_fail:cand_multi:2_candidate_sentence_groups": 1}
- V5_one_word_substituted: {"restored_exact_truth": 123, "safe_fail:cand0:unmatched_run_too_long(9>6)": 2, "safe_fail:cand0:unmatched_run_too_long(31>6)": 1, "safe_fail:not_fired:explanatory_mixed_left_to_P": 1}
- V6_extra_word_prepended: {"restored_exact_truth": 126, "safe_fail:not_fired:explanatory_mixed_left_to_P": 1}
- V7_extra_word_appended: {"restored_exact_truth": 125, "safe_fail:cand0:no_verbatim_anchor_in_article": 1, "safe_fail:not_fired:explanatory_mixed_left_to_P": 1}
- 合計: {"restored_exact_truth": 712, "skipped(variant_not_applicable)": 41, "base_resolved(L6_not_invoked)": 127, "safe_fail:not_fired:explanatory_mixed_left_to_P": 4, "safe_fail:cand_multi:2_candidate_sentence_groups": 1, "safe_fail:cand0:unmatched_run_too_long(9>6)": 2, "safe_fail:cand0:unmatched_run_too_long(31>6)": 1, "safe_fail:cand0:no_verbatim_anchor_in_article": 1}
- 誤復元(正解と無関係の文)詳細: []
- 正解と完全一致しなかった復元(部分集合・上位集合・部分重なり)詳細(先頭20件): []

## 過去unresolved全claim(unique)

### U01 [g_japanese_claim(旧Checker言語)] L6=not_applicable (出現3回)
- base: unverified/explanatory_mixed
- claim: `「市場が見ているのは『言葉』より海の安全」「投資家が気にしているのは、20％の料金案が残るかどうかだけではない」とし、海上の危険がBrent価格の反発を説明するかのように述べている。`
- issue: Ledgerは、撤回発表後にBrentが一時的に上げ幅を縮小し、その後発表前に近い高水準へ戻ったことと、攻撃・封鎖・タンカー安全上の懸念が続いていたことを記録している。一方、市場参加者が政策発言より海上の安全を重視していたことや、それが価格回復の理由だったことまでは確認していない。
- L6: reason=claim_is_japanese fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01/instances/bgroup_B1.json:bgroup_B1:c1, er052_output/open233_self_recovery_flow_runner_01_iter2/instances/bgroup_B1.json:bgroup_B1:c1, er052_output/open233_self_recovery_flow_runner_01_iter3/instances/bgroup_B1.json:bgroup_B1:c1

### U02 [h_precheck_descriptor(非Checker出力、数値差分の説明文)] L6=cand0 (出現12回)
- base: unverified/mismatch
- claim: `percent values found in article not matching any ledger fact: [2.0, 3.0]`
- issue: precheck detected number_mismatch vs ledger_value=約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない)
- L6: reason=no_verbatim_anchor_in_article fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01/instances/bgroup_B3.json:bgroup_B3:c1, er052_output/open233_self_recovery_flow_runner_01/instances/bgroup_B3.json:bgroup_B3:c1, er052_output/open233_self_recovery_flow_runner_01_iter2/instances/bgroup_B3.json:bgroup_B3:c1, er052_output/open233_self_recovery_flow_runner_01_iter2/instances/bgroup_B3.json:bgroup_B3:c1 ...

### U03 [h_precheck_descriptor(非Checker出力、数値差分の説明文)] L6=cand0 (出現12回)
- base: unverified/mismatch
- claim: `count values found in article not matching any ledger fact: [30000000.0]`
- issue: precheck detected number_mismatch vs ledger_value=1,300万件超
- L6: reason=no_verbatim_anchor_in_article fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01/instances/safety_er009_changed_number.json:safety_er009_changed_number:c1, er052_output/open233_self_recovery_flow_runner_01_iter2/instances/safety_er009_changed_number.json:safety_er009_changed_number:c1, er052_output/open233_self_recovery_flow_runner_01_iter3/instances/safety_er009_changed_number.json:safety_er009_changed_number:c1, er052_output/open233_self_recovery_flow_runner_01_iter4/instances/safety_er009_changed_number.json:safety_er009_changed_number:c1 ...

### U04 [e_substituted_word] L6=restored (出現1回)
- base: unverified/mismatch
- claim: `Users could not know who was really doing the work they’d asked AI to do.`
- issue: None
- L6: reason=None fired_by=['anchor_with_substituted_words(unmatched=5)'] restore_reason=['anchor_with_substituted_words']
- 復元文(1文): `But users could not know who was really doing the work they had asked AI to do—and their personal information might reach that person.`
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter2/instances/neg7_meta_prodrunner_b1b.json:neg7_meta_prodrunner_b1b:c1

### U05 [c_ellipsis_mid] L6=restored (出現1回)
- base: unverified/mismatch
- claim: `At the same time, attacks by the United States and Iran ... continued.`
- issue: None
- L6: reason=None fired_by=['ellipsis_mid'] restore_reason=['ellipsis_mid']
- 復元文(1文): `At the same time, attacks by the United States and Iran, a sea blockade, and concerns about tanker safety continued.`
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter3/instances/hormuz_run03_advanced.json:hormuz_run03_advanced:c1

### U06 [d_explanatory_mixed] L6=cand0 (出現1回)
- base: unverified/explanatory_mixed
- claim: `“Their job is visual. They add a special feeling. They say, ‘This is today’s mood.’” Also: “Large bags are the luggage crew. They carry what we need. Mini bags are the stage crew. They catch the eye and set the mood. In 2026, the runway proudly shows this split in their work.”`
- issue: None
- L6: reason=spans_more_than_2_sentences fired_by=['anchor_with_substituted_words(unmatched=5)'] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter3/instances/neg4_smallbag_div_a2.json:neg4_smallbag_div_a2:c1

### U07 [c_ellipsis_mid] L6=restored (出現1回)
- base: unverified/mismatch
- claim: `“attacks by the United States and Iran ... continued”`
- issue: None
- L6: reason=None fired_by=['ellipsis_mid'] restore_reason=['ellipsis_mid']
- 復元文(1文): `At the same time, attacks by the United States and Iran, a sea blockade, and concerns about tanker safety continued.`
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s2/hormuz_run03_advanced.json:hormuz_run03_advanced:c1

### U08 [d_explanatory_mixed] L6=not_fired (出現1回)
- base: unverified/explanatory_mixed
- claim: `“That was what people thought as they spoke.” The opening also presents the call as one people believed was from an AI.`
- issue: The article states that the call recipients believed they were speaking with an AI. The Ledger confirms a test without appropriate disclosure, but does not establish what recipients believed.
- L6: reason=explanatory_mixed_left_to_P fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s2/safety_A4.json:safety_A4:c2

### U09 [g_japanese_claim(旧Checker言語)] L6=not_applicable (出現1回)
- base: unverified/mismatch
- claim: `AIが苦手な場面で人間が助ける。仕組みだけ見れば、かなり現実的な作戦です。AIに全部任せるより、人間を控えに置くほうが安心。`
- issue: Ledgerは一部の電話を人間の契約スタッフが担当したことを確認していますが、それがAIの苦手な場面での支援や、人間を控えに置く運用だったこと、またそのほうが安心であることは確認していません。
- L6: reason=claim_is_japanese fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter7/instances/safety_A4.json:safety_A4:c3

### U10 [g_japanese_claim(旧Checker言語)] L6=not_applicable (出現1回)
- base: unverified/mismatch
- claim: `アメリカが海峡の安全を守るために使う費用を、貨物を運ぶ側に返してもらうという考えです。`
- issue: 記事は、償還料の支払義務者として「貨物を運ぶ側」を特定していますが、Ledgerでは支払義務者は示されていません。
- L6: reason=claim_is_japanese fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s1/safety_A2A3.json:safety_A2A3:c2

### U11 [d_explanatory_mixed] L6=not_fired (出現1回)
- base: unverified/explanatory_mixed
- claim: `“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also state this more broadly as a claim about oil prices generally.`
- issue: The Ledger verifies the post-withdrawal price movement for Brent futures, not for oil prices generally. The broader wording in the body, headline, and summary extends that observation beyond the verified scope.
- L6: reason=explanatory_mixed_left_to_P fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s2/hormuz_run03_standard.json:hormuz_run03_standard:c2

### U12 [g_japanese_claim(旧Checker言語)] L6=not_applicable (出現1回)
- base: unverified/mismatch
- claim: `アメリカが海峡の安全を守るために使う費用を、貨物を運ぶ側に返してもらうという考えです。`
- issue: 記事は貨物を運ぶ側を支払義務者として特定していますが、Ledgerでは7月13日の案に支払義務者は示されていません。
- L6: reason=claim_is_japanese fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s2/safety_A2A3.json:safety_A2A3:c2

### U13 [g_japanese_claim(旧Checker言語)] L6=not_applicable (出現1回)
- base: unverified/mismatch
- claim: `トランプ氏は、アメリカがホルムズ海峡の安全確保に使う費用について、海峡を通るすべての貨物に二割の償還を求めると投稿した。`
- issue: この表現は、すべての貨物を支払義務者として特定しているように読めるが、Ledgerでは支払義務者は特定されていない。
- L6: reason=claim_is_japanese fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_rep16/instances_s1/neg3_hormuz_prodrunner_b1b.json:neg3_hormuz_prodrunner_b1b:c2

### U14 [d_explanatory_mixed] L6=not_fired (出現1回)
- base: unverified/explanatory_mixed
- claim: `“The human backup plan” and “that backup plan” characterize the human-staff calls as a backup arrangement.`
- issue: The Ledger confirms that trained contractors handled some calls, but does not establish that they were positioned as a backup or fallback. The Japanese source already uses this framing.
- L6: reason=explanatory_mixed_left_to_P fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_rep23/instances_s1/safety_A4.json:safety_A4:c3

### U15 [b_ellipsis_edge] L6=restored (出現1回)
- base: unverified/mismatch
- claim: `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage...`
- issue: The word “so” presents the continuing concerns as a cause of the plan’s withdrawal. The Ledger says Trump cited productive discussions with Middle Eastern leaders, but does not establish that the continuing concerns caused the withdrawal.
- L6: reason=None fired_by=['ellipsis_tail', 'anchor_with_substituted_words(unmatched=1)'] restore_reason=['anchor_with_substituted_words', 'ellipsis_tail']
- 復元文(1文): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.`
- 出現: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s2/bgroup_B3.json:bgroup_B3:c2

### U16 [e_substituted_word] L6=restored (出現1回)
- base: unverified/mismatch
- claim: `“the trade and investment deals that the Gulf states were working on with the United States”`
- issue: The article adds that the deals were already being worked on; HF-007 verifies the replacement with trade and investment deals but does not establish that status.
- L6: reason=None fired_by=['anchor_with_substituted_words(unmatched=1)'] restore_reason=['anchor_with_substituted_words']
- 復元文(1文): `On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States.`
- 出現: er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s2/safety_A2A3.json:safety_A2A3:c2

### U17 [d_explanatory_mixed] L6=not_fired (出現1回)
- base: unverified/explanatory_mixed
- claim: `“Oil prices moved briefly, then returned to a high level”; “oil prices stayed high” (also reflected in the headline).`
- issue: The article generalizes the observed Brent-futures movement to oil prices broadly. The Ledger confirms this movement for Brent futures, not the whole oil market.
- L6: reason=explanatory_mixed_left_to_P fired_by=[] restore_reason=None
- 出現: er052_output/open233_self_recovery_flow_runner_01_rep9/instances_s1/hormuz_run03_standard.json:hormuz_run03_standard:c2


## 確定済みだが範囲の端が数値の途中(小数点・桁区切り)のclaim

- claim: `6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge ha` / 範囲先頭: 6 percent, because attacks between the United States and Iran continued, fears o / 出現7回 ['er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/safety_A2A3.json:safety_A2A3:c1', 'er052_output/open233_self_recovery_flow_runner_01_rep18/instances_s1/safety_A2A3.json:safety_A2A3:c1']
  - 境界修正後のL6: {"status": "restored", "reason": null, "restore_reason": ["truncated_head"], "restored": "After the announcement, the rise in Brent crude futures briefly narrowed, but prices soon returned to nearly the high level seen before it; at the time of reporting, they were above $85 a barrel, up about 2.6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had l
