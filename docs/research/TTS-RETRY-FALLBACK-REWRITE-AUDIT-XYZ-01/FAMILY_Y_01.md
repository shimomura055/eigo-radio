# FAMILY_Y_01: Family Y 正式Production — Retry・Fallback・Local Rewrite・Human Review 仕様棚卸し(read-only、API 0、JPY 0)

管理ID: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Y / 2026-10-26。到達上限Status=調査完了(AUDITED)。コード・Prompt・SSOT・run dirの編集なし、有料API・音声生成なし。
構造化データ: `family_y_01.json`(同dir)。共通核(er003_*/er020/er011)の正本記述はX Agent。本書は『Yがどの共通関数をどの引数で呼び、その結果LR/Fallbackが有効か無効か』を事実として記す。

## 0. 読み方・語彙・方法
- 表の各セルは事実(ファイル:行・文書・run出力)のみ。技術的見解は§10『所見(事実ではない)』に分離。根拠が見つからないものは『理由不明・記録なし』と書く。
- 語彙: **通常TTS上限**=同一設定での最大試行(品質NG n回+技術エラー別枠m回)/ **Retry**=品質NG契機の同一設定再TTS / **Fallback**=設定切替を伴う再TTS(F-Style,F-Model,F-Voice,F-Prompt,F-Tech)/ **LR**=本文局所書換え後の再TTS / **HR**=Human Review queue登録+Lock / **STOP**=run停止。
- 『3回NG』は『通常n+Fallback m+LR後k=総N』で書く。
- **Yは新規のretry/cooldown/LR/Fallbackコードを一切持たない**(Grep `cooldown|600|time.sleep|max_attempts|attempt_hook|prior_generations|local_rewrite` in er121_family_y_audio_01.py / er121_family_y_runner_01.py / er121_family_y_structure_01.py: 該当は er121_family_y_audio_01.py:708 のY Gate検査1件のみ)。『最終attempt前10分cooldown』の実装は共通 er020_tts_retry_local_rewrite_01.py:57-93(COOLDOWN_SECONDS=600.0)で、呼出点は news_tail_fix.py:149 / voice01.py:156 / crosslevel_audio_02_common.py:200 / repro01.py:339。Yの `attempt_hook`(er012_b専用)・`prior_generations`(共通関数の内部引数)の指定はない。
- Yの『有効/無効』を決める唯一のスイッチは `enable_connected_speech_equivalence_layer`(=`er020.connected_speech_enabled_for(segment_id)`の戻り値)で、cooldownとLRが連動する(er020:188-193)。Yは本文・topic_intro・Adv支援文の呼出し7箇所でこの関数の戻り値を渡す(er121_family_y_audio_01.py:386,415,454,467,487,562,602)。
- 共通の技術エラー別枠: 技術エラー別枠: 各TTS呼出し直後に最大1回の即時再呼出(common._call_tts_with_retry(max_retry=MAX_TTS_TECHNICAL_RETRY=1, sleep_fn=None=待機なし): er002_common.py:703-718, er003_b1_p4_audio.py:61, er003_b1_p9a_audio.py:138)
- 共通のcooldown: 600秒の実sleepを『通算最終attempt(max_attempts>=3 かつ attempt==max_attempts)の直前』にだけ入れる(er020_tts_retry_local_rewrite_01.py:57-93 COOLDOWN_SECONDS=600.0)。有効化はenable_connected_speech_equivalence_layer(=connected_speech_enabled_for)で連動
- 共通のHR/Lock: ER-011 Lock=<level>/audit/review_lock_state.json(record_outcome: er011_human_review_lock_01.py:357-)。HUMAN_REVIEW_REQUIRED後は同一文面で0 API(check_before_generation:299-)。解除=approve_regenerate(:474, REGENERATE_APPROVED、次の1回のみ)またはrecord_human_approval(HUMAN_APPROVED)。通算 MAX_CUMULATIVE_TTS_ATTEMPTS=15(:68)超でも同Lock
- 共通の最終NG後のrun挙動: TTS段のNG(STOPPED)ではrunは停止しない(tts stage rc=0、E-1で実測)。後段 stage_gate が y_style_gate BLOCKでYE2EStop rc=2(er121_family_y_runner_01.py:1017-1021)、stage_assemble が assemble_level非OKでYE2EStop(同:1030-1038)。assemble_levelは Audio Validation Gate(load_y_sources→er003_v1_n3_01_assemble.py:474-)でSTOPPED/未承認segmentをBLOCK

## 1. Y音声部位の完全一覧(Std/Adv別、生成関数、呼出引数)
正式Productionで音声化される部位は、`generate_y_b1_segments`(er121_family_y_audio_01.py:429-513)/`generate_y_a2_segments`(:516-620)の呼出しで確定する。Y本文8 segment(`Y_SEGMENT_IDS`: er121_family_y_structure_01.py:34)=y_lead / y_intro_1 / y_voice_1 / y_intro_2 / y_voice_2 / y_intro_3 / y_voice_3 / y_closing(Tension+Closing)。Voice割当=narrator(`p9a.VOICE_NAME`)+Voice 1〜3=Algieba/Zephyr/Schedar(`FIXED_VOICE_SLOTS`: er121_family_y_structure_01.py:53[HEAD aedbb88a9])。**注: 作業木には他Agent(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01)の未commit変更があり、Voice 1がAlgieba→Puckへ変更中(structure_01.pyは+8行ずれ、audio_01.pyはコメント1行のみ)。本書の行番号はHEAD基準で、runtime証拠はすべてAlgieba時点。Voice変更はRetry/Fallback/LR規則に影響しない(Voice名のみ差替え)。Comment 4・In One Lineは無い。

| ID | レベル | 音声部位 | 生成関数(呼出行) |
|---|---|---|---|
| Y-B-00 | Adv(b1b) | Intro / Notification1-3 / Outro(固定mp3) | TTSなし。p9a.load_and_resample_to_target(INTRO/NOTIFICATION/OUTRO_MP3_PATH)(er121_family_y_audio_01.py:773-775) |
| Y-B-01 | Adv(b1b) | 共有固定英語9: welcome / preview_intro / key_phrases_intro / full_story_intro / num_one〜num_five(*_charon.wav) | shared_narration.ensure_all_shared_narration_b1 → ensure_fixed_english_segment → store.get_or_generate(..., voice01.generate_charon_english)(呼出 er121:440 / er006_audio_cost_pilot_02_shared_narration.py:220-233, 271-283)。@guarded_generate('en') |
| Y-B-02 | Adv(b1b) | topic_intro('Today's topic is {title}.') | er003_v1_sing01_voice01_generate.generate_charon_english(@guarded_generate('en'), :49)。呼出 er121_family_y_audio_01.py:450-456 |
| Y-B-03 | Adv(b1b) | preview / comment_1 / comment_3(Comment 2は2026-10-26承認で削除) | voice01.generate_charon_english。呼出 er121_family_y_audio_01.py:459-469 |
| Y-B-04 | Adv(b1b) | ナレーター本文5: y_lead / y_intro_1 / y_intro_2 / y_intro_3 / y_closing(Tension+Closing) | news_tail_fix.generate_news_narration_wide_margin(@guarded_generate('en'): er003_v1_sing01_news_tail_fix.py:62-63)。呼出 er121_family_y_audio_01.py:483-490 |
| Y-B-05 | Adv(b1b) | Voice本文3: y_voice_1(Algieba) / y_voice_2(Zephyr) / y_voice_3(Schedar) | news_tail_fix.generate_news_narration_wide_margin(同上)。呼出 er121_family_y_audio_01.py:483-490(with tts_voice(voice)) |
| Y-B-06 | Adv(b1b) | 本文chunk: y_<segment>_k<j>(segmentが空行区切り2段落以上のときのみ。現行Y契約は各Voice 1段落) | news_tail_fix.generate_news_narration_wide_margin を chunkごとに呼出(_generate_y_body_segment_chunked: er121_family_y_audio_01.py:373-395) |
| Y-B-07 | Adv(b1b) | Key Phrase英語 kp{rank}_en(3件。末尾の再掲phrase_repeatは新規生成せず同一entry複製) | xr._generate_key_phrase_segments_b1 → _kp_english_generate_fn → er104_kp_vote_reuse_01.ensure_key_phrase_english_component_x_vote → store.get_or_generate(repro01.generate_key_phrase_component_verified(vote_pass_required=True))(呼出 er121_family_y_audio_01.py:503; er019_family_x_audio_production_runner_01.py:1661-1676; er104_kp_vote_reuse_01.py:287-) |
| Y-B-08 | Adv(b1b) | Key Phrase英語解説 kp{rank}_explanation_en(3件) | xr._generate_key_phrase_segments_b1 → generate_key_phrase_explanation_en_verified → repro01.generate_narration_snippet_verified_strict(er019:1205-1219; 呼出 er121_family_y_audio_01.py:503) |
| Y-S-01 | Std(a2) | 共有固定英語9(welcome / preview_intro / key_phrases_intro / full_story_intro / num_one〜num_five) | shared_narration.ensure_all_shared_narration_a2 → ensure_fixed_english_segment → store.get_or_generate(voice01.generate_charon_english)(呼出 er121_family_y_audio_01.py:548; shared:286-296) |
| Y-S-01b | Std(a2) | 共有固定日本語 point_explanation('ポイント解説') | shared_narration.ensure_fixed_japanese_segment → store.get_or_generate(voice01.generate_charon_japanese(text,p,text,max_attempts=6,...))(shared:236-243, 286-296) |
| Y-S-02 | Std(a2) | topic_intro(英語) | crosslevel_common.generate_english_segment_with_fallback(@guarded_generate('en'): er003_v1_crosslevel_audio_02_common.py:94-95)。呼出 er121_family_y_audio_01.py:556-565 |
| Y-S-03 | Std(a2) | japanese_title(日本語タイトル) | n3_tts.generate_a2_japanese_with_reading_safety → generate_a2_japanese_with_fallback(@guarded_generate('ja'): er003_v1_n3_01_tts_generate.py:819, 693)。呼出 er121_family_y_audio_01.py:567-575 |
| Y-S-04 | Std(a2) | 日本語支援文: preview / comment_1 / comment_2 / comment_3(Stdはcomment_2を維持) | n3_tts.generate_a2_japanese_with_reading_safety(同上)。呼出 er121_family_y_audio_01.py:574-584 |
| Y-S-05 | Std(a2) | ナレーター本文5: y_lead / y_intro_1〜3 / y_closing(全segmentに6%減速) | n3_tts.generate_a2_segment_with_slowdown(er003_v1_n3_01_tts_generate.py:331。本体は guarded でなく、内側 generate_english_segment_with_fallback が @guarded_generate('en'))。呼出 er121_family_y_audio_01.py:595-604 |
| Y-S-06 | Std(a2) | Voice本文3: y_voice_1(Algieba) / y_voice_2(Zephyr) / y_voice_3(Schedar)(6%減速) | n3_tts.generate_a2_segment_with_slowdown(同上)。呼出 er121_family_y_audio_01.py:595-604 |
| Y-S-07 | Std(a2) | 本文chunk: y_<segment>_k<j>(2026-10-26 Std/Adv双方承認。chunkごとに6%減速→0.2秒→連結) | n3_tts.generate_a2_segment_with_slowdown を chunkごとに呼出(_generate_y_body_segment_chunked_a2: er121_family_y_audio_01.py:398-420) |
| Y-S-08 | Std(a2) | Key Phrase英語 kp{rank}_en(3件) | xr._generate_key_phrase_segments_a2 → Y-B-07と同じ _kp_english_generate_fn(呼出 er121_family_y_audio_01.py:618; er019:2043-2085) |
| Y-S-09 | Std(a2) | Key Phrase日本語意味 meaning_{i}(3件、japanese_meaning) | xr._generate_key_phrase_segments_a2 → n3_tts.generate_a2_japanese_with_reading_safety(er019:2090-2096) |

### 1-1 呼出引数(LR関連・Style・上限)
| ID | 渡している引数 |
|---|---|
| Y-B-00 | 該当なし(音声ファイル読込のみ) |
| Y-B-01 | text=FIXED_ENGLISH_TEXTS[name]; style_prefix_override=_resolve_shell_english_style_prefix_override(name,tts_backend); tts_backend=flash-lite。enable_connected_speech_equivalence_layer/disfluency_qa/max_attempts 未指定(既定False/False/3)。Master Audio Store key一致なら生成0(再利用) |
| Y-B-02 | text=_pnap_supply(topic_text, tts_safe_number_words_en(tts_safe_en())); enable_connected_speech_equivalence_layer=connected_speech_enabled_for('topic_intro')=True; enable_pronunciation_resolver=True; style_prefix_override=_role_style('TOPIC_INTRO'); tts_backend=flash-lite。max_attempts/disfluency_qa 未指定(既定3/False)。enable_repetition_qa引数なし。attempt_hook(er012_b専用)・prior_generations(内部引数)は渡さない |
| Y-B-03 | enable_connected_speech_equivalence_layer=connected_speech_enabled_for(name)=True(PREVIEW/COMMENT); disfluency_qa=True; enable_pronunciation_resolver=True; style_prefix_override=_role_style('PREVIEW'\|'COMMENT') or B1_PREVIEW_STYLE_PREFIX_CALM; tts_backend=flash-lite。max_attempts未指定(3) |
| Y-B-04 | text=_pnap_supply(text, tts_safe_news_en(text)); disfluency_qa=False; enable_connected_speech_equivalence_layer=connected_speech_enabled_for(id)=True(FULL_STORY: er020:132,150-165); enable_repetition_qa=True; enable_pronunciation_resolver=True; style_prefix_override=_role_style('FULL_STORY'); tts_backend=flash-lite; Voiceは with tts_voice(voice): p9a.VOICE_NAME を一時差替え(narrator=p9a.VOICE_NAME / voice=Algieba・Zephyr・Schedar)。max_attempts未指定(3)・max_extra_chars既定15 |
| Y-B-05 | text=_pnap_supply(text, tts_safe_news_en(text)); disfluency_qa=False; enable_connected_speech_equivalence_layer=connected_speech_enabled_for(id)=True(FULL_STORY: er020:132,150-165); enable_repetition_qa=True; enable_pronunciation_resolver=True; style_prefix_override=_role_style('FULL_STORY'); tts_backend=flash-lite; Voiceは with tts_voice(voice): p9a.VOICE_NAME を一時差替え(narrator=p9a.VOICE_NAME / voice=Algieba・Zephyr・Schedar)。max_attempts未指定(3)・max_extra_chars既定15 |
| Y-B-06 | 非chunk本文と同一(BODY引数): 同Voice/Style/Gate/retry/fallback。chunk idは resolve_narrative_role で FULL_STORY へ解決(_FAMILY_Y_SEGMENT_PATTERN の _k<n> 接尾辞: er020:132)。解決不能なら課金前STOP(_assert_chunk_roles: er121_family_y_audio_01.py:278-285)。chunk間0.2秒無音はasm側 |
| Y-B-07 | used_form(tts_safe_kp_en), tts_backend=flash-lite, style_profile='default'(→K2なし=旧key+vote1専用key)。enable_connected_speech引数なし(False既定)。vote_pass_required=vote_enabled()=True(er104_kp_three_asr_vote_01.py:33 KP_THREE_ASR_VOTE_ENABLED=True) |
| Y-B-08 | explanation_text(tts_safe_en); style_prefix_override=_kp_explanation_style()(flash-lite時KEY_PHRASE_EXPLANATION_EN); max_attempts=KP_EXPLANATION_MAX_ATTEMPTS=3; disfluency_qa=True; enable_non_latin_cascade=True; connected_speech引数なし。text-gate status!='OK'のrankはTTSを呼ばずSTOPPED(er019:1747) |
| Y-S-01 | Y-B-01と同じ(suffixなし) |
| Y-S-01b | max_attempts=6指定だが関数内で min(max_attempts, 3) にクランプ(voice01.py:487)。LR・cooldown引数なし |
| Y-S-02 | text=_pnap_supply(...); expected_substring=first_words(title,3); max_extra_chars=30; style_prefix_override=_role_style('TOPIC_INTRO'); enable_connected_speech_equivalence_layer=True; tts_backend=flash-lite。max_attempts/standard_attempts 未指定(3/2)。prior_generations=0 |
| Y-S-03 | expected_substring=expected_substring_ja(title); max_extra_chars=30; style_prefix_override=_role_style_ja(); tts_backend=flash-lite。connected_speech/repetition引数なし。max_attempts既定6→min(,3)にクランプ(:732) |
| Y-S-04 | expected_substring=expected_substring_ja(text); style_prefix_override=_role_style_ja_support(); tts_backend=flash-lite。connected_speech引数なし |
| Y-S-05 | tts_input=_pnap_supply(text, tts_safe_news_en(text)); expected_substring=first_words(text); style_prefix_override=(_role_style_slower('FULL_STORY') or A2_ENGLISH_STYLE_PREFIX_SLOWER); disfluency_qa=False; enable_connected_speech_equivalence_layer=connected_speech_enabled_for(id)=True; enable_repetition_qa=True; tts_backend=flash-lite; Voiceはtts_voice(voice)。max_extra_chars=60既定・max_slowdown_attempts=3既定 |
| Y-S-06 | tts_input=_pnap_supply(text, tts_safe_news_en(text)); expected_substring=first_words(text); style_prefix_override=(_role_style_slower('FULL_STORY') or A2_ENGLISH_STYLE_PREFIX_SLOWER); disfluency_qa=False; enable_connected_speech_equivalence_layer=connected_speech_enabled_for(id)=True; enable_repetition_qa=True; tts_backend=flash-lite; Voiceはtts_voice(voice)。max_extra_chars=60既定・max_slowdown_attempts=3既定 |
| Y-S-07 | tts_input=_pnap_supply(text, tts_safe_news_en(text)); expected_substring=first_words(text); style_prefix_override=(_role_style_slower('FULL_STORY') or A2_ENGLISH_STYLE_PREFIX_SLOWER); disfluency_qa=False; enable_connected_speech_equivalence_layer=connected_speech_enabled_for(id)=True; enable_repetition_qa=True; tts_backend=flash-lite; Voiceはtts_voice(voice)。max_extra_chars=60既定・max_slowdown_attempts=3既定; chunk idはFULL_STORYへ解決(未解決なら課金前STOP) |
| Y-S-08 | Y-B-07と同じ(level='a2') |
| Y-S-09 | ja_gloss_tts; max_extra_chars=30; known_key_phrase_terms=[used_form]; style_prefix_override=_role_style_ja_kp_meaning()(default profileはJ3素通し); tts_backend=flash-lite |

## 2. 星取表①(Y行): 何回失敗すると何が起こるか
| Family | レベル | 音声部位 | 通常TTS上限 | Retry条件 | Fallback有無・種類 | Rewrite有無 | Rewrite発動条件 | 最終NG時 | 仕様・実装一致 |
|---|---|---|---|---|---|---|---|---|---|
| Y | Adv(b1b) | Y-B-00 Intro / Notification1-3 / Outro(固定mp3) | TTSなし | - | - | 無 | - | - | 一致(対象外) |
| Y | Adv(b1b) | Y-B-01 共有固定英語9: welcome / preview_intro / key_phrases_intro / full_story_intro / num_one〜num_five(*_charon.wav) | 品質NG3+技術別枠1/呼出(Store再利用で生成0あり) | ASR NG・長さ・異常長・発話区間検出失敗(Repetition/disfluency対象外) | F-Style(MINIMAL): trimmed None時のattempt内のみ。品質NGでは切替なし | 無(connected_speech未配線・role=None) | - | 3NG→STOPPED→Lock+EN HR queue。SharedNarrationBlockedError/assemble BLOCK | 一致/runtime未検証(Store再利用のみ) |
| Y | Adv(b1b) | Y-B-02 topic_intro('Today's topic is {title}.') | 品質NG3(同一Style)+技術別枠1/呼出 | ASR NG・長さ・異常長・発話区間検出失敗 | F-Style: trimmed None時のattempt内のみ。品質NGでは切替なし | 有(1回, TOPIC_INTRO) | 3回目(cooldown600s後)もNG | LR不成立→STOPPED→Lock+EN HR queue。Y Gate対象外 | 一致/runtime未検証(att=1のみ) |
| Y | Adv(b1b) | Y-B-03 preview / comment_1 / comment_3(Comment 2は2026-10-26承認で削除) | 品質NG3+技術別枠1/呼出 | Y-B-02+disfluency gate | F-Style: Y-B-02と同じ | 有(1回, PREVIEW/COMMENT) | 3回目もNG | Y-B-02と同じ | 一致/runtime未検証(att=1のみ) |
| Y | Adv(b1b) | Y-B-04 ナレーター本文5: y_lead / y_intro_1 / y_intro_2 / y_intro_3 / y_closing(Tension+Closing) | 品質NG3+技術別枠1/呼出 | ASR NG・長さ・Repetition QA・異常長・発話区間検出失敗 | F-Style(minimal): trimmed None時のattempt内のみ | 有(1回, FULL_STORY) | 3回目もNG | LR不成立→STOPPED→Lock。LR成功でもY Gate LOCAL_REWRITE_RECOVERY BLOCK→user承認要 | 一致/本部位の実走なし(未検証) |
| Y | Adv(b1b) | Y-B-05 Voice本文3: y_voice_1(Algieba) / y_voice_2(Zephyr) / y_voice_3(Schedar) | 品質NG3+技術別枠1/呼出 | Y-B-04と同じ | F-Style(minimal): Y-B-04と同じ | 有(1回, FULL_STORY) | 3回目もNG(E-1 y_voice_1で発動) | Y-B-04と同じ。E-1: LR成功→Gate BLOCK→user承認 | 一致/runtime実走あり(通常3+LR後1=総4) |
| Y | Adv(b1b) | Y-B-06 本文chunk: y_<segment>_k<j>(segmentが空行区切り2段落以上のときのみ。現行Y契約は各Voice 1段落) | chunk単位でY-B-04と同じ | Y-B-04と同じ(chunkごと) | Y-B-04と同じ | 有(chunkごと1回) | chunkの3回目もNG | chunk失敗後も後続chunk継続。親=CHUNKS_NOT_ALL_VALIDATED。chunk単位でGate BLOCK | 一致/実記事不発火・dev入力att=1(未検証) |
| Y | Adv(b1b) | Y-B-07 Key Phrase英語 kp{rank}_en(3件。末尾の再掲phrase_repeatは新規生成せず同一entry複製) | MINIMAL2+ENGLISH_LOCK2=総4 | 3-ASR多数決NG・非ラテン再判定・disfluency | F-Style/F-Prompt: MINIMAL2回NG→ENGLISH_LOCK2回 | 無(Key Phrase非適用) | - | 4回NG→STOPPED→Lock+EN HR queue(slot4のみ)→Audio Gate BLOCK | 一致/MINIMAL内retry実走・LOCK段未検証 |
| Y | Adv(b1b) | Y-B-08 Key Phrase英語解説 kp{rank}_explanation_en(3件) | 3(単一Style) | ASR NG・長さ・disfluency | 無 | 無(5 role外) | - | 3NG→STOPPED→Lock→Audio Gate BLOCK | 一致/runtime未検証 |
| Y | Std(a2) | Y-S-01 共有固定英語9(welcome / preview_intro / key_phrases_intro / full_story_intro / num_one〜num_five) | 品質NG3+技術別枠1/呼出(Store再利用) | Y-B-01と同じ | F-Style: Y-B-01と同じ | 無 | - | Y-B-01と同じ | 一致/runtime未検証 |
| Y | Std(a2) | Y-S-01b 共有固定日本語 point_explanation('ポイント解説') | 標準2+minimal1=総3 | JA ASR NG・長さ | F-Style: 標準2回NG→MINIMAL_JA1回 | 無(JA) | - | 3NG→STOPPED→Lock+JA HR queue。ただしY timelineは未使用(Y-F06) | 一致/Y未使用(C) |
| Y | Std(a2) | Y-S-02 topic_intro(英語) | 標準2+minimal fallback1=総3 | ASR NG・長さ・異常長/発話区間 | F-Style/F-Prompt: 標準2回NG→minimal instruction1回(Secondary必須) | 有(1回, minimal系再TTS) | 標準2+fallback1の全NG後 | LR不成立→STOPPED→Lock+EN HR queue。Y Gate対象外 | 一致/runtime未検証(att=1のみ) |
| Y | Std(a2) | Y-S-03 japanese_title(日本語タイトル) | 標準2+minimal1=総3 | JA ASR NG・長さ・事前STOP(記号/外来語gate) | F-Style: 標準2回NG→MINIMAL_JA1回 | 無(JA) | - | 3NG→STOPPED→Lock+JA HR queue | 一致/runtime未検証 |
| Y | Std(a2) | Y-S-04 日本語支援文: preview / comment_1 / comment_2 / comment_3(Stdはcomment_2を維持) | 標準2+minimal1=総3 | Y-S-03と同じ | F-Style: Y-S-03と同じ | 無(JA) | - | 3NG→STOPPED→Lock+JA HR queue。解除=user承認 or support再生成 | 一致/runtime実走あり(E-1 preview: 3NG→HR→approve後3NG→HR queue→user承認) |
| Y | Std(a2) | Y-S-05 ナレーター本文5: y_lead / y_intro_1〜3 / y_closing(全segmentに6%減速) | 通算3(標準2+minimal1)を6%減速取直しと共有 | ASR NG・長さ・Repetition QA・減速後ASR NG・異常長 | F-Style/F-Prompt: 標準2回NG→minimal1回 | 有(1回, minimal系再TTS) | 標準2+fallback1の全NG後(減速後NGではLRしない) | STOPPED→Lock。減速後NG最終→HR+Lock+HR queue。成功でもGate: fallback/LR/減速欠落でBLOCK | 一致/本部位の実走なし(未検証) |
| Y | Std(a2) | Y-S-06 Voice本文3: y_voice_1(Algieba) / y_voice_2(Zephyr) / y_voice_3(Schedar)(6%減速) | Y-S-05と同じ | Y-S-05と同じ | Y-S-05と同じ | 有(1回) | Y-S-05と同じ(E-1 y_voice_1で発動) | Y-S-05と同じ。E-1: LR成功→Gate BLOCK(2違反)→user承認 | 一致/runtime実走あり(標準2+Fallback1+LR後1=総4) |
| Y | Std(a2) | Y-S-07 本文chunk: y_<segment>_k<j>(2026-10-26 Std/Adv双方承認。chunkごとに6%減速→0.2秒→連結) | chunk単位でY-S-05と同じ | Y-S-05と同じ(chunkごと) | Y-S-05と同じ | 有(chunkごと1回) | Y-S-05と同じ | Y-S-05と同じ(chunk単位Lock/Gate) | 一致/実記事不発火・dev入力att=1(未検証) |
| Y | Std(a2) | Y-S-08 Key Phrase英語 kp{rank}_en(3件) | MINIMAL2+ENGLISH_LOCK2=総4 | Y-B-07と同じ | F-Style/F-Prompt: Y-B-07と同じ | 無 | - | Y-B-07と同じ | 一致/runtime未検証 |
| Y | Std(a2) | Y-S-09 Key Phrase日本語意味 meaning_{i}(3件、japanese_meaning) | 標準2+minimal1=総3 | JA ASR NG・長さ | F-Style: 標準2回NG→MINIMAL_JA1回 | 無(JA) | - | 3NG→STOPPED→Lock+JA HR queue→Audio Gate BLOCK | 一致/runtime未検証 |

注: 各セルの詳細(判定関数:行、cooldown、Lock、runtime証拠path)は `family_y_01.json` の同ID。フローは§4。

## 3. 星取表②(Y行): Rewrite無し・例外の理由とユーザー承認
理由区分: (1)ユーザーが明示不採用 (2)品質保護等で承認済み仕様として対象外 (3)実装当時の技術的制約 (4)共通仕様の適用漏れ・配線漏れ (5)設計・承認記録に理由なし。
| Family | 音声部位 | Rewrite | 不適用・例外の理由(事実) | ユーザー承認の有無 | 根拠資料 | 分類 |
|---|---|---|---|---|---|---|
| Y | Y-B-01/Y-S-01 共有固定英語9(welcome等) | 無 | 区分(2)の包含規定: LRは『英語の5 role(Full Story/Comment/Preview/Topic intro/In One Line)のみ』に適用、Heading readout・Key Phraseは明示除外。shell固定文は5 role外。shell固定文を対象外にする個別理由: 記録なし | 有(5 role限定の承認=2026-09-26。shell固定文への個別承認記述は未発見) | CURRENT_SPEC.md:2176,2873; er020_tts_retry_local_rewrite_01.py:1-55,150-185 | A(包含規定のみ。個別理由は理由不明・記録なし) |
| Y | Y-S-01b 共有固定日本語 point_explanation | 無 | 区分(2): JAはLRなし(CURRENT_SPEC.md:2885(3)『JA KP・JA全般=Local Rewriteなし、3NG→STOPPED→HR Lock(原文L146)』)。JAを対象外にした個別理由・原文L146のファイル: 本調査で特定できず=理由不明・記録なし | 有(CURRENT_SPEC.mdが『原文L146』の承認として記載。原文ファイル未特定) | CURRENT_SPEC.md:2885(3); E1_HUMAN_REVIEW_01.md:53(JA LRはTrial専用er058) | A(承認記載あり・原文path未特定) |
| Y | Y-S-03 japanese_title / Y-S-04 日本語支援文4種 / Y-S-09 KP日本語意味 | 無 | 同上(JAはLRなし) | 有(同上) | CURRENT_SPEC.md:2885(3),2873,2886 | A(承認記載あり・原文path未特定) |
| Y | Y-B-07/Y-S-08 Key Phrase英語 | 無 | 区分(1)/(2): Key Phraseは明示除外(ユーザー承認2026-09-26)。KPは4回構成(MINIMAL2+ENGLISH_LOCK2) | 有 | CURRENT_SPEC.md:2176,2885(1); er020:1-55 | A |
| Y | Y-B-08 Key Phrase英語解説(Adv) | 無 | 区分(2)の包含規定(5 role外)。KP英語解説にLRを付けない旨を明示した承認記述: 見つからず。er019:1213のコメントは『TTS①②③、3回NGでLR/HR』と書くが配線なし | 5 role限定の承認は有。KP解説個別の明示は未発見 | CURRENT_SPEC.md:2873,2885(2); er019_family_x_audio_production_runner_01.py:1202-1219 | A(包含規定のみ) |
| Y | Y-B-02/03 topic_intro・preview・comment(Adv), Y-S-02 topic_intro(Std) | 有 | LR有効。LR再TTSはstyle_prefix_override保持(Adv)/minimal系(Std)。Y Gateの対象外(body8のみ)のためLR成功音声はGateでBLOCKされない | 有(5 role適用の承認) | CURRENT_SPEC.md:2176,2886; er121_family_y_audio_01.py:683-720 | A |
| Y | Y-B-04/05/06, Y-S-05/06/07 本文8 segment(+chunk) | 有(ただしLR成功後の採用に人間承認が必要) | LR自体は有効。成功しても y_style_gate が LOCAL_REWRITE_RECOVERY を違反としBLOCK(record_human_approval(approved_by=user)なしでは組立不可)。同型のX M3 Gateは『LR再TTSがrole styleを落とす既存の穴(OPEN-312)』の検知・BLOCKとして置かれ、USER_DECISION_REGISTER #6はDeferred。Y固有のユーザー承認: 記録なし | Y固有の承認なし(X側は#6 Deferred) | er121_family_y_audio_01.py:706-709; er019_family_x_style_profile_01.py:742-743; OPEN_ITEMS.md:815(OPEN-312); USER_DECISION_REGISTER_01.md:24 | C(安全側ガード。Y-F05) |

新解釈(別欄): §10参照。

## 4. §5形式: 部位別の現行フロー(「通常n+Fallback m+LR後k=総N」)
### Y-B-04/05/06 Adv本文(narrator5・Voice3・chunk) — news_tail_fix.generate_news_narration_wide_margin
- ①attempt1: TTS(role style FULL_STORY、同Voice/モデル)[技術エラー→即時再呼出1回]→トリム/異常長検査[trimmed None→同attempt内でminimal instructionへF-Style 1回]→ASR(Primary OpenAI→NGならSecondary Azure、unified judge)+長さ+Repetition QA→全PASSでOK終了
- ②attempt2(待機なし、同一Style/モデル/Voice)→NGなら
- (cooldown 600秒の実sleep)→③attempt3 →NGなら
- LR: 問題spanをluna候補5件→7 Gate→全PASS1件で書換え→再TTS 1 attempt(v1、Style指定なし=OPEN-312、Repetition QA有)→OKならstatus=OK(local_rewrite_recovery)
- LR不成立/再TTS NG→STOPPED→record_outcome→HUMAN_REVIEW_REQUIRED Lock(+ASR judge最終NGならEN HR queue行)
- tts stageはrc=0で継続→gate: LR成功ならLOCAL_REWRITE_RECOVERY BLOCK/STOPPEDはassembleのAudio Validation GateでBLOCK→YE2EStop rc=2
- 再実行: 同一文面はLock中0 API→approve_regenerate後の次の1回だけ通常3+cooldown+LRを再走→採用はrecord_human_approval(user)
- **3回NGの数え方**: 通常3+Fallback0(品質NGでは切替なし)+LR後1=総4(attempts_log 4行。E-1 b1b y_voice_1で実測)。技術再試行・attempt内F-Styleは別カウント(発動時はattempts_logに行が増える=record_outcomeの累積に加算、累積15超でLock)

### Y-B-02/03 Adv topic_intro・preview・comment_1/3 — voice01.generate_charon_english
- ①attempt1 TTS(role style)→ASR unified judge+長さ(+preview/commentはdisfluency)→PASSで終了
- ②attempt2 →NG→(cooldown 600秒)→③attempt3→NG→LR(再TTS 1 attempt、style_prefix_override保持)→不成立でSTOPPED→Lock+EN HR queue
- LR成功音声はY Gate対象外のためassemble可(PASS_WITH_WARNING『LR_REWRITTEN』が事後試聴リストに入る)
- **3回NGの数え方**: 通常3+Fallback0+LR後1=総4

### Y-S-05/06/07 Std本文(narrator5・Voice3・chunk) — n3_tts.generate_a2_segment_with_slowdown
- 内側 generate_english_segment_with_fallback: ①標準attempt1(slower style、Repetition QA有)→②標準attempt2→(cooldown 600秒)→③minimal instruction fallback 1回(Secondary必須)→NGなら
- LR: 再TTSはminimal instruction系1 attempt(v1)
- OK→6%減速→減速後unified judge(LR採用時は書換え後文が正解)→OKでslowdown_applied=True・status=OK
- 減速後NG→通算予算(3)が残れば通常ペースから取り直し(標準 min(2,残))、尽きれば finalize_a2_slowdown_final_ng → HR+Lock+HR queue
- 成功でも y_style_gate: fallback_used≠False→STD_FALLBACK_USED_OR_UNKNOWN、LR→LOCAL_REWRITE_RECOVERY、減速欠落→Y_MISSING_MANDATORY_A2_SLOWDOWN でBLOCK(人間承認なしでは組立不可)
- **3回NGの数え方**: 通常(標準)2+Fallback(minimal)1+LR後1=総4生成(通算予算3は標準2+fallback1、LR後1は予算外でrecord_outcome累積に加算。減速後取り直しは同じ予算3を共有)

### Y-S-02 Std topic_intro — generate_english_segment_with_fallback
- 標準attempt1→標準attempt2→(cooldown 600秒)→minimal fallback 1(Secondary必須)→NG→LR(minimal系1 attempt)→不成立でSTOPPED→Lock+EN HR queue。6%減速なし。Y Gate対象外
- **3回NGの数え方**: 通常2+Fallback1+LR後1=総4

### Y-S-03/04/09, Y-S-01b Std日本語(タイトル・支援文4種・KP意味・point_explanation) — generate_a2_japanese_with_fallback / generate_charon_japanese
- TTS前の事前STOP(placeholder記号・禁止記号・外来語gate)→標準attempt1→標準attempt2→minimal(JA) fallback 1→NG→STOPPED→Lock(ja)+JA HR queue。cooldownなし・LRなし。解除=record_human_approval(user)またはsupport再生成
- **3回NGの数え方**: 通常2+Fallback1+LR0=総3(max_attemptsは関数内でmin(,3)にクランプ)

### Y-B-07 / Y-S-08 Key Phrase英語 — generate_key_phrase_component_verified
- MINIMAL attempt1→attempt2(各回3-ASR多数決)→NGなら ENGLISH_LOCK attempt3→attempt4(Azure/Whisper circuit open時は技術STOPでスキップ)→NG→STOPPED→Lock+EN HR queue(通算slot4のみ)。cooldownなし・LRなし
- **3回NGの数え方**: 通常(MINIMAL)2+Fallback(ENGLISH_LOCK)2+LR0=総4

### Y-B-08 Adv KP英語解説 — generate_key_phrase_explanation_en_verified
- text-gate非OKならTTSなしでSTOPPED。OKなら attempt1→2→3(単一Style、disfluency)→NG→STOPPED→Lock。Fallback・cooldown・LRなし
- **3回NGの数え方**: 通常3+Fallback0+LR0=総3

### Y-B-01 / Y-S-01 共有固定英語9
- Master Audio Store照会→hitなら生成0。missのみ attempt1→2→3(F-Styleはattempt内のみ)→STOPPED→Lock+EN HR queue→SharedNarrationBlockedError(監査保存後)/assemble BLOCK。cooldownなし・LRなし
- **3回NGの数え方**: 通常3+Fallback0+LR0=総3(Y runでは全件Store再利用)

## 5. YでLRが有効/無効になる仕組み(事実)
1. LRは共通関数の内側にあり、Yは専用経路を持たない。有効化の条件は(a)呼出元が `enable_connected_speech_equivalence_layer=True` を渡す、(b)出力pathが `.../<theme>/<level>/narration/<segment>.wav` 形式(`_has_valid_narration_layout`: er011:119-137。Yは `{out_dir}/{b1b|a2}/narration/{id}.wav` で満たす)の2点。(a)の値は `connected_speech_enabled_for(segment_id)`(er020:188)で、`resolve_narrative_role`(er020:135-185)が segment idをroleへ解決する。
2. **有効**: y_lead / y_intro_1〜3 / y_voice_1〜3 / y_closing とそのchunk id(`_FAMILY_Y_SEGMENT_PATTERN`: er020:132。import時自己検査 er020:172。Y testで固定 er121_family_y_structure_match_test_01.py:205-213)=FULL_STORY、topic_intro=TOPIC_INTRO、preview=PREVIEW、comment_1/2/3=COMMENT。
3. **無効(引数未指定)**: 共有固定英語9(shared_narration経由。connected_speech引数を渡さない)、Key Phrase英語(`kp*_en`→role=KEY_PHRASE、かつ引数なし)、Adv KP英語解説(role=None、引数なし)。**別関数で非対応**: すべての日本語(`generate_a2_japanese_with_fallback`/`generate_charon_japanese`にLR呼出なし。JA LRは er058 のTrial専用でProduction非経由: E1_HUMAN_REVIEW_01.md:53)。
4. LRの内部条件(共通核): ①呼出元が通算TTS試行を使い切ってなおNG(新旧とも『両ASR合意』条件は無い: er020:754の記述とGrep `合意`=該当1件[docstringのみ])②`identify_ng_span`が差分spanを見つけること(見つからない=HUMAN_REVIEW_LOCKED_NO_NG_SPAN。er020:775-779)③luna候補5件のうち7 Gate全PASSが1件以上④再TTS 1回がPASS。全て満たしてstatus=OK。
5. LR成功後のY側の扱い: 本文8 segment(とchunk)は `y_style_gate` が `local_rewrite_recovery` を違反にする(er121_family_y_audio_01.py:708-709)ため、approvals(`human_approved_segments.json`)に該当segmentのcanonical sha一致の承認が無いと `BLOCKED_STYLE_PROFILE_GATE`(同:919)。topic_intro・preview・comment・日本語・KPはGate対象外。

## 6. 2026-10-19 ユーザー決定の逐語引用と照合
出典: `docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md` §3(L41-63)・§4(L65-76)。
> **「両ASRが同じ箇所の誤読に合意すること」というRewrite発動条件を削除する。**(L45)
> Status：`APPROVED_FOR_PRODUCTION`
> 基本フロー：(L49)
> TTS初回生成 → Primary／Secondaryによる承認済み検証 → NGなら最大2回のTTS再生成 → なおNGならRewriteへ進む。(L51)
> 既存の音韻同等性判定やその他の承認済み品質・安全条件を省略することは認めない。(L53)
> **正式に許可されたRewrite後は、書換え後の原稿を正解として、すべての後続音声検査を行うこと。**(L71)

| 決定の要素 | Yの該当部位での実装 | 照合 |
|---|---|---|
| 両ASR合意条件の削除 | Y側コードに条件なし。共通 er020:754 docstringが『本関数内にも呼出元にも存在しない(実装されたことはない)』と記載。Grep `合意` はdocstring1件のみ | 一致 |
| TTS初回→Primary/Secondary検証→NGで最大2回再生成→なおNGでRewrite | Adv本文/Adv支援文/Std topic_intro・本文(LR有効部位): 通常3 attempt(=初回+再生成2)使い切り後にLR(news_tail_fix.py:325, voice01.py:325, crosslevel:317-325)。stop_retryingによる早期LRは cascade有効時 False固定(er006_secondary_asr_01.py:284,961,1238)で不到達 | 一致(コード)。runtime: Adv y_voice_1・Std y_voice_1で実走(EVIDENCE_02) |
| Std の『再生成』の中身 | Std本文/topic_introの3回目はminimal instruction(Style変更・Secondary必須)。CURRENT_SPEC.md:2873は『再生成②③(原稿・Prompt・モデル・Voice・速度を維持)』と記述。2026-09-04『標準2+minimal1』(er011:86-104)との整合は本書では判定しない(共通核=X Agent) | 仕様記録の整合は要確認(Y-F08, C) |
| LR対象はrole=英語5 roleのみ | Y: FULL_STORY/TOPIC_INTRO/PREVIEW/COMMENTは有効、JA・KP・shared固定は無効(§5) | 一致(CURRENT_SPEC.md:2873,2886) |
| LR後は書換え後原稿を正解にして後続検査 | Std本文: apply_a2_slowdown_postprocess が resolve_expected_text_after_local_rewrite を読む(n3_tts.py:217-221)。resume/再利用: _generate_or_reuse→guard_entry(er019:1060-1073)。Adv: LR再TTSの検査は書換え後文で行う(__wrapped__(rewritten_text)=text引数が書換え後) | 一致(コード)。runtime: 実走中の減速後再検証はE-1 a2 y_voice_1(ただし採用はR0音声のuser承認に置換)で確認、再利用側はrun_ev_01 b1b y_voice_1(reused=True, lr=Y)が存在 |
| HR遷移・Lock keyは元の原稿のまま | finalize_a2_slowdown_final_ng/record_outcomeは元tts_inputでrecord(n3_tts.py:309-327)。Y gate承認のsha照合は canonical_text(元原稿) | 一致(コード) |

## 7. runtime evidence 有無表(部位別)
| ID | retry | Fallback | cooldown | LR | HR/Lock | 証拠path(代表) |
|---|---|---|---|---|---|---|
| Y-B-01/S-01 shared | なし(Store再利用) | なし | なし | なし | なし | sns_age_limit/run_01/{b1b,a2}/audit/tts_generation_results.json shared_narration(reused=True) |
| Y-B-02/03, Y-S-02, Y-S-03 | なし(att=1) | なし | なし | なし | なし | 同 segments.* att=1 |
| Y-B-04, Y-S-05(narrator) | なし(att=1) | なし | なし | なし | なし | 同 segments.y_lead 等 |
| Y-B-05 b1b y_voice_1 | あり(Repetition QA flagで3回) | なし | あり(600.004s) | あり(RESOLVED_BY_LOCAL_REWRITE、attempts_log 4行) | Lock(7累積)→Y Gate BLOCK→2026-10-26 user承認(HUMAN_APPROVED)。EN HR queue行なし | redelivery_fee/run_01/b1b/audit/{tts_generation_results,review_lock_state}.json; EVIDENCE_02.md §3-5; ypl7_user_approval_record_y_voice_1.json |
| Y-S-06 a2 y_voice_1 | あり(標準2: flag/不一致) | あり(minimal 1) | あり(600.003s) | あり(RESOLVED、gen=3) | EN HR queue行129・Y Gate BLOCK(2違反)・user承認(6%減速版) | redelivery_fee/run_01/a2/audit/tts_generation_results.json; er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl:129; EVIDENCE_02.md §8 |
| Y-S-06 a2 y_voice_2(E-3) | あり(attempt1 Repetition flag→attempt2 OK) | なし | なし | なし | なし | sns_age_limit/run_01/a2/audit/tts_generation_results.json |
| Y-S-04 a2 preview(JA, E-1) | あり(標準2+approve後3) | あり(minimal JA 1) | なし | なし(JAにLRなし) | Lock→JA HR queue行15→approve_regenerate(Fable権限)→再STOPPED→user承認 | redelivery_fee/run_01/a2/audit/tts_generation_results.json; er007_output/ja_asr_cascade_01/human_review_queue.jsonl:15; EVIDENCE_02.md §3-4 |
| Y-B-07 KP英語(E-3 kp3) | あり(MINIMAL attempt1 TRUE_CONTENT_MISMATCH→attempt2 OK) | ENGLISH_LOCK未発動 | なし | なし | なし | sns_age_limit/run_01/b1b/audit/tts_generation_results.json key_phrases.3.english |
| Y-B-06 / Y-S-07 chunk | なし(dev入力att=1) | なし | なし | なし(mock testのみ: er121_family_y_audio_chunk_test_01.py:296-302) | なし | redelivery_fee_stdchunk_ev/run_ev_01/{b1b,a2}; er121_output/family_y_std_chunk_evidence_01/ |
| Y-B-08, Y-S-08, Y-S-09 | なし(att=1) | なし | なし | なし | なし | sns_age_limit/run_01 key_phrases |
| 全体(参考) | - | - | - | - | attempt_history.jsonl: family_y\|er121を含む行126(うちProduction path=run_01 18, run_ev_01 3、他はDEV/Voice Trial)。EN HR queue Y由来12行(123,124=DEV persona trial、129=E-1 a2 y_voice_1、130=候補take、131-132=PAUSE-CAUSE Trial、133-138=MALE7 Trial)、JA queue Y由来1行(15) | er011_output/attempt_history.jsonl; er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl; er007_output/ja_asr_cascade_01/human_review_queue.jsonl |

未検証(実走証拠なし)として明記: 減速後NGの取り直し(slowdown retake)、ENGLISH_LOCK段、HRあり経路でのchunk、Adv/Std topic_intro・支援文のretry/LR、Std前の共有固定のretry。

## 8. 不一致・理由不明箇所(分類A/B/C、重要度・品質リスク・量産単価・Delivery影響)
A=承認済みの合理的差異(根拠あり・一致)/B=承認済み仕様との不一致(修正せず原因と解決方針)/C=未承認・根拠不明。
| ID | 内容(事実) | 分類 | 重要度 | 品質リスク | 量産単価 | Delivery | 原因/解決方針(修正しない) |
|---|---|---|---|---|---|---|---|
| Y-F01 | Y runnerは `STYLE_PROFILE = "default"` 固定(er121_family_y_runner_01.py:37)。仕様側: DESIGN_01.md:84『Style: profile fx_20261017を継承』、SPEC_LEDGER_03.md:60 YL-A01『APPLY(適用)』、CURRENT_SPEC.md:1699付近の共通仕様表はPD06/S3/E1/K2/P8-KP/P7を『Y化時に最初から配線対象』。runtime: E-3 b1b y_voice_1 の style_prefix は『calm, steady news narration…』(基底style)、y_style_profile_gate.json の x_gate.checked=[]。fx_20261017のFULL_STORYは『Speak directly to one listener with warmth…』(PD06)。Yを default にした意図的除外の記録は未発見。結果としてM3/Y Gateの Adv minimal_fallback・Style prefix・支援文fallback検査は no-op(er121_family_y_audio_01.py:697 `if prof is not None`、m3_assembly_gate('default')は即PASS) | B(配線漏れの疑い。断定せず) | 高(Style=音声品質。本監査のRetry/Fallback/LR範囲外の一覧外発見) | Y本文・支援文・KPのStyleが承認済みprofile(PD06等)でない可能性 | なし(再生成が発生すれば増) | 修正すれば全Y音声の再生成が必要な可能性 | 原因: Y runnerが共通profile継承を配線していない(要確認)。方針: 次委任で意図的除外の有無をFableが確認→B確定なら配線+Std/Adv再生成要否を見積。本Agentは修正・断定しない |
| Y-F02 | CURRENT_SPEC.mdのChunk節に旧記述が残存: L2954『対象外: Standard(a2)・…・Family Y』、L2963『Standard本文は仕様上対象外』。実装・承認は Y=Std/Adv双方(er121_family_y_structure_01.py:113 CHUNK_TTS_Y_LEVELS=("b1b","a2")、2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md:14,32-33)。コード内にも古いコメント: er121_family_y_audio_01.py:17『Adv(b1b)本文のみ(X同様、Std本文はchunk化しない)』 | B(古いルール残存・文書) | 低(挙動には影響しない) | なし | なし | なし | SSOT同期(PM-SSOT-SYNC-04進行中、OPEN-532に包含)。新規OPEN不要。コメント1行はコード編集のため別委任 |
| Y-F03 | Repetition QA単独NG(ASR転写が正本と一致/正規化一致)の本文は、LR段で identify_ng_span が差分を見つけず HUMAN_REVIEW_LOCKED_NO_NG_SPAN→書換えなしでHR(er020:775-779。E1_HUMAN_REVIEW_01.md §5 のdry判定: b1b y_voice_1 は是正後 found=false)。2026-10-19決定は『なおNGならRewriteへ進む』。NO_NG_SPAN時の扱いを明示したユーザー決定: 未発見(実装由来、DECISION_LOG.md:9722のtest記述レベル)。Y Voice 1 Algiebaで主要な失敗型(旗率72%・take最終OK率38%: OPEN_ITEMS.md:1048) | C(仕様記録なし) | 中 | Y Voice 1の再生成/HR頻度に直結(Algieba) | 再生成連鎖の追加費用(MALE7 Trialで26.1円超過の一因: OPEN-533) | HR待ちで完成が止まる(E-1で実発生) | 判断候補(分類D候補): Repetition QA単独NGをLR対象にするのは受理面/方式の新設で新仕様。既存OPEN-525(閾値)/OPEN-533(再生成率)に追記して統合し、新規OPENは不要。ユーザー判断要否はFable |
| Y-F04 | ER-011 Lockは書かれるが、EN HR queue行は『ASR judgeの最終slot NG』でのみ書かれる(er006_secondary_asr_01.py:641-642)。Repetition QAはjudge後に判定する(news_tail_fix.py:223-228)ため、Repetition QA単独NGの最終STOPPEDではqueue行が出ない。実測: E-1 b1b y_voice_1(Lock→STOPPED)のEN queue行なし(redelivery_fee行は a2 y_voice_1[129]と候補take[130]のみ) | C(記録なし) | 低〜中(人間がqueueだけを見ると見落とす) | なし(Lock・tts_generation_results.jsonには記録あり) | なし | 見落とし時は完成遅延 | 方針: queue登録契機を『Lock到達』に揃えるのは共通核の仕様変更。X Agentの共通核記述と合わせてFable判断。新規OPEN候補は§9 |
| Y-F05 | Y Gateは本文8 segment(+chunk)の LOCAL_REWRITE_RECOVERY と Std の fallback_used≠False を人間承認なしでBLOCK(er121_family_y_audio_01.py:706-709)。結果: Std本文の3回目(minimal)で成功した音声、LR成功した音声は、ASR PASSでも自動採用されない。X M3 Gateと同型で、根拠は OPEN-312(LR再TTSがrole styleを落とす)。Adv LR再TTSは style_prefix_overrideを渡さない(news_tail_fix.py:369-378)。ユーザー判断: USER_DECISION_REGISTER #6=Deferred。Y固有の承認: 記録なし | C(安全側ガード・ユーザー未承認のFable設計) | 中(品質は守る側) | なし(守る側) | なし | Std本文3回目/LR成功のたびにユーザー試聴承認が必要(E-1で2 segment発生) | A/B/C/D判定(27-3): C(現タスクと独立。X共通の既存Deferred OPEN-312)。解消には共通核(LR再TTSのStyle保持)の修正=X Agent領域 |
| Y-F06 | Std用共有固定日本語 `point_explanation` を ensure_all_shared_narration_a2 が生成するが(er006_audio_cost_pilot_02_shared_narration.py:286-296)、Yのa2 timelineは読まない(er121_family_y_audio_01.py:782-790の narration辞書に無い。build_a2_key_phrase_blocksも不使用)。かつ _assert_shared_narration_ok(er019:1255)の対象で、これが非OKだとY a2のTTS stageがSTOPする。Y runでは Store再利用(reused=True, 生成0) | C(理由不明・記録なし) | 低 | なし(再利用中) | Store miss時のみ数円未満の無駄なJA 1 clip | 未使用clipの失敗でY a2が止まるリスク(発生実績なし) | Xとの共通呼出の副作用の可能性(所見)。Fable判断で『Yでは呼ばない』か現状維持 |
| Y-F07 | Y runnerの予算guardは『clip単位1回』(TTS_CLIP_EST_JPY=1.0、_guarded: er121_family_y_audio_01.py:252-263, runner:985)で、clip内のretry/cooldown/LR再TTSは個別にguardされない(clip内の上限はER-011累積15・API STOP guard[runner:1294]のみ)。実測: E-1 b1b y_voice_1 stage 5.579円(7 attempt+LR)、Y累計約166.85/Cap170(EVIDENCE_02 冒頭) | C(『新規API呼出の前に累計+見積』の呼出単位の記録なし) | 低 | なし | Cap近傍での超過余地 | なし | 方針: 現状は共通guardの設計。変更は費用管理の仕様変更のためFable判断 |
| Y-F08 | CURRENT_SPEC.md:2873『再生成②③(原稿・Prompt・モデル・Voice・速度を維持)』と、Std/JAの標準2+minimal1(3回目=Styleが変わる: er011:86-104、crosslevel:188-218)の関係が文書上で整合説明されていない(Section固有の既存例外一覧 L2885 にも2+1の記載なし)。Y影響: Std本文の3回目は常にminimal→Y GateでBLOCK(Y-F05) | C(仕様記録の整合不明) | 中 | Std 3回目の音声はStyle変更+要人間承認 | なし | Std HR増 | 共通核の仕様整合=X Agentの共通核記述と合わせてFableが判断。Yは変更不要 |
| Y-F09 | E-1で `approve_regenerate` を 『Fable権限による追加再生成の許可』名義で3 segmentに各1回実行(EVIDENCE_02.md §4に開示。approved_by="user"は不使用)。一方 er011:474-476 のdocstringは『ユーザーの明示的な指示でのみ呼ぶこと』。Fable名義の許容を定める規定: 本調査で特定できず | C(承認主体の規定未特定。実行は開示済み・NG音声の最終採用承認ではない) | 低 | なし | 再生成追加費用(5.58+13.75円) | なし | 判断候補(分類は27-3でFableが決定): 規定の明文化の要否。過去の同種運用がある場合は既判断Aの可能性 |

A(合理的差異・現状維持)の要約: 日本語にLRが無い(承認記載あり)、Key Phrase=4回構成・LRなし、KP解説=3回・LRなし、shared固定はStore再利用、Y本文のLR有効化はYL-C11/YL-A05(Fable設計+承認済み共通仕様のY適用)、Std本文6%減速と通算3予算共有、chunk配線(承認済み・実記事は構造的に不発火)。

## 9. OPEN起票候補文案(重複確認結果付き。SSOT編集権なし=文案のみ)
既存確認: OPEN-525(Repetition QA D'閾値)・OPEN-533(Algieba再生成率)・OPEN-527/532(Chunk)・OPEN-312(LR再TTSのrole style落ち)・OPEN-371(U4)・OPEN-517/520/531。
1. **Y-F01(Style profile)**: 既存OPENにY STYLE_PROFILE=defaultを指摘する項目は見つからず(Grep `STYLE_PROFILE|fx_20261017` in OPEN_ITEMS: Yの項目なし)。文案『FAMILY-Y-STYLE-PROFILE-WIRING-CHECK-01 [11-8分類=修正へ進む候補(Bの疑い)]: Y runnerがSTYLE_PROFILE=defaultで、DESIGN_01.md:84/YL-A01(APPLY)・CURRENT_SPEC.md:1699付近の『Y化時に最初から配線対象』と不一致。意図的除外の記録の有無を確認→B確定なら配線とStd/Adv再生成要否を見積』。次委任案: Fableが除外記録の有無を確認(read-only、30分)。
2. **Y-F02**: 新規OPEN不要(OPEN-532/PM-SSOT-SYNC-04に包含)。CURRENT_SPEC.md:2954,2963の更新とer121_family_y_audio_01.py:17のコメント訂正を同期作業に含める。
3. **Y-F03/F04**: 新規OPENにせずOPEN-525へ追記する案『Repetition QA単独NGはLRが発動できずHR直行(NO_NG_SPAN)、かつHR queue行が書かれない』。分類=ユーザー判断要の可能性(D: 方式新設)。重複: OPEN-525は閾値・境界のみ、OPEN-533は再生成率のみで、この2点は未記載。
4. **Y-F05/F08**: 既存OPEN-312(Deferred)に『Y本文でもGate BLOCKとして顕在(E-1で2 segment)』を追記する案。新規不要。
5. **Y-F06/F07/F09**: 低重要度。Fable判断で『実害なし・追跡のみ』または不要。

## 10. 所見(事実ではない)
- (所見1)Y本文の失敗の主因はASR不一致ではなくRepetition QA D'の閾値境界(E-1 b1b 7 attempt中6、a2は標準全attempt: OPEN-525)と、Algieba固有の旗率の高さ(OPEN-533)に見える。この型はLRの前提(NG spanの存在)を満たさないため、LRは救済になりにくい。『3NG→LR』フローはY Voice 1に対して実質『3NG→HR』として働く可能性が高い(E-1はこの型で、ハイフン差という偽spanによりLRが発火していた。是正後は書換えなしHR)。
- (所見2)Y Gateの LOCAL_REWRITE_RECOVERY / STD_FALLBACK BLOCKは、Style落ち(OPEN-312)を人間承認なしに通さない点で品質保護として合理的だが、Std本文では3回目到達=必ず人間承認になる(Delivery負荷)。共通核でLR再TTSとfallbackがroleのStyleを保持できれば、このBLOCKを緩める余地が出る(承認済み品質基準を変えない方向。X Agentの共通核記述と併せて検討)。
- (所見3)Yのretry/LR/cooldownは共通核の挙動そのもので、Y固有のコードはGate(音声採用側)にだけある。Yの回帰リスクは『共通核の変更がYにも波及する』点にあり、Yにはsegment id→role解決のtest(er121_family_y_structure_match_test_01.py:205-213)があるが、LR/cooldown/retryがY idで end-to-end に動くtestは無い(YL-A05の確認項目『retry/Local Rewrite/HR LockがY IDで発動するtest』に対しては、E-1のruntime evidenceが代替になっている)。
- (所見4)Adv支援文(topic_intro/preview/comment)の narrator Voiceは voice01.CHARON='Charon'(voice01.py:44)固定で、Y本文のnarratorは p9a.VOICE_NAME(コメント上 'Aoede')。X共通の設計で本監査の範囲外だが、Y音声の一貫性に関わる可能性がある(未検証)。
- (所見5)`stop_retrying`によるLR/HR早期遷移は cascade有効時に撤去済み(AUW)。Yのすべての呼出しは cascade_enabled=True 既定(er006_secondary_asr_01.py:297)なので、LRは常に『通常枠使い切り後』にだけ働く。

## 11. 古いルールの残存・矛盾(Chunk Std拡張2026-10-26後のY経路、Y Voice Trial観測との差)
- 残存(文書): CURRENT_SPEC.md:2954,2963(Y-F02)。コード内コメント: er121_family_y_audio_01.py:17(Y-F02)。
- 撤去済み(確認): `CHUNK_TTS_Y_LEVELS`の旧`("b1b",)`限定は撤去(er121_family_y_structure_01.py:109-113コメント)。Comment 2のAdvからの削除は`Y_SUPPORT_NAMES['b1b']`に反映(同:240-251)。Grep `comment_2` in Adv経路: er121_family_y_audio_01.py の Adv分岐に `comment_2` 参照なし(support_namesが導出)。
- Y Voice Trial(PAUSE-CAUSE-01/MALE7-01)との差: 両Trialは『正式経路のretry規則を尊重』(PAUSE-CAUSE DESIGN_01.md:54: 3回目前に10分cool-down)で生成しており、規則との差なし。MALE7でAlgieba旗率72%・最終OK率38%・平均2.31 attempt/take(RESULT_01.md:299, OPEN-533)は本書のY-F03と同根の観測。

## 12. 参照文書・Git履歴
- `git log --oneline --since=2026-10-01 -- er121_family_y_audio_01.py er121_family_y_runner_01.py` の結果: d00f41c8b(Std chunk Opus反映)/7ca0df0ad(Std chunk配線)/28bad7b33・4ffdf7600(Comment 2削除)/fb768a357・d2bbce56c(E-1再走・Part1/2接続)/89b630bd1(Chunk/案B)/4437e98cf・7d5b9f8fc(runner/audio新設)。
- 参照: CURRENT_SPEC.md L2176,2873,2885,2886,2954-2963,3057-3070,1699; DECISION_LOG.md L21941-21944,22426-22535; OPEN_ITEMS.md L815,880,1035,1040,1046-1048; USER_DECISION_REGISTER_01.md L22-26; docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{DESIGN_01,SPEC_LEDGER_03,EVIDENCE_01,EVIDENCE_02,E1_HUMAN_REVIEW_01,REWRITE_EVIDENCE_01}.md; docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/CHUNK_WIRING_CHECK_01.md; docs/research/FAMILY-Y-VOICE1-{PAUSE-CAUSE,MALE7}-TRIAL-01/DESIGN_01.md; docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md。
- 注意(同名の別機構): `REWRITE_EVIDENCE_01.md`・Y runnerの『Closing局所書換え』(er121_family_y_text_core_01.py: 判定→局所書換え→再判定、判定≤3)は**テキスト生成段のClosing Gate**であり、TTSのLocal Rewriteとは目的・動作が別。本棚卸しの対象外。

## 13. 範囲外で読んだファイル(事前指定一覧外)
er003_v1_sing01_voice01_generate.py / er003_v1_sing01_news_tail_fix.py / er003_v1_crosslevel_audio_02_common.py / er003_v1_n3_01_tts_generate.py / er003_v1_n3_01_assemble.py(Gate) / er003_v1_repro01_main_generate.py / er006_secondary_asr_01.py / er006_audio_cost_pilot_02_shared_narration.py / er011_human_review_lock_01.py / er019_family_x_audio_production_runner_01.py / er019_family_x_style_profile_01.py / er104_kp_vote_reuse_01.py / er104_kp_three_asr_vote_01.py(flag) / er121_output/** の tts_generation_results.json・review_lock_state.json / er011_output/attempt_history.jsonl / HR queue 2種 / docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/** / docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md / 2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md。いずれもread-only。
