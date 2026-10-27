# COST_01 実費(AI-ISLAND-FORM-PRODUCTION-01 委任_01、2026-10-27)

| 項目 | 実測(円) | 出典 |
|---|---|---|
| KP候補(再利用、再生成0) | 0 | run_kp75_ev_01 既存doc |
| Standard Step A''(新規1 call) | 0.4165 | `grammar_prep_out/summary_a2.json` cost.step_a |
| Standard Step B ×4 | 0.2882 (0.0735/0.0681/0.0867/0.0599) | 同 cost.step_b |
| Advanced Step A'' | 0(旧run_ai_01の候補docを再利用。0.3218円は2026-10-26計上済み) | summary_b1b.json |
| Advanced Step B ×3 | 0.1683 (0.0471/0.0627/0.0585) | 同 |
| **合計(今回新規)** | **0.8730円** | raw_usage_log.jsonl(不追跡)と一致 |

- 上限¥15に対し約5.8%。日次1,000円/JSTに対し無視できる額。TTS/ASR/本文生成: 0。
- 量産単価への影響(参考): Step A''を新規に呼ぶ場合のStd 1記事 ¥0.70(候補4件)・Adv ¥0.49(候補3件。Step A''0.32を含む)=Std+Advで約¥1.2。70円/記事セット目標の約1.7%。
- ※本数値は実測(ログ`raw_usage_log.jsonl`、`audit.total_cost_jpy`)で、課金額はAPI請求を正としないrunner内部換算。
