# MELOS_REGEN_RUN_E2E_06_RECORD_01(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_01、2026-10-20、事実のみ。Status=`PL_WEIGHT_2_WIRED_MELOS_REGENERATED_PENDING_FABLE`)

## 実走
- run_e2e_06作成: `copy_reusable_run_assets(run_e2e_05→run_e2e_06)` copied 66 / denied 324(writer/plan/support/kp/動的設定を再利用、tts_b1b/tts_a2は全clip新規=tts_generation_results.jsonなし)。`writer/provenance.json` `audio_text_deviations=[]`。`stop_scope_check_plwp1.json` rc=0(STOP_ALL不在)。
- runner: 1回のみ起動、再起動0。`TTS_EXECUTION_MODE=STANDARD ... --run run_e2e_06 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD`、console=`run_plwp1_console.log`(Traceback 0)。開始 2026-10-20 10:37:43 JST / 終了 10:52:14 JST(約14分31秒、page_verify 178秒を含む)。stage完走(seed_check〜page_verify 13 stage、`e2e_stage_log.jsonl`)。
- stage別所要: tts_b1b 344.9s / tts_a2 321.6s / provision_shell 0.2s / gate 0.5s / assemble 1.9s / pages 10.5s / page_verify 177.9s。名称: ディレクトリ`a2`=Standard、`b1b`=Advanced。

## clip結果(`{a2,b1b}/audit/tts_generation_results.json`、集計=`run06_clip_evidence_01.json`)
- **全77 clip status=OK**(Standard 38 + Advanced 39)。`review_lock_state`: a2 39 key・b1b 40 key全RESOLVED。TTS 2回生成=a2 comment_3の1clipのみ(Std/Adv他は全て1回)。cooldown/Pro fallbackの追加発生は無し(model_ids_measuredはrun_e2e_05と同一分布: flash-lite a2 19・b1b 19、pro-preview a2 10・b1b 11)。
- asr_judgement集計: Standard = PASS/primary_pass 17・PASS(approved equivalence READING_MATCH 2 / TIER1_DIFF_ANCHORED 1 / TIER1_NUMERIC_EQUIVALENCE 1)・PASS_WITH_WARNING/primary_pass 5・PASS_WITH_WARNING/secondary_confirmed 3・固定clip等(判定なし)9。Advanced = PASS/primary_pass 22・PASS(TIER1_NUMERIC_EQUIVALENCE 1)・PASS_WITH_WARNING/primary_pass 6・PASS_WITH_WARNING/secondary_confirmed 1・判定なし9。
- Voice/Style: run_e2e_05とclip別に一致(Aoede/Algieba[Melos、PROVISIONAL_UNAPPROVED]/Charon/Erinome、Std PD06/S3/X_J3、Dialogue `existing_dialogue_style(ENGLISH_STYLE_PREFIX)`[Stdは+post6%]、Adv E1/E2_UPBEAT/PD06)。actual model_id: `gemini-3.8-flash-lite-tts`/`gemini-2.5-pro-preview-tts`(TTS)、ASR=`gpt-4o-mini-transcribe`(Primary)+`azure-speech-stt`(Secondary)、LLM補助=`gpt-6-luna`(a2のみ6 call、JPY0.0384)。
- Azure Phrase List重み: `azure_phrase_list_weight=2.0` / `azure_phrase_list=["Melos"]`をruntime記録(attempt_history 4行[a2 part1_c9 secondary_1 ×2、a2 part3_c1 secondary_1、b1b kp4_en=PL空で`null`]、attempt別json 3件)。run_e2e_05では0件(キー自体なし)。Secondary使用clip(EN): Std part1_c1/part1_c9/part1_c11/part3_c3・Adv comment_1/part1_c1/part1_c9/part1_c11/part2_c1/part3_c3/kp4_en。全てPythonコード`setWeight(2.0)`を通る(DEV wire evidence `dgi.bias=2.000000`で送信確認)。監査キーの個別記録が残るのは上記一部(Cache hit・step保存範囲による)。
- Tier3/M1: Tier3(approved equivalence)=Std TIER1_DIFF_ANCHORED 1(part2_c1)・TIER1_NUMERIC_EQUIVALENCE 1、Adv TIER1_NUMERIC_EQUIVALENCE 1、JA READING_MATCH 2。M1 `M1_MULTI_CANDIDATE`警告=Std part1_c5・Adv part1_c5。CS層(`CONNECTED_SPEECH`警告)=Adv kp3_explanation_en。
- PASS_WITH_WARNING listening list(`*/audit/pass_with_warning_listening_list.json`): Standard 8件(japanese_title・preview・comment_2・part1_c1・part1_c5・part1_c9・part1_c11・part3_c3)、Advanced 9件(comment_1・part1_c1・part1_c5・part1_c9・part1_c11・part2_c1・part3_c3・kp3_explanation_en・kp4_en)。run_e2e_05は Std 8 / Adv 4。Adv増加5件は全てSECONDARY_CORROBORATED/SECONDARY_CONFIRMED/CONNECTED_SPEECH=Secondary裏付けのPASS_WITH_WARNING(新規clipの転写差。重み2.0が単独原因かは本runの比較だけでは切分け不能=未確認)。
- **part3_c1(委任の焦点)**: Standard = 1回生成、転写 `…Melos drank, got onto his knees, and stood up. …`、`NORMALIZED_MATCH`(PASS、primary_pass)、減速6%適用、採用テキスト=元原稿。run_e2e_05は`Mellos drank`で`SECONDARY_ASR_CORROBORATED_MATCH`(PASS_WITH_WARNING)だった。Advanced = 1回生成、転写 `…Melo drank, pushed himself onto his knees, and stood. …`、`HIGH_SIMILARITY_SAFE`(PASS、primary_pass、既存判定)。run_e2e_05は`Melos drank`で`TIER1_DIFF_ANCHORED`。**Adv part3_c1の転写は`Melo`(sなし)でPASS_WITH_WARNING listening list外=事後試聴の注意事項**。`He drank`出現0、`audio_text_deviation`全clip 0。
- **Local Rewrite発火: 0**(`er011_output/local_rewrite_recovery/`にrun_e2e_06なし、`attempt_history.jsonl`の theme_id=run_e2e_06 102行にLR行なし)。①のlive evidence(`post_slowdown_expected_text_source=local_rewrite_text`)は未観測。
- HR: Human Review Lock 0、`human_review_queue.jsonl`のrun_e2e_06行0、Master Audio Store reuse_telemetry新規行0(Z経路は不呼出)。

## gate / assemble / pages / page_verify
- gate(`*/audit/gate_result_04C.json`): Std/Adv `shared_gate=PASS`、`m2_complete=True`、`audio_text_deviations=[]`。
- assemble: `a2/assembly/Family_Z_melos_a2.wav`・`b1b/assembly/Family_Z_melos_b1b.wav`(wavはcommit対象外)。
- pages: `user_test/family_z_melos_02/{index,standard,advanced}.html`と`audio_standard/`・`audio_advanced/`のmp3を更新(完成音声=`Melos_a2_full.mp3`/`Melos_b1b_full.mp3`、各section原稿行、Key Phrases、事後試聴リスト[PASS_WITH_WARNING]を各ページが含む)。
- page_verify(`page_verify_local.json`): `user_page_standard_check.overall=PASS`。standard.html audio 52 plays_ok 52 / advanced.html audio 53 plays_ok 53 / index.html 53。console_errors 全て0。`seek_ok_all=False`(3ページ、run_e2e_03/05と同じ前例・Gate項目外)。

## 費用(`audit/cost_by_stage_06.json`、`er026_fz_cost_17.py --cap 80`、cost_log 211件、全て実測usage換算)
- 合計 **JPY 27.5762** / 上限80(残52.4238)。runner stage log最終 27.5762 と一致。tts_b1b 12.7594(gemini 8.2099・azure ASR 3.4231・openai ASR 1.1264)、tts_a2 14.8168(gemini 8.3321・azure ASR 4.4995・openai ASR 1.9468・openai LLM 0.0384)。種別: TTS(gemini) 16.542 / ASR azure 7.9226 / ASR openai 3.0732 / LLM 0.0384。Web Search 0、failed_calls 0、usage未取得22件(azure ASR、推定値は含めず)。
- run_e2e_05比: 28.79 → 27.58(-1.21)。重み2.0による量産単価の増加は観測されず(Azure ASR呼出1回あたりの料金体系は重み非依存、azure 6.38→7.92はSecondary呼出数の差)。
- DEV wire evidence: Azure 1回(録音2、24.6秒)、約JPY1(24.6秒×Azure秒課金の単価換算の概算、`wire_evidence_cost_log.jsonl`)。
