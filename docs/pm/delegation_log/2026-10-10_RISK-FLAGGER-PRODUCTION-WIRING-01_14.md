# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_14 (OPEN-251修正 + L3 coffee_prices audio + 追加証跡2件)

実行日: 2026-10-10〜11 / checkout=main / 使用: Sonnet 5.5 (実行層)。

## 1. OPEN-251修正
- commit 8ba79fdc: er009 PRICING_USD_PER_Mへ ("openai","gpt-6-luna"): (0.10, 0.01, 0.50) 追加(pricing_snapshot.json登録値転記)。
- 新規test er009_n1_routing_governance_10_pricing_table_open251_test.py 4件 + 既存関連(coverage/gpt6_wiring)計24 passed (.venv)。
- Routing contract登録のOpenAIモデル: gpt-6-luna(追加済) / gpt-6-astra(W-1専用の別集計経路、本表を使う経路では呼ばれないため追加せず)。gpt-6.1-solはRouting未登録。未知modelはfail-closed維持。
- 環境メモ: グローバルpy -3.14にはscipy等が無く、テスト/runnerは .venv/Scripts/python.exe で実行(scipy,soundfileをグローバル3.14へpip installしたが本タスクの成果物には影響しない)。

## 2. L3 audio (Production正式経路, --tts-backend speech_metadata_flash_lite, budget 200)
- 初回(前委任)=OPEN-251でSTOP。本回=1回目で EXIT=0 (技術retry/再修正なし)。
- stage発火: scaffold OK(A2/B1 KP選定 db_hybrid, CANONICALIZATION_PASS) -> rf_guard(三者sha一致, RF再実行なし) -> tts OK -> assemble OK -> player OK。
- 三者照合: a2 / b1b とも scaffold_sha == source_sha == Queue sha, match=true, action=verified (a2: ...a618236, b1b: ...3e1d23)。
  注: a2は derived_from_advanced_sha 不一致の観測のみ警告(記録のみ・STOPに使わない設計。recorded 2c627b38... vs current b1b 5e8979df...)。要Fable確認(OPEN候補)。
- 技術QA: a2 21 segment / b1b 25 segment 全て status=OK, asr_verified 全件True, clipping 0, KP source gate PASS (5/5, 両level), kp_scaffold_status OK。
  ASR初回不一致で自動retry(attempt2で解決)=a2: japanese_title/comment_3/full_story_part1/full_story_part3/KP2日本語意味 (5件、attempt2=PHONETIC/NORMALIZED/NUMERIC_EQUIVALENCE_MATCH)、b1b: KP4 "cause a stir"(english/phrase_repeat、初回ASR 'causister'=TTS_FAILURE分類 -> attempt2 NORMALIZED_MATCH)。disfluency判定: a2 6attempt, b1b 13attempt(flagged 0)、repetition QA 各3(flagged 0)。b1b KP 8音声はmaster audio reuse。
  headroom: a2 peak 1.0054 -> safety valve適用(scalar 0.9747, peak 0.98)、b1b 0.8227(未適用)。
- 完成音声(gitignore *.wav, 所在のみ):
  - a2: er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01/a2/assembled/Family_X_Audio_A2_COFFEE_PRICES.wav (320.96s, 48kHz stereo, sha256 e914a809...7686)
  - b1b: er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01/b1b/assembled/Family_X_Audio_B1_COFFEE_PRICES.wav (303.0s, sha256 a6a566a7...0ac7)
  - player: er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01/player.html
- manifest相当: 専用manifestファイルは存在せず、entry_point.json / scaffold_run_summary.json / {a2,b1b}/run_summary_{tts,assemble}.json / {a2,b1b}/audit/{tts_generation_results,timeline}.json が該当。
- 費用(audio runner実測): 15.80円 = openai 3.55 + gemini_batch(Gemini TTS) 8.08 + openai_asr 4.16。wall clock: 22:11 -> 23:51 JST (約100分、TTS segment毎の直列実行)。

## 3. 追加証跡
- (a) entertainment runner --stage standard: 別copy dir er019_output/coffee_prices/run_l3_01_stdregen(元run_l3_01のa2/Level出力を汚さないため)。ledger/brief/R2 U-1再利用 -> Standard再生成(a2 sha 6f5e8e53 -> c582868e) -> Std RF status=OK issues=4 queue_saved=True (article_id=coffee_prices__run_l3_01_stdregen) -> Queue追記 (review_queue/post_en/index.jsonl +1行)。費用 1.49円(差分)。証跡 stdregen_stdout.log。
- (b) --stage tts 単独: 別out dir er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01_ttsonly へ(scaffold済みartifact copy、b1b narration/assembled等を除去、raw_usage_log新規)。source=元run_l3_01(article_id一致)。rf_tts_guard.json[b1b]: match=true, mismatch_reasons=[], action=verified, rf_status=null(RF未実行) -> 三者一致でRF再実行なし。TTS費用 4.09円(gemini_batch 2.87 / openai_asr 1.18 / openai 0.03)。※guardのrecordにreason=matchキーは無く、match=true/action=verifiedで表現。

## 4. 費用
- L3累計: 前回89.05 + audio 15.80 + (a)1.49 + (b)4.09 = 110.43円 (L3上限350内、合計600に対する残額 489.57円、META用250円以上確保)。本委任支出 21.38円 (上限200内)。

## 5. Gate 3 Runtime
- audio stage(scaffold/tts/assemble/player)、三者照合、技術QA、Std再生成経路、tts単独経路: 本委任で充足。残(Sonnet側見解): CURRENT_SPEC更新のみ + a2 derived sha警告の扱い判断(Fable)。
- STOP該当: なし(OPEN-251解消済み)。
