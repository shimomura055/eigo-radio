# BUDGET_LOG_01 — FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03

| 項目 | 実測 |
|---|---|
| 再組立(gate/assemble/pages/page_verify) | API 0・0円 |
| Voice 1候補 Std 3 take | 8.79円(`daily_dev_cost_01.py`の`run_01/a2/hr_adopt_prep/voice1_candidates`、cost_log_a2.jsonl 15行 = TTS/ASR) |
| Voice 1候補 Adv 3 take | 8.73円(同`run_01/b1b/hr_adopt_prep/voice1_candidates`、cost_log_b1b.jsonl 14行) |
| 本委任合計 | **17.52円**(Guardrail 20円以内。見積6〜10円を超過した理由=Std take1とAdv take2/3が3回試行[標準2+fallback1]してもASR/QAを通らずSTOPPED[各3 TTS]、他にretry・減速後ASR再検証が入ったため。正式経路の通常のretry上限内[PRODUCTION_MAX_TTS_ATTEMPTS=3/take]で暴走ではない) |
| Y案件累計 | 約167 + 17.52 ≒ 184.5円 / Y上限250円(Fable権限) |
| 日次(JST 2026-10-26) | 委任開始時 80.21円 → 終了時 114.34円(他agentの並行作業を含む合計。本委任分は上記17.52円) / 1,000円 |

cost_log行数=API呼出記録(Std 15行、Adv 14行)。再起動なし。外部停止なし。
