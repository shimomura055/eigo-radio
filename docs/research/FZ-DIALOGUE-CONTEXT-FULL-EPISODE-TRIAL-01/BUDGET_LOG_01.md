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

## 委任_02 Phase 1b(scope=Phase 1b、Guardrail 100円。出典: 同 raw_usage_log.jsonl、unitごとの `gen_summary.json`)

| unit(起動 JST) | 結果 | 実費(円) | wall | provider内訳(累計cost log) |
|---|---|---|---|---|
| 猿の手 Standard(09:38:40) | 15/15 OK・初回1 call・全採用 | 7.007 | 138.7秒 | gemini TTS 6.76 / openai_asr 0.25(累計に感情LLM 1.01を含む) |
| 猿の手 Advanced(09:43:29、起動間隔≥150秒) | 17/17 OK・各clip 1生成(外側ループ1周)・全採用 | 7.389 | 149.6秒 | gemini累計 13.53 / openai_asr 0.73 / azure 0.14 |
| メロス Standard | **未生成**(起動待機中に停止。API 0) | 0 | - | - |
| メロス Advanced | **未生成** | 0 | - | - |
| **Phase 1b累計** | 32 clip、再生成0 | **14.396 / 100** | - | 期待25円(53 clip)に対し32 clip時点で約57%(clip比 60%) |

- 停止理由: 猿の手 Advanced の組立で **M-5(3)`headroom.scalar` 不一致**(Trial 0.99656194 / Production 1.0)。Fable決定どおり STOP し報告(メロス Standard の生成プロセスは待機中=有料call 0の段階で自プロセスのPIDのみ終了)。詳細は RESULT_PACKET_FZFE2。
- 日次(JST、`daily_dev_cost_01.py`): 委任開始前 約92.74円 → 停止時 112.13円(本委任14.4円+並行agent分)。1,000円/日以内。
- Guardrail 100円に対する超過なし。暴走疑いなし(再生成0、無意味なretry 0)。
- 使用モデル: TTS `gemini-2.5-pro-preview-tts`(Production Zと同一=比較条件)、ASR Production cascade(gpt-4o-mini-transcribe + Azure Secondary)。評価・Trial用途だが、比較条件を現行Production・Round 1/2と揃えるため据置(PM_GOVERNANCE 25節の明示例外理由)。

## 委任_03 Phase 1b 続き(scope=Phase 1b、Guardrail 100円。出典: 同 raw_usage_log.jsonl、unitごとの `gen_summary.json`)

| unit(起動 JST) | 結果 | 実費(円) | wall |
|---|---|---|---|
| メロス Standard(09:54:25) | 10 clip中 9 OK・全採用、**part3_c10 は3試行ともASR検証不合格(STOPPED、NG 1)**。再生成せず(M-8) | 6.413 | 122.8秒 |
| メロス Advanced(09:57:20、間隔≥150秒) | 11/11 OK・各1 call・全採用 | 4.772 | 104.8秒 |
| **Phase 1b累計** | 53 clip(猿の手32+メロス21)、NG 1 | **25.581 / 100** | - |

- 日次(JST、`daily_dev_cost_01.py`): 委任_03開始前 112.13円 → 組立後 123.31円。1,000円/日以内。暴走疑いなし(再生成0)。
- 使用モデル・据置理由は委任_02と同一(TTS gemini-2.5-pro-preview-tts / ASR Production cascade、比較条件のため)。
