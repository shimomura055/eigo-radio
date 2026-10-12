# COST_ESTIMATE_01 (2026-10-12)

- call数: 80 (R 8x5=40 + Q 8x5=40)。各1回、技術失敗時のみ1回retry(見込み+20%)。基準P2/M2は既存音声再利用(再TTSなし)。
- 想定出力音声: 約609秒(基準P2/M2の既存尺+margin、25 token/秒)。入力token約7966(保守的)。
- 単価(01Bと同一式): 出力$6.0/M tokens、入力$0.5/M tokens、USD_JPY=160.0。
- TTS概算: $0.0954 = 約JPY 15.3(retry+20%見込み 約JPY 18.3)。
- ASR(Primary OpenAI ja-JP、候補80+基準10=90件): 約JPY 1.1以下(保守的見積)。
- 合計概算 約JPY 19.4(retry込み・ASR込み)。上限JPY 25。上限以下なら実行可、超過ならSTOP。
