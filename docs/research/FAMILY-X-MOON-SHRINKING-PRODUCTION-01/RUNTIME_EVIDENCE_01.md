# RUNTIME_EVIDENCE_01 (FAMILY-X-MOON-SHRINKING-PRODUCTION-01 委任_02、2026-10-24)

## 正式入口・起動
- text: `er019_family_x_entertainment_production_runner_01.py --stage all`(1起動、開始22:25 JST、約10分)。run=`er019_output/moon_shrinking/run_ms_01`
- audio: `er019_family_x_audio_production_runner_01.py --level both --stage all --budget-jpy 100`(1起動、22:36〜23:52 JST、約76分)。out=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_01`
- 起動前 `stop_scope_check` rc=0(`stop_check_text/audio/page.json`)。再起動0・HR再生成0・例外起動0。import graph内tracked .py差分0(HEAD=ed24bae8c)。cost logger `install`はrunner内(`cl.install(.../raw_usage_log.jsonl)`)。

## actual model_id
- text/KP: `gpt-6-luna`(requested=actual、fallback_detected=false。Adv英訳 `resp_00f245fd...`)。 Risk flag: gpt-6-luna / gemini35fl
- TTS: `gemini-3.8-flash-lite-tts`(tts_backend=speech_metadata_flash_lite、33 call 全success)
- ASR Primary: `gpt-4o-mini-transcribe`(37 call)、Secondary: `azure-speech-stt`(8 call)。style_profile=fx_20261017

## Gate結果
| Gate | Std(a2) | Adv(b1b) |
|---|---|---|
| Fact Ledger | VERIFIED 10 / AMBIGUOUS 1 / REJECTED 0(F05のみAMBIGUOUS=断定禁止として保持) | 同 |
| TTS segment | 全48件 OK | 全50件 OK |
| ASR | PASS_WITH_WARNING 1件: `japanese_title`(Primary「しじんだ」→Azure Secondary「縮んだ」でSECONDARY_CONFIRMED、`audit/pass_with_warning_listening_list.json`) | 0件 |
| Style Profile Gate | PASS(blocked 0、human_approved 0、warnings 0) | PASS(同) |
| HR Lock | なし(review_lock_state 全RESOLVED) | なし |
| Pronunciation alarm | 0件 | 0件 |
| KP vote audit / KP source gate | 3/3 vote evidence、blocking=false | 同 |
| Headroom | peak 0.879、clipping無し | peak 0.929、clipping無し |
| Local Rewrite | 0件(開示事項なし) | 0件 |
| 公開page_verify | 47/47再生、seek OK、console error 0、HTTP>=400 0、file:// 0(`page_verify_01.json`) | 同 |

## KP(A-1・課題②・X2p'適用、`meaning_stage={stage:applied,path:newgen_meaning_v1,n_newgen_calls:1,n_legacy_calls:0}`、ALIGN_PASS、unresolved 0)
Std: 1 the Moon's radius=月の半径 / 2 a failing grade=落第点 / 3 reach a certain level=一定の水準に達する
Adv: 1 put the brakes on=歯止めをかける / 2 show up as=〜という形で現れる / 3 accounting period=会計期間
(canonicalization_PASS、`keyphrase_redundancy_qa`あり、未承認KPなし。KP日本語gloss生成費 Std 0.1733円/Adv 0.2836円)

## 尺・成果物
Std 322.47秒(5:22)、Adv 299.76秒(5:00)。試聴URL(Std/Adv切替): https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_01/index.html (commit 05c20d3aa)。日本語題=「月のしわに『縮んだ分、全部載ってますか?』」(ページ見出しは委任文指定の「月は少しずつ縮んでいる?」)。

## 費用(円)
| 段 | 実費 |
|---|---|
| text(research 5.82/ledger 9.10/B3 12.07/中核数値丸め 0.17/W-1 R0 7.79+symbol再生成 6.23/R1 3.63/R2 2.51/Adv 0.47/Std 0.20/RF 約1.7) | 49.76 |
| audio(openai 1.91/gemini_batch(TTS) 6.10/openai_asr 3.41/azure 2.61) | 14.02 |
| 合計 | **63.78**(目標70円/記事セット以内、上限100円以内) |
参考: 『英単語ガチャ』104.73円より約41円低い(ASR同音NG・HR Lock再生成なし)。Ledger/B3が多め(論文ベース)でもtext約50円。

## 所要
text約10分+audio約76分(TTS直列+cooldown込み)+page/verify約5分。他agent TTSとの重複待機は観測されず。
