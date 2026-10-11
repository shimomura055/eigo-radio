# COST_ESTIMATE_D_01 (2026-10-12)

- TTS call数: 32(8語x4版、各1回、技術失敗時のみ1回retry見込み+20%)。model=gemini-3.8-flash-lite-tts(Production同一)。
- 想定出力音声 約70秒(25token/秒)、入力token約6982。単価 出力$6/M・入力$0.5/M、USD_JPY=160(前Trialと同一式)。
- TTS概算: 約JPY2.7(retry込み)。
- Primary ASR(OpenAI gpt-4o-mini-transcribe、約2秒x32、$0.003/分想定): 約JPY0.51。Azure/Secondaryは呼ばない。ローカルwhisperは0円。
- 合計見込み: 約JPY3.2。上限JPY10。実行可。
