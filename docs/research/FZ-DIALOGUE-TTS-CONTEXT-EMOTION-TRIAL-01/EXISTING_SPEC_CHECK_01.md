# EXISTING_SPEC_CHECK_01 — FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01 (Phase 0、API 0)

- ユーザー原文: `docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_USER.md`。委任文: 同 `_DELEGATION_01.md`。
- タグ: [確認済み: path:line] = 実ファイル/コードで確認。本書はProduction変更0・TTS 0・LLM 0。

## 1. 先行調査の結論(INVESTIGATION_01 / EVIDENCE_01)の引継ぎ

- 現行ZのセリフTTSは、**1セリフ(引用符つき)+全dialogue共通の汎用style**だけを渡す。前後の会話・地の文・感情・場面は一切渡らない [確認済み: `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01/INVESTIGATION_01.md` §1-§3, EVIDENCE_01 §1]。
- TTSへ送った全文promptは保存されていない(`tts_generation_results.json`はstyle sha256のみ)。先行調査はProduction関数から再構成し、**今回の再確認でも sha256 が一致**: `ENGLISH_STYLE_PREFIX` sha256=`add26d27a79c2cbee982eb5ddc32616b8294494a316b973215c94cccc76ede26`(`tts_generation_results.json` `style.effective_style_prefix_sha256`と一致)、『Please let him still think I'm pretty,』のprompt全体 sha256先頭=`8c917f335f2be3f5`/2294字(EVIDENCE_01 §1と一致)。testで固定(`er118_..._test_01.py::StyleTests::test_base_style_is_production_default_and_prompt_matches_recorded_sha`)。

## 2. TTS入力の構成(Structured Separation)

- `er003_b1_p4c_audio.py:78-100 build_tts_prompt(text, style_prefix)`: 「STYLE INSTRUCTIONS(読み上げ禁止)」区画 + 「TEXT TO SPEAK(これだけ読む)」区画の2区画。ER-005-AUDIO-INSTRUCTION-SEPARATION-01(DECIDED)の構造。**本Trialはこの関数を無改変で使い、STYLE区画の中身(=style_prefix)だけを②で拡張する**。TEXT区画は①②で逐語同一(testで検証)。
- dialogue style = `er002_common.build_style_prefix()`(1842字)→ `er003_b1_p9a_audio.ENGLISH_STYLE_PREFIX` [確認済み: `er012_b_family_voices_production_01.py:519-520` `p4c.build_tts_prompt(text, style_prefix_override or p9a.ENGLISH_STYLE_PREFIX)`、Zのdialogueは`style_prefix_override`を渡さない(`er063_family_z_audio_01.py:790-795 style_text_for` dialogue→None、`:924-929`)]。
- `style_prefix_override`は`generate_voice_body_wide_margin`の**既存の公開引数**(`er012_b…:483-`)。本Trialの②は**この既存引数にCONTEXT付きstyleを渡すだけ**で、Production関数・Prompt定数・正規表現・閾値を編集しない。

## 3. 生成条件(①の実行記録 = ②が一致させる条件)

| 項目 | ①の記録(Magi Adv) | 根拠 |
|---|---|---|
| model | `gemini-2.5-pro-preview-tts`(narratorは別model) | `tts_generation_results.json` attempts `tts_model_id`、`attempts/*.json` `model` |
| 実行mode | `STANDARD`(同期API) | `b1b/narration/attempts/full_story_part2_c7_attempt1_englishstyleprefixwidemargin.json:15` `tts_execution_mode`。既定は`BATCH`(`er006_batch_tts_wiring_01.py:74-85 resolve_tts_execution_mode`)なので、**②のprocessは`TTS_EXECUTION_MODE=STANDARD`を明示**(`capture_tts_requests`が設定し終了時に復元。記録に実modeを保存) |
| 呼出関数 | `er003_b1_p7a_audio.make_tts_call_fn_for_model` | `er006_batch_tts_wiring_01.py:88-103`。`response_modalities=["AUDIO"]`+`speech_config(language_code=en-us, prebuilt voice)`+`http_options(timeout=150s)`。**temperature等のsampling設定は未指定**(SDK/モデル既定)。②も同一関数を通すので同一 |
| Voice | della=Zephyr / madame=Kore / jim=Algieba | `the_gift_of_the_magi/run_sf_prod_01/voice_assignment.json`(APPROVED_FOR_PRODUCTION 2026-10-23)。注意: `segment_plan`の`clip["voice"]`は話者key(`della`等)でありVoice名ではない。モジュールは`voice_assignment.json`から引き(`tts_voice()`)、testで①の実生成Voiceと全8件一致を確認 |
| 本文整形 | `tts_safe_news_en`→`_pnap_supply`(`er063:815-818`) | モジュールは`er063._norm_for_tts`を直接使う |
| 生成関数 | `bvoices.generate_voice_body_wide_margin`(ASR・Cascade・Repetition QA・最大3回、`er012_b:483-`)。Advは外側に`generate_with_a2_slowdown_outer_loop`(atempo=1.06)(`er063:921-929`) | ②は内側関数を直接呼ぶ=**速度加工前の原音**が比較対象(①は`*_original.wav`) |
| attempt数 | 8件すべて attempt1で採用、minimal_fallback 0 | `existing_audio_record()`(testで`attempts==1`) |

## 4. 既存Magi音声の所在(①の素材。読み取りのみ)

- Adv(b1b)dialogue 8 clip、すべて`er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/`:
  - 原音(速度加工前): `full_story_{part2_c2,c4,c5,c7, part3_c2,c4,c6,c8}_original.wav`。**`attempts/*.json`の`sha256`と一致**(testで全件確認)。これが①(Style以外が②と同条件)。
  - 最終音声(atempo=1.06適用後): `full_story_*.wav`(公開版・今回は比較に使わない)。
  - ASR結果: `tts_generation_results.json` `segments[clip].asr_text`/`asr_judgement`(全8件PASS。Madame『Twenty dollars.』のみprimary labelが`ORTHOGRAPHIC_EQUIVALENT_MATCH`(ASR転写`twenty dollars`)で、attempt log上の`audio_classification`欄は`TRUE_CONTENT_MISMATCH`だがjudgeはPASS=既存の記録。本Trialの結論に影響しない)。
  - 具体値(sha256・ASR・gain)は`SELECTION_01.md`。
- Std(a2)のdialogue clipも8件(Della 6/Madame 1/Jim 1、`a2/narration/full_story_part1_c2,c4,c5 part2_c2,c4 part3_c2,c4,c6.wav`)だが、**文面はAdvの言い換えでカテゴリが重複**するため今回は補わない(Advの8件で全カテゴリを網羅できる。『機械的網羅で不自然に増やさない』)。

## 5. 再利用の仕組みと、Trial内での確実な分離

- **Master Audio Store**: Z会話は経路上に登録呼出が無い(`er063_family_z_audio_01.py`/`er012_b_family_voices_production_01.py`/`er003_v1_n3_01_tts_generate.py`に`master_audio_store`/`audio_store`のGrep一致0。`er063:257,1776`に『Master Store書込なし』と明記)。
- **Zの再利用**: `er063:798-814 build_reuse_key`の`style_prefix_sha256`は`style_prefix_sha256(style_text_for(spec))`で、dialogueは`style_text_for`が常にNone→**dialogueのstyle hashは常にNone**(実記録でも`reuse_key.style_prefix_sha256=null`)。再利用は前回runの`tts_generation_results.json`のcached_entryとreuse_keyの完全一致で起き(`er063:840-866`)、②のStyleを変えてもreuse_keyが変わらず**①の保存音声が返る**(先行調査の指摘どおり。`ReuseSeparationTests`で`production_reuse_key_for`が①②で同一(style=None)であることを実コードで確認)。
- **分離方法(Productionの再利用仕様は変更しない)**:
  1. Production再利用経路(`run_tts_stage`/cached_entry)を**呼ばない**。Trialは`generate_voice_body_wide_margin`を直接呼ぶので再利用判定が構造上存在しない。
  2. ①は`*_original.wav`の**読み取りのみ**(`existing_audio_record`、sha256固定)。②の出力先は`er118_output/fz_dialogue_context_tts_trial_01/gen/<arm>_t<take>/<clip>/b1b/narration/`(DEV専用dir)。Production run dir・Master Store・`tts_generation_results.json`へは書かない(before/after sha256 snapshotでSTOP判定。`snapshot_protected`)。
  3. Trial内の識別keyは`trial_reuse_key()`(Trial ID・arm・take・**style_sha256**・text sha・Voice・model)。①②でstyle_sha256が異なり、同一armの別takeも区別される(testで確認)。
  4. 実送信promptのsha256が期待prompt(`build_prompt`)と一致することをrequest記録ごとに保存し、②のStyle追加情報がTTSリクエストに渡った証拠とする。

## 6. 副作用の隔離(Production sink)

`generate_voice_body_wide_margin`の内部は`review_lock.save_tts_attempt_audio`・`attempt_history`・ASR cascadeのtelemetry・Pronunciation Ledgerへ書く。`er113_fx_paragraph_chunk_trial_01.redirect_production_sinks(dev_dir)`(既存DEV helper、実績あり)でこれらをTrial dirへ向け、`snapshot_protected`(+Magi run音声/results/plan)でbefore/afterを照合する。

## 7. 本Trialが触らないもの(Grep・差分確認用)

- Production file/Prompt/flag/Seed/再利用仕様: 編集0(新規2ファイル+docs+OPEN行のみ)。
- 既定値: 新flagなし。`gen`/`llm`はGO(`PHASE1_GO.json`)が無い限り起動しない(`GuardTests`: GO無しで呼ぶとSystemExit・副作用ファイル0・`raw_usage_log.jsonl`作成0を検証)。
- Family A/B/C: 触れない(27-7)。
