# COST_ESTIMATE_02 (FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-02 委任_01, 2026-10-12)
結論: 8候補x3Part=24 call、概算 JPY 33〜36 <= 上限JPY 40 のため実行。
根拠: 前回(PACE-01)実費 JPY 33.06(TTS 26.96 + Primary ASR 6.10、24call)。今回もPrompt差のみで同一原稿・同一方式。Prompt文字数は短縮(入力トークンは僅減)。遅い候補は音声が長く出力トークン増(+数%)の余地を見込み上限側 約36。
予算ガード: 実行中累計が JPY 40 を超えた時点で以降のjobをBUDGET_STOP(コード内)。技術失敗retryは各jobで1回のみ。F5は再生成しない。
