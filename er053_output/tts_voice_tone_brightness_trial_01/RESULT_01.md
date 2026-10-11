# RESULT_01: FAMILY-X-TTS-VOICE-TONE-BRIGHTNESS-TRIAL-01 委任_01

Status: **USER_DECISION_REQUIRED(ユーザー試聴待ち)**。到達上限=VALIDATED、Production採用は未承認。Trial専用(Production code/Prompt/Routing/CURRENT_SPEC変更なし)。
使用モデル: TTS=`gemini-3.8-flash-lite-tts`(現行Production承認条件のまま。新モデル比較は対象外、PM_GOVERNANCE 25節の例外=「Style指示のみ比較」というタスク定義による)。ASR=gpt-4o-mini-transcribe系(既存判定関数)。

## 1. 比較表(Voice・model・backend・原稿・速度・音量処理は全案共通)
| ID | 言語 | 水準 | model_id | voice | 長さ(s) | peak raw | RMS raw | gain | RMS norm | peak norm | ASR判定 | call数 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J0_CURRENT | ja | 0現行 | gemini-3.8-flash-lite-tts | Aoede | 13.19 | 0.6999 | 0.10805 | 1.0 | 0.10805 | 0.6999 | NORMALIZED_MATCH | 1 |
| J1_BRIGHT | ja | 1少し明るい | gemini-3.8-flash-lite-tts | Aoede | 12.39 | 0.6999 | 0.07936 | 1.3573 | 0.10771 | 0.95 | EXACT_MATCH | 1 |
| J2_BRIGHT | ja | 2明るく親しみやすい | gemini-3.8-flash-lite-tts | Aoede | 12.68 | 0.6999 | 0.10227 | 1.0565 | 0.10805 | 0.7394 | EXACT_MATCH | 1 |
| J3_BRIGHT | ja | 3かなり明るく軽快 | gemini-3.8-flash-lite-tts | Aoede | 11.89 | 0.6999 | 0.10143 | 1.0652 | 0.10805 | 0.7456 | EXACT_MATCH | 1 |
| E0_CURRENT | en | 0現行 | gemini-3.8-flash-lite-tts | Charon | 9.35 | 0.6999 | 0.09341 | 1.0 | 0.09341 | 0.6999 | EXACT_MATCH | 1 |
| E1_UPBEAT | en | 1少し明るい | gemini-3.8-flash-lite-tts | Charon | 9.9 | 0.6999 | 0.09646 | 0.9684 | 0.09341 | 0.6778 | EXACT_MATCH | 1 |
| E2_UPBEAT | en | 2明るく親しみやすい | gemini-3.8-flash-lite-tts | Charon | 10.77 | 0.6999 | 0.09184 | 1.0172 | 0.09341 | 0.7119 | EXACT_MATCH | 1 |
| E3_UPBEAT | en | 3かなり明るく軽快 | gemini-3.8-flash-lite-tts | Charon | 9.47 | 0.6999 | 0.10502 | 0.8895 | 0.09341 | 0.6226 | EXACT_MATCH | 1 |

Style指示(実際にTTSへ渡した文字列=指示どおり、JA/ENともsent==指定を機械確認):
- J0_CURRENT: 落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。
- J1_BRIGHT: 自然で親しみやすい話し言葉で、少し明るく軽やかな声のトーンで話してください。内容に応じて自然に抑揚をつけ、落ち着きも保ってください。演技がかった話し方は避けてください。
- J2_BRIGHT: 明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。
- J3_BRIGHT: 明るく生き生きとした声で、軽快なリズムと表情豊かな抑揚をつけて話してください。聞き手が思わず続きを聞きたくなるような、前向きでエネルギーのある語り口にしてください。ただし、大げさな演技や過度なテンションは避けてください。
- E0_CURRENT: calm, conversational
- E1_UPBEAT: slightly upbeat, warm and conversational; natural and relaxed.
- E2_UPBEAT: warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.
- E3_UPBEAT: bright, lively and energetic; cheerful conversational delivery with expressive intonation, without sounding exaggerated.

## 2. 試聴URL
https://shimomura055.github.io/eigo-radio/user_test/tts_voice_tone_brightness_01/index.html

## 3. 基本QA
- 生成: 8/8成功(各1回、再生成なし、technical retry 0)。STOPPED/ERROR 0。
- ASR忠実性(1回、多重照合なし): J1/J2/J3=EXACT_MATCH、J0=NORMALIZED_MATCH(空白差のみ)、E0〜E3=EXACT_MATCH。8/8 PASS相当。
- TTS入力原稿: JAは原稿と完全同一。ENは原稿の`’`を`'`へ変換するProduction標準のTTS入力正規化のみ(全案同一、表示原稿は不変)。
- ASRはraw wav(音量正規化前)に対して実施(正規化は一律スケーリングのみで内容不変)。

## 4. 条件統一の証拠
詳細は`CONDITIONS_01.md`。model/voice/backend/trim(0.35s)/language_code/実行方式は全案同一(表参照)。音量はProduction assemblyと同じ`compute_gain_for_target_rms`(言語内で現行案のRMSへ合わせる)のみ。raw peak=全案0.6999(同一値、Production trimの結果)、正規化後RMSは言語内で同一(JA 0.10805、EN 0.09341、J1のみgain上限0.95peak制約で0.10771)。長さの差は話速/間の違いによる結果で、速度指定は全案なし(J0 13.19s→J3 11.89s、E0 9.35s→E2 10.77s)。印象を変える加工なし。raw wavは`audio/`(commit対象外)にsha256付きで`results_01.jsonl`に記録。

## 5. 費用(実測ではなく登録単価での推定、token usageがcall_fnから返らないため)
- TTS(Standard単価: 出力$6/M tokens@25tok/s、入力$0.5/M): 推定 約$0.0137 = 約¥2.2(1本¥0.23〜0.32)。
- ASR 8回(gpt-4o-mini-transcribe、約$0.003/分×計約1.5分): 約¥0.1以下。
- 合計 約¥2.3(上限¥20内)。cost_logger未install(共有ログ書込みなし)のため`raw_usage_log`には非記録。

## 6. 旧日本語TTS参考音源
**未特定**。SSOT(DECISION_LOG/各REPORT)を検索したが、「2026-09-28以前の旧日本語ナレーター(gemini-3.1-flash-tts-preview、Aoede)音声をユーザーが好評価した」旨の明示記録は見つからなかった(好評価の逐語記録は新モデルflash-lite側の「自然で全く問題なし」(NEXT-TRIAL-01 §23、2026-09-27)のみ)。参考候補(好評価未確認・掲載せず): 旧モデルProduction実績音声 `user_test/flash_lite_family_x_02_hormuz/hormuz_standard_current_model.mp3`(Pages: https://shimomura055.github.io/eigo-radio/user_test/flash_lite_family_x_02_hormuz/index.html)。ユーザーが好評価した音源を指定いただければ参考枠へ追加可能。

## 7. 注意・ユーザー判断事項
- Style指示のみの1回生成比較(N=1)。TTSは同一指示でも出力が揺れるため、差は傾向として聴くこと。
- 気に入った案をProduction採用する場合は別途ユーザー承認(APPROVED_FOR_PRODUCTION)+Wiring Taskが必要(未実施)。採用時はJA(FAMILY_X_ROLE_STYLE_JA)/EN(PREVIEW/COMMENT)の変更のみで済む見込みだが、他roleの整合・ASR再確認は別途。
- ユーザー試聴後の判断: どの水準(1/2/3)を採用候補にするか、日本語と英語で別水準にするか。
