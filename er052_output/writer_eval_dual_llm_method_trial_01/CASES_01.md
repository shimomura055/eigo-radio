# CASES_01: 評価方式Trial用ケース一覧(人間/Checker情報つき、評価LLMには渡さない)

凡例: 【確認】=一次資料で逐語確認 / 【推測】=資料から推した解釈 / 人間既知判定の区分: ユーザー確認済み > Fable確定 > Sonnet暫定 > 未裁定。
評価LLMへ渡すのは `eval_items_01.json`(case_id・Fact・対象文・前後文のみ)。本ファイルと `cases_01.json` は評価LLMへ渡さない。
case_idは固定seed 20261009、提示順は固定seed 20261010 でシャッフル(`build_cases_01.py`、API呼び出しなし)。

## 一覧(K番号順)

| K | case_id | 枠 | 言語 | 人間既知の区分 | 事前期待 |
|---|---|---|---|---|---|
| K01 | y84g5r | 重大(人間確認済み寄り) | EN | Fable確定+ユーザー呼称 | C |
| K02 | ur5649 | 重大(人間確認済み) | EN | ユーザー確認済み | C |
| K03 | hdr8y4 | 重大(Fable確定gold) | EN | Fable確定 | C |
| K04 | yjjmk8 | 境界(JA、Rollback語義) | JA | Sonnet暫定(未ラベル) | B? |
| K05 | upps5x | 境界(Rollback語義、ラベル揺れ) | EN | Sonnet暫定(ラベル揺れあり) | B? |
| K06 | 7b6trp | 境界(不在・非公開の断定) | EN | Sonnet暫定(ユーザー未裁定) | B? |
| K07 | 6j5x2m | 境界(因果語 so) | EN | 未裁定 | B? |
| K08 | 6urnmg | 明らかに問題なし(日付・数値あり) | EN | Sonnet暫定(明白、本委任で逐語照合) | A |
| K09 | sq5c2g | 明らかに問題なし(日付・数値あり) | EN | Sonnet暫定(明白) | A |
| K10 | 7suvyn | 明らかに問題なし(ai_control) | EN | Sonnet暫定(明白、本委任で逐語照合) | A |

期待欄: C=重大 / A=問題なし / B?=境界(期待を固定しない)。K03はユーザー個別確認ではなくFable確定goldのため、PREREGISTRATION_01では必須判定から外し参考扱い。

## K01 (case_id=y84g5r) 重大(人間確認済み寄り)

- Fact(MUSE-HC-012): MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  - 出典: er019_output/meta/run_03/ledger/verified_fact_ledger.txt L74
- Writer文(EN): The company also restored the human concierge feature to the way it had been before, at least for now.
  - 出典: er052_output/open233_prod_e2e_02 meta_run03_advanced EN(claim逐語は labels/labels_merged.json 他)。前後文は同文を含む er019_output/meta/run_03/b1b/article.md L17-L19 から採取【推測: prod_e2e_02の記事本体は未保存のため同一記事とみなす】
- 前文: A Meta executive admitted that starting the test without properly explaining it was a mistake.
- 後文: The real challenge for AI phone calls is not just how they talk.
- 人間既知判定[Fable確定+ユーザー呼称]: 重大(方向反転: ロールバックを復元と記述)
  - 出典: er052_output/open233_prod_e2e_02/labels/labels_w2_notes.md L24-L26; report_final/critical_trace.md L12-L14; DECISION_LOG.md L20019(Fable確定)・L20053(ユーザーが『今回発見した重大見逃し』と呼称)。ユーザー個別ラベルの記録は未発見(docs/pm/rollback_misread_history_01.md §5)
- Checker参考判定(正解扱いしない): 見逃し: 機械候補(negation_polarity_mismatch)→Stage1/Stage2=ACCEPTABLE→S1第2意見=ACCEPTABLE→最終 RESOLVED_STAGE2_DOWNGRADE
  - 出典: critical_trace.md L12-L14 / rollback_misread_history_01.md §2 #4

## K02 (case_id=ur5649) 重大(人間確認済み)

- Fact(EVID-008): Anthropic reported that a review of 141,006 evaluation runs identified three incidents in which Claude models reached the internet from third-party evaluation environments and gained unauthorized access to real systems belonging to three organizations. The environments were misconfigured, standard cyber safeguards were absent, and the models were operating on capture-the-flag tasks. Anthropic stated that the models did not exfiltrate themselves or deliberately attempt to escape their test environments.
  - 出典: er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_PACK.md L154-L162
- Writer文(EN): Nor has anyone reported that an AI got out of the test environment.
  - 出典: er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L15
- 前文: The unusual activity in AISI's incident was brought under control about an hour after it was found. In another internal test, the latest test model stopped once it learned that the target was real.
- 後文: (なし)
- 人間既知判定[ユーザー確認済み]: 重大(台帳EVID-008の外部到達・不正アクセスと矛盾し、外へ出ていないと誤解させる)
  - 出典: er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md L12; DECISION_LOG.md L20214付近(2026-10-07 ユーザー人間判定)
- Checker参考判定(正解扱いしない): 見逃し: Stage1 dev=MAJOR(scope拡大・unsupported_new_claim)→Stage2 materiality=QUALITY(basis=ledger_scope)→第2意見QUALITY→最終 RESOLVED_REWRITE_THEN_DOWNGRADE(PASS系)
  - 出典: er052_output/open233_control_checker_polysemy_trial_01/eval/RCA_jb9k_qvqc.md RCA-①

## K03 (case_id=hdr8y4) 重大(Fable確定gold)

- Fact(MUSE-HC-012): MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  - 出典: 同上(HC-012)
- Writer文(EN): They also temporarily put back the feature in which humans handled the calls.
  - 出典: er045_output/family_x_no_heading_segmentation_trial_01/meta/trial_translation.json(同文を含む段落)
- 前文: Meta executives admitted that starting the test without a proper explanation was a mistake.
- 後文: They did not stop Muse itself.
- 人間既知判定[Fable確定]: 重大(再有効化と読める意味反転。Safety-critical gold A5-0)
  - 出典: DECISION_LOG.md L17940-L17943(A5-0=時期・経過の創作[重大])、docs/pm/investigation_ledger_deviation_check_01_part_b.md A-5(MAJOR)。ユーザー個別確認の一次記録は本委任では未発見
- Checker参考判定(正解扱いしない): Checkerではなく旧Deviation Check: v1でMAJOR検出→must-fix retry 1回→LEDGER_COMPLIANT(当時は検出できた事例)
  - 出典: docs/pm/investigation_ledger_deviation_check_01_part_b.md A-5

## K04 (case_id=yjjmk8) 境界(JA、Rollback語義)

- Fact(MUSE-HC-012): MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  - 出典: 同上(HC-012)
- Writer文(JA): Metaの幹部は、適切な開示なしにこのテストを始めたのはミスだったと認め、人間コンシェルジュ機能を当面、以前の状態に戻しました。
  - 出典: er019_output/meta/run_03/ja_writer/original.md L13(前後文も同ファイル)
- 前文: ただし、これは一件の報告です。契約スタッフ全体の話に広げることはできません。
- 後文: 電話の便利さを急いで見せるより、誰が話しているのかを先に伝える。
- 人間既知判定[Sonnet暫定(未ラベル)]: 未確定: Sonnetは『誤読はJA R0で既に発生』と記述(ユーザー未確認)。同型の『元に戻した』系はRB/CCP評価で『曖昧』(ユーザーはCCPの10件に異議なし)、Opusは『元に戻したを禁じると正しい読みまで禁じる』と指摘
  - 出典: docs/pm/ledger_clarity_p_trial/00c_before_evidence.md L10; docs/pm/opus_l2_review_pn_design_01.md L47; er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md L16
- Checker参考判定(正解扱いしない): なし(JA R0はChecker未適用)
  - 出典: docs/pm/rollback_misread_history_01.md §2 #2

## K05 (case_id=upps5x) 境界(Rollback語義、ラベル揺れ)

- Fact(MUSE-HC-012): MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  - 出典: 同上(HC-012)
- Writer文(EN): The company also changed the human concierge feature back to how it was before, at least for now.
  - 出典: claim逐語: er052_output/open233_prod_e2e_02/labels/labels_merged.json idx96。前後文は同文を含む er019_output/meta/run_03/a2/article.md L17-L19 から採取【推測: neg2記事本体は一部のみ保存】
- 前文: A Meta executive admitted that starting the test without explaining it clearly was a mistake.
- 後文: The real challenge for AI phone calls is not only how they speak.
- 人間既知判定[Sonnet暫定(ラベル揺れあり)]: Sonnet W3=問題なし(N)。一方、方向Trialのgold設定G-06は『曖昧』。Fable/ユーザーの最終ラベルなし
  - 出典: labels_merged.json idx96(confirmed_by空); er052_output/open233_directional_misread_trial_01/testset_01.json G-06
- Checker参考判定(正解扱いしない): 未確認(当該runのCheckerでの候補化有無は今回未読)
  - 出典: -

## K06 (case_id=7b6trp) 境界(不在・非公開の断定)

- Fact(F-001): 2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。
  - 出典: er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/shared/ledger.txt L1
- Writer文(EN): But the name of the device and exactly what it can do in an attack have not been made public.
  - 出典: er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/b1b/article.md L5
- 前文: An official U.S. government article describes this statement as the first public acknowledgment that the Space Force had put weapons in space.
- 後文: So we know the weapon's address, but its details are still unclear.
- 人間既知判定[Sonnet暫定(ユーザー未裁定)]: Sonnet W1=軽微(確信0.5、基準(6)字義なら重大寄り)。ユーザー回答待ち(HUMAN_CHECK_E2E_01 S-2)
  - 出典: er052_output/factlock_astra_e2e_trial_01/eval/labels_merged.jsonl w1-73; eval/HUMAN_CHECK_E2E_01.md S-1/S-2
- Checker参考判定(正解扱いしない): 最終EN本文に残存(residual_miss。Checkerは修正せず)
  - 出典: labels_merged.jsonl w1-73(kind=residual_miss)

## K07 (case_id=6j5x2m) 境界(因果語 so)

- Fact(MUSE-HC-012): MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  - 出典: 同上(HC-012)
- Writer文(EN): Meta's AI calling test used human contractors without proper disclosure, so the company rolled back that feature.
  - 出典: er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md 確認2(要約の1文、前後文なし)
- 前文: (なし)
- 後文: (なし)
- 人間既知判定[未裁定]: ユーザー回答待ち(S0_USER_CHECK 確認2: 許容/不許容)
  - 出典: er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md
- Checker参考判定(正解扱いしない): Checkerではなく翻訳Deviation Check: MAJOR(changed_causality)が解消せずSTOP
  - 出典: er052_output/open243_translation_ng_analysis_01/S0_AUDIT_01.md G09 / S0_USER_CHECK.md

## K08 (case_id=6urnmg) 明らかに問題なし(日付・数値あり)

- Fact(HF-007): トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％の米国償還料を、湾岸諸国による対米貿易・投資案件に置き換えると投稿した。
  - 出典: er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt L44
- Writer文(EN): Trump announced that he would drop the 20 percent fee plan and replace it with trade and investment deals between Gulf countries and the United States.
  - 出典: er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/article.md L9
- 前文: Then, the next day, the story suddenly changed.
- 後文: (なし)
- 人間既知判定[Sonnet暫定(明白、本委任で逐語照合)]: 問題なし(類似文F-12は新9 runでSonnetが問題なしとラベル。この文自体のFable/ユーザー確認なし)
  - 出典: er052_output/open233_directional_misread_trial_01/testset_01.json F-12(類似); 本委任で台帳と照合
- Checker参考判定(正解扱いしない): 当該文は候補化されず(local_contextとして登場のみ)
  - 出典: er052_output/open233_prod_e2e_02/runs/hormuz_run03_advanced.json stage2_results

## K09 (case_id=sq5c2g) 明らかに問題なし(日付・数値あり)

- Fact(HF-002): ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。
  - 出典: er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt L8
- Writer文(EN): On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement.
  - 出典: er052_output/open233_directional_misread_trial_01/testset_01.json F-15(前後文なし、記事本体未保存)
- 前文: (なし)
- 後文: (なし)
- 人間既知判定[Sonnet暫定(明白)]: 問題なし(新9 runでSonnetが問題なしとラベル、台帳とほぼ逐語一致)
  - 出典: testset_01.json F-15 origin=新9 runラベル問題なし
- Checker参考判定(正解扱いしない): 未確認(参考なし)
  - 出典: -

## K10 (case_id=7suvyn) 明らかに問題なし(ai_control)

- Fact(EVID-008): Anthropic reported that a review of 141,006 evaluation runs identified three incidents in which Claude models reached the internet from third-party evaluation environments and gained unauthorized access to real systems belonging to three organizations. The environments were misconfigured, standard cyber safeguards were absent, and the models were operating on capture-the-flag tasks. Anthropic stated that the models did not exfiltrate themselves or deliberately attempt to escape their test environments.
  - 出典: 同上(EVID-008)
- Writer文(EN): But because of a setup mistake, it was able to connect to the outside internet.
  - 出典: er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L5
- 前文: The AI was trying a task like a made-up game of capturing flags.
- 後文: (なし)
- 人間既知判定[Sonnet暫定(明白、本委任で逐語照合)]: 問題なし(台帳: misconfigured・インターネットへ到達。ユーザー判定の対象は別文)
  - 出典: HUMAN_REVIEW_RESULT.md(重大1文は別。この文の人間確認なし)
- Checker参考判定(正解扱いしない): Stage1で候補化(causal_not_in_fact, negation_polarity_mismatch)→Stage2 ACCEPTABLE
  - 出典: er052_output/open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1/checker/runs/meta_run03_advanced.json cycles[0].stage2_results[2]
