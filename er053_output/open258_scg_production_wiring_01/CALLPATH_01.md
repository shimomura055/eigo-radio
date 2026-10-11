# CALLPATH_01 (OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01 委任_01, 2026-10-11)

日本語segmentのASR検証を呼ぶProduction経路の全数調査(Grep: `evaluate_attempt_ja_with_cascade` / `classify_ja_asr_match` / `ja_secondary` / `routing.transcribe(...ja-JP)`)。
結論: 日本語ASR検証の本番呼び出しは**4か所**で、すべて同じ関数 `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade`(→`_detail`)に集約される。SCGはその1関数内(L128早期return直前)にあるため、4か所すべてで自動的に動く。

| # | 呼び出し元(ファイル:行) | 経路 | SCGが通るか | attempt消費 | 証跡記録 |
|---|---|---|---|---|---|
| 1 | `er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict` (language=ja) L363 | 初回attempt・retry(attempt 1..max_attempts) | 通る | SCG PASS=そのattemptでOK(再生成不要)。NG/UNAVAILABLE/不実行=従来の再生成へ(attempt+1) | attempts_log[].scg_info、save_tts_attempt_audio metadata、OK return `scg_info` |
| 2 | `er003_v1_n3_01_tts_generate.generate_a2_japanese_with_fallback` fallback(minimal instruction) L540 | fallback attempt(標準2回NG後の3回目) | 通る(標準経路は#1経由) | 同上。fallback NGなら従来どおりSTOPPED(合計3回上限不変) | fallback_attempts_log[].scg_info、metadata、r["scg_info"] |
| 3 | `er003_v1_sing01_voice01_generate.generate_charon_japanese` 標準 L515 | B系/B1日本語 標準attempt(標準2回) | 通る | 同上 | attempts_log[].scg_info、metadata |
| 4 | 同 fallback L560 | fallback attempt | 通る | 同上 | fallback_attempts_log[].scg_info、metadata |

上記4関数へ流れ込む上位経路(すべてSCG対象、個別改修不要):
- A2日本語(japanese_title/meaning_N/comment/KP meaning/support text): `n3.generate_a2_japanese_with_reading_safety` -> `generate_a2_japanese_with_fallback` -> (#1 + #2)。Family X audio runner(`er019_family_x_audio_production_runner_01`)・Human Review Lock再生成/resume(`er011_human_review_lock_01` L941/959/1045)・scaffold(`er003_v1_b1_scaffold_audio_01_generate` L321 = #1)・crosslevel/a2_audio runner(#1)もすべてこの関数群を呼ぶ。
- B/B1日本語: `voice01.generate_charon_japanese[_with_reading_safety]` (#3 + #4)。
- regeneration/resume: 新規に`generate_*`を呼び直すだけで検証は同じ関数(#1〜#4)。attempt上限(PRODUCTION_MAX_TTS_ATTEMPTS=3=標準2+fallback1)・Human Review Lock(`guarded_generate`)・budget guardは無変更。

意図的にSCGを通さない/該当しない経路:
| 経路 | 理由 |
|---|---|
| 英語(language=en)全経路(`er006_secondary_asr_01`、repro01 en分岐、crosslevel_common L338、sing01_news_tail_fix、point_headings_aoede、er012_b_family_voices) | 日本語専用機能。英語ASR仕様は変更しない(test: english path never touches SCG) |
| `er003_audio_tts_asr_safety.validate_japanese_short_segment_match` | 旧prefix方式の関数。Production呼び出し元なし(定義とTrial scriptのみ) |
| Local Rewrite(`er020_*`) | 英語TTS role専用(日本語参照0)。STOPPED後の回復であり、SCGと干渉しない |
| Trial/検証script(`er007_ja_cost_latency_projection_01`、`er008_n8_revalidation_15`、`verify_ja_cascade_production_on` 等) | Production経路ではない(`evaluate_..._detail`を直接呼ぶ解析用、実TTS再生成なし)。SCGが有効でもAzure課金は呼び出し側の実行時のみ |
| ASR_VALIDATION_UNCERTAIN(entity_like/濁点)経路 | 従来のCascade(Primary#2->Azure#1->#2)のまま。SCGはTRUE_CONTENT_MISMATCH専用の別分岐 |
| cascade_enabled=False | 従来どおりclassifyの結果をそのまま返す(SCG不実行) |

仕様整合(初回/retry/fallback/regeneration):
- SCG PASS: そのattemptで`verified=True`(length_ok等の呼び出し側ANDは従来どおり)。TTS再生成attemptは増えない(1 attempt=Azure最大1回)。
- SCG NG/UNAVAILABLE/不実行: `stop_retrying=False`・classification=TRUE_CONTENT_MISMATCHのまま=従来の再生成/fallback/STOP。Human Review新規投入なし(`_log_human_review`はSCG経路で呼ばれない)。
- fallback attemptでも標準attemptと同じ判定(test: N3FallbackScgTests / VoiceCharonJapaneseScgTests)。

既知の注意点(仕様変更せず報告のみ):
1. 呼び出し側の `length_ok`(Primary転写長 <= len(text)+max_extra_chars)はSCG PASS後もANDで効く。Primary転写が極端に長い場合はSCG PASSでも不合格(従来どおり再生成)、このときAzureは無駄に1回呼ばれる(約0.16円)。
2. SCG PASS時の `asr_text` キーは従来どおりPrimary(OpenAI)の転写のまま(既存キー不変の方針)。Secondary転写全文は`scg_info.secondary_transcript`にある。
3. 既存の否定検出(`protected_check_ja`)は「縛られず->縛られる」(ず)を否定差として検出しない(実測: negation_mismatches=[])。このためg12型はSCG対象になるが、Phase 0でAzureが「縛られる」と転写してNG。この否定検出範囲は既存設計であり今回は変更していない(安全条件を緩めてはいないが、Secondaryが原稿寄りに丸めた場合の最後の砦が既存否定検出のみである点は残余リスク)。
