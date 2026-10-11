# COST_ESTIMATE_01B (2026-10-11)

- call数: 75 (B 25 + C 25 + D 25)。各1回、技術失敗時のみ1回retry。ASRなし(無料)。
- 想定出力音声: 合計 約424秒(既存音声尺+margin。25 token/秒)。入力token合計 約9752(保守的)。
- 単価(前Trial TTS_VOICE_TONE_BRIGHTNESS_TRIALと同一式): 出力$6.0/M tokens、入力$0.5/M tokens、USD_JPY=160.0。
- 概算: $0.0684 = 約¥10.9(技術失敗retry+20%見込み 約¥13.1)。
- 上限判定: 上限¥50。概算が¥50以下なら実行可、超過ならSTOP。
