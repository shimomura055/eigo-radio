# CONDITIONS_01: 現行Production呼出条件の特定(FAMILY-X-TTS-VOICE-TONE-BRIGHTNESS-TRIAL-01 委任_01)

Production変更なし。実コード読取のみ。Trialは下記を同一条件で呼ぶ(`tone_trial_01.py`)。

## 1. Style指示文(実コードとの一致確認)
| 項目 | 実コード | 一致 |
|---|---|---|
| 日本語 J0_CURRENT | `er033_tts_flash_lite_family_x_styles_01.py` L94-97 `FAMILY_X_ROLE_STYLE_JA`(Production名J3) | 一字一句一致(script内assertで確認、assert通過) |
| 英語 E0_CURRENT | 同 L41-48 `FAMILY_X_ROLE_STYLE_EN["PREVIEW"]`/`["COMMENT"]` = `calm, conversational` | 一字一句一致(assert通過) |
差異なし(Trial案の文は無変更)。

## 2. 呼出経路(ファイル・関数・行)
- 日本語Standard(Aoede): `er019_family_x_audio_production_runner_01.py` `generate_family_x_a2_segments`(L825-)内 `_role_style_ja()`(L902-905、`tts_backend=="speech_metadata_flash_lite"`時のみ`FAMILY_X_ROLE_STYLE_JA`)→ preview/comment_1-4(L957-962) → `er003_v1_n3_01_tts_generate.generate_a2_japanese_with_reading_safety`(L589) → `generate_a2_japanese_with_fallback`(L473) → `er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict`(L196) → `er003_b1_p9a_audio.generate_narration_snippet`(L199-)。JAは**日本語側にpronunciation Ledger style注入なし**(styleはそのまま`speech_metadata.style`)。
- 英語Advanced Preview/Comment(Charon): `er019...runner` `generate_family_x_b1_segments`(L559-)内 L636-646 `style_prefix_override=_role_style("PREVIEW"/"COMMENT")`(=`calm, conversational`、flash-lite backend時のみ。既定backendは`B1_PREVIEW_STYLE_PREFIX_CALM`)→ `er003_v1_sing01_voice01_generate.generate_charon_english`(L47-)。注入形式: `enable_pronunciation_resolver=True`により`resolve_and_augment_en_style_prefix`→`augment_style_prefix_with_pronunciation`(`er006_pronunciation_tts_injection_01.py` L52、Ledger cache hitがある時のみstyleへヒント追記。Trial文では該当hit 0=styleは無改変)。
- 実際のTTS呼出: `er033_tts_flash_lite_backend_wiring_01.resolve_tts_call_and_prompt`(L357-411): prompt=`(text, style_prefix)`のtuple、`types.SpeechMetadata(style=style)`を`Part.speech_metadata`へ渡す(`make_speech_metadata_batch_call_fn` L219-/`make_speech_metadata_call_fn`)。
## 3. パラメータ表(全案共通)
| 項目 | 値 | 根拠 |
|---|---|---|
| model | `gemini-3.8-flash-lite-tts` | `fls.FAMILY_X_FLASH_LITE_MODEL_NAME`、`flw.resolve_actual_model_name` |
| backend | `speech_metadata_flash_lite` | runner `--tts-backend` |
| voice | JA=Aoede(`p9a.VOICE_NAME`) / EN=Charon(`voice01.CHARON`) | |
| language_code | `en-us`(`common.LANGUAGE_CODE`、Production現行どおりJAにも同値) | `er002_common.py` L55 |
| 速度 | 変更指示なし(speaking rate設定なし。A2のfull_story/in_one_lineのみ6%減速=別経路で本Trial対象外) | n3 `generate_a2_japanese_with_reading_safety`にslowdownなし |
| trim | `trim_english_keyword_silence`、safety margin 0.35秒(JA=`NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS`、EN=`voice01.SAFETY_MARGIN`) | |
| 異常長検知 | `safety.detect_duration_anomaly`(ENは結果記録、JAはp9a内で実行) | |
| 音量正規化 | Production assembly `apply_family_x_a2_gain`(L1367-)と同じ`compute_gain_for_target_rms`(max_peak=0.95)。Trialでは言語内の目標RMS=現行案(J0/E0)のRMSで各案へ同関数を適用(追加加工なし、clip回避のみ) | |
| headroom | assembly段(`apply_headroom_safety_valve`)はエピソード結合時のみのため単体サンプルでは非該当 | |
| 実行方式 | Production既定=**BATCH**(`resolve_tts_execution_mode`既定、`er006_batch_tts_wiring_01.py` L74)。Trialは開発方針(PM_GOVERNANCE 7節 DEV Standard同期)に従い`TTS_EXECUTION_MODE=STANDARD`。同一backend関数で出力音声は同モデル・同voice・同style経路(差は実行方式のみ、単価はStandard) | |
| technical retry | `common._call_tts_with_retry`(`MAX_TTS_TECHNICAL_RETRY`)は維持。Trialの品質再生成は無し(各案1回) | |
| ASR | `routing.transcribe`(Production primary ASR、gpt-4o-mini-transcribe系)1回。判定: JA=`classify_ja_asr_match`、EN=`classify_asr_match`。Cascade/多重照合なし | |

## 4. 既存音声の再利用可否
原稿が新規(「コーヒーの価格は…」は既存Family X音声と同一原稿+同一style+同一backendのMaster Store/保存音声なし)のため再利用不可。8本すべて新規生成。Master Store・review_lock・human_review_queue・cost_loggerへは書込みなし(Trial専用script、cost_logger未install)。
