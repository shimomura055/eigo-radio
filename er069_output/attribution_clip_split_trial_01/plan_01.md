# plan_01 (Phase 2 事前登録。実行前に確定。2026-10-13)

## 目的
「narrator tag clipの短さ」と「名前語末s + 次語頭s(s+s)融合」の交絡を分離し、R1(s+s回避の語選択)とR2(最小語数)がProduction判定のPASS率に与える効果を、Melos以外の名前でも測る。
Trial(Production非変更、採用判断なし)。到達上限Status = VALIDATED / REJECTED / USER_DECISION_REQUIRED。

## 設計
- 要因: 境界 {ss: `NAME said` = 語末s+語頭s / nss: `NAME replied` = s+s無し} x 長さ {L2: `N v.`(2語) / L4: `N v to him.`(4語) / L7: `N v, looking straight at the ruler.`(7語)} x 名前 x レベル {std, adv} x take 3。
- 名前: Melos / Brontes / Pelias (cmudict実測で未収録[OOV]、語末s) + Kallis(cmudict収録の語末s名=OOV寄与の分離用対照)。Melos専用にしない。
- 優先順(削る場合は後ろから): P1=OOV3名 x {L2,L7} x 2境界 x 2level x 3take = 72 / P2=+L4 = 36 / P3=+Kallis(L2/L4/L7) = 36。計144 task。
- TTS: gemini-3.8-flash-lite-tts, Aoede, Standard同期(TTS_EXECUTION_MODE=STANDARD)。Style=Production同一定数(er063 NARRATOR_FULL_STORY_ADV=PD8 / STD=PD8+A2_SLOWER)。Std は 6%減速(er008 apply_a2_slowdown、既存関数を呼ぶのみ)。最新モデル原則の例外理由=比較可能性(Production条件でのASR通過率を測るため)。応答model_idは実測を記録。
- 判定: 一次=OpenAI gpt-4o-mini-transcribe の転写を `val.evaluate_attempt`(Production同一、classify_asr_match含む)で判定。補強=Azure STT + Phrase List([NAME]) を `classify_asr_match` で判定。参考=faster-whisper small(無料)。Std は 減速前(raw)/減速後(slow6)の両方を再検証。post-slowdown cascade rescue(Azure Tier3等)は副作用のため呼ばない(=下限側の保守的な値)。
- 指標: Production判定PASS率(OpenAI)、Azure判定PASS率、どちらか一方PASS(=OR)、両方NG=HR相当、名前の綴り一致率(NAMEが転写に完全一致)。
- 解析: 長さ効果(L2 vs L7、nss内)、s+s効果(ss vs nss、L2/L7内)、交互作用。名前/take/level を層別。n不足(各セルn<4観測)なら断定しない。

## 費用見積(実行前)
| 項目 | 数量 | 単価(出典) | 見積 |
|---|---|---|---|
| TTS output | 144 call x 平均約2.4秒 x 25tok/s = 約60tok/call | USD6.0/1M tok, USD_JPY=160 (er057_tone_trial_final_build_03.py L33-34 Gemini TTS Standard)、25tok/s=er057 gen02 log実測(1142tok/45.68s) | 約JPY5.5 |
| TTS input | 約70tok/call | USD0.5/1M tok (同上) | 約JPY0.8 |
| OpenAI ASR | 216音声(raw144+slow72) | USD1.25/1M input tok, USD5.0/1M output tok (er065 lib L27-28, pricing_snapshot.json text単価)。**音声入力tokenの正式単価は未確認**(過小評価の可能性、usage画面照合要)。実token数はAPI usageで記録 | 未確認(参考: 前Trial約JPY0.03/8秒=216音声で約JPY1-4) |
| Azure STT | 約530秒(0.147時間) | USD1.0/hour (er065 lib L29, pricing_snapshot.json Retail Prices API) | 約JPY23.6 |
| faster-whisper | 216音声 | 無料(local) | JPY0 |
| 合計見積 | | | 約JPY30-40 (上限JPY100 Guardrailの範囲内) |
- 縮小順(超過見込み時): Kallis(P3) -> L4(P2) -> Std slow後Azure -> take 3->2。
- 暴走防止: gen scriptは技術失敗retryを全体3回まで、BUDGET超過/STOP検出で新規API停止、監督ループなし。
- 既存音声再利用: 該当なし(narrator短文clipの新規生成が目的)。差分再生成: 該当なし(Trial専用の新規clip)。
