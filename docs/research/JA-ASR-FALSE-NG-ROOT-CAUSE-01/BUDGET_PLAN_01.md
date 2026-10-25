# BUDGET_PLAN_01(Phase 3 見積。承認枠: 案件300円以下は7-7に基づきAI自律。これは本委任の対象外=未実行)

単価の根拠: Azure STT=¥0.0447/秒(月題記録: 5.96秒=¥0.2667、`review_lock_state.json` japanese_title attempt2 `est_cost_jpy`)。OpenAI gpt-4o-mini-transcribe=公表単価$0.003/分×¥160≒¥0.0008/秒(**概算。実測は`raw_usage_log`で確認**)。Gemini TTS(flash-lite)=1 clip ¥0.3〜1.0(概算。月run全体の音声費15.19円/約25 clip=平均0.6円、`RESULT_PACKET_FXNR7.md`)。ローカルWhisper(faster-whisper)=CPUのみ¥0。
| # | API call | 件数 | 単価 | 費用(概算) | 目的 |
|---|---|---|---|---|---|
| 1 | Azure STT(月題 attempt1/3の既存wav 各約7秒) | 2 | ¥0.31 | ¥0.6 | 案B-lightの可否(Azureが8900を返すか) |
| 2 | OpenAI再転写(月題3 wav ×3回) | 9 | ¥0.006 | ¥0.1(上限¥0.5) | 数詞崩れの再現性(確率的か決定的か) |
| 3 | Azure STT(P-2/P-3 flip集合のうちAzure未呼出wav、平均約12秒) | 約10 | ¥0.54 | ¥5.4 | 推定正例の独立確認 |
| 4 | Azure STT(N-2推定負例の値DIFF/UNKNOWN 約10 wav) | 約10 | ¥0.54 | ¥5.4 | B-lightの誤PASS側確認 |
| 5 | TTS新規(N-3 誤読音声16 clip) | 16 | ¥0.3〜1.0 | ¥4.8〜16 | 確定負例の生成 |
| 6 | OpenAI+Azure ASR(N-3 16 clip、各約6秒) | 16×2 | ¥0.006/¥0.27 | ¥4.4 | N-3の実判定 |
| 7 | ローカルWhisper(medium) | 任意 | ¥0 | ¥0 | 第3の独立転写(参考。Production導入判断には使わない) |
**合計の中央値≈¥21、上限≈¥34**(再実行0。再試行は委任文が許可した場合のみ)。Cap提案=¥50。7-7により300円以下の承認済みScope内は自律実行可、ただし**新仕様の検証Trialである点(案Aの新層・B-lightのP1変更)は、本委任文の“Phase 3は別委任”に従い、Fableの委任後に実行**。
量産単価影響(採用時の見込み): 案A=API 0(Primaryで通る件が増えるため、Azure呼出はむしろ減)。案B-light=発火率≈0.16%×Azure約¥0.27≒¥0.0005/attempt。70円/セット目標への影響は無視可能(±0.01円未満)。
削減効果(再生成・HR回避): 1 JA segmentのHRを避けると、TTS 3回(0.9〜3円)+ASR+Azure+人手確認を節約。
