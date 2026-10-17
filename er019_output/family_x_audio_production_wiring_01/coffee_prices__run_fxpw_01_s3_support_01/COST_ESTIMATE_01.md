# COST_ESTIMATE_01 (S3W Phase A, 2026-10-17, API 0)

- 対象: Std Preview/Comment1〜4 の 5 clip(原稿文字数: preview=88字, comment_1=43字, comment_2=101字, comment_3=79字, comment_4=69字)。S3 Style {len(s3)}字。
- 想定出力音声 約63.0秒(正式版実尺+margin)→出力token約1575(25 tok/秒)、入力token約788。
- 単価(Trial-04と同一式): 出力$6.0/M、入力$0.5/M、USD_JPY=160.0。
- TTS概算 $0.0098 = 約JPY1.57(技術失敗retry込み最悪 約JPY3.15)。
- ASR(OpenAI、約1.0分、$0.003/分目安) 約JPY0.50(統一judgeのcascade[Azure等]が発火した場合は別途。通常PASSなら0)。
- 合計 期待約JPY2.08 / 最悪約JPY4.16。Guardrail JPY15.0。
- T-2追記4点: (1)差分再生成=5 clipのみ生成(他sectionはR2版を参照、再生成しない) (2)再利用キャッシュ=Master Audio Store等は参照・書込みしない(新Style×同一原稿の独立生成が目的) (3)--budget-jpy=15.0明示 (4)全再生成ではない(5 clip)。
