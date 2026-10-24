# Family Y Trial (FAMILY-Y-VOICES-DESIGN-01) が共有Local Rewrite recovery機構の既定出力先(er011_output/local_rewrite_recovery/<run>/<level>/)へ書いた成果物の退避先
- 退避元: er011_output/local_rewrite_recovery/it2/b1b/ , it3/a2/ , it3/b1b/ (中身はschool_phone_ban/Family Yの本文segment)
- 理由: er020_tts_retry_local_rewrite_fullseg_test_01.RegressionCorpusTest.test_recorded_candidates はer011記録(Family X/Z系corpus)を全件globする。Y TrialのrewriteがX/Z現行ruleで全文判定FALSEとなり恒常失敗していた。
- 退避日: 2026-10-24 (FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_27 D-4)。削除なし(中身は無加工)。
- 注意: 過去docs(FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/AUDIO_QA_03.md等)内の旧path表記 er011_output/local_rewrite_recovery/it2|it3/... は歴史的記述で、現在は本dir配下。
- 再発: Y Trialを再実行すると共有機構が再び er011_output/ に書く。次回Y委任で出力先をer110_output側にする対応(Y側の別管理)が必要。
