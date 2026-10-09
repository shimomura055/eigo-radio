# 委任ログ: WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_02C(既存Production Checker判定のケース別回収、¥0)

- 日付: 2026-10-09。実行: Sonnet(実行層)。API呼び出しなし、Production変更なし、新規記事生成・再判定なし。read-only回収+新規2ファイルのみ。並行workerが改修中の `detectors/`・設計書・`casebank_01.json` は編集していない。
- 目的: 最終報告項目7「Production Checkerを今後残す合理性」の判断材料。casebank_01の実記事61件それぞれについて、OPEN-233 Checker(Stage1/Stage2/第2意見/最終判定/Rewrite)とEN deviation checkが当時どう判定したかを過去成果物から回収。
- 成果物: `er052_output/writer_dev_risk_flagger_01/casebank/checker_reference_01.json`(機械可読)、`casebank/CHECKER_REFERENCE_01.md`(表+集計)。
- 回収の方法: 記事path→Checker出力(prod_e2e_02 runs、allfact_note_e2e_02 checker/runs、control_checker_polysemy checker/runs、factlock_astra checker/{advanced,standard}.json)を対応づけ、casebankの文を正規化部分一致でclaim_text・Stage1 union・candidate_filter・en_text_before_rewriteと照合。RC-K系のTrial延べはopen233_missed_detection_truth_check_01/cases_01.csvと、self_recovery_flow_runner系664 fileの機械走査。照合スクリプトは一時領域で実行しリポジトリには含めない。
- 回収区分(61件): Production経路単一run 40 / Trial多runのみ 8 / EN deviation checkのみ 4(Checker未実行1+S0要約3) / JA対象外 9 / 未回収 0。
- 集計(Production単一run): Recall(重大)=7/9(77.8%、ユーザー確認の重大は0/2=見逃し)、FPR(非重大のBLOCKING率)=3/31(9.7%)。Trial run加重: Recall 183/234(78.2%)、FPR 87/637(13.7%)。EN deviation checkは重大7件を全て通した。
- 記事単位: factlock 18記事(Checker実行13、Checker費用合計¥65.23、Rewrite 11 records[不要5・軽微文6]、EN重大見逃し0)、既知重大の元記事8本、実行群別の費用。Checker1実行あたり平均¥3.56(59 run)。
- 注意(MD§0): 選択バイアス(重大のSonnet/Fable判定はCheckerが浮上させた文に偏る、RC-K系非重大はBLOCKING型から再分類)、旧label_sheetとcasebankのラベル時点差、Trialはコード版混在で条件が異なる。
- 【未回収】: JAのJA Fact Check個別判定(rf_vph9nb以外)、rf_665ga9のChecker(未実行)、devcheckのretry前attempt指摘、一部のRewrite新規NG個別ラベル、Checker出力が無いfactlock 5記事の個別理由。
- 次: Fableがrisk flaggerの比較(同一case_id単位)と最終報告項目7の整理に利用する。残す/外すの結論は書いていない。
