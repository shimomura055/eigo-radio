# BUDGET_PLAN_02: 委任_10(V1修復B+通し音声組立)の費用計画

開始前(T-0)。上限40円(本委任)、Y累計600円(既使用約315.7円・残約284.3円)、当日1,400円(開始時の当日額は`daily_dev_cost_01`で再取得)。報告トリガ: 本委任累計32円で見込み再計算、40円超過見込みなら停止前にFableへ。
| 工程 | 見積(円) | 根拠 |
|---|---|---|
| V1 Adv 再生成 最大3テイク(TTS+ASR+Repetition QA) | 〜7.5 | 1テイク約1.5〜2.5円(V1_REPAIR_PLAN_01) |
| V1 Std 再生成 最大3テイク | 〜7.5 | 同上 |
| Local Rewrite recovery(発火時+1テイク)・予備 | 〜5 | AUDIO_QA_03 Adv試行4 |
| その他segment(V1以外)は同一本文のためcache再利用 | 0〜2 | `_generate_or_reuse`(canonical_text一致で再利用) |
| assemble・ページ生成・Playwright | 0 | API 0 |
| 合計(上限見込み) | 〜22(平常想定 約4〜8) | 40円上限内 |
