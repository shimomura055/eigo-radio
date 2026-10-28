# BUDGET_PLAN_03 (JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03)
- 対象: 正例拡張4 wav(mey_02 comment_2 att3 13.7s / Z melos run_e2e_02 comment_1 att3 18.8s / Y preview att5 14.0s / Y preview att1 15.7s、計62.2秒)を OpenAI gpt-4o-mini-transcribe(Production Primary route `er006_asr_provider_routing_01.transcribe`)で各4 draw = 16呼出。
- 見積: 249秒 × ¥0.0075/秒(N3 120呼出の実績: ¥1.55/206.6秒)= 約¥1.9。上限(個別Cap)¥15。案件見積≪¥300、日次1,000円内。Azure・TTS呼出なし。
- 負例追加draw: なし(N3既出の4 drawを再利用)。0円。
- 実行: 1起動(redraw_03.py)、自動再試行・ラッパなし、エラー時は即停止してFableへ報告。cost_log=redraw_03.cost_log.jsonl。実績はBUDGET_LOG_01.mdに追記。
