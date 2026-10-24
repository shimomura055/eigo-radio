# RUNTIME_EVIDENCE_01 (FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_03、2026-10-24)

状態: **COMPLETE_USER_LISTENING_PENDING**(正式完成候補。ユーザー最終試聴待ち。PASS先取りなし)。
run dir: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/`(stage log=`e2e_stage_log.jsonl`、起動log=`run_launch_log.jsonl`)。

## 1. 正式入口・stage
- 入口: `er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_01 --mode real --approved-budget-jpy 70 --tts-execution-mode STANDARD`(Z正式Production経路・STORY_REGISTRY登録済み作品)。
- 委任_02: seed_check,writer,std_adjust / plan,support / kp(Adv OK、Std 外側retry 3/3でSTOP)。
- 委任_03起動(全て1起動1コマンド、rc=0): ① `--stages kp --regenerate-stage kp_a2`(22:42:55、案A=1回、約203秒) ② `--stages tts_b1b`(22:46:33、約205秒) ③ `--stages tts_a2`(22:50:09、約221秒) ④ `--stages provision_shell,gate,assemble,pages,page_verify`(22:53:59、約2分)。起動間隔>150秒、RESTART_STORMなし、STOP通知/センチネルなし(`docs/pm/delegation_log/2026-10-24_FZTTH3_stop_check.json` rc=0 applies=false)。再起動0回。案B(myself→oneself)は不要につき**未実施**(コード変更0)。
- 総所要: 委任_03分は約14分(22:42〜22:56)。

## 2. 使用モデル(actual model_id、最新原則 PM_GOVERNANCE 25節)
- Writer/std_adjust: gpt-6.1-sol(3+1 call)。plan/support/kp/gloss_alignment/NER等: gpt-6-luna。
- TTS: gemini-3.8-flash-lite-tts(narrator全clip、Std18/Adv16 call)+gemini-2.5-pro-preview-tts(old_man台詞1 clip/レベル、台詞専用)。ASR: gpt-4o-mini-transcribe(英)+azure-speech-stt(日本語補助)。いずれもcost_log.jsonlのresponse model_id実測。

## 3. Gate結果(`{a2,b1b}/audit/gate_result_04C.json`)
- shared_gate=PASS(a2/b1b)、m2_complete=true、audio_text_deviations=0、article_text_source=canonical。
- 速度Gate(z_speed_v2): a2=全6 clip ok(narrator std_narrator_slow6 ×5、old_man std_dialogue_none)、b1b=全6 clip ok(narrator adv_narrator_none×5、old_man adv_dialogue_fast6: ratio0.9566[0.9-1.0])。速度Gate停止なし。
- kp_vote_audit: checked 3/3 with_vote_evidence(a2/b1b)。Pronunciation alarm 0件(両level)。HR Lock: review_lock_state 全segment RESOLVED(a2 19件/b1b 18件、LOCKなし)。
- pass_with_warning_listening_list: a2=1件(`japanese_title`「告げ口心臓」、一次ASR「菅口新造」→二次確認で「菅口心臓」=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG)、b1b=0件。**試聴時に日本語タイトル「告げ口心臓」の読みを確認してほしい**。
- ASR_VALIDATION_UNCERTAIN(verified=True、HR化せず): a2 part2_c3/part3_c1、b1b part2_c3/part3_c1(長clipのASR全文対比で分類が不確定になる既存挙動。本文逸脱=0)。

## 4. Voice割当(`voice_assignment.json`、Family Z Voice正式表PRODUCTION_WIRED、Fable受入2026-10-23)
- narrator=Aoede(Std/Adv本文)、老人(old_man)=Algieba(両level各1台詞「Who is in here?」/「Who's there?」)、警官(officer)=Schedar(台詞なし=未使用)。導入/KP番号等=Charon。

## 5. Key Phrase(KP、X2p'発火evidence: 全6件 `meaning_stage=applied` / `meaning_stage_path=newgen_meaning_v1`)
| level | # | 英語KP(正規化後) | source_span | 日本語gloss | gloss_alignment |
|---|---|---|---|---|---|
| Adv(b1b) | 1 | sharpen someone's senses | sharpened his senses | 人の感覚を研ぎ澄ます | GLOSS_REALIGNED |
| Adv | 2 | make someone's blood turn cold | made his blood turn cold | 人をぞっとさせる | GLOSS_REALIGNED |
| Adv | 3 | hideous | hideous | ぞっとするほど恐ろしい | GLOSS_REALIGNED |
| Std(a2) | 1 | in heaven and on earth | 同左 | この世のあらゆるところに | GLOSS_REALIGNED |
| Std | 2 | vulture's | vulture's | ハゲワシの | GLOSS_REALIGNED |
| Std | 3 | metal catch | metal catch | 金属製の留め金 | GLOSS_REALIGNED |
- Adv英語説明(KP explanation、全3件OK/15語以内): sharpen=「to make someone notice sounds, sights, or other things more clearly」等(`key_phrases/b1b/kp_explanations.json`)。Advは外側retry 2回目でCANONICALIZATION_PASS(overall PASS)。
- **注意(品質所見)**: Std KP#2 `vulture's` はcanonicalization QAで standalone_natural_unit/no_residual_context_word/reusable_other_context/standalone_comprehensibility がFAIL(CANONICALIZATION_REVIEW_REQUIRED、`key_phrases/a2/keywords_canonicalized.json` overall_status=REVIEW_REQUIRED)。runner(er026:1712-1713)は既存設計どおり REVIEW_REQUIRED を受理してKP資産を設置・音声化した(Gate緩和・Prompt変更なし)。単独の名詞所有格で学習単位として弱い。ユーザー最終試聴で要確認(下記「問題・未解決」)。
- Std KP外側retry(`key_phrases/a2/outer_retry_log.json`、案A再選定1回): attempt1=[froze my blood, sure of myself, metal catch]→INVALID(freeze someone's blood=活用形変更Rule7、sure of oneself=myself未登録)、attempt2=[metal catch, My ears began ringing, Pull up the floorboards]→INVALID(活用形変更)、attempt3=[in heaven and on earth, vulture's, metal catch]→REVIEW_REQUIRED(受理)。
- Adv外側retry: attempt1=[made his blood turn cold, eased open, fitted them back]→INVALID(ease open=活用形変更)、attempt2=[sharpened his senses, made his blood turn cold, hideous]→PASS。

## 6. ASR(音声検証)
- 全clip verified=True(EXACT/NORMALIZED/NUMERIC_EQUIVALENCE/PHONETIC/HIGH_SIMILARITY_SAFE/SECONDARY_CONFIRMED/一部ASR_VALIDATION_UNCERTAIN)。英語はgpt-4o-mini-transcribe全文ASRで本文一致を確認、日本語はASR+二次確認(azure)。TRUE_CONTENT_MISMATCH初回→再生成成功: a2 japanese_title(attempt1「菅口新造」→attempt2二次確認OK)の1件のみ。

## 7. 成果物・公開
- 全編: Std=`Family_Z_the_tell_tale_heart_a2.wav` 288.27秒、Adv=`..._b1b.wav` 275.21秒(`{level}/assembly/timeline.json`)。
- 公開ディレクトリ: `user_test/family_z_tell_tale_heart_01/`(index.html/standard.html/advanced.html + audio_standard/audio_advanced の全編・パート別mp3)。
- page_verify(`page_verify_local.json`): index/standard/advanced 全て HTTP200・console_errors 0・http>=400 0・plays_failed なし、`user_page_standard_check` overall=PASS(failed {})。`seek_ok_all=false`は既存全Z作品共通の表示(『開いた窓』run_sf_prod_01でも同値、既存挙動)。
- 試聴URL(push後): Std=https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/standard.html / Adv=https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/advanced.html / 一覧=.../index.html。

## 8. 費用(runner spent_jpy実測。run累計36.6373円)
- seed_check 0 / writer 9.2566 / std_adjust 6.8413 / plan 0.1044 / support 0.3978 / kp 5.5112(委任_02のkp[Adv成功分]を含む可能性のある累計、案A再選定を含む) / tts_b1b 6.7472 / tts_a2 7.7788 / provision〜page_verify 0。
- 作品累計 36.64円 / 承認Cap 70円(余裕33.36円)。**70円/記事セット目標との差: -33.36円(目標内)**。日次: 並行案件含む日次合計はdaily_dev_cost_01で別途確認(本作品分のみで日次1,000円に影響なし)。
