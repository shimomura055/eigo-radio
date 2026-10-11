# CONDITIONS_01: Full Story Tone Trial(FAMILY-X-TTS-FULL-STORY-TONE-TRIAL-01 委任_01)
Production変更なし。実コード読取のみ。
- 現行経路(Standard/Aoede): `er019_family_x_audio_production_runner_01.py` L975-985 `n3_tts.generate_a2_segment_with_slowdown`(L197、`tts_safe_news_en`で入力正規化→`generate_english_segment_with_fallback`→`apply_a2_slowdown_postprocess`6%減速)。style=`_role_style_slower("FULL_STORY")`(L875-、`FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`+`A2_SLOWER_PACE_INSTRUCTION`連結)。
- 本Trialの通常速度化: slowdown関数・`_role_style_slower`連結・post-process 6%減速は使わず、同系列内部の `er003_b1_p9a_audio.generate_narration_snippet(text,"en",...,style_prefix_override=<Style>,tts_backend="speech_metadata_flash_lite")`(voice=Aoede=`p9a.VOICE_NAME`、trim margin=`NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS`0.35、language_code=`common.LANGUAGE_CODE`、`_call_tts_with_retry`技術retry)を直接呼ぶ。Review Lock/Master Store/human_review_queue書込を伴う`verified_strict`は経由しない。
- 入力正規化: Production `n3.tts_safe_news_en(原稿)`(全4案共通、引用符"“”"除去・段落結合等)。
- F0 Style = `FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]` と一字一句一致(script内assert通過)。
- 実行方式: TTS_EXECUTION_MODE=STANDARD(DEV同期、Production既定=BATCH)。
- 音量: F0のRMSを目標に`compute_gain_for_target_rms`(max_peak=0.95)のみ。
- ASR: `routing.transcribe`(1回)+`classify_asr_match`、多重照合なし。
