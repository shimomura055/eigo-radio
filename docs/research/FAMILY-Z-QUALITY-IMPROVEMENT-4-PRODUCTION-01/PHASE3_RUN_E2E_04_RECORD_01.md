# PHASE3_RUN_E2E_04_RECORD_01(委任_07、2026-10-19、事実のみ。状態=STOPPED_AT_tts_a2_HR_LOCK)

## 実走
- run_e2e_03へSTOPセンチネル設置(commit 3be22c7c3)。`*_prompt_gen350.txt` 4件退避(run_e2e_03/writer、copy時にrun_e2e_04/writerへも複製)。
- copy: `copy_reusable_run_assets`(ALLOW 64 / DENY 324。計画=`run_e2e_04_copy_plan_07.json`)。stop_scope_check rc=0(`run_e2e_04/stop_scope_check_fzqi7.json`、直前`..._prerun.json`)。
- runner: 1回のみ起動(background、再起動0)。`--run run_e2e_04 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD --regenerate-stage support_a2`、`TTS_EXECUTION_MODE=STANDARD`。開始11:31 JST・終了12:15 JST、所要2679秒(44.7分、うちclip再試行cooldown 600秒1回)。console=`run_e2e_04/run_07_console.log`。
- 結果: rc=2。seed_check/writer/std_adjust/plan/support/kp/tts_b1b は完走。**tts_a2 でStd `full_story_part3_c1` が STOPPED**(`FamilyZTtsClipFailedStop: FAMILY_Z_TTS_CLIPS_NOT_OK(a2)`)。以降(provision_shell/gate/assemble/pages/page_verify)は未実行。a2 review_lock_state: part3_c1=`HUMAN_REVIEW_REQUIRED`(HR Lock、迂回せず)。
- 原因(観測): Std TTS(gemini-3.8-flash-lite-tts)が"Melos drank"を"Melo strained/Mello drank/Mellows drank"と読み、OpenAI/Azure ASRとも不一致(attempt1 TRUE_CONTENT_MISMATCH、attempt2・Pro fallback ASR_VALIDATION_UNCERTAIN、asr_judgement NG_BOTH/secondary_not_accepted)。3 attempt(うち600秒cooldown1回)後STOPPED。他のa2 28 clip・b1b 30 clipはOK。

## 費用(`audit/cost_by_stage_04.json`、実測、本件枠JPY80、他枠分離)
合計JPY46.1364/80: kp_gloss_person_repair 0.0557(LLM) / support 0.249(LLM) / tts_b1b 26.24 / tts_a2 19.5917。種別: TTS(gemini)22.5846 / ASR(azure)18.475 / ASR(openai)4.175 / LLM 0.9019(うち writer/std_adjust/plan/kp_expl LLM 0)。

## runtime evidence(取得済み分)
- ①: a2 rank2 gloss: 旧「あなたの代わりに」(run_e2e_03)→新「誰かの代わりに」、`gloss_alignment_status=ALIGNED`、`a2_result.json.person_gloss_repairs[0]`(version ER-003-KP-GLOSS-PERSON-ALIGN-01、alignment_status ALIGN_PASS、cost 0.0557)。
- ②: `support/a2_support.json` method=`adv_method_ja_v1`、lint_warn={preview:[LISTEN_INSTRUCTION], comment_1:[LISTEN_INSTRUCTION]}、ngram4_overlap={}。新Comment1=「メロスが友人に何を約束し、そのあとどう行動するのかに注目してください。」/Comment2「メロスは、友を人質に残して三日以内に戻ると約束しました。…」/Comment3「メロスは疲れきって、立ち上がることさえ難しくなっていました。…」。Preview新=「恐れから人を罰し、話す機会を与えない支配者に、メロスが向き合います。…」。旧は`run_e2e_03/support/a2_support.json`(全文対照は同2ファイルを参照)。
- ③: Std Dialogue 10 clip全てOK、`effective_style_prefix_sha256`=add26d27…(Adv 11 clipと同一)、label=`existing_dialogue_style(ENGLISH_STYLE_PREFIX)+post6%`、slowdown_applied=True、ratio 1.0537〜1.0581(範囲[1.03,1.09]内)。part1_c8(王)=Std 7.163秒/Adv 7.281秒(参考、旧 Std 8.645/Adv 5.641)。Voice(Algieba/Charon/Erinome)割当は両levelで継続。
- ④: writer/std_adjust は cost_log に行なし(reused)。`writer/provenance.json` output_sha256 は run_e2e_03由来。
- 未取得: Style表・全clip exp_match・Pages・標準適合check・公開URL実再生・Regression(STOPのため未実施)。
