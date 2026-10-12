# COST_01
- モデル: TTS `gemini-3.8-flash-lite-tts`(Production同一。最新モデル原則の例外種別2=測定対象がProduction使用モデル。応答model_version=gemini-3.8-flash-lite-tts)、ASR `gpt-4o-mini-transcribe`(Production Primary ASR、費用は推定式)。
- TTS 55 call(各KP 27 = P0×3 + P1〜P8×3、+ KP4 P8r2の再生成1。ASR ASR_VALIDATION_UNCERTAIN→同一Promptで再生成、技術失敗0)。TTS JPY 4.579 + ASR推定 JPY 0.774 = **JPY 5.353 / 上限 JPY30**。算出は `generation_log_01.jsonl` の tts_cost_jpy / asr_cost_jpy_est 合計。
