# BUDGET_LOG_01 — 実費記録(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01、2026-10-26 JST)

出典: `er118_output/fz_full_episode_trial_01/raw_usage_log.jsonl`(`er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far`=`er005_cost_logger`の記録から集計。推定値は使わない)。個別Guardrail 5円(Phase 1a)。

| 区分 | call数 | 円(実測) | 備考 |
|---|---|---|---|
| gpt-6-luna 感情情報(4作品×レベル 初回) | 4 | 約0.65 | 入力2,149〜3,207 / 出力1,098〜1,882 token、1 call 12〜26秒 |
| gpt-6-luna 感情情報(猿の手2レベル 再実行) | 2 | 約0.27 | 初回で scene の "the Whites" 12件が複数形の誤DISCARD→許可名に `whites` を追加して再実行(検査規則は無変更。`llm_run1_whites_discard/` に初回を保存) |
| gemini-2.5-pro-preview-tts / ASR | 0 | 0 | 本委任はTTS・ASR禁止 |
| **合計** | **6** | **1.0106**(cost log集計 `{'openai': 1.01}`) | Guardrail 5円に対し残 約3.99円。先読み guard 発火なし |

- 見積(BUDGET_PLAN_01): 感情LLM 4 call × 約0.1円 = 約0.4円 → 実測 初回4 callで約0.65円(Round 2比 1 call 0.0969円に対し 作品×レベルのclip数が15/17と多く 約0.16円/call)。再実行を含め1.01円(cost log基準。`zw.cost_jpy` による単価式では0.92円、差はpricing snapshotの違い)。
- 日次(JST 2026-10-26、`docs/pm/tools/daily_dev_cost_01.py`): 開始時 約79.85円 → 終了時 80.21円(本委任の実費+並行agent分)。1,000円/日以内。
- 時間: 感情LLMは1 call 12〜26秒(4 callを直列で約80秒、再実行2 callで約40秒)。量産では作品×レベル並列で最長1 call分の所要。
- 使用モデル(開発・評価用途の最新モデル原則、PM_GOVERNANCE 25節): Round 1/2と同一の `gpt-6-luna`(返却モデル名も `gpt-6-luna`)。比較条件を揃えるための据置(Round 2と方式同一)。
- 本委任のunit test(67件=Round 1/2 54件+新規13件)は遮断harness下で実行、外部接続の試行0(cost logの行数6のまま)。
- 委任_02の見積(再掲、BUDGET_PLAN_01): 期待25円 / 保守31円 / 天井75円。全て300円以下=Fable自律枠。
