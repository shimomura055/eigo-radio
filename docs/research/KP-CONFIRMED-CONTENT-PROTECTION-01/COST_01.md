# COST_01(委任_02B 実費。usage logの実測)

上限: 個別Cap ¥30(Family別目安 約¥10)。案件見積300円以下・承認済みScope内=自律実行(PM_GOVERNANCE 7-7)。日次1,000円内。

| Family | 内容 | モデル/routing | 実費 | 根拠 |
|---|---|---|---|---|
| X | a2 `--stage tts`(Full Story chunk 9本の実TTS+ASR) | TTS `gemini-3.8-flash-lite-tts`(Aoede)、ASR=OpenAI(primary)+Azure(secondary vote) | **¥7.39**(gemini 3.68 / azure 2.23 / openai_asr 1.49) | コピーdirの`raw_usage_log.jsonl`の増分30行(実行前後比較) |
| Y | function-level+mock+実runner改変STOP(API前に停止) | なし | **¥0** | `cost_log.jsonl` 146行のまま |
| Z | `--stages kp --mode real`(Redundancy QA 1 call) | `gpt-6-luna`(OpenAI Responses) | **¥0.0596** | `cost_log.jsonl`の増分(5.6802→5.7398) |
| Z | gate〜page_verify、改変STOP、`--regenerate-stage part2_cand_b1b`拒否 | なし(API前に停止/既存音声検査) | ¥0 | spent_jpy 5.7398のまま、cost_log 39行のまま |
| 全体 | | | **約¥7.45**(上限¥30の約25%) | |

反省(再発防止): X `--stage tts` は a2 の Full Story TTS を再生成した(runnerが`tts`でa2を再実行する仕様。既存TTSが有効でもキャッシュ再利用しない経路)。事前に`--only-segments`で絞るか、`--stage assemble/player`のみで足りるかを確認すべきだった。`--budget-jpy` は累計(コピーした旧usage含む)判定のため、小さい値にしても完了後にしか止まらない。
