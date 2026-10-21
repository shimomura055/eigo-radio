# TRIAL_DESIGN_01 (事前登録・実行前に固定。以後変更しない)
管理ID: FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01 委任_01 / 2026-10-21 / 性質: 限定Trial(ASR再実行のみ、TTS 0)

## S0 確認事項
- STOP確認: `tools/stop_scope_check_01.py --managed-id FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01` rc=0 (stop=false)。
- 本日(2026-10-21 JST)既使用: `docs/pm/tools/daily_dev_cost_01.py --date 2026-10-21` total_jpy=275.17。本Trial見積約JPY1〜3、T-3 Guardrail=JPY30。
- git status 変更行数(着手時): 1136 (無関係な既存差分。本Trialは明示addのみ)。
- T-0: 委任文逐語 `docs/pm/delegation_log/2026-10-21_FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01_委任_01.md` (index=209で抽出、原文区間含む)。ユーザー原文 `..._USER.md` (本文2956文字, sha256(本文のみ)=3c9ae4b0e513e1fe0b077c8a53519f58ac5995e2e247e676afef1a292115bf77)。
- 対象wav: `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/a2/narration/kp4_en.wav` sha256=675cd6b1aec9865acbdb411b588672d9cc963b936bb4a35bb2d8158cb4172186 (tts_generation_results.json key_phrases.4.english.sha256と一致、duration 1.3秒)。読取専用、Trial out_dirへコピーして使用(*.wavはgitignore)。
- canonical: `tts_generation_results.json` key_phrases.4.english.canonical_text = "take part"。
- Phrase List(事前確認): Production同一呼出 `pronun_ledger.get_hint_for_text("take part", min_confidence="low")` = [] (空)。→ 空のためPhraseListGrammar未作成・setWeight未実行(`er006_secondary_asr_01.py:111-117`の `if phrases:` 内)。AZURE_PHRASE_LIST_WEIGHT=2.0定数は存在するがPLが空の間は送信されない。= 既存Production設定どおり。実行時にharnessがsetup.jsonへ実測を記録する。

## キャッシュ/重複防止機構の確認(コード)
- Primary: `er006_asr_provider_routing_01.transcribe`→`_transcribe_openai_mini`(同:93-103)は毎回`client.audio.transcriptions.create`を直接呼ぶ。転写cache・wav sha key再利用・Master Store参照は無い。OpenAI側にidempotencyは付与していない。→ 各回が実際にAPIを呼ぶ。
- Secondary: `_AzureShared`は`SecondaryCache`(key=sha,engine,lang,phrase_hash)経由(`er006_secondary_asr_01.py:~700`, `er078_asr_unified_judge_01.py:229-243`)。cacheは`evaluate_attempt_with_cascade_detail`呼出ごとに新規(`actx.get("cache") or (_RUN_CACHE if ... else SecondaryCache())`)で、`begin_secondary_run()`(run単位共有cache)を呼ばない限り呼出間で共有されない。harnessは`_RUN_CACHE is None`をassertし、各回のaudit `adapter.cache.calls/hits`を保存する(期待 calls=1, hits=0)。
- Whisper: `_MODEL_CACHE`はモデルのみ(転写はcacheしない)。
- 共有ログ書込: `evaluate_attempt_with_cascade`(wrapper)はHR queueへ書くため使わず`_detail`を直接呼ぶ。cost loggerはTrial専用`raw_usage_log.jsonl`へ向ける。slot=1/total_slots=4(Production KP primary段と同一)でis_last_slot=False。実行前後で共有ファイル(ledger/manifest/attempt_history/review_queue/telemetry)のmtime・hashを比較して無変更を確認する。

## 判定方式
- Production判定関数を呼ぶ(コピー・改変なし): `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail(canonical, primary_text, [], wav, language="en-US", ledger_phrases=<上記PL>, cascade_enabled=True(FEATURE_FLAG), force_secondary=True, enable_non_latin_cascade=True, enable_connected_speech_equivalence_layer=False, segment_id=None, attempt_ctx=build_attempt_ctx(1,2,slot_offset=0,total_slots=4,max_len=19))`。force_secondary=Trueは既存のfallback音声向け「Primary PASSでもSecondary許容集合PASSを必須」機構で、本Trialの「両方PASS方式」と同一意味。Primary=`routing.transcribe(wav,"en-US",prompt=KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)`(`er003_v1_repro01_main_generate.py:~771`のKP呼出と同一)。
- 保存: Primary転写・判定label・Secondary(Azure)転写・label・accepted・両方PASS総合(`dual_verified`と`primary.passed AND secondary.accepted`の両方を保存し一致確認)・reason・audit_record全体・OpenAI応答(usage/_request_id/elapsed)・Azure秒数/経過・cost。Secondaryが呼ばれなかった回があれば補足で独立に1回呼ぶ(`secondary_supplement`)。
- Whisper: `er008_disfluency_qa_18.transcribe_verbatim(wav,"en","small")`(吃音QAと同設定: small/cpu/int8/word_timestamps、seed指定なし)。`val.classify_asr_match`+`_step_alternate_pass`でPASS相当/NG相当。総合判定には含めない。直列10回。
- 並列: Primary+Secondaryの10セットは同時3並列。Whisperは直列。cooldown無し。
- 費用: OpenAI gpt-4o-mini-transcribe $1.25/M in, $5.0/M out(pricing_snapshot.json)、Azure S0/S1 $1.0/音声時(同)、JPY=160/USD(er078_asr_unified_judge_01.py:80)。Azure概算はProduction式`ceil(秒)/3600*1.0*160`と、正確秒数式の両方を併記。
- 禁止の再確認: 認識条件・判定基準・Promptを途中変更せず、結果が期待と異なっても再試行しない。
