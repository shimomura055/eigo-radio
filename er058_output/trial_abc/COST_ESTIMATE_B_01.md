# COST_ESTIMATE_B_01(Trial B 実行前見積、2026-10-12)

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04B。承認予算 JPY 20(ユーザー承認2026-10-12)。為替 USD/JPY=160(既存集計と同一)。

| 項目 | 数量 | 単価(pricing_snapshot.json / 公称) | 見積(平均3.0秒/clip) |
|---|---|---|---|
| TTS gemini-3.8-flash-lite-tts(Production同一) | 73 clip(EN 37 + JA 36) | output $6/1M tok(25 tok/s)、input $0.5/1M | 約5.96円 |
| Azure STT(Phrase Listなし、全clip) | 73 clip x 3.0s = 219s | $1.00/音声時間 | 約9.73円 |
| Azure STT(EN Phrase Listあり、misread 10 clip) | 10 clip x 3.0s = 30s | 同上 | 約1.33円 |
| Primary gpt-4o-mini-transcribe | 73 clip x 3.0s | 概算$0.003/分(尺換算) | 約1.75円 |
| local faster-whisper medium | 73 clip | 無料 | 0円 |
| **合計(中心値)** | | | **約18.8円**(`--mode estimate`出力) |

- 予算 20円 以内の見込み(中心値18.8円)。尺が平均3.5秒に延びると約21.9円となるため、実行スクリプトは**TTS完了後に実尺で残りASR費を再予測**し、超過見込みなら (1) Phrase List群(約1.3円)を省略、(2) それでも超過ならASR前にSTOPする。ASR中も毎件、累計が予算を超えたら即STOPする。
- clip数: 日英合計73(誤読44 + 対照29)。「約80」より少なくしたのは、20円枠を守るため(8-3-Aの80クリップ案は尺3.0sで約20円となり余裕が無い)。
- Azure単価は送信WAV尺課金のSnapshot値(F0無料枠の可能性は未確認のため上限側で計上)。OpenAI ASRはAPI応答のusageを取得しないため尺換算の概算。
- 実費は実行後 `cost_actual_B_01.json` に記録。
- 最新モデル原則(PM_GOVERNANCE 25節)の例外: TTS/ASRは「Production経路の測定対象」のため、現行Production同一モデル(TTS gemini-3.8-flash-lite-tts[最新世代]、Primary gpt-4o-mini-transcribe、Azure Speech STT、faster-whisper medium)を使う。
