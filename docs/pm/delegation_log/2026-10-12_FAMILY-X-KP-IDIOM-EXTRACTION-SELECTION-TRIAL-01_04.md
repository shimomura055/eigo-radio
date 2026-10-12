# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 委任_04(2026-10-12、Sonnet)
- 範囲: extractor v3(rank順・件数圧文言なし・transparency記録のみ・LEVEL_DESC adv修正) -> 再凍結(FROZEN_PLAN_02) -> M1 Coffee再確認 -> Phase D本体 -> 暫定SSOT。Production無変更。
- 結果: M1 6/6 PASS(v3)。Phase D: D2 shortlist 5/6・最終4/6(V0 2/6)、D4回帰PASS、N1/D5/D6偽陽性0。陰性対照R3 run1でLLM由来`get the first word`が最終入り=FAIL、D3_shortlist run2 FAIL。Status見込み=再設計(REJECTED as-is)。
- 費用: 委任_04 JPY20.81(M1 1.50/抽出 2.09/最終 17.22)、本件累計 36.53 / 50。
- 事故: V1+d(Coffee Adv n=2)を`--stage v1d`で起動した際、自分で付けた`timeout 115`により自プロセスを打切り(外部停止ではない)。job_resultなし・cost未計上。再起動していない(許可回数外)。未計上費用は最大約JPY1.6。
- STOP確認: 各段前に本件STOP/STOP_NOTICE不在を確認。Melos STOP_NOTICEは別案件。Family Z STOP_ALL不在(参考ログ)。
- 「attempts空」: ドライ実行2回で再現せず(原因未特定)。
- SSOT: DECISION_LOG.md末尾に暫定記録、OPEN_ITEMS.md OPEN-325新規。CURRENT_SPEC.md未変更。
- 詳細: `er064_output/kp_idiom_trial_01/phase_d/PHASE_D_REPORT_02.md`。
