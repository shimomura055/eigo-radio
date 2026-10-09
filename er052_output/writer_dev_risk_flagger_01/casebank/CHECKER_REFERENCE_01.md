# CHECKER_REFERENCE_01: 既存Production Checker判定のケース別回収(WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_02C、API¥0)

casebank_01(実記事61件)の各ケースについて、既存Production Checker(OPEN-233経路: Stage1[R3/R5候補化]→Stage2[LLM判定]→第2意見→最終判定[floor含む]→Rewrite、および書き手内蔵のEN deviation check)が当時どう判定したかを、**過去成果物からの逐語回収のみ**で並べた参照表。新規API・新規生成・再判定は一切なし。機械可読の正本は `checker_reference_01.json`(同ディレクトリ)。最終報告項目7「Production Checkerを今後残す合理性」の判断材料であり、**残す/外すの結論は書かない**(判断はFable/ユーザー)。

## 0. 読み方・前提(重要な注意)

- 表記: **【確認】**=過去成果物の記録で直接確認できた事実。**【未回収】**=記録が存在しない/回収できなかった(理由を併記)。推測で埋めていない。
- 回収区分(61件): 回収済(Production経路単一run) **40** / 回収済(Trial多run集計のみ) **8** / 部分(Checker未実行または対象外で、EN deviation checkのみ) **4** / 対象外(JA) **9** / 未回収 **0**。回収率(判定が何らかの形で回収できた)= 52EN中 **52/52**(うちOPEN-233 Checker自体の判定を回収できたのは **48/52**)、JA9件はChecker対象外(JA_MODE=english_only)で回収不要。
- **「Production経路単一run」**=当時の1記事×1回のChecker実行結果(prod_e2e_02、allfact_note_e2e_02、control_checker_polysemy、factlock_astra各runのcheckerディレクトリ)。**「Trial多run」**=self_recovery_flow_runner系の繰り返しTrial(コード版・fixtureが混在、Stage1凍結再利用を含む)の延べ集計で、Production単一runとは条件が違う参考値。
- 「検出(BLOCKING)」=その文がcycleのどこかで最終materiality=BLOCKINGになったこと。Stage2はStage1の候補にだけ走るので、**「非候補」=Stage1で候補化されなかった/再分類で除外された文**(Stage2判定なし)。
- **選択バイアスの警告**: casebankの重大・非重大は、Checkerが問題にした文(BLOCKING/指摘)から拾われたものが多い。特に(a)重大のうち「Sonnet判定/Fable確定」はCheckerが一度でも浮上させた文に偏る(Checkerが一度も候補化しなかった重大は拾われにくい)、(b)非重大のRC-K系はTrialで「少なくとも1回BLOCKINGされた型」から再分類した文。よって**RecallはCheckerに有利に、FPRはTrial参考値でCheckerに不利に偏り得る**。ユーザー確認の重大(独立の目)はK01/K02が見逃し(下記3節)。
- ラベルの時点差: prod_e2e_02の旧label_sheetは「true_critical=Y」としたが、casebankは2026-10-03のユーザー決定後の再分類(RC-K05等は軽微)に従う。本書の重大/非重大はcasebankのラベルを使い、再判定していない。
- JSONの出典行は `path:L行`(その文のclaim_textが現れる行)。cycles[c].stage2_resultsにあたる。casebankの本文文は逐語で一致を機械照合した(正規化部分一致)。照合スクリプトはリポジトリに含めない(再現は本書の出典で追える)。

## 1. ケース別のChecker判定(61件)

略号: ACC=ACCEPTABLE, QUA=QUALITY, BLK=BLOCKING, c=cycle, 2nd=第2意見, det=決定論floor。「BLK(any-cycle) a/b run」=Trial多runでその文がBLOCKINGになったrun数/instance延べrun数。devcheck=EN deviation check最終本文判定(COMPLIANT・指摘0 など)。

| case_id | 重大/非重大(根拠) | 言語 | 回収区分 | Stage1 | Stage2(LLM→2nd→最終) | 最終(Production run) | Rewrite/新規NG | Trial参考 | devcheck | 出典(path:行) |
|---|---|---|---|---|---|---|---|---|---|---|
| rf_y84g5r | 重大(ユーザー確認) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 0/29 run | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/meta_run03_advanced.json:L331<br>open233_prod_e2e_02/report_final/critical_trace.md:L12-L24 |
| rf_emcgyx | 重大(ユーザー確認) | EN | P単一run | 候補(r3+r5) | c1:LLM=QUA/2nd=QUA/最終=QUA; c2:LLM=QUA/2nd=QUA/最終=QUA | 非BLOCKING通過 | なし | - | - | open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1/checker/runs/meta_run03_advanced.json:L634<br>open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md:L12 |
| rf_ur5649 | 重大(ユーザー確認) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 18/18 run | - | open233_self_recovery_flow_runner_01*/instances*/safety_A5.json (18 runs) |
| rf_hdr8y4 | 重大(ユーザー確認) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_yjjmk8 | 非重大(ユーザー確認) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | BLK(any-cycle) 0/23 run | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/hormuz_run03_advanced.json |
| rf_upps5x | 非重大(ユーザー確認) | EN | P単一run | Stage2記録あり(cycle3。Stage1 union照合外/再判定) ;再分類=SUPPORTED | c3:LLM=ACC/2nd=BLK/最終=BLK(floor:s1_second_opinion_blocking) | BLOCKING | あり(c3 0_delete) / 新規NG: 文そのものを削除(0_delete, cycle3)。台帳整合の正しい文(7/13の償還投稿)が最終本文から欠落=情報欠… | BLK(any-cycle) 3/38 run | - | open233_prod_e2e_02/runs/neg3_hormuz_prodrunner_b1b.json:L1202<br>open233_prod_e2e_02/report_final/report_abcde.md(C. Rewrite 不要だった=2) |
| rf_7b6trp | 非重大(ユーザー確認) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | - | open233_control_checker_polysemy_trial_01/runs/meta/nb/rep7/checker/runs/meta_run03_advanced.json:L323 |
| rf_grqgvt | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_6j5x2m | 非重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/space_weapons/old/checker/advanced.json:L12 |
| rf_6urnmg | 非重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC; c2:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | - | open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1/checker/runs/meta_run03_advanced.json:L168 |
| rf_sq5c2g | 重大(Sonnet判定) | EN | P単一run | 候補(r3+r5) | c1:LLM=BLK/最終=BLK | BLOCKING | あり(c1 1_word_connective) / 新規NG: Rewrite(語句置換のみ)後も同型の重大NGが最終ENに残存(新規NGではなく未修正残存)。cycle3のACCEP… | - | COMPLIANT・指摘0 | open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2/checker/runs/meta_run03_advanced.json:L478<br>open233_allfact_note_e2e_02/eval/stagewise/stagewise_meta_hormuz.json(meta p2 rep2 meta-p2r2-02) |
| rf_7suvyn | 重大(Sonnet判定) | EN | P単一run | 候補(r3+r5) | c1:LLM=BLK/最終=BLK | BLOCKING | あり(c1 4_paragraph) / 新規NG: なし(②→③で修正済み。当該記事のRewrite新規発生=0) | - | COMPLIANT・指摘0 | open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1/checker/runs/meta_run03_advanced.json:L246<br>open233_allfact_note_e2e_02/eval/stagewise/stagewise_sewer_ai_control.json(ai_control p2 rep1 ai-p2r1-01, s2_to_s3_new=0) |
| rf_qupxd4 | 重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=BLK/最終=BLK | BLOCKING | あり(c1 1_word_connective) / 新規NG: なし(②→③で修正済み。当該記事のRewrite新規発生=0) | - | COMPLIANT・指摘0 | open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1/checker/runs/meta_run03_advanced.json:L871<br>open233_allfact_note_e2e_02/eval/stagewise/stagewise_sewer_ai_control.json(ai-p2r1-02) |
| rf_5qddqw | 重大(Sonnet判定) | EN | P単一run | Stage2記録あり(cycle2。Stage1 union照合外/再判定) | c2:LLM=BLK/最終=BLK | BLOCKING | あり(c2 4_paragraph; c2 None) / 新規NG: 【あり】このケース自体がRewrite(cycle1)が挿入した無関係文(重大)。cycle2のBLOCKINGで検出・… | - | - | open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2/checker/runs/meta_run03_advanced.json:L1932<br>open233_allfact_note_e2e_02/eval/stagewise/STAGEWISE_SUMMARY.md:L49(注) |
| rf_apqtyt | 重大(Sonnet判定) | EN | P単一run | 候補(r3+r5) | c1:LLM=BLK/最終=BLK | BLOCKING | あり(c1 1_word_connective) / 新規NG: なし(②→③で修正済み。当該記事のRewrite新規発生=0)。ただし同記事はRewrite 9 recordsで最多(… | - | COMPLIANT・指摘0 | open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2/checker/runs/meta_run03_advanced.json:L400<br>open233_allfact_note_e2e_02/eval/stagewise/stagewise_space_weapons.json(sw-p2r2-02) |
| rf_665ga9 | 重大(Sonnet判定) | EN | Checker未実行/devcheckのみ | - | - | Production run無 | - | - | COMPLIANT・指摘0 | open233_note_transfer_matrix_01/eval/MATRIX_SUMMARY.md:L151<br>open233_note_transfer_matrix_01/runs/hormuz/nb/T0M0/rep2/b1b/audit/deviation_check.json |
| rf_t9nxuv | 重大(Sonnet判定) | EN | P単一run | 候補(r3+r5) | c1:LLM=BLK/最終=BLK | BLOCKING | あり(c1 1_word_connective) / 新規NG: なし(後続cycle2/3で同factはACCEPTABLE)。ただし同一run後半cycle3で別の正しい文を削除(r… | BLK(any-cycle) 38/38 run [truth_check K16: 15/15] | - | open233_prod_e2e_02/runs/neg3_hormuz_prodrunner_b1b.json:L326<br>open233_missed_detection_truth_check_01/cases_01.csv:L310-L324 |
| rf_nck2y6 | 重大(Sonnet判定) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 31/32 run [truth_check K18: 2/13] | - | open233_missed_detection_truth_check_01/cases_01.csv:L340-L352<br>docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:L413 |
| rf_fmu3aa | 重大(Sonnet判定) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 12/19 run [truth_check K20: 4/5] | - | open233_missed_detection_truth_check_01/cases_01.csv:L366-L370<br>docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:L468 |
| rf_p4mtyd | 重大(Fable確定) | EN | P単一run | 候補(r3) | c1:LLM=BLK/最終=BLK | BLOCKING | あり(c1 1_word_connective) / 新規NG: なし(cycle2以降の同factはACCEPTABLE。so→and) | BLK(any-cycle) 51/64 run | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/bgroup_B3.json:L90<br>open233_prod_e2e_02/report_final/critical_trace.md(bgroup_B3) |
| rf_g7k93w | 重大(Fable確定) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 14/15 run | - | - |
| rf_tcdxe4 | 重大(Fable確定) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 19/19 run | - | - |
| rf_vph9nb | 重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_c3p892 | 非重大(ユーザー確認) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 1/32 run [truth_check K19: 1/13] | - | open233_missed_detection_truth_check_01/cases_01.csv:L353-L365<br>docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:L439 |
| rf_kkh6ng | 非重大(ユーザー確認) | EN | P単一run | 再分類で除外(SUPPORTED) | (Stage2対象外) | 非候補で通過 | なし | BLK(any-cycle) 21/44 run [truth_check K04: 16/23] | - | open233_prod_e2e_02/runs/meta_run03_standard.json<br>open233_missed_detection_truth_check_01/cases_01.csv:L53-L75 |
| rf_hmpyuu | 非重大(ユーザー確認) | EN | P単一run | 候補(r3+r5) | c1:LLM=ACC/2nd=ACC/最終=ACC; c2:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 6/44 run [truth_check K10: 4/23] | - | open233_prod_e2e_02/runs/meta_run03_standard.json:L485<br>open233_missed_detection_truth_check_01/cases_01.csv:L191-L213 |
| rf_hspzde | 非重大(Sonnet判定) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 7/15 run [truth_check K01: 3/5] | - | open233_missed_detection_truth_check_01/cases_01.csv:L2-L6<br>docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:L91 |
| rf_b2nvsf | 非重大(Sonnet判定) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) ;再分類=SUPPORTED | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 6/40 run [truth_check K02: 5/23] | - | open233_prod_e2e_02/runs/hormuz_run03_standard.json:L801<br>open233_missed_detection_truth_check_01/cases_01.csv:L7-L29 |
| rf_562myt | 非重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 4/63 run [truth_check K03: 5/23] | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/hormuz_run03_advanced.json:L559<br>open233_missed_detection_truth_check_01/cases_01.csv:L30-L52 |
| rf_zbe99x | 非重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=BLK/最終=BLK(floor:det:changed_number) | BLOCKING | あり(c1 1_word_connective) / 新規NG: なし(同factの後続cycleでBLOCKING再発なし: report C「Rewrite後に再修正が必要=0」)。… | BLK(any-cycle) 18/44 run [truth_check K05: 12/23] | - | open233_prod_e2e_02/runs/meta_run03_standard.json:L718<br>open233_missed_detection_truth_check_01/cases_01.csv:L76-L98 |
| rf_75v4en | 非重大(Sonnet判定) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | BLK(any-cycle) 1/44 run [truth_check K08: 1/23] | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/meta_run03_standard.json<br>open233_missed_detection_truth_check_01/cases_01.csv:L145-L167 |
| rf_wrv48r | 非重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC; c2:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 1/44 run [truth_check K09: 1/23] | - | open233_prod_e2e_02/runs/meta_run03_standard.json:L170<br>open233_missed_detection_truth_check_01/cases_01.csv:L168-L190 |
| rf_gtwtjt | 非重大(Sonnet判定) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 1/37 run [truth_check K11: 1/22] | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/neg1_meta_b3prod_a2.json:L956<br>open233_missed_detection_truth_check_01/cases_01.csv:L214-L235 |
| rf_da6twd | 非重大(Sonnet判定) | EN | P単一run | 候補(r3+r5) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 1/37 run [truth_check K12: 1/22] | - | open233_prod_e2e_02/runs/neg1_meta_b3prod_a2.json:L407<br>open233_missed_detection_truth_check_01/cases_01.csv:L236-L257 |
| rf_7kyezh | 非重大(Sonnet判定) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) ;再分類=SUPPORTED | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 1/37 run [truth_check K13: 1/22] | COMPLIANT・指摘0 | open233_prod_e2e_02/runs/neg1_meta_b3prod_a2.json:L1112<br>open233_missed_detection_truth_check_01/cases_01.csv:L258-L279 |
| rf_sprwsa | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | open233_missed_detection_truth_check_01/cases_01.csv:L280-L294 |
| rf_pb7rz2 | 非重大(Sonnet判定) | EN | P単一run | Stage2記録あり(cycle3。Stage1 union照合外/再判定) | c3:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 5/38 run [truth_check K15: 5/15] | - | open233_prod_e2e_02/runs/neg3_hormuz_prodrunner_b1b.json:L1378<br>open233_missed_detection_truth_check_01/cases_01.csv:L295-L309 |
| rf_rhubds | 非重大(Sonnet判定) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) ;再分類=SUPPORTED | c1:LLM=ACC/2nd=ACC/最終=ACC; c2:LLM=ACC/2nd=ACC/最終=ACC; c3:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | BLK(any-cycle) 5/38 run [truth_check K17: 5/15] | - | open233_prod_e2e_02/runs/neg3_hormuz_prodrunner_b1b.json:L401<br>open233_missed_detection_truth_check_01/cases_01.csv:L325-L339 |
| rf_y45s87 | 非重大(Sonnet判定) | EN | Trialのみ | - | - | Production run無 | - | BLK(any-cycle) 6/19 run [truth_check K23: 5/5] | - | open233_missed_detection_truth_check_01/cases_01.csv:L381-L385<br>docs/pm/open233_missed_candidates_reclassification_2026-10-03.md:L543 |
| rf_w3ucr6 | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_xkgmt5 | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_wfzehu | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_ptrj37 | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_mytfwc | 非重大(Sonnet判定) | JA | 対象外JA | - | - | 対象外(JA) | - | - | - | - |
| rf_aennw4 | 非重大(Sonnet判定) | EN | devcheckのみ | - | - | devcheck MAJOR→STOP | - | - | - | open243_translation_ng_analysis_01/S0_USER_CHECK.md:L9 |
| rf_xyw4mp | 非重大(Sonnet判定) | EN | devcheckのみ | - | - | devcheck MAJOR→STOP | - | - | - | open243_translation_ng_analysis_01/S0_USER_CHECK.md:L15 |
| rf_8fbz5r | 非重大(Sonnet判定) | EN | devcheckのみ | - | - | devcheck MAJOR→STOP | - | - | - | open243_translation_ng_analysis_01/S0_USER_CHECK.md:L21 |
| rf_e42vt2 | 非重大(弱ラベル) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/hormuz/new/checker/standard.json:L717 |
| rf_qupkjh | 非重大(弱ラベル) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/streaming_price/old/checker/advanced.json:L816 |
| rf_ah9aha | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/semiconductor_earnings/old/checker/standard.json |
| rf_5cryu9 | 非重大(弱ラベル) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) | c1:LLM=QUA/2nd=BLK/最終=BLK(floor:s1_second_opinion_blocking) | BLOCKING | あり(c1 3_sentence) / 新規NG: なし(will cost→cost の時制修正はSonnetラベルで改善と判定: w3-109/w3-117)。同記事の… | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/streaming_price/old/checker/standard.json:L872<br>factlock_astra_e2e_trial_01/eval/labels_merged.jsonl w3-109,w3-112,w3-117 |
| rf_6c53hz | 非重大(弱ラベル) | EN | P単一run | Stage2記録あり(cycle1。Stage1 union照合外/再判定) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/hormuz/new/checker/advanced.json:L474 |
| rf_9x3gdn | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/semiconductor_earnings/old/checker/standard.json |
| rf_ejrk5u | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/central_bank_mortgage/old/checker/standard.json |
| rf_pdmdt5 | 非重大(弱ラベル) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC; c1:LLM=QUA/2nd=ACC/最終=QUA | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/streaming_price/new/checker/standard.json:L90 |
| rf_g4uegk | 非重大(弱ラベル) | EN | P単一run | 候補(r3) | c1:LLM=ACC/2nd=ACC/最終=ACC; c1:LLM=ACC/2nd=QUA/最終=QUA | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/streaming_price/new/checker/advanced.json:L168 |
| rf_vqhe62 | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/central_bank_mortgage/old/checker/standard.json |
| rf_rdwghg | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/space_weapons/old/checker/advanced.json |
| rf_w3dtae | 非重大(弱ラベル) | EN | P単一run | 候補(r3+r5) | c1:LLM=ACC/2nd=ACC/最終=ACC | 非BLOCKING通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/small_bag/old/checker/advanced.json:L12 |
| rf_nykkru | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/byd_recall/old/checker/advanced.json |
| rf_frwds2 | 非重大(弱ラベル) | EN | P単一run | 非候補 | (Stage2対象外) | 非候補で通過 | なし | - | COMPLIANT・指摘0 | factlock_astra_e2e_trial_01/runs/space_weapons/old/checker/standard.json |

### 1-1. 個別メモ(表で書き切れない事実)

- **rf_y84g5r**: 重大見逃し。Stage1は候補化(negation_polarity_mismatch)したが、Stage2 LLM=ACCEPTABLE、第2意見=ACCEPTABLE(confirmed_downgrade)で非BLOCKINGのまま終了(RESOLVED_STAGE2_DOWNGRADE)。Rewriteなし。Trial 29 runでもBLOCKING 0。
- **rf_emcgyx**: 重大見逃し。Stage1で候補化(R3+R5, model)、Stage2はQUALITY(ledger_scope)、第2意見QUALITYで確認、cycle1・cycle2とも非BLOCKING。ユーザー確認で重大NG(評価者は軽微/保留と判定していた)。同記事のRewrite 1件は別文(before_was_ng=true)。
- **rf_ur5649**: Production経路の実記事ではなくTrial fixture(safety_A5。es045 trial_translation由来の同文)。Trial 18 runすべてでBLOCKING。単一Production runの判定は無い。
- **rf_hdr8y4**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。stagewise上、JAのみ残存の重大(EN最終は修正済み)。Checker対象外のためCheckerは見逃しでも捕捉でもない。
- **rf_upps5x**: 不要Rewrite。cycle1はSUPPORTEDで除外(非候補)。cycle3でLLM=ACCEPTABLE・第2意見1回目=ACCEPTABLEなのに最終BLOCKING(floor=s1_second_opinion_blocking)へ引き上げ。
- **rf_grqgvt**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_5qddqw**: casebankの対象文はRewrite由来の挿入文で元記事には無い。「元の重大NG」ではなく「Rewriteが生んだ重大NGをCheckerが自己修復した」例。
- **rf_665ga9**: open233_note_transfer_matrix_01は「Checkerなし」のTrial(MATRIX_SUMMARY.md:L151)。OPEN-233 Checker出力は存在しない=Checker判定は未回収(未実行)。EN deviation check(最終)=LEDGER_COMPLIANT・指摘0で、重大を通した。
- **rf_nck2y6**: Trialのみ(safety_A2A3 fixture)。RC-K18(truth_check)の2/13は日本語版文の数字で、casebankの英語文のBLOCKINGとは別(Trial sweepでは32 run中31でBLOCKING)。
- **rf_fmu3aa**: Trialのみ(safety_A4 fixture)。K20は4/5 runでBLOCKING(truth_check)。Trial sweepではcycle1非候補・cycle2以降に文を含む拡張claimがBLOCKING(19 run中12)。
- **rf_g7k93w**: Trialのみ(bgroup_B4 fixture)。Trial 15 run中14でBLOCKING。
- **rf_tcdxe4**: Trialのみ(safety_A4 fixture)。Trial 19 runすべてBLOCKING。
- **rf_vph9nb**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。参考: JA側のFact Check(writer内蔵)は当該JAをMAJORと判定しSTOP(旧腕R2 attempt2, rejected)=JA Fact Checkは捕捉。
- **rf_c3p892**: Trialのみ(safety_A2A3 fixture)。RC-K19(ユーザー決定2026-10-03で軽微。casebankでは非重大)。BLOCKINGは稀(truth_check 1/13, sweep 1/32)。
- **rf_hspzde**: Trialのみ(bgroup_B4 fixture)。RC-K01(問題なし)。truth_checkで3/5 runがBLOCKING(過剰品質)。
- **rf_zbe99x**: casebank上は非重大(軽微/境界。RC-K05)。旧label_sheetではtrue_critical=Y(Sonnet)だったが、ユーザー決定(2026-10-03)後の再分類で軽微。BLOCKINGはLLM+決定論floor(changed_number)。
- **rf_sprwsa**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_y45s87**: Trialのみ(safety_A4 fixture)。RC-K23(問題なし)。truth_checkで5/5 runがBLOCKING。
- **rf_w3ucr6**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_xkgmt5**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_wfzehu**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_ptrj37**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_mytfwc**: JA文: OPEN-233 Checkerは英語のみ対象(JA_MODE=english_only)で、Checker判定なし(対象外)。
- **rf_aennw4**: OPEN-233 Checkerではなく、書き手内蔵のEN deviation checkがMAJOR(確認1 users)と判定→解消せずSTOP(出荷されず)。非重大なので偽STOP候補(ユーザー確認待ち: 許容/不許容)。OPEN-233 Checker自体の判定は存在しない。
- **rf_xyw4mp**: OPEN-233 Checkerではなく、書き手内蔵のEN deviation checkがMAJOR(確認2 so)と判定→解消せずSTOP(出荷されず)。非重大なので偽STOP候補(ユーザー確認待ち: 許容/不許容)。OPEN-233 Checker自体の判定は存在しない。
- **rf_8fbz5r**: OPEN-233 Checkerではなく、書き手内蔵のEN deviation checkがMAJOR(確認3 Brent→oil prices)と判定→解消せずSTOP(出荷されず)。非重大なので偽STOP候補(ユーザー確認待ち: 許容/不許容)。OPEN-233 Checker自体の判定は存在しない。
- **rf_5cryu9**: casebankでは機械抽出弱ラベルの非重大。Sonnet個別ラベルは軽微(時制)。BLOCKINGはLLM=QUALITY→第2意見BLOCKINGの引き上げ(floor=s1_second_opinion_blocking)。

## 2. 記事単位の表

### 2-1. factlock_astra 18記事(9テーマ×新旧2腕。EN AdvanceはCheckerのadvanced、EN Standardはstandard)

Checker費用=checkerのtotal_cost_jpy(実測)をAdv/Std分合算。Rewrite件数はrewrite_records(同一文の重複recordを含む)。「不要Rewrite」=Rewrite対象文のSonnetラベルが問題なしのもの。重大見逃し(EN)=ラベル上ENの重大は0件。

| 記事 | Checker実行 | Checker費用(¥) | Rewrite件数 | 不要Rewrite(問題なし文) | 軽微文へのRewrite | EN重大見逃し | Rewriteが生んだ新規NG | 備考 |
|---|---|---|---|---|---|---|---|---|
| byd_recall/new | adv:R_REWRITE_THEN_DOWNGRADE | 5.30 | 2 | 2 | 0 | 0 | なし(比喩文の削除。劣化限定的 w2-240) | 比喩文1文を削除(断片artifact含め2 record)。ラベル=問題なし文→不要Rewrite。second opinionの誤BLOCKING起点。 |
| byd_recall/old | adv:R_STAGE2_DOWNGRADE | 2.50 | 0 | 0 | 0 | 0 | - | - |
| central_bank_mortgage/new | 未実行/出力なし | - | 0 | 0 | 0 | 0 | - | Checker未実行。新腕はR0(JA段)でSTOP(HUMAN_CHECK_E2E_01.md:L20) |
| central_bank_mortgage/old | adv:R_STAGE2_DOWNGRADE,sta:R_STAGE2_DOWNGRADE | 3.92 | 0 | 0 | 0 | 0 | - | - |
| hormuz/new | adv:R_STAGE2_DOWNGRADE,sta:R_STAGE2_DOWNGRADE | 5.45 | 0 | 0 | 0 | 0 | - | - |
| hormuz/old | 未実行/出力なし | - | 0 | 0 | 0 | 0 | - | Checker未実行。runsにEN記事(b1b/a2)が無い(JA段で停止した可能性。理由の個別確認は未回収) |
| meta/new | adv:R_STAGE2_DOWNGRADE,sta:R_STAGE2_DOWNGRADE | 4.22 | 0 | 0 | 0 | 0 | - | - |
| meta/old | 未実行/出力なし | - | 0 | 0 | 0 | 0 | - | Checker未実行。runsにEN記事(b1b/a2)が無い(JA段で停止した可能性。理由の個別確認は未回収) / JA重大1(w1-11)はJA Fact Check(MAJOR→STOP)が捕捉。Checker対象外。 |
| openai_copyright/new | 未実行/出力なし | - | 0 | 0 | 0 | 0 | - | Checker出力なし。EN Adv STOP(HUMAN_CHECK_E2E_01.md:L19)。b1b/a2は存在 |
| openai_copyright/old | adv:R_STAGE2_DOWNGRADE,sta:R_REWRITE_THEN_DOWNGRADE | 6.52 | 1 | 0 | 1 | 0 | 未回収(Rewrite後の個別判定ラベル無し) | 見出し的な軽微文(w3-26: 提訴主体の曖昧化)。Rewriteは主体語を置換(Companies…/GPT models)。 |
| semiconductor_earnings/new | 未実行/出力なし | - | 0 | 0 | 0 | 0 | - | Checker出力なし(理由未回収) |
| semiconductor_earnings/old | adv:R_STAGE2_DOWNGRADE,sta:R_REWRITE_THEN_DOWNGRADE | 5.64 | 2 | 2 | 0 | 0 | あり(軽微): 限定句「not the whole semiconductor segment」を削除(w3-73/w3-83) | 小数点で文が分割された断片($29. / $16.)を別claimとして判定→BLOCKING→Rewrite。元の完全文は正しい。 |
| small_bag/new | adv:R_STAGE2_DOWNGRADE,sta:R_STAGE2_DOWNGRADE | 5.45 | 0 | 0 | 0 | 0 | - | - |
| small_bag/old | adv:R_STAGE2_DOWNGRADE | 2.36 | 0 | 0 | 0 | 0 | - | - |
| space_weapons/new | adv:R_REWRITE_THEN_DOWNGRADE | 5.35 | 2 | 0 | 2 | 0 | なし(副作用小。ただしmissiles複数形は残存 w1-58/w1-77) | 軽微文2件(satellites→COSMOS 1408、these were tests→this was a test)。機械floor(changed_number)で実行。 |
| space_weapons/old | adv:R_STAGE2_DOWNGRADE,sta:R_STAGE2_DOWNGRADE | 4.79 | 0 | 0 | 0 | 0 | - | - |
| streaming_price/new | adv:R_STAGE2_DOWNGRADE,sta:R_STAGE2_DOWNGRADE | 5.32 | 0 | 0 | 0 | 0 | - | - |
| streaming_price/old | adv:R_STAGE2_DOWNGRADE,sta:R_REWRITE_THEN_DOWNGRADE | 8.41 | 4 | 1 | 3 | 0 | あり(軽微): $2.50差額文を削除し欠落+二重空白(w3-112/w3-117) | 時制修正2件・年額の限定補完1件は改善。断片artifact($2.)のdeleteは問題なし文の削除=不要Rewrite。 |

合計(【確認】): Checker実行 13/18記事、Checker費用 合計¥65.23(実行記事平均¥5.02/記事)、Rewrite 11 records(不要=問題なし文 5・軽微文 6・重大文 0)、EN重大見逃し 0。Checker出力が無い5記事の理由は表のとおり(一部**【未回収】**)。JA重大1件(meta/old w1-11)はJA Fact Checkが捕捉。

### 2-2. 既知の重大の元記事(8本。項目で挙げた「約6本」より2本多い=重大を含みCheckerが走った記事を全て載せた)

| 記事 | final_state | Checker費用(¥) | Rewrite件数 | 不要Rewrite | 軽微文Rewrite | 重大見逃し(最終に残存した重大でBLOCKING無し) | Rewriteが生んだ新規NG | 重大の扱い | Rewrite内訳 |
|---|---|---|---|---|---|---|---|---|---|
| refresh meta run_03 b1b (prod_e2e_02 meta_run03_advanced) | R_STAGE2_DOWNGRADE | 2.41 | 0 | 0 | 0 | 1 | - | rf_y84g5r(rollback方向反転・ユーザー確認) | Rewriteなし |
| ccp ai_control jb9k (control rep1) | R_REWRITE_THEN_DOWNGRADE | 4.91 | 1 | 0 | 0 | 1 | なし | rf_emcgyx(不在断定・ユーザー確認) QUALITYで通過 | Rewrite 1件(別文。ccp評価でbefore_was_ng=true=必要) |
| allfact meta P2 rep2 | R_REWRITE_THEN_DOWNGRADE | 5.29 | 1 | 0 | 0 | 1 | 未修正残存(新規NGではない) | rf_sq5c2g(主体対象入替) 初回BLOCKING→Rewrite後も残存 | Rewrite 1件=重大NGへ(語句置換のみで未修正) |
| allfact ai_control P2 rep1 | R_REWRITE_THEN_DOWNGRADE | 6.92 | 2 | 0 | 0 | 0 | なし | rf_7suvyn・rf_qupxd4(重大2) BLOCKING→修正済み | Rewrite 2件=重大2件に対応(必要) |
| allfact ai_control P2 rep2 | R_REWRITE_THEN_DOWNGRADE | 8.43 | 5 | 未回収(NG台帳に紐づかないrecord 2件。同一NGへの重複recordの可能性あり) | 1 | 0 | あり: 重大1(loop内で修正)+軽微1(最終ENに残存・Checker未検出) | rf_5qddqw: Rewriteが生んだ重大(無関係文挿入)をcycle2で検出・修正 | Rewrite 5 records。NG台帳のrewritten=True 3項目(ai-p2r2-01軽微, -07重大[Rewrite由来], -08軽微[Rewrite由来・未検出]) |
| allfact space_weapons P2 rep2 | R_REWRITE_THEN_DOWNGRADE | 9.68 | 9 | 未回収(NG台帳に紐づかないrecord 6件。後続cycleのBLOCKING対象で個別ラベル無し) | 1 | 0 | なし(最終ENに新規NGなし) | rf_apqtyt(+JA側rf_hdr8y4): EN重大2件BLOCKING→EN最終は修正済み。JAのみ残存2(Checker対象外) | Rewrite 9 records。NG台帳のrewritten=True 3項目(重大2+軽微1) |
| prod_e2e_02 neg3 hormuz prodrunner b1b | R_REWRITE_THEN_DOWNGRADE | 5.66 | 2 | 1 | 0 | 0 | 削除による情報欠落1(個別NGラベル未回収) | rf_t9nxuv(数量時系列) c1 BLOCKING→修正 | Rewrite 2件: (1)重大対応(必要) (2)cycle3で正しい文を削除(不要, rf_upps5x) |
| prod_e2e_02 bgroup_B3 (hormuz run_02 b1b) | R_REWRITE_THEN_DOWNGRADE | 3.96 | 1 | 0 | 0 | 0 | なし | rf_p4mtyd(因果so) c1 BLOCKING→修正 | Rewrite 1件=必要 |

注: 「重大見逃し」の定義=最終本文に重大NGが残り、その文がBLOCKINGにならなかった(または修正されなかった)もの。meta P2 rep2のrf_sq5c2gは初回BLOCKINGだがRewriteが語句置換のみで重大が残存(検出≠修正)。allfact ai_control P2 rep2とspace_weapons P2 rep2のRewrite内訳のうちNG台帳に紐づかないrecordは、不要Rewriteか同一NGへの重複recordか個別ラベルが無いため**【未回収】**。

### 2-3. 参考: 実行群ごとのChecker費用・Rewrite(各群の延べ)

| 群 | run数 | 1runあたり平均(¥) | 最小〜最大(¥) | 合計(¥) | Rewrite records | Rewriteが発生したrun数 |
|---|---|---|---|---|---|---|
| prod_e2e_02(9 run) | 9 | 3.50 | 1.97〜5.66 | 31.52 | 6 | 4 |
| allfact_note_e2e_02 P2(10 run) | 10 | 5.27 | 2.05〜9.68 | 52.71 | 22 | 7 |
| control_checker_polysemy(18 run) | 18 | 3.38 | 1.96〜6.33 | 60.81 | 10 | 6 |
| factlock(EN Adv/Std checker run) | 22 | 2.96 | 1.67〜5.46 | 65.23 | 11 | 5 |
| 全体 | 59 | 3.56 | 1.67〜9.68 | - | - | - |

- prod_e2e_02(9run)のRewrite判定(旧label_sheet。`er052_output/open233_prod_e2e_02/report_final/report_abcde.md` C節): Rewrite 6件=必要4・不要2(不要=neg2のfloor changed_number誤発火1、neg3 cycle3の正しい文の削除1)。重大見逃し(出口)=0とされたが、これはgold(既知重大)行のみの集計で、meta_run03_advancedの重大(rf_y84g5r)は「真に重大だったのに非重大」としてlabel_sheetに別途あり(report_abcde.md:L39の`Y&AI非重大`=1)。
- control_checker_polysemy(18記事)のCheckerのRewrite評価(`aggregate_ccp.json`): Rewrite評価8件のうち、元がNGだった(必要)2・NGでなかった(不要)4・不明2 → 不要率 strict 50%(不要のみ)〜75%(不明含む)。Rewriteが生んだ新規NG: 軽微1(meta qvqcのタイトル書換えで主体取り違え。ユーザーが「NG」と判定、重大/軽微は確認中)。

## 3. 集計(Recall/FPR。回収できた範囲、分母を明記)

### 3-1. Production経路・単一run(OPEN-233 Checker)

| 指標 | 値 | 分母/分子 | 備考 |
|---|---|---|---|
| Recall(重大)=重大のうちBLOCKINGになった割合 | **77.8%** | 7 / 9 | 見逃し=rf_y84g5r(非BLK: 第2意見がACC確認)、rf_emcgyx(QUALITY) |
| FPR(非重大のBLOCKING率) | **9.7%** | 3 / 31 | BLOCKING=rf_upps5x(問題なし文を削除)、rf_zbe99x(軽微/境界, LLM+det floor)、rf_5cryu9(軽微。時制。Rewriteは改善) |

Recallの根拠別(重大): Fable確定 1/1、Sonnet判定 6/6、ユーザー確認 0/2。**独立の目であるユーザー確認の重大は 0/2(見逃し)**。BLOCKINGした7件のうち1件(rf_5qddqw)はRewriteが挿入した文で、元記事の重大ではない(除くと 6/8=75.0%)。

FPRの根拠別(非重大): Sonnet判定 1/12、ユーザー確認 1/5、機械抽出(弱ラベル) 1/14。分母31件にはTrial/devcheckのみのケース(c3p892・hspzde・y45s87・aennw4等)は含まない。

非重大のうち非BLOCKINGの内訳(分母31): 候補化されたが非BLOCKINGで通過 18、非候補で通過 10、BLOCKING 3。第2意見がdowngradeを確認(confirmed_downgrade=true)した非重大は18件。

### 3-2. Trial多run(参考。条件がProductionと異なる)

| 指標 | run加重の値 | 分子/分母 | ケース数 |
|---|---|---|---|
| Recall(重大) | 78.2% | 183 / 234 run | 8 |
| FPR(非重大のBLOCKING率) | 13.7% | 87 / 637 run | 17 |

- 重大ケース別(BLOCKING run/延べrun): rf_y84g5r 0/29、rf_ur5649 18/18、rf_t9nxuv 38/38、rf_nck2y6 31/32、rf_fmu3aa 12/19、rf_p4mtyd 51/64、rf_g7k93w 14/15、rf_tcdxe4 19/19。**rf_y84g5r(rollback方向反転・ユーザー確認)は29 runで一度もBLOCKINGにならなかった**。
- Trial FPRは、RC-K系の非重大がTrialで繰り返しBLOCKINGされた型(再分類元)を含むため、Production単一run FPRより高く出るのは定義上の偏り。ケース別: rf_yjjmk8 0/23、rf_upps5x 3/38、rf_c3p892 1/32、rf_kkh6ng 21/44、rf_hmpyuu 6/44、rf_hspzde 7/15、rf_b2nvsf 6/40、rf_562myt 4/63、rf_zbe99x 18/44、rf_75v4en 1/44、rf_wrv48r 1/44、rf_gtwtjt 1/37、rf_da6twd 1/37、rf_7kyezh 1/37、rf_pb7rz2 5/38、rf_rhubds 5/38、rf_y45s87 6/19。
- nonsevere分母にはinstance延べrun数を使い、同一instanceに複数ケースがあるため独立ではない(例: neg1の3文、meta_run03_standardの複数K)。

### 3-3. EN deviation check(書き手内蔵。OPEN-233 Checkerとは別)

- 最終採用本文のdeviation_check.json: 重大のうちデータありの 7件はすべて LEDGER_COMPLIANT・指摘0(=通した)。非重大のデータあり 20件も LEDGER_COMPLIANT。【確認】
- 別系統のopen243 S0要約3件(rf_aennw4/xyw4mp/8fbz5r)ではEN deviation checkがMAJORと判定しSTOP(非重大=偽STOP候補、ユーザー確認待ち)。【確認】
- 注意: deviation_check.jsonは最終本文(retry後)の判定。retry前attemptの指摘は**【未回収】**。

### 3-4. Rewriteの有効性(回収できた範囲)

- 重大文へのRewrite: BLOCKINGした重大7ケースすべてでRewriteが発生。最終ENで解消=6、残存=1(rf_sq5c2g。語句置換のみ)。うち1ケース(rf_5qddqw)はRewrite自体が生んだ重大(Checkerが自己修復)。【確認】
- 非重大(軽微/問題なし)文へのRewrite: factlock 11 records中 不要(問題なし文)5 records・軽微文6 records、prod_e2e_02 6中不要2、ccp 8評価中 不要4(strict)。不要RewriteのうちChecker起因の新規軽微NG(情報欠落)が出た例: factlock semiconductor/old std、streaming_price/old std。【確認】
- 小数点で文が分割された断片(`$29.`、`$16.`、`$2.`)が別claimとしてBLOCKINGになり問題なし文が削除・変更された事象が factlock 2記事で確認できる。【確認: w3-72/w3-73/w3-112】

## 4. 最終報告項目7(Production Checkerを今後残す合理性)向けの事実整理(結論は書かない)

- 【確認】捕捉面: Production単一runでRecall(重大)は 77.8%(7/9)。ただしユーザー確認の重大 0/2(rollback方向反転rf_y84g5r、不在断定rf_emcgyx)を通した。いずれもStage1は候補化したが、Stage2/第2意見が非BLOCKINGと確認した(すなわち「候補化は成功、判定段で見逃し」)。
- 【確認】過剰面: FPR 9.7%(3/31)。不要/軽微文へのRewriteが発生し、削除・限定句欠落などの新規軽微NGを作った例がある。Rewriteが重大NGを自ら生み、Checkerが自己修復した例もある(rf_5qddqw)。
- 【確認】費用: Checker実行1回あたり平均¥3.56(全59 run、最小¥1.67〜最大¥9.68)。Rewriteが多い記事ほど高く、最大はspace_weapons P2 rep2(Rewrite 9 records)の¥9.68。
- 【確認】対象範囲: OPEN-233 CheckerはEN専用。JA側の重大(rf_hdr8y4)は対象外で、JA Fact Checkが捕捉する場合(rf_vph9nb)と、JAに残った場合(rf_hdr8y4。最終ENは修正済み)がある。EN deviation checkは重大7件を全て通した。
- 【未回収】Risk Flaggerとの同一ケース比較に必要な「Flaggerの値」は本書の対象外。Checkerの別run間の揺れ(同一記事の再実行)はTrialのみ(重大で29 run中0〜全BLOCKINGまで幅がある)で、Production単一runは各ケース1回のみ。

## 5. 【未回収】一覧

- JA文(9件)のJA側Fact Check個別判定: rf_vph9nb以外は未回収(Checker対象外のため回収せず)
- rf_665ga9: OPEN-233 Checkerは未実行(Trialが「Checkerなし」)。回収不能
- rf_aennw4/rf_xyw4mp/rf_8fbz5r: OPEN-233 Checker判定なし(EN deviation check MAJORのみ。S0要約文は完走記事ではない)
- EN deviation checkのretry前attempt指摘の集計(deviation_checks/attempt*.json)
- Rewriteで新規発生したNGの個別ラベルは、prod_e2e_02のneg3削除文など一部ケースで未回収
- factlockの18記事中Checker出力が無い記事(central_bank/new, hormuz/old, meta/old, openai/new, semiconductor/new 等)の理由の個別確認

## 6. 出典(主なもの)

- er052_output/open233_prod_e2e_02/runs/*.json, report_final/{critical_trace.md,report_abcde.md,label_sheet.csv}
- er052_output/open233_allfact_note_e2e_02/runs/*/nb/p2/rep*/checker/runs/*.json, eval/stagewise/*
- er052_output/open233_control_checker_polysemy_trial_01/runs/**/checker/runs/*.json, eval/{HUMAN_REVIEW_RESULT.md,aggregate_ccp.json}
- er052_output/factlock_astra_e2e_trial_01/runs/*/*/checker/{advanced,standard}.json, eval/{labels_merged.jsonl,HUMAN_CHECK_E2E_01.md}
- er052_output/open233_missed_detection_truth_check_01/cases_01.csv(RC-K系のTrial延べ判定)、docs/pm/open233_missed_candidates_reclassification_2026-10-03.md
- er052_output/open233_self_recovery_flow_runner_01*/instances*/*.json, open233_e2e_acceptance_01/runs/*/*.json(Trial sweep: 664 file)
- er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md, er052_output/open233_note_transfer_matrix_01/eval/MATRIX_SUMMARY.md
