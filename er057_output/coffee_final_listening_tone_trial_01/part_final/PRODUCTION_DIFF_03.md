# PRODUCTION_DIFF_03(委任_03、Production正式経路との差異一覧)

本最終試聴版はTrial/試聴用の隔離成果物であり、Production正式経路の成果物ではない。差異:
| 項目 | Production正式経路 | 本Trial(委任_03) |
|---|---|---|
| 生成経路 | runner(`er019`)→`generate_a2_segment_with_slowdown`/`generate_family_x_b1_segments` | Trial専用 `er057_tone_trial_final_build_03.py`(Production runner不使用)。Styleは各ユーザー選択(F5等)、Productionの承認Style(F1.5/E2_UPBEAT/J2等)ではない |
| TTS実行方式 | Batch(既定) | Standard同期(DEV、PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01) |
| model | gemini-3.8-flash-lite-tts | 同一(応答model_version実測: gemini-3.8-flash-lite-tts)。最新世代TTS(最新原則上の例外なし) |
| 発音hint(Pronunciation resolver / Ledger) | Style末尾にhint追記 | **省略**(F5 Style逐語を優先。KP英語・本文とも) |
| 原稿 | 確定原稿に `tts_safe_news_en` 適用(同一) | 同一(parts.json原稿を逐語使用、`tts_safe_news_en` 適用、Std part2はLR前の元原稿・`data from the United States` 不使用) |
| 内容QA | Primary→cascade/Secondary/意味等価/LR/minimal fallback/Human Review | **Primary ASR(gpt-4o-mini-transcribe)+既存validator `val.evaluate_attempt`(segment_id=role)+長さ条件のみ**。Secondary ASR・Local Rewrite・minimal fallbackなし。validator telemetryはTrial内メモリへ退避。disfluency/repetition QAは未実行 |
| 再生成ループ | Production retry機構(上限・cool-down等) | 同一Promptで最大2回まで(実際は全6 segment初回合格、再生成0回) |
| 6%減速 | `generate_a2_segment_with_slowdown`内(status=OK後) | 同一処理(`apply_a2_slowdown`)をOK後に適用。減速後再検証はPrimary-only参考記録(OPEN-270の外側ループ未実装は維持) |
| assemble | `stage_assemble_family_x_{a2,b1}`(Gate・run dir書込) | Trial assembler(`er057_tone_trial_final_build_03_asm.py`): runnerの`apply_family_x_*_gain`/`build_family_x_*_timeline`/`asm.assemble_with_timeline`/`asm.apply_headroom_safety_valve`を同一呼出し。**既存音声のみ組立てで既存完成版wavとbyte-identical(sha256一致、Standard 8f085ef4…、Advanced 4b2a30d7…)を確認**。Audio Validation Gate(`verify_episode_audio_validation_gate`)は未呼出(run dir依存)で、同等チェックを`qa_03.json`に計算 |
| gain正規化target RMS | (preview+part1)/2 | 同一式。ただし素材が変わったため target_rms は Std 0.10621 / Adv 0.11604(既存完成版 0.09932。Std previewがP2で無加工RMSが高く、Part1がF5のため) |
| Master Store | shell/KPを登録・再利用 | **未登録**・未参照書込(shellはTrial生成のA5/B5をそのまま使用、Master Storeへ書込なし) |
| manifest/telemetry/human_review_queue/attempt_history/ledger/cost_logger | 書込あり | **書込なし**(sha256前後一致を確認) |
| KP(Advanced)英語 | - | **K2未適用**(Advanced KPフレーズはStandardと異なりK2音声未生成。既存承認音声のまま) |
| shell(A5/B5)のtrim | Master Store登録時にtrim | 01A生成のraw wavをそのまま使用(trim処理の差。前後無音は0.1〜0.44秒) |
| Gate記録・Human Approval | あり | なし(Trial)。Production採用は人間ユーザーのみ |
