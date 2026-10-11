# 委任_04B 報告(Trial A: 既存音声確認 / Trial B: 日英意図的誤読テスト) 2026-10-12

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04B / Trial限定・Production変更なし
詳細: `er058_output/trial_abc/TRIAL_A_EXISTING_AUDIO_01.md`、`TRIAL_B_INTENTIONAL_MISREAD_01.md`、結果 `trial_b_results_01.json`、script `er058_trial_b_intentional_misread_01.py`(`--approved-budget-jpy`必須、mock乾式後real)。
使用モデル(最新原則の例外=Production経路の測定対象): TTS gemini-3.8-flash-lite-tts[最新世代]、Primary gpt-4o-mini-transcribe、Azure Speech STT(en-US/ja-JP)、local faster-whisper medium。ASRの最新性は未確認(Fable確認)。LLM呼出0。

## 結論(先に)
- **Secondary PASSの原則自動採用は条件付きで可**: 証拠のある誤読30本でSecondary固有の原稿寄せ誤PASSは2件(2/30)、Primary NG→Secondary PASSの誤採用は1件(`ja_voi5` てんき/電気、GT未確定)。数値・否定・語形(です/でした)・長音・最小対語・ガス/カス型の濁点は、Primary/Azure/localの全てが誤読形を逐語転写しValidatorもNG(誤PASS 0)。C1(entity_like)を外しても日本語Primary NG+entity_like 4本は全てAzure NG(誤PASS 0/4)。統一フローで対照29本の誤不採用0。
- **型別の例外は必要(Secondary分岐ではなく「ASR PASSでも確定しない型」)**: 誤読44本中14本は全ASRが原稿形に転写(英語: -ed/-s脱落4/4、固有名詞綴り3/3、read/red・lead/led、parked/barked。日本語: ゴミ/コミ、スターバクス、コヒー、同音の紹介/照会)。TTSが正しく読んだのかASRが丸めたのか区別不能=未確定(要試聴)。日本語の同形異音(`会議を行った`いった、`人気`にんき)はPrimaryが`PHONETIC_MATCH`/EXACTで通過。共通ルールで防げない理由=ASR出力に発音差が現れない/LM priorが3系統で同方向に働く。
- Phrase List: EN10本で転写は無しと同一(原稿寄せの悪化証拠なし、救済効果も無し)。PHONETIC_MATCHをSecondary PASSに含めると `ja_len3`(ゆうき→Azure「雪」)が誤PASSになる(厳格集合なら防げる)。
- Trial A: Coffee part2のNG 5件で真の誤読と確定できたものは0。#2/#3/#4は偽NG(Primary ASR誤認/F-5 Validator仕様/Azure forced)の可能性が高い。#5(LR後)はPrimary PASSで採用されるがAzure・local smallが`raw bean→robbing`、未確定(要試聴)。日本語Phase 0: 統一フローで真の誤読の代理5本は全て再生成(誤採用0)、正解音声は10/15採用(現行SCG 8/15、差はg8・g7)。g8はPrimary側ASR誤認(ほぼ確定、Azure+whisper一致、Trial BでAzureは濁点を丸めない)。needs_listen 5は未確定(統一フロー・現行SCGとも採用される)。

## 実施・費用
Trial A: JPY 0(既存転写のみ)。Trial B: 事前 `COST_ESTIMATE_B_01.md`(約18.8円)→ mock乾式 → real。初回real実行はAzureで例外(cl.init_loggerが無く内部record失敗)で中断、cost_loggerをtrial_abc配下に向けて再実行(TTS/Primary結果は保持、Azure送信済み分は保守的に10秒加算)。実費 **JPY 12.52**(TTS 3.99、Azure 7.44、OpenAI ASR 1.10)。`cost_actual_B_01.json`。clipは73(要求「約80」より少ない=見積の保守性のため。実費に余裕があったが追加実行はしていない)。

## 限界・新規仕様候補
ground truthは人間試聴なし(話した形の仮定)。型ごとn=2〜5、短文のみ。1回実行(非決定性)。新規仕様候補・改善案の実装なし(ASR PASS≠発音確認の範囲拡張はFable/ユーザー判断事項として報告のみ)。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は未編集。
