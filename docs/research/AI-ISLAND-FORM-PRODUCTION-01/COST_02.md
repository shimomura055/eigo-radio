# COST_02 実費(AI-ISLAND-FORM-PRODUCTION-01 委任_03、2026-10-27。assemble BLOCK時点)
出典=新run `<run>/raw_usage_log.jsonl`(不追跡)を `er019.compute_cost_jpy_so_far` で円換算(内訳 `<run>/audit/cost_breakdown_01.json`)。上限¥150、案件見積300円以下。
| stage | 円 | 呼出 | 備考 |
|---|---|---|---|
| study_text(Part 2候補抽出+Top1/Top2事前生成、Std+Adv) | 1.23 | 6 | 新仕様Production初回runtime evidence(pregen_max=2) |
| scaffold(KP最終化、Std+Adv。support/KP選定はreview resumeで再生成0) | 0.33 | 3 | |
| Adv Part 1(kp_part1+ja、①+②5件) | 0.17 | 2 | |
| risk_flag(Std/Adv) | 1.33 / 0.74 | 5 / 4 | 非Blocking(Std A4: gemini format_invalid 1件はPARTIAL) |
| tts(Std+Adv、segment+KP音声+ASR一次二次) | 32.72 | 145 | openai 0.81 / gemini TTS 16.09 / OpenAI ASR 4.23 / Azure ASR 11.60 |
| assemble / player | 0 | 0 | API 0 |
| **合計(今回新規)** | **36.52** | 165 | openai 3.43 / gemini 17.26 / openai_asr 4.23 / azure 11.60 |
- Cap ¥150の24%、日次¥1,000の3.7%(JST当日、他Agent費用は含まず)。
- TTS増分の主因: `full_story_part1_k2`(複数形`AIs`)のStd 8試行(標準2+減速後再検証3+fallback+LR)/Adv 4試行+Azure二次ASR 11.6円(LR・減速後再検証の二次ASR呼出を含む)。他segmentはretry 0。
- 量産単価比(¥70/記事セット): 本文生成の承認済み先行費用 ¥47.56(run_ai_01 cost.json total)+KP候補(run_kp75_ev_01 ≒¥3.57、COST_01(7+5))+今回 ¥36.52 = 約¥87.7(Std+Adv 1セット、assembleは未完了のため最終値ではない)。X先例(ig_nobel e2e_02): text 72.8+audio 10.9=83.7。今回のaudio単独は先例の約3.3倍(retry連鎖由来)。KP/Part 2 stage増分は約¥1.7で小さい。
