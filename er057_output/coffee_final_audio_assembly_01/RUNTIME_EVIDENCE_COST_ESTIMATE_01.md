# RUNTIME_EVIDENCE_COST_ESTIMATE_01(S6、FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02)

日付2026-10-12。**見積のみ(実行・API呼出・課金なし)**。実行可否はユーザー判断待ち。

## 対象run
`--style-profile coffee_p8 --tts-backend speech_metadata_flash_lite --stage tts --level both`、新out_dir(`er019_output/coffee_prices/run_p8_wiring_01` 想定)、両level(Std=a2 / Adv=b1b)の全segment(topic_intro・japanese_title・preview・comment1〜4・Full Story part1〜3・In One Line・Key Phrase・shared narration)をTTS生成。scaffold成果物(parts/support/KP)は出所記録付きで明示コピー(scaffold LLMは再実行しない=M2)。

## 実績ベース
| 根拠 | 内容 | 費用 |
|---|---|---|
| `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01/raw_usage_log.jsonl` | Coffee同記事・両level・flash-lite の tts stage 全体(101 call: gemini_batch 8.08 + openai_asr 4.16 + openai 0.03 内訳は提供者別) | **JPY 12.34**(scaffold stage は別に JPY 3.46、合計15.80) |
| `.../coffee_prices__run_l3_01_ttsonly/raw_usage_log.jsonl` | b1bのみ tts 31 call | JPY 4.09 |
| `er057_output/aoede_style_trial_03` / `pace_trial_02` の実績メモ(FINAL_V3_BUILD_PLAN_01.md) | P8/PD8 Std Full Story 3 call+ASR | 約JPY 4.5(約1.5/part) |
| `er057_output/coffee_final_audio_assembly_01/FINAL_V3_BUILD_PLAN_01.md` | v3再生成 5 call(概算6〜8、理論上限17) | 参考 |

## 見積
- 通常ケース(全segment 1回でASR PASS、Master Store cache hit含む): **約 JPY 10〜15**(実績12.34。P8はStyle文字列が約+340文字増えるが入力トークン増は無視できる)。
- 再生成を含む上限(Full Story 6 segment が各+2回生成[総生成3回上限]、各約JPY1.5): +約JPY 18 -> **理論上限 約 JPY 30**。
- scaffoldを再実行する場合は +約JPY 3.5 かつv3と原稿が変わる(Writer出力が異なる)ため非推奨(M2の明示コピーを推奨)。
- 推奨予算: `--budget-jpy 40`(Budget Guardは **tts stage完了後** にのみ判定されるため、事前抑止ではない点に注意)。事前抑止したい場合は `--level b1b` を先に実行 -> 結果確認 -> `--level a2`(各JPY約5〜8)の直列分割を推奨(同一profile記録・同一out_dir、直列の理由=同一out_dir・Review Lock state競合回避)。
- Production採用判断は別途人間ユーザー。本runは配線証跡であり、01A成果物(Coffee v4)を置き換えない(M6)。

## 実行前チェックリスト(runtime evidence実行が承認された場合)
1. 新out_dirであること(`audit/tts_generation_results.json`等が無い。M2)。
2. scaffold成果物の出所記録付き明示コピー(parts/support/KP、Review Lock・承認・attempt系はコピーしない)。
3. `--tts-backend speech_metadata_flash_lite`(M5)。
4. 実行後: M4判定(`audit/style_profile_gate.json`、各segmentの `style_profile`+`style_prefix`/`attempts_log`)、Audio Validation Gate、Assembly前M3 Gate。
