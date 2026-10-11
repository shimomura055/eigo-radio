# COST_ESTIMATE_C_01 (Trial C 英語ASR比較 縮小版) 2026-10-12

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04C。ユーザー承認上限: 約40円。

| 項目 | 内容 |
|---|---|
| 課金対象 | Azure Speech STT(en-US、Phrase Listなし、1パス)のみ。単価 $1.00/音声時間 x 160円/USD = 0.04444円/秒(`er005_output/cost_baseline_01/pricing_snapshot.json`) |
| 対象 | 保存済み英語wav 32本(sha256重複除外済み): Primary NG 18本(er056のNG attempt全件)+ 現行HR queue由来 6本(短い順)+ Primary PASS対照 8本 |
| 合計音声長 | 788.6秒(内訳: NG 696.0秒 / HR 30.8秒 / 対照 61.7秒) |
| 見積(Azure) | **約35.05円**(NG 30.94 + HR 1.37 + 対照 2.74) -> 承認上限40円以内。STOP不要 |
| 他の課金 | なし。OpenAI/Gemini/LLM/TTS呼出0(新規TTS生成なし)。ローカルfaster-whisper small/medium=CPU無料。Primary(OpenAI)転写・Azure PL付き転写は既存の保存値を再利用 |
| 安全装置 | `--approved-budget-jpy 40`必須。実行中、累積+次ファイル見込が40円を超える場合は停止(`cmd_azure`)。送信秒数ベースで失敗分も保守的に計上 |
| 書込先 | `er058_output/trial_c/`のみ(Production telemetry/queue/attempt_history/Master Storeへ書込なし、`cl.record`を呼ばないAzure関数を使用) |

使用モデル(PM_GOVERNANCE 25節): Azure STT en-US / OpenAI Primary ASR は**測定対象=Production同一の例外**(評価対象そのもの)。ローカルASR=faster-whisper small/medium(参考列、LLMではない)。新規LLM/TTS呼出なし。
