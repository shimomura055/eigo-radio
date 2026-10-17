# COST_ESTIMATE_01 (2026-10-17, API 0)

- call数: 10仕様×2Take×5section = 100。技術失敗時のみ1回retry(+10%見込み)。
- 想定出力音声: 1セット約63.0秒(正式版5 segment実尺+margin)×20セット = 約1260秒。出力token約31495、入力token約15655。
- 単価(前回Trial 02と同一式): 出力$6.0/M、入力$0.5/M、USD_JPY=160.0。
- TTS概算: $0.1968 = 約JPY 31.5(retry+10%込み 約JPY 34.6)。
- ASR(OpenAI、約21.0分、$0.003/分目安): 約JPY 10.1。
- 合計概算 約JPY 44.7。Guardrail JPY40.0(接近・超過は記録して継続可)、7-7 JPY100判定: 超過見込みなし。
- 補足: 委任文の見積(期待約JPY20)は前回Trial 02の80 clip(うちKP短clip 40)を件数比例で外挿したもの。今回は全clipが長いPreview/Comment(1セット約63秒)のため、音声秒ベースでは上記が妥当。前回実測 JPY13.73(85 call、候補40セグメント分は約12,800出力token)と25 tok/s換算で整合。
- 再利用/差分再生成: 新規Style×新規Takeの独立生成が目的のため再利用キャッシュ・差分再生成は対象外(Master Audio Store/キャッシュは参照しない)。
