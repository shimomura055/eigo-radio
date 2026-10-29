# FY-STD-V2-FEMALE-VOICE-TRIAL-01 結果(Trial。Voice採用はユーザー判断待ち。Production Voice割当は不変更)

原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_02.md` §3。対象=Standard(a2) Full Story **Voice 2(母親, `y_voice_2`)のみ**。Advanced・他Voice・他segmentは対象外・不変更。

## 条件(全候補共通。Voice名以外は同一)
- スクリプト=run_02 `a2/parts.json` segments.y_voice_2 全文(sha256 `common_conditions.json`)。1段落=chunk分割なし(Production同様に1 call)。
- TTS: backend `speech_metadata_flash_lite`、model_id `gemini-3.8-flash-lite-tts`(各`result.json`の`model`)、Style profile `fx_20261017` の FULL_STORY(177字。Std減速は文字指示ではなく生成後の6%time-stretch+減速後ASR再検証)。Style/Prompt全文=`common_conditions.json`の`style_prefix`(「Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, while keeping the news clear and credible.」の1文のみ)。
- 生成関数=Production同一(`n3_tts.generate_a2_segment_with_slowdown` = TTS→6%減速→減速後ASR再検証、connected speech判定・repetition QA有効、retry/fallback既定)。Voice切替=`ya.tts_voice`(Productionと同じ仕組み)。後処理の音量調整なし。
- 候補選定: Family Y女性Voice候補表(`er121_family_y_structure_01.py:58` `female: Zephyr, Kore, Leda, Sulafat, Erinome`=Family Z正式女性表と同じ。CURRENT_SPEC.md:1566)の**全5名**。候補1=現行Zephyr(同条件で再生成)。X/Zで使用中のVoiceと重複(Zの女性Voice表そのもの)。声量・明るさの事前選別はせず、承認済み表の5名を全比較(新規Voice追加なし=追加比較Trial回避)。
- 出力: `er121_output/family_y_voice_trial_01/surname_v2/c{1-5}_<Voice>/`(wav・result.json・ASR/attempt証跡)、`measurements.json`、`cost_log.jsonl`。Production run_02には書込なし(出力dirを分離、実装は`er121_family_y_voice_trial_01.py`)。

## 候補と結果(全5件 status=OK・ASR検証OK・retry 0・call 1)
| 候補 | Voice(voice_id) | 長さ(s) | 有音区間RMS(dBFS) | 全体RMS(dBFS) | スペクトル重心(Hz) | 2kHz以上比(%) |
|---|---|---|---|---|---|---|
| 1 | Zephyr(現行) | 46.07 | -19.99 | -21.46 | 1799 | 5.9 |
| 2 | Kore | 43.24 | **-18.06**(最大) | -19.31 | 1486 | 5.2 |
| 3 | Leda | 44.33 | -18.43 | -19.53 | 1627 | 6.3 |
| 4 | Sulafat | 45.86 | -18.88 | -20.26 | 1803 | **7.3**(最も明るい) |
| 5 | Erinome | 41.46 | -20.54(最小) | -21.60 | 1662 | 6.0 |
参考: 現行Production(run_02 `a2/narration/y_voice_2.wav`)=有音区間RMS -20.90 / 重心1535 / 2kHz以上3.8%。全候補のピークは約-3.1 dBFS(既存の出力limit)で揃う。
機械計測は参考(50msフレームRMS>-45dBFSの有音区間、重心・2kHz比=明るさ)。**声量の差は最大約2dB(Kore vs Erinome)**、暗さ(重心)は Sulafat≒Zephyr > Erinome > Leda > Kore。聞き取りやすさ・感情表現の自然さ・人物像(息子の結婚に寂しさを抱く母親)との適合は耳で判断が必要。
所見(機械計測のみからの仮説。採用判断はユーザー): 声量Koreが最大だが最も暗い、Leda・Sulafatは声量改善(+1.1〜+1.6dB vs 現行再生成)と明るさのバランス、Erinomeは最小声量。

## 費用・Status
- 費用=¥4.59(`cost_log.jsonl`、Gemini TTS+ASR。5候補×約¥0.9)。
- 比較試聴ページ: `user_test/family_y_surname_v2_voice_trial_01/index.html`(5候補mp3・スクリプト全文・条件表・評価観点・「Trial・採用はユーザー判断」注記)。
- Status=Trial(比較結果提示済み)。**Voice採用はユーザー判断**。採用決定前にProduction Voice割当(`er121_family_y_structure_01.py:60 FIXED_VOICE_SLOTS`・run_02 voice_assignment.json)は変更しない。採用時は別途、Std voice_2の再生成(約¥1.5)とVoice割当の変更範囲(Std限定か共通か)の決定が要る(Adv・既出Y記事への波及はユーザー決定事項)。
