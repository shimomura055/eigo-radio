# BUDGET_LOG_01 (FX-PARAGRAPH-CHUNK-TTS-TRIAL-01)

| 日時(JST) | 委任/Phase | 内容 | 有料API | 費用(円) | 累計(円) | 上限(円) |
|---|---|---|---|---|---|---|
| 2026-10-25 | 委任_01 Phase 1 | 既存仕様調査・DEV script/test・A側計測(ローカル)・ローカルfaster-whisper(small)境界gap測定・A全体再構築検証 | なし(Gemini/OpenAI/Azure呼出0。`raw_usage_log`の新規行0) | 0.00 | 0.00 | 50(Fable設定、Phase 2用) |

- 日次開発費上限1,000円(PM_GOVERNANCE 7-9)に対する本件の当日加算: 0円。
- Phase 2見積(DESIGN_01 §7): B_r1≈4.2円 / A_r2≈4.2円 / B_r2≈4.2円(合計≈12.6円、最悪≈57円相当だがCap50円で停止)。単価出典=`er005_output/cost_baseline_01/pricing_snapshot.json`。

## 委任_02 Phase 2(2026-10-25 JST 07:26:10〜07:31:06)

| 日時(JST) | 委任/Phase | 内容 | 有料API | 費用(円) | 累計(円) | 上限(円) |
|---|---|---|---|---|---|---|
| 2026-10-25 | 委任_02 Phase 2 | B_r1(段落10chunk)+A_r2(part3call)+B_r2(段落10chunk、1件retry)。TTS 24 call(gemini-3.8-flash-lite-tts)・OpenAI ASR 24 call・Azure 1 call | Gemini 10.91円/OpenAI ASR 2.18円/Azure 0.80円 | 13.89 | 13.89 | 50(Fable設定) |

- 出典: `er113_output/fx_paragraph_chunk_trial_01/raw_usage_log.jsonl`(cost logger、`runner.compute_cost_jpy_so_far`で集計)。arm別: B_r1 4.27円/A_r2 3.98円/B_r2 5.64円(retry+Azure含む)。見積12.6円に対し+10%。
- 日次開発費1,000円に対する本件の当日加算=13.89円(他Family・並行タスク分は別)。Cap到達なし、有料run再起動0。
- postprocess(ローカルfaster-whisper・計測・mp3・ページ生成)は費用0。
