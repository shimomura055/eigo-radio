# STYLE_APPLICATION_EVIDENCE_V5 (FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01、2026-10-12)

状態: **Std(R2)=runtime evidence取得済み・Std v5組立済み / Adv(P3)=5件中3件のみ生成済み(runner実行中に実行層のshell timeoutで中断、結果記録なし)=Adv未完**。数値はすべて実測(`style_application_evidence_v5.json`、`audit/tts_generation_results.json`、各clip `attempts/*.json`のinstruction_text、`raw_usage_log.jsonl`)。

## 実行経路
- 正式Production runner: `er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --level a2 --stage tts --style-profile coffee_final_v5 --tts-backend speech_metadata_flash_lite --budget-jpy 30 --only-segments preview,comment_1,comment_2,comment_3,comment_4`(起動1回、rc=0)。
- out_dir `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01`(新規、`audit/style_profile.json` = profile coffee_final_v5、roles FULL_STORY(P8 3eadf4f6)/SUPPORT_JA(R2 625826c1)/KP_EXPLANATION_EN(P3 a8aaec59))。
- 使用モデル: TTS = gemini-3.8-flash-lite-tts(最新世代・Production正式backend、voice=Aoede、BATCH)、ASR = gpt-4o-mini-transcribe(Production既存)、Comment4文章 = gpt-6-luna(Trial-03同一経路)、RF guard = gpt-6-luna + gemini-3.5-flash-lite(既存Risk Flagger)。最新でない例外なし。

## Std Preview/Comment 1〜4 = R2(実測)
Result(runner results JSON、style_profile.style_base_sha256 = R2 `625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f`):
| clip | status | fallback_used | style_base_sha256 | model | ASR分類 | wav sha256 |
|---|---|---|---|---|---|---|
| preview | OK | False | 625826c1187b(=R2) | gemini-3.8-flash-lite-tts | NORMALIZED_MATCH | b9739f509f5e |
| comment_1 | OK | False | 625826c1187b(=R2) | gemini-3.8-flash-lite-tts | EXACT_MATCH | 1381b2418be6 |
| comment_2 | OK | False | 625826c1187b(=R2) | gemini-3.8-flash-lite-tts | NORMALIZED_MATCH | 9a588e46c189 |
| comment_3 | OK | False | 625826c1187b(=R2) | gemini-3.8-flash-lite-tts | NORMALIZED_MATCH | 4500cb0fb87d |
| comment_4 | OK | False | 625826c1187b(=R2) | gemini-3.8-flash-lite-tts | PHONETIC_MATCH | d108c5872efd |

attempt別(attempt audit JSONの instruction_text の sha256 を計算し R2 と比較):
| clip | attempt | model | voice | mode | instruction sha256 | R2比較 | ASR分類 | verified |
|---|---|---|---|---|---|---|---|---|
| preview | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | 625826c1187b | R2一致 | NORMALIZED_MATCH | True |
| comment_1 | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | 625826c1187b | R2一致 | TRUE_CONTENT_MISMATCH | False |
| comment_1 | 2 | gemini-3.8-flash-lite-tts | Aoede | BATCH | 625826c1187b | R2一致 | EXACT_MATCH | True |
| comment_2 | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | 625826c1187b | R2一致 | NORMALIZED_MATCH | True |
| comment_3 | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | 625826c1187b | R2一致 | NORMALIZED_MATCH | True |
| comment_4 | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | 625826c1187b | R2一致 | PHONETIC_MATCH | True |

- 全attempt(6件)でinstruction_text全文のsha256がR2と一致(Std Preview/Comment 1〜4でR2が実送信された)。comment_1のattempt1は数字(10)の転写差でTRUE_CONTENT_MISMATCH(ASR不合格、既存retry機構で再生成)、attempt2でEXACT_MATCH。fallback(minimal instruction)は0件。Local Rewrite 0件。
- M3 Gate相当(SUPPORT_JA 5 segmentのみ判定、Full Storyはv4流用でruntime生成なし): BLOCKなし。

## Adv KP英英解説 = P3(部分)
| clip | attempt | model | voice | mode | instruction sha256 | P3比較 | ASR分類 | verified |
|---|---|---|---|---|---|---|---|---|
| kp1_explanation_en | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | a8aaec591ef6 | P3一致 | NORMALIZED_MATCH | True |
| kp2_explanation_en | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | a8aaec591ef6 | P3一致 | NORMALIZED_MATCH | True |
| kp3_explanation_en | 1 | gemini-3.8-flash-lite-tts | Aoede | BATCH | a8aaec591ef6 | P3一致 | NORMALIZED_MATCH | True |

- kp1〜kp3のattemptは全てP3(instruction sha一致)・gemini-3.8-flash-lite-tts・Aoede・BATCH。ただし**runnerがkp4生成中に外部からではなく実行層のshell timeout(540s)で終了**したため、`b1b/audit/tts_generation_results.json`にはsegment結果が書かれていない(seed bundleのみ)。wavは存在するが結果recordとM3 Gate判定が無い=採用不可(未完)。kp4・kp5は未生成(kp4のBatch submitが発生した可能性は否定できない)。
- 再起動は委任文の許可がないため**実施していない**(Fable判断待ち)。
