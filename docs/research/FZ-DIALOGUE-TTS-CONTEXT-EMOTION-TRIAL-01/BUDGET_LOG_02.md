# BUDGET_LOG_02 — 実費記録(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 追加2作品、2026-10-26 JST)

出典: `er118_output/fz_dialogue_context_tts_trial_02/raw_usage_log.jsonl`(`compute_cost_jpy_so_far`=`er005_cost_logger`の記録から集計。推定値は使わない)。Cap 30円(追加2作品の合計、Round 1の30円とは別枠)。

| 区分 | 担当 | call数 | 円(実測) |
|---|---|---|---|
| gpt-6-luna(感情情報、開いた窓) | 委任_04 Phase 1a | 1(入力2,018/出力784 token) | 0.095 |
| gpt-6-luna(感情情報、猿の手) | 委任_04 Phase 1a | 1(入力1,848/出力866 token) | 0.0988 |
| gemini-2.5-pro-preview-tts | **未実行**(Phase 1b=委任_05) | 0 | 0 |
| ASR(生成時) | 未実行 | 0 | 0 |
| **合計** | | **2** | **0.1938**(cost logの集計値 0.193856) |

- Cap残: 約29.81円。見積(BUDGET_PLAN_02): 保守上限29.6円(感情LLM 0.19円は実測へ置換済み) / 期待値26.8円。
- 日次(JST 2026-10-26、`docs/pm/tools/daily_dev_cost_01.py`): 委任_04開始前 0.17円 → Phase 1a後 0.37円(他agent分0.17円を含む)。1,000円/日以内。証跡 `er118_output/fz_dialogue_context_tts_trial_02/daily_cost_{before,after}_委任_04.json`。
- 使用モデル(開発・評価用途の最新モデル原則、PM_GOVERNANCE 25節): 感情LLMは Round 1と同一の `gpt-6-luna`(返却モデル名も`gpt-6-luna`)、TTSは本番と同一の `gemini-2.5-pro-preview-tts`(比較条件を揃えるため。本番モデルとの同一性が目的で、旧モデルを選ぶ例外ではない)。
- 本委任のunit test(54件)は遮断harness下で実行し、外部接続の試行は0(上記cost logの行数も2のまま)。

## 委任_05(Phase 1b、2026-10-26 JST)実測
- 起動: open_window gen-session 07:24:29〜07:29:39(310秒) / monkeys_paw gen-session 07:30:06〜07:34:48(282秒)。起動間隔は約27秒だが別作品・別コマンドで暴走・再起動ではない(各1起動、rc=0)。起動前 stop check rc=0(`er118_output/fz_dialogue_context_tts_trial_02/stop_check_委任_05.json`)。実行: `TTS_EXECUTION_MODE=STANDARD`、`PYTHONUTF8=1`、`.venv/Scripts/python.exe er118_fz_dialogue_context_tts_trial_01.py --work <w> gen-session`。
- 実費(cost log `compute_cost_jpy_so_far`): open_window後の累計 14.8558円(Phase 1a LLM 0.1938円含む) / monkeys_paw後の累計 **27.9896円**。内訳: LLM 0.19 + Gemini TTS 26.20(50 call) + OpenAI ASR 1.12(50 call) + Azure STT 0.48(2 call)。Cap 30円に対し残 約2.01円。先読みguard発火なし。
- 日次(JST 10/26): 79.2円(うち本Trial 27.99円、X並行分 約51円)、1,000円/日以内。`daily_cost_after_委任_05.json`。
- 使用モデル: TTS=gemini-2.5-pro-preview-tts(本番同一、比較条件のため)、ASR=OpenAI/Azure(Production検査と同一)、感情LLM=gpt-6-luna(Phase 1a済み)。
