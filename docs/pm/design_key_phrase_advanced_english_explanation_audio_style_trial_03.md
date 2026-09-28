# design_key_phrase_advanced_english_explanation_audio_style_trial_03.md

管理ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03
性質: Trial(音声Styleのみ)。Production採用・配線は行っていない。

## 1. 前提・スコープ

- Advanced Key Phrase英語解説の**text仕様**はユーザーが正式採用済み
  (`APPROVED_FOR_PRODUCTION`、KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-
  TRIAL-02のB候補5件)。ただしProduction wiringは未実施(OPEN-221は
  引き続きOPEN)。
- 本Trialは**音声Styleだけ**を比較する: Before=`clear, precise,
  explanatory` / After=`clear, precise, unhurried`。Phrase・解説文の
  再生成/再選定は一切行わない(Hormuz既存5 Phrase、TRIAL-02のB解説文を
  逐語使用)。

## 2. Beforeのreuse判定(machine-verified)

`er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz/
audio_summary.json` の `generated_new_explanation_audio[*]` を確認した
結果、5件全て:
- `style_prefix_used == "clear, precise, explanatory"`(完全一致)
- `en_pronunciation_resolver_info.hints_applied == False`
  (発音resolverによるstyle augmentation無し、TTSへ渡された最終文字列
  はraw値のまま)
- `status == "OK"`

以上より、Before音声はer041が生成したwavをそのまま**コピー再利用**し、
新規TTS callを行わない(`er042_....py::verify_before_style_reusable()`
で機械検証、不一致ならSystemExitでSTOPする設計)。Phrase EN音声も同様に
er041出力配下の既存コピーを再利用する。

## 3. Afterの新規生成

Production同一関数`er003_v1_repro01_main_generate.
generate_narration_snippet_verified_strict`をTrial Store隔離
(`er038_tts_all_spoken_role_style_trial_01.trial_master_audio_store`)・
`style_prefix_override="clear, precise, unhurried"`で呼び出し、既存ASR
cascade(`max_attempts=2`、既存値のまま変更なし)を通す。5件とも
`status=OK`、`retry_count=0`、`asr_verified=True`。
`en_pronunciation_resolver_info.hints_applied`も5件ともFalseであり、
実際にTTSへ渡された最終文字列は`AFTER_STYLE`定数のまま(augmentation
無し)。

## 4. Production非接触の設計

- Key Phrase選定ロジック・DB Hybrid・Production Master Audio Store
  (`er006_output/master_audio_store_01/`)は一切import・変更しない
  (test `ProductionIsolationTest`で機械検証)。
- `TTS_EXECUTION_MODE=STANDARD`明示必須(未設定時はSystemExit)。
- Trial専用Store: `er042_output/key_phrase_advanced_english_
  explanation_audio_style_trial_03/master_store`(生成物なし、er041と
  同型の挙動、Store側の永続化トリガー無しは既存precedent通り)。

## 5. 試聴ページ

`user_test/kp_advanced_explanation_audio_trial_03/index.html`
(生成: `er042_key_phrase_advanced_english_explanation_audio_style_
trial_03_page_01.py`、wav→mp3変換はlameenc、既存precedent
[`er040_tts_fixed_shell_master_champion_trial_01_page_01.py`]と同じ
判断枠組み、ffmpeg不要)。5 Phrase × [Phrase EN音声/英語解説text/
Before音声/After音声/実際に渡したStyle文言全文/duration/ASR結果]を表示。

## 6. 既知の関連OPEN

- OPEN-221: `KEY_PHRASE_EXPLANATION_EN`のProduction未実装(引き続き
  OPEN、本Trialでも配線せず)。
- OPEN-223: Trialが共有固定path(Human Review Queue等)を隔離せず使う
  既知の限界(本TrialもMaster Storeのみ隔離、Human Review Queueは
  未隔離。ただし本Trialは5件ともstatus=OK・retry_count=0で
  Human Review Lockに到達しなかった)。
