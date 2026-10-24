# RUNTIME_EVIDENCE_01 (FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_03、委任_04更新、2026-10-24)

状態: **COMPLETE_USER_LISTENING_PENDING**(正式完成候補。ユーザー最終試聴待ち。PASS先取りなし)。
run dir: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/`(stage log=`e2e_stage_log.jsonl`、起動log=`run_launch_log.jsonl`)。

## 1. 正式入口・stage
- 入口: `er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_01 --mode real --approved-budget-jpy 70 --tts-execution-mode STANDARD`(Z正式Production経路・STORY_REGISTRY登録済み作品)。
- 委任_02: seed_check,writer,std_adjust / plan,support / kp(Adv OK、Std 外側retry 3/3でSTOP)。
- 委任_03起動(全て1起動1コマンド、rc=0): ① `--stages kp --regenerate-stage kp_a2`(22:42:55、案A=1回、約203秒) ② `--stages tts_b1b`(22:46:33、約205秒) ③ `--stages tts_a2`(22:50:09、約221秒) ④ `--stages provision_shell,gate,assemble,pages,page_verify`(22:53:59、約2分)。起動間隔>150秒、RESTART_STORMなし、STOP通知/センチネルなし(`docs/pm/delegation_log/2026-10-24_FZTTH3_stop_check.json` rc=0 applies=false)。再起動0回。案B(myself→oneself)は委任_03時点では未実施 → 委任_04で実施。
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
| Std(a2、委任_04差替え後) | 1 | in heaven and on earth | 同左 | ありとあらゆる場所に | ALIGNED |
| Std | 2 | metal catch | metal catch | 金属製の留め金 | ALIGNED |
| Std | 3 | sure of oneself | sure of myself(myself→oneself人称一般化) | 自分に自信がある | ALIGNED |

(委任_03時点のStd KP=[in heaven and on earth, vulture's, metal catch]は委任_04で差替え。旧artifact退避先=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/_bak_pre04/`)
- Adv英語説明(KP explanation、全3件OK/15語以内): sharpen=「to make someone notice sounds, sights, or other things more clearly」等(`key_phrases/b1b/kp_explanations.json`)。Advは外側retry 2回目でCANONICALIZATION_PASS(overall PASS)。
- **委任_04是正(Std KP)**: 委任_03の`vulture's`(canonicalization QA 4項目FAIL・REVIEW_REQUIRED受理)は学習単位として不適切のため、案B(`er003_key_words_canonicalization.py` `_PERSON_DEPENDENT_TO_GENERIC`へ`myself→oneself`追加、commit 13b63f06f、影響分析=`OPEN_KP_MYSELF_IMPACT_01.md`)の後に`--stages kp --regenerate-stage kp_a2`を**2回**実施(委任_03の1回と通算3回目・4回目)。1回目(23:10:48起動)=selection[vulture's, as if they heard nothing, sure of myself]→**REVIEW_REQUIRED(vulture'sがqa_standalone_natural_unit/reusable_other_context/standalone_comprehensibility FAIL)→不採用**(artifact退避=`_bak_pre04/kp_try1/`)。2回目(23:13:50起動、間隔>150秒)=attempt1[froze my blood(INVALID: 活用形変更), bear another second, sure of myself]→INVALID、attempt2[in heaven and on earth, metal catch, sure of myself]→**CANONICALIZATION_PASS(QA全PASS、overall_status=PASS)→採用**。`sure of myself`は案Bにより旧来のINVALID(myself未登録)ではなく`sure of oneself`へ受理。
- 最終Std KP全件CANONICALIZATION_PASS・GLOSS ALIGNED。Std KP一覧は上表。

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

## 9. 委任_04追補(2026-10-24 23:10〜23:23)
- 起動(全て1起動1コマンド、rc=0、stop_scope_check rc=0[`docs/pm/delegation_log/2026-10-24_FZTTH4_stop_check*.json`]、間隔>150秒、RESTART_STORMなし、STOP通知なし、再起動0): ① `--stages kp --regenerate-stage kp_a2`(23:10:48) ② 同(23:13:50) ③ `--stages tts_a2`(約23:19) ④ `--stages provision_shell,gate,assemble,pages,page_verify`(約23:21、1起動)。
- TTS: Std KP clipのみ再生成(kp1_ja/kp2_en/kp2_ja/kp3_en/kp3_ja。kp1_en=`in heaven and on earth`は同文のため再利用、本文segment・Adv側は全wav md5不変=`diff`で確認)。費用+約0.45円。
- Gate(`a2/audit/gate_result_04C.json`、`b1b`): shared_gate=PASS(a2/b1b)、m2_complete=true、audio_text_deviations=[]、kp_vote_audit 3/3 with_vote_evidence、z_speed_v2 全clip ok、review_lock全segment RESOLVED(a2 18/b1b 17)。page_verify(`page_verify_local.json`): user_page_standard_check overall=PASS(failed{})。
- 試聴確認項目(再生成していない): 日本語タイトル「告げ口心臓」(委任_03で一次ASR「菅口新造」→二次確認OK、clip不変)。
- 費用: 作品累計 **39.974円**(委任_03終了時36.637円 + 委任_04 約3.34円: kp再選定2回 約2.89円 + tts_a2 約0.45円)/ Cap70円(余裕30.03円)。70円/記事セット目標内。
