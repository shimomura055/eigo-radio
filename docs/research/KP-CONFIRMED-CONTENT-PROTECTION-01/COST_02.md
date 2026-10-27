# COST_02(委任_03 実費。usage logの実測)

上限: 個別Cap ¥20(TTS再生成禁止)。案件見積300円以下・承認済みScope内=自律実行(PM_GOVERNANCE 7-7)。

| 経路 | 内容 | モデル/routing | 実費 | 根拠 |
|---|---|---|---|---|
| X Adv | study_text(再利用)/assemble/player/改変STOP | なし(`reused:True`) | **¥0** | コピーの`raw_usage_log.jsonl` 125行のまま |
| Y(y_01 + y_02) | 確定後の`--stage kp`(Redundancy QA 各3 call) | `gpt-6-luna`(OpenAI Responses) | **¥0.3268 + ¥0.3168 = ¥0.6436** | 各コピー`cost_log.jsonl`(コピー後に空にした)3行/3行、runnerの`spent_jpy`。assemble/pages/page_verify/改変STOP/regenerate拒否は追加0 |
| Z | b1b/a2 `--stages kp`(Redundancy QA 各1 call) | `gpt-6-luna` | **¥0.066**(5.7398→5.8058) | コピー`cost_log.jsonl` 38→40行。gate〜page_verify・kp_b1b再実行・改変STOPは追加0 |
| 合計 | | | **約¥0.71**(Cap ¥20の約3.5%) | |

TTS再生成: **0回**(`--stage tts`/`tts_*`/`--regenerate-stage tts_*` を一度も使っていない)。Y/Zの`gate`〜`page_verify`は既存音声の検査・組立のみ。02Bの教訓(X a2 TTS ¥7.39)は再発していない。
