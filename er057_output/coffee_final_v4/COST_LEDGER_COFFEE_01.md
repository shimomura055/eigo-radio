# COST_LEDGER_COFFEE_01 (FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_01A, 2026-10-12)

SSOT(DECISION_LOG/OPEN_ITEMS)をgrep: Coffee全体枠の上限記載は見つからず(個別Trial上限のみ: 例 pace 40/ tone 20)。よって本委任上限 JPY30(Fable承認)で進行。

## 既知のCoffee関連Trial実費(er057_output配下 cost記録、JPY、請求画面未確認の推定)
| 作業 | JPY | 出典 |
|---|---|---|
| coffee_final_listening_tone_trial_01 part_AEF | 5.16 | cost_actual_01A.json |
| 同 part_BCD | 9.55 | cost_actual_01B.json |
| 同 part_final(v2 gen) | 8.52 | gen_summary_03.json |
| 同 part_final KP adv | 0.15 | cost_actual_04.json |
| ja_aoede_style_trial_02 | 13.73 | cost_actual_01.json |
| pace_trial_01 | 33.06 | cost_actual_01.json |
| pace_trial_02 | 33.66 | cost_actual_02.json |
| coffee_final_audio_assembly_01 (v3) | 8.43 (+Std Part2 Secondary Azure少額) | gen_summary_v3_01.json |
| aoede_style_trial_03 | 12.17 | gen_summary_03.json |
| 小計(上記9件) | 124.43 | |

未集計(別集計で記録済み): Coffee Phase 2(公式JPY20.73+Azure補正、OPEN-275)、coffee_new_tone/coffee_prices_l3/ER-052系の記事生成費。上記小計に含まない。

## 本委任の生成前概算 (P8 x 6 Part, gemini-3.8-flash-lite-tts)
- pace_trial_02のPD8実績: 3 Part ASR込み JPY4.46 -> 6 Part 約JPY9。減速後参考ASR 3件 約0.3。
- Secondary(Azure)は Primary非verified時のみ。retry余地を含む理論上限(6 Part x 3 attempt)約JPY27、実行ガード JPY28超でSTOP。
- 概算 約JPY9-10、上限 JPY30以内。

## 実績(生成完了後)
- 本委任実費 JPY9.48(TTS 6 call=JPY7.22 gemini-3.8-flash-lite-tts、Primary ASR+減速後参考ASR推定 約JPY2.26 gpt-4o-mini-transcribe、Secondary Azure 0回)。全clip attempt1採択、再生成0。上限JPY30以内。
- Coffee累計(上記小計124.43 + 本委任9.48) = 約JPY133.9(未集計項目除く)。
- 請求画面は未確認(usage_metadata実測x単価の推定)。
