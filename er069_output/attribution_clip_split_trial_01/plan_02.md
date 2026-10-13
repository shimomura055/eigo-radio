# plan_02 (委任_02 事前登録。実行前に確定。2026-10-13)

## 目的
委任_01で交絡した「s+s融合」と「動詞の種類(said vs replied)」を分離する。長さは委任_01でR2効果なしのため2語固定。

## 設計 (84 task)
- 要因A(次語頭): s始まり(s+sあり) vs 非s始まり。要因B(動詞): s群={said, says, sighed}、非s群={replied, answered, asked}(各群3語、said/repliedは委任_01再現確認)。
- 名前: Melos 4take / Brontes 3take。level: std(減速前raw + 6%減速後slow6を既存関数で再検証)+adv。文は `<Name> <verb>.`。
- 音声数: Melos 6動詞x2level x4take=48、Brontes 6x2x3=36、計84 TTS call。観測: std 2 + adv 1 = 3obs/(名前,動詞,take) -> Melos 72 + Brontes 54 = 126 obs。
- 追加条件: Azure Phrase Listなし(Melos x said/replied、全take x 3obs=24obs)。OpenAI判定はもともとPhrase Listなし。
- 判定: 委任_01と同一(OpenAI gpt-4o-mini-transcribe -> val.evaluate_attempt / Azure+Phrase List[NAME] -> classify_asr_match / faster-whisper small参考)。
- TTS: gemini-3.8-flash-lite-tts, Aoede, Standard同期(TTS_EXECUTION_MODE=STANDARD)、Production同一Style定数。最新モデル原則の例外=比較可能性(Production同一)。model_id実測を記録。post-slowdown cascade rescueは呼ばない。

## 費用見積(実行前)
| 項目 | 数量 | 単価(出典) | 見積 |
|---|---|---|---|
| TTS | 84 call | 委任_01 L2実測平均JPY0.045/call (cost_01.json、USD0.5/6.0 per 1M tok, USD_JPY=160) | 約JPY3.8 |
| Azure STT | 126+24=150 obs x 約1.8秒 | USD1.0/h (er065 lib, Retail Prices)、委任_01 L2実測平均JPY0.081/obs | 約JPY12.1 |
| OpenAI ASR | 126 obs | text単価で計上、委任_01 L2実測JPY0.0087/obs。**音声入力単価は未確認**(過小の可能性) | 約JPY1.1 |
| 合計 | | | 約JPY17 (上限JPY25 Guardrail内) |
- 縮小順(超過見込み時): Brontes take3 -> 他動詞のadv。差分再生成/既存音声再利用: 該当なし(新規clip)。Azureは各音声・各target 1回、再実行なし。技術失敗retryは全体3回まで。
- 判定規則(事前): 分離結論は (a) s群内の動詞(says/sighed)でも非s群より有意に低い -> 「s+s融合が主因」; (b) saidのみ低く says/sighed は非s群並 -> 「said固有」; (c) それ以外/n不足 -> 「分離不能」。主指標はMelosのOR PASSとOpenAI綴り一致。
