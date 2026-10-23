# BUDGET_PLAN_02: 委任_10(V1修復B+通し音声組立)の費用計画

> **[2026-10-24 注記 PM-FAMILY-Y-BUDGET-CONSOLIDATION-01]** 本書内の「Family Y累計上限(600円/650円等)」は作成当時の枠。同日ユーザー決定で撤廃済み(以後は日次1,000円で一元管理、PM_GOVERNANCE 7-9)。本書の委任単位上限(run単位Cap)は歴史的記録として維持。

開始前(T-0)。上限40円(本委任)、Y累計600円(既使用約315.7円・残約284.3円)、当日1,400円(開始時の当日額は`daily_dev_cost_01`で再取得)。報告トリガ: 本委任累計32円で見込み再計算、40円超過見込みなら停止前にFableへ。
| 工程 | 見積(円) | 根拠 |
|---|---|---|
| V1 Adv 再生成 最大3テイク(TTS+ASR+Repetition QA) | 〜7.5 | 1テイク約1.5〜2.5円(V1_REPAIR_PLAN_01) |
| V1 Std 再生成 最大3テイク | 〜7.5 | 同上 |
| Local Rewrite recovery(発火時+1テイク)・予備 | 〜5 | AUDIO_QA_03 Adv試行4 |
| その他segment(V1以外)は同一本文のためcache再利用 | 0〜2 | `_generate_or_reuse`(canonical_text一致で再利用) |
| assemble・ページ生成・Playwright | 0 | API 0 |
| 合計(上限見込み) | 〜22(平常想定 約4〜8) | 40円上限内 |

## 実績追記(委任_10完了時点)
| 段 | 円 | 出典 |
|---|---|---|
| V1 Adv(1テイク)+V1 Std(3テイク)+他segment cache再利用確認+ASR/Azure | 11.66 | `er110_output/family_y_persona_trial_01/audio/it3/raw_usage_log.jsonl` runner集計 43.12->54.78円 (gemini +5.28 / openai_asr +1.09 / azure +4.91 / openai +0.38) |
| assemble(Adv)・ページ・Playwright・blind資料再生成 | 0 | API 0 |
| **本委任合計** | **11.66** | 上限40円内(32円見込み再計算トリガ未到達) |
- Y累計: 約315.7 + 11.66 = 約327.4円(上限600円、残約272.6円)。当日: `daily_dev_cost_01` adopted 912.95円(上限1,400円内、他案件含む)。
- 再起動なし(1回のtts run、PID 28900、rc=0)。
