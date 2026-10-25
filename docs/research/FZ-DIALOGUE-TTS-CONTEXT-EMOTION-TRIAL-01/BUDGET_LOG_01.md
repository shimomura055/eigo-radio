# BUDGET_LOG_01 — 実費記録(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01、2026-10-25 JST)

出典: `er118_output/fz_dialogue_context_tts_trial_01/raw_usage_log.jsonl`(`compute_cost_jpy_so_far`)。Cap 30円(Trial固有)。

| 区分 | call数 | 円 |
|---|---|---|
| gpt-6-luna(感情情報、Phase 1a 委任_02) | 1 | 約0.10 |
| gemini-2.5-pro-preview-tts | 26(ctx_t1 9 / base_t1 9 / ctx_t2 8、retry計2) | 約9.46(平均0.364/call) |
| gpt-4o-mini-transcribe(ASR) | 26 | 約0.38 |
| Azure STT(secondary) | 1 | 約0.12 |
| **合計** | | **10.07** |

- Cap残: 約19.93円(Phase 1bで使用: 約9.97円)。見積(BUDGET_PLAN_01): 約16〜19.5円 → 実費は見積以下。
- 日次(JST 2026-10-25、`daily_dev_cost_01.py`): 実行前 961.17円 → 実行後 971.14円(1,000円以内)。
- call別のarm内訳: retryは base_t1 part2_c7(2call)・ctx_t1 part3_c6(2call)。
