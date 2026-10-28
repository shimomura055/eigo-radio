# BUDGET_PLAN_02 (JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B)
- 対象: n3_clips_01.json の N3 30 wav(phase3_run/n3/N3-01..30.wav、約6秒/本)を OpenAI gpt-4o-mini-transcribe(Production Primary route `er006_asr_provider_routing_01.transcribe`)で各4 draw再転写 = 120呼出。
- 見積: 120 × 6秒 × ¥0.0008〜0.0009/秒 ≈ ¥0.58〜0.65(BUDGET_LOG_01の実測単価 ¥0.0056/本 → ¥0.67)。個別Cap ¥3、案件見積≪¥300、日次1,000円内。Azure・TTS呼出なし。
- 実行: 1起動(`n3_redraw_02.py`)、自動再試行・ラッパなし、エラー時は即停止してFableへ報告。cost_log=`n3_redraw_02.cost_log.jsonl`。
- 実績は BUDGET_LOG_01.md に追記。
