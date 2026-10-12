# FINAL_V3_BUILD_PLAN_01(FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01、2026-10-12)

ユーザー決定(2026-10-12): Coffee Style選択=APPROVED_FOR_PRODUCTION(**Coffee記事限定**)。全記事共通Styleは未承認。本作業は Trial隔離経路(Production runner/Master Store/manifest/telemetry/queue 非使用)で完成版v3を制作する。Production配線(PRODUCTION_WIRED)ではない。

## role別 再利用/再生成表
| role | Standard | Advanced | 区分 | 根拠 |
|---|---|---|---|---|
| Intro A / Intro B | A5 / B5 (Charon) | 同左 | 再利用(Trial音声) | Final v2と同sha、Style/model不変 |
| Preview | R2 (Aoede, 日本語) | E1 (Charon, 英語) | 再利用(Trial音声) | R2 Prompt sha 625826c1…、gemini-3.8-flash-lite-tts |
| Comment 1-4 | R2 | 既存承認(E2_UPBEAT) | 再利用 | Final v2と同sha |
| KP英語 | K2 | K2 | 再利用(Trial音声) | Final v2(委任_03/04)と同sha |
| KP日本語意味 | M2 | - | 再利用(M2維持、Q1-Q8不採用) | Final v2と同sha |
| KP英語解説/固定音声/topic_intro/japanese_title/num_*/intro類 | 既存承認 | 既存承認 | 再利用 | 未変更role |
| Full Story Part1-3 | **PD8再生成(3 call)+6%減速** | PD8 Trial音声(sha一致)再利用 | Std=再生成 / Adv=再利用 | Adv PD8: pace_trial_02で生成・Primary ASR verified(3/3)・WPM 183.2 |
| In One Line | **新原稿で再生成(1 call)+6%減速(現行Style踏襲)** | **新原稿で再生成(1 call)** | 再生成 | 本文/Comment/KPは作り直さない |

## 再生成TTS合計: 5 call(Std Full Story 3 + IOL 2)。In One Line原稿LLM: gpt-6-luna(Production英語Writerと同一) 各レベル1〜2 call。
## 概算費用(USD/JPY=160)
- PD8 Std Full Story TTS 3 call: 約JPY4.5(pace_trial_02のPD8実績 JPY4.46/3 Part、ASR込み)
- IOL TTS 2 call+ASR: 約JPY0.4
- 減速後ASR(参考)3+1 call: 約JPY0.3
- IOL原稿LLM 2〜4 call(入力約2k tok、出力小): 約JPY0.5〜2
- retry余地(Full Story 3 Part×最大2回再生成の理論上限): 約JPY9
- **概算 約JPY6〜8、理論上限 約JPY17。上限JPY50以内。実行時に累計JPY45超でSTOPするガードを置く。**
