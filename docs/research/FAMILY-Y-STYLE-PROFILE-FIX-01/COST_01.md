# COST_01 — 費用実績(FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02)

出典: `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01/cost_log.jsonl`(108行)を`er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far`(runnerの予算guardと同じ関数)で集計。runner出力の`spent_jpy_cumulative`: tts_b1b完了時 7.8412、tts_a2完了時 30.7877。

| 区分 | 円 |
|---|---|
| Gemini TTS | 16.43 |
| OpenAI ASR | 4.33 |
| Azure STT(KP voteと二次ASR) | 10.03 |
| **合計** | **30.79** |
| 内訳: Adv(tts_b1b) | 7.84 |
| 内訳: Std(tts_a2。launch 2) | 22.95 |
| launch 3(`--regenerate-stage tts_a2 --only-segments y_voice_1,preview`) | 0(review lockによりAPI 0。cost_log行数108不変) |

- 見積(委任文)25〜45円/Cap 60円 → 範囲内(51%)。Cap到達・接近なし。当日既使用 約563円 + 30.79円 = 約594円 < 1,000円(7-9)。案件300円以下(7-7)。
- Std側が高かった要因: y_voice_1(3 TTS+二次ASR/Azure、cooldown 180秒)、preview(3 TTS)、y_voice_2(2 TTS)のretry。
- KP英語(K2)はStd/Advで別Master Audio ID(Store hitなし。R-6の想定〔3 take減〕は不成立): generated 6件。shell固定音声はStore再利用19件(charon_english 18、charon_japanese 1)。出典=`er006_output/master_audio_store_01/reuse_telemetry.jsonl`(`run_style_fix_01`の行)。
- 追加費用なし(再試行・暴走疑いなし)。残作業(HR承認後のgate/assemble/pages/page_verify・公開)はAPI 0(0円)。
