# EVIDENCE_PLAN_01 runtime evidence の取り方(計画。本委任では実行なし・費用JPY0)

不変条件: unit test PASS=Production実行済みの証拠ではない。実行証拠は「Production正式経路が、実際にM1/F1を呼び、その記録が残る」ことで取る。`PRODUCTION_WIRED` は全項目が揃うまで宣言しない。

## 1. 「到達・実行」証拠(layer_invoked)
- M1/F1の呼出ごとに、ASRログ(`cls.connected_speech_info` と attempt/telemetry)へ **`m1.layer_invoked=true/false`・`f1.checked=true`・`f1_all_diffs`・`f1_residual`・判定結果・経路ラベル(初回/減速後/P2/S1/S2/fallback)** を残す(M1_WIRING_DESIGN_01 §4。OPEN-328の観測性不足=「推測が必要」を解消)。
- 進行中のFamily X Coffee run(委任_03管轄)のASRログに上記が出れば、「Production正式初回経路で到達・実行した」証拠になる(受理事例の有無とは独立)。**Coffee runのファイルを本委任では編集・書込しない**(委任_03が配線を入れた後に、出力されたログを読取りで確認)。
- 到達証拠が取れる場所: 初回 / Std減速前 / Std減速後(`_post_slowdown_cascade_rescue`) / Adv / retry / fallback(`force_secondary`)/ dialogue / point_headings_aoede。実行されたものだけ「実行済み」と書き、未実行は「未実行」と明記。

## 2. M1「受理」事例が自然発生しない場合
- Production runで `ASR_VALIDATION_UNCERTAIN` かつ同音綴り受理、という状況は稀(census Aでも連結発音PASSは10/674)。自然発生を待たない。
- 代替(費用0): 既存の実ASR転写(er069 results_02等)をProduction関数へそのまま通す **replay**(`val.classify_asr_match`+配線後のcascade関数、ASR呼出をスタブ化)。これは「実装が動く」証拠であり、「正式経路で発火した」証拠とは区別して報告する。
- 代替(有料・要承認): 短clip数本を正式経路(`evaluate_attempt_with_cascade_detail`)でTTS→ASRする。見積はCOST_ESTIMATE_01。**OOV扱い(UDR-1)が確定するまで実施しない**。

## 3. 経路別の証拠の取り方
| 経路 | 方法 |
|---|---|
| 初回(Std/Adv) | Coffee run等の正式生成ログの `layer_invoked`(読取りのみ) |
| Std減速後 | `_post_slowdown_cascade_rescue` 経由のログ行(経路ラベル `post_slowdown`)。自然発生しなければreplay(転写固定)で関数到達のみ証明し、「減速後の実生成では未確認」と明記 |
| Adv | Adv生成ログ(Coffee run Adv)。Adv assemble Gate BLOCK中は未生成=未確認として報告 |
| retry/fallback | 既存HR queue・attempt_historyにfallback実績があれば転写を再投入。新規生成は不要なら行わない |
| dialogue / point_headings_aoede | `segment_id` 未渡し経路でM1が呼ばれることを、スタブASRでの単体呼出で確認(実生成なし) |

## 4. model_id・routing
- 有料ASRを使う場合のみ記録: TTS `model_requested`/`model_version`(例 er069 cost_02: gemini-3.8-flash-lite-tts)、ASR=OpenAI(gpt-4o-transcribe系のactual model_id)・Azure STT。実際のmodel_idは応答メタから取得し、推測で書かない。本委任ではAPI呼出0のため記録対象なし。
- 使用モデル名/最新か/理由(PM_GOVERNANCE 25節): 本委任は有料推論なし。判定はすべて決定論的ロジック(LLM不使用)。

## 5. 既存品質Gate・retry上限の維持証拠
- 差分レビュー: 変更ファイルに `max_same_signature` 等の上限値・閾値・Gate関数の差分が無いこと(`git diff` で確認)。
- 実行時: retry回数がM1/F1導入前後で上限内であること(attempt_historyの `tts_attempts_this_call`)。
